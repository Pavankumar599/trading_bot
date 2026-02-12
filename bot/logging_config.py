import logging
from logging.handlers import RotatingFileHandler
import os

DEFAULT_LOG_PATH = os.path.join("logs", "bot.log")

def setup_logging(log_path: str = DEFAULT_LOG_PATH, level: int = logging.INFO) -> None:
    """Configure rotating file logging and a concise console logger."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if root.handlers:
        return

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(fmt)

    root.addHandler(file_handler)
    root.addHandler(console_handler)
