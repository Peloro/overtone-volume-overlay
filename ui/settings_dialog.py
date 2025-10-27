"""
Settings Dialog for configuring the application
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QDoubleSpinBox, QLineEdit,
                             QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from config.constants import UIConstants


class SettingsDialog(QDialog):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()
    
    def init_ui(self):
        """Initialize the settings dialog UI"""
        self.setWindowTitle("Settings")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        size_group = QGroupBox("Overlay Size")
        size_layout = QFormLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setMinimum(UIConstants.MIN_OVERLAY_WIDTH)
        self.width_spin.setMaximum(UIConstants.MAX_OVERLAY_WIDTH)
        self.width_spin.setValue(self.app.settings_manager.overlay_width)
        self.width_spin.valueChanged.connect(self.on_width_changed)
        
        self.height_spin = QSpinBox()
        self.height_spin.setMinimum(UIConstants.MIN_OVERLAY_HEIGHT)
        self.height_spin.setMaximum(UIConstants.MAX_OVERLAY_HEIGHT)
        self.height_spin.setValue(self.app.settings_manager.overlay_height)
        self.height_spin.valueChanged.connect(self.on_height_changed)
        
        size_layout.addRow("Width:", self.width_spin)
        size_layout.addRow("Height:", self.height_spin)
        size_group.setLayout(size_layout)
        
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()
        
        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setMinimum(UIConstants.MIN_OPACITY)
        self.opacity_spin.setMaximum(UIConstants.MAX_OPACITY)
        self.opacity_spin.setSingleStep(0.1)
        self.opacity_spin.setValue(self.app.settings_manager.overlay_opacity)
        self.opacity_spin.setDecimals(1)
        self.opacity_spin.valueChanged.connect(self.on_opacity_changed)
        
        appearance_layout.addRow("Opacity:", self.opacity_spin)
        appearance_group.setLayout(appearance_layout)
        
        hotkey_group = QGroupBox("Hotkeys")
        hotkey_layout = QFormLayout()
        
        self.hotkey_open_edit = QLineEdit(self.app.settings_manager.hotkey_open)
        self.hotkey_settings_edit = QLineEdit(self.app.settings_manager.hotkey_settings)
        self.hotkey_quit_edit = QLineEdit(self.app.settings_manager.hotkey_quit)
        
        hotkey_layout.addRow("Open Overlay:", self.hotkey_open_edit)
        hotkey_layout.addRow("Open Settings:", self.hotkey_settings_edit)
        hotkey_layout.addRow("Quit Application:", self.hotkey_quit_edit)
        
        hotkey_info = QLabel("Format: ctrl+shift+key, alt+key, etc.")
        hotkey_info.setStyleSheet("color: gray; font-size: 10px;")
        hotkey_layout.addRow(hotkey_info)
        
        hotkey_group.setLayout(hotkey_layout)
        
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(size_group)
        layout.addWidget(appearance_group)
        layout.addWidget(hotkey_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
            QGroupBox {
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: white;
            }
            QLabel {
                color: white;
            }
            QSpinBox, QDoubleSpinBox, QLineEdit {
                background-color: #424242;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 5px;
                color: white;
            }
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #42a5f5;
            }
        """)
    
    def on_width_changed(self, value):
        """Handle width change in real-time"""
        self.app.settings_manager.set("overlay_width", value)
        self.app.overlay.resize(value, self.app.settings_manager.overlay_height)
        self.app.settings_manager.save_settings()
    
    def on_height_changed(self, value):
        """Handle height change in real-time"""
        self.app.settings_manager.set("overlay_height", value)
        self.app.overlay.resize(self.app.settings_manager.overlay_width, value)
        self.app.settings_manager.save_settings()
    
    def on_opacity_changed(self, value):
        """Handle opacity change in real-time"""
        self.app.settings_manager.set("overlay_opacity", value)
        self.app.overlay.update_background_opacity()
        self.app.settings_manager.save_settings()
    
    def save_settings(self):
        """Save the hotkey settings (size and opacity are already saved in real-time)"""
        self.app.settings_manager.update({
            "hotkey_open": self.hotkey_open_edit.text(),
            "hotkey_settings": self.hotkey_settings_edit.text(),
            "hotkey_quit": self.hotkey_quit_edit.text()
        })
        
        self.app.setup_hotkeys()
        self.close()
