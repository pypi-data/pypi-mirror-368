"""mcp_registry.py

This module implements the MCPRegistry class for storing and retrieving generated
Model Context Protocols (MCPs) in a persistent, file-based registry.

The MCPRegistry provides the following interface:
    - __init__(config: dict) -> None
    - register_mcp_tool(tool_name: str, script:str, requirements:str) -> None
"""

import asyncio
import logging
from textwrap import dedent
from typing import Dict, Any

import httpx

from calita.utils.utils import handle_error


class MCPRegistry:
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the MCPRegistry with configuration settings.

        Args:
            config (Dict[str, Any]): Configuration dictionary loaded from config.yaml.
                Optional Key:
                    - mcp_registry.registry_path: The file path for storing the MCP registry.
                      If not provided, defaults to "mcp_registry.json" in the current working directory.
        """
        mcp_registry_config: Dict[str, Any] = config.get("mcp_registry", {})
        self.registry_url = mcp_registry_config.get("registry_url", None)
        logging.info("Initializing MCPRegistry with registry url: %s", self.registry_url)


    async def _call_add_mcp_tool(self, mcp_tool_name: str, mcp_tool_code: str) -> str:
        url = f"{self.registry_url}/add_mcp_tool/"
        params = {"mcp_tool_name": mcp_tool_name}
        mcp_box_url = None

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    url,
                    params=params,
                    content=mcp_tool_code.encode('utf-8'),
                    headers={"Content-Type": "text/plain; charset=utf-8"}
                )
                result = response.json()
                logging.info(f"call_add_mcp_tool result={result}")
                if response.status_code == 200 and result['result'] == 0:
                    mcp_box_url = result['mcp_box_url']
            except Exception as e:
                logging.error(f"call_add_mcp_tool: error {e}")

            return mcp_box_url

    async def _call_remove_mcp_tool(self, mcp_tool_name: str):
        url = f"{self.registry_url}/remove_mcp_tool/"
        params = {"mcp_tool_name": mcp_tool_name}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    url,
                    params=params,
                    headers={"Content-Type": "text/plain; charset=utf-8"}
                )
                result = response.json()
                logging.info(f"call_remove_mcp_tool result={result}")
            except Exception as e:
                logging.error(f"call_remove_mcp_tool: error {e}")

    def _merge_mcp_code(self, script:str, requirements:str) ->str:
        code = f"\"\"\"\n<requirements>\n{requirements}\n</requirements>\n\"\"\"\n{script}"
        code = dedent(code)
        return code

    def register_mcp_tool(self, tool_name: str, script:str, requirements:str) -> bool:
        return asyncio.run(self.async_register_mcp_tool(tool_name, script, requirements))

    async def async_register_mcp_tool(self, tool_name: str, script:str, requirements:str) -> bool:
        succeed = False
        try:
            if self.registry_url:
                code = self._merge_mcp_code(script, requirements)
                #logging.info(f"Registering MCP : name={tool_name}, code=\n{code}'")
                await self._call_remove_mcp_tool(tool_name)
                mcpbox_url = await self._call_add_mcp_tool(tool_name, code)

                if mcpbox_url:
                    logging.info("register_mcp: register tool[%s] success in McpBox with url: '%s'", tool_name, mcpbox_url)
                    succeed = True
                else:
                    logging.error("register_mcp: register tool[%s] fail in McpBox", tool_name)
        except Exception as e:
            logging.error("Failed to register MCP '%s': %s", tool_name, str(e))
            handle_error(e)

        return succeed