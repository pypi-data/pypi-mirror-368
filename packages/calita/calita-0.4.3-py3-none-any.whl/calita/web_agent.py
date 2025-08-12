import asyncio
import json
import logging
import re
from typing import Dict, Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from calita.utils.mcp_config_loader import load_mcp_servers_config
from calita.utils.utils import read_template
from calita.utils.model_client import ModelClient

class WebAgent:
    def __init__(self, model_client: ModelClient, model_config: Dict[str, Any]) -> None:
        mcp_servers_config: Dict[str, Any] = load_mcp_servers_config("mcp_config/mcp_web_server.json")
        self.mcp_client = MultiServerMCPClient(mcp_servers_config.get("mcpServers", {}))
        logging.info("WebAgent: Loaded MCP servers: %s", list(mcp_servers_config.keys()))

        self.summary_template: str = read_template("templates/web_summary_template.txt")

        self.model_client = model_client
        self.model_config = model_config


    def _extract_search_result(self, query: str, search_response)->Dict[str, Any]:
        result = {}
        try:
            _response = json.loads(search_response)
            if "results" in _response  and  len(_response["results"]) > 1:
                raw_results = _response['results']
                search_result = []
                for raw_result in raw_results:
                    search_text = raw_result.get("text","")
                    if len(search_text) > 0:
                        short_content =  search_text[:500] if len(search_text) >= 500 else search_text
                        search_result.append({
                            "search_result_title": raw_result["title"],
                            "search_result_content": short_content
                        })
                summary = self._summary(query, str(search_result))
                summary_type = int(summary.get("summary_type", -1))
                summary_content = summary.get("summary", "")
                if summary_type == 0:
                    result = {"result": summary_content}
                elif summary_type > 0:
                    result = {"result": summary_content}
                    logging.warning(f"WebAgent <extract_search_result>:  Search result only partly satisfied!")
                else:
                    logging.error(f"WebAgent <extract_search_result>:  Search result  unsatisfied !")
                    result = {"error": f"Web Search '{query}' ,result is empty"}
            else:
                result = {'error': f"Web Search '{query}' ,result is empty"}
        except json.JSONDecodeError as e:
            logging.error(f"WebAgent <extract_search_result>: exception={e}")
            result = {'error': "Web Search result is not valid"}
        return result

    def _summary(self, query: str, search_result: str) ->Dict[str, Any]:
        prompt = self.summary_template.replace("{query}", query)
        prompt = prompt.replace("{search_result}", search_result)

        messages = [{"role": "user", "content": prompt}]
        response: str = self.model_client.create_completion(
            messages=messages,
            temperature=self.model_config.get("temperature", 0.7),
            max_tokens=self.model_config.get("max_tokens", 16384),
            model=self.model_config.get("model"),
        )
        cleaned_text = re.sub(r'^\s*```json|```\s*$', '', response, flags=re.MULTILINE).strip()
        summary = json.loads(cleaned_text)
        return summary

    async def _exa_search(self, query)-> Dict[str, Any]:
        result = {}
        try:
            logging.info(f"WebAgent <exa_search>: query={query}")

            async with self.mcp_client.session("exa") as session:
                tools = await load_mcp_tools(session)
                web_search_tool = next(t for t in tools if t.name == "web_search_exa")

                response = await web_search_tool.arun({"query": query, "numResults": 3})
                result = self._extract_search_result(query, response)
        except Exception as e:
            logging.error(f"WebAgent <exa_search>: query={query}, exception={e}")
            result['error'] = str(e)

        return result

    def search(self, query: str) -> Dict[str, Any]:
        return asyncio.run(self.async_search(query))

    async def async_search(self, query: str) -> Dict[str, Any]:
        return await self._exa_search(query)

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

    web_agent = WebAgent(model_client, model_config)
    final_result = web_agent.search("北京本周每天的天气数据")
    #final_result = web_agent.search("上周的黄金价格")

    print(final_result)
