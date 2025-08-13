#!/usr/bin/env python3
"""
System Monitor MCP Server
基于系统资源监控程序的MCP服务器实现
提供系统监控、性能分析和资源管理功能
"""

import asyncio
import json
import logging
import sys
import time
from typing import Any, Dict, List, Optional, Sequence

import psutil
import numpy as np
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("system-monitor-mcp")

class SystemMonitorMCP:
    """系统监控MCP服务器类"""
    
    def __init__(self):
        self.server = Server("system-monitor-mcp")
        self.monitoring_data = {
            'cpu': [],
            'memory': [],
            'disk': [],
            'network': [],
            'processes': [],
            'temperatures': [],
            'battery': []
        }
        self.last_net_io = None
        self.last_disk_io = None
        self.last_time = time.time()
        
        # 注册工具和资源
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """注册MCP工具"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """列出所有可用工具"""
            return [
                Tool(
                    name="get_system_info",
                    description="获取系统基本信息（CPU、内存、磁盘等）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "detailed": {
                                "type": "boolean",
                                "description": "是否返回详细信息",
                                "default": False
                            }
                        }
                    }
                ),
                Tool(
                    name="monitor_cpu",
                    description="监控CPU使用情况",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "duration": {
                                "type": "integer",
                                "description": "监控持续时间（秒）",
                                "default": 5
                            },
                            "per_cpu": {
                                "type": "boolean",
                                "description": "是否显示每个CPU核心的使用率",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="monitor_memory",
                    description="监控内存使用情况",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_swap": {
                                "type": "boolean",
                                "description": "是否包含交换内存信息",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="monitor_disk",
                    description="监控磁盘使用情况和I/O",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_io": {
                                "type": "boolean",
                                "description": "是否包含磁盘I/O信息",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="monitor_network",
                    description="监控网络使用情况",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "duration": {
                                "type": "integer",
                                "description": "监控持续时间（秒）",
                                "default": 5
                            }
                        }
                    }
                ),
                Tool(
                    name="get_processes",
                    description="获取系统进程信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sort_by": {
                                "type": "string",
                                "description": "排序方式",
                                "enum": ["cpu", "memory", "name", "pid"],
                                "default": "cpu"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回进程数量限制",
                                "default": 20
                            },
                            "filter_name": {
                                "type": "string",
                                "description": "按进程名过滤",
                                "default": ""
                            }
                        }
                    }
                ),
                Tool(
                    name="kill_process",
                    description="终止指定进程",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pid": {
                                "type": "integer",
                                "description": "进程ID"
                            },
                            "force": {
                                "type": "boolean",
                                "description": "是否强制终止",
                                "default": False
                            }
                        },
                        "required": ["pid"]
                    }
                ),
                Tool(
                    name="get_temperatures",
                    description="获取系统温度信息",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_battery_info",
                    description="获取电池信息",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="system_performance_report",
                    description="生成系统性能报告",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "duration": {
                                "type": "integer",
                                "description": "监控持续时间（秒）",
                                "default": 30
                            },
                            "format": {
                                "type": "string",
                                "description": "报告格式",
                                "enum": ["text", "json"],
                                "default": "text"
                            }
                        }
                    }
                ),
                Tool(
                    name="start_monitoring",
                    description="开始持续监控系统资源",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "interval": {
                                "type": "integer",
                                "description": "监控间隔（秒）",
                                "default": 1
                            },
                            "duration": {
                                "type": "integer",
                                "description": "监控持续时间（秒）",
                                "default": 60
                            }
                        }
                    }
                ),
                Tool(
                    name="get_gpu_info",
                    description="获取GPU信息（如果可用）",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
            """处理工具调用"""
            try:
                if name == "get_system_info":
                    return await self._get_system_info(arguments.get("detailed", False))
                elif name == "monitor_cpu":
                    return await self._monitor_cpu(
                        arguments.get("duration", 5),
                        arguments.get("per_cpu", True)
                    )
                elif name == "monitor_memory":
                    return await self._monitor_memory(arguments.get("include_swap", True))
                elif name == "monitor_disk":
                    return await self._monitor_disk(arguments.get("include_io", True))
                elif name == "monitor_network":
                    return await self._monitor_network(arguments.get("duration", 5))
                elif name == "get_processes":
                    return await self._get_processes(
                        arguments.get("sort_by", "cpu"),
                        arguments.get("limit", 20),
                        arguments.get("filter_name", "")
                    )
                elif name == "kill_process":
                    return await self._kill_process(
                        arguments["pid"],
                        arguments.get("force", False)
                    )
                elif name == "get_temperatures":
                    return await self._get_temperatures()
                elif name == "get_battery_info":
                    return await self._get_battery_info()
                elif name == "system_performance_report":
                    return await self._system_performance_report(
                        arguments.get("duration", 30),
                        arguments.get("format", "text")
                    )
                elif name == "start_monitoring":
                    return await self._start_monitoring(
                        arguments.get("interval", 1),
                        arguments.get("duration", 60)
                    )
                elif name == "get_gpu_info":
                    return await self._get_gpu_info()
                else:
                    return [TextContent(type="text", text=f"未知工具: {name}")]
            except Exception as e:
                logger.error(f"工具调用错误 {name}: {e}")
                return [TextContent(type="text", text=f"工具执行错误: {str(e)}")]
    
    def _register_resources(self):
        """注册MCP资源"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """列出所有可用资源"""
            return [
                Resource(
                    uri="system://info",
                    name="系统信息",
                    description="当前系统的基本信息",
                    mimeType="application/json"
                ),
                Resource(
                    uri="system://cpu",
                    name="CPU状态",
                    description="实时CPU使用情况",
                    mimeType="application/json"
                ),
                Resource(
                    uri="system://memory",
                    name="内存状态",
                    description="实时内存使用情况",
                    mimeType="application/json"
                ),
                Resource(
                    uri="system://disk",
                    name="磁盘状态",
                    description="磁盘使用情况和I/O统计",
                    mimeType="application/json"
                ),
                Resource(
                    uri="system://network",
                    name="网络状态",
                    description="网络接口和流量统计",
                    mimeType="application/json"
                ),
                Resource(
                    uri="system://processes",
                    name="进程列表",
                    description="当前运行的进程信息",
                    mimeType="application/json"
                ),
                Resource(
                    uri="system://monitoring-data",
                    name="监控历史数据",
                    description="系统监控的历史数据",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """读取资源内容"""
            try:
                if uri == "system://info":
                    return json.dumps(await self._collect_system_info(), ensure_ascii=False, indent=2)
                elif uri == "system://cpu":
                    return json.dumps(await self._collect_cpu_info(), ensure_ascii=False, indent=2)
                elif uri == "system://memory":
                    return json.dumps(await self._collect_memory_info(), ensure_ascii=False, indent=2)
                elif uri == "system://disk":
                    return json.dumps(await self._collect_disk_info(), ensure_ascii=False, indent=2)
                elif uri == "system://network":
                    return json.dumps(await self._collect_network_info(), ensure_ascii=False, indent=2)
                elif uri == "system://processes":
                    return json.dumps(await self._collect_processes_info(), ensure_ascii=False, indent=2)
                elif uri == "system://monitoring-data":
                    return json.dumps(self.monitoring_data, ensure_ascii=False, indent=2)
                else:
                    return json.dumps({"error": f"未知资源: {uri}"}, ensure_ascii=False)
            except Exception as e:
                logger.error(f"资源读取错误 {uri}: {e}")
                return json.dumps({"error": str(e)}, ensure_ascii=False)
    
    # 工具实现方法
    async def _get_system_info(self, detailed: bool) -> Sequence[TextContent]:
        """获取系统基本信息"""
        info = await self._collect_system_info()
        
        if detailed:
            text = f"""
