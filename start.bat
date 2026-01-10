@echo off
:: 1. 切换到脚本所在目录
cd /d %~dp0

:: 2. 设置绝对路径 (根据你提供的路径)
set PYTHONW_PATH="C:\Users\Aaten77\.conda\envs\szu-net\pythonw.exe"

:: 3. 启动！
:: start "" 是告诉 Windows "启动一个新进程，别管它了"
start "" %PYTHONW_PATH% app_gui.py

:: 4. 立刻退出黑窗口
exit