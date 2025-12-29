from typing import Dict, Any
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSlider, 
                             QLabel, QPushButton, QLineEdit, QFrame)
from PyQt5.QtCore import Qt

from config import UIConstants, Colors, StyleSheets
from .base_volume_control import BaseVolumeControl


class AppVolumeControl(QFrame, BaseVolumeControl):
    
    def __init__(self, session: Dict[str, Any], audio_controller) -> None:
        QFrame.__init__(self)
        BaseVolumeControl.__init__(self)
        self.session = session
        self.audio_controller = audio_controller
        self._is_master = False
        self.init_volume_state(int(session['volume'] * UIConstants.VOLUME_PERCENTAGE_FACTOR), session.get('muted', False))
        self.init_ui()

    def update_session(self, session: Dict[str, Any]) -> None:
        """Update the control with new session data"""
        self.session = session
        new_val = int(session['volume'] * UIConstants.VOLUME_PERCENTAGE_FACTOR)
        new_muted = session.get('muted', False)
        
        # Update slider value if different
        if self.slider and self.slider.value() != new_val:
            self.slider.blockSignals(True)
            self.slider.setValue(new_val)
            self.slider.blockSignals(False)
            
        # Update volume text if different
        if self.volume_text:
            new_val_str = str(new_val)
            if self.volume_text.text() != new_val_str:
                self.volume_text.setText(new_val_str)
                
        # Update mute state if different
        if self.is_muted != new_muted:
            self.is_muted = new_muted
            self.update_mute_icon(new_muted)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*[UIConstants.FRAME_MARGIN] * UIConstants.MARGIN_SIDES_COUNT)
        layout.setSpacing(UIConstants.CONTROL_SPACING)
        self.setStyleSheet(StyleSheets.get_frame_stylesheet(bg_color=Colors.APP_CONTROL_BG))
        
        self.setFixedHeight(UIConstants.APP_CONTROL_HEIGHT)
        self.setMinimumWidth(UIConstants.MIN_CONTROL_WIDTH)
        self.setMaximumHeight(UIConstants.APP_CONTROL_HEIGHT)
        
        from PyQt5.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.setMouseTracking(True)
        
        self.name_label = QLabel(self.session['name'])
        self.name_label.setStyleSheet(StyleSheets.get_label_stylesheet())
        self.name_label.setMinimumWidth(UIConstants.STRETCH_FACTOR_NONE)
        self.name_label.setWordWrap(False)
        self.name_label.setTextFormat(Qt.PlainText)
        self.name_label.setSizePolicy(self.name_label.sizePolicy().Ignored, self.name_label.sizePolicy().Preferred)
        font_metrics = self.name_label.fontMetrics()
        elided_text = font_metrics.elidedText(self.session['name'], Qt.ElideMiddle, UIConstants.TEXT_ELIDE_WIDTH)
        self.name_label.setText(elided_text)
        self.name_label.setToolTip(self.session['name'])  # Show full name on hover
        self._label = self.name_label  # Reference for base class apply_styles
        layout.addWidget(self.name_label)
        
        control_layout = QHBoxLayout()
        control_layout.setSpacing(UIConstants.CONTROL_SPACING)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setMinimum(0)
        self.slider.setMaximum(UIConstants.VOLUME_PERCENTAGE_FACTOR)
        self.slider.setValue(int(self.session['volume'] * UIConstants.VOLUME_PERCENTAGE_FACTOR))
        self.slider.setStyleSheet(StyleSheets.get_app_slider_stylesheet())
        self.slider.valueChanged.connect(self.on_slider_changed)
        self.slider.setMinimumWidth(UIConstants.MIN_SLIDER_WIDTH)
        self.slider.setContentsMargins(UIConstants.STRETCH_FACTOR_NONE, UIConstants.STRETCH_FACTOR_NONE, 
                                       UIConstants.STRETCH_FACTOR_NONE, UIConstants.STRETCH_FACTOR_NONE)
        
        self.volume_text = QLineEdit()
        self.volume_text.setFocusPolicy(Qt.NoFocus)
        self.volume_text.setFixedWidth(UIConstants.VOLUME_TEXT_WIDTH)
        self.volume_text.setMinimumWidth(UIConstants.VOLUME_TEXT_WIDTH)
        self.volume_text.setText(str(int(self.session['volume'] * UIConstants.VOLUME_PERCENTAGE_FACTOR)))
        self.volume_text.setStyleSheet(StyleSheets.get_volume_text_stylesheet())
        self.volume_text.setReadOnly(False)
        self.volume_text.returnPressed.connect(self.on_volume_text_changed)
        self.volume_text.editingFinished.connect(self.on_volume_text_changed)
        
        is_muted = self.session.get('muted', False)
        self.mute_button = QPushButton("🔇" if is_muted else "🔊")
        self.mute_button.setFocusPolicy(Qt.NoFocus)
        self.mute_button.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.mute_button.setMinimumSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.mute_button.setStyleSheet(StyleSheets.get_mute_button_stylesheet(is_master=False))
        self.mute_button.clicked.connect(self.on_mute_clicked)
        
        control_layout.addWidget(self.slider, UIConstants.STRETCH_FACTOR_STANDARD)
        control_layout.addWidget(self.volume_text, UIConstants.STRETCH_FACTOR_NONE)
        control_layout.addWidget(self.mute_button, UIConstants.STRETCH_FACTOR_NONE)
        layout.addLayout(control_layout)
    
    def on_slider_changed(self, value: int) -> None:
        self.handle_volume_slider_change(
            value,
            lambda vol: self.audio_controller.set_application_volume(self.session['pids'], vol / UIConstants.VOLUME_PERCENTAGE_FACTOR)
        )
    
    def on_mute_clicked(self) -> None:
        self.handle_mute_toggle(
            lambda: self.audio_controller.get_application_mute(self.session['pids']),
            lambda mute: self.audio_controller.set_application_mute(self.session['pids'], mute)
        )
    
    def on_volume_text_changed(self) -> None:
        self.handle_volume_text_change()
    
    def _get_frame_bg_color(self) -> str:
        """Return the background color for app controls."""
        return Colors.APP_CONTROL_BG
