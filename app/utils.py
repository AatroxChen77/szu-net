import socket
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
