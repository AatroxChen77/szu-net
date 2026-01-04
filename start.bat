@echo off
:: Ensure working directory is the script directory
cd /d %~dp0
title SZU Network Monitor

echo [INFO] Initializing environment...

:: 1. Try to activate Conda environment (Silent mode)
call conda activate szu-net 2>nul
if %errorlevel% equ 0 (
    echo [INFO] Conda environment 'szu-net' activated.
) else (
    echo [INFO] Conda environment not found or failed. Using system Python...
)

echo.
:: 2. Start the main program
echo [INFO] Starting Daemon Process (Press Ctrl+C to stop)...
echo [LOG]  Monitoring network status...
echo ------------------------------------------

:: Run the python script
python main.py --loop

:: 3. Error Handling
if %errorlevel% neq 0 (
    echo.
    echo ------------------------------------------
    echo [ERROR] Program exited with error code: %errorlevel%
    echo.
    echo Please check the following:
    echo 1. Is Python installed and added to PATH?
    echo 2. Are dependencies installed? (pip install -r requirements.txt)
    echo 3. Is the .env file configured correctly?
    echo.
    pause
)