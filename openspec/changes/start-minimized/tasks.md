# Tasks

## 1. Refactor Tray Logic
- [x] 1.1 Extract tray icon creation logic into `setup_tray_icon()` method.
- [x] 1.2 Update `__init__` to call `setup_tray_icon()` and start the tray thread.
- [x] 1.3 Implement Conditional Silent Start: Check credentials in `__init__`. If valid, call `self.withdraw()`; otherwise, show window.
- [x] 1.4 Update `on_close_request` to only hide the window (remove lazy loading).
- [x] 1.5 Implement Thread-Safe Callbacks: Wrap `show_window` and `quit_app` logic in `self.after(0, lambda: ...)` to ensure main thread execution.

## 2. Verification
- [x] 2.1 Verify app starts silently if credentials exist.
- [x] 2.2 Verify app starts visible if credentials are missing (delete .env or clear vars to test).
- [x] 2.3 Verify tray icon appears immediately in both cases.
- [x] 2.4 Verify clicking tray icon shows window (thread-safe).
- [x] 2.5 Verify "Exit" from tray terminates app completely (thread-safe).
