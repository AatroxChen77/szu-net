@echo off
:: 1. 切换到脚本所在目录
cd /d %~dp0

:: 2. 激活 Conda 环境 (关键步骤，否则找不到库)
call conda activate szu-net 2>nul

:: 3. 启动 GUI (使用 start 命令)
:: start "" "pythonw" ... 表示用无窗口模式启动，且不等待程序结束
:: 这里的 app_gui.py 不需要改成 .pyw，保留 .py 即可
start "" pythonw app_gui.py

:: 4. Bat 脚本立刻退出 (黑窗口闪一下就消失)
exit