import logging
from logging.handlers import RotatingFileHandler
import os


def get_logger(
    name: str = __name__,
    log_level: int = logging.INFO,
    log_dir: str = "logs",
    log_file: str = "app.log",
) -> logging.Logger:
    """
    Set up and return a configured logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    # Define formats
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    file_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_format)

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, log_file),
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_format)

    # Attach handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = get_logger(
    log_file="app.log",
    log_level=logging.DEBUG,
    name="fast-api app"
)
