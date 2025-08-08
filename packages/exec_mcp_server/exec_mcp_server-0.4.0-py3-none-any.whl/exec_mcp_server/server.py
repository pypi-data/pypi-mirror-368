# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import os
import logging
logger = logging.getLogger('mcp')
settings = {
    'log_level': 'DEBUG'
}
# 初始化mcp服务
mcp = FastMCP('exec-mcp-server', log_level='ERROR', settings=settings)
# 定义工具
@mcp.tool(name='命令执行', description='输入执行的命令')
async def command(
        prompt: str = Field(description='命令执行')
) -> str:

    result = os.popen(prompt).read()

    return str(result)
def run():
    mcp.run(transport='stdio')
if __name__ == "__main__":
    main()