系统信息详细报告
==================

操作系统: {info['platform']['system']} {info['platform']['release']} ({info['platform']['version']})
架构: {info['platform']['machine']}
处理器: {info['platform']['processor']}
主机名: {info['platform']['node']}

CPU信息:
- 物理核心数: {info['cpu']['physical_cores']}
- 逻辑核心数: {info['cpu']['logical_cores']}
- 当前频率: {info['cpu']['current_freq']:.2f} MHz
- 最大频率: {info['cpu']['max_freq']:.2f} MHz
- 最小频率: {info['cpu']['min_freq']:.2f} MHz
- 当前使用率: {info['cpu']['usage']:.1f}%

内存信息:
- 总内存: {self._format_bytes(info['memory']['total'])}
- 可用内存: {self._format_bytes(info['memory']['available'])}
- 已用内存: {self._format_bytes(info['memory']['used'])}
- 使用率: {info['memory']['percent']:.1f}%

启动时间: {info['boot_time']}
运行时间: {info['uptime']}
"""
        else:
            text = f"""
系统概览
========
系统: {info['platform']['system']} {info['platform']['release']}
CPU: {info['cpu']['logical_cores']}核心, 使用率 {info['cpu']['usage']:.1f}%
内存: {self._format_bytes(info['memory']['used'])}/{self._format_bytes(info['memory']['total'])} ({info['memory']['percent']:.1f}%)
运行时间: {info['uptime']}
"""
        
        return [TextContent(type="text", text=text)]
    
    async def _monitor_cpu(self, duration: int, per_cpu: bool) -> Sequence[TextContent]:
        """监控CPU使用情况"""
        cpu_data = []
        
        for i in range(duration):
            if per_cpu:
                cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
                cpu_data.append({
                    'timestamp': time.time(),
                    'total': sum(cpu_percent) / len(cpu_percent),
                    'per_cpu': cpu_percent
                })
            else:
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_data.append({
                    'timestamp': time.time(),
                    'total': cpu_percent
                })
        
        # 生成报告
        avg_cpu = sum(data['total'] for data in cpu_data) / len(cpu_data)
        max_cpu = max(data['total'] for data in cpu_data)
        min_cpu = min(data['total'] for data in cpu_data)
        
        text = f"""
