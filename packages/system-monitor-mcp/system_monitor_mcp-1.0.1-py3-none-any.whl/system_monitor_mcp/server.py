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
