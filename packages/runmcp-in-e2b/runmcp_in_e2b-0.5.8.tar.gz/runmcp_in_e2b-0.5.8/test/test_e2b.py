from e2b_code_interpreter import Sandbox
import re
from textwrap import dedent

t1_code = """
from typing import Annotated, Optional
from pydantic import Field
@mcp.tool(
    description='主机故障解决方案'
)
def getHostFaultCause(
    faultCode: Annotated[str, Field(description="故障代码")],
    severity: Annotated[int, Field(default=2, description="故障严重等级，1-5，默认为1")]
    ):
    print(f"getHostFaultCause: faultCode={faultCode}, severity={severity}")
    faultCause = ""
    if (faultCode == 'F02'):
        faultCause = "主机磁盘故障，需要更换磁盘"
    else:
        faultCause = f"未知故障，故障代码{faultCode}"        
    return faultCause

getHostFaultCause('F02', 2)
"""

t2_code = """
@mcp.tool(
    description='中间件故障解决方案',
    annotations={
    "parameters": {
        "faultCode": {"description": "故障代码"},
        "severity": {"description": "故障严重等级，1-5，默认为1"}
    }
}
)
def getMiddleFaultCause(
    faultCode: str,
    severity: int=1
    ):
    print(f"getHostFaultCause: faultCode={faultCode}, severity={severity}")
    faultCause = ""
    if (faultCode == 'F03'):
        faultCause = "中间件redis故障，重启redis"
    else:
        faultCause = f"未知故障，故障代码{faultCode}"        
    return faultCause

getMiddleFaultCause(faultCode='F03')
"""



def prepare_sandbox_code(raw_code: str)->str:
    code = re.sub(r'@mcp\.tool\(.*?\)\s+def', 'def', raw_code, flags=re.DOTALL)
    code = dedent(code)
    print(code)
    return code

sandbox = Sandbox()

# sandbox.commands.run("pip install pydantic")
# sandbox.commands.run("pip install typing")
code = prepare_sandbox_code(t1_code)
execution = sandbox.run_code(code)
print(execution.text)

code = prepare_sandbox_code(t2_code)
execution = sandbox.run_code(code)
print(execution.text)