"""
Settings Dialog for configuring the application
"""
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QDoubleSpinBox, QLineEdit,
                             QGroupBox, QFormLayout, QCheckBox, QTabWidget, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from config import UIConstants, AppInfo


class SettingsDialog(QDialog):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.init_ui()
    
    def init_ui(self):
        """Initialize the settings dialog UI"""
        self.setWindowTitle("Settings")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(450)
        
        # Set window icon (use black version for dark-themed dialog)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon2_black.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
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
        
        # Close button at the bottom (no Save/Cancel needed since all changes apply immediately)
        button_layout = QHBoxLayout()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.apply_styles()
    
    def _create_group_with_form(self, title: str, form_rows: list) -> QGroupBox:
        """Create a group box with a form layout"""
        group = QGroupBox(title)
        layout = QFormLayout()
        for row in form_rows:
            if isinstance(row, tuple):
                layout.addRow(*row)
            else:
                layout.addRow(row)
        group.setLayout(layout)
        return group
    
    def create_settings_tab(self):
        """Create the settings tab content"""
        settings_widget = QVBoxLayout()
        
        # Size group
        self.width_spin = QSpinBox()
        self.width_spin.setRange(UIConstants.MIN_OVERLAY_WIDTH, UIConstants.MAX_OVERLAY_WIDTH)
        self.width_spin.setValue(self.app.settings_manager.overlay_width)
        self.width_spin.valueChanged.connect(self.on_width_changed)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(UIConstants.MIN_OVERLAY_HEIGHT, UIConstants.MAX_OVERLAY_HEIGHT)
        self.height_spin.setValue(self.app.settings_manager.overlay_height)
        self.height_spin.valueChanged.connect(self.on_height_changed)
        
        size_group = self._create_group_with_form("Overlay Size", [
            ("Width:", self.width_spin),
            ("Height:", self.height_spin)
        ])
        
        # Appearance group
        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(UIConstants.MIN_OPACITY, UIConstants.MAX_OPACITY)
        self.opacity_spin.setSingleStep(0.05)
        self.opacity_spin.setDecimals(2)
        self.opacity_spin.setValue(self.app.settings_manager.overlay_opacity)
        self.opacity_spin.valueChanged.connect(self.on_opacity_changed)
        
        appearance_group = self._create_group_with_form("Appearance", [("Opacity:", self.opacity_spin)])
        
        # Behavior group
        self.confirm_quit_checkbox = QCheckBox("Ask for confirmation when quitting")
        self.confirm_quit_checkbox.setChecked(self.app.settings_manager.confirm_on_quit)
        self.confirm_quit_checkbox.setStyleSheet("QCheckBox { color: white; }")
        self.confirm_quit_checkbox.stateChanged.connect(self.on_confirm_quit_changed)
        
        self.show_system_volume_checkbox = QCheckBox("Show system volume control in overlay")
        self.show_system_volume_checkbox.setChecked(self.app.settings_manager.show_system_volume)
        self.show_system_volume_checkbox.setStyleSheet("QCheckBox { color: white; }")
        self.show_system_volume_checkbox.stateChanged.connect(self.on_show_system_volume_changed)
        
        self.always_show_filter_checkbox = QCheckBox("Always show filter textbox (hide toggle button)")
        self.always_show_filter_checkbox.setChecked(self.app.settings_manager.always_show_filter)
        self.always_show_filter_checkbox.setStyleSheet("QCheckBox { color: white; }")
        self.always_show_filter_checkbox.stateChanged.connect(self.on_always_show_filter_changed)
        
        behavior_group = self._create_group_with_form("Behavior", [
            self.confirm_quit_checkbox,
            self.show_system_volume_checkbox,
            self.always_show_filter_checkbox
        ])
        
        # Hotkey group
        self.hotkey_open_edit = QLineEdit(self.app.settings_manager.hotkey_open)
        self.hotkey_settings_edit = QLineEdit(self.app.settings_manager.hotkey_settings)
        self.hotkey_quit_edit = QLineEdit(self.app.settings_manager.hotkey_quit)
        
        for edit in (self.hotkey_open_edit, self.hotkey_settings_edit, self.hotkey_quit_edit):
            edit.textChanged.connect(self.on_hotkey_changed)
        
        hotkey_info = QLabel("Format: ctrl+shift+key, alt+key, etc.")
        hotkey_info.setStyleSheet("color: gray; font-size: 10px;")
        
        hotkey_warning = QLabel("Note: Changes apply immediately")
        hotkey_warning.setStyleSheet("color: #42a5f5; font-size: 10px; font-style: italic;")
        
        hotkey_group = self._create_group_with_form("Hotkeys", [
            ("Open Overlay:", self.hotkey_open_edit),
            ("Open Settings:", self.hotkey_settings_edit),
            ("Quit Application:", self.hotkey_quit_edit),
            hotkey_info,
            hotkey_warning
        ])
        
        for group in (size_group, appearance_group, behavior_group, hotkey_group):
            settings_widget.addWidget(group)
        settings_widget.addStretch()
        
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
        description_label = QLabel(f"""
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
        description_label.setWordWrap(True)
        description_label.setOpenExternalLinks(True)
        description_label.setTextFormat(Qt.RichText)
        description_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        description_label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 10px;
            }
        """)
        
        about_widget.addWidget(title_label)
        about_widget.addWidget(version_label)
        about_widget.addWidget(description_label)
        about_widget.addStretch()
        
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
    
    def on_width_changed(self, value: int) -> None:
        """Handle width change in real-time"""
        self.app.settings_manager.set("overlay_width", value)
        self.app.overlay.resize(value, self.app.settings_manager.overlay_height)
        self.app.settings_manager.save_settings()  # Debounced automatically
    
    def on_height_changed(self, value: int) -> None:
        """Handle height change in real-time"""
        self.app.settings_manager.set("overlay_height", value)
        self.app.overlay.resize(self.app.settings_manager.overlay_width, value)
        self.app.settings_manager.save_settings()  # Debounced automatically
    
    def on_opacity_changed(self, value: float) -> None:
        """Handle opacity change in real-time"""
        self.app.settings_manager.set("overlay_opacity", value)
        self.app.overlay.update_background_opacity()
        self.app.settings_manager.save_settings()  # Debounced automatically
    
    def on_confirm_quit_changed(self, state: int) -> None:
        """Handle confirm quit checkbox change"""
        self.app.settings_manager.set("confirm_on_quit", bool(state))
        self.app.settings_manager.save_settings(debounce=False)  # Immediate for checkbox
    
    def on_show_system_volume_changed(self, state: int) -> None:
        """Handle show system volume checkbox change"""
        self.app.settings_manager.set("show_system_volume", bool(state))
        self.app.overlay.update_system_volume_visibility()
        self.app.settings_manager.save_settings(debounce=False)  # Immediate for checkbox
    
    def on_always_show_filter_changed(self, state: int) -> None:
        """Handle always show filter checkbox change"""
        self.app.settings_manager.set("always_show_filter", bool(state))
        self.app.overlay.update_filter_display_mode()
        self.app.settings_manager.save_settings(debounce=False)  # Immediate for checkbox
    
    def on_hotkey_changed(self) -> None:
        """Handle hotkey change - save and reapply immediately"""
        self.app.settings_manager.update({
            "hotkey_open": self.hotkey_open_edit.text(),
            "hotkey_settings": self.hotkey_settings_edit.text(),
            "hotkey_quit": self.hotkey_quit_edit.text(),
        })
        self.app.setup_hotkeys()
