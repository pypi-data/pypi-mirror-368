import re
import threading
import click
import uvicorn
import json

from textwrap import dedent
from mcp.server.fastmcp import FastMCP

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

mcp = FastMCP(name="Dynamic MCP Box Server")

def init_mcp():
    print("@todo: read code from DB, call dyn_add_mcp_tool, init MCP BOX")

init_mcp()


def dyn_add_mcp_tool(code: str):
    try:
        exec(code)
        #@todo add to DB
    except Exception as e:
        print(f'# dyn_add_mcp_tool error: {e}')

async def parse_code(request: Request)-> str:
    code = None
    _code = None
    try:
        body_bytes = await request.body()
        _code = body_bytes.decode('utf-8')
        code = _code.strip('"')
        code = re.sub(r'\\\\([nrt"])', lambda m: f'\\{m.group(1)}', code)
        code = dedent(code)
        print(f"=== parse_code:{code} end ===")
    except Exception as e:
        print(f'# parse_code error: {_code} \n{e}')
    return code

async def handle_add_mcp_tool(scope: Scope, receive: Receive, send: Send) -> None:
    _result = 0
    error  = ''

    request = Request(scope, receive)
    mcp_tool_name = request.query_params.get("mcp_tool_name")
    if(mcp._tool_manager.get_tool(mcp_tool_name)):
        _result = 1
        error = f"handle_add_mcp_tool: mcp_tool_name={mcp_tool_name} already exists, remove first !"
        print(error)
    else:
        print(f"handle_add_mcp_tool: mcp_tool_name={mcp_tool_name}")
        code = await parse_code(request)
        if(code):
            dyn_add_mcp_tool(code)
        else:
            _result = 2
            error = f"handle_add_mcp_tool: mcp_tool_name={mcp_tool_name} parse_code fail !"

    result = {'result': _result, 'error': error}
    response = Response(content=json.dumps(result), status_code=202,media_type="application/json")
    await response(scope, receive, send)

async def handle_remove_mcp_tool(scope: Scope, receive: Receive, send: Send) -> None:
    _result = 0
    error  = ''

    request = Request(scope, receive)
    mcp_tool_name = request.query_params.get("mcp_tool_name")
    if(mcp._tool_manager.get_tool(mcp_tool_name)):
        print(f"handle_remove_mcp_tool: mcp_tool_name={mcp_tool_name}")
        mcp._tool_manager._tools.pop(mcp_tool_name)
        # @todo remove From DB
    else:
        _result = 1
        error = f"handle_remove_mcp_tool: mcp_tool_name={mcp_tool_name}, not exists !"
        print(error)

    result = {'result': _result, 'error': error}
    response = Response(content=json.dumps(result), status_code=202,media_type="application/json")
    await response(scope, receive, send)

@click.command()
@click.option("--host", default="0.0.0.0", help="Host to listen on for SSE")
@click.option("--port", default=47070, help="Port to listen on for SSE")
def main(host: str, port: int):
    mcp.settings.host = host
    mcp.settings.port = port

    print(f"Start MCP Box Server host={host}, port={port} on thread !")
    mcp_thread = threading.Thread(target=mcp.run, kwargs={"transport": "sse"})
    mcp_thread.daemon = True  # 设置为守护线程，主线程退出时自动结束
    mcp_thread.start()

    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/add_mcp_tool/", app=handle_add_mcp_tool),
            Mount("/remove_mcp_tool/", app=handle_remove_mcp_tool),
        ],
    )

    port = port + 1
    print(f"Start Mcp Box Manager on host={host}, port={port}")
    uvicorn.run(starlette_app, host=host, port=port)

if __name__ == "__main__":
    main()
