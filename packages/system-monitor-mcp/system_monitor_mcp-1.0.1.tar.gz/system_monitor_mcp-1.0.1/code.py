import sys
import time
import psutil
import numpy as np
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QLinearGradient, QBrush, QFontMetrics
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTabWidget, QGridLayout, QMenu, QAction, QToolBar,
                            QDockWidget, QScrollArea, QSizePolicy, QSplitter,
                            QTableWidget, QTableWidgetItem, QHeaderView)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class MatrixRainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.characters = "0123456789qwertyuiopasdfghjklzxcvb"
        self.font_size = 12
        self.rain = []
        
        # 初始列数和行数，会在resizeEvent中更新
        self.columns = 0
        self.rows = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rain)
        self.timer.start(0)
        
    def resizeEvent(self, event):
        # 当窗口大小改变时重新计算列数和行数
        font_metrics = QFontMetrics(QFont("MS Gothic", self.font_size))
        char_width = font_metrics.horizontalAdvance("0")
        char_height = font_metrics.height()
        
        if char_width > 0 and char_height > 0:
            self.columns = max(10, self.width() // char_width)
            self.rows = max(5, self.height() // char_height)
        
        self.init_rain()
        super().resizeEvent(event)
        
    def init_rain(self):
        self.rain = []
        for i in range(self.columns):
            length = np.random.randint(5, self.rows)
            speed = np.random.uniform(0.5, 1.5)
            start_pos = np.random.randint(-self.rows, 0)
            self.rain.append({
                'length': length,
                'speed': speed,
                'position': start_pos,
                'chars': [np.random.choice(list(self.characters)) for _ in range(length)],
                'brightness': [max(0.1, 1 - i/length) for i in range(length)]
            })
    
    def update_rain(self):
        for drop in self.rain:
            drop['position'] += drop['speed']
            if drop['position'] - drop['length'] > self.rows:
                drop['position'] = np.random.randint(-self.rows, 0)
                drop['chars'] = [np.random.choice(list(self.characters)) for _ in range(drop['length'])]
        self.update()
    
    def paintEvent(self, event):
        if not self.rain:
            return
            
        painter = QPainter(self)
        painter.setFont(QFont("MS Gothic", self.font_size))
        
        font_metrics = painter.fontMetrics()
        char_width = font_metrics.horizontalAdvance("0")
        char_height = font_metrics.height()
        
        if char_width == 0 or char_height == 0:
            return
            
        for i, drop in enumerate(self.rain):
            x = i * char_width
            for j in range(drop['length']):
                y_pos = drop['position'] - j
                if 0 <= y_pos < self.rows:
                    y = y_pos * char_height
                    brightness = drop['brightness'][j]
                    color = QColor(0, int(255 * brightness), 0)
                    painter.setPen(color)
                    painter.drawText(QPoint(int(x), int(y)), drop['chars'][j])

class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("资源监控系统-By 创客白泽")
        self.setGeometry(100, 100, 1400, 900)
        
        # 初始化主题
        self.current_theme = "matrix"
        self.init_theme()
        
        # 主部件和布局
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        
        # 添加矩阵数字雨背景（先添加，确保在最底层）
        self.matrix_rain = MatrixRainWidget(self.main_widget)
        self.matrix_rain.setGeometry(0, 0, self.width(), self.height())
        
        # 创建标签页（后添加，确保在上层）
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("background: transparent;")  # 设置标签页透明
        self.main_layout.addWidget(self.tabs)
        
        # 创建各个监控标签页
        self.create_cpu_tab()
        self.create_memory_tab()
        self.create_gpu_tab()
        self.create_network_tab()
        self.create_disk_tab()
        self.create_process_tab()
        self.create_sensors_tab()
        self.create_battery_tab()
        
        # 底部状态栏
        self.status_bar = QLabel()
        self.status_bar.setAlignment(Qt.AlignCenter)
        self.status_bar.setFont(QFont("Consolas", 10))
        self.main_layout.addWidget(self.status_bar)
        
        # 数据初始化
        self.init_data()
        
        # 工具栏
        self.create_toolbar()
        
        # 右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # 定时器更新数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(1000)
        
        # 初始化数据
        self.update_all()
    
    def resizeEvent(self, event):
        # 更新数字雨部件的大小
        if hasattr(self, 'matrix_rain'):
            self.matrix_rain.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
    
    def init_theme(self):
        """初始化主题样式"""
        if self.current_theme == "matrix":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: black;
                }
                QLabel {
                    color: #00FF00;
                    font-family: Consolas, Courier New, monospace;
                }
                QTabWidget::pane {
                    border: 1px solid #00FF00;
                    background: rgba(0, 0, 0, 200);
                }
                QTabBar::tab {
                    background: black;
                    color: #00FF00;
                    border: 1px solid #00FF00;
                    padding: 5px;
                }
                QTabBar::tab:selected {
                    background: #003300;
                }
                QToolBar {
                    background: rgba(0, 20, 0, 150);
                    border: 1px solid #00AA00;
                }
                QToolButton {
                    color: #00FF00;
                    background: transparent;
                    padding: 5px;
                }
                QToolButton:hover {
                    background: rgba(0, 100, 0, 100);
                }
                QScrollArea {
                    background: transparent;
                    border: none;
                }
                QTableView {
                    background: rgba(0, 10, 0, 150);
                    color: #00FF00;
                    gridline-color: #005500;
                    font-family: Consolas;
                }
                QHeaderView::section {
                    background-color: rgba(0, 30, 0, 150);
                    color: #00FF00;
                    padding: 5px;
                    border: 1px solid #005500;
                }
            """)
    
    def create_cpu_tab(self):
        """创建CPU监控标签页"""
        self.cpu_tab = QWidget()
        self.tabs.addTab(self.cpu_tab, "CPU")
        
        layout = QVBoxLayout(self.cpu_tab)
        
        # CPU信息标签
        self.cpu_info_label = QLabel()
        self.cpu_info_label.setFont(QFont("Consolas", 10))
        layout.addWidget(self.cpu_info_label)
        
        # CPU使用率波形图
        self.cpu_fig, self.cpu_ax = plt.subplots(figsize=(10, 6))
        self.setup_chart_style(self.cpu_fig, self.cpu_ax, "CPU Usage (%)")
        
        # 初始化CPU核心线
        self.cpu_lines = []
        for i in range(psutil.cpu_count()):
            line, = self.cpu_ax.plot([], [], label=f'Core {i+1}', color=self.get_green_color(i))
            self.cpu_lines.append(line)
        
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.set_xlim(0, 60)
        self.cpu_ax.legend(facecolor='black', labelcolor='#00FF00')
        
        self.cpu_canvas = FigureCanvas(self.cpu_fig)
        layout.addWidget(self.cpu_canvas)
        
        # 添加工具栏
        cpu_toolbar = NavigationToolbar(self.cpu_canvas, self)
        layout.addWidget(cpu_toolbar)
    
    def create_memory_tab(self):
        """创建内存监控标签页"""
        self.mem_tab = QWidget()
        self.tabs.addTab(self.mem_tab, "Memory")
        
        layout = QVBoxLayout(self.mem_tab)
        
        # 内存信息标签
        self.mem_info_label = QLabel()
        self.mem_info_label.setFont(QFont("Consolas", 10))
        layout.addWidget(self.mem_info_label)
        
        # 内存使用率波形图
        self.mem_fig, self.mem_ax = plt.subplots(figsize=(10, 6))
        self.setup_chart_style(self.mem_fig, self.mem_ax, "Memory Usage (%)")
        
        self.mem_line, = self.mem_ax.plot([], [], label='Memory Usage', color='#00FF00')
        self.mem_ax.set_ylim(0, 100)
        self.mem_ax.set_xlim(0, 60)
        self.mem_ax.legend(facecolor='black', labelcolor='#00FF00')
        
        self.mem_canvas = FigureCanvas(self.mem_fig)
        layout.addWidget(self.mem_canvas)
        
        # 添加工具栏
        mem_toolbar = NavigationToolbar(self.mem_canvas, self)
        layout.addWidget(mem_toolbar)
        
        # 内存详细信息网格
        self.mem_detail_grid = QGridLayout()
        layout.addLayout(self.mem_detail_grid)
        
        self.mem_detail_labels = {
            'total': QLabel(),
            'available': QLabel(),
            'used': QLabel(),
            'free': QLabel(),
            'percent': QLabel(),
            'swap_total': QLabel(),
            'swap_used': QLabel(),
            'swap_free': QLabel(),
            'swap_percent': QLabel()
        }
        
        row = 0
        col = 0
        for key, label in self.mem_detail_labels.items():
            label.setFont(QFont("Consolas", 9))
            self.mem_detail_grid.addWidget(QLabel(key.replace('_', ' ').title() + ":"), row, col)
            self.mem_detail_grid.addWidget(label, row, col+1)
            col += 2
            if col >= 4:
                col = 0
                row += 1
    
    def create_gpu_tab(self):
        """创建显卡监控标签页"""
        self.gpu_tab = QWidget()
        self.tabs.addTab(self.gpu_tab, "GPU")
        
        layout = QVBoxLayout(self.gpu_tab)
        
        # GPU信息标签
        self.gpu_info_label = QLabel("GPU monitoring requires additional libraries like GPUtil")
        self.gpu_info_label.setFont(QFont("Consolas", 10))
        layout.addWidget(self.gpu_info_label)
        
        # GPU使用率波形图
        self.gpu_fig, self.gpu_ax = plt.subplots(figsize=(10, 6))
        self.setup_chart_style(self.gpu_fig, self.gpu_ax, "GPU Usage (%)")
        
        self.gpu_line, = self.gpu_ax.plot([], [], label='GPU Usage', color='#00FF00')
        self.gpu_ax.set_ylim(0, 100)
        self.gpu_ax.set_xlim(0, 60)
        self.gpu_ax.legend(facecolor='black', labelcolor='#00FF00')
        
        self.gpu_canvas = FigureCanvas(self.gpu_fig)
        layout.addWidget(self.gpu_canvas)
        
        # 添加工具栏
        gpu_toolbar = NavigationToolbar(self.gpu_canvas, self)
        layout.addWidget(gpu_toolbar)
        
        # GPU详细信息
        self.gpu_detail_label = QLabel()
        self.gpu_detail_label.setFont(QFont("Consolas", 9))
        layout.addWidget(self.gpu_detail_label)
    
    def create_network_tab(self):
        """创建网络监控标签页"""
        self.net_tab = QWidget()
        self.tabs.addTab(self.net_tab, "Network")
        
        layout = QVBoxLayout(self.net_tab)
        
        # 网络信息标签
        self.net_info_label = QLabel()
        self.net_info_label.setFont(QFont("Consolas", 10))
        layout.addWidget(self.net_info_label)
        
        # 网络使用率波形图
        self.net_fig, self.net_ax = plt.subplots(figsize=(10, 6))
        self.setup_chart_style(self.net_fig, self.net_ax, "Network Traffic (MB/s)")
        
        self.net_sent_line, = self.net_ax.plot([], [], label='Sent', color='#00FF00')
        self.net_recv_line, = self.net_ax.plot([], [], label='Received', color='#00CC00')
        self.net_ax.set_ylim(0, 10)
        self.net_ax.set_xlim(0, 60)
        self.net_ax.legend(facecolor='black', labelcolor='#00FF00')
        
        self.net_canvas = FigureCanvas(self.net_fig)
        layout.addWidget(self.net_canvas)
        
        # 添加工具栏
        net_toolbar = NavigationToolbar(self.net_canvas, self)
        layout.addWidget(net_toolbar)
        
        # 网络详细信息
        self.net_detail_label = QLabel()
        self.net_detail_label.setFont(QFont("Consolas", 9))
        layout.addWidget(self.net_detail_label)
    
    def create_disk_tab(self):
        """创建磁盘监控标签页"""
        self.disk_tab = QWidget()
        self.tabs.addTab(self.disk_tab, "Disk")
        
        layout = QVBoxLayout(self.disk_tab)
        
        # 磁盘信息标签
        self.disk_info_label = QLabel()
        self.disk_info_label.setFont(QFont("Consolas", 10))
        layout.addWidget(self.disk_info_label)
        
        # 磁盘使用率波形图
        self.disk_fig, self.disk_ax = plt.subplots(figsize=(10, 6))
        self.setup_chart_style(self.disk_fig, self.disk_ax, "Disk I/O (MB/s)")
        
        self.disk_read_line, = self.disk_ax.plot([], [], label='Read', color='#00FF00')
        self.disk_write_line, = self.disk_ax.plot([], [], label='Write', color='#00CC00')
        self.disk_ax.set_ylim(0, 10)
        self.disk_ax.set_xlim(0, 60)
        self.disk_ax.legend(facecolor='black', labelcolor='#00FF00')
        
        self.disk_canvas = FigureCanvas(self.disk_fig)
        layout.addWidget(self.disk_canvas)
        
        # 添加工具栏
        disk_toolbar = NavigationToolbar(self.disk_canvas, self)
        layout.addWidget(disk_toolbar)
        
        # 磁盘分区信息
        self.disk_partitions_label = QLabel()
        self.disk_partitions_label.setFont(QFont("Consolas", 9))
        layout.addWidget(self.disk_partitions_label)
    
    def create_process_tab(self):
        """创建进程监控标签页"""
        self.process_tab = QWidget()
        self.tabs.addTab(self.process_tab, "Processes")
        
        layout = QVBoxLayout(self.process_tab)
        
        # 进程信息标签
        self.process_info_label = QLabel("系统进程监控 - 按CPU使用率排序")
        self.process_info_label.setFont(QFont("Consolas", 12))
        layout.addWidget(self.process_info_label)
        
        # 进程表格
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(6)
        self.process_table.setHorizontalHeaderLabels(["PID", "名称", "CPU%", "内存%", "状态", "用户"])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.process_table.setSortingEnabled(True)
        
        # 添加滚动区域
        scroll = QScrollArea()
        scroll.setWidget(self.process_table)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
    
    def create_sensors_tab(self):
        """创建传感器监控标签页"""
        self.sensors_tab = QWidget()
        self.tabs.addTab(self.sensors_tab, "Sensors")
        
        layout = QVBoxLayout(self.sensors_tab)
        
        # 传感器信息标签
        self.sensors_info_label = QLabel("系统传感器数据 - 温度/风扇/电压")
        self.sensors_info_label.setFont(QFont("Consolas", 12))
        layout.addWidget(self.sensors_info_label)
        
        # 温度监控图表
        self.temp_fig, self.temp_ax = plt.subplots(figsize=(10, 4))
        self.setup_chart_style(self.temp_fig, self.temp_ax, "Temperature (°C)")
        
        self.temp_lines = {}
        self.temp_data = {}
        
        # 初始化温度线
        temps = self.get_temperatures()
        for name in temps.keys():
            self.temp_data[name] = []
            line, = self.temp_ax.plot([], [], label=name, color=self.get_green_color(len(self.temp_lines)))
            self.temp_lines[name] = line
        
        self.temp_ax.legend(facecolor='black', labelcolor='#00FF00')
        self.temp_canvas = FigureCanvas(self.temp_fig)
        layout.addWidget(self.temp_canvas)
        
        # 添加工具栏
        temp_toolbar = NavigationToolbar(self.temp_canvas, self)
        layout.addWidget(temp_toolbar)
        
        # 传感器详细信息
        self.sensors_detail_label = QLabel()
        self.sensors_detail_label.setFont(QFont("Consolas", 9))
        layout.addWidget(self.sensors_detail_label)
    
    def create_battery_tab(self):
        """创建电池监控标签页"""
        self.battery_tab = QWidget()
        self.tabs.addTab(self.battery_tab, "Battery")
        
        layout = QVBoxLayout(self.battery_tab)
        
        # 电池信息标签
        self.battery_info_label = QLabel()
        self.battery_info_label.setFont(QFont("Consolas", 12))
        layout.addWidget(self.battery_info_label)
        
        # 电池状态图表
        self.batt_fig, self.batt_ax = plt.subplots(figsize=(10, 4))
        self.setup_chart_style(self.batt_fig, self.batt_ax, "Battery Level (%)")
        
        self.batt_line, = self.batt_ax.plot([], [], label='Battery', color='#00FF00')
        self.batt_ax.set_ylim(0, 100)
        self.batt_ax.set_xlim(0, 60)
        self.batt_ax.legend(facecolor='black', labelcolor='#00FF00')
        
        self.batt_canvas = FigureCanvas(self.batt_fig)
        layout.addWidget(self.batt_canvas)
        
        # 添加工具栏
        batt_toolbar = NavigationToolbar(self.batt_canvas, self)
        layout.addWidget(batt_toolbar)
        
        # 电池详细信息
        self.batt_detail_label = QLabel()
        self.batt_detail_label.setFont(QFont("Consolas", 9))
        layout.addWidget(self.batt_detail_label)
        
        # 初始化电池数据
        self.batt_data = []
    
    def setup_chart_style(self, fig, ax, title):
        """设置图表样式"""
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        ax.tick_params(axis='x', colors='#00FF00')
        ax.tick_params(axis='y', colors='#00FF00')
        for spine in ax.spines.values():
            spine.set_color('#00FF00')
        ax.title.set_color('#00FF00')
        ax.set_title(title)
    
    def get_green_color(self, index):
        """获取不同深浅的绿色"""
        intensity = 0.3 + (index % 8) * 0.1
        return (0, intensity, 0, 1)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # 主题切换
        theme_menu = QMenu("主题", self)
        matrix_action = QAction("矩阵风格", self)
        dark_action = QAction("暗黑风格", self)
        tech_action = QAction("科技风格", self)
        
        matrix_action.triggered.connect(lambda: self.change_theme("matrix"))
        dark_action.triggered.connect(lambda: self.change_theme("dark"))
        tech_action.triggered.connect(lambda: self.change_theme("tech"))
        
        theme_menu.addAction(matrix_action)
        theme_menu.addAction(dark_action)
        theme_menu.addAction(tech_action)
        
        theme_button = toolbar.addAction("主题")
        theme_button.setMenu(theme_menu)
        
        # 刷新控制
        refresh_menu = QMenu("刷新率", self)
        fast_action = QAction("快速 (500ms)", self)
        normal_action = QAction("正常 (1s)", self)
        slow_action = QAction("慢速 (2s)", self)
        
        fast_action.triggered.connect(lambda: self.change_refresh_rate(500))
        normal_action.triggered.connect(lambda: self.change_refresh_rate(1000))
        slow_action.triggered.connect(lambda: self.change_refresh_rate(2000))
        
        refresh_menu.addAction(fast_action)
        refresh_menu.addAction(normal_action)
        refresh_menu.addAction(slow_action)
        
        refresh_button = toolbar.addAction("刷新率")
        refresh_button.setMenu(refresh_menu)
        
        # 窗口控制
        toolbar.addAction("分离窗口", self.detach_window)
        toolbar.addAction("重置布局", self.reset_layout)
    
    def show_context_menu(self, pos):
        """显示右键菜单"""
        context_menu = QMenu(self)
        
        screenshot_action = QAction("截图保存", self)
        screenshot_action.triggered.connect(self.save_screenshot)
        
        export_action = QAction("导出数据", self)
        export_action.triggered.connect(self.export_data)
        
        context_menu.addAction(screenshot_action)
        context_menu.addAction(export_action)
        context_menu.exec_(self.mapToGlobal(pos))
    
    def init_data(self):
        """初始化所有数据容器"""
        # CPU数据
        self.cpu_data = [[] for _ in range(psutil.cpu_count())]
        
        # 内存数据
        self.mem_data = []
        
        # GPU数据
        self.gpu_data = []
        
        # 网络数据
        self.net_sent_data = []
        self.net_recv_data = []
        self.last_net_io = None
        self.last_net_time = time.time()
        
        # 磁盘数据
        self.disk_read_data = []
        self.disk_write_data = []
        self.last_disk_io = None
        self.last_disk_time = time.time()
        
        # 温度数据
        self.temp_data = {name: [] for name in self.get_temperatures().keys()}
        
        # 电池数据
        self.batt_data = []
    
    def update_all(self):
        """更新所有监控数据"""
        self.update_cpu()
        self.update_memory()
        self.update_gpu()
        self.update_network()
        self.update_disk()
        self.update_processes()
        self.update_sensors()
        self.update_battery()
        
        # 更新状态栏
        self.status_bar.setText(time.strftime("%Y-%m-%d %H:%M:%S") + 
                              " | System Monitoring Active | Press Ctrl+Q to exit")
    
    def update_cpu(self):
        """更新CPU数据"""
        # 获取CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        
        # 更新数据
        for i, percent in enumerate(cpu_percent):
            self.cpu_data[i].append(percent)
            if len(self.cpu_data[i]) > 60:  # 保留60秒数据
                self.cpu_data[i] = self.cpu_data[i][-60:]
        
        # 更新图表
        for i, line in enumerate(self.cpu_lines):
            line.set_data(range(len(self.cpu_data[i])), self.cpu_data[i])
        
        # 自动调整Y轴范围
        max_val = max([max(core) for core in self.cpu_data if core] + [10])
        self.cpu_ax.set_ylim(0, max(100, max_val * 1.1))
        
        # 更新CPU信息标签
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        info_text = (f"CPU: {psutil.cpu_percent()}% Total | "
                    f"Cores: {cpu_count} | "
                    f"Frequency: {cpu_freq.current:.2f} MHz (Max: {cpu_freq.max:.2f} MHz)")
        self.cpu_info_label.setText(info_text)
        
        # 重绘图表
        self.cpu_canvas.draw()
    
    def update_memory(self):
        """更新内存数据"""
        # 获取内存使用情况
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # 更新数据
        self.mem_data.append(mem.percent)
        if len(self.mem_data) > 60:
            self.mem_data = self.mem_data[-60:]
        
        # 更新图表
        self.mem_line.set_data(range(len(self.mem_data)), self.mem_data)
        
        # 自动调整Y轴范围
        max_val = max(self.mem_data + [10])
        self.mem_ax.set_ylim(0, max(100, max_val * 1.1))
        
        # 更新内存信息标签
        info_text = (f"Memory: {mem.percent}% Used | "
                    f"Total: {self.format_bytes(mem.total)} | "
                    f"Available: {self.format_bytes(mem.available)} | "
                    f"Swap: {swap.percent}% Used ({self.format_bytes(swap.used)}/{self.format_bytes(swap.total)})")
        self.mem_info_label.setText(info_text)
        
        # 更新详细内存信息
        self.mem_detail_labels['total'].setText(self.format_bytes(mem.total))
        self.mem_detail_labels['available'].setText(self.format_bytes(mem.available))
        self.mem_detail_labels['used'].setText(self.format_bytes(mem.used))
        self.mem_detail_labels['free'].setText(self.format_bytes(mem.free))
        self.mem_detail_labels['percent'].setText(f"{mem.percent}%")
        self.mem_detail_labels['swap_total'].setText(self.format_bytes(swap.total))
        self.mem_detail_labels['swap_used'].setText(self.format_bytes(swap.used))
        self.mem_detail_labels['swap_free'].setText(self.format_bytes(swap.free))
        self.mem_detail_labels['swap_percent'].setText(f"{swap.percent}%")
        
        # 重绘图表
        self.mem_canvas.draw()
    
    def update_gpu(self):
        """更新GPU数据"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            if gpus:
                gpu = gpus[0]  # 只显示第一个GPU
                gpu_percent = gpu.load * 100
                
                # 更新数据
                self.gpu_data.append(gpu_percent)
                if len(self.gpu_data) > 60:
                    self.gpu_data = self.gpu_data[-60:]
                
                # 更新图表
                self.gpu_line.set_data(range(len(self.gpu_data)), self.gpu_data)
                
                # 自动调整Y轴范围
                max_val = max(self.gpu_data + [10])
                self.gpu_ax.set_ylim(0, max(100, max_val * 1.1))
                
                # 更新GPU信息
                info_text = (f"GPU: {gpu.name} | "
                            f"Usage: {gpu_percent:.1f}% | "
                            f"Memory: {gpu.memoryUsed:.1f}/{gpu.memoryTotal:.1f} MB ({gpu.memoryUtil*100:.1f}%) | "
                            f"Temperature: {gpu.temperature}°C")
                self.gpu_info_label.setText(info_text)
                
                # 更新GPU详细信息
                detail_text = (f"Driver: {gpu.driver}\n"
                              f"UUID: {gpu.uuid}\n"
                              f"Serial: {gpu.serial}\n"
                              f"Display Mode: {gpu.display_mode}\n"
                              f"Display Active: {gpu.display_active}")
                self.gpu_detail_label.setText(detail_text)
                
                # 重绘图表
                self.gpu_canvas.draw()
            else:
                self.gpu_info_label.setText("No GPU detected")
        except ImportError:
            self.gpu_info_label.setText("GPUtil library not installed. Install with: pip install gputil")
        except Exception as e:
            self.gpu_info_label.setText(f"GPU monitoring error: {str(e)}")
    
    def update_network(self):
        """更新网络数据"""
        # 获取网络IO
        net_io = psutil.net_io_counters()
        
        # 如果是第一次调用，只保存当前值不计算
        if self.last_net_io is None:
            self.last_net_io = net_io
            self.last_net_time = time.time()
            return  # 第一次不进行计算
        
        # 计算每秒的发送/接收量 (MB)
        time_passed = time.time() - self.last_net_time
        if time_passed > 0:  # 避免除以0
            sent_mb = (net_io.bytes_sent - self.last_net_io.bytes_sent) / (1024 * 1024 * time_passed)
            recv_mb = (net_io.bytes_recv - self.last_net_io.bytes_recv) / (1024 * 1024 * time_passed)
            
            # 更新数据
            self.net_sent_data.append(sent_mb)
            self.net_recv_data.append(recv_mb)
            if len(self.net_sent_data) > 60:
                self.net_sent_data = self.net_sent_data[-60:]
                self.net_recv_data = self.net_recv_data[-60:]
            
            # 更新图表
            self.net_sent_line.set_data(range(len(self.net_sent_data)), self.net_sent_data)
            self.net_recv_line.set_data(range(len(self.net_recv_data)), self.net_recv_data)
            
            # 自动调整Y轴范围
            max_val = max(max(self.net_sent_data + [0.1]), max(self.net_recv_data + [0.1]))
            self.net_ax.set_ylim(0, max(10, max_val * 1.1))
            
            # 更新网络信息
            info_text = (f"Network: Sent {sent_mb:.2f} MB/s | Received {recv_mb:.2f} MB/s | "
                        f"Total Sent: {self.format_bytes(net_io.bytes_sent)} | "
                        f"Total Received: {self.format_bytes(net_io.bytes_recv)}")
            self.net_info_label.setText(info_text)
            
            # 更新网络详细信息
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            detail_text = "Network Interfaces:\n"
            for interface, addrs in net_if_addrs.items():
                stats = net_if_stats.get(interface, None)
                detail_text += (f"\n{interface}: {stats.speed}Mbps " if stats else f"\n{interface}: ")
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:
                        detail_text += f"MAC: {addr.address} "
                    elif addr.family == 2:  # AF_INET
                        detail_text += f"IPv4: {addr.address} "
                    elif addr.family == 23:  # AF_INET6
                        detail_text += f"IPv6: {addr.address} "
            
            self.net_detail_label.setText(detail_text)
            
            # 重绘图表
            self.net_canvas.draw()
        
        # 保存当前值供下次比较
        self.last_net_io = net_io
        self.last_net_time = time.time()
    
    def update_disk(self):
        """更新磁盘数据"""
        # 获取磁盘IO
        disk_io = psutil.disk_io_counters()
        
        # 如果是第一次调用，只保存当前值不计算
        if self.last_disk_io is None:
            self.last_disk_io = disk_io
            self.last_disk_time = time.time()
            return  # 第一次不进行计算
        
        # 计算每秒的读/写量 (MB)
        time_passed = time.time() - self.last_disk_time
        if time_passed > 0:  # 避免除以0
            read_mb = (disk_io.read_bytes - self.last_disk_io.read_bytes) / (1024 * 1024 * time_passed)
            write_mb = (disk_io.write_bytes - self.last_disk_io.write_bytes) / (1024 * 1024 * time_passed)
            
            # 更新数据
            self.disk_read_data.append(read_mb)
            self.disk_write_data.append(write_mb)
            if len(self.disk_read_data) > 60:
                self.disk_read_data = self.disk_read_data[-60:]
                self.disk_write_data = self.disk_write_data[-60:]
            
            # 更新图表
            self.disk_read_line.set_data(range(len(self.disk_read_data)), self.disk_read_data)
            self.disk_write_line.set_data(range(len(self.disk_write_data)), self.disk_write_data)
            
            # 自动调整Y轴范围
            max_val = max(max(self.disk_read_data + [0.1]), max(self.disk_write_data + [0.1]))
            self.disk_ax.set_ylim(0, max(10, max_val * 1.1))
            
            # 更新磁盘信息
            info_text = (f"Disk: Read {read_mb:.2f} MB/s | Write {write_mb:.2f} MB/s | "
                        f"Total Read: {self.format_bytes(disk_io.read_bytes)} | "
                        f"Total Write: {self.format_bytes(disk_io.write_bytes)}")
            self.disk_info_label.setText(info_text)
            
            # 重绘图表
            self.disk_canvas.draw()
        
        # 保存当前值供下次比较
        self.last_disk_io = disk_io
        self.last_disk_time = time.time()
        
        # 更新磁盘分区信息
        partitions = psutil.disk_partitions()
        usage = [psutil.disk_usage(p.mountpoint) for p in partitions]
        
        detail_text = "Disk Partitions:\n"
        for p, u in zip(partitions, usage):
            detail_text += (f"\n{p.device} -> {p.mountpoint} ({p.fstype}) "
                          f"Total: {self.format_bytes(u.total)} "
                          f"Used: {self.format_bytes(u.used)} ({u.percent}%) "
                          f"Free: {self.format_bytes(u.free)}")
        
        self.disk_partitions_label.setText(detail_text)
    
    def update_processes(self):
        """更新进程信息"""
        try:
            # 获取进程列表并按CPU排序
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username']):
                try:
                    processes.append((
                        proc.info['pid'],
                        proc.info['name'],
                        proc.info['cpu_percent'],
                        proc.info['memory_percent'],
                        proc.info['status'],
                        proc.info['username'] or 'N/A'
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # 按CPU使用率排序
            processes.sort(key=lambda p: p[2], reverse=True)
            
            # 更新表格
            self.process_table.setRowCount(len(processes[:50]))  # 只显示前50个
            for row, proc in enumerate(processes[:50]):
                for col, val in enumerate(proc):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    # 高亮显示高资源占用的进程
                    if col == 2 and val > 50:  # CPU > 50%
                        item.setForeground(QColor(255, 0, 0))
                    elif col == 3 and val > 10:  # 内存 > 10%
                        item.setForeground(QColor(255, 165, 0))
                    
                    self.process_table.setItem(row, col, item)
            
            # 更新进程信息标签
            total_procs = len(processes)
            running_procs = sum(1 for p in processes if p[4] == 'running')
            self.process_info_label.setText(
                f"系统进程监控 | 总数: {total_procs} | 运行中: {running_procs} | 显示CPU最高的50个进程")
                
        except Exception as e:
            self.process_info_label.setText(f"进程监控错误: {str(e)}")
    
    def update_sensors(self):
        """更新传感器数据"""
        try:
            temps = self.get_temperatures()
            
            # 更新温度数据
            for name, temp in temps.items():
                if name in self.temp_data:
                    self.temp_data[name].append(temp)
                    if len(self.temp_data[name]) > 60:
                        self.temp_data[name] = self.temp_data[name][-60:]
                    
                    # 更新图表
                    if name in self.temp_lines:
                        self.temp_lines[name].set_data(range(len(self.temp_data[name])), self.temp_data[name])
            
            # 自动调整Y轴范围
            max_temp = max([max(data) for data in self.temp_data.values() if data] + [50])
            self.temp_ax.set_ylim(0, max(90, max_temp * 1.1))
            
            # 更新传感器信息
            fan_info = self.get_fan_speeds()
            voltage_info = self.get_voltages()
            
            info_text = "传感器数据:\n"
            info_text += "\n温度:\n"
            for name, temp in temps.items():
                info_text += f"{name}: {temp}°C  "
            
            if fan_info:
                info_text += "\n\n风扇转速:\n"
                for name, speed in fan_info.items():
                    info_text += f"{name}: {speed}RPM  "
            
            if voltage_info:
                info_text += "\n\n电压:\n"
                for name, volt in voltage_info.items():
                    info_text += f"{name}: {volt}V  "
            
            self.sensors_detail_label.setText(info_text)
            self.temp_canvas.draw()
            
        except Exception as e:
            self.sensors_detail_label.setText(f"传感器监控错误: {str(e)}")
    
    def update_battery(self):
        """更新电池信息"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                self.battery_info_label.setText("未检测到电池")
                return
            
            # 更新电池数据
            self.batt_data.append(battery.percent)
            if len(self.batt_data) > 60:
                self.batt_data = self.batt_data[-60:]
            
            # 更新图表
            self.batt_line.set_data(range(len(self.batt_data)), self.batt_data)
            self.batt_ax.set_ylim(0, 100)
            self.batt_canvas.draw()
            
            # 更新电池信息
            status = "充电中" if battery.power_plugged else "放电中"
            time_left = "N/A"
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                hours, remainder = divmod(battery.secsleft, 3600)
                minutes, _ = divmod(remainder, 60)
                time_left = f"{hours}h {minutes}m"
            
            info_text = (f"电池状态: {battery.percent}% | {status} | "
                        f"剩余时间: {time_left}")
            self.battery_info_label.setText(info_text)
            
            # 更新详细信息
            detail_text = (f"是否充电: {'是' if battery.power_plugged else '否'}\n"
                         f"剩余电量: {battery.percent}%\n"
                         f"剩余时间: {time_left}\n"
                         f"电池状态: {status}")
            self.batt_detail_label.setText(detail_text)
            
        except Exception as e:
            self.battery_info_label.setText(f"电池监控错误: {str(e)}")
    
    def get_temperatures(self):
        """获取温度数据"""
        temps = {}
        try:
            # CPU温度
            if hasattr(psutil, "sensors_temperatures"):
                sensors = psutil.sensors_temperatures()
                for name, entries in sensors.items():
                    for entry in entries:
                        temps[f"{name}_{entry.label or 'temp'}"] = entry.current
            
            # GPU温度 (需要额外库)
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    temps[f"GPU_{i}"] = gpu.temperature
            except ImportError:
                pass
            
            # 如果没有获取到温度数据，使用模拟数据
            if not temps:
                temps = {
                    "CPU": np.random.normal(50, 5),
                    "GPU": np.random.normal(60, 8)
                }
            
        except Exception:
            temps = {
                "CPU": np.random.normal(50, 5),
                "GPU": np.random.normal(60, 8)
            }
        
        return temps
    
    def get_fan_speeds(self):
        """获取风扇转速"""
        fans = {}
        try:
            if hasattr(psutil, "sensors_fans"):
                sensors = psutil.sensors_fans()
                for name, entries in sensors.items():
                    for i, entry in enumerate(entries):
                        fans[f"{name}_fan{i+1}"] = entry.current
        except Exception:
            pass
        
        return fans
    
    def get_voltages(self):
        """获取电压数据"""
        volts = {}
        try:
            # 需要特定平台的实现
            pass
        except Exception:
            pass
        
        return volts
    
    def format_bytes(self, size):
        """格式化字节大小为易读的字符串"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def change_theme(self, theme_name):
        """切换主题"""
        self.current_theme = theme_name
        self.init_theme()
    
    def change_refresh_rate(self, interval):
        """更改刷新频率"""
        self.timer.setInterval(interval)
    
    def detach_window(self):
        """分离当前标签页为独立窗口"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            dock = QDockWidget(self.tabs.tabText(self.tabs.currentIndex()), self)
            dock.setWidget(current_tab)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
    
    def reset_layout(self):
        """重置窗口布局"""
        for dock in self.findChildren(QDockWidget):
            dock.close()
    
    def save_screenshot(self):
        """保存截图"""
        # 实现截图保存逻辑
        pass
    
    def export_data(self):
        """导出数据"""
        # 实现数据导出逻辑
        pass
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key_Q and event.modifiers() == Qt.ControlModifier:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置全局字体
    font = QFont("Consolas", 10)
    app.setFont(font)
    
    monitor = SystemMonitor()
    monitor.show()
    
    sys.exit(app.exec_())
