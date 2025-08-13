#!/usr/bin/env python3
"""
System Monitor MCP Server 测试模块
"""

import asyncio
import unittest
from .server import SystemMonitorMCP

class TestSystemMonitorMCP(unittest.TestCase):
    """测试系统监控MCP服务器"""
    
    def setUp(self):
        """测试前准备"""
        self.monitor_mcp = SystemMonitorMCP()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.monitor_mcp)
        self.assertIsNotNone(self.monitor_mcp.server)
        self.assertEqual(self.monitor_mcp.server.name, "system-monitor-mcp")
    
    def test_monitoring_data_structure(self):
        """测试监控数据结构"""
        expected_keys = ['cpu', 'memory', 'disk', 'network', 'processes', 'temperatures', 'battery']
        for key in expected_keys:
            self.assertIn(key, self.monitor_mcp.monitoring_data)

if __name__ == "__main__":
    unittest.main()