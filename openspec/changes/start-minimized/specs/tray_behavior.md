# Spec: Start Minimized to Tray

## Use Case
The user wants the application to run in the background (daemon mode) immediately upon startup without cluttering the desktop, provided that the application is already configured.

## Behavior

### Startup Logic
1.  **Icon**: A cyan 64x64 icon appears in the system tray immediately.
2.  **Condition**:
    *   **IF** Username AND Password are present in config:
        *   Window is **HIDDEN** (`withdraw`).
        *   App runs silently in background.
    *   **ELSE** (First run / Missing config):
        *   Window is **VISIBLE**.
        *   User is prompted to enter credentials.

### Interaction & Thread Safety
1.  **Left Click / Menu "Show"**:
    *   Callback triggers `self.after(0, lambda: self.deiconify(); self.lift())`.
    *   Ensures UI updates happen on Main Thread.
2.  **Window Close (X)**:
    *   The main window hides (`withdraw`).
    *   The application continues running in the background.
3.  **Menu "Exit"**:
    *   Callback triggers `self.after(0, self.perform_shutdown)`.
    *   **Shutdown Sequence**:
        1.  Stop network daemon.
        2.  Stop tray icon (`icon.stop()`).
        3.  Destroy window (`self.destroy()`) and quit loop (`self.quit()`).

## Implementation Details
- **Tray Library**: `pystray`.
- **Icon Generation**: `PIL` (Programmatic generation).
- **Threading**:
    *   Tray icon runs in a separate daemon thread.
    *   **CRITICAL**: All interactions from Tray Thread -> GUI must use `after(0, ...)` to dispatch to Main Thread.
