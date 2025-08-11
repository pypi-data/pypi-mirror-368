import json

import anyio
import click
from typing import Dict, Any

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport

from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import Response

import uvicorn
alarm_type = 0

async def _getAlarm(ip: str) -> Dict[str, Any]:
    print(f"_getAlarm, ip={ip}")
    return {"alarmId":"alm0123", "objId": "obj567"}

async def _getAlarmType(alarmId: str, alarm_type:int ) -> str:
    print(f"_getAlarmType, alarmId={alarmId}, alarm_type={alarm_type}")
    return f"{alarm_type}"

async def _getFault(type: int, objId: str) -> Dict[str, Any]:
    print(f"_getFault, type={type}, objId={objId}")
    result = {"faultCode": "", "faultDesc": "无故障"}
    if(type == 1) :
        result = {"faultCode": "F01", "faultDesc": "业务充值故障"}
    elif(type == 2) :
        result = {"faultCode": "F02", "faultDesc": "主机硬盘故障"}
    elif(type == 3)  :
        result = {"faultCode": "F03", "faultDesc": "redis故障"}
    else :
        result = {"faultCode": f"F{type}", "faultDesc": "未知故障"}
    return result

async def _getFaultCause(faultCode: str) -> str:
    print(f"_getFaultCause, faultCode={faultCode}")
    faultCause = ""
    if (faultCode == 'F01'):
        faultCause = "业务充值故障，充值程序导致，重启充值程序"
    else:
        faultCause = f"未知故障，故障代码{faultCode}"
    return  faultCause

@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="sse", help="Transport type")
@click.option("--host", default="0.0.0.0", help="Host to listen on for SSE")
@click.option("--port", default=17070, help="Port to listen on for SSE")
@click.option("--alarmtype", default=1, help="AlarmType Set")
def main(transport: str, host: str, port: int, alarmtype:int) -> int:
    app = Server("bomc_fault")
    alarm_type = alarmtype

    @app.call_tool()
    async def call_tool(
        name: str, arguments: dict
    )-> list[types.TextContent]:
        print(f"bomc_fault === recv call_tool {name} ===")
        result = None
        if(name == 'getAlarm'):
            ip = arguments['ip']
            _result = await _getAlarm(ip)
            _result = json.dumps(_result)
        elif(name == 'getAlarmType'):
            alarmId = arguments['alarmId']
            _result = await _getAlarmType(alarmId, alarm_type)
        elif(name == 'getBusiFault'):
            objId = arguments['objId']
            _result = await _getFault(1, objId)
            _result = json.dumps(_result)
        elif (name == 'getEquipFault'):
            objId = arguments['objId']
            _result = await _getFault(2, objId)
            _result = json.dumps(_result)
        elif (name == 'getMwareFault'):
            objId = arguments['objId']
            _result = await _getFault(3, objId)
            _result = json.dumps(_result)
        elif (name == 'getBusiFaultCause'):
            faultCode = arguments['faultCode']
            _result = await _getFaultCause(faultCode)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [types.TextContent(type="text", text=_result)]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        print(f"bomc_fault === recv list_tools ===")
        return [
            types.Tool(
                name="getBusiFaultCause",
                description="业务故障解决方案",
                inputSchema={
                    "type": "object",
                    "required": ["faultCode"],
                    "properties": {
                        "faultCode": {
                            "type": "string",
                            "description": "故障代码",
                        }
                    },
                },
                # outputSchema={
                #     "type": "string",
                #     "description": "业务故障解决方案"
                # }
            ),
            types.Tool(
                name="getMwareFault",
                description="中间件故障定位",
                inputSchema={
                    "type": "object",
                    "required": ["objId"],
                    "properties": {
                        "objId": {
                            "type": "string",
                            "description": "故障对象的ID",
                        }
                    },
                },
                # outputSchema={
                #     "type": "object",
                #     "required": ["faultCode", "faultDesc"],
                #     "properties": {
                #         "faultCode": {
                #             "type": "string",
                #             "description": "故障代码"
                #         },
                #         "faultDesc": {
                #             "type": "string",
                #             "description": "故障信息描述"
                #         }
                #     }
                # }
            ),
            types.Tool(
                name="getEquipFault",
                description="设备故障定位",
                inputSchema={
                    "type": "object",
                    "required": ["objId"],
                    "properties": {
                        "objId": {
                            "type": "string",
                            "description": "故障对象的ID",
                        }
                    },
                },
                # outputSchema={
                #     "type": "object",
                #     "required": ["faultCode", "faultDesc"],
                #     "properties": {
                #         "faultCode": {
                #             "type": "string",
                #             "description": "故障代码"
                #         },
                #         "faultDesc": {
                #             "type": "string",
                #             "description": "故障信息描述"
                #         }
                #     }
                # }
            ),
            types.Tool(
                name="getBusiFault",
                description="业务故障定位",
                inputSchema={
                    "type": "object",
                    "required": ["objId"],
                    "properties": {
                        "objId": {
                            "type": "string",
                            "description": "故障对象的ID",
                        }
                    },
                },
                # outputSchema={
                #     "type": "object",
                #     "required": ["faultCode", "faultDesc"],
                #     "properties": {
                #         "faultCode": {
                #             "type": "string",
                #             "description": "故障代码"
                #         },
                #         "faultDesc": {
                #             "type": "string",
                #             "description": "故障信息描述"
                #         }
                #     }
                # }
            ),
            types.Tool(
                name="getAlarmType",
                description="获取告警类型，返回值枚举：1：业务类型告警、2：设备类型告警、3：中间件类型告警",
                inputSchema={
                    "type": "object",
                    "required": ["alarmId"],
                    "properties": {
                        "alarmId": {
                            "type": "string",
                            "description": "告警ID",
                        }
                    },
                },
                # outputSchema={
                #     "type": "integer",
                #     "description": "告警类型的枚举：1: 业务故障, 2: 设备故障, 3:中间件故障"
                # }
            ),
            types.Tool(
                name="getAlarm",
                description="查询对象告警",
                inputSchema={
                    "type": "object",
                    "required": ["ip"],
                    "properties": {
                        "ip": {
                            "type": "string",
                            "description": "告警对象的IP地址",
                        }
                    },
                },
                # outputSchema={
                #     "type": "object",
                #     "required": ["alarmId", "objId"],
                #     "properties": {
                #         "alarmId": {
                #             "type": "string",
                #             "description": "告警的ID"
                #         },
                #         "objId": {
                #             "type": "string",
                #             "description": "告警所属对象的ID"
                #         }
                #     },
                # }
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

        print(f"MCP Server bomc-fault run on localhost host={host}, port={port}")
        uvicorn.run(starlette_app, host=host, port=port)
    else:
        from mcp.server.stdio import stdio_server

        print(f"MCP Server bomc-fault run on stdio mode")
        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0

if __name__ == '__main__':
    main()