CPU监控报告 ({duration}秒)
===================
平均使用率: {avg_cpu:.1f}%
最高使用率: {max_cpu:.1f}%
最低使用率: {min_cpu:.1f}%

"""
        
        if per_cpu and cpu_data:
            text += "各核心平均使用率:\n"
            core_count = len(cpu_data[0]['per_cpu'])
            for i in range(core_count):
                core_avg = sum(data['per_cpu'][i] for data in cpu_data) / len(cpu_data)
                text += f"核心 {i+1}: {core_avg:.1f}%\n"
        
        # 保存监控数据
        self.monitoring_data['cpu'].extend(cpu_data)
        if len(self.monitoring_data['cpu']) > 1000:
            self.monitoring_data['cpu'] = self.monitoring_data['cpu'][-1000:]
        
        return [TextContent(type="text", text=text)]
    
    async def _monitor_memory(self, include_swap: bool) -> Sequence[TextContent]:
        """监控内存使用情况"""
        mem = psutil.virtual_memory()
        
        text = f"""
内存使用情况
============
总内存: {self._format_bytes(mem.total)}
可用内存: {self._format_bytes(mem.available)}
已用内存: {self._format_bytes(mem.used)}
空闲内存: {self._format_bytes(mem.free)}
使用率: {mem.percent:.1f}%
缓存: {self._format_bytes(mem.cached)}
缓冲区: {self._format_bytes(mem.buffers)}
"""
        
        if include_swap:
            swap = psutil.swap_memory()
            text += f"""
