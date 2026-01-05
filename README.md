# 🌐 SZU 教学区校园网自动登录脚本

专为深圳大学（SZU）教学区网络设计的自动登录工具。基于 Python 实现，内置 SRUN 认证协议支持，支持断线自动重连与守护模式。

## ✨ 功能特性

*   🚀 **智能启动**：通过 `start.bat` 自动检测运行环境（Conda/System Python），一键启动。
*   🔄 **守护模式**：支持 `--loop` 参数（默认开启），每 5 分钟（可配）自动检测网络状态，掉线即秒连。
*   🔐 **安全配置**：使用 `.env` 文件管理敏感信息，无需修改代码。
*   🛠️ **协议原生**：内置 Python/JS 混合加密逻辑，完美适配 SRUN 认证，无需浏览器驱动。

## 🛠️ 环境要求

*   **操作系统**: 🪟 Windows (脚本依赖 `ipconfig` 输出格式)
*   **Python**: 🐍 Python 3.8+
*   **运行时**: 🟢 Node.js (必需，用于执行加密 JS 代码)

## 📦 安装指南

### 1. 获取代码
```bash
git clone https://github.com/your-repo/szu-net.git
cd szu-net
```

### 2. 环境配置 (二选一)

**选项 A: 使用 Conda (推荐)**
```bash
conda create -n szu-net python=3.10
conda activate szu-net
conda install -c conda-forge nodejs
pip install -r requirements.txt
```

**选项 B: 使用系统 Python**
```bash
pip install -r requirements.txt
```

### 3. 填写配置
复制配置文件模板，并填入你的校园网账号密码：

1.  将项目根目录下的 `.env.example` 复制一份并重命名为 `.env`。
2.  用记事本打开 `.env`，修改以下内容：
    ```ini
    SRUN_USERNAME=2020123456      # 你的学号
    SRUN_PASSWORD=your_password   # 你的密码
    ```

## ▶️ 使用方法

### 🚀 推荐方式 (Windows)
直接双击运行根目录下的 **`start.bat`**。
*   脚本会自动尝试激活名为 `szu-net` 的 Conda 环境。
*   如果未找到 Conda 环境，将回退使用系统 Python。
*   启动后将进入守护模式，持续监控网络。

### 💻 命令行方式
```bash
# 单次登录
python main.py

# 开启守护模式 (每300秒检查一次)
python main.py --loop

# 自定义检查间隔 (例如 60 秒)
python main.py --loop --interval 60
```

## ⚙️ 高级配置 (.env)

| 变量名 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `SRUN_USERNAME` | - | **(必填)** 校园网账号 |
| `SRUN_PASSWORD` | - | **(必填)** 校园网密码 |
| `RETRY_INTERVAL` | 300 | 守护模式下的重试/检查间隔(秒) |
| `SRUN_AC_ID` | 12 | AC ID (教学区通常为 12) |

## ❓ 常见问题

*   **`execjs.RuntimeUnavailable`**: 
    *   请确保已安装 Node.js 并将其添加到系统环境变量 PATH 中。
*   **启动闪退**: 
    *   请先在命令行运行 `start.bat` 查看具体报错信息。
    *   检查 `.env` 文件是否存在且格式正确。
*   **一直提示 "Login failed"**: 
    *   检查账号密码是否正确。
    *   检查是否欠费。
    *   尝试手动登录 `net.szu.edu.cn` 确认账号状态。

## 📝 许可证

MIT License
