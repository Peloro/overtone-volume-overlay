"""UI Utilities for common widget operations"""
import os
from typing import Callable
from contextlib import contextmanager
from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtGui import QIcon
from config import UIConstants, AppInfo


@contextmanager
def batch_update(widget: QWidget):
    """
    Context manager for batch UI updates.
    Disables widget updates during context, then re-enables them.
    This reduces repaints and improves performance for multiple UI changes.
    
    Example:
        with batch_update(self):
            self.update_control_1()
            self.update_control_2()
    """
    widget.setUpdatesEnabled(False)
    try:
        yield widget
    finally:
        widget.setUpdatesEnabled(True)


def create_button(text: str, callback: Callable, tooltip: str = "", stylesheet: str = "",
                  fixed_width: int = None, fixed_height: int = None) -> QPushButton:
    """Create a QPushButton with common properties"""
    button = QPushButton(text)
    
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
    """Create a standard button with the default size"""
    return create_button(text, callback, tooltip, stylesheet, UIConstants.BUTTON_SIZE, UIConstants.BUTTON_SIZE)


def get_icon_path() -> str:
    """Get the path to the application icon"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', AppInfo.ICON_FILE)


def set_window_icon(widget) -> None:
    """Set window icon for a widget if icon exists"""
    icon_path = get_icon_path()
    if os.path.exists(icon_path):
        widget.setWindowIcon(QIcon(icon_path))
