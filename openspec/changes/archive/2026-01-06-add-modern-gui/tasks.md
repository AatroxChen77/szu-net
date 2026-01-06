## 1. Preparation
- [x] 1.1 Add `ttkbootstrap` to `requirements.txt`.
- [x] 1.2 Create `app_gui.py` skeleton with `ttkbootstrap.Window`.

## 2. UI Implementation
- [x] 2.1 Implement Header with Title and Connection Status (Red/Green).
- [x] 2.2 Implement Configuration Frame (Inputs for Username, Password, Zone Select, Save Button).
- [x] 2.3 Implement Control Frame (Start/Stop Toggle Button).
- [x] 2.4 Implement Log Console (ScrolledText widget).

## 3. Logic Integration
- [x] 3.1 Implement `load_config` to populate fields from `.env`.
- [x] 3.2 Implement `save_config` to update `.env` using `dotenv.set_key` AND explicitly reload `app.config.settings` (or re-instantiate it) before the next daemon run.
- [x] 3.3 Implement `QueueSink` class (custom loguru sink) to push log records to a `queue.Queue`. Register it via `logger.add()`.
- [x] 3.4 Implement `update_log_console` using `window.after()` polling loop to consume the queue and update the text widget safely on the main thread.

## 4. Daemon & Concurrency
- [x] 4.1 Implement `toggle_daemon` logic (Start thread / Set stop event).
- [x] 4.2 Ensure thread safety for UI updates (handled via 3.4).

## 5. System Tray & Lifecycle
- [x] 5.1 Implement `pystray` integration using programmatically generated icons (via `PIL`) - do not load external .ico files.
- [x] 5.2 Handle `WM_DELETE_WINDOW` to minimize to tray instead of closing.
- [x] 5.3 Implement "Exit" action to kill daemon and close app.

## 6. Verification
- [x] 6.1 Verify config saving works.
- [x] 6.2 Verify daemon starts/stops correctly.
- [x] 6.3 Verify logs appear in the GUI window.
- [x] 6.4 Verify minimize-to-tray works.
