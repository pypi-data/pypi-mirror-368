import json
import logging
import re
from typing import Any, Dict, List


from calita.utils.model_client import ModelClient
from calita.utils.utils import read_template


class TaskPlanAgent:
    def __init__(self, model_client: ModelClient, model_config: Dict[str, Any]):
        self.model_client = model_client
        self.prompt_template: str = read_template("templates/task_plan_template.txt")
        self.model_config = model_config


    def task_plan(self, user_request: str, tool_schemas: str, context: str= "")-> List[Dict[str, Any]]:
        prompt = self.prompt_template.replace("{user_request}", user_request)
        prompt = prompt.replace("{context}", context)
        prompt = prompt.replace("{mcp_tool_list}", tool_schemas)

        messages = [{"role": "user", "content": prompt}]

        model = self.model_config.get("reason_model") #use 'model'

        stream = True
        response_text: str = ""
        response = self.model_client.create_completion(
            messages=messages,
            temperature=self.model_config.get("temperature", 0.7),
            max_tokens=self.model_config.get("max_tokens", 16384),
            model=model,
            enable_thinking=True,
            stream = stream,
        )
        if stream:
            for chunk in response:
                response_text = response_text + str(chunk)
        else:
            response_text = response

        cleaned_text = re.sub(r'^\s*```json|```\s*$', '', response_text, flags=re.MULTILINE).strip()
        tasks = json.loads(cleaned_text)
        task_no = 0
        for task in tasks:
            task['state'] = -1
            task['task_no'] = task_no
            task_no += 1
        logging.info(tasks)
        return tasks


if __name__ == "__main__":
    from calita.utils.utils import get_global_config
    from calita.utils.utils import setup_logging
    from calita.utils.model_client import ModelClientFactory

    config = get_global_config("config.yaml")
    model_client: ModelClient = ModelClientFactory.create_client(config)
    setup_logging(config)

    api_config: Dict[str, Any] = config.get("api", {})
    model_config = {
        "temperature": float(api_config.get("temperature", 0.7)),
        "max_tokens": int(api_config.get("max_tokens", 16384)),
        "model": config.get("agent", {}).get("primary_llm"),
        "reason_model": config.get("agent", {}).get("reason_llm")
    }
    task_plan_agent = TaskPlanAgent(model_client, model_config)

    task_plan_agent.task_plan("上周每天黄金的价格, 按照价格从低到高排序输出，输出格式[{‘周一’: price}]", "")