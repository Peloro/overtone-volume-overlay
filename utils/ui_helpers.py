"""
UI Utilities for common widget operations
"""
from typing import Callable
from PyQt5.QtWidgets import QPushButton
from config import UIConstants


def create_button(
    text: str,
    callback: Callable,
    tooltip: str = "",
    stylesheet: str = "",
    fixed_width: int = None,
    fixed_height: int = None
) -> QPushButton:
    """
    Create a QPushButton with common properties
    
    Args:
        text: Button text
        callback: Click handler function
        tooltip: Tooltip text
        stylesheet: Qt stylesheet string
        fixed_width: Fixed width in pixels (None for default)
        fixed_height: Fixed height in pixels (None for default)
    
    Returns:
        Configured QPushButton
    """
    button = QPushButton(text)
    
    if fixed_width is not None and fixed_height is not None:
        button.setFixedSize(fixed_width, fixed_height)
    elif fixed_width is not None:
        button.setFixedWidth(fixed_width)
    elif fixed_height is not None:
        button.setFixedHeight(fixed_height)
    
    if stylesheet:
        button.setStyleSheet(stylesheet)
    
    button.clicked.connect(callback)
    
    if tooltip:
        button.setToolTip(tooltip)
    
    return button


def create_standard_button(text: str, callback: Callable, tooltip: str, stylesheet: str) -> QPushButton:
    """
    Create a standard button with the default size
    
    Args:
        text: Button text
        callback: Click handler function
        tooltip: Tooltip text
        stylesheet: Qt stylesheet string
    
    Returns:
        Configured QPushButton with standard size
    """
    return create_button(
        text=text,
        callback=callback,
        tooltip=tooltip,
        stylesheet=stylesheet,
        fixed_width=UIConstants.BUTTON_SIZE,
        fixed_height=UIConstants.BUTTON_SIZE
    )