交换内存:
总交换空间: {self._format_bytes(swap.total)}
已用交换空间: {self._format_bytes(swap.used)}
空闲交换空间: {self._format_bytes(swap.free)}
交换使用率: {swap.percent:.1f}%
"""
        
        # 保存监控数据
        mem_data = {
            'timestamp': time.time(),
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent
        }
        self.monitoring_data['memory'].append(mem_data)
        if len(self.monitoring_data['memory']) > 1000:
            self.monitoring_data['memory'] = self.monitoring_data['memory'][-1000:]
        
        return [TextContent(type="text", text=text)]
    
    async def _monitor_disk(self, include_io: bool) -> Sequence[TextContent]:
        """监控磁盘使用情况"""
        # 获取磁盘分区信息
        partitions = psutil.disk_partitions()
        
        text = "磁盘使用情况\n============\n"
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                text += f"""
分区: {partition.device}
挂载点: {partition.mountpoint}
文件系统: {partition.fstype}
总空间: {self._format_bytes(usage.total)}
已用空间: {self._format_bytes(usage.used)}
空闲空间: {self._format_bytes(usage.free)}
使用率: {usage.percent:.1f}%
---
"""
            except PermissionError:
                text += f"分区 {partition.device}: 无权限访问\n---\n"
        
        if include_io:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                text += f"""
磁盘I/O统计:
读取次数: {disk_io.read_count:,}
写入次数: {disk_io.write_count:,}
读取字节: {self._format_bytes(disk_io.read_bytes)}
写入字节: {self._format_bytes(disk_io.write_bytes)}
读取时间: {disk_io.read_time:,} ms
写入时间: {disk_io.write_time:,} ms
"""
        
        return [TextContent(type="text", text=text)]
    
    async def _monitor_network(self, duration: int) -> Sequence[TextContent]:
        """监控网络使用情况"""
        # 获取初始网络统计
        net_io_start = psutil.net_io_counters()
        start_time = time.time()
        
        # 等待指定时间
        await asyncio.sleep(duration)
        
        # 获取结束时的网络统计
        net_io_end = psutil.net_io_counters()
        end_time = time.time()
        
        # 计算速率
        time_diff = end_time - start_time
        bytes_sent_rate = (net_io_end.bytes_sent - net_io_start.bytes_sent) / time_diff
        bytes_recv_rate = (net_io_end.bytes_recv - net_io_start.bytes_recv) / time_diff
        
        text = f"""
网络监控报告 ({duration}秒)
===================
发送速率: {self._format_bytes(bytes_sent_rate)}/s
接收速率: {self._format_bytes(bytes_recv_rate)}/s

总统计:
发送字节: {self._format_bytes(net_io_end.bytes_sent)}
接收字节: {self._format_bytes(net_io_end.bytes_recv)}
发送包数: {net_io_end.packets_sent:,}
接收包数: {net_io_end.packets_recv:,}
发送错误: {net_io_end.errout:,}
接收错误: {net_io_end.errin:,}
发送丢包: {net_io_end.dropout:,}
接收丢包: {net_io_end.dropin:,}

