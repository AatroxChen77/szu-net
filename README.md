<div align="center">

# SZU Network Guardian

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-brightgreen)](https://github.com/your-repo/szu-net)

**深圳大学校园网双区自动登录工具**

> **全场景覆盖**：专为深圳大学（SZU）设计的网络认证工具，现已支持 **教学区 (SRUN)** 与 **宿舍区 (Dr.COM)** 双网区自动登录与断线重连。

</div>

---

<p align="center">
  <a href="#features">✨ 核心特性</a> •
  <a href="#installation">⚙️ 安装指南</a> •
  <a href="#configuration">⚙️ 配置说明</a> •
  <a href="#usage">� 使用方法</a> •
  <a href="#troubleshooting">❓ 常见问题</a>
</p>

## 简介 (Introduction)

本项目旨在提供一个稳定、跨平台的校园网自动登录解决方案。无论是教学区复杂的 SRUN 协议（涉及 JS 逆向加密），还是宿舍区 Dr.COM 的 Web 认证，本工具都能通过统一的配置和接口轻松搞定。

它内置了 **"Keep-Alive" 守护模式**，能够持续监控网络连通性（通过 Captive Portal 检测），一旦发现断网或认证失效，立即触发重连，确保您的设备 24 小时在线。

---

## <span id="features">✨ 核心特性 (Key Features)</span>

- 🏰 **双区支持 (Dual-Zone)**
    - **教学区 (Teaching)**: 原生实现 SRUN 协议，内置 Python/JS 混合加密引擎 (PyExecJS)，无需浏览器驱动。
    - **宿舍区 (Dorm)**: 完美适配 Dr.COM Web Portal 认证流程，支持 GBK/UTF-8 编码自动处理。
- 🖥️ **炫酷 TUI 仪表盘**
    - 基于 `rich` 库构建的终端用户界面，提供启动动画、实时状态面板和清晰的日志输出。
- 🔄 **智能守护 (Daemon Mode)**
    - 自动检测网络状态（HTTP 204 Check），断线秒连。
    - 支持自定义检测间隔。
- ⚙️ **配置分离**
    - 通过 `.env` 环境变量管理敏感信息（账号/密码），安全且易于迁移。
- 🛠️ **跨平台**
    - 支持 Windows, Linux, macOS。

---

## <span id="installation">⚙️ 安装指南 (Installation)</span>

### 1. 环境要求
*   **Python**: 3.8+
*   **Node.js**: 必需（用于处理教学区 SRUN 协议的加密逻辑）

### 2. 获取代码
```bash
git clone https://github.com/your-repo/szu-net.git
cd szu-net
```

### 3. 安装依赖
```bash
# 推荐使用虚拟环境
pip install -r requirements.txt
```

---

## <span id="configuration">⚙️ 配置说明 (Configuration)</span>

在项目根目录下创建一个 `.env` 文件（可复制 `.env.example`），并填入以下内容：

```ini
# --- 认证信息 ---
SRUN_USERNAME=2020123456      # 你的学号
SRUN_PASSWORD=your_password   # 你的密码

# --- 网络区域选择 ---
# teaching = 教学区 (SRUN)
# dorm     = 宿舍区 (Dr.COM)
NETWORK_ZONE=teaching

# --- 进阶配置 (可选) ---
RETRY_INTERVAL=300            # 守护模式检查间隔(秒)
SRUN_AC_ID=12                 # 教学区 AC ID (通常无需修改)
```

---

## <span id="usage">🚀 使用方法 (Usage)</span>

### 🚀 快速启动 (Windows)
直接双击运行根目录下的 **`start.bat`**。
*   脚本会自动激活环境并启动 TUI 仪表盘。
*   默认进入守护模式。

### 💻 命令行启动
如果您偏好命令行或在 Linux/macOS 上运行：

#### 方式一：启动 TUI 面板 (推荐)
```bash
python cli.py
```
*这将展示带动画和面板的交互式界面。*

#### 方式二：后台纯净模式
```bash
# 单次登录（执行完即退出）
python main.py

# 开启守护模式 (持续监控)
python main.py --loop

# 自定义检查间隔 (例如 60 秒)
python main.py --loop --interval 60
```

---

## <span id="architecture">🏗️ 项目架构 (Architecture)</span>

*   **Entry Points**:
    *   `cli.py`: 用户入口，提供 Rich TUI 界面。
    *   `main.py`: 核心逻辑入口，处理参数解析和信号。
*   **App Core (`app/`)**:
    *   `client.py`: 核心客户端类 `SZUNetworkClient`。使用 **策略模式** 根据 `NETWORK_ZONE` 动态切换登录逻辑。
    *   `config.py`: 基于 `pydantic` 的强类型配置管理。
*   **Encryption (`encryption/`)**:
    *   包含处理 SRUN 协议所需的 XEncode, MD5, SHA1 算法实现及 `srun_base64.js`。

---

## <span id="troubleshooting">❓ 常见问题 & 故障排查 (Troubleshooting)</span>

### 🛑 脚本运行中突然卡住/不刷新日志？
**现象**：程序运行一段时间后，日志停止更新（疑似假死），只有**按下回车键 (Enter)** 后，才会瞬间刷出一堆日志并继续运行。

**原因**：这是 Windows 命令提示符 (CMD) 的 **"快速编辑模式" (Quick Edit Mode)** 导致的。当你无意中点击了窗口内容时，CMD 会挂起进程等待你复制文本。

**解决方法**：
1. 在运行脚本的黑窗口**标题栏**上点击右键 -> 选择 **"属性" (Properties)**。
2. 在 **"选项" (Options)** 标签页中。
3. **取消勾选** `快速编辑模式 (QuickEdit Mode)`。
4. 点击确定。

---

## � 许可证 (License)

[MIT License](LICENSE)
