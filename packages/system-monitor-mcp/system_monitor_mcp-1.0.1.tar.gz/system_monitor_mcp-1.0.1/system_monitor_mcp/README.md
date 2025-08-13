# System Monitor MCP

基于系统资源监控程序开发的MCP服务器，提供全面的系统监控、性能分析和资源管理功能。

## 安装方法

```bash
pip install system-monitor-mcp
```

或者使用uvx安装（推荐）:

```bash
uvx system-monitor-mcp
```

## 配置MCP客户端

在你的MCP客户端配置中添加：

```json
{
  "mcpServers": {
    "system-monitor-mcp": {
      "command": "uvx",
      "args": [
        "--index-url",
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "system-monitor-mcp"
      ]
    }
  }
}
```

## 功能特性

- 系统信息监控（CPU、内存、磁盘、网络等）
- 进程管理
- 温度监控
- 电池状态监控
- GPU信息监控（需要安装GPUtil）
- 性能报告生成
- 持续监控系统资源

## 可用工具

- `get_system_info` - 获取系统基本信息
- `monitor_cpu` - CPU使用率监控
- `monitor_memory` - 内存使用监控
- `monitor_disk` - 磁盘使用和I/O监控
- `monitor_network` - 网络流量监控
- `get_processes` - 获取进程列表
- `get_temperatures` - 获取硬件温度
- `get_battery_info` - 获取电池信息
- `get_gpu_info` - 获取GPU信息
- `system_performance_report` - 生成性能报告
- `start_monitoring` - 开始持续监控
- `kill_process` - 终止进程

## 可用资源

- `system://info` - 系统基本信息
- `system://cpu` - CPU实时状态
- `system://memory` - 内存实时状态
- `system://disk` - 磁盘状态
- `system://network` - 网络状态
- `system://processes` - 进程列表
- `system://monitoring-data` - 监控历史数据