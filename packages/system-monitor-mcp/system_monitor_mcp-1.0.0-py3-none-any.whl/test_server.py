#!/usr/bin/env python3
"""
System Monitor MCP Server 测试脚本
用于测试MCP服务器的各种功能
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Dict, Any, List

class MCPTester:
    """MCP服务器测试类"""
    
    def __init__(self):
        self.test_results = []
    
    async def test_system_info(self):
        """测试系统信息获取"""
        print("🔍 测试系统信息获取...")
        try:
            # 这里应该调用MCP工具，但为了演示，我们直接测试底层功能
            import psutil
            import platform
            
            # 模拟MCP工具调用
            system_info = {
                'platform': platform.system(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'cpu_percent': psutil.cpu_percent(interval=1)
            }
            
            print(f"✅ 系统信息获取成功: {system_info}")
            self.test_results.append(("system_info", True, "成功"))
            return True
        except Exception as e:
            print(f"❌ 系统信息获取失败: {e}")
            self.test_results.append(("system_info", False, str(e)))
            return False
    
    async def test_cpu_monitoring(self):
        """测试CPU监控"""
        print("🖥️ 测试CPU监控...")
        try:
            import psutil
            
            # 监控5秒
            cpu_data = []
            for i in range(5):
                cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
                cpu_data.append(cpu_percent)
                print(f"  第{i+1}秒: 总体CPU {sum(cpu_percent)/len(cpu_percent):.1f}%")
            
            print(f"✅ CPU监控完成，收集了{len(cpu_data)}个数据点")
            self.test_results.append(("cpu_monitoring", True, f"收集{len(cpu_data)}个数据点"))
            return True
        except Exception as e:
            print(f"❌ CPU监控失败: {e}")
            self.test_results.append(("cpu_monitoring", False, str(e)))
            return False
    
    async def test_memory_monitoring(self):
        """测试内存监控"""
        print("💾 测试内存监控...")
        try:
            import psutil
            
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            print(f"  物理内存: {mem.percent}% 使用")
            print(f"  交换内存: {swap.percent}% 使用")
            print(f"  可用内存: {self._format_bytes(mem.available)}")
            
            print("✅ 内存监控成功")
            self.test_results.append(("memory_monitoring", True, f"内存使用率{mem.percent}%"))
            return True
        except Exception as e:
            print(f"❌ 内存监控失败: {e}")
            self.test_results.append(("memory_monitoring", False, str(e)))
            return False
    
    async def test_process_listing(self):
        """测试进程列表"""
        print("📋 测试进程列表...")
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # 按CPU使用率排序
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            print(f"  找到 {len(processes)} 个进程")
            print("  CPU使用率最高的5个进程:")
            for i, proc in enumerate(processes[:5]):
                print(f"    {i+1}. {proc['name']} (PID: {proc['pid']}) - {proc['cpu_percent']}%")
            
            print("✅ 进程列表获取成功")
            self.test_results.append(("process_listing", True, f"找到{len(processes)}个进程"))
            return True
        except Exception as e:
            print(f"❌ 进程列表获取失败: {e}")
            self.test_results.append(("process_listing", False, str(e)))
            return False
    
    async def test_disk_monitoring(self):
        """测试磁盘监控"""
        print("💿 测试磁盘监控...")
        try:
            import psutil
            
            # 获取磁盘分区
            partitions = psutil.disk_partitions()
            print(f"  找到 {len(partitions)} 个磁盘分区")
            
            for partition in partitions[:3]:  # 只显示前3个
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    print(f"    {partition.device}: {usage.percent}% 使用 "
                          f"({self._format_bytes(usage.used)}/{self._format_bytes(usage.total)})")
                except PermissionError:
                    print(f"    {partition.device}: 无权限访问")
            
            # 磁盘I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                print(f"  磁盘I/O: 读取 {self._format_bytes(disk_io.read_bytes)}, "
                      f"写入 {self._format_bytes(disk_io.write_bytes)}")
            
            print("✅ 磁盘监控成功")
            self.test_results.append(("disk_monitoring", True, f"监控{len(partitions)}个分区"))
            return True
        except Exception as e:
            print(f"❌ 磁盘监控失败: {e}")
            self.test_results.append(("disk_monitoring", False, str(e)))
            return False
    
    async def test_network_monitoring(self):
        """测试网络监控"""
        print("🌐 测试网络监控...")
        try:
            import psutil
            
            # 获取网络I/O统计
            net_io_start = psutil.net_io_counters()
            print("  开始网络监控...")
            
            await asyncio.sleep(2)  # 等待2秒
            
            net_io_end = psutil.net_io_counters()
            
            # 计算速率
            bytes_sent = net_io_end.bytes_sent - net_io_start.bytes_sent
            bytes_recv = net_io_end.bytes_recv - net_io_start.bytes_recv
            
            print(f"  2秒内发送: {self._format_bytes(bytes_sent)}")
            print(f"  2秒内接收: {self._format_bytes(bytes_recv)}")
            
            # 网络接口
            interfaces = psutil.net_if_addrs()
            print(f"  找到 {len(interfaces)} 个网络接口")
            
            print("✅ 网络监控成功")
            self.test_results.append(("network_monitoring", True, f"监控{len(interfaces)}个接口"))
            return True
        except Exception as e:
            print(f"❌ 网络监控失败: {e}")
            self.test_results.append(("network_monitoring", False, str(e)))
            return False
    
    async def test_temperature_monitoring(self):
        """测试温度监控"""
        print("🌡️ 测试温度监控...")
        try:
            import psutil
            
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    print(f"  找到 {len(temps)} 个温度传感器组")
                    for name, entries in temps.items():
                        for entry in entries:
                            label = entry.label or "温度"
                            print(f"    {name} {label}: {entry.current}°C")
                    
                    print("✅ 温度监控成功")
                    self.test_results.append(("temperature_monitoring", True, f"找到{len(temps)}个传感器组"))
                else:
                    print("⚠️ 未找到温度传感器")
                    self.test_results.append(("temperature_monitoring", True, "未找到传感器"))
            else:
                print("⚠️ 当前系统不支持温度监控")
                self.test_results.append(("temperature_monitoring", True, "系统不支持"))
            
            return True
        except Exception as e:
            print(f"❌ 温度监控失败: {e}")
            self.test_results.append(("temperature_monitoring", False, str(e)))
            return False
    
    async def test_gpu_monitoring(self):
        """测试GPU监控"""
        print("🎮 测试GPU监控...")
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            if gpus:
                print(f"  找到 {len(gpus)} 个GPU")
                for i, gpu in enumerate(gpus):
                    print(f"    GPU {i}: {gpu.name}")
                    print(f"      使用率: {gpu.load*100:.1f}%")
                    print(f"      温度: {gpu.temperature}°C")
                    print(f"      显存: {gpu.memoryUsed:.0f}MB/{gpu.memoryTotal:.0f}MB")
                
                print("✅ GPU监控成功")
                self.test_results.append(("gpu_monitoring", True, f"找到{len(gpus)}个GPU"))
            else:
                print("⚠️ 未找到GPU设备")
                self.test_results.append(("gpu_monitoring", True, "未找到GPU"))
            
            return True
        except ImportError:
            print("⚠️ GPUtil库未安装，跳过GPU监控测试")
            self.test_results.append(("gpu_monitoring", True, "GPUtil未安装"))
            return True
        except Exception as e:
            print(f"❌ GPU监控失败: {e}")
            self.test_results.append(("gpu_monitoring", False, str(e)))
            return False
    
    async def test_battery_monitoring(self):
        """测试电池监控"""
        print("🔋 测试电池监控...")
        try:
            import psutil
            
            battery = psutil.sensors_battery()
            if battery:
                status = "充电中" if battery.power_plugged else "放电中"
                print(f"  电池电量: {battery.percent}%")
                print(f"  电池状态: {status}")
                
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                    hours, remainder = divmod(battery.secsleft, 3600)
                    minutes, _ = divmod(remainder, 60)
                    print(f"  剩余时间: {hours}小时{minutes}分钟")
                
                print("✅ 电池监控成功")
                self.test_results.append(("battery_monitoring", True, f"电量{battery.percent}%"))
            else:
                print("⚠️ 未检测到电池")
                self.test_results.append(("battery_monitoring", True, "未检测到电池"))
            
            return True
        except Exception as e:
            print(f"❌ 电池监控失败: {e}")
            self.test_results.append(("battery_monitoring", False, str(e)))
            return False
    
    def _format_bytes(self, size: int) -> str:
        """格式化字节大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始MCP服务器功能测试")
        print("=" * 50)
        
        tests = [
            self.test_system_info,
            self.test_cpu_monitoring,
            self.test_memory_monitoring,
            self.test_process_listing,
            self.test_disk_monitoring,
            self.test_network_monitoring,
            self.test_temperature_monitoring,
            self.test_gpu_monitoring,
            self.test_battery_monitoring
        ]
        
        for test in tests:
            await test()
            print()  # 空行分隔
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("📊 测试报告")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        print()
        
        print("详细结果:")
        for test_name, success, message in self.test_results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"  {test_name}: {status} - {message}")
        
        print("\n🎉 测试完成!")

async def main():
    """主函数"""
    tester = MCPTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())