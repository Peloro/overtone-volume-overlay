"""
Base Volume Control Widget
Contains shared functionality for volume controls
"""
from PyQt5.QtWidgets import QWidget, QSlider, QPushButton, QLineEdit
from PyQt5.QtCore import Qt


class BaseVolumeControl(QWidget):
    """Base class for volume control widgets with common functionality"""
    
    def __init__(self):
        super().__init__()
        self.previous_volume = 100
        self.slider = None
        self.volume_text = None
        self.mute_btn = None
    
    def init_volume_state(self, current_volume: int):
        """Initialize volume state, storing non-zero volume for unmute"""
        self.previous_volume = current_volume if current_volume > 0 else 100
    
    def update_mute_icon(self, volume: int):
        """Update mute button icon based on volume"""
        if self.mute_btn:
            self.mute_btn.setText("🔇" if volume == 0 else "🔊")
    
    def handle_volume_slider_change(self, value: int, set_volume_callback):
        """
        Handle slider value change with common logic
        
        Args:
            value: New volume value (0-100)
            set_volume_callback: Function to call to actually set the volume
        """
        set_volume_callback(value / 100.0)
        
        if self.volume_text:
            self.volume_text.setText(str(value))
        
        if value > 0:
            self.previous_volume = value
        
        self.update_mute_icon(value)
    
    def handle_mute_toggle(self, set_mute_callback):
        """
        Handle mute button click with common logic
        
        Args:
            set_mute_callback: Function to call to set mute state (True/False)
        """
        if not self.slider or not self.volume_text:
            return
        
        current_volume = self.slider.value()
        
        if current_volume > 0:
            self.previous_volume = current_volume
            self.slider.setValue(0)
            set_mute_callback(True)
            self.volume_text.setText("0")
            self.update_mute_icon(0)
        else:
            self.slider.setValue(self.previous_volume)
            set_mute_callback(False)
            self.volume_text.setText(str(self.previous_volume))
            self.update_mute_icon(self.previous_volume)
    
    def handle_volume_text_change(self):
        """Handle volume text box change with validation"""
        if not self.volume_text or not self.slider:
            return
        
        try:
            value = int(self.volume_text.text())
            value = max(0, min(100, value))
            self.slider.setValue(value)
        except ValueError:
            self.volume_text.setText(str(self.slider.value()))
