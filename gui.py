import sys
import threading
import time
import win32gui
import win32con
from PIL import Image, ImageDraw
import pystray
from loguru import logger

from app.client import SZUNetworkClient
from main import configure_logging

# Global control event
stop_event = threading.Event()

def create_image():
    """Generate a simple 64x64 color icon."""
    # Create a new image with RGBA mode (Cyan color)
    width = 64
    height = 64
    color = (0, 255, 255) # Cyan
    image = Image.new('RGB', (width, height), color)
    
    # Optional: Draw a simple rectangle or circle to make it look a bit better
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
        fill=(255, 255, 255)
    )
    
    return image

def hide_window(hwnd):
    """Hide the specified window."""
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

def show_window(hwnd):
    """Show the specified window."""
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(hwnd)

def run_daemon(stop_evt):
    """Run the network client in a background thread."""
    try:
        client = SZUNetworkClient()
        # Use the keep_alive method which respects the stop_event
        client.keep_alive(stop_event=stop_evt)
    except Exception as e:
        logger.exception(f"Daemon thread crashed: {e}")

def on_exit(icon, hwnd):
    """Handle application exit."""
    logger.info("Exiting application...")
    stop_event.set()
    show_window(hwnd)  # Show window so user can see exit logs
    icon.stop()

def main():
    # 1. Setup Logging
    configure_logging()
    
    # 2. Grab the Console Window Handle
    hwnd = win32gui.GetForegroundWindow()
    logger.info(f"Captured Window Handle: {hwnd}")
    
    # 3. Define Tray Menu Actions
    def on_show_action(icon, item):
        show_window(hwnd)

    def on_hide_action(icon, item):
        hide_window(hwnd)
    
    def on_exit_action(icon, item):
        on_exit(icon, hwnd)

    # 4. Create System Tray Icon
    image = create_image()
    menu = pystray.Menu(
        pystray.MenuItem("Show Console", on_show_action, default=True),
        pystray.MenuItem("Hide Console", on_hide_action),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_exit_action)
    )
    
    icon = pystray.Icon("SZU Net", image, "SZU Network Client", menu)
    
    # 5. Start Background Daemon
    daemon_thread = threading.Thread(target=run_daemon, args=(stop_event,), daemon=True)
    daemon_thread.start()
    
    logger.info("🚀 App is running! Minimize or Close this window to hide it to the System Tray.")
    logger.info("Use the Tray Icon to toggle visibility or exit.")

    # 6. Run Tray Loop (Blocking)
    try:
        icon.run()
    except KeyboardInterrupt:
        # Handle Ctrl+C if the window is visible and focused
        on_exit(icon, hwnd)
    
    # Wait for daemon to clean up if needed (optional, since it's a daemon thread)
    # But better to join if we want clean shutdown logging
    if daemon_thread.is_alive():
        daemon_thread.join(timeout=2)

if __name__ == "__main__":
    main()
