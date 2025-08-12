import asyncio
import json
import logging
import re
from typing import Dict, Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from calita.utils.mcp_config_loader import load_mcp_servers_config
from calita.utils.model_client import ModelClient
from calita.utils.utils import read_template


class McpToolAgent:
    def __init__(self, model_client: ModelClient, model_config: Dict[str, Any]) -> None:
        mcp_servers_config: Dict[str, Any] = load_mcp_servers_config("mcp_config/mcp_box_servers.json")
        self.mcp_client = MultiServerMCPClient(mcp_servers_config.get("mcpServers", {}))
        logging.info("McpToolAgent: Loaded MCP servers: %s", list(mcp_servers_config.keys()))

        self.model_client = model_client
        self.prompt_template: str = read_template("templates/mcp_tool_fetch_template.txt")
        self.model_config = model_config

    async def _fetch_mcp_tool(self, task: str, context: str) ->Dict[str, Any]:
        mcp_tool = {}
        prompt = self.prompt_template.replace("{task}", task)
        prompt = prompt.replace("{context}", context)
        mcp_tool_schemas = await self.async_get_tool_schema()
        prompt = prompt.replace("{mcp_tool_list}", mcp_tool_schemas)

        logging.info(f"McpToolAgent <fetch_mcp_tool>: task={task} in mcp tools {self.mcp_tool_names}")

        messages = [{"role": "user", "content": prompt}]
        response_text: str = self.model_client.create_completion(
            messages=messages,
            temperature=self.model_config.get("temperature", 0.7),
            max_tokens=self.model_config.get("max_tokens", 16384),
            model=self.model_config.get("model"),
            #enable_thinking=True
        )
        cleaned_text = re.sub(r'^\s*```json|```\s*$', '', response_text, flags=re.MULTILINE).strip()
        mcp_tool = json.loads(cleaned_text)
        logging.info(f"McpToolAgent <fetch_mcp_tool>: fetched mcp_tool={mcp_tool}")
        return mcp_tool

    def get_tool_schema(self) -> str:
        return asyncio.run(self.async_get_tool_schema())

    async def async_get_tool_schema(self) -> str:
        logging.info("McpToolAgent: Begin get mcp tool schema .....")
        mcp_tools = await self.mcp_client.get_tools()
        self.mcp_tool_names = [tool.name for tool in mcp_tools]
        logging.info("McpToolAgent <get_tool_schema>: McpBox has %s tools %s ", len(self.mcp_tool_names), self.mcp_tool_names)

        mcp_tool_schemas = []
        i = 1
        for tool in mcp_tools:
            tool_schema = {tool.name: {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.args,
            }}
            mcp_tool_schemas.append(tool_schema)
            logging.debug("------ MCP TOOL[%s] Schema: %s  -------", i,tool_schema)
            i += 1

        mcp_tool_schemas = json.dumps(mcp_tool_schemas, ensure_ascii=False, indent=4)

        return mcp_tool_schemas

    def call(self, task: str, context: str)-> Dict[str, Any]:
        return asyncio.run(self.async_call(task, context))

    async def async_call(self, task: str, context: str) -> Dict[str, Any]:
        result = {}
        try:
            mcp_tool = await self._fetch_mcp_tool(task, context)
            tool_name = mcp_tool.get("tool_name")
            tool_args = mcp_tool.get("tool_args")
            if tool_name is None:
                error = f"No mcp tool found for task:{task}"
                logging.info(f"McpToolAgent _call: {error}")
                return {"error": error}

            logging.info(f"McpToolAgent <call> : Begin call mcp tool={tool_name}, tool_args={tool_args}")
            async with self.mcp_client.session("mcpbox") as session:
                tools = await load_mcp_tools(session)
                mcp_tool = next(t for t in tools if t.name == tool_name)
                if mcp_tool is not None:
                    tool_result = await mcp_tool.arun(tool_args)
                    result =  {'result': tool_result}
                else:
                    error = f"No mcp tool fetched for task:{task}"
                    logging.info(f"McpToolAgent <call>: error={error}")
                    result['error'] = error
        except Exception as e:
            logging.error(f"McpToolAgent <async_call>: task={task}, exception={e}")
            result['error'] = str(e)

        return result

if __name__ == "__main__":
    from calita.utils.utils import get_global_config
    from calita.utils.utils import setup_logging
    from calita.utils.model_client import ModelClientFactory

    config = get_global_config("config.yaml")
    setup_logging(config)

    api_config: Dict[str, Any] = config.get("api", {})
    model_config = {
        "temperature": float(api_config.get("temperature", 0.7)),
        "max_tokens": int(api_config.get("max_tokens", 16384)),
        "model": config.get("agent", {}).get("primary_llm"),
    }
    model_client: ModelClient = ModelClientFactory.create_client(config)

    agent = McpToolAgent(model_client, model_config)
    result = agent.call("排序4，2, 5, 1", "")

    print(result)