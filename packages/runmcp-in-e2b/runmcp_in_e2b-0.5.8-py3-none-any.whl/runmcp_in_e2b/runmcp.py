import anyio
import click

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport

from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import Response

import uvicorn

async def run_mcp_in_e2b(transport, cmd: str) -> str:
    mcp_server_url = "http://127.0.0.1:12020/sse" if transport == "sse" else "stdio"
    print(f"run uvx {cmd} in e2b, url={mcp_server_url}")
    return mcp_server_url


@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="sse", help="Transport type")
@click.option("--host", default="0.0.0.0", help="Host to listen on for SSE")
@click.option("--port", default=18080, help="Port to listen on for SSE")
def main(transport: str, host: str, port: int) -> int:
    app = Server("runmcp_in_e2b")

    @app.call_tool()
    async def runmcp(
        name: str, arguments: dict
    )-> list[types.TextContent]:
        print("runmcp_in_e2b === recv call_tool runmcp ===")

        if name != "runmcp":
            raise ValueError(f"Unknown tool: {name}")
        if "cmd" not in arguments:
            raise ValueError("Missing required argument 'url'")

        print(f"call run_mcp_in_e2b({arguments['cmd']})")
        result = await run_mcp_in_e2b(transport, arguments["cmd"])

        return [types.TextContent(type="text",text=result)]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        print("runmcp_in_e2b === list tools ===")
        return [
            types.Tool(
                name="runmcp",
                description="Run Mcp Server in E2B Sandbox",
                inputSchema={
                    "type": "object",
                    "required": ["cmd"],
                    "properties": {
                        "cmd": {
                            "type": "string",
                            "description": "Run Mcp by uvx command, not inculde uvx",
                        }
                    },
                },
            )
        ]


    if transport == "sse":

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
            return Response()

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        print(f"MCP Server runmcp_in_e2b run on localhost host={host}, port={port}")
        uvicorn.run(starlette_app, host=host, port=port)
    else:
        from mcp.server.stdio import stdio_server

        print(f"MCP Server runmcp_in_e2b run on stdio mode")
        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0

if __name__ == '__main__':
    main()
