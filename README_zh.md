<div align="center">

# SZU Network Guardian

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-Required-339933?style=flat&logo=node.js&logoColor=white)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat)](https://github.com/szu-net/szu-net)

**[中文说明](README_zh.md)** | **[English Version](README.md)**

<p align="center">
  <a href="#features">✨ 核心特性</a> •
  <a href="#installation">⚙️ 安装指南</a> •
  <a href="#configuration">🛠️ 配置说明</a> •
  <a href="#usage">🚀 使用方法</a> •
  <a href="#architecture">🏗️ 项目架构</a>
</p>

</div>

## 📖 简介 (Introduction)

**SZU Network Guardian** 是一款专为深圳大学（SZU）校园网设计的工业级自动认证与守护工具。它致力于解决复杂的跨区域认证问题，提供极其稳定的网络连接体验。

**痛点 (The Problem)**：深大校园网分为两个认证机制截然不同的区域：**教学区**（使用复杂的 SRUN 协议和 JS 加密）与 **宿舍区**（使用 Dr.COM Web Portal）。用户经常面临掉线、需手动重连以及跨区配置繁琐的问题。

**解决方案 (The Solution)**：本项目提供了一个统一的 **"Keep-Alive" 守护进程**。它通过 Captive Portal 检测（`connect.rom.miui.com/generate_204`）持续监控网络连通性，并自动处理 SRUN 的加密挑战或 Dr.COM 的 HTTP 流程，确保设备 24 小时在线。

## <span id="features">✨ 核心特性 (Key Features)</span>

*   **🏰 双区策略引擎 (Dual-Zone Engine)**
    *   **教学区 (Teaching)**: 原生实现 SRUN 协议，内置混合加密引擎。使用 `PyExecJS` 调用原生 `srun_base64.js` 逻辑，结合 Python 实现 MD5/SHA1，无需笨重的浏览器驱动。
    *   **宿舍区 (Dorm)**: 完美适配 Dr.COM Web Portal 的 HTTP 流程，自动处理编码问题。

*   **🛡️ 智能守护 (Resilient Daemon)**
    *   **Check-then-Act**: 采用“先检查，后行动”的逻辑。仅在 HTTP 204 连通性检测失败时才发起登录请求，最小化服务器负载。
    *   **秒级重连**: 一旦检测到断网，立即触发重连机制。

*   **🖥️ 多维交互界面 (Versatile Interfaces)**
    *   **Modern GUI**: 基于 `ttkbootstrap` (Dark Theme) 构建的现代化桌面应用，深度集成系统托盘 (`pystray`) 和 Windows 任务栏特性 (`AppUserModelID`)。
    *   **Rich TUI**: 基于 `rich` 库打造的终端仪表盘，提供启动动画、实时状态表格和彩色日志。

*   **⚙️ 工业级配置管理**
    *   遵循 **12-Factor App** 原则。所有敏感凭据和配置均通过 `.env` 环境变量管理，并由 `Pydantic` 进行强类型加载与校验。

## <span id="installation">⚙️ 安装指南 (Installation)</span>

### 前置要求 (Prerequisites)
*   **Python 3.10+**
*   **Node.js** (必须安装，用于运行 SRUN 协议的 JS 加密脚本)

### 1. 获取代码
```bash
git clone https://github.com/your-repo/szu-net.git
cd szu-net
```

### 2. 安装依赖
您可以选择使用 **Conda** (推荐) 或 **pip**。

**方案 A: 使用 Conda (全自动)**
```bash
# 创建环境 'szu-net'，自动包含 Python, Node.js 及所有依赖库
conda env create -f environment.yml
conda activate szu-net
```

**方案 B: 使用 Pip**
*请先确保您的系统已安装 Node.js。*
```bash
pip install -r requirements.txt
```

## <span id="configuration">🛠️ 配置说明 (Configuration)</span>

在项目根目录下创建一个 `.env` 文件（可复制 `.env.example`）。

```ini
# --- 认证信息 ---
SRUN_USERNAME=2020123456      # 你的学号
SRUN_PASSWORD=your_password   # 你的密码

# --- 网络区域选择 ---
# 'teaching' = 教学区/图书馆 (SRUN 协议)
# 'dorm'     = 宿舍区 (Dr.COM 协议)
NETWORK_ZONE=teaching

# --- 进阶配置 ---
RETRY_INTERVAL=300            # 守护模式下的检查间隔 (秒)
```

## <span id="usage">🚀 使用方法 (Usage)</span>

### 🖥️ 桌面 GUI 模式 (Windows 推荐)
启动带有系统托盘支持的现代化界面。
```bash
python app_gui.py
```
*   **特性**: 支持最小化到托盘、实时日志查看、深色模式。
*   *注: Windows 用户可直接运行 `start.bat` 以隐藏控制台窗口。*

### 💻 终端仪表盘 (TUI)
在终端中获得可视化的交互体验。
```bash
python cli.py
```

### 🤖 纯命令行守护 (Headless)
适合服务器或后台服务使用。

```bash
# 单次登录 (成功或失败后立即退出)
python main.py

# 开启守护模式 (无限循环监控)
python main.py --loop

# 自定义检查间隔 (例如每 60 秒检查一次)
python main.py --loop --interval 60
```

### CLI 参数表 (`main.py`)

| 参数 Argument | 简写 | 描述 Description | 默认值 |
| :--- | :--- | :--- | :--- |
| `--loop` | - | 开启守护模式 (无限循环保持在线)。 | `False` |
| `--interval` | - | 覆盖默认的连通性检查间隔 (秒)。 | `300` (`.env`) |
| `--help` | `-h` | 显示帮助信息并退出。 | - |

## <span id="architecture">🏗️ 项目架构 (Architecture)</span>

```plaintext
szu-net/
├── app/
│   ├── client.py       # 核心策略引擎 (Teaching/Dorm)
│   ├── config.py       # Pydantic 配置管理 & .env 加载器
│   ├── log_utils.py    # 三路日志系统 (Console/File/GUI)
│   └── utils.py        # 网络探针 (Captive Portal Check)
├── app_gui.py          # 现代化 GUI 入口 (ttkbootstrap + pystray)
├── cli.py              # TUI 入口 (Rich)
├── encryption/         # SRUN 协议加密逻辑
│   ├── srun_base64.js  # 遗留的 JS 加密桥接脚本
│   └── srun_*.py       # MD5/SHA1/XEncode 的 Python 实现
├── main.py             # 命令行运行器 & 参数解析
└── requirements.txt    # Python 依赖列表
```

## 📜 许可证 (License)

本项目基于 [MIT License](LICENSE) 开源。