网络接口信息:
"""
        
        # 获取网络接口信息
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for interface, addrs in net_if_addrs.items():
            stats = net_if_stats.get(interface)
            text += f"\n接口: {interface}\n"
            if stats:
                text += f"状态: {'启用' if stats.isup else '禁用'}\n"
                text += f"速度: {stats.speed} Mbps\n"
                text += f"MTU: {stats.mtu}\n"
            
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    text += f"MAC地址: {addr.address}\n"
                elif addr.family == 2:  # AF_INET
                    text += f"IPv4地址: {addr.address}\n"
                    if addr.netmask:
                        text += f"子网掩码: {addr.netmask}\n"
            text += "---\n"
        
        return [TextContent(type="text", text=text)]
    
    async def _get_processes(self, sort_by: str, limit: int, filter_name: str) -> Sequence[TextContent]:
        """获取系统进程信息"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username', 'create_time']):
            try:
                pinfo = proc.info
                if filter_name and filter_name.lower() not in pinfo['name'].lower():
                    continue
                
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_percent': pinfo['memory_percent'],
                    'status': pinfo['status'],
                    'username': pinfo['username'] or 'N/A',
                    'create_time': pinfo['create_time']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # 排序
        if sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        elif sort_by == "name":
            processes.sort(key=lambda x: x['name'].lower())
        elif sort_by == "pid":
            processes.sort(key=lambda x: x['pid'])
        
        # 限制数量
        processes = processes[:limit]
        
        text = f"进程信息 (按{sort_by}排序，显示前{limit}个)\n"
        text += "=" * 60 + "\n"
        text += f"{'PID':<8} {'名称':<20} {'CPU%':<8} {'内存%':<8} {'状态':<12} {'用户':<15}\n"
        text += "-" * 60 + "\n"
        
        for proc in processes:
            text += f"{proc['pid']:<8} {proc['name'][:19]:<20} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.1f} {proc['status']:<12} {proc['username'][:14]:<15}\n"
        
        return [TextContent(type="text", text=text)]
    
    async def _kill_process(self, pid: int, force: bool) -> Sequence[TextContent]:
        """终止指定进程"""
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            if force:
                proc.kill()
                text = f"强制终止进程 {proc_name} (PID: {pid}) 成功"
            else:
                proc.terminate()
                text = f"终止进程 {proc_name} (PID: {pid}) 成功"
            
        except psutil.NoSuchProcess:
            text = f"进程 PID {pid} 不存在"
        except psutil.AccessDenied:
            text = f"没有权限终止进程 PID {pid}"
        except Exception as e:
            text = f"终止进程失败: {str(e)}"
        
        return [TextContent(type="text", text=text)]
    
    async def _get_temperatures(self) -> Sequence[TextContent]:
        """获取系统温度信息"""
        text = "系统温度信息\n============\n"
        
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        text += f"{name}:\n"
                        for entry in entries:
                            label = entry.label or "温度"
                            text += f"  {label}: {entry.current}°C"
                            if entry.high:
                                text += f" (高温警告: {entry.high}°C)"
                            if entry.critical:
                                text += f" (临界温度: {entry.critical}°C)"
                            text += "\n"
                        text += "\n"
                else:
                    text += "未检测到温度传感器\n"
            else:
                text += "当前系统不支持温度监控\n"
            
            # 尝试获取GPU温度
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    text += "GPU温度:\n"
                    for i, gpu in enumerate(gpus):
                        text += f"  GPU {i} ({gpu.name}): {gpu.temperature}°C\n"
            except ImportError:
                text += "GPU温度监控需要安装 GPUtil 库\n"
            except Exception as e:
                text += f"GPU温度获取失败: {str(e)}\n"
                
        except Exception as e:
            text += f"温度信息获取失败: {str(e)}\n"
        
        return [TextContent(type="text", text=text)]
    
    async def _get_battery_info(self) -> Sequence[TextContent]:
        """获取电池信息"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                text = "未检测到电池或系统不支持电池监控"
            else:
                status = "充电中" if battery.power_plugged else "放电中"
                time_left = "未知"
                
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                    hours, remainder = divmod(battery.secsleft, 3600)
                    minutes, _ = divmod(remainder, 60)
                    time_left = f"{hours}小时{minutes}分钟"
                
                text = f"""
