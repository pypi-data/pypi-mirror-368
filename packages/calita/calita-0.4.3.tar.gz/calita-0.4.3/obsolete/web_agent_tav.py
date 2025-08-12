import asyncio
import json
import logging
import re
from typing import Dict, Any, List
from datetime import datetime

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from calita.utils.mcp_config_loader import load_mcp_servers_config
from calita.utils.model_client import ModelClient
from calita.utils.utils import read_template


class WebAgent:
    def __init__(self, model_client: ModelClient, model_config: Dict[str, Any]) -> None:
        mcp_servers_config: Dict[str, Any] = load_mcp_servers_config("mcp_config/mcp_web_server.json")
        logging.info("Loaded MCP servers: %s", list(mcp_servers_config.keys()))
        self.mcp_client = MultiServerMCPClient(mcp_servers_config.get("mcpServers", {}))

        self.summary_template: str = read_template("templates/web_summary_template.txt")
        self.rewrite_template: str = read_template("templates/web_rewrite_template.txt")

        self.model_client = model_client
        self.model_config = model_config

    def _extract_search_result(self, search_response: str)-> List[Dict[str, Any]]:
        # Define the pattern to match each entry
        pattern = r'Title: (.+?)\nURL: (.+?)\nContent: (.+?)(?=\n\nTitle:|\n*$)'
        # Find all matches
        matches = re.findall(pattern, search_response, re.DOTALL)
        # Create the output list
        search_result = []
        for match in matches:
            title = match[0].strip()
            url = match[1].strip()
            content = match[2].strip()
            # Clean up content by removing excessive whitespace
            content = ' '.join(content.split())

            search_result.append({
                "title": title,
                "url": url,
                "content": content
            })
        return search_result

    async def _tavily_search(self, query)-> Dict[str, Any]:
        result = {}
        try:
            async with self.mcp_client.session("tavily") as session:
                tools = await load_mcp_tools(session)
                web_search_tool = next(t for t in tools if t.name == "tavily-search")
                craw_tool = next(t for t in tools if t.name == "tavily-crawl")

                search_response:str = await web_search_tool.arun({"query": query, "max_results": 5, "search_depth": "advanced"})

                summary = self._summary(query, search_response)
                summary_type = int(summary.get("summary_type", -1))
                summary_content = summary.get("summary", "")
                if summary_type == 0:
                    return {"result": summary_content}

                logging.warning(f"WebAgent <tavily_search> : Not get result directly, summary_type={summary_type}")
                result = await self._crawl(query, search_response, craw_tool)
        except Exception as e:
            logging.error("### tavily_search exception: '%s' ###",  str(e))
            result = {'error': f"Tavily Search '{query}' Failed!"}
        return result

    async def _crawl(self, query: str, search_response: str, crawl_tool)-> Dict[str, Any]:
        search_results = self._extract_search_result(search_response)
        i = 0
        for search_result in search_results:
            url = search_result.get("url", "")
            if len(url.strip()) > 0 and i < 2:
                logging.info(f"WebAgent <tavily_search.crawl> : url={url}")
                try:
                    content = await crawl_tool.arun({"url": url})
                    search_result["url_content"] = content
                except Exception as e:
                    logging.warning(f"WebAgent <tavily_search.crawl_tool> : url={url}, exception={e}")
                i += 1
        summary = self._summary(query, str(search_results))
        summary_type = int(summary.get("summary_type", -1))
        summary_content = summary.get("summary", "")
        if summary_type >= 0:
            result = {"result": summary_content}
        else:
            result = {"error": f"Web Search '{query}' ,result is empty"}
        return result

    def _summary(self, query: str, search_result: str) ->Dict[str, Any]:
        short_result = search_result[:2000] if len(search_result) >= 2000 else search_result
        print(short_result)
        prompt = self.summary_template.replace("{query}", query)
        prompt = prompt.replace("{search_result}", short_result)

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

    def _rewrite(self, query: str)-> str:
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        prompt = self.rewrite_template.replace("{current_time}", current_time)
        prompt = prompt.replace("{query}", query)

        messages = [{"role": "user", "content": prompt}]
        response: str = self.model_client.create_completion(
            messages=messages,
            temperature=self.model_config.get("temperature", 0.7),
            max_tokens=self.model_config.get("max_tokens", 16384),
            model=self.model_config.get("model"),
        )

        logging.info(f"WebAgent <rewrite> : rewrite result={response}")
        return response

    def search(self, query: str) -> Dict[str, Any]:
        return asyncio.run(self.async_search(query))

    async def async_search(self, query: str) -> Dict[str, Any]:
        final_result = {}
        logging.info("WebAgent <async_search> : query: %s", query)

        query = self._rewrite(query)

        search_result = await self._tavily_search(query)
        summary = search_result.get("result")
        if summary is not None and len(summary) == 0:
            logging.error("WebAgent <async_search> : query: %s ,result is empty ", query)
            final_result = {"error": f"Web Search '{query}' ,result is empty"}
        else:
            final_result = search_result

        return final_result

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
    result = web_agent.search("北京本周每天的天气数据")
    print(result)