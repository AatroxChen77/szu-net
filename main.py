import argparse
import sys
import signal
import threading
from loguru import logger
from app.client import SZUNetworkClient
from app.config import settings

# Global event for graceful shutdown
stop_event = threading.Event()

def signal_handler(signum, frame):
    """Handle termination signals."""
    signame = signal.Signals(signum).name
    logger.info(f"Received signal {signame} ({signum}), stopping daemon...")
    stop_event.set()

def configure_logging():
    logger.remove()
    logger.add(
        sys.stderr, 
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add("logs/monitor.log", rotation="1 day", retention="7 days", level="DEBUG", compression="zip")

def run_daemon(force_loop=False):
    parser = argparse.ArgumentParser(description="SZU Teaching Area Network Auto-Login")
    parser.add_argument("--loop", action="store_true", help="Run in daemon mode (keep-alive)")
    parser.add_argument("--interval", type=int, help="Override check interval in seconds", default=settings.RETRY_INTERVAL)
    args = parser.parse_args()

    configure_logging()
    
    # Update settings from args if provided
    if args.interval:
        settings.RETRY_INTERVAL = args.interval

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        client = SZUNetworkClient()
        
        if args.loop or force_loop:
            logger.info("Starting daemon... Press Ctrl+C to stop.")
            client.keep_alive(stop_event=stop_event)
        else:
            success = client.login()
            sys.exit(0 if success else 1)
            
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("Application exited.")

if __name__ == "__main__":
    run_daemon()
