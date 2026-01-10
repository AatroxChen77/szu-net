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

        # Load Icons for dynamic switching
        self.icon_online = self.load_icon(state="online")
        self.icon_offline = self.load_icon(state="offline")
        # Keep a reference to the main app icon for the window title bar
        self.tk_icon = ImageTk.PhotoImage(self.load_icon(name="icon.png"))
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
        
        # Singleton flag for settings window
        self._settings_window = None
        
        # Start Log Polling Loop
        self.update_log_console()

        # Enforce Visibility on Startup (User Request)
        # Only show the window if START_MINIMIZED is False to prevent "flashing"
        if not settings.START_MINIMIZED:
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

        # Settings Button (Gear Unicode)
        self.settings_btn = ttk.Button(
            header_frame, 
            text="⚙", 
            bootstyle="link", 
            command=self.open_settings_window,
            width=3
        )
        self.settings_btn.pack(side=RIGHT, padx=(0, 10))

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
            if self.tray_icon:
                self.tray_icon.icon = self.icon_online
        else:
            self.status_var.set("Offline")
            self.status_label.configure(bootstyle="danger.inverse") # Red background
            if self.tray_icon:
                self.tray_icon.icon = self.icon_offline

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

        # Verify & Save Button
        self.save_btn = ttk.Button(
            config_group, 
            text="Verify & Save Credentials", 
            bootstyle="outline-primary", 
            command=self.verify_and_save_credentials
        )
        self.save_btn.grid(row=4, column=0, columnspan=2, sticky=EW, pady=(15, 0))

    def on_zone_change(self):
        """Handle immediate zone switching."""
        new_zone = self.zone_var.get()
        try:
            env_path = settings.PROJECT_ROOT / ".env"
            set_key(env_path, "NETWORK_ZONE", new_zone)
            settings.NETWORK_ZONE = new_zone
            logger.success(f"Network zone switched to {new_zone} (Immediate effect)")
        except Exception as e:
            logger.error(f"Failed to switch zone: {e}")

    def verify_and_save_credentials(self):
        """Test credentials before saving them to disk."""
        user = self.username_var.get().strip()
        pwd = self.password_var.get().strip()

        if not user or not pwd:
            logger.error("Credentials cannot be empty.")
            return

        # Disable UI during test
        self.save_btn.configure(text="Verifying...", state="disabled")
        
        # Run verification in background thread
        threading.Thread(target=self._test_credentials_thread, args=(user, pwd), daemon=True).start()

    def _test_credentials_thread(self, user, pwd):
        """Background thread for credential testing."""
        try:
            client = SZUNetworkClient(username=user, password=pwd)
            success = client.login() # Test with current zone
            
            # Back to main thread for UI updates
            self.after(0, lambda: self._on_verification_result(success, user, pwd))
        except Exception as e:
            logger.error(f"Verification process error: {e}")
            self.after(0, lambda: self._on_verification_result(False, user, pwd))

    def _on_verification_result(self, success, user, pwd):
        """Handle the result of credential verification on the main thread."""
        if success:
            try:
                env_path = settings.PROJECT_ROOT / ".env"
                set_key(env_path, "SRUN_USERNAME", user)
                set_key(env_path, "SRUN_PASSWORD", pwd)
                
                # Update in-memory settings
                settings.SRUN_USERNAME = user
                settings.SRUN_PASSWORD = pwd
                
                logger.success("Credentials verified and saved successfully.")
                self.save_btn.configure(bootstyle="success")
                self.after(2000, lambda: self.save_btn.configure(bootstyle="outline-primary"))
            except Exception as e:
                logger.error(f"Failed to save verified credentials: {e}")
        else:
            logger.error("Credential verification failed. Settings NOT saved.")
            self.save_btn.configure(bootstyle="danger")
            self.after(2000, lambda: self.save_btn.configure(bootstyle="outline-primary"))

        # Re-enable button
        self.save_btn.configure(text="Verify & Save Credentials", state="normal")

    def on_startup_toggle(self):
        """Handle the 'Run at Startup' checkbox toggle."""
        toggle_startup(self.startup_var.get())

    def open_settings_window(self, icon=None, item=None):
        """Open the Advanced Settings modal window (Singleton)."""
        # Ensure we run this on the main thread if called from tray
        if threading.current_thread() != threading.main_thread():
            self.after(0, self.open_settings_window)
            return

        if self._settings_window is not None and self._settings_window.winfo_exists():
            self._settings_window.lift()
            return

        self._settings_window = ttk.Toplevel(self)
        self._settings_window.title("Advanced Settings")
        self._settings_window.geometry("400x450")
        self._settings_window.resizable(False, False)
        self._settings_window.grab_set() # Modal

        container = ttk.Frame(self._settings_window, padding=20)
        container.pack(fill=BOTH, expand=YES)

        ttk.Label(container, text="Advanced System Parameters", font=("Segoe UI", 12, "bold"), bootstyle="info").pack(pady=(0, 20))

        # 1. Keep-Alive Interval
        ttk.Label(container, text="Check Interval (s) - 心跳检测间隔").pack(anchor=W)
        interval_spin = ttk.Spinbox(container, from_=1, to=3600, bootstyle="info")
        interval_spin.set(settings.CHECK_INTERVAL)
        interval_spin.pack(fill=X, pady=(5, 15))

        # 2. Request Timeout
        ttk.Label(container, text="Request Timeout (s) - 请求超时阈值").pack(anchor=W)
        timeout_spin = ttk.Spinbox(container, from_=1, to=60, bootstyle="info")
        timeout_spin.set(settings.REQUEST_TIMEOUT)
        timeout_spin.pack(fill=X, pady=(5, 15))

        # 3. Max Retries
        ttk.Label(container, text="Max Retries - 最大重试次数").pack(anchor=W)
        retries_spin = ttk.Spinbox(container, from_=1, to=10, bootstyle="info")
        retries_spin.set(settings.MAX_RETRIES)
        retries_spin.pack(fill=X, pady=(5, 15))

        # 4. Start Minimized
        start_min_var = ttk.BooleanVar(value=settings.START_MINIMIZED)
        ttk.Checkbutton(container, text="Start Minimized to Tray (开机后自动隐藏到托盘)", variable=start_min_var).pack(anchor=W, pady=(0, 20))

        def save_advanced_settings():
            try:
                new_interval = int(interval_spin.get())
                new_timeout = int(timeout_spin.get())
                new_retries = int(retries_spin.get())
                new_start_min = start_min_var.get()

                # Update in-memory settings immediately (Requirement)
                settings.CHECK_INTERVAL = new_interval
                settings.REQUEST_TIMEOUT = new_timeout
                settings.MAX_RETRIES = new_retries
                settings.START_MINIMIZED = new_start_min

                # Persist to .env
                env_path = settings.PROJECT_ROOT / ".env"
                set_key(env_path, "CHECK_INTERVAL", str(new_interval))
                set_key(env_path, "REQUEST_TIMEOUT", str(new_timeout))
                set_key(env_path, "MAX_RETRIES", str(new_retries))
                set_key(env_path, "START_MINIMIZED", str(new_start_min))

                logger.success("Advanced settings updated and saved.")
                self._settings_window.destroy()
            except ValueError:
                logger.error("Invalid input: Please enter numeric values.")
            except Exception as e:
                logger.error(f"Failed to save advanced settings: {e}")

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary-outline", command=self._settings_window.destroy).pack(side=RIGHT, padx=(10, 0))
        ttk.Button(btn_frame, text="Apply & Save", bootstyle="primary", command=save_advanced_settings).pack(side=RIGHT)

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
            pystray.MenuItem("Settings", self.open_settings_window),
            pystray.MenuItem("Exit", self.quit_app)
        )
        # Use the offline icon as default state
        self.tray_icon = pystray.Icon("SZU Net", self.icon_offline, "SZU Network Guardian", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def load_icon(self, name=None, state="online"):
        """
        Load an icon from assets or generate a high-quality fallback.
        Args:
            name (str, optional): Specific filename to load.
            state (str): 'online' or 'offline' for state-based loading.
        Returns: PIL.Image
        """
        # Determine target filename if not specified
        if name is None:
            name = "tray_on.png" if state == "online" else "tray_off.png"
            
        icon_path = pathlib.Path(__file__).parent / "assets" / name
        
        if icon_path.exists():
            try:
                return Image.open(icon_path)
            except Exception as e:
                logger.warning(f"Failed to load icon from {icon_path}: {e}")
        
        # Fallback: Generate 64x64 high-quality icons programmatically
        width, height = 64, 64
        
        if state == "online":
            # Solid Cyan Filled Square
            image = Image.new('RGB', (width, height), (0, 255, 255))
            draw = ImageDraw.Draw(image)
            draw.rectangle(
                (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
                fill=(255, 255, 255)
            )
            return image
        else:
            # Hollow Gray Outline with Transparency (RGBA)
            # Create a fully transparent background
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            # Draw gray outline
            outline_color = (128, 128, 128, 255)
            draw.rectangle(
                (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
                outline=outline_color,
                width=4,
                fill=None # Transparent center
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
