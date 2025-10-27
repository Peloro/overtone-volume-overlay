"""
Settings Dialog for configuring the application
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QDoubleSpinBox, QLineEdit,
                             QGroupBox, QFormLayout, QCheckBox, QTabWidget, QTextBrowser)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices
from config.constants import UIConstants, AppInfo


class SettingsDialog(QDialog):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()
    
    def init_ui(self):
        """Initialize the settings dialog UI"""
        self.setWindowTitle("Settings")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        tab_widget.addTab(settings_tab, "Settings")
        
        # About tab
        about_tab = self.create_about_tab()
        tab_widget.addTab(about_tab, "About")
        
        layout.addWidget(tab_widget)
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.apply_styles()
    
    def create_settings_tab(self):
        """Create the settings tab content"""
        settings_widget = QVBoxLayout()
        
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
        
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout()
        
        self.confirm_quit_checkbox = QCheckBox("Ask for confirmation when quitting")
        self.confirm_quit_checkbox.setChecked(self.app.settings_manager.confirm_on_quit)
        self.confirm_quit_checkbox.setStyleSheet("QCheckBox { color: white; }")
        
        behavior_layout.addRow(self.confirm_quit_checkbox)
        behavior_group.setLayout(behavior_layout)
        
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
        
        settings_widget.addWidget(size_group)
        settings_widget.addWidget(appearance_group)
        settings_widget.addWidget(behavior_group)
        settings_widget.addWidget(hotkey_group)
        settings_widget.addStretch()
        
        from PyQt5.QtWidgets import QWidget
        container = QWidget()
        container.setLayout(settings_widget)
        return container
    
    def create_about_tab(self):
        """Create the about tab content"""
        about_widget = QVBoxLayout()
        
        # App name and version
        title_label = QLabel(f"<h2>{AppInfo.APP_NAME}</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; margin: 10px;")
        
        version_label = QLabel(f"<p style='font-size: 12px; color: #aaa;'>Version {AppInfo.VERSION}</p>")
        version_label.setAlignment(Qt.AlignCenter)
        
        # Description
        description = QTextBrowser()
        description.setOpenExternalLinks(True)
        description.setMaximumHeight(350)
        description.setHtml(f"""
            <div style='color: white; font-family: Arial; font-size: 12px;'>
                <p><b>Description:</b></p>
                <p>{AppInfo.DESCRIPTION}</p>
                
                <p><b>Features:</b></p>
                <ul>
                    <li>Per-Application Volume Control</li>
                    <li>System Volume Control</li>
                    <li>Always-on-Top Overlay</li>
                    <li>Global Hotkeys</li>
                    <li>Smart Pagination</li>
                    <li>System Tray Integration</li>
                    <li>Modern Dark UI</li>
                </ul>
                
                <p><b>Author:</b> {AppInfo.AUTHOR}</p>
                <p><b>GitHub:</b> <a href="{AppInfo.GITHUB_URL}" style="color: #42a5f5;">{AppInfo.GITHUB_URL}</a></p>
                <p><b>Repository:</b> <a href="{AppInfo.REPO_URL}" style="color: #42a5f5;">{AppInfo.REPO_URL}</a></p>
                
                <p style='margin-top: 15px; color: #aaa; font-size: 11px;'><b>License:</b> {AppInfo.LICENSE}</p>
                <p style='color: #aaa; font-size: 11px;'>© {AppInfo.YEAR} {AppInfo.AUTHOR}</p>
            </div>
        """)
        description.setStyleSheet("""
            QTextBrowser {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        about_widget.addWidget(title_label)
        about_widget.addWidget(version_label)
        about_widget.addWidget(description)
        about_widget.addStretch()
        
        from PyQt5.QtWidgets import QWidget
        container = QWidget()
        container.setLayout(about_widget)
        return container
    
    def apply_styles(self):
        """Apply stylesheets to the dialog"""
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
            QTabWidget::pane {
                border: 1px solid #555;
                border-radius: 5px;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #424242;
                color: white;
                border: 1px solid #555;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #1e88e5;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #555;
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
            "hotkey_quit": self.hotkey_quit_edit.text(),
            "confirm_on_quit": self.confirm_quit_checkbox.isChecked()
        })
        
        self.app.setup_hotkeys()
        self.close()
