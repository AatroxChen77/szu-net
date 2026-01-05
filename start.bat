@echo off
cd /d %~dp0
:: 不需要设置颜色了，Python 会接管
title SZU Network Guardian

echo Launching Python Interface...

:: 激活环境后，直接运行新的 cli.py
call conda activate szu-net 2>nul
python cli.py

if %errorlevel% neq 0 pause