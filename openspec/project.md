# Project Context

## Purpose
This project provides a robust, automated login solution for the Shenzhen University (SZU) campus network. It is designed to handle the specific authentication mechanisms of two distinct network zones:

1.  **Teaching Area**: Uses the **SRUN** authentication system, which requires complex JavaScript-based encryption (XEncode, MD5, SHA1) and a multi-step challenge-response flow.
2.  **Dormitory Area**: Uses the **Dr.COM Web Portal**, which employs a simpler HTTP GET flow with specific query parameters.

The application features a "keep-alive" daemon mode that continuously monitors network connectivity (via captive portal detection) and automatically attempts to reconnect when the connection is dropped. It provides multiple interfaces to suit different user needs:
-   **Modern GUI**: A dark-themed, system-tray-integrated desktop application for Windows.
-   **Rich CLI**: A terminal-based dashboard with startup animations and live status updates.
-   **Legacy Tray**: A minimal system tray implementation (deprecated).

## Tech Stack

### Core Runtime
-   **Language**: Python 3.x
-   **Runtime Dependencies**: Node.js (Required by `PyExecJS` for executing the SRUN JavaScript encryption logic).

### Key Libraries
-   **Network & Logic**:
    -   [`requests`](https://pypi.org/project/requests/): For handling HTTP sessions, headers, and API interactions.
    -   [`PyExecJS`](https://pypi.org/project/PyExecJS/): To bridge Python and Node.js for running the legacy `srun_base64.js` encryption script.
    -   [`pydantic-settings`](https://pypi.org/project/pydantic-settings/) & [`python-dotenv`](https://pypi.org/project/python-dotenv/): For robust, type-safe configuration management using environment variables (`.env`).
    -   [`loguru`](https://pypi.org/project/loguru/): For modern, thread-safe, and structured logging.

-   **CLI & Terminal UI**:
    -   [`rich`](https://pypi.org/project/rich/): For rendering beautiful terminal dashboards, tables, spinners, and colored output.

-   **GUI & System Integration (Windows)**:
    -   [`ttkbootstrap`](https://pypi.org/project/ttkbootstrap/): For a modern, Bootstrap-styled Tkinter GUI (specifically the "cyborg" dark theme).
    -   [`pystray`](https://pypi.org/project/pystray/): For system tray icon management and context menus.
    -   [`Pillow` (PIL)](https://pypi.org/project/Pillow/): For image processing required by the tray icon.
    -   [`pywin32`](https://pypi.org/project/pywin32/) (`win32gui`, `win32con`): For advanced Windows API interactions (e.g., hiding console windows, setting AppUserModelID).

## Project Conventions

### Code Style
-   **Naming**: Follows PEP 8 `snake_case` for variables and functions, `PascalCase` for classes.
-   **Typing**: Extensive use of Python type hints (e.g., `def login(self) -> bool:`) for better developer experience and static analysis.
-   **Configuration**: The [12-Factor App](https://12factor.net/config) principle is followed. Configuration is strictly separated from code, managed via a `.env` file, and loaded into a global `Settings` singleton.
-   **Logging**: All output is routed through `loguru`. In the GUI, a custom `QueueSink` is used to safely redirect logs from background threads to the UI thread.

### Project Structure
-   **Entry Points**:
    -   `app_gui.py`: **Primary GUI Application**. Launches the `ttkbootstrap` window and system tray icon. Sets the Windows AppUserModelID for proper taskbar grouping.
    -   `cli.py`: **CLI Dashboard**. The terminal entry point featuring a `rich` TUI.
    -   `main.py`: **Core Runner**. Handles command-line arguments (like `--loop`, `--interval`) and exposes the `run_daemon` function.
    -   `start.bat`: **Launcher**. A Windows batch script to run `app_gui.py` with `pythonw` (no console window).
    -   `gui.py`: **Legacy**. A minimal tray-only implementation (superseded by `app_gui.py`).

-   **Core Logic (`app/`)**:
    -   `client.py`: `SZUNetworkClient`. The heart of the application. Implements the authentication logic for both Teaching and Dorm zones.
    -   `config.py`: Defines the `Settings` class using `pydantic`, handling environment variable validation and defaults.
    -   `utils.py`: Network helpers, including `get_local_ip` and `is_internet_connected` (using `connect.rom.miui.com/generate_204`).

-   **Encryption (`encryption/`)**:
    -   Contains the logic for the Teaching Zone's complex SRUN protocol: `srun_md5.py`, `srun_sha1.py`, `srun_xencode.py`, and the JS bridge `srun_base64.js`.

### Architecture Patterns
-   **Strategy Pattern (Implicit)**: The `SZUNetworkClient` dynamically switches authentication strategies (`_login_teaching` vs `_login_dorm`) based on the configured `NETWORK_ZONE`.
-   **Hybrid Encryption**: Combines native Python hashing (MD5, SHA1) with legacy JavaScript logic (executed via `PyExecJS`) to perfectly replicate the browser's encryption behavior.
-   **Daemon/Keep-Alive Loop**: An infinite loop that periodically checks internet connectivity. It uses a "check-then-act" logic: only attempting login if the captive portal check fails.
-   **Thread-Safe GUI**:
    -   **Concurrency**: Networking operations run in a separate daemon thread to keep the UI responsive.
    -   **Communication**: `queue.Queue` is used to pass log messages from the worker thread to the GUI thread for display.
    -   **Synchronization**: `threading.Event` or simple flags are used to handle graceful shutdowns.

## Domain Context

### 1. Teaching Area (SRUN)
-   **Protocol**: SRUN (Deeply integrated with the university's central authentication).
-   **Flow**:
    1.  **Get Challenge**: Request a unique token from `/cgi-bin/get_challenge`.
    2.  **Encryption**:
        -   XEncode the user info JSON.
        -   Calculate MD5 of the password + token.
        -   Calculate SHA1 checksum of the entire payload.
    3.  **Login**: Send the encrypted payload to `/cgi-bin/srun_portal`.
-   **Key Params**: `ac_id='12'`, `enc='srun_bx1'`.

### 2. Dormitory Area (Dr.COM)
-   **Protocol**: Dr.COM Web Portal (HTTP/1.1).
-   **Flow**: A single HTTP GET request to the login endpoint.
-   **Endpoint**: `http://172.30.255.42:801/eportal/portal/login`.
-   **Key Params**:
    -   `login_method='1'`
    -   `jsVersion='4.1.3'`
    -   `user_account=',0,<username>'` (Note the specific prefix format).

### External Dependencies / Endpoints
-   **Teaching Zone**:
    -   `https://net.szu.edu.cn/cgi-bin/get_challenge`
    -   `https://net.szu.edu.cn/cgi-bin/srun_portal`
-   **Dorm Zone**:
    -   `http://172.30.255.42:801/eportal/portal/login`
-   **Connectivity Check**:
    -   `http://connect.rom.miui.com/generate_204` (Returns HTTP 204 if online, otherwise redirects or fails).
