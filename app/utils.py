import socket
import requests
from loguru import logger

def get_local_ip(target_host="8.8.8.8", target_port=80) -> str:
    """
    Get the local IP address used to connect to the outside world.
    This method is cross-platform (Windows/Linux/macOS) and does not rely on system commands.
    
    Args:
        target_host: The target host to connect to (default: Google DNS).
        target_port: The target port to connect to.
        
    Returns:
        str: The local IP address.
        
    Raises:
        OSError: If network is unreachable.
    """
    try:
        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to an external server (doesn't actually send data)
            s.connect((target_host, target_port))
            local_ip = s.getsockname()[0]
            logger.debug(f"Detected local IP: {local_ip}")
            return local_ip
    except Exception as e:
        logger.error(f"Failed to detect local IP: {e}")
        # Fallback for localhost if offline (though login will fail anyway)
        return "127.0.0.1"

def is_internet_connected(test_url: str = "http://www.baidu.com", timeout: int = 3) -> bool:
    """
    检查互联网连接状态
    :param test_url: 用于测试的网站 (推荐国内访问快的)
    :param timeout: 超时时间 (秒)
    :return: True (通) / False (断)
    """
    try:
        # 使用 head 请求减少流量，timeout 设短一点防止卡顿
        requests.head(test_url, timeout=timeout)
        return True
    except:
        return False
