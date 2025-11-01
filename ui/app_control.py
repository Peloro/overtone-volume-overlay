"""
Individual Application Volume Control Widget
"""
from typing import Dict, Any
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSlider, 
                             QLabel, QPushButton, QLineEdit, QFrame)
from PyQt5.QtCore import Qt

from config import UIConstants, Colors, StyleSheets
from .base_volume_control import BaseVolumeControl


class AppVolumeControl(QFrame, BaseVolumeControl):
    """Widget for controlling volume of a single application"""
    
    def __init__(self, session: Dict[str, Any], audio_controller) -> None:
        QFrame.__init__(self)
        BaseVolumeControl.__init__(self)
        self.session = session
        self.audio_controller = audio_controller
        self.init_volume_state(int(session['volume'] * 100), session.get('muted', False))
        self.init_ui()

    def update_session(self, session: Dict[str, Any]) -> None:
        """Update UI state from a refreshed session without recreating the widget"""
        self.session = session
        new_val = int(session['volume'] * 100)
        new_muted = session.get('muted', False)
        
        if self.slider and self.slider.value() != new_val:
            self.slider.blockSignals(True)
            self.slider.setValue(new_val)
            self.slider.blockSignals(False)
        if self.volume_text and self.volume_text.text() != str(new_val):
            self.volume_text.setText(str(new_val))
        if self.is_muted != new_muted:
            self.is_muted = new_muted
            self.update_mute_icon(new_muted)
    
    def init_ui(self):
        """Initialize the UI for a single app control"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*[UIConstants.FRAME_MARGIN] * 4)
        layout.setSpacing(UIConstants.CONTROL_SPACING)
        self.setStyleSheet(StyleSheets.get_frame_stylesheet(bg_color=Colors.APP_CONTROL_BG))
        
        # Set fixed size to prevent deformation and expansion
        self.setFixedHeight(UIConstants.APP_CONTROL_HEIGHT)
        self.setMinimumWidth(UIConstants.MIN_CONTROL_WIDTH)
        self.setMaximumHeight(UIConstants.APP_CONTROL_HEIGHT)
        
        # Set size policy to prevent expansion
        from PyQt5.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Enable mouse tracking for hover events
        self.setMouseTracking(True)
        
        self.name_label = QLabel(self.session['name'])
        self.name_label.setStyleSheet(StyleSheets.get_label_stylesheet())
        self.name_label.setMinimumWidth(0)  # Allow text to be elided
        self.name_label.setWordWrap(False)  # Prevent wrapping
        self.name_label.setTextFormat(Qt.PlainText)  # Use plain text
        self.name_label.setSizePolicy(self.name_label.sizePolicy().Ignored, self.name_label.sizePolicy().Preferred)
        # Elide text from the middle to keep both start and end visible
        font_metrics = self.name_label.fontMetrics()
        elided_text = font_metrics.elidedText(self.session['name'], Qt.ElideMiddle, 280)
        self.name_label.setText(elided_text)
        self.name_label.setToolTip(self.session['name'])  # Show full name on hover
        layout.addWidget(self.name_label)
        
        control_layout = QHBoxLayout()
        control_layout.setSpacing(UIConstants.CONTROL_SPACING)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(int(self.session['volume'] * 100))
        self.slider.setStyleSheet(StyleSheets.get_app_slider_stylesheet())
        self.slider.valueChanged.connect(self.on_slider_changed)
        self.slider.setMinimumWidth(UIConstants.MIN_SLIDER_WIDTH)
        
        self.volume_text = QLineEdit()
        self.volume_text.setFixedWidth(UIConstants.VOLUME_TEXT_WIDTH)
        self.volume_text.setMinimumWidth(UIConstants.VOLUME_TEXT_WIDTH)
        self.volume_text.setText(str(int(self.session['volume'] * 100)))
        self.volume_text.setStyleSheet(StyleSheets.get_volume_text_stylesheet())
        self.volume_text.setReadOnly(False)
        self.volume_text.returnPressed.connect(self.on_volume_text_changed)
        self.volume_text.editingFinished.connect(self.on_volume_text_changed)
        
        is_muted = self.session.get('muted', False)
        self.mute_button = QPushButton("🔇" if is_muted else "🔊")
        self.mute_button.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.mute_button.setMinimumSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.mute_button.setStyleSheet(StyleSheets.get_mute_button_stylesheet(is_master=False))
        self.mute_button.clicked.connect(self.on_mute_clicked)
        
        control_layout.addWidget(self.slider, 1)  # Give slider stretch factor
        control_layout.addWidget(self.volume_text, 0)
        control_layout.addWidget(self.mute_button, 0)
        layout.addLayout(control_layout)
    
    def on_slider_changed(self, value: int) -> None:
        """Handle slider value change"""
        self.handle_volume_slider_change(
            value,
            lambda vol: self.audio_controller.set_application_volume(self.session['pids'], vol)
        )
    
    def on_mute_clicked(self) -> None:
        """Handle mute button click"""
        self.handle_mute_toggle(
            lambda: self.audio_controller.get_application_mute(self.session['pids']),
            lambda mute: self.audio_controller.set_application_mute(self.session['pids'], mute)
        )
    
    def on_volume_text_changed(self) -> None:
        """Handle volume text box change"""
        self.handle_volume_text_change()
    

    
    def apply_styles(self):
        """Reapply all styles to reflect color changes"""
        # Reapply frame background
        self.setStyleSheet(StyleSheets.get_frame_stylesheet(bg_color=Colors.APP_CONTROL_BG))
        
        # Reapply label style
        if hasattr(self, 'name_label') and self.name_label:
            self.name_label.setStyleSheet(StyleSheets.get_label_stylesheet())
        
        # Reapply slider style
        if self.slider:
            self.slider.setStyleSheet(StyleSheets.get_app_slider_stylesheet())
        
        # Reapply volume text style
        if self.volume_text:
            self.volume_text.setStyleSheet(StyleSheets.get_volume_text_stylesheet())
        
        # Reapply mute button style
        if self.mute_button:
            self.mute_button.setStyleSheet(StyleSheets.get_mute_button_stylesheet(is_master=False))
        
        # Force update
        self.update()
