import sys
from pathlib import Path
from loguru import logger

class QueueSink:
    """
    Custom Loguru Sink to push logs into a thread-safe queue.
    Prevents GUI crashes caused by logging from background threads.
    """
    def __init__(self, log_queue):
        self.log_queue = log_queue

    def write(self, message):
        self.log_queue.put(message)

def setup_logger(ui_queue=None):
    """
    Configure the logging system with a triple-stream strategy:
    1. Console: INFO (for dev/CLI)
    2. File: DEBUG (for auditing, auto-creates directory)
    3. GUI: INFO (for user, if queue provided)
    """
    logger.remove()
    
    # 1. Console Stream
    if sys.stderr:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level="INFO"
        )

    # 2. File Stream (Backend)
    log_path = Path("logs/szu_net.log")
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass # Handle permission errors gracefully if needed
    
    logger.add(
        str(log_path),
        rotation="00:00",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8"
    )
    
    # 3. GUI Stream (Frontend)
    if ui_queue:
        sink = QueueSink(ui_queue)
        logger.add(
            sink, 
            format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level: <8}</level> | {message}", 
            level="INFO"
        )