电池信息
========
电量: {battery.percent}%
状态: {status}
剩余时间: {time_left}
电源连接: {'是' if battery.power_plugged else '否'}
"""
        except Exception as e:
            text = f"电池信息获取失败: {str(e)}"
        
        return [TextContent(type="text", text=text)]
    
    async def _system_performance_report(self, duration: int, format_type: str) -> Sequence[TextContent]:
        """生成系统性能报告"""
        report_data = {
            'timestamp': time.time(),
            'duration': duration,
            'cpu': [],
            'memory': [],
            'disk_io': [],
            'network_io': []
        }
        
        # 收集性能数据
        start_net_io = psutil.net_io_counters()
        start_disk_io = psutil.disk_io_counters()
        
        for i in range(duration):
            # CPU数据
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            report_data['cpu'].append({
                'timestamp': time.time(),
                'total': sum(cpu_percent) / len(cpu_percent),
                'per_cpu': cpu_percent
            })
            
            # 内存数据
            mem = psutil.virtual_memory()
            report_data['memory'].append({
                'timestamp': time.time(),
                'percent': mem.percent,
                'used': mem.used,
                'available': mem.available
            })
        
        # 网络和磁盘I/O统计
        end_net_io = psutil.net_io_counters()
        end_disk_io = psutil.disk_io_counters()
        
        if format_type == "json":
            report_data['network_io'] = {
                'bytes_sent': end_net_io.bytes_sent - start_net_io.bytes_sent,
                'bytes_recv': end_net_io.bytes_recv - start_net_io.bytes_recv,
                'packets_sent': end_net_io.packets_sent - start_net_io.packets_sent,
                'packets_recv': end_net_io.packets_recv - start_net_io.packets_recv
            }
            
            if end_disk_io and start_disk_io:
                report_data['disk_io'] = {
                    'read_bytes': end_disk_io.read_bytes - start_disk_io.read_bytes,
                    'write_bytes': end_disk_io.write_bytes - start_disk_io.write_bytes,
                    'read_count': end_disk_io.read_count - start_disk_io.read_count,
                    'write_count': end_disk_io.write_count - start_disk_io.write_count
                }
            
            return [TextContent(type="text", text=json.dumps(report_data, ensure_ascii=False, indent=2))]
        
        else:  # text format
            # 计算统计数据
            cpu_avg = sum(data['total'] for data in report_data['cpu']) / len(report_data['cpu'])
            cpu_max = max(data['total'] for data in report_data['cpu'])
            cpu_min = min(data['total'] for data in report_data['cpu'])
            
            mem_avg = sum(data['percent'] for data in report_data['memory']) / len(report_data['memory'])
            mem_max = max(data['percent'] for data in report_data['memory'])
            mem_min = min(data['percent'] for data in report_data['memory'])
            
            net_sent = end_net_io.bytes_sent - start_net_io.bytes_sent
            net_recv = end_net_io.bytes_recv - start_net_io.bytes_recv
            
            text = f"""
系统性能报告 ({duration}秒监控)
===============================

CPU性能:
- 平均使用率: {cpu_avg:.1f}%
- 最高使用率: {cpu_max:.1f}%
- 最低使用率: {cpu_min:.1f}%

内存性能:
- 平均使用率: {mem_avg:.1f}%
- 最高使用率: {mem_max:.1f}%
- 最低使用率: {mem_min:.1f}%

网络流量:
- 发送数据: {self._format_bytes(net_sent)}
- 接收数据: {self._format_bytes(net_recv)}
- 平均发送速率: {self._format_bytes(net_sent/duration)}/s
- 平均接收速率: {self._format_bytes(net_recv/duration)}/s
"""
            
            if end_disk_io and start_disk_io:
                disk_read = end_disk_io.read_bytes - start_disk_io.read_bytes
                disk_write = end_disk_io.write_bytes - start_disk_io.write_bytes
                text += f"""
