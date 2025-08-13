# System Monitor MCP Server

基于原始系统资源监控程序开发的MCP服务器，提供全面的系统监控、性能分析和资源管理功能。

## 功能特性

### 🖥️ 系统监控工具
- **系统信息获取** - 获取操作系统、CPU、内存等基本信息
- **CPU监控** - 实时监控CPU使用率，支持单核和多核显示
- **内存监控** - 监控物理内存和交换内存使用情况
- **磁盘监控** - 监控磁盘使用率和I/O性能
- **网络监控** - 监控网络接口状态和流量统计
- **进程管理** - 查看和管理系统进程
- **温度监控** - 获取CPU、GPU等硬件温度信息
- **电池监控** - 监控笔记本电脑电池状态
- **GPU监控** - 监控显卡使用率和温度（需要GPUtil）

### 📊 性能分析
- **性能报告生成** - 生成详细的系统性能分析报告
- **持续监控** - 长时间监控系统资源变化
- **历史数据** - 保存和查询监控历史数据

### 🔧 系统管理
- **进程终止** - 安全终止或强制杀死进程
- **资源访问** - 通过MCP资源接口访问实时系统数据

## 安装和使用

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 安装方法

```bash
pip install system-monitor-mcp
```

或者使用uvx安装（推荐）:

```bash
uvx system-monitor-mcp
```

### 3. 配置MCP客户端
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

## 可用工具

### 基础监控工具
- `get_system_info` - 获取系统基本信息
- `monitor_cpu` - CPU使用率监控
- `monitor_memory` - 内存使用监控
- `monitor_disk` - 磁盘使用和I/O监控
- `monitor_network` - 网络流量监控
- `get_processes` - 获取进程列表
- `get_temperatures` - 获取硬件温度
- `get_battery_info` - 获取电池信息
- `get_gpu_info` - 获取GPU信息

### 高级功能
- `system_performance_report` - 生成性能报告
- `start_monitoring` - 开始持续监控
- `kill_process` - 终止进程

## 可用资源

通过MCP资源接口可以访问：
- `system://info` - 系统基本信息
- `system://cpu` - CPU实时状态
- `system://memory` - 内存实时状态
- `system://disk` - 磁盘状态
- `system://network` - 网络状态
- `system://processes` - 进程列表
- `system://monitoring-data` - 监控历史数据

## 工具参数说明

### get_system_info
```json
{
  "detailed": false  // 是否返回详细信息
}
```

### monitor_cpu
```json
{
  "duration": 5,     // 监控持续时间（秒）
  "per_cpu": true    // 是否显示每个CPU核心
}
```

### monitor_network
```json
{
  "duration": 5      // 监控持续时间（秒）
}
```

### get_processes
```json
{
  "sort_by": "cpu",     // 排序方式: cpu, memory, name, pid
  "limit": 20,          // 返回进程数量
  "filter_name": ""     // 按名称过滤
}
```

### kill_process
```json
{
  "pid": 1234,       // 进程ID
  "force": false     // 是否强制终止
}
```

### system_performance_report
```json
{
  "duration": 30,    // 监控时长（秒）
  "format": "text"   // 报告格式: text, json
}
```

### start_monitoring
```json
{
  "interval": 1,     // 监控间隔（秒）
  "duration": 60     // 监控时长（秒）
}
```

## 特性说明

### 矩阵风格界面
继承了原始程序的矩阵数字雨风格，所有输出都采用绿色字体和科技感设计。

### 实时监控
支持实时监控系统资源，数据自动更新并保存历史记录。

### 跨平台支持
基于psutil库，支持Windows、Linux、macOS等多个平台。

### 安全性
进程终止等危险操作需要明确的参数确认，防止误操作。

## 依赖说明

- **mcp** - Model Context Protocol核心库
- **psutil** - 系统和进程监控库
- **numpy** - 数值计算库（用于数据处理）
- **GPUtil** - GPU监控库（可选，用于NVIDIA GPU监控）

## 注意事项

1. GPU监控需要安装GPUtil库和NVIDIA驱动
2. 某些系统信息可能需要管理员权限
3. 温度监控在某些系统上可能不可用
4. 进程终止操作请谨慎使用

## 错误处理

服务器包含完善的错误处理机制：
- 权限不足时会给出明确提示
- 不支持的功能会返回相应说明
- 所有异常都会被捕获并返回友好的错误信息

## 扩展性

代码结构清晰，易于扩展新的监控功能：
- 添加新的监控指标
- 支持更多硬件类型
- 集成其他系统管理功能

## 许可证

本项目基于原始系统监控程序开发，继承其开源特性。