import threading
import queue
import pystray
import pathlib
import ctypes
import time
from PIL import Image, ImageDraw, ImageTk
from dotenv import set_key
from loguru import logger
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText

from app.config import settings
from app.client import SZUNetworkClient
from app.log_utils import setup_logger
from app.startup_utils import get_startup_status, toggle_startup

class SZUNetworkGUI(ttk.Window):
    """
    Main GUI Class for SZU Network Guardian.
    """
    def __init__(self):
        # Set AppUserModelID so Windows treats this as a standalone app with its own icon
        try:
            myappid = 'szu.network.guardian.gui.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        # Initialize window with 'cyborg' theme (Dark Mode)
        super().__init__(themename="cyborg")
        self.title("SZU Network Guardian")
        self.geometry("1000x1000") # Slightly taller for better spacing
        self.resizable(True, True)
        
        # Initialize thread-safe log queue
        self.log_queue = queue.Queue()
        self.setup_logging()

        # Load Icon
        self.icon_image = self.load_icon()
        # Keep a reference to the ImageTk object to prevent garbage collection
        self.tk_icon = ImageTk.PhotoImage(self.icon_image)
        # Apply icon to window title bar
        self.wm_iconphoto(True, self.tk_icon)
        
        # System Tray setup
        self.protocol("WM_DELETE_WINDOW", self.on_close_request)
        self.setup_tray_icon()

        # Main Container
        self.main_container = ttk.Frame(self, padding=20)
        self.main_container.pack(fill=BOTH, expand=YES)
        
        # UI Components Setup
        self.setup_header()
        self.setup_config_frame()
        self.setup_control_frame()
        self.setup_log_console()
        
        # Load initial config
        self.load_config()
        
        # Start Log Polling Loop
        self.update_log_console()

        # Enforce Visibility on Startup (User Request)
        # Always show the window so the user knows the app is running.
        self.deiconify()

    def setup_logging(self):
        """Configure Loguru to sink logs into our queue."""
        setup_logger(self.log_queue)

    def load_config(self):
        """Load settings from environment variables and registry."""
        self.username_var.set(settings.SRUN_USERNAME)
        self.password_var.set(settings.SRUN_PASSWORD)
        self.zone_var.set(settings.NETWORK_ZONE)
        self.startup_var.set(get_startup_status())

    def update_log_console(self):
        """
        Poll the log queue and update the UI in the main thread.
        """
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            
            # Stricter check to prevent accidental interception of standard logs
            if msg.strip().endswith("SYS_HEARTBEAT_SIGNAL"):
                # Heartbeat Logic
                current_time = time.strftime("%H:%M:%S")
                self.lbl_heartbeat.configure(text=f"Last Heartbeat: {current_time}", bootstyle="success")
                self.after(500, lambda: self.lbl_heartbeat.configure(bootstyle="secondary"))
            else:
                # Standard Log Logic
                # Ensure message ends with newline for proper stacking
                formatted_msg = msg if msg.endswith('\n') else msg + '\n'
                self.log_text.text.configure(state="normal")
                self.log_text.text.insert(END, formatted_msg)
                self.log_text.text.see(END)
                self.log_text.text.configure(state="disabled")
        
        # Schedule next check in 100ms
        self.after(100, self.update_log_console)

    def setup_header(self):
        """Header with Title and Status Indicator."""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=X, pady=(0, 25))
        
        title_label = ttk.Label(
            header_frame, 
            text="SZU Network Guardian", 
            font=("Segoe UI", 18, "bold"),
            bootstyle="info"
        )
        title_label.pack(side=LEFT)
        
        # Status Indicator
        self.status_var = ttk.StringVar(value="Offline")
        self.status_label = ttk.Label(
            header_frame, 
            textvariable=self.status_var,
            bootstyle="danger.inverse", # Red background tag style
            font=("Helvetica", 9, "bold"),
            padding=(5, 2)
        )
        self.status_label.pack(side=RIGHT)

        # Heartbeat Indicator
        self.lbl_heartbeat = ttk.Label(
            header_frame, 
            text="Last Heartbeat: --:--:--", 
            bootstyle="secondary", 
            font=("Consolas", 9)
        )
        self.lbl_heartbeat.pack(side=RIGHT, padx=(0, 10))

    def update_connection_status(self, connected=False):
        if connected:
            self.status_var.set("Online")
            self.status_label.configure(bootstyle="success.inverse") # Green background
        else:
            self.status_var.set("Offline")
            self.status_label.configure(bootstyle="danger.inverse") # Red background

    def setup_config_frame(self):
        """Configuration Inputs."""
        config_group = ttk.Labelframe(self.main_container, text="Credentials & Zone", padding=15)
        config_group.pack(fill=X, pady=(0, 20))
        
        config_group.columnconfigure(1, weight=1)
        
        # Username
        ttk.Label(config_group, text="Username").grid(row=0, column=0, sticky=W, pady=5)
        self.username_var = ttk.StringVar()
        ttk.Entry(config_group, textvariable=self.username_var).grid(row=0, column=1, sticky=EW, padx=(10, 0), pady=5)
        
        # Password
        ttk.Label(config_group, text="Password").grid(row=1, column=0, sticky=W, pady=5)
        self.password_var = ttk.StringVar()
        ttk.Entry(config_group, textvariable=self.password_var, show="•").grid(row=1, column=1, sticky=EW, padx=(10, 0), pady=5)
        
        # Zone Selection
        ttk.Label(config_group, text="Zone").grid(row=2, column=0, sticky=W, pady=5)
        self.zone_var = ttk.StringVar(value="teaching")
        zone_frame = ttk.Frame(config_group)
        zone_frame.grid(row=2, column=1, sticky=EW, padx=(10, 0), pady=5)
        
        ttk.Radiobutton(zone_frame, text="Teaching", variable=self.zone_var, value="teaching", command=self.on_zone_change).pack(side=LEFT, padx=(0, 15))
        ttk.Radiobutton(zone_frame, text="Dormitory", variable=self.zone_var, value="dorm", command=self.on_zone_change).pack(side=LEFT)
        
        # Run at Startup Toggle
        self.startup_var = ttk.BooleanVar()
        self.startup_chk = ttk.Checkbutton(
            config_group, 
            text="Run at Startup (开机自启)", 
            variable=self.startup_var,
            command=self.on_startup_toggle
        )
        self.startup_chk.grid(row=3, column=0, columnspan=2, sticky=W, pady=(10, 0))

        # Save Button
        self.save_btn = ttk.Button(config_group, text="Save Settings", bootstyle="outline-primary", command=self.save_config)
        self.save_btn.grid(row=4, column=0, columnspan=2, sticky=EW, pady=(15, 0))

    def save_config(self):
        """Save config to .env and reload settings."""
        user = self.username_var.get().strip()
        pwd = self.password_var.get().strip()
        zone = self.zone_var.get()
        
        if not user or not pwd:
            logger.error("Credentials cannot be empty.")
            return

        try:
            env_path = settings.PROJECT_ROOT / ".env"
            set_key(env_path, "SRUN_USERNAME", user)
            set_key(env_path, "SRUN_PASSWORD", pwd)
            set_key(env_path, "NETWORK_ZONE", zone)
            
            # Hot reload logic
            settings.SRUN_USERNAME = user
            settings.SRUN_PASSWORD = pwd
            settings.NETWORK_ZONE = zone
            
            logger.success("Settings saved and reloaded.")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def on_startup_toggle(self):
        """Handle the 'Run at Startup' checkbox toggle."""
        toggle_startup(self.startup_var.get())

    def setup_control_frame(self):
        """Control Buttons."""
        control_frame = ttk.Frame(self.main_container)
        control_frame.pack(fill=X, pady=(0, 20))
        
        self.toggle_btn = ttk.Checkbutton(
            control_frame, 
            text="START DAEMON", 
            bootstyle="success-toolbutton",
            command=self.toggle_daemon
        )
        self.toggle_btn.pack(fill=X, ipady=12) # Slightly taller button

    def toggle_daemon(self):
        if "selected" in self.toggle_btn.state():
            self.toggle_btn.configure(text="STOP DAEMON", bootstyle="danger-toolbutton")
            self.start_daemon()
        else:
            self.toggle_btn.configure(text="START DAEMON", bootstyle="success-toolbutton")
            self.stop_daemon()

    def start_daemon(self):
        self.stop_event = threading.Event()
        self.daemon_thread = threading.Thread(target=self.run_daemon_loop, daemon=True)
        self.daemon_thread.start()
        self.update_connection_status(True)

    def stop_daemon(self):
        if hasattr(self, 'stop_event'):
            self.stop_event.set()
            logger.info("Stopping daemon... (Waiting for current cycle)")
        self.update_connection_status(False)

    def run_daemon_loop(self):
        try:
            client = SZUNetworkClient()
            client.keep_alive(stop_event=self.stop_event)
        except Exception as e:
            logger.exception(f"Daemon error: {e}")
            # Reset UI on crash
            self.after(0, lambda: self.toggle_btn.configure(text="START DAEMON", bootstyle="success-toolbutton"))
            self.after(0, lambda: self.toggle_btn.state(["!selected"]))
            self.after(0, lambda: self.update_connection_status(False))

    def setup_log_console(self):
        """Log Console Area."""
        log_group = ttk.Labelframe(self.main_container, text="Live Logs", padding=10)
        log_group.pack(fill=BOTH, expand=YES)
        
        self.log_text = ScrolledText(log_group, height=10, autohide=True)
        self.log_text.pack(fill=BOTH, expand=YES)
        self.log_text.text.configure(state="disabled", font=("Consolas", 11))

    # --- System Tray Logic ---
    
    def setup_tray_icon(self):
        """Initialize the system tray icon immediately."""
        menu = pystray.Menu(
            pystray.MenuItem("Show Window", self.show_window, default=True),
            pystray.MenuItem("Exit", self.quit_app)
        )
        # Use the already loaded icon image
        self.tray_icon = pystray.Icon("SZU Net", self.icon_image, "SZU Network Guardian", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def load_icon(self):
        """
        Load 'assets/icon.png' if it exists, otherwise generate a default colored square.
        Returns: PIL.Image
        """
        icon_path = pathlib.Path(__file__).parent / "assets" / "icon.png"
        
        if icon_path.exists():
            try:
                return Image.open(icon_path)
            except Exception as e:
                logger.warning(f"Failed to load icon from {icon_path}: {e}")
        else:
            logger.warning(f"Icon not found at {icon_path}. Using default.")
            
        # Fallback: Generate a 64x64 icon programmatically
        width = 64
        height = 64
        color = (0, 255, 255) # Cyan
        image = Image.new('RGB', (width, height), color)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
            fill=(255, 255, 255)
        )
        return image

    def on_close_request(self):
        """Minimize to Tray on Close."""
        self.withdraw()

    def show_window(self, icon=None, item=None):
        """
        Show the window. 
        MUST use after() because this is called from the tray thread.
        """
        self.after(0, self._show_window_safe)

    def _show_window_safe(self):
        self.deiconify()
        self.lift()

    def quit_app(self, icon=None, item=None):
        """
        Quit the application.
        MUST use after() because this is called from the tray thread.
        """
        self.after(0, self._quit_app_safe)

    def _quit_app_safe(self):
        self.stop_daemon()
        if self.tray_icon:
            self.tray_icon.stop()
        self.quit()
        self.destroy()

if __name__ == "__main__":
    app = SZUNetworkGUI()
    app.mainloop()
