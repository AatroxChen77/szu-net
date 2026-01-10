@echo off
cd /d %~dp0

:: 1. 使用 python.exe (有窗口) 而不是 pythonw
:: 这样如果有错，会打印在屏幕上
set PYTHON_PATH="C:\Users\Aaten77\.conda\envs\szu-net\python.exe"

echo [INFO] Trying to launch with absolute path...
%PYTHON_PATH% app_gui.py

:: 2. 如果软件正常关闭或崩溃，才会运行到这行
echo.
echo ================================
echo [CRASH REPORT] Program stopped.
echo If you see an error above, take a screenshot!
echo ================================
pause