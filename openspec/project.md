# Project Context

## Purpose
This project provides an automated login script for the Shenzhen University (SZU) teaching area network. It interacts with the SRUN authentication system to handle challenge retrieval, credential encryption, and session establishment. It supports both a one-time login and a daemon mode ("keep-alive") that continuously monitors network connectivity and re-authenticates when necessary.

## Tech Stack
- **Language**: Python 3
- **Key Libraries**:
  - `requests`: For handling HTTP requests to the network portal and connectivity checks.
  - `PyExecJS`: For executing JavaScript-based encryption logic.
  - `pydantic-settings`: For robust configuration management via environment variables.
  - `loguru`: For structured and thread-safe logging.
- **Runtime Environment**:
  - **OS**: Cross-platform (Windows, Linux, macOS).
  - **Dependencies**: Node.js (required by `PyExecJS` as the runtime for executing encryption scripts).

## Project Conventions

### Code Style
- **Naming**: Uses `snake_case` for variables and function names.
- **Typing**: Uses Python type hints (e.g., `def login(self) -> bool:`) for clarity.
- **Configuration**: All configuration (credentials, network params) is managed via environment variables (loaded from `.env`).

### Structure
- `main.py`: Entry point. Parses CLI arguments (`--loop`, `--interval`) and initializes the client.
- `app/`:
  - `client.py`: Contains `SZUNetworkClient` class, encapsulating the core business logic (get token, encrypt, login, keep-alive).
  - `config.py`: Defines the `Settings` class using `pydantic`, loading config from `.env`.
  - `utils.py`: Utility functions for cross-platform IP detection (`socket`) and connectivity checks (`requests`).
- `encryption/`: Contains Python helpers and the legacy JavaScript file (`srun_base64.js`) for SRUN encryption algorithms.

### Architecture Patterns
- **Object-Oriented**: Logic is encapsulated in the `SZUNetworkClient` class.
- **Hybrid Encryption**: Combines Python implementation of standard hashes (`md5`, `sha1`) with JavaScript execution for specific SRUN encoding logic (via `PyExecJS`).
- **Daemon/Keep-Alive**: Uses a simple infinite loop with sleep intervals to monitor network status and auto-recover.

## Domain Context
- **SRUN Protocol**: The underlying authentication system is SRUN. It requires a specific sequence of operations:
  1.  **Get Challenge**: Retrieve a dynamic token from the server.
  2.  **Encryption**: Use the token to encrypt the user's password and information using custom XEncode and standard MD5/SHA1 algorithms.
  3.  **Login**: Send the encrypted payload to the portal.
- **Parameters**:
  - `ac_id = '12'`: Identifier for the teaching area network.
  - `enc = 'srun_bx1'`: Encryption version identifier.

## External Dependencies
- **Network Portal**:
  - `https://net.szu.edu.cn/cgi-bin/get_challenge`
  - `https://net.szu.edu.cn/cgi-bin/srun_portal`
- **Connectivity Check**:
  - Uses `http://connect.rom.miui.com/generate_204` (or fallback) to detect captive portals.
