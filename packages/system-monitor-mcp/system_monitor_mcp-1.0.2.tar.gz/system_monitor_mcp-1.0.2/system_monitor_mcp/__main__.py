#!/usr/bin/env python3
"""
System Monitor MCP Server 入口点
"""

import asyncio
import sys
from .server import SystemMonitorMCP

async def main():
    """主函数"""
    # 创建MCP服务器实例
    monitor_mcp = SystemMonitorMCP()
    
    # 运行服务器
    from mcp.server.stdio import stdio_server
    from mcp.server.models import InitializationOptions
    
    async with stdio_server() as (read_stream, write_stream):
        await monitor_mcp.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="system-monitor-mcp",
                server_version="1.0.2",
                capabilities=monitor_mcp.server.get_capabilities()
            )
        )

# 无论是作为脚本运行还是作为模块导入，都确保main()被执行
if __name__ == "__main__":
    asyncio.run(main())
else:
    # 当作为模块导入时，也需要执行main()
    # 这是为了支持 python -m system_monitor_mcp 或 uvx system-monitor-mcp 的调用方式
    if not asyncio.get_event_loop().is_running():
        asyncio.run(main())
