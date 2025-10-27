"""
Hotkey Handler for thread-safe Qt signal emission
"""
from PyQt5.QtCore import QObject, pyqtSignal


class HotkeyHandler(QObject):
    """Handler for hotkey signals to ensure thread-safe Qt operations"""
    toggle_signal = pyqtSignal()
    settings_signal = pyqtSignal()
    quit_signal = pyqtSignal()
