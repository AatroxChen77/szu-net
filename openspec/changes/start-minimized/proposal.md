# Proposal: Support "Start Minimized to Tray"

## Goal
Refactor `app_gui.py` to support launching the application in a "silent" mode where it starts minimized to the system tray without showing the main window, unless configuration is missing.

## Current State
- The system tray icon is lazily initialized in `on_close_request`.
- The application always starts with the main window visible.
- Users cannot start the application silently (e.g., on system startup).
- Potential thread-safety issues with calling tkinter methods from `pystray` callbacks.

## Proposed Changes

### 1. Eager Tray Initialization
- Move tray icon creation logic from `on_close_request` to a new `setup_tray_icon()` method.
- Call `setup_tray_icon()` in `__init__` to ensure the tray icon exists immediately upon startup.
- Start the tray icon thread in `__init__`.

### 2. Conditional Silent Start
- Check for valid credentials (username and password) in `__init__`.
- **IF** credentials are valid: Call `self.withdraw()` to hide the main window immediately (Silent Start).
- **ELSE**: Do NOT hide the window, forcing the user to configure settings (First Run / Missing Config).

### 3. Thread-Safe Event Handling
- Ensure all tkinter methods (`deiconify`, `withdraw`, `quit`, `destroy`) called from `pystray` callbacks are wrapped in `self.after(0, ...)` to guarantee execution on the main thread.
- `on_close_request`: Remove icon creation logic (since it's already created). Just call `self.withdraw()`.
- `quit_app`: Ensure clean shutdown of both the daemon and the tray icon, executed safely on the main thread.
