import json
import logging
import re
from typing import Any, Dict, List

from calita.utils.model_client import ModelClient
from calita.utils.utils import read_template


class FinalResultAgent:
    def __init__(self, model_client: ModelClient, model_config: Dict[str, Any]):
        self.model_client = model_client
        self.prompt_template: str = read_template("templates/final_result_template.txt")
        self.model_config = model_config


    def final_result(self, user_request: str, task_results: str)-> Dict[str, Any]:
        prompt = self.prompt_template.replace("{user_request}", user_request)
        prompt = prompt.replace("{task_results}", task_results)

        messages = [{"role": "user", "content": prompt}]

        model = self.model_config.get("reason_model")

        stream = True
        response_text: str = ""
        response = self.model_client.create_completion(
            messages=messages,
            temperature=self.model_config.get("temperature", 0.7),
            max_tokens=self.model_config.get("max_tokens", 16384),
            model=model,
            enable_thinking=True,
            stream = True,
        )
        if stream:
            for chunk in response:
                response_text = response_text + str(chunk)
        else:
            response_text = response

        cleaned_text = re.sub(r'^\s*```json|```\s*$', '', response_text, flags=re.MULTILINE).strip()
        final_result = json.loads(cleaned_text)
        return final_result


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
        "reason_model": config.get("agent", {}).get("reason_llm")
    }
    task_plan_agent = FinalResultAgent(model_client, model_config)

    final_result = task_plan_agent.final_result("Create a function to sort a list of numbers, sort [6,8,7,5]", "{'task': '使用sortNumbers工具对列表[6,8,7,5]进行升序排序', 'task_no': 0, 'result': \"{'original': [6, 8, 7, 5], 'sorted': [5, 6, 7, 8], 'is_ascending': True}\", 'error': None}")
    print(f"FINAL_RESULT：   {final_result} ")