磁盘I/O:
- 读取数据: {self._format_bytes(disk_read)}
- 写入数据: {self._format_bytes(disk_write)}
- 平均读取速率: {self._format_bytes(disk_read/duration)}/s
- 平均写入速率: {self._format_bytes(disk_write/duration)}/s
"""
            
            return [TextContent(type="text", text=text)]
    
    async def _start_monitoring(self, interval: int, duration: int) -> Sequence[TextContent]:
        """开始持续监控系统资源"""
        monitoring_data = []
        end_time = time.time() + duration
        
        text = f"开始监控系统资源 (间隔: {interval}秒, 持续: {duration}秒)\n"
        text += "=" * 50 + "\n"
        
        while time.time() < end_time:
            timestamp = time.time()
            
            # 收集数据
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            
            data_point = {
                'timestamp': timestamp,
                'cpu_percent': cpu_percent,
                'memory_percent': mem.percent,
                'memory_used': mem.used,
                'memory_available': mem.available
            }
            
            monitoring_data.append(data_point)
            
            # 实时显示
            text += f"[{time.strftime('%H:%M:%S', time.localtime(timestamp))}] "
            text += f"CPU: {cpu_percent:5.1f}% | 内存: {mem.percent:5.1f}% "
            text += f"({self._format_bytes(mem.used)}/{self._format_bytes(mem.total)})\n"
            
            await asyncio.sleep(interval)
        
        # 保存监控数据
        self.monitoring_data['continuous'] = monitoring_data
        
        # 生成摘要
        if monitoring_data:
            avg_cpu = sum(d['cpu_percent'] for d in monitoring_data) / len(monitoring_data)
            avg_mem = sum(d['memory_percent'] for d in monitoring_data) / len(monitoring_data)
            max_cpu = max(d['cpu_percent'] for d in monitoring_data)
            max_mem = max(d['memory_percent'] for d in monitoring_data)
            
            text += f"\n监控摘要:\n"
            text += f"平均CPU使用率: {avg_cpu:.1f}%\n"
            text += f"最高CPU使用率: {max_cpu:.1f}%\n"
            text += f"平均内存使用率: {avg_mem:.1f}%\n"
            text += f"最高内存使用率: {max_mem:.1f}%\n"
            text += f"数据点数量: {len(monitoring_data)}\n"
        
        return [TextContent(type="text", text=text)]
    
    async def _get_gpu_info(self) -> Sequence[TextContent]:
        """获取GPU信息"""
        text = "GPU信息\n========\n"
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            if not gpus:
                text += "未检测到GPU设备\n"
            else:
                for i, gpu in enumerate(gpus):
                    text += f"GPU {i}: {gpu.name}\n"
                    text += f"  使用率: {gpu.load*100:.1f}%\n"
                    text += f"  显存使用: {gpu.memoryUsed:.0f}MB / {gpu.memoryTotal:.0f}MB ({gpu.memoryUtil*100:.1f}%)\n"
                    text += f"  温度: {gpu.temperature}°C\n"
                    text += f"  UUID: {gpu.uuid}\n"
                    text += f"  驱动版本: {gpu.driver}\n"
                    text += f"  显示模式: {gpu.display_mode}\n"
                    text += f"  显示激活: {gpu.display_active}\n"
                    text += "\n"
        
        except ImportError:
            text += "GPU监控需要安装 GPUtil 库\n"
            text += "安装命令: pip install gputil\n"
        except Exception as e:
            text += f"GPU信息获取失败: {str(e)}\n"
        
        return [TextContent(type="text", text=text)]
    
    # 资源收集方法
    async def _collect_system_info(self) -> Dict[str, Any]:
        """收集系统基本信息"""
        import platform
        
        # CPU信息
        cpu_freq = psutil.cpu_freq()
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'current_freq': cpu_freq.current if cpu_freq else 0,
            'max_freq': cpu_freq.max if cpu_freq else 0,
            'min_freq': cpu_freq.min if cpu_freq else 0,
            'usage': psutil.cpu_percent(interval=1)
        }
        
        # 内存信息
        mem = psutil.virtual_memory()
        memory_info = {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'free': mem.free,
            'percent': mem.percent
        }
        
        # 系统信息
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        return {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'node': platform.node()
            },
            'cpu': cpu_info,
            'memory': memory_info,
            'boot_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time)),
            'uptime': self._format_uptime(uptime_seconds)
        }
    
    async def _collect_cpu_info(self) -> Dict[str, Any]:
        """收集CPU信息"""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        
        return {
            'timestamp': time.time(),
            'usage_total': sum(cpu_percent) / len(cpu_percent),
            'usage_per_cpu': cpu_percent,
            'frequency': {
                'current': cpu_freq.current if cpu_freq else 0,
                'max': cpu_freq.max if cpu_freq else 0,
                'min': cpu_freq.min if cpu_freq else 0
            },
            'cores': {
                'physical': psutil.cpu_count(logical=False),
                'logical': psutil.cpu_count(logical=True)
            }
        }
    
    async def _collect_memory_info(self) -> Dict[str, Any]:
        """收集内存信息"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'timestamp': time.time(),
            'virtual': {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'free': mem.free,
                'percent': mem.percent,
                'cached': mem.cached,
                'buffers': mem.buffers
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
        }
    
    async def _collect_disk_info(self) -> Dict[str, Any]:
        """收集磁盘信息"""
        partitions = psutil.disk_partitions()
        disk_info = {
            'timestamp': time.time(),
            'partitions': [],
            'io_counters': None
        }
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info['partitions'].append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except PermissionError:
                disk_info['partitions'].append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'error': 'Permission denied'
                })
        
        # 磁盘I/O统计
        disk_io = psutil.disk_io_counters()
        if disk_io:
            disk_info['io_counters'] = {
                'read_count': disk_io.read_count,
                'write_count': disk_io.write_count,
                'read_bytes': disk_io.read_bytes,
                'write_bytes': disk_io.write_bytes,
                'read_time': disk_io.read_time,
                'write_time': disk_io.write_time
            }
        
        return disk_info
    
    async def _collect_network_info(self) -> Dict[str, Any]:
        """收集网络信息"""
        net_io = psutil.net_io_counters()
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        network_info = {
            'timestamp': time.time(),
            'io_counters': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout
            },
            'interfaces': {}
        }
        
        for interface, addrs in net_if_addrs.items():
            stats = net_if_stats.get(interface)
            interface_info = {
                'addresses': [],
                'stats': {}
            }
            
            if stats:
                interface_info['stats'] = {
                    'isup': stats.isup,
                    'duplex': stats.duplex,
                    'speed': stats.speed,
                    'mtu': stats.mtu
                }
            
            for addr in addrs:
                addr_info = {
                    'family': addr.family,
                    'address': addr.address
                }
                if addr.netmask:
                    addr_info['netmask'] = addr.netmask
                if addr.broadcast:
                    addr_info['broadcast'] = addr.broadcast
                
                interface_info['addresses'].append(addr_info)
            
            network_info['interfaces'][interface] = interface_info
        
        return network_info
    
    async def _collect_processes_info(self) -> Dict[str, Any]:
        """收集进程信息"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username', 'create_time', 'cmdline']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_percent': pinfo['memory_percent'],
                    'status': pinfo['status'],
                    'username': pinfo['username'] or 'N/A',
                    'create_time': pinfo['create_time'],
                    'cmdline': ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # 按CPU使用率排序
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return {
            'timestamp': time.time(),
            'total_processes': len(processes),
            'processes': processes[:50]  # 只返回前50个进程
        }
    
    # 工具方法
    def _format_bytes(self, size: int) -> str:
        """格式化字节大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def _format_uptime(self, seconds: float) -> str:
        """格式化运行时间"""
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}天 {hours}小时 {minutes}分钟"
        elif hours > 0:
            return f"{hours}小时 {minutes}分钟"
        else:
            return f"{minutes}分钟 {seconds}秒"

async def main():
    """主函数"""
    # 创建MCP服务器实例
    monitor_mcp = SystemMonitorMCP()
    
    # 运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await monitor_mcp.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="system-monitor-mcp",
                server_version="1.0.0",
                capabilities=monitor_mcp.server.get_capabilities()
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
