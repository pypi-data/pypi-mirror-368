# Run MCP Server in E2B Sandbox
### 项目发布地址：https://pypi.org/project/runmcp-in-e2b/   
<br/>

- __MCP服务说明__  
Run MCP Server in E2B Sandbox 是一个样例（目前未运行E2B），说明如何发布托管一个MCP Server。
  - 支持stdio和sse两种模式：
    - sse：默认模式，默认端口 18080，指定端口启动参数：--port xxx 指定
    - stdio：启动参数：--transport stdio。
 
<br/>
  
- __开发环境和过程__
  - 注册PYPI账号 https://pypi.org/ ，创建PYPI_TOKEN，发布需要用；export $PYPI_TOKEN 到环境变量
  - 安装uv工具
  - uv项目结果
     - 建立项目目录runmcp_in_e2b,初始化，uv init （可以指定python版本），生成.venv
     - 编写程序，需要按照uvx要求的结构：  
       - src/runmcp_in_e2b  #项目目录  
       - test          #可选  
       - pyprojct.toml #自动生成，除了自动生成，需要添加[build-system]和[project.scripts]（uvx的启动入口） 
       - README.md     #项目说明，必须有  
       - LICENSE       #需要  
       - uv.lock       #根据pyprojct.toml，自动生成  
     - 添加依赖包：uv add click mcp starlette uvicorn，成功后会自动添加到pyprojct.toml的依赖  
     - 编译包：uv build，注意编译新版本，build 前需要手工清除dist，并需要修改pyprojct.toml的version，否则发布会版本冲突
     - 发布包：uv publish --token $PYPI_TOKEN , 成功后查看：https://pypi.org/project/runmcp-in-e2b/
<br/>
    
- __开发测试__  
     - 可以在pycharm中开发和运行代码，但是依赖包需要用uv add，pycharm自动识别会报错  
     - 进入项目目录，可以采用uv run runmcp-in-e2b --alarmtype 2 , alarmtype 默认 1(业务告警), 2(主机告警), 3(中间件告警)，运行MCP Server, runmcp-in-e2b 是在[project.scripts]配置的入口  
     - 注意：项目有两个工程，18080服务端口是runmcp，17070服务端口是bomc-fault，默认是17070  
<br/>
  
- __运行验证__  
  - uvx runmcp-in-e2b@latest ，latest标签会运行最新代码
  - 从 https://pypi.org/project/runmcp-in-e2b/#files 下载代码 runmcp_in_e2b-0.3.1.tar.gz ，解压到任意目录，有源码包
  - 进入解压目录后，uv sync 同步生成uv环境，进入test目录，uv run test_runmcp.py ，运行测试代码调用服务器  
  - 进入解压目录后，uv sync 同步生成uv环境，进入test目录，uv run test_bomcfault.py,运行测试代码调用服务器
<br/>

- __阿里云MCP Server 参数样例__  
{  
"mcpServers": {  
"runmcp_in_e2b": {  
"type": "stdio",  
"command": "uvx",    
"args": [  
"runmcp-in-e2b@latest",  
"--transport",  
"stdio"]}  
}  
} 
  
- __其他运行和安装方式__  
  - 不支持uvx install的模式，uvx运行的依赖是统一cache，第二次uvx启动，会从cache加载依赖，非常快，而且不需要手工remove依赖包
  - 支持 uv run的模式，直接运行服务，run之前先uv sync，指定python版本：uv sync --python /usr/local/bin/python3.12    
  - 支持 pip install runmcp-in-e2b  
  - pip install 完成后，采用 python -m runmcp_in_e2b 运行服务  
  - 支持python -m 启动模块，项目需要编写__main__.py 
  - 支持uv run 启动模块，项目需要编写__init__.py   
  - 如果采用pycharm 调试，Setting：Python Interpreter 选择当前目录的.ven，然后Run的配置选择module：runmcp_in_e2b ，修改Working目录为项目目录  
<br/>
