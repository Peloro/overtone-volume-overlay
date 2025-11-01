"""
Settings Dialog for configuring the application
"""
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QDoubleSpinBox, QLineEdit,
                             QGroupBox, QFormLayout, QCheckBox, QTabWidget, QWidget, QColorDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from config import UIConstants, AppInfo


class SettingsDialog(QDialog):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.has_unsaved_changes = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize the settings dialog UI"""
        from utils import set_window_icon
        self.setWindowTitle("Settings")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(450)
        set_window_icon(self)
        
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        tab_widget.addTab(settings_tab, "Settings")
        
        # Colors tab
        colors_tab = self.create_colors_tab()
        tab_widget.addTab(colors_tab, "Colors")
        
        # Profiles tab
        profiles_tab = self.create_profiles_tab()
        tab_widget.addTab(profiles_tab, "Profiles")
        
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
    
    def create_colors_tab(self):
        """Create the colors customization tab content"""
        colors_widget = QVBoxLayout()
        
        # Background colors group
        bg_group = QGroupBox("Background Colors")
        bg_layout = QFormLayout()
        
        # Title bar background
        self.color_title_bar_btn = self._create_color_button(
            self.app.settings_manager.color_title_bar_bg,
            lambda: self._pick_color("color_title_bar_bg", self.color_title_bar_btn, "Title Bar Background")
        )
        bg_layout.addRow("Title Bar:", self.color_title_bar_btn)
        
        # Master control frame background
        self.color_master_frame_btn = self._create_color_button(
            self.app.settings_manager.color_master_frame_bg,
            lambda: self._pick_color("color_master_frame_bg", self.color_master_frame_btn, "Master Control Background")
        )
        bg_layout.addRow("Master Control:", self.color_master_frame_btn)
        
        # Container background
        self.color_container_btn = self._create_color_button(
            self.app.settings_manager.color_container_bg,
            lambda: self._pick_color("color_container_bg", self.color_container_btn, "Container Background")
        )
        bg_layout.addRow("Container:", self.color_container_btn)
        
        # App control background
        self.color_app_control_btn = self._create_color_button(
            self.app.settings_manager.color_app_control_bg,
            lambda: self._pick_color("color_app_control_bg", self.color_app_control_btn, "App Control Background")
        )
        bg_layout.addRow("App Control:", self.color_app_control_btn)
        
        bg_group.setLayout(bg_layout)
        
        # Slider colors group
        slider_group = QGroupBox("Slider Colors")
        slider_layout = QFormLayout()
        
        # Master slider handle
        self.color_master_slider_btn = self._create_color_button(
            self.app.settings_manager.color_master_slider_handle,
            lambda: self._pick_color("color_master_slider_handle", self.color_master_slider_btn, "Master Slider Handle")
        )
        slider_layout.addRow("Master Slider:", self.color_master_slider_btn)
        
        # App slider handle
        self.color_app_slider_btn = self._create_color_button(
            self.app.settings_manager.color_app_slider_handle,
            lambda: self._pick_color("color_app_slider_handle", self.color_app_slider_btn, "App Slider Handle")
        )
        slider_layout.addRow("App Slider:", self.color_app_slider_btn)
        
        slider_group.setLayout(slider_layout)
        
        # Button colors group
        button_group = QGroupBox("Button Colors")
        button_layout = QFormLayout()
        
        # Primary button
        self.color_primary_button_btn = self._create_color_button(
            self.app.settings_manager.color_primary_button_bg,
            lambda: self._pick_color("color_primary_button_bg", self.color_primary_button_btn, "Primary Button")
        )
        button_layout.addRow("Primary Button:", self.color_primary_button_btn)
        
        # Close button
        self.color_close_button_btn = self._create_color_button(
            self.app.settings_manager.color_close_button_bg,
            lambda: self._pick_color("color_close_button_bg", self.color_close_button_btn, "Close Button")
        )
        button_layout.addRow("Close Button:", self.color_close_button_btn)
        
        button_group.setLayout(button_layout)
        
        # Text colors group
        text_group = QGroupBox("Text Colors")
        text_layout = QFormLayout()
        
        # Text color
        self.color_text_btn = self._create_color_button(
            self.app.settings_manager.color_text_white,
            lambda: self._pick_color("color_text_white", self.color_text_btn, "Text Color")
        )
        text_layout.addRow("Text Color:", self.color_text_btn)
        
        text_group.setLayout(text_layout)
        
        # Reset button
        reset_colors_layout = QHBoxLayout()
        reset_colors_btn = QPushButton("Reset Colors to Default")
        reset_colors_btn.clicked.connect(self.on_reset_colors)
        reset_colors_layout.addStretch()
        reset_colors_layout.addWidget(reset_colors_btn)
        reset_colors_layout.addStretch()
        
        colors_widget.addWidget(bg_group)
        colors_widget.addWidget(slider_group)
        colors_widget.addWidget(button_group)
        colors_widget.addWidget(text_group)
        colors_widget.addLayout(reset_colors_layout)
        colors_widget.addStretch()
        
        container = QWidget()
        container.setLayout(colors_widget)
        return container
    
    def _create_color_button(self, color: str, callback):
        """Create a color picker button"""
        button = QPushButton()
        button.setMinimumHeight(30)
        button.setMinimumWidth(90)
        button.setStyleSheet("font-size: 8px;")
        button.clicked.connect(callback)
        self._update_color_button(button, color)
        return button
    
    def _update_color_button(self, button: QPushButton, color: str):
        """Update button appearance to show the color"""
        try:
            if color.startswith("rgba"):
                color_str = color.replace("rgba(", "").replace(")", "").replace("{alpha}", "255")
                r, g, b, a = [int(x.strip()) for x in color_str.split(",")][:4]
                a = a if len(color_str.split(",")) > 3 else 255
                display_text = f"({r}, {g}, {b}, {a})"
                bg_css = f"rgba({r}, {g}, {b}, {a})"
            else:
                q = QColor(color)
                r, g, b, a = q.red(), q.green(), q.blue(), q.alpha()
                display_text = f"({r}, {g}, {b}, {a})"
                bg_css = q.name()

            button.setStyleSheet(f"QPushButton {{ background-color: {bg_css}; color: white; border: 2px solid #666; border-radius: 3px; }}")
            button.setText(display_text)
        except Exception:
            button.setStyleSheet(f"QPushButton {{ background-color: {color}; color: white; border: 2px solid #666; border-radius: 3px; }}")
            button.setText(str(color))
    
    def _pick_color(self, setting_key: str, button: QPushButton, title: str):
        """Open color picker and update setting"""
        current_color = self.app.settings_manager.get(setting_key)
        
        # Parse current color
        if current_color.startswith("rgba"):
            color_str = current_color.replace("rgba(", "").replace(")", "").replace("{alpha}", "255")
            parts = [int(x.strip()) for x in color_str.split(",")]
            initial_color = QColor(parts[0], parts[1], parts[2])
        else:
            initial_color = QColor(current_color)
        
        # Open color dialog
        color = QColorDialog.getColor(initial_color, self, f"Choose {title}")
        
        if color.isValid():
            self.mark_as_changed()
            # Determine format based on current setting
            if current_color.startswith("rgba"):
                new_color = f"rgba({color.red()}, {color.green()}, {color.blue()}, {{alpha}})" if "{alpha}" in current_color else f"rgba({color.red()}, {color.green()}, {color.blue()}, 255)"
            else:
                new_color = color.name()
            
            # Update setting and button
            self.app.settings_manager.set(setting_key, new_color)
            self._update_color_button(button, new_color)
            self.app.settings_manager.save_settings(debounce=False)
            
            # Refresh the overlay to apply new colors
            self.refresh_overlay_colors()
    
    def on_reset_colors(self):
        """Reset all colors to default values"""
        defaults = {
            "color_main_background": "rgba(30, 30, 30, {alpha})",
            "color_title_bar_bg": "rgba(43, 43, 43, 255)",
            "color_master_frame_bg": "rgba(30, 58, 95, 255)",
            "color_container_bg": "rgba(43, 43, 43, 255)",
            "color_app_control_bg": "rgba(50, 50, 50, 200)",
            "color_master_slider_handle": "#4caf50",
            "color_app_slider_handle": "#1e88e5",
            "color_primary_button_bg": "#1e88e5",
            "color_close_button_bg": "#d32f2f",
            "color_text_white": "white",
        }
        
        self.app.settings_manager.update(defaults)
        
        # Update all color buttons using mapping
        button_mapping = [
            (self.color_title_bar_btn, "color_title_bar_bg"),
            (self.color_master_frame_btn, "color_master_frame_bg"),
            (self.color_container_btn, "color_container_bg"),
            (self.color_app_control_btn, "color_app_control_bg"),
            (self.color_master_slider_btn, "color_master_slider_handle"),
            (self.color_app_slider_btn, "color_app_slider_handle"),
            (self.color_primary_button_btn, "color_primary_button_bg"),
            (self.color_close_button_btn, "color_close_button_bg"),
            (self.color_text_btn, "color_text_white"),
        ]
        
        for button, key in button_mapping:
            self._update_color_button(button, defaults[key])
        
        # Refresh the overlay to apply new colors
        self.refresh_overlay_colors()
    
    def refresh_overlay_colors(self):
        """Refresh overlay to apply new colors"""
        if hasattr(self.app, 'overlay'):
            # Force re-apply styles by refreshing the entire overlay
            self.app.overlay.apply_styles()
            if hasattr(self.app.overlay, 'master_control') and self.app.overlay.master_control:
                self.app.overlay.master_control.apply_styles()
            # Refresh all app controls
            if hasattr(self.app.overlay, 'refresh_applications'):
                self.app.overlay.refresh_applications()
    
    def create_profiles_tab(self):
        """Create the profiles management tab content"""
        from PyQt5.QtWidgets import QListWidget, QMessageBox, QInputDialog
        
        profiles_widget = QVBoxLayout()
        
        # Active profile display
        active_profile_group = QGroupBox("Active Profile")
        active_profile_layout = QVBoxLayout()
        
        self.active_profile_label = QLabel()
        self.active_profile_label.setStyleSheet("color: #42a5f5; font-size: 14px; padding: 5px;")
        active_profile_layout.addWidget(self.active_profile_label)
        
        active_profile_group.setLayout(active_profile_layout)
        profiles_widget.addWidget(active_profile_group)
        
        # Profile list group
        profile_list_group = QGroupBox("Available Profiles")
        profile_list_layout = QVBoxLayout()
        
        self.profile_list = QListWidget()
        self.profile_list.setStyleSheet("""
            QListWidget {
                background-color: #424242;
                border: 1px solid #666;
                border-radius: 3px;
                color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #1e88e5;
            }
            QListWidget::item:hover {
                background-color: #555;
            }
        """)
        # Connect double-click signal to switch profile
        self.profile_list.itemDoubleClicked.connect(self.on_profile_double_clicked)
        profile_list_layout.addWidget(self.profile_list)
        profile_list_group.setLayout(profile_list_layout)
        profiles_widget.addWidget(profile_list_group)
        
        # Profile actions - grouped by color
        actions_layout = QHBoxLayout()
        
        # Button style constants
        primary_style = """
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #42a5f5;
            }
        """
        danger_style = """
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
        """
        
        # Create buttons with styles
        for text, callback, style in [
            ("Switch to Selected", self.on_switch_profile, primary_style),
            ("Save to Active Profile", self.on_save_to_active_profile, primary_style),
            ("New Profile", self.on_new_profile, None),
            ("Rename", self.on_rename_profile, None),
            ("Delete", self.on_delete_profile, danger_style),
        ]:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            if style:
                btn.setStyleSheet(style)
            actions_layout.addWidget(btn)
        
        profiles_widget.addLayout(actions_layout)
        
        # Populate the profile list
        self.refresh_profile_list()
        
        container = QWidget()
        container.setLayout(profiles_widget)
        return container
    
    def refresh_profile_list(self):
        """Refresh the list of profiles"""
        self.profile_list.clear()
        active_profile = self.app.settings_manager.get_active_profile_name()
        
        for profile_name in self.app.settings_manager.get_profile_names():
            item_text = profile_name
            if profile_name == active_profile:
                item_text += " (Active)"
            if self.app.settings_manager.is_default_profile(profile_name):
                item_text += " [Default]"
            self.profile_list.addItem(item_text)
        
        # Update active profile label with asterisk if there are unsaved changes
        asterisk = " *" if self.has_unsaved_changes else ""
        self.active_profile_label.setText(f"{active_profile}{asterisk}")
    
    def mark_as_changed(self):
        """Mark that the profile has unsaved changes"""
        if not self.has_unsaved_changes:
            self.has_unsaved_changes = True
            self.refresh_profile_list()
    
    def on_new_profile(self):
        """Create a new profile"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        name, ok = QInputDialog.getText(
            self, "New Profile", "Enter profile name:",
            text=""
        )
        
        if ok and name:
            name = name.strip()
            if self.app.settings_manager.create_profile(name, base_on_current=True):
                self.app.settings_manager.switch_profile(name)
                self.refresh_profile_list()
                self.refresh_overlay_after_profile_switch()
    
    def on_rename_profile(self):
        """Rename the selected profile"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a profile to rename.")
            return
        
        # Extract the actual profile name (remove markers like "(Active)" and "[Default]")
        item_text = selected_items[0].text()
        old_name = item_text.split(" (")[0].split(" [")[0]
        
        if self.app.settings_manager.is_default_profile(old_name):
            QMessageBox.warning(
                self, "Cannot Rename",
                "The default profile cannot be renamed."
            )
            return
        
        new_name, ok = QInputDialog.getText(
            self, "Rename Profile", "Enter new profile name:",
            text=old_name
        )
        
        if ok and new_name:
            new_name = new_name.strip()
            if self.app.settings_manager.rename_profile(old_name, new_name):
                self.refresh_profile_list()
    
    def on_delete_profile(self):
        """Delete the selected profile"""
        from PyQt5.QtWidgets import QMessageBox
        
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a profile to delete.")
            return
        
        # Extract the actual profile name
        item_text = selected_items[0].text()
        profile_name = item_text.split(" (")[0].split(" [")[0]
        
        if self.app.settings_manager.is_default_profile(profile_name):
            QMessageBox.warning(
                self, "Cannot Delete",
                "The default profile cannot be deleted."
            )
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the profile '{profile_name}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.app.settings_manager.delete_profile(profile_name):
                self.refresh_profile_list()
                if profile_name == self.app.settings_manager.get_active_profile_name():
                    self.refresh_overlay_after_profile_switch()
    
    def on_profile_double_clicked(self, item):
        """Handle double-click on a profile item to switch to it"""
        # Extract the actual profile name
        item_text = item.text()
        profile_name = item_text.split(" (")[0].split(" [")[0]
        
        # Switch to the double-clicked profile
        if self.app.settings_manager.switch_profile(profile_name):
            self.has_unsaved_changes = False
            self.refresh_profile_list()
            self.refresh_overlay_after_profile_switch()
    
    def on_switch_profile(self):
        """Switch to the selected profile"""
        from PyQt5.QtWidgets import QMessageBox
        
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a profile to switch to.")
            return
        
        # Extract the actual profile name
        item_text = selected_items[0].text()
        profile_name = item_text.split(" (")[0].split(" [")[0]
        
        # Allow re-selecting the same profile to revert unsaved changes
        if self.app.settings_manager.switch_profile(profile_name):
            self.has_unsaved_changes = False
            self.refresh_profile_list()
            self.refresh_overlay_after_profile_switch()
    
    def on_save_to_active_profile(self):
        """Save current settings to the active profile"""
        from PyQt5.QtWidgets import QMessageBox
        
        active_profile = self.app.settings_manager.get_active_profile_name()
        
        reply = QMessageBox.question(
            self, "Confirm Save",
            f"Save current settings to profile '{active_profile}'?\n\n"
            "This will overwrite the saved settings in this profile.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.app.settings_manager.save_to_profile(active_profile)
            self.has_unsaved_changes = False
            self.refresh_profile_list()
    
    def refresh_overlay_after_profile_switch(self):
        """Refresh the overlay after switching profiles"""
        sm = self.app.settings_manager
        
        # Update all UI elements to reflect the new profile settings
        self.width_spin.setValue(sm.overlay_width)
        self.height_spin.setValue(sm.overlay_height)
        self.opacity_spin.setValue(sm.overlay_opacity)
        self.hotkey_open_edit.setText(sm.hotkey_open)
        self.hotkey_settings_edit.setText(sm.hotkey_settings)
        self.hotkey_quit_edit.setText(sm.hotkey_quit)
        self.confirm_quit_checkbox.setChecked(sm.confirm_on_quit)
        self.show_system_volume_checkbox.setChecked(sm.show_system_volume)
        self.always_show_filter_checkbox.setChecked(sm.always_show_filter)
        
        # Update color buttons using mapping
        button_mapping = [
            (self.color_title_bar_btn, sm.color_title_bar_bg),
            (self.color_master_frame_btn, sm.color_master_frame_bg),
            (self.color_container_btn, sm.color_container_bg),
            (self.color_app_control_btn, sm.color_app_control_bg),
            (self.color_master_slider_btn, sm.color_master_slider_handle),
            (self.color_app_slider_btn, sm.color_app_slider_handle),
            (self.color_primary_button_btn, sm.color_primary_button_bg),
            (self.color_close_button_btn, sm.color_close_button_bg),
            (self.color_text_btn, sm.color_text_white),
        ]
        
        for button, color in button_mapping:
            self._update_color_button(button, color)
        
        # Refresh overlay
        self.app.overlay.resize(self.app.settings_manager.overlay_width, self.app.settings_manager.overlay_height)
        self.app.overlay.update_background_opacity()
        self.app.overlay.update_system_volume_visibility()
        self.app.overlay.update_filter_display_mode()
        self.refresh_overlay_colors()
        
        # Reapply hotkeys
        self.app.setup_hotkeys()
    
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
        self.mark_as_changed()
        self.app.settings_manager.set("overlay_width", value)
        self.app.overlay.resize(value, self.app.settings_manager.overlay_height)
        self.app.settings_manager.save_settings()
    
    def on_height_changed(self, value: int) -> None:
        """Handle height change in real-time"""
        self.mark_as_changed()
        self.app.settings_manager.set("overlay_height", value)
        self.app.overlay.resize(self.app.settings_manager.overlay_width, value)
        self.app.settings_manager.save_settings()
    
    def on_opacity_changed(self, value: float) -> None:
        """Handle opacity change in real-time"""
        self.mark_as_changed()
        self.app.settings_manager.set("overlay_opacity", value)
        self.app.overlay.update_background_opacity()
        self.app.settings_manager.save_settings()
    
    def on_confirm_quit_changed(self, state: int) -> None:
        """Handle confirm quit checkbox change"""
        self.mark_as_changed()
        self.app.settings_manager.set("confirm_on_quit", bool(state))
        self.app.settings_manager.save_settings(debounce=False)
    
    def on_show_system_volume_changed(self, state: int) -> None:
        """Handle show system volume checkbox change"""
        self.mark_as_changed()
        self.app.settings_manager.set("show_system_volume", bool(state))
        self.app.overlay.update_system_volume_visibility()
        self.app.settings_manager.save_settings(debounce=False)
    
    def on_always_show_filter_changed(self, state: int) -> None:
        """Handle always show filter checkbox change"""
        self.mark_as_changed()
        self.app.settings_manager.set("always_show_filter", bool(state))
        self.app.overlay.update_filter_display_mode()
        self.app.settings_manager.save_settings(debounce=False)
    
    def on_hotkey_changed(self) -> None:
        """Handle hotkey change - save and reapply immediately"""
        self.mark_as_changed()
        self.app.settings_manager.update({
            "hotkey_open": self.hotkey_open_edit.text(),
            "hotkey_settings": self.hotkey_settings_edit.text(),
            "hotkey_quit": self.hotkey_quit_edit.text(),
        })
        self.app.setup_hotkeys()
