import asyncio
import click

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import StdioServerParameters, stdio_client

@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="sse", help="Transport type")
@click.option("--host", default="localhost", help="Host to listen on for SSE")
@click.option("--port", default=17070, help="Port to listen on for SSE")
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
                    for tool in response.tools:
                        print(f"list_tools: TOOL name={tool.name}, description={tool.description}, "
                              f"outputSchema={tool.outputSchema} \ninputSchema=\n{tool.inputSchema}")

                    # call the runmcp tool
                    result = await session.call_tool("getAlarm", {"ip": "10.0.0.1"})
                    print('\n call_tool getAlarm result:', result)

                    result = await session.call_tool("getAlarmType", {"alarmId": "234"})
                    print('\n call_tool getAlarmType result:', result)

                    result = await session.call_tool("getBusiFault", {"objId": "12"})
                    print('\n call_tool getBusiFault result:', result)

                    result = await session.call_tool("getEquipFault", {"objId": "45"})
                    print('\n call_tool getEquipFault result:', result)

                    result = await session.call_tool("getMwareFault", {"objId": "78"})
                    print('\n call_tool getMwareFault result:', result)

                    result = await session.call_tool("getBusiFaultCause", {"faultCode": "F01"})
                    print('\n call_tool getBusiFaultCause result:', result)

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
