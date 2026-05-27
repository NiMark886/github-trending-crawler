#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging Configuration Module

Features:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Console and file output
- Colored console output
- Log rotation
- Structured log format

Usage:
    from logger import setup_logger, get_logger

    setup_logger(level="INFO", log_file="app.log")
    logger = get_logger(__name__)
    logger.info("Application started")
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


# Custom log colors for console output
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }

    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        # Format the message
        result = super().format(record)

        # Reset levelname for file handler
        record.levelname = levelname

        return result


# Global logger registry
_loggers = {}
_initialized = False


def setup_logger(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    console_output: bool = True,
    file_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """
    Setup logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file name (auto-generated if None)
        log_dir: Directory for log files
        console_output: Enable console output
        file_output: Enable file output
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    global _initialized

    if _initialized:
        return

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Log format
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_format = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)

    # File handler
    if file_output:
        # Create log directory
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Generate log filename
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = f"github_crawler_{timestamp}.log"

        log_filepath = log_path / log_file

        # Use rotating file handler
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_filepath,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)

    _initialized = True

    # Log startup message
    logger = get_logger("logger")
    logger.info(f"日志系统初始化完成 (级别: {level})")
    if file_output:
        logger.info(f"日志文件: {log_path / log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)

    return _loggers[name]


def set_level(level: str):
    """
    Set global log level.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    logger = get_logger("logger")
    logger.info(f"日志级别已设置为: {level}")


def disable_logging():
    """Disable all logging."""
    logging.disable(logging.CRITICAL)


def enable_logging():
    """Enable logging."""
    logging.disable(logging.NOTSET)


# Convenience functions
def debug(msg: str, *args, **kwargs):
    """Log debug message."""
    get_logger("crawler").debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """Log info message."""
    get_logger("crawler").info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """Log warning message."""
    get_logger("crawler").warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """Log error message."""
    get_logger("crawler").error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """Log critical message."""
    get_logger("crawler").critical(msg, *args, **kwargs)


# Context manager for temporary log level
class LogLevel:
    """Context manager for temporary log level change."""

    def __init__(self, level: str):
        self.new_level = getattr(logging, level.upper(), logging.INFO)
        self.old_level = None

    def __enter__(self):
        root_logger = logging.getLogger()
        self.old_level = root_logger.level
        root_logger.setLevel(self.new_level)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        root_logger = logging.getLogger()
        root_logger.setLevel(self.old_level)
        return False


# Example usage
if __name__ == "__main__":
    # Setup logger
    setup_logger(level="DEBUG", log_file="test.log")

    # Get logger
    logger = get_logger(__name__)

    # Test different log levels
    logger.debug("这是一条 DEBUG 消息")
    logger.info("这是一条 INFO 消息")
    logger.warning("这是一条 WARNING 消息")
    logger.error("这是一条 ERROR 消息")
    logger.critical("这是一条 CRITICAL 消息")

    # Test context manager
    with LogLevel("WARNING"):
        logger.info("这条消息不会显示")
        logger.warning("这条消息会显示")

    logger.info("恢复正常日志级别")
