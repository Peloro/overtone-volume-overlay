import logging
from logging.handlers import RotatingFileHandler

_loggers = {}

_DEFAULT_LOG_MAX_BYTES = 5 * 1024 * 1024
_DEFAULT_LOG_BACKUP_COUNT = 3


def setup_logger(name: str = "overtone", log_file: str = "overtone.log", level: int = logging.INFO,
                max_bytes: int = None, backup_count: int = None) -> logging.Logger:
    if max_bytes is None:
        try:
            from config import UIConstants
            max_bytes = UIConstants.LOG_MAX_BYTES
        except ImportError:
            max_bytes = _DEFAULT_LOG_MAX_BYTES
    
    if backup_count is None:
        try:
            from config import UIConstants
            backup_count = UIConstants.LOG_BACKUP_COUNT
        except ImportError:
            backup_count = _DEFAULT_LOG_BACKUP_COUNT
    
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
        logging.basicConfig(level=logging.WARNING)
        logging.warning(f"Could not create log file handler: {e}")
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    _loggers[name] = logger
    return logger


def get_logger(name: str = "overtone") -> logging.Logger:
    return _loggers.get(name) or setup_logger(name)
