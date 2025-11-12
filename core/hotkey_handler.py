from PyQt5.QtCore import QObject, pyqtSignal


class HotkeyHandler(QObject):
    toggle_signal = pyqtSignal()
    settings_signal = pyqtSignal()
    quit_signal = pyqtSignal()
