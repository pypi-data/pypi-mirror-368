
import asyncio
import logging
from typing import Any, Dict, List, Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from calita.manager_sub_agents.final_result_agent import FinalResultAgent
from calita.manager_sub_agents.mcp_tool_agent import McpToolAgent
from calita.manager_sub_agents.task_plan_agent import TaskPlanAgent
from calita.mcp_creation.mcp_creation_agent import McpCreationAgent
from calita.mcp_creation.mcp_creation_agent_pro import McpCreationAgentPro
from calita.utils.model_client import ModelClientFactory, ModelClient
from calita.utils.utils import handle_error
from calita.web_agent import WebAgent


class TaskState(TypedDict):
    """State definition for the agent orchestration graph"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_input: str
    super_next: str
    tasks: List[Dict[str, Any]]
    context: str
    current_task: Dict[str, Any]
    next_task: Dict[str, Any]
    formatted_result: str
    final_error_info: str
    iteration_count: int

class ManagerAgent:
    def __init__(self, config: Dict[str, Any]) -> None:
        try:
            # API configuration
            model_config = {}
            api_config: Dict[str, Any] = config.get("api", {})
            model_config['temperature'] = float(api_config.get("temperature", 0.7))
            model_config['max_tokens'] = int(api_config.get("max_tokens", 16384))

            # LLM configuration
            primary_llm = config.get("agent", {}).get("primary_llm")
            model_config['model'] = primary_llm
            reason_model = config.get("agent", {}).get("reason_llm")
            model_config['reason_model'] = reason_model if reason_model else primary_llm

            # Initialize model client using factory
            model_client: ModelClient = ModelClientFactory.create_client(config)

            # Initialize the graph (will be created when needed)
            self.graph = None
            self.max_iterations: int = int(config.get("graph_max_iterations", 3))

            # Initialize agents
            self.mcp_creation_agent = McpCreationAgentPro(config) # can use McpCreationAgent too
            self.web_agent = WebAgent(model_client, model_config)
            self.task_plan_agent = TaskPlanAgent(model_client, model_config)
            self.mcp_tool_agent = McpToolAgent(model_client, model_config)
            self.final_result_agent = FinalResultAgent(model_client, model_config)

            logging.info(f"ManagerAgent initialized , max_iterations={self.max_iterations}")
        except Exception as e:
            handle_error(e)


    async def _create_graph(self) -> StateGraph:
        """
        Create and configure the LangGraph with MCP tools.

        Returns:
            StateGraph: Configured retrieval graph
        """
        try:
            # Create graph builder
            graph_builder = StateGraph(TaskState)

            # Add nodes
            graph_builder.add_node("supervisor", self._supervisor_node)
            graph_builder.add_node("task_plan_agent", self._task_plan_agent_node)
            graph_builder.add_node("web_agent", self._web_agent_node)
            graph_builder.add_node("tool_agent", self._tool_agent_node)
            graph_builder.add_node("mcp_creation_agent", self._mcp_creation_agent_node)
            graph_builder.add_node("eval_task", self._eval_task_node)
            graph_builder.add_node("final_result", self._final_result_node)

            # Add edges
            graph_builder.add_edge(START, "supervisor")
            graph_builder.add_conditional_edges(
                "supervisor",
                self._supervisor_router,
                {
                    "task_plan_agent": "task_plan_agent",
                    "web_agent": "web_agent",
                    "tool_agent": "tool_agent",
                    "mcp_creation_agent": "mcp_creation_agent",
                    "end": END,
                }
            )

            graph_builder.add_edge("task_plan_agent", "supervisor")
            graph_builder.add_edge("web_agent", "eval_task")
            graph_builder.add_edge("tool_agent", "eval_task")
            graph_builder.add_edge("mcp_creation_agent", "eval_task")

            graph_builder.add_conditional_edges(
                "eval_task",
                self._next_task_condition,
                {
                    "next_task": "supervisor",
                    "final_result": "final_result",
                }
            )

            graph_builder.add_conditional_edges(
                "final_result",
                self._task_end_condition,
                {
                    "restart": "supervisor",
                    "task_end": END,
                }
            )

            graph_builder.add_edge("final_result", END)

            # Compile the graph with proper checkpointer configuration
            graph = graph_builder.compile(checkpointer=MemorySaver())
            graph.name = "ManagerAgent"

            logging.info(f"ManagerAgent graph created, graph.name=: {graph.name}")
            return graph
        except Exception as e:
            logging.error("Failed to create ManagerAgent graph: %s", str(e))
            raise

    def _supervisor_node(self, state: TaskState) -> Dict[str, Any]:
        super_next = "end"

        current_task = None
        tasks = state["tasks"]
        iteration_count = state["iteration_count"]
        user_input = state['user_input']
        final_error_info = ""

        node_id = f"[NODE.1]supervisor({iteration_count})"
        if state["super_next"] is None: #First Time
            super_next = "task_plan_agent"
            logging.info(f"{node_id}: Start run FIRST, user_input={user_input}")
        elif state["super_next"]  == "task_plan_agent": #Task Plan Complete
            if len(tasks) > 0 and tasks[0].get("agent") : #Task Plan Succeed
                first_task = tasks[0]
                current_task = first_task
                super_next = first_task["agent"]
            else:
                final_error_info = "Task plan fail, can't complete request"
                logging.error(f"{node_id}: ### Task plan fail, task END, user_input={user_input} ###")
        elif state["next_task"] and len(state["next_task"]) > 0: #Start next task
            current_task = state["next_task"]
            super_next = current_task["agent"]
            logging.info(f"{node_id}: Start next task, super_next={super_next}")
        else: # Current task execute fail or Final result is unsatisfy
            if iteration_count < self.max_iterations: # Task fail, plan task again
                super_next = "task_plan_agent"
                iteration_count += 1
                tasks = []
                logging.warning(f"{node_id}: === Start next iteration, iteration_count={iteration_count} ===")
            else:
                final_error_info = "Reached max iterations, can't complete request"
                logging.error(f"{node_id}: ### Max iteration is reached, task END, iteration_count={iteration_count} ### ")

        return {
            "next_task": None,
            "super_next": super_next,
            "current_task": current_task,
            "iteration_count": iteration_count,
            "tasks": tasks,
            "final_error_info": final_error_info,
            "messages": state["messages"] + [AIMessage(content=f"{node_id}: super_next={super_next}, final_error_info={final_error_info}")],
        }

    async def _task_plan_agent_node(self, state: TaskState) -> Dict[str, Any]:
        iteration_count = state["iteration_count"]
        node_id = f"[NODE.2]task_plan_agent({iteration_count})"

        user_input = state['user_input']
        logging.info(f"{node_id}: Start task plan, LLM reasoning ... , user_input={user_input}")

        plan_tasks = []
        try:
            # Refresh McpBox tool schema,
            mcp_tool_schemas = await self.mcp_tool_agent.async_get_tool_schema()
            context = state["context"]
            plan_tasks = self.task_plan_agent.task_plan(user_input, mcp_tool_schemas, context)
        except Exception as e:
            logging.error(f"{node_id}: call task_plan exception: {e}")

        plan_task_len = len(plan_tasks)
        logging.info(f"{node_id}: ====== Task Plan Result [{plan_task_len}] ======\n{plan_tasks}======")

        return {
            "tasks" : plan_tasks,
            "messages": state["messages"] + [AIMessage(content=f"{node_id}: plan_task_len={plan_task_len}")]
        }

    async def _web_agent_node(self, state: TaskState) -> Dict[str, Any]:
        task = state["current_task"]

        task_no = task["task_no"]
        iteration_count = state["iteration_count"]
        node_id = f"[NODE.3.{task_no}]web_agent({iteration_count})"

        logging.info(f"{node_id}: Start web search , task={task}")

        search_result = {}
        try:
            search_result = await self.web_agent.async_search(task["target"])
            task["result"] = search_result.get("result")
            task["error"] = search_result.get("error")
        except Exception as e:
            error = f"web_agent call search exception: {e}"
            logging.error(f"{node_id}: call search exception: {e}")
            task["result"] = None
            task["error"] = error
            search_result["error"] = error

        succeed = False if task["error"] else True
        logging.info(f"{node_id}: ====== Web Search Result Exec Succeed={succeed} ======\n{search_result}\n======")

        return {
            "current_task": task,
            "messages": state["messages"] + [AIMessage(content=f"{node_id}: task exec succeed={succeed}")]
        }

    async def _tool_agent_node(self, state: TaskState) -> Dict[str, Any]:
        task = state["current_task"]

        task_no = task["task_no"]
        iteration_count = state["iteration_count"]
        node_id = f"[NODE.3.{task_no}]tool_agent({iteration_count})"

        logging.info(f"{node_id}: Start call mcp tool , task={task}")

        context = state["context"]
        tool_result = {}
        try:
            tool_result = await self.mcp_tool_agent.async_call(task["target"], context)
            task["result"] = tool_result.get("result")
            task["error"] = tool_result.get("error")
        except Exception as e:
            error = f"tool_agent call mcp tool exception: {e}"
            logging.error(f"{node_id}: call mcp tool exception: {e}")
            task["result"] = None
            task["error"] = error
            tool_result["error"] = error

        succeed = False if task["error"] else True
        logging.info(f"{node_id}: ====== MCP Tool Result Exec Succeed={succeed} : {tool_result} ======")

        return {
            "current_task": task,
            "messages": state["messages"] + [AIMessage(content=f"{node_id}: task exec succeed={succeed}")]
        }

    async def _mcp_creation_agent_node(self, state: TaskState) -> Dict[str, Any]:
        task = state["current_task"]

        task_no = task["task_no"]
        iteration_count = state["iteration_count"]
        node_id = f"[NODE.3.{task_no}]mcp_creation_agent({iteration_count})"

        logging.info(f"{node_id}: Start create generate mcp tool code and execute... , task={task}")

        generate_result = {}
        context = state["context"]
        try:
            generate_result = await self.mcp_creation_agent.async_generate(task["target"], context)
            task["result"] = generate_result.get("result")
            task["error"] = generate_result.get("error")
        except Exception as e:
            error = f"mcp_creation_agent generate exception: {e}"
            logging.error(f"{node_id}: call generate exception: {e}")
            task["result"] = None
            task["error"] = error
            generate_result["error"] = error

        succeed = False if task["error"] else True
        logging.info(f"{node_id}: ====== MCP Creation Result Exec Succeed={succeed} : {generate_result} ======")
        return {
            "current_task": task,
            "messages": state["messages"] + [AIMessage(content=f"{node_id}: task exec succeed={succeed}")]
        }

    def _eval_task_node(self, state: TaskState) -> Dict[str, Any]:
        current_task = state["current_task"]
        tasks = state["tasks"]
        task_no = current_task["task_no"]

        iteration_count = state["iteration_count"]
        node_id = f"[NODE.4]eval_task({iteration_count})"

        logging.info(f"{node_id}: Start evaluate task result, task={current_task}")

        next_task = None
        tasks[task_no]["result"] = current_task.get("result")
        tasks[task_no]["error"] = current_task.get("error")

        task_state = 1
        if current_task.get("error") is None:
            task_state = 0
            if task_no < len(tasks) -1: # Has next task
                next_task = tasks[task_no + 1]
            else: # All task is completed succeed
                next_task = {}
        elif state['iteration_count'] >= self.max_iterations: # max_iterations is reached， END
            logging.warning(f"### {node_id}: max_iteration is reached, task END, iteration_count={state['iteration_count']} ### ")
            next_task = {}

        tasks[task_no]["state"] = task_state
        current_task["state"] = task_state

        context = "" if len(tasks) == 0 else str(tasks)
        logging.info(f"{node_id}: ====== Evaluate Result Next Task: {next_task} ====== ")
        return {
            "current_task": current_task,
            "next_task" : next_task,
            "context": context,
            "messages": state["messages"] + [AIMessage(content=f"{node_id}: next_task={next_task}")]
        }

    def _final_result_node(self, state: TaskState) -> Dict[str, Any]:
        iteration_count = state["iteration_count"]
        node_id = f"[NODE.5]final_result({iteration_count})"

        task_results = []
        tasks = state["tasks"]
        for task in tasks:
            task_result = {
                "task_no": task["task_no"],
                "task": task["target"],
            }
            if task.get("error") is not None:
                task_result["error"] = task["error"]
            else:
                result = task["result"]
                if task["agent"] == "mcp_creation_agent":
                    task_result["result"] = result.get("output", "")
                else:
                    task_result["result"] = result
            task_results.append(task_result)

        logging.info(f"{node_id}: Start generate final task result..., task_results ======:\n{task_results}======")
        final_result_type = -1
        formatted_result = ""
        try:
            user_input = state["user_input"]
            final_result = self.final_result_agent.final_result(user_input, str(task_results))
            final_result_type = int(final_result.get("final_result_type"))
            formatted_result = str(final_result.get("formatted_result", ""))
        except Exception as e:
            logging.error(f"### {node_id}: final_result_agent call final_result exception: {e} ### ")

        logging.info(f"{node_id}: ====== FINAL_RESULT ======\nfinal_result_type={final_result_type}\nformatted_result={formatted_result}\n ======")

        if final_result_type < 0: # If require high quality, can add condition 'or final_result_type > 0'
            if  state['iteration_count'] < self.max_iterations:
                # Restart iteration
                logging.warning(f"### {node_id}: Can't generate satisfied result, RESTART  iteration, iteration_count={state['iteration_count']} ### ")
                formatted_result = ""
            else:
                logging.warning(f"### {node_id}: max_iteration is reached, task END, iteration_count={state['iteration_count']} ### ")
                formatted_result = "Reached max iterations, can't complete request"
        return {
            "formatted_result" : formatted_result,
            "messages": state["messages"] + [AIMessage(content=f"{node_id}: formatted_result={formatted_result}")]
        }

    def _next_task_condition(self, state: TaskState) -> str:
        cond = "next_task"
        next_task = state["next_task"]
        if next_task is not None and len(next_task) == 0:
            cond = "final_result"
        return cond

    def _task_end_condition(self, state: TaskState) -> str:
        formatted_result = state["formatted_result"]
        cond = "task_end" if formatted_result.strip() else "restart"
        return cond

    def _supervisor_router(self, state: TaskState) -> str:
        return state['super_next']

    async def async_generate(self, user_input: str) -> str:
        result = ""
        try:
            logging.info("="*100)
            logging.info("Starting ManagerAgent graph work for user_input: %s", user_input)
            logging.info("=" * 100)

            # Create graph if not already created
            if self.graph is None:
                self.graph = await self._create_graph()

            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=f"information for: {user_input}")],
                "user_input": user_input,
                "super_next": None,
                "tasks": [],
                "context": "",
                "current_task": None,
                "next_task": None,
                "formatted_result": "",
                "final_error_info": "",
                "iteration_count": 1
            }


            # Run the retrieval graph with proper configuration
            config = {"recursion_limit": 90,
                      "configurable": {"thread_id": "manager_async_generate_thread"}}
            final_state = await self.graph.ainvoke(initial_state, config=config)

            # Parse and return formatted results
            result = final_state["formatted_result"] if final_state["formatted_result"] else final_state["final_error_info"]

            logging.info("=" * 100)
            logging.info("User question: %s", user_input)
            logging.info("User answer: %s", result)
            logging.info("=" * 100)

            return result
        except Exception as e:
            logging.error("### Error ManagerAgent _agent_work for user_input '%s': %s ###", user_input, str(e))
            handle_error(e)
            result = "Never get result, Unexpected Error"
            return result

    def generate(self, request: str) -> str:
        return asyncio.run(self.async_generate(request))


if __name__ == "__main__":
    from calita.utils.utils import get_global_config
    from calita.utils.utils import setup_logging

    config = get_global_config("config.yaml")
    setup_logging(config)


    manager = ManagerAgent(config)
    user_inputs = [
                    #"上周黄金价格, 按照价格从低到高排序输出，输出格式[{‘周一’: price}]"
                    "北京本周每天的天气数据, 按照温度从低到高排序输出，输出格式[{‘周一’: degree}]"
                    #"Create a function to sort a list of numbers, sort [6,8,7,5]"
                    #, "sort [3,2,7,5]"
                ]
    for user_input in user_inputs:
        result = manager.generate(user_input)
        print(result)
