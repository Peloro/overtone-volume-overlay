"""Logging configuration for Overtone Application"""
import logging
from logging.handlers import RotatingFileHandler

_loggers = {}


def setup_logger(name: str = "overtone", log_file: str = "overtone.log", level: int = logging.INFO,
                max_bytes: int = 5 * 1024 * 1024, backup_count: int = 3) -> logging.Logger:
    """Setup and configure a logger with file and console handlers"""
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    logger.handlers.clear()
    
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter('%(levelname)s - %(module)s - %(message)s')
    
    try:
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file handler: {e}")
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    _loggers[name] = logger
    return logger


def get_logger(name: str = "overtone") -> logging.Logger:
    """Get or create a logger instance"""
    return _loggers.get(name) or setup_logger(name)
