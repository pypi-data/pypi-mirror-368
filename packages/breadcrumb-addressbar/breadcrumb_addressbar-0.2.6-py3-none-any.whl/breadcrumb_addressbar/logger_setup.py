"""
Logger setup utility for Breadcrumb Address Bar library.

Provides centralized logging configuration for the project.
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "breadcrumb_addressbar",
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Setup and configure logger for the project.

    Args:
        name: Logger name
        level: Logging level
        log_format: Custom log format string
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # 既存のハンドラーをクリア（重複を防ぐ）
    if logger.handlers:
        logger.handlers.clear()

    logger.setLevel(level)

    # デフォルトのログフォーマット
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)

    # コンソールハンドラー
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラー（指定された場合）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "breadcrumb_addressbar") -> logging.Logger:
    """
    Get logger instance for the project.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# デフォルトロガーの初期化
_default_logger = setup_logger()


def debug(message: str) -> None:
    """Log debug message."""
    _default_logger.debug(message)


def info(message: str) -> None:
    """Log info message."""
    _default_logger.info(message)


def warning(message: str) -> None:
    """Log warning message."""
    _default_logger.warning(message)


def error(message: str) -> None:
    """Log error message."""
    _default_logger.error(message)


def critical(message: str) -> None:
    """Log critical message."""
    _default_logger.critical(message)
