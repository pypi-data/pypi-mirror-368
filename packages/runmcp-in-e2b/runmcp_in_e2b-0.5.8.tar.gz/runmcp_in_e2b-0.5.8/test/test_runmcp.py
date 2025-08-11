import asyncio
import click

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import StdioServerParameters, stdio_client

@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="sse", help="Transport type")
@click.option("--host", default="localhost", help="Host to listen on for SSE")
@click.option("--port", default=18080, help="Port to listen on for SSE")
def main(transport: str, host: str, port: int):
    if transport == "sse":
        url = f"http://{host}:{port}/sse"
        async def run_sse(url):
            async with sse_client(url, sse_read_timeout=5) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()

                    # list available tools
                    response = await session.list_tools()
                    tools = response.tools
                    print("\n list_tools:", [(tool.name, tool.description) for tool in tools])

                    # call the runmcp tool
                    result = await session.call_tool("runmcp", {"cmd": "mcp-server-fetch"})
                    print('\n call_tool runmcp result:', result)

        asyncio.run(run_sse(url))
    else:
        async def run_stdio():
            async with stdio_client(
                    #StdioServerParameters(command="uv", args=["run", "runmcp_in_e2b", "--transport", "stdio"])
                    StdioServerParameters(command="uvx", args=["runmcp_in_e2b", "--transport", "stdio"])
            ) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # List available tools
                    tools = await session.list_tools()
                    print(tools)

                    # Call the runmcp tool
                    result = await session.call_tool("runmcp", {"cmd": "mcp-server-fetch"})
                    print(result)

        asyncio.run(run_stdio())

if __name__ == "__main__":
    main()
