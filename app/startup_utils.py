import winreg
import pathlib
from loguru import logger

REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "SZUNetworkGuardian"

def get_startup_status() -> bool:
    """
    Check if the application is set to run at Windows startup.
    Returns:
        bool: True if the registry key exists, False otherwise.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False
    except Exception as e:
        logger.error(f"Error checking startup status: {e}")
        return False

def toggle_startup(enable: bool):
    """
    Enable or disable the application to run at Windows startup.
    Args:
        enable (bool): True to enable, False to disable.
    """
    try:
        if enable:
            # Explicitly resolve the path to start.bat relative to the project root
            # This module is in 'app/', so project root is the parent directory.
            project_root = pathlib.Path(__file__).resolve().parent.parent
            bat_path = project_root / "start.bat"
            
            if not bat_path.exists():
                logger.error(f"Cannot enable startup: 'start.bat' not found at {bat_path}")
                return

            # Wrap the absolute path in double quotes to handle spaces correctly
            cmd = f'"{bat_path}"'
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            logger.success(f"Startup enabled: Registry key '{APP_NAME}' set to {cmd}")
        else:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    logger.success(f"Startup disabled: Registry key '{APP_NAME}' removed.")
                except FileNotFoundError:
                    # Key already doesn't exist, which is fine
                    pass
    except Exception as e:
        logger.error(f"Failed to toggle startup: {e}")
