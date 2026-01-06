# Change: Add Modern GUI

## Why
The current CLI-based interface, while functional, lacks user-friendliness for non-technical users. Users need a modern, graphical interface to easily configure settings (username, password, zone), monitor logs in real-time without opening a terminal, and control the daemon (Start/Stop) intuitively.

## What Changes
- **New Feature**: A Modern GUI application (`app_gui.py`) built with `ttkbootstrap`.
  - **Theme**: Cyberpunk/Dark mode (`cyborg` or `darkly`).
  - **Layout**: Vertical dashboard style.
  - **Controls**: Start/Stop toggle for the daemon.
  - **Config**: Input fields for credentials and network zone with "Save" functionality.
  - **Logs**: Real-time log streaming to a ScrolledText widget.
- **Architecture & Stability**:
  - **Dynamic Config**: Explicitly reload the `app.config.settings` object after saving changes to `.env` to ensure the daemon picks up new values immediately.
  - **Thread Safety**: Use `queue.Queue` for log message passing and `window.after()` for UI updates. No direct UI manipulation from background threads.
  - **Loguru Integration**: Register a custom sink (callable/class) with `loguru.logger.add()` that pushes messages to the thread-safe queue.
  - **Zero-Dependency Assets**: Programmatically generate tray icons using `PIL` (e.g., a colored square) instead of relying on external `.ico` files.
- **Integration**:
  - Replaces `gui.py` logic (or creates a new entry point) to launch the new GUI.
  - Integrates with `pystray` for system tray functionality (minimize to tray).
  - Uses `threading` for non-blocking daemon execution.
- **Dependencies**: Adds `ttkbootstrap` to requirements.

## Impact
- **Affected Specs**:
  - `network-auth`: Unaffected (core logic remains).
  - `gui`: New capability spec.
- **Affected Code**:
  - Create `app_gui.py`.
  - Update `requirements.txt`.
