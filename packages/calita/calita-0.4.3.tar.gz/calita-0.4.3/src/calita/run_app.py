import sys

import click
from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP

from calita.manager_agent import ManagerAgent
from calita.utils.utils import get_global_config, setup_logging


def run_mcp(host: str, port: int, transport: str="sse") -> None:
    mcp = FastMCP("Calita Server")
    config = get_global_config("config.yaml")
    setup_logging(config)
    mcp.settings.host = host
    mcp.settings.port = port

    @mcp.tool(
        description='Base on request, AI generate answer'
    )
    def calita_generate(request: Annotated[str, Field(description="user request")])->str:
        manager = ManagerAgent(config)
        result = manager.generate(request)
        return result

    mcp.run(transport=transport)

def run_cli():
    config = get_global_config("config.yaml")
    setup_logging(config)

    manager_agent: ManagerAgent = ManagerAgent(config)

    # For single task mode, prompt the user for a natural language query.
    task: str = input("Enter a natural language query/task: ").strip()
    if not task:
        print("No task entered. Exiting.")
        sys.exit(0)
    # Process the task through ManagerAgent orchestration.
    result: str = manager_agent.generate(task)
    print("Result from ManagerAgent:")
    print(result)

@click.command()
@click.option("--mode", type=click.Choice(["sse", "streamable-http", "cli"]),  default="cli", help="App Type：Human input cli or MCP")
@click.option("--host", default="localhost", help="Host to listen on for SSE")
@click.option("--port", default=57070, help="Port to listen on for SSE")
def main(mode: str, host: str, port: int) :
    try:
        if mode == "cli":
            run_cli()
        else:
            run_mcp(host, port, mode)
    except Exception as e:
        print(f"An error occurred in the application: {str(e)}")
        sys.exit(1)
        
if __name__ == "__main__":
    #run_mcp("localhost", 57070, "sse")
    run_cli()