# Project Context

## Purpose
This project provides a robust, automated login solution for the Shenzhen University (SZU) campus network. It supports **Dual-Zone** authentication:
1.  **Teaching Area**: Interacts with the SRUN authentication system (requires complex JS-based encryption).
2.  **Dormitory Area**: Interacts with the Dr.COM Web Portal (simpler HTTP flow).

It features a "keep-alive" daemon mode that continuously monitors network connectivity and auto-reconnects when dropped. The application can run as:
- A **CLI Daemon** with a rich terminal dashboard.
- A **System Tray Application** (Windows) for background operation.

## Tech Stack
- **Language**: Python 3
- **Key Libraries**:
  - **Core Logic**:
    - `requests`: For HTTP requests and session management.
    - `PyExecJS`: For executing legacy JavaScript encryption logic (SRUN).
    - `pydantic-settings` & `python-dotenv`: For type-safe configuration via environment variables.
    - `loguru`: For structured logging.
  - **CLI & UI**:
    - `rich`: For beautiful terminal output, dashboards, and animations.
  - **GUI (Windows)**:
    - `ttkbootstrap`: For modern, themed Tkinter-based window management.
    - `pystray`: For system tray icon and menu management.
    - `Pillow` (PIL): For generating and handling tray icons.
    - `pywin32` (`win32gui`, `win32con`): For window management (hiding/showing console) and AppID setting.
- **Runtime Environment**:
  - **OS**: Cross-platform (Windows, Linux, macOS) for CLI; Windows-specific features for GUI/Tray.
  - **Dependencies**: Node.js (required by `PyExecJS` for SRUN encryption).

## Project Conventions

### Code Style
- **Naming**: `snake_case` for variables and functions.
- **Typing**: Python type hints (e.g., `def login(self) -> bool:`) are mandatory.
- **Configuration**: Strictly separated from code. Managed via `.env` file and loaded into the `Settings` singleton.

### Structure
- **Entry Points**:
  - `app_gui.py`: **Modern GUI Application**. The primary entry point (launched via `start.bat`). Uses `ttkbootstrap` for a dark-themed control panel and `pystray` for system tray integration.
  - `cli.py`: **Rich CLI**. The terminal entry point, featuring a TUI dashboard and startup animations.
  - `gui.py`: **Legacy Tray App**. A simpler, tray-only implementation (mostly superseded by `app_gui.py`).
  - `main.py`: **Core Runner**. Handles argument parsing (`--loop`, `--interval`) and exports `run_daemon` for use by other entry points.
- **Scripts**:
  - `start.bat`: Windows batch script to launch `app_gui.py` in the background (using `pythonw`).
- **`app/`**:
  - `client.py`: `SZUNetworkClient`. Implements the Strategy pattern to switch between `_login_teaching` (SRUN) and `_login_dorm` (Dr.COM) based on config.
  - `config.py`: `Settings` definition using `pydantic`.
  - `utils.py`: Network helpers (IP detection, connectivity checks).
- **`encryption/`**:
  - SRUN-specific logic (`srun_md5.py`, `srun_sha1.py`, `srun_xencode.py`, `srun_base64.js`).

### Architecture Patterns
- **Strategy Pattern**: The `login()` method dynamically dispatches to the correct backend (`teaching` vs `dorm`) based on `NETWORK_ZONE`.
- **Hybrid Encryption**: Teaching zone login uses a mix of Python (hashing) and JavaScript (custom encoding via `PyExecJS`).
- **Daemon/Keep-Alive**: An infinite loop that checks `is_internet_connected()` (captive portal detection) and triggers login only when needed.
- **Concurrency**:
  - The GUI uses `threading` to run the network client in a daemon thread while the main thread handles the system tray event loop.
  - Graceful shutdown is managed via `threading.Event` to coordinate between UI/Signal handlers and the worker loop.

## Domain Context
### 1. Teaching Area (SRUN)
- **Protocol**: SRUN.
- **Flow**: Get Challenge -> Encrypt Credentials (XEncode + MD5 + SHA1) -> Login.
- **Key Params**: `ac_id='12'`, `enc='srun_bx1'`.

### 2. Dormitory Area (Dr.COM)
- **Protocol**: Dr.COM Web Portal.
- **Flow**: Simple HTTP GET request with query parameters.
- **Key Params**: `login_method='1'`, `jsVersion='4.1.3'`.
- **Endpoint**: `http://172.30.255.42:801/eportal/portal/login`.

## External Dependencies
- **Teaching Zone APIs**:
  - Challenge: `https://net.szu.edu.cn/cgi-bin/get_challenge`
  - Portal: `https://net.szu.edu.cn/cgi-bin/srun_portal`
- **Dorm Zone API**:
  - Portal: `http://172.30.255.42:801/eportal/portal/login`
- **Connectivity Check**:
  - `http://connect.rom.miui.com/generate_204` (Captive Portal Detection)
