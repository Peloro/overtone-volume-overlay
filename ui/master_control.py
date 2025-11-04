"""
Master Volume Control Widget
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSlider,
                             QLabel, QPushButton, QLineEdit, QFrame)
from PyQt5.QtCore import Qt

from config import UIConstants, Colors, StyleSheets
from .base_volume_control import BaseVolumeControl


class MasterVolumeControl(QFrame, BaseVolumeControl):
    """Widget for controlling system master volume"""
    
    def __init__(self, audio_controller) -> None:
        QFrame.__init__(self)
        BaseVolumeControl.__init__(self)
        self.audio_controller = audio_controller
        self.init_volume_state(int(audio_controller.get_master_volume() * UIConstants.VOLUME_PERCENTAGE_FACTOR), audio_controller.get_master_mute())
        self.init_ui()
    
    def init_ui(self):
        """Initialize the master volume control UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*[UIConstants.FRAME_MARGIN] * UIConstants.MARGIN_SIDES_COUNT)
        layout.setSpacing(UIConstants.CONTROL_SPACING)
        
        # Set minimum size to prevent deformation
        self.setMinimumWidth(UIConstants.MIN_CONTROL_WIDTH)
        
        # Enable mouse tracking for hover events
        self.setMouseTracking(True)
        
        self.master_label = QLabel("System Volume")
        self.master_label.setStyleSheet(StyleSheets.get_label_stylesheet())
        self.master_label.setMinimumWidth(UIConstants.STRETCH_FACTOR_NONE)  # Allow text to be elided
        layout.addWidget(self.master_label)
        
        master_control_layout = QHBoxLayout()
        master_control_layout.setSpacing(UIConstants.CONTROL_SPACING)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(UIConstants.VOLUME_PERCENTAGE_FACTOR)
        self.slider.setValue(self.previous_volume)
        self.slider.setStyleSheet(StyleSheets.get_master_slider_stylesheet())
        self.slider.valueChanged.connect(self.on_volume_changed)
        self.slider.setMinimumWidth(UIConstants.MIN_SLIDER_WIDTH)
        self.slider.setContentsMargins(UIConstants.STRETCH_FACTOR_NONE, UIConstants.STRETCH_FACTOR_NONE, 
                                       UIConstants.STRETCH_FACTOR_NONE, UIConstants.STRETCH_FACTOR_NONE)

        self.volume_text = QLineEdit()
        self.volume_text.setFixedWidth(UIConstants.VOLUME_TEXT_WIDTH)
        self.volume_text.setMinimumWidth(UIConstants.VOLUME_TEXT_WIDTH)
        self.volume_text.setText(str(self.previous_volume))
        self.volume_text.setStyleSheet(StyleSheets.get_master_volume_text_stylesheet())
        self.volume_text.setReadOnly(False)
        self.volume_text.returnPressed.connect(self.on_volume_text_changed)
        self.volume_text.editingFinished.connect(self.on_volume_text_changed)
        
        self.mute_button = QPushButton("🔇" if self.is_muted else "🔊")
        self.mute_button.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.mute_button.setMinimumSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.mute_button.setStyleSheet(StyleSheets.get_mute_button_stylesheet(is_master=True))
        self.mute_button.clicked.connect(self.on_mute_clicked)
        
        master_control_layout.addWidget(self.slider, UIConstants.STRETCH_FACTOR_STANDARD)  # Give slider stretch factor
        master_control_layout.addWidget(self.volume_text, UIConstants.STRETCH_FACTOR_NONE)
        master_control_layout.addWidget(self.mute_button, UIConstants.STRETCH_FACTOR_NONE)
        layout.addLayout(master_control_layout)
        
        self.setStyleSheet(StyleSheets.get_frame_stylesheet(bg_color=Colors.MASTER_FRAME_BG))
    
    def on_volume_changed(self, value: int) -> None:
        """Handle master volume slider change"""
        self.handle_volume_slider_change(
            value,
            lambda vol: self.audio_controller.set_master_volume(vol / UIConstants.VOLUME_PERCENTAGE_FACTOR)
        )
    
    def on_mute_clicked(self) -> None:
        """Handle master mute button click"""
        self.handle_mute_toggle(
            lambda: self.audio_controller.get_master_mute(),
            lambda mute: self.audio_controller.set_master_mute(mute)
        )
    
    def on_volume_text_changed(self) -> None:
        """Handle master volume text box change"""
        self.handle_volume_text_change()
    
    def apply_styles(self):
        """Reapply all styles to reflect color changes"""
        # Reapply frame background
        self.setStyleSheet(StyleSheets.get_frame_stylesheet(bg_color=Colors.MASTER_FRAME_BG))
        
        # Reapply label style
        if hasattr(self, 'master_label') and self.master_label:
            self.master_label.setStyleSheet(StyleSheets.get_label_stylesheet())
        
        # Reapply slider style
        if self.slider:
            self.slider.setStyleSheet(StyleSheets.get_master_slider_stylesheet())
        
        # Reapply volume text style
        if self.volume_text:
            self.volume_text.setStyleSheet(StyleSheets.get_master_volume_text_stylesheet())
        
        # Reapply mute button style
        if self.mute_button:
            self.mute_button.setStyleSheet(StyleSheets.get_mute_button_stylesheet(is_master=True))
        
        # Force update
        self.update()
