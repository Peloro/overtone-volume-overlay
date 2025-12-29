"""Utility functions for logging and UI helpers"""
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Callable
from contextlib import contextmanager
from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

_loggers = {}

# Fallback values to avoid circular imports during logger initialization
_DEFAULT_LOG_MAX_BYTES = 5 * 1024 * 1024
_DEFAULT_LOG_BACKUP_COUNT = 3


# ========== Logging Functions ==========

def setup_logger(name: str = "overtone", log_file: str = "overtone.log", level: int = logging.INFO,
                max_bytes: int = None, backup_count: int = None) -> logging.Logger:
    # Use fallback values to avoid circular import during initialization
    if max_bytes is None:
        max_bytes = _DEFAULT_LOG_MAX_BYTES
    
    if backup_count is None:
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


# ========== UI Helper Functions ==========

@contextmanager
def batch_update(widget: QWidget):
    """Context manager for batch widget updates to reduce repaints"""
    widget.setUpdatesEnabled(False)
    try:
        yield widget
    finally:
        widget.setUpdatesEnabled(True)


def create_button(text: str, callback: Callable, tooltip: str = "", stylesheet: str = "",
                  fixed_width: int = None, fixed_height: int = None) -> QPushButton:
    """Create a QPushButton with optional styling and callbacks"""
    button = QPushButton(text)
    button.setFocusPolicy(Qt.NoFocus)  # Prevent focus stealing for fullscreen compatibility
    
    if fixed_width and fixed_height:
        button.setFixedSize(fixed_width, fixed_height)
    elif fixed_width:
        button.setFixedWidth(fixed_width)
    elif fixed_height:
        button.setFixedHeight(fixed_height)
    
    if stylesheet:
        button.setStyleSheet(stylesheet)
    if callback:
        button.clicked.connect(callback)
    if tooltip:
        button.setToolTip(tooltip)
    
    return button


def create_standard_button(text: str, callback: Callable, tooltip: str, stylesheet: str) -> QPushButton:
    """Create a standard-sized button"""
    from config import UIConstants
    return create_button(text, callback, tooltip, stylesheet, UIConstants.BUTTON_SIZE, UIConstants.BUTTON_SIZE)


def get_icon_path() -> str:
    """Get the path to the application icon"""
    from config import AppInfo
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', AppInfo.ICON_FILE)


def set_window_icon(widget) -> None:
    """Set the window icon for a widget"""
    icon_path = get_icon_path()
    if os.path.exists(icon_path):
        widget.setWindowIcon(QIcon(icon_path))
