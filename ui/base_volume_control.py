"""Base Volume Control Widget - Contains shared functionality for volume controls"""
from typing import Callable
from PyQt5.QtWidgets import QWidget, QSlider, QPushButton, QLineEdit
from PyQt5.QtCore import QTimer
from config import UIConstants


class BaseVolumeControl(QWidget):
    """Base class for volume control widgets with common functionality"""
    
    def __init__(self) -> None:
        super().__init__()
        self.previous_volume = 100
        self.slider = None
        self.volume_text = None
        self.mute_button = None
        self.is_muted = False
        self._is_hovered = False
    
    def init_volume_state(self, current_volume: int, is_muted: bool = False) -> None:
        """Initialize volume state, storing non-zero volume for unmute"""
        self.previous_volume = current_volume if current_volume > 0 else 100
        self.is_muted = is_muted
    
    def update_mute_icon(self, is_muted: bool) -> None:
        """Update mute button icon based on mute state"""
        if self.mute_button:
            self.mute_button.setText("🔇" if is_muted else "🔊")
    
    def handle_volume_slider_change(self, value: int, set_volume_callback: Callable[[float], bool]) -> None:
        """Handle slider value change with common logic"""
        set_volume_callback(value / 100.0)
        if self.volume_text:
            self.volume_text.setText(str(value))
        if value > 0:
            self.previous_volume = value
    
    def handle_mute_toggle(self, get_mute_callback: Callable[[], bool], set_mute_callback: Callable[[bool], bool]) -> None:
        """Handle mute button click with common logic"""
        if not (self.slider and self.volume_text):
            return
        
        try:
            new_mute = not get_mute_callback()
            if set_mute_callback(new_mute):
                self.is_muted = new_mute
                self.update_mute_icon(new_mute)
        except Exception as e:
            print(f"Error toggling mute: {e}")
    
    def handle_volume_text_change(self) -> None:
        """Handle volume text box change with validation"""
        if not self.volume_text or not self.slider:
            return
        
        try:
            self.slider.setValue(max(0, min(100, int(self.volume_text.text()))))
        except ValueError:
            self.volume_text.setText(str(self.slider.value()))
            original_style = self.volume_text.styleSheet()
            self.volume_text.setStyleSheet(original_style + "border: 2px solid #f44336;")
            QTimer.singleShot(UIConstants.ERROR_FLASH_DURATION_MS, lambda: self.volume_text.setStyleSheet(original_style))
    
    def wheelEvent(self, event) -> None:
        """Handle mouse wheel events for volume adjustment"""
        if not self._is_hovered:
            event.ignore()
            return
        
        delta = 5 if event.angleDelta().y() > 0 else -5
        new_volume = max(0, min(100, self.slider.value() + delta))
        self.slider.setValue(new_volume)
        event.accept()
    
    def enterEvent(self, event) -> None:
        """Handle mouse enter event"""
        self._is_hovered = True
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """Handle mouse leave event"""
        self._is_hovered = False
        super().leaveEvent(event)
