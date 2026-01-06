import threading
import queue
import pystray
from PIL import Image, ImageDraw
from dotenv import set_key, load_dotenv
from loguru import logger
from app.config import settings
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText

from app.client import SZUNetworkClient

class QueueSink:
    """
    自定义 Loguru Sink，用于将日志推送到线程安全的队列中。
    这样可以避免多线程直接操作 GUI 导致的崩溃问题。
    """
    def __init__(self, log_queue):
        self.log_queue = log_queue

    def write(self, message):
        self.log_queue.put(message)

class SZUNetworkGUI(ttk.Window):
    """
    SZU 网络认证客户端的主 GUI 窗口类。
    继承自 ttkbootstrap.Window 以获得现代化的外观。
    """
    def __init__(self):
        # 初始化窗口，使用 'cyborg' 主题 (深色科技风)
        super().__init__(themename="cyborg")
        self.title("SZU Network Guardian (深大校园网认证)")
        self.geometry("400x600")
        self.resizable(False, False)
        
        # 初始化线程安全的日志队列
        self.log_queue = queue.Queue()
        self.setup_logging()
        
        # 系统托盘图标相关初始化
        self.protocol("WM_DELETE_WINDOW", self.on_close_request) # 拦截关闭窗口事件
        self.tray_icon = None

        # 主布局容器，设置内边距
        self.main_container = ttk.Frame(self, padding=20)
        self.main_container.pack(fill=BOTH, expand=YES)
        
        # 初始化各个 UI 模块
        self.setup_header()        # 顶部标题和状态
        self.setup_config_frame()  # 配置输入区域
        self.setup_control_frame() # 控制按钮区域
        self.setup_log_console()   # 日志输出区域
        
        # 加载初始配置
        self.load_config()
        
        # 启动日志轮询更新 (GUI 线程)
        self.update_log_console()

    def setup_logging(self):
        """配置 Loguru 将日志输出到我们的队列中"""
        # 注意：这里我们保留了默认的控制台输出 (stderr)，方便调试
        # 添加自定义的 Sink，将日志格式化后放入队列
        sink = QueueSink(self.log_queue)
        logger.add(sink, format="{time:HH:mm:ss} | {message}", level="INFO")

    def load_config(self):
        """从 settings 或环境变量加载配置到输入框"""
        self.username_var.set(settings.SRUN_USERNAME)
        self.password_var.set(settings.SRUN_PASSWORD)
        self.zone_var.set(settings.NETWORK_ZONE)

    def update_log_console(self):
        """
        定时轮询日志队列并更新 UI。
        这是为了保证 GUI 操作 (修改 Text 控件) 始终在主线程执行。
        """
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_text.text.configure(state="normal") # 启用编辑以插入文本
            self.log_text.text.insert(END, msg)          # 插入日志
            self.log_text.text.see(END)                  # 滚动到底部
            self.log_text.text.configure(state="disabled") # 恢复只读状态
        
        # 安排下一次检查 (100毫秒后)
        self.after(100, self.update_log_console)

    def setup_header(self):
        """设置顶部标题和连接状态指示器"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame, 
            text="SZU Network Guardian", 
            font=("Helvetica", 16, "bold"),
            bootstyle="info"
        )
        title_label.pack(side=LEFT)
        
        # 连接状态指示器
        self.status_var = ttk.StringVar(value="Disconnected")
        self.status_label = ttk.Label(
            header_frame, 
            textvariable=self.status_var,
            bootstyle="danger", # 默认红色表示未连接
            font=("Helvetica", 10, "bold")
        )
        self.status_label.pack(side=RIGHT, anchor=CENTER)

    def update_connection_status(self, connected=False):
        """更新连接状态标签的文字和颜色"""
        if connected:
            self.status_var.set("Connected")
            self.status_label.configure(bootstyle="success") # 绿色
        else:
            self.status_var.set("Disconnected")
            self.status_label.configure(bootstyle="danger") # 红色

    def setup_config_frame(self):
        """设置配置输入区域 (用户名、密码、网络区域)"""
        config_group = ttk.Labelframe(self.main_container, text="Configuration (配置)", padding=15)
        config_group.pack(fill=X, pady=(0, 20))
        
        # 使用 Grid 布局
        config_group.columnconfigure(1, weight=1)
        
        # 用户名输入
        ttk.Label(config_group, text="Username:").grid(row=0, column=0, sticky=W, pady=5)
        self.username_var = ttk.StringVar()
        ttk.Entry(config_group, textvariable=self.username_var).grid(row=0, column=1, sticky=EW, padx=(10, 0), pady=5)
        
        # 密码输入
        ttk.Label(config_group, text="Password:").grid(row=1, column=0, sticky=W, pady=5)
        self.password_var = ttk.StringVar()
        ttk.Entry(config_group, textvariable=self.password_var, show="*").grid(row=1, column=1, sticky=EW, padx=(10, 0), pady=5)
        
        # 网络区域选择
        ttk.Label(config_group, text="Zone:").grid(row=2, column=0, sticky=W, pady=5)
        self.zone_var = ttk.StringVar(value="teaching")
        zone_frame = ttk.Frame(config_group)
        zone_frame.grid(row=2, column=1, sticky=EW, padx=(10, 0), pady=5)
        
        ttk.Radiobutton(zone_frame, text="Teaching Area (教学区)", variable=self.zone_var, value="teaching").pack(side=LEFT, padx=(0, 10))
        ttk.Radiobutton(zone_frame, text="Dormitory (宿舍)", variable=self.zone_var, value="dorm").pack(side=LEFT)
        
        # 保存按钮
        self.save_btn = ttk.Button(config_group, text="Save Config (保存配置)", bootstyle="outline-primary", command=self.save_config)
        self.save_btn.grid(row=3, column=0, columnspan=2, sticky=EW, pady=(15, 0))

    def save_config(self):
        """保存配置到 .env 文件并动态重新加载设置"""
        user = self.username_var.get().strip()
        pwd = self.password_var.get().strip()
        zone = self.zone_var.get()
        
        if not user or not pwd:
            logger.error("Username and Password cannot be empty! (用户名和密码不能为空)")
            return

        try:
            # 更新 .env 文件
            env_path = settings.PROJECT_ROOT / ".env"
            set_key(env_path, "SRUN_USERNAME", user)
            set_key(env_path, "SRUN_PASSWORD", pwd)
            set_key(env_path, "NETWORK_ZONE", zone)
            
            # 动态重新加载设置 (架构要求 3.2)
            # 因为 settings 对象是单例，我们需要手动更新它的属性以使其立即生效
            settings.SRUN_USERNAME = user
            settings.SRUN_PASSWORD = pwd
            settings.NETWORK_ZONE = zone
            
            logger.success("Configuration saved and reloaded successfully! (配置已保存并重载)")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def setup_control_frame(self):
        """设置启动/停止控制按钮"""
        control_frame = ttk.Frame(self.main_container)
        control_frame.pack(fill=X, pady=(0, 20))
        
        self.toggle_btn = ttk.Checkbutton(
            control_frame, 
            text="START DAEMON (启动守护进程)", 
            bootstyle="success-toolbutton", # 样式：绿色工具按钮
            command=self.toggle_daemon
        )
        self.toggle_btn.pack(fill=X, ipady=10)

    def toggle_daemon(self):
        """切换守护进程的启动/停止状态"""
        if "selected" in self.toggle_btn.state():
            # 按钮被按下 -> 启动
            self.toggle_btn.configure(text="STOP DAEMON (停止守护进程)", bootstyle="danger-toolbutton")
            self.start_daemon()
        else:
            # 按钮弹起 -> 停止
            self.toggle_btn.configure(text="START DAEMON (启动守护进程)", bootstyle="success-toolbutton")
            self.stop_daemon()

    def start_daemon(self):
        """启动后台守护线程"""
        self.stop_event = threading.Event() # 创建停止事件标志
        self.daemon_thread = threading.Thread(target=self.run_daemon_loop, daemon=True)
        self.daemon_thread.start()
        self.update_connection_status(True)

    def stop_daemon(self):
        """停止后台守护线程"""
        if hasattr(self, 'stop_event'):
            self.stop_event.set() # 发送停止信号
            logger.info("Stopping daemon... please wait. (正在停止守护进程，请稍候...)")
            # 注意：这里不使用 join() 等待，以免阻塞 GUI。
            # 守护线程检测到 stop_event 后会自行退出。
        self.update_connection_status(False)

    def run_daemon_loop(self):
        """后台线程运行的主循环：调用 SZUNetworkClient"""
        try:
            client = SZUNetworkClient()
            client.keep_alive(stop_event=self.stop_event)
        except Exception as e:
            logger.exception(f"Daemon crashed: {e}")
            # 如果发生崩溃，重置 UI 状态
            self.after(0, lambda: self.toggle_btn.configure(text="START DAEMON (启动守护进程)", bootstyle="success-toolbutton"))
            self.after(0, lambda: self.toggle_btn.state(["!selected"]))
            self.after(0, lambda: self.update_connection_status(False))

    def setup_log_console(self):
        """设置实时日志输出区域"""
        log_group = ttk.Labelframe(self.main_container, text="System Logs (系统日志)", padding=10)
        log_group.pack(fill=BOTH, expand=YES)
        
        self.log_text = ScrolledText(log_group, height=10, autohide=True)
        self.log_text.pack(fill=BOTH, expand=YES)
        self.log_text.text.configure(state="disabled", font=("Consolas", 9))

    # --- 系统托盘 & 生命周期管理 ---
    
    def create_tray_icon(self):
        """使用 PIL 动态生成一个简单的 64x64 颜色图标 (避免依赖外部 .ico 文件)"""
        width = 64
        height = 64
        color = (0, 255, 255) # 青色
        image = Image.new('RGB', (width, height), color)
        dc = ImageDraw.Draw(image)
        # 绘制一个简单的白色矩形在中间
        dc.rectangle(
            (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
            fill=(255, 255, 255)
        )
        return image

    def on_close_request(self):
        """处理窗口关闭事件 (点击 X 按钮) -> 最小化到托盘"""
        self.withdraw() # 隐藏主窗口
        self.show_tray_notification()
        
        if not self.tray_icon:
            # 创建托盘菜单
            menu = pystray.Menu(
                pystray.MenuItem("Show (显示)", self.show_window, default=True),
                pystray.MenuItem("Exit (退出)", self.quit_app)
            )
            self.tray_icon = pystray.Icon("SZU Net", self.create_tray_icon(), "SZU Network Guardian", menu)
            # 在单独的线程中运行托盘图标，以免阻塞主循环
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_tray_notification(self):
        # 可选：显示气泡通知 (为保持简单暂未实现)
        pass

    def show_window(self, icon=None, item=None):
        """从托盘恢复窗口"""
        self.deiconify() # 显示窗口
        self.lift()      # 提升到最前

    def quit_app(self, icon=None, item=None):
        """完全退出应用程序"""
        self.stop_daemon() # 先停止守护进程
        if self.tray_icon:
            self.tray_icon.stop() # 停止托盘图标
        self.quit()    # 退出 mainloop
        self.destroy() # 销毁窗口

if __name__ == "__main__":
    app = SZUNetworkGUI()
    app.mainloop()
