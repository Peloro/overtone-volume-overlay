from typing import Callable
from PyQt5.QtWidgets import QWidget, QSlider, QPushButton, QLineEdit
from PyQt5.QtCore import QTimer
from config import UIConstants
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseVolumeControl(QWidget):
    
    def __init__(self) -> None:
        super().__init__()
        self.previous_volume = UIConstants.VOLUME_PERCENTAGE_FACTOR
        self.slider = None
        self.volume_text = None
        self.mute_button = None
        self.is_muted = False
        self._is_hovered = False
    
    def init_volume_state(self, current_volume: int, is_muted: bool = False) -> None:
        self.previous_volume = current_volume if current_volume > 0 else UIConstants.VOLUME_PERCENTAGE_FACTOR
        self.is_muted = is_muted
    
    def update_mute_icon(self, is_muted: bool) -> None:
        if self.mute_button:
            self.mute_button.setText("🔇" if is_muted else "🔊")
    
    def handle_volume_slider_change(self, value: int, set_volume_callback: Callable[[float], bool]) -> None:
        set_volume_callback(value)
        if self.volume_text:
            self.volume_text.setText(str(value))
        if value > 0:
            self.previous_volume = value
    
    def handle_mute_toggle(self, get_mute_callback: Callable[[], bool], set_mute_callback: Callable[[bool], bool]) -> None:
        if not (self.slider and self.volume_text):
            return
        
        try:
            new_mute = not get_mute_callback()
            if set_mute_callback(new_mute):
                self.is_muted = new_mute
                self.update_mute_icon(new_mute)
        except Exception as e:
            logger.error(f"Error toggling mute: {e}", exc_info=True)
    
    def handle_volume_text_change(self) -> None:
        if not self.volume_text or not self.slider:
            return
        
        try:
            self.slider.setValue(max(0, min(UIConstants.VOLUME_PERCENTAGE_FACTOR, int(self.volume_text.text()))))
        except ValueError:
            self.volume_text.setText(str(self.slider.value()))
            original_style = self.volume_text.styleSheet()
            self.volume_text.setStyleSheet(original_style + "border: 2px solid #f44336;")
            QTimer.singleShot(UIConstants.ERROR_FLASH_DURATION_MS, lambda: self.volume_text.setStyleSheet(original_style))
    
    def wheelEvent(self, event) -> None:
        if not self._is_hovered:
            event.ignore()
            return
        
        delta = UIConstants.WHEEL_SCROLL_DELTA if event.angleDelta().y() > 0 else -UIConstants.WHEEL_SCROLL_DELTA
        new_volume = max(0, min(UIConstants.VOLUME_PERCENTAGE_FACTOR, self.slider.value() + delta))
        self.slider.setValue(new_volume)
        event.accept()
    
    def enterEvent(self, event) -> None:
        self._is_hovered = True
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        self._is_hovered = False
        super().leaveEvent(event)
