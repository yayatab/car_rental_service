import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.core.config import get_settings


def setup_logger(name: str = "car_rental") -> logging.Logger:
    settings = get_settings()
    returned_logger = logging.getLogger(name)

    if returned_logger.hasHandlers():
        return returned_logger

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    returned_logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    returned_logger.addHandler(console_handler)

    log_file_path = Path(settings.LOG_FILE_PATH)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=str(log_file_path),
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    returned_logger.addHandler(file_handler)

    returned_logger.propagate = False
    return returned_logger


logger = setup_logger()
