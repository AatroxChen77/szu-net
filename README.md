<div align="center">

# SZU Network Guardian

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-Required-339933?style=flat&logo=node.js&logoColor=white)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat)](https://github.com/szu-net/szu-net)

**[中文说明](README_zh.md)** | **[English Version](README.md)**

<p align="center">
  <a href="#features">✨ Key Features</a> •
  <a href="#installation">⚙️ Installation</a> •
  <a href="#configuration">🛠️ Configuration</a> •
  <a href="#usage">🚀 Usage</a> •
  <a href="#architecture">🏗️ Architecture</a>
</p>

</div>

## 📖 Introduction

**SZU Network Guardian** is a robust, automated authentication solution designed specifically for the Shenzhen University (SZU) campus network. It bridges the gap between complex enterprise authentication protocols and user convenience.

**The Problem**: SZU's network is divided into two zones with completely different authentication mechanisms: the Teaching Area (complex SRUN protocol with JS encryption) and the Dormitory Area (Dr.COM Web Portal). Users often face disconnections and need to manually re-login.

**The Solution**: This project provides a unified **"Keep-Alive" Daemon** that continuously monitors connectivity via Captive Portal detection (`connect.rom.miui.com/generate_204`). It automatically handles the cryptographic challenges of SRUN or the HTTP flow of Dr.COM, ensuring your device stays online 24/7.

## <span id="features">✨ Key Features</span>

*   **🏰 Dual-Zone Strategy Engine**
    *   **Teaching Area (SRUN)**: Implements a hybrid encryption engine using `PyExecJS` to execute the original `srun_base64.js` logic alongside native Python MD5/SHA1 hashing.
    *   **Dormitory Area (Dr.COM)**: Native support for Dr.COM Web Portal HTTP flow with automatic encoding handling.

*   **🛡️ Resilient Keep-Alive Daemon**
    *   **Smart Monitoring**: Uses "Check-then-Act" logic. It only attempts login if the connectivity check fails (HTTP 204 probe), minimizing server load.
    *   **Auto-Reconnect**: Instantly restores connection upon drop detection.

*   **🖥️ Versatile Interfaces**
    *   **Modern GUI**: A `ttkbootstrap` (Dark Theme) desktop app with System Tray integration (using `pystray` and `pywin32` for AppUserModelID).
    *   **Rich TUI**: A beautiful terminal dashboard powered by `rich`, featuring startup animations and live status tables.

*   **⚙️ Enterprise-Grade Configuration**
    *   Follows **12-Factor App** principles. All credentials and settings are managed via `.env` files and loaded into a type-safe `Settings` singleton (Pydantic).

## <span id="installation">⚙️ Installation</span>

### Prerequisites
*   **Python 3.10+**
*   **Node.js** (Required for the SRUN encryption JavaScript runtime)

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/szu-net.git
cd szu-net
```

### 2. Install Dependencies
You can use either **Conda** (recommended for isolation) or **pip**.

**Option A: Using Conda (Automated)**
```bash
# Creates env 'szu-net' with Python, Node.js, and all libs
conda env create -f environment.yml
conda activate szu-net
```

**Option B: Using Pip**
*Ensure Node.js is installed in your system PATH first.*
```bash
pip install -r requirements.txt
```

## <span id="configuration">🛠️ Configuration</span>

Create a `.env` file in the project root (copy from `.env.example`).

```ini
# --- Credentials ---
SRUN_USERNAME=2020123456      # Your Student ID
SRUN_PASSWORD=your_password

# --- Network Zone Selector ---
# 'teaching' = SRUN Protocol (Teaching Area/Library)
# 'dorm'     = Dr.COM Protocol (Dormitory)
NETWORK_ZONE=teaching

# --- Advanced ---
RETRY_INTERVAL=300            # Check interval in seconds
```

## <span id="usage">🚀 Usage</span>

### �️ Desktop GUI (Windows Recommended)
Launch the modern desktop application with system tray support.
```bash
python app_gui.py
```
*   **Features**: Minimizes to tray, real-time logs, dark mode.
*   *Note: Use `start.bat` for a console-free experience on Windows.*

### 💻 Terminal Dashboard (TUI)
For a visual experience in the terminal.
```bash
python cli.py
```

### 🤖 Headless Daemon
Ideal for servers or background services.

```bash
# Single login attempt (Exit on success/fail)
python main.py

# Keep-alive daemon mode
python main.py --loop

# Custom check interval (e.g., every 60 seconds)
python main.py --loop --interval 60
```

### CLI Arguments (`main.py`)

| Argument | Short | Description | Default |
| :--- | :--- | :--- | :--- |
| `--loop` | - | Enable daemon mode (infinite keep-alive loop). | `False` |
| `--interval` | - | Override the connectivity check interval (seconds). | `300` (`.env`) |
| `--help` | `-h` | Show help message and exit. | - |

## <span id="architecture">🏗️ Architecture</span>

```plaintext
szu-net/
├── app/
│   ├── client.py       # Core Strategy Engine (Teaching/Dorm)
│   ├── config.py       # Pydantic Settings & .env loader
│   ├── log_utils.py    # Triple-stream logging (Console/File/GUI)
│   └── utils.py        # Network probes (Captive Portal Check)
├── app_gui.py          # Modern GUI Entry (ttkbootstrap + pystray)
├── cli.py              # TUI Entry (Rich)
├── encryption/         # SRUN Protocol Crypto Logic
│   ├── srun_base64.js  # Legacy JS encryption bridge
│   └── srun_*.py       # Python implementations of MD5/SHA1/XEncode
├── main.py             # Headless Runner & Arg Parsing
└── requirements.txt    # Python dependencies
```

## 📜 License

This project is licensed under the [MIT License](LICENSE).
