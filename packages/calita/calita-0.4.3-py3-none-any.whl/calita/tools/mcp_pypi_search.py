import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Pypi Search Server")

@mcp.tool()
async def pypi_search(query: str):
    """通过PyPI API搜索Python包"""
    async with httpx.AsyncClient() as client:
        print(f"pypi_search: excute query={pypi_search}")
        response = await client.get(f"https://pypi.org/search/?q={query}")
        # @todo parse response
        return "unknown"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(pypi_search("runmcp-in-e2b"))
    print(result)
    #main()