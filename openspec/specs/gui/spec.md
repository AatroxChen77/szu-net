# gui Specification

## Purpose
TBD - created by archiving change add-modern-gui. Update Purpose after archive.
## Requirements
### Requirement: Modern GUI Dashboard
The system SHALL provide a graphical user interface (GUI) using `ttkbootstrap` with a "Cyberpunk" or "Dark" theme.

#### Scenario: Dashboard Layout
- **WHEN** the application starts
- **THEN** it SHALL display a vertical layout containing:
  - A Header with the title "SZU Network Guardian" and a connection status indicator.
  - A Configuration Frame with inputs for Username, Password (masked), and Network Zone.
  - A Control Frame with a Start/Stop toggle button.
  - A Log Console (ScrolledText) for real-time output.

#### Scenario: Configuration Management
- **WHEN** the user modifies inputs and clicks "Save Config"
- **THEN** the system SHALL update the `.env` file with the new values using `dotenv`.
- **AND** the system SHALL reload the application configuration (settings object) so that the next daemon run uses the new values without restarting the app.

#### Scenario: Daemon Control
- **WHEN** the user clicks "START"
- **THEN** the system SHALL run the network daemon in a separate background thread.
- **AND** the UI SHALL NOT freeze.
- **WHEN** the user clicks "STOP"
- **THEN** the system SHALL signal the daemon to stop (via `threading.Event`) and wait for it to finish.

#### Scenario: Log Streaming
- **WHEN** the daemon generates logs (stdout/stderr or loguru)
- **THEN** the system SHALL capture these logs via a custom `loguru` sink.
- **AND** push them to a thread-safe `queue.Queue`.
- **AND** the GUI SHALL poll this queue (e.g., via `window.after()`) to update the ScrolledText widget on the main thread, ensuring no crashes or freezes.

#### Scenario: System Tray Integration
- **WHEN** the application starts
- **THEN** it SHALL programmatically generate a tray icon (using `PIL`) without relying on external `.ico` files.
- **WHEN** the user clicks the window's "Close" (X) button
- **THEN** the window SHALL hide.
- **AND** the application SHALL continue running in the system tray.
- **WHEN** the user selects "Exit" from the tray menu
- **THEN** the application SHALL stop the daemon and terminate completely.

