#!/usr/bin/env python3
"""
System Monitor MCP Server 入口点
"""

import asyncio
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
                server_version="1.0.1",
                capabilities=monitor_mcp.server.get_capabilities()
            )
        )

if __name__ == "__main__":
    asyncio.run(main())