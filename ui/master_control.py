"""
Master Volume Control Widget
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSlider,
                             QLabel, QPushButton, QLineEdit, QFrame)
from PyQt5.QtCore import Qt

from config.constants import UIConstants, Colors, StyleSheets
from .base_volume_control import BaseVolumeControl


class MasterVolumeControl(QFrame, BaseVolumeControl):
    """Widget for controlling system master volume"""
    
    def __init__(self, audio_controller):
        QFrame.__init__(self)
        BaseVolumeControl.__init__(self)
        self.audio_controller = audio_controller
        
        master_volume = self.audio_controller.get_master_volume()
        current_master_vol = int(master_volume * 100)
        self.init_volume_state(current_master_vol)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the master volume control UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            UIConstants.FRAME_MARGIN,
            UIConstants.FRAME_MARGIN,
            UIConstants.FRAME_MARGIN,
            UIConstants.FRAME_MARGIN
        )
        layout.setSpacing(UIConstants.CONTROL_SPACING)
        
        master_label = QLabel("🔊 System Volume")
        master_label.setStyleSheet(StyleSheets.get_label_stylesheet())
        layout.addWidget(master_label)
        
        master_control_layout = QHBoxLayout()
        
        self.master_slider = QSlider(Qt.Horizontal)
        self.master_slider.setMinimum(0)
        self.master_slider.setMaximum(100)
        master_volume = self.audio_controller.get_master_volume()
        self.master_slider.setValue(int(master_volume * 100))
        self.master_slider.setStyleSheet(StyleSheets.get_master_slider_stylesheet())
        self.master_slider.valueChanged.connect(self.on_volume_changed)
        
        self.slider = self.master_slider
        
        self.master_volume_text = QLineEdit()
        self.master_volume_text.setFixedWidth(UIConstants.VOLUME_TEXT_WIDTH)
        self.master_volume_text.setText(str(int(master_volume * 100)))
        self.master_volume_text.setStyleSheet(StyleSheets.get_master_volume_text_stylesheet())
        self.master_volume_text.setReadOnly(False)
        self.master_volume_text.returnPressed.connect(self.on_volume_text_changed)
        self.master_volume_text.editingFinished.connect(self.on_volume_text_changed)
        
        self.volume_text = self.master_volume_text
        
        is_muted = self.audio_controller.get_master_mute()
        self.master_mute_btn = QPushButton("🔇" if is_muted else "🔊")
        self.master_mute_btn.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.master_mute_btn.setStyleSheet(StyleSheets.get_mute_button_stylesheet(is_master=True))
        self.master_mute_btn.clicked.connect(self.on_mute_clicked)
        
        self.mute_btn = self.master_mute_btn
        
        master_control_layout.addWidget(self.master_slider)
        master_control_layout.addWidget(self.master_volume_text)
        master_control_layout.addWidget(self.master_mute_btn)
        
        layout.addLayout(master_control_layout)
        
        self.setStyleSheet(StyleSheets.get_frame_stylesheet(
            bg_color=Colors.MASTER_FRAME_BG
        ))
    
    def on_volume_changed(self, value):
        """Handle master volume slider change"""
        self.handle_volume_slider_change(
            value,
            lambda vol: self.audio_controller.set_master_volume(vol)
        )
    
    def on_mute_clicked(self):
        """Handle master mute button click"""
        self.handle_mute_toggle(
            lambda mute: self.audio_controller.set_master_mute(mute)
        )
    
    def on_volume_text_changed(self):
        """Handle master volume text box change"""
        self.handle_volume_text_change()
