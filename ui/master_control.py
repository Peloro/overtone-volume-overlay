from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSlider,
                             QLabel, QPushButton, QLineEdit, QFrame)
from PyQt5.QtCore import Qt

from config import UIConstants, Colors, StyleSheets
from .base_volume_control import BaseVolumeControl


class MasterVolumeControl(QFrame, BaseVolumeControl):
    
    def __init__(self, audio_controller) -> None:
        QFrame.__init__(self)
        BaseVolumeControl.__init__(self)
        self.audio_controller = audio_controller
        self.init_volume_state(int(audio_controller.get_master_volume() * UIConstants.VOLUME_PERCENTAGE_FACTOR), audio_controller.get_master_mute())
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*[UIConstants.FRAME_MARGIN] * UIConstants.MARGIN_SIDES_COUNT)
        layout.setSpacing(UIConstants.CONTROL_SPACING)
        
        self.setMinimumWidth(UIConstants.MIN_CONTROL_WIDTH)
        
        self.setMouseTracking(True)
        
        self.master_label = QLabel("System Volume")
        self.master_label.setStyleSheet(StyleSheets.get_label_stylesheet())
        self.master_label.setMinimumWidth(UIConstants.STRETCH_FACTOR_NONE)
        layout.addWidget(self.master_label)
        
        master_control_layout = QHBoxLayout()
        master_control_layout.setSpacing(UIConstants.CONTROL_SPACING)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setMinimum(0)
        self.slider.setMaximum(UIConstants.VOLUME_PERCENTAGE_FACTOR)
        self.slider.setValue(self.previous_volume)
        self.slider.setStyleSheet(StyleSheets.get_master_slider_stylesheet())
        self.slider.valueChanged.connect(self.on_volume_changed)
        self.slider.setMinimumWidth(UIConstants.MIN_SLIDER_WIDTH)
        self.slider.setContentsMargins(UIConstants.STRETCH_FACTOR_NONE, UIConstants.STRETCH_FACTOR_NONE, 
                                       UIConstants.STRETCH_FACTOR_NONE, UIConstants.STRETCH_FACTOR_NONE)

        self.volume_text = QLineEdit()
        self.volume_text.setFocusPolicy(Qt.NoFocus)
        self.volume_text.setFixedWidth(UIConstants.VOLUME_TEXT_WIDTH)
        self.volume_text.setMinimumWidth(UIConstants.VOLUME_TEXT_WIDTH)
        self.volume_text.setText(str(self.previous_volume))
        self.volume_text.setStyleSheet(StyleSheets.get_master_volume_text_stylesheet())
        self.volume_text.setReadOnly(False)
        self.volume_text.returnPressed.connect(self.on_volume_text_changed)
        self.volume_text.editingFinished.connect(self.on_volume_text_changed)
        
        self.mute_button = QPushButton("🔇" if self.is_muted else "🔊")
        self.mute_button.setFocusPolicy(Qt.NoFocus)
        self.mute_button.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.mute_button.setMinimumSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.mute_button.setStyleSheet(StyleSheets.get_mute_button_stylesheet(is_master=True))
        self.mute_button.clicked.connect(self.on_mute_clicked)
        
        master_control_layout.addWidget(self.slider, UIConstants.STRETCH_FACTOR_STANDARD)
        master_control_layout.addWidget(self.volume_text, UIConstants.STRETCH_FACTOR_NONE)
        master_control_layout.addWidget(self.mute_button, UIConstants.STRETCH_FACTOR_NONE)
        layout.addLayout(master_control_layout)
        
        self.setStyleSheet(StyleSheets.get_frame_stylesheet(bg_color=Colors.MASTER_FRAME_BG))
    
    def on_volume_changed(self, value: int) -> None:
        self.handle_volume_slider_change(
            value,
            lambda vol: self.audio_controller.set_master_volume(vol / UIConstants.VOLUME_PERCENTAGE_FACTOR)
        )
    
    def on_mute_clicked(self) -> None:
        self.handle_mute_toggle(
            lambda: self.audio_controller.get_master_mute(),
            lambda mute: self.audio_controller.set_master_mute(mute)
        )
    
    def on_volume_text_changed(self) -> None:
        self.handle_volume_text_change()
    
    def apply_styles(self):
        self.setStyleSheet(StyleSheets.get_frame_stylesheet(bg_color=Colors.MASTER_FRAME_BG))
        
        if hasattr(self, 'master_label') and self.master_label:
            self.master_label.setStyleSheet(StyleSheets.get_label_stylesheet())
        
        if self.slider:
            self.slider.setStyleSheet(StyleSheets.get_master_slider_stylesheet())
        
        if self.volume_text:
            self.volume_text.setStyleSheet(StyleSheets.get_master_volume_text_stylesheet())
        
        if self.mute_button:
            self.mute_button.setStyleSheet(StyleSheets.get_mute_button_stylesheet(is_master=True))
        
        self.update()
