"""
Settings Dialog for configuring the application
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QFormLayout, QCheckBox, QTabWidget, QWidget, QColorDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from config import UIConstants, AppInfo, Hotkeys
from .hotkey_recorder import HotkeyRecorderButton


class SettingsDialog(QDialog):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.has_unsaved_settings_changes = False
        self.has_unsaved_color_changes = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize the settings dialog UI"""
        from utils import set_window_icon
        self.setWindowTitle("Settings")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(UIConstants.SETTINGS_MIN_WIDTH)
        set_window_icon(self)
        
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        tab_widget.addTab(settings_tab, "Settings")
        
        # Settings Profiles tab (next to Settings)
        settings_profiles_tab = self.create_settings_profiles_tab()
        tab_widget.addTab(settings_profiles_tab, "Settings Profiles")
        
        # Colors tab
        colors_tab = self.create_colors_tab()
        tab_widget.addTab(colors_tab, "Colors")
        
        # Color Profiles tab (next to Colors)
        color_profiles_tab = self.create_color_profiles_tab()
        tab_widget.addTab(color_profiles_tab, "Color Profiles")
        
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
        
        # Resize mode button
        self.resize_mode_btn = QPushButton("Enter Resize Mode")
        self.resize_mode_btn.setToolTip("Opens the overlay in a resizable window mode.\nDrag the edges to resize, then click 'Done' to save.")
        self.resize_mode_btn.clicked.connect(self.enter_resize_mode)
        
        size_group = self._create_group_with_form("Overlay Size", [
            ("Width:", self.width_spin),
            ("Height:", self.height_spin),
            self.resize_mode_btn
        ])
        
        # Appearance group
        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(UIConstants.MIN_OPACITY, UIConstants.MAX_OPACITY)
        self.opacity_spin.setSingleStep(UIConstants.OPACITY_STEP)
        self.opacity_spin.setDecimals(UIConstants.OPACITY_DECIMAL_PLACES)
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
        self.hotkey_open_btn = HotkeyRecorderButton(self.app.settings_manager.hotkey_open)
        self.hotkey_settings_btn = HotkeyRecorderButton(self.app.settings_manager.hotkey_settings)
        self.hotkey_quit_btn = HotkeyRecorderButton(self.app.settings_manager.hotkey_quit)
        
        self.hotkey_open_btn.hotkey_changed.connect(lambda hk: self.on_hotkey_recorded("hotkey_open", hk))
        self.hotkey_settings_btn.hotkey_changed.connect(lambda hk: self.on_hotkey_recorded("hotkey_settings", hk))
        self.hotkey_quit_btn.hotkey_changed.connect(lambda hk: self.on_hotkey_recorded("hotkey_quit", hk))
        
        hotkey_group = self._create_group_with_form("Hotkeys", [
            ("Open Overlay:", self.hotkey_open_btn),
            ("Open Settings:", self.hotkey_settings_btn),
            ("Quit Application:", self.hotkey_quit_btn),
        ])
        
        for group in (size_group, appearance_group, behavior_group, hotkey_group):
            settings_widget.addWidget(group)
        
        # Action buttons layout
        settings_actions_layout = QHBoxLayout()
        
        # Save to Profile button
        self.save_settings_btn = QPushButton("Save to Profile")
        self.save_settings_btn.setToolTip("Save current settings to the active settings profile")
        self.save_settings_btn.clicked.connect(self.on_save_settings_to_profile)
        
        # Reset Settings to Default button
        reset_settings_btn = QPushButton("Reset Settings to Default")
        reset_settings_btn.clicked.connect(self.on_reset_settings)
        
        settings_actions_layout.addStretch()
        settings_actions_layout.addWidget(self.save_settings_btn)
        settings_actions_layout.addWidget(reset_settings_btn)
        settings_actions_layout.addStretch()
        
        settings_widget.addLayout(settings_actions_layout)
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
        
        # Action buttons layout
        colors_actions_layout = QHBoxLayout()
        
        # Save to Profile button
        self.save_colors_btn = QPushButton("Save to Profile")
        self.save_colors_btn.setToolTip("Save current colors to the active color profile")
        self.save_colors_btn.clicked.connect(self.on_save_colors_to_profile)
        
        # Reset button
        reset_colors_btn = QPushButton("Reset Colors to Default")
        reset_colors_btn.clicked.connect(self.on_reset_colors)
        
        colors_actions_layout.addStretch()
        colors_actions_layout.addWidget(self.save_colors_btn)
        colors_actions_layout.addWidget(reset_colors_btn)
        colors_actions_layout.addStretch()
        
        colors_widget.addWidget(bg_group)
        colors_widget.addWidget(slider_group)
        colors_widget.addWidget(button_group)
        colors_widget.addWidget(text_group)
        colors_widget.addLayout(colors_actions_layout)
        colors_widget.addStretch()
        
        container = QWidget()
        container.setLayout(colors_widget)
        return container
    
    def _create_color_button(self, color: str, callback):
        """Create a color picker button"""
        button = QPushButton()
        button.setMinimumHeight(UIConstants.COLOR_BUTTON_MIN_HEIGHT)
        button.setMinimumWidth(UIConstants.COLOR_BUTTON_MIN_WIDTH)
        button.setStyleSheet(f"font-size: {UIConstants.COLOR_BUTTON_FONT_SIZE}px;")
        button.clicked.connect(callback)
        self._update_color_button(button, color)
        return button
    
    def _update_color_button(self, button: QPushButton, color: str):
        """Update button appearance to show the color"""
        try:
            if color.startswith("rgba"):
                color_str = color.replace("rgba(", "").replace(")", "").replace("{alpha}", str(UIConstants.ALPHA_CHANNEL_MAX))
                r, g, b, a = [int(x.strip()) for x in color_str.split(",")][:UIConstants.RGBA_COMPONENT_COUNT]
                a = a if len(color_str.split(",")) > UIConstants.RGBA_COMPONENT_COUNT - 1 else UIConstants.ALPHA_CHANNEL_MAX
                display_text = f"({r}, {g}, {b}, {a})"
                bg_css = f"rgba({r}, {g}, {b}, {a})"
            else:
                q = QColor(color)
                r, g, b, a = q.red(), q.green(), q.blue(), q.alpha()
                display_text = f"({r}, {g}, {b}, {a})"
                bg_css = q.name()

            button.setStyleSheet(f"QPushButton {{ background-color: {bg_css}; color: white; border: {UIConstants.THICK_BORDER_WIDTH}px solid #666; border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px; }}")
            button.setText(display_text)
        except Exception:
            button.setStyleSheet(f"QPushButton {{ background-color: {color}; color: white; border: {UIConstants.THICK_BORDER_WIDTH}px solid #666; border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px; }}")
            button.setText(str(color))
    
    def _pick_color(self, setting_key: str, button: QPushButton, title: str):
        """Open color picker and update setting"""
        current_color = self.app.settings_manager.get(setting_key)
        
        # Parse current color
        if current_color.startswith("rgba"):
            color_str = current_color.replace("rgba(", "").replace(")", "").replace("{alpha}", str(UIConstants.ALPHA_CHANNEL_MAX))
            parts = [int(x.strip()) for x in color_str.split(",")]
            initial_color = QColor(parts[0], parts[1], parts[2])
        else:
            initial_color = QColor(current_color)
        
        # Open color dialog
        color = QColorDialog.getColor(initial_color, self, f"Choose {title}")
        
        if color.isValid():
            self.mark_colors_as_changed()
            # Determine format based on current setting
            if current_color.startswith("rgba"):
                new_color = f"rgba({color.red()}, {color.green()}, {color.blue()}, {{alpha}})" if "{alpha}" in current_color else f"rgba({color.red()}, {color.green()}, {color.blue()}, {UIConstants.ALPHA_CHANNEL_MAX})"
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
    
    def on_reset_settings(self):
        """Reset all settings to default values"""
        defaults = {
            "overlay_width": UIConstants.DEFAULT_OVERLAY_WIDTH,
            "overlay_height": UIConstants.DEFAULT_OVERLAY_HEIGHT,
            "overlay_opacity": UIConstants.DEFAULT_OPACITY,
            "hotkey_open": Hotkeys.DEFAULT_HOTKEY_OPEN,
            "hotkey_settings": Hotkeys.DEFAULT_HOTKEY_SETTINGS,
            "hotkey_quit": Hotkeys.DEFAULT_HOTKEY_QUIT,
            "confirm_on_quit": True,
            "show_system_volume": True,
            "always_show_filter": False,
        }
        
        self.app.settings_manager.update(defaults)
        
        # Update all UI elements
        self.width_spin.setValue(defaults["overlay_width"])
        self.height_spin.setValue(defaults["overlay_height"])
        self.opacity_spin.setValue(defaults["overlay_opacity"])
        self.hotkey_open_btn.set_hotkey(defaults["hotkey_open"])
        self.hotkey_settings_btn.set_hotkey(defaults["hotkey_settings"])
        self.hotkey_quit_btn.set_hotkey(defaults["hotkey_quit"])
        self.confirm_quit_checkbox.setChecked(defaults["confirm_on_quit"])
        self.show_system_volume_checkbox.setChecked(defaults["show_system_volume"])
        self.always_show_filter_checkbox.setChecked(defaults["always_show_filter"])
        
        # Refresh overlay
        self.app.overlay.resize(defaults["overlay_width"], defaults["overlay_height"])
        self.app.overlay.update_background_opacity()
        self.app.overlay.update_system_volume_visibility()
        self.app.overlay.update_filter_display_mode()
        
        # Reapply hotkeys
        self.app.setup_hotkeys()

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
    
    def create_settings_profiles_tab(self):
        """Create the settings profiles management tab content"""
        return self._create_profile_tab(
            profile_type="settings",
            active_label_attr="active_settings_profile_label",
            list_attr="settings_profile_list",
            group_title_active="Active Settings Profile",
            group_title_available="Available Settings Profiles",
            get_active_name=self.app.settings_manager.get_active_settings_profile_name,
            get_names=self.app.settings_manager.get_settings_profile_names,
            is_default=self.app.settings_manager.is_default_settings_profile,
            has_unsaved_attr="has_unsaved_settings_changes",
            on_double_click=self._on_profile_double_clicked,
            actions=[
                ("Switch to Selected", lambda: self._on_switch_profile("settings")),
                ("Save to Active", lambda: self._on_save_to_active_profile("settings")),
                ("New Profile", lambda: self._on_new_profile("settings")),
                ("Rename", lambda: self._on_rename_profile("settings")),
                ("Delete", lambda: self._on_delete_profile("settings")),
            ]
        )
    
    def create_color_profiles_tab(self):
        """Create the color profiles management tab content"""
        return self._create_profile_tab(
            profile_type="color",
            active_label_attr="active_color_profile_label",
            list_attr="color_profile_list",
            group_title_active="Active Color Profile",
            group_title_available="Available Color Profiles",
            get_active_name=self.app.settings_manager.get_active_color_profile_name,
            get_names=self.app.settings_manager.get_color_profile_names,
            is_default=self.app.settings_manager.is_default_color_profile,
            has_unsaved_attr="has_unsaved_color_changes",
            on_double_click=self._on_profile_double_clicked,
            actions=[
                ("Switch to Selected", lambda: self._on_switch_profile("color")),
                ("Save to Active", lambda: self._on_save_to_active_profile("color")),
                ("New Profile", lambda: self._on_new_profile("color")),
                ("Rename", lambda: self._on_rename_profile("color")),
                ("Delete", lambda: self._on_delete_profile("color")),
            ]
        )
    
    def _create_profile_tab(self, profile_type, active_label_attr, list_attr, group_title_active, 
                            group_title_available, get_active_name, get_names, is_default, 
                            has_unsaved_attr, on_double_click, actions):
        """Generic method to create a profile management tab"""
        from PyQt5.QtWidgets import QListWidget
        
        profiles_widget = QVBoxLayout()
        
        # Active profile display
        active_profile_group = QGroupBox(group_title_active)
        active_profile_layout = QVBoxLayout()
        
        active_label = QLabel()
        active_label.setStyleSheet(f"color: #42a5f5; font-size: {UIConstants.TITLE_FONT_SIZE}px; padding: {UIConstants.MEDIUM_PADDING}px;")
        setattr(self, active_label_attr, active_label)
        active_profile_layout.addWidget(active_label)
        
        active_profile_group.setLayout(active_profile_layout)
        profiles_widget.addWidget(active_profile_group)
        
        # Profile list group
        profile_list_group = QGroupBox(group_title_available)
        profile_list_layout = QVBoxLayout()
        
        profile_list = QListWidget()
        profile_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #424242;
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid #666;
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                color: white;
                padding: {UIConstants.MEDIUM_PADDING}px;
            }}
            QListWidget::item {{
                padding: {UIConstants.SETTINGS_PADDING_STANDARD}px;
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
            }}
            QListWidget::item:selected {{
                background-color: #1e88e5;
            }}
            QListWidget::item:hover {{
                background-color: #555;
            }}
        """)
        profile_list.itemDoubleClicked.connect(lambda item: on_double_click(profile_type, item))
        setattr(self, list_attr, profile_list)
        profile_list_layout.addWidget(profile_list)
        profile_list_group.setLayout(profile_list_layout)
        profiles_widget.addWidget(profile_list_group)
        
        # Profile actions
        actions_layout = QHBoxLayout()
        
        primary_style = f"""
            QPushButton {{
                background-color: #1e88e5;
                color: white;
                border: none;
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: {UIConstants.SETTINGS_PADDING_STANDARD}px {UIConstants.BUTTON_PADDING_H}px;
            }}
            QPushButton:hover {{
                background-color: #42a5f5;
            }}
        """
        danger_style = f"""
            QPushButton {{
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: {UIConstants.SETTINGS_PADDING_STANDARD}px {UIConstants.BUTTON_PADDING_H}px;
            }}
            QPushButton:hover {{
                background-color: #f44336;
            }}
        """
        
        for i, (text, callback) in enumerate(actions):
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            # First two buttons are primary, last one is danger
            if i < 2:
                btn.setStyleSheet(primary_style)
            elif i == len(actions) - 1:
                btn.setStyleSheet(danger_style)
            actions_layout.addWidget(btn)
        
        profiles_widget.addLayout(actions_layout)
        
        # Populate the profile list
        self._refresh_profile_list(profile_type)
        
        container = QWidget()
        container.setLayout(profiles_widget)
        return container
    
    def _refresh_profile_list(self, profile_type):
        """Generic method to refresh a profile list"""
        if profile_type == "settings":
            profile_list = self.settings_profile_list
            active_label = self.active_settings_profile_label
            get_active = self.app.settings_manager.get_active_settings_profile_name
            get_names = self.app.settings_manager.get_settings_profile_names
            is_default = self.app.settings_manager.is_default_settings_profile
            has_unsaved = self.has_unsaved_settings_changes
        else:
            profile_list = self.color_profile_list
            active_label = self.active_color_profile_label
            get_active = self.app.settings_manager.get_active_color_profile_name
            get_names = self.app.settings_manager.get_color_profile_names
            is_default = self.app.settings_manager.is_default_color_profile
            has_unsaved = self.has_unsaved_color_changes
        
        profile_list.clear()
        active_profile = get_active()
        
        for profile_name in get_names():
            item_text = profile_name
            if profile_name == active_profile:
                item_text += " (Active)"
            if is_default(profile_name):
                item_text += " [Default]"
            profile_list.addItem(item_text)
        
        asterisk = " *" if has_unsaved else ""
        active_label.setText(f"{active_profile}{asterisk}")
    
    def refresh_settings_profile_list(self):
        """Refresh the list of settings profiles"""
        self._refresh_profile_list("settings")
    
    def refresh_color_profile_list(self):
        """Refresh the list of color profiles"""
        self._refresh_profile_list("color")
    
    def mark_settings_as_changed(self):
        """Mark that the settings profile has unsaved changes"""
        if not self.has_unsaved_settings_changes:
            self.has_unsaved_settings_changes = True
            self.refresh_settings_profile_list()
    
    def mark_colors_as_changed(self):
        """Mark that the color profile has unsaved changes"""
        if not self.has_unsaved_color_changes:
            self.has_unsaved_color_changes = True
            self.refresh_color_profile_list()
    
    # ========== Generic Profile Actions ==========
    
    def _extract_profile_name(self, item_text):
        """Extract actual profile name from list item text"""
        return item_text.split(" (")[0].split(" [")[0]
    
    def _on_new_profile(self, profile_type):
        """Create a new profile"""
        from PyQt5.QtWidgets import QInputDialog
        
        title = f"New {'Settings' if profile_type == 'settings' else 'Color'} Profile"
        name, ok = QInputDialog.getText(self, title, "Enter profile name:", text="")
        
        if ok and name:
            name = name.strip()
            if profile_type == "settings":
                if self.app.settings_manager.create_settings_profile(name, base_on_current=True):
                    self.app.settings_manager.switch_settings_profile(name)
                    self.refresh_settings_profile_list()
                    self.refresh_overlay_after_settings_profile_switch()
            else:
                if self.app.settings_manager.create_color_profile(name, base_on_current=True):
                    self.app.settings_manager.switch_color_profile(name)
                    self.refresh_color_profile_list()
                    self.refresh_overlay_colors()
    
    def _on_rename_profile(self, profile_type):
        """Rename the selected profile"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        profile_list = self.settings_profile_list if profile_type == "settings" else self.color_profile_list
        is_default = self.app.settings_manager.is_default_settings_profile if profile_type == "settings" else self.app.settings_manager.is_default_color_profile
        rename_func = self.app.settings_manager.rename_settings_profile if profile_type == "settings" else self.app.settings_manager.rename_color_profile
        refresh_func = self.refresh_settings_profile_list if profile_type == "settings" else self.refresh_color_profile_list
        
        selected_items = profile_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a profile to rename.")
            return
        
        old_name = self._extract_profile_name(selected_items[0].text())
        
        if is_default(old_name):
            QMessageBox.warning(self, "Cannot Rename", "The default profile cannot be renamed.")
            return
        
        title = f"Rename {'Settings' if profile_type == 'settings' else 'Color'} Profile"
        new_name, ok = QInputDialog.getText(self, title, "Enter new profile name:", text=old_name)
        
        if ok and new_name:
            new_name = new_name.strip()
            if rename_func(old_name, new_name):
                refresh_func()
    
    def _on_delete_profile(self, profile_type):
        """Delete the selected profile"""
        from PyQt5.QtWidgets import QMessageBox
        
        profile_list = self.settings_profile_list if profile_type == "settings" else self.color_profile_list
        is_default = self.app.settings_manager.is_default_settings_profile if profile_type == "settings" else self.app.settings_manager.is_default_color_profile
        get_active = self.app.settings_manager.get_active_settings_profile_name if profile_type == "settings" else self.app.settings_manager.get_active_color_profile_name
        delete_func = self.app.settings_manager.delete_settings_profile if profile_type == "settings" else self.app.settings_manager.delete_color_profile
        refresh_func = self.refresh_settings_profile_list if profile_type == "settings" else self.refresh_color_profile_list
        
        selected_items = profile_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a profile to delete.")
            return
        
        profile_name = self._extract_profile_name(selected_items[0].text())
        
        if is_default(profile_name):
            QMessageBox.warning(self, "Cannot Delete", "The default profile cannot be deleted.")
            return
        
        type_name = "settings" if profile_type == "settings" else "color"
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the {type_name} profile '{profile_name}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            was_active = profile_name == get_active()
            if delete_func(profile_name):
                refresh_func()
                if was_active:
                    if profile_type == "settings":
                        self.refresh_overlay_after_settings_profile_switch()
                    else:
                        self.refresh_overlay_colors()
    
    def _on_profile_double_clicked(self, profile_type, item):
        """Handle double-click on a profile item"""
        profile_name = self._extract_profile_name(item.text())
        
        if profile_type == "settings":
            if self.app.settings_manager.switch_settings_profile(profile_name):
                self.has_unsaved_settings_changes = False
                self.refresh_settings_profile_list()
                self.refresh_overlay_after_settings_profile_switch()
        else:
            if self.app.settings_manager.switch_color_profile(profile_name):
                self.has_unsaved_color_changes = False
                self.refresh_color_profile_list()
                self.refresh_overlay_colors()
                self.refresh_color_buttons()
    
    def _on_switch_profile(self, profile_type):
        """Switch to the selected profile"""
        from PyQt5.QtWidgets import QMessageBox
        
        profile_list = self.settings_profile_list if profile_type == "settings" else self.color_profile_list
        
        selected_items = profile_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a profile to switch to.")
            return
        
        profile_name = self._extract_profile_name(selected_items[0].text())
        
        if profile_type == "settings":
            if self.app.settings_manager.switch_settings_profile(profile_name):
                self.has_unsaved_settings_changes = False
                self.refresh_settings_profile_list()
                self.refresh_overlay_after_settings_profile_switch()
        else:
            if self.app.settings_manager.switch_color_profile(profile_name):
                self.has_unsaved_color_changes = False
                self.refresh_color_profile_list()
                self.refresh_overlay_colors()
                self.refresh_color_buttons()
    
    def _on_save_to_active_profile(self, profile_type):
        """Save current settings/colors to the active profile"""
        from PyQt5.QtWidgets import QMessageBox
        
        if profile_type == "settings":
            active_profile = self.app.settings_manager.get_active_settings_profile_name()
            save_func = self.app.settings_manager.save_to_settings_profile
            refresh_func = self.refresh_settings_profile_list
            type_name = "settings"
        else:
            active_profile = self.app.settings_manager.get_active_color_profile_name()
            save_func = self.app.settings_manager.save_to_color_profile
            refresh_func = self.refresh_color_profile_list
            type_name = "colors"
        
        reply = QMessageBox.question(
            self, "Confirm Save",
            f"Save current {type_name} to profile '{active_profile}'?\n\nThis will overwrite the saved {type_name} in this profile.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            save_func(active_profile)
            if profile_type == "settings":
                self.has_unsaved_settings_changes = False
            else:
                self.has_unsaved_color_changes = False
            refresh_func()
    
    def refresh_color_buttons(self):
        """Refresh color buttons to reflect current color profile"""
        sm = self.app.settings_manager
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
    
    def refresh_overlay_after_settings_profile_switch(self):
        """Refresh the overlay after switching settings profiles"""
        sm = self.app.settings_manager
        
        # Update all UI elements to reflect the new profile settings
        self.width_spin.setValue(sm.overlay_width)
        self.height_spin.setValue(sm.overlay_height)
        self.opacity_spin.setValue(sm.overlay_opacity)
        self.hotkey_open_btn.set_hotkey(sm.hotkey_open)
        self.hotkey_settings_btn.set_hotkey(sm.hotkey_settings)
        self.hotkey_quit_btn.set_hotkey(sm.hotkey_quit)
        self.confirm_quit_checkbox.setChecked(sm.confirm_on_quit)
        self.show_system_volume_checkbox.setChecked(sm.show_system_volume)
        self.always_show_filter_checkbox.setChecked(sm.always_show_filter)
        
        # Refresh overlay
        self.app.overlay.resize(self.app.settings_manager.overlay_width, self.app.settings_manager.overlay_height)
        self.app.overlay.update_background_opacity()
        self.app.overlay.update_system_volume_visibility()
        self.app.overlay.update_filter_display_mode()
        
        # Reapply hotkeys
        self.app.setup_hotkeys()
        
    def create_about_tab(self):
        """Create the about tab content"""
        about_widget = QVBoxLayout()
        
        # App name and version
        title_label = QLabel(f"<h2>{AppInfo.APP_NAME}</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: white; margin: {UIConstants.SETTINGS_MARGIN_STANDARD}px;")
        
        version_label = QLabel(f"<p style='font-size: {UIConstants.SETTINGS_ABOUT_TITLE_FONT_SIZE}px; color: #aaa;'>Version {AppInfo.VERSION}</p>")
        version_label.setAlignment(Qt.AlignCenter)
        
        # Description
        description_label = QLabel(f"""
            <div style='color: white; font-family: Arial; font-size: {UIConstants.SETTINGS_ABOUT_DESCRIPTION_FONT_SIZE}px;'>
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
                
                <p style='margin-top: {UIConstants.SETTINGS_MARGIN_TOP_LARGE}px; color: #aaa; font-size: {UIConstants.SETTINGS_ABOUT_FOOTER_FONT_SIZE}px;'><b>License:</b> {AppInfo.LICENSE}</p>
                <p style='color: #aaa; font-size: {UIConstants.SETTINGS_ABOUT_FOOTER_FONT_SIZE}px;'>© {AppInfo.YEAR} {AppInfo.AUTHOR}</p>
            </div>
        """)
        description_label.setWordWrap(True)
        description_label.setOpenExternalLinks(True)
        description_label.setTextFormat(Qt.RichText)
        description_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        description_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                padding: {UIConstants.XLARGE_PADDING}px;
            }}
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
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #2b2b2b;
                color: white;
            }}
            QGroupBox {{
                border: {UIConstants.GROUP_BOX_BORDER_WIDTH}px solid #555;
                border-radius: {UIConstants.FRAME_RADIUS}px;
                margin-top: {UIConstants.GROUP_BOX_MARGIN_TOP}px;
                padding-top: {UIConstants.GROUP_BOX_PADDING_TOP}px;
                font-weight: bold;
                color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {UIConstants.GROUP_BOX_TITLE_LEFT}px;
                padding: {UIConstants.STRETCH_FACTOR_NONE} {UIConstants.GROUP_BOX_TITLE_PADDING}px;
                color: white;
            }}
            QLabel {{
                color: white;
            }}
            QSpinBox, QDoubleSpinBox, QLineEdit {{
                background-color: #424242;
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid #666;
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: {UIConstants.MEDIUM_PADDING}px;
                color: white;
            }}
            QPushButton {{
                background-color: #1e88e5;
                color: white;
                border: none;
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: {UIConstants.SETTINGS_PADDING_STANDARD}px {UIConstants.BUTTON_PADDING_H}px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #42a5f5;
            }}
            QTabWidget::pane {{
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid #555;
                border-radius: {UIConstants.FRAME_RADIUS}px;
                background-color: #2b2b2b;
            }}
            QTabBar::tab {{
                background-color: #424242;
                color: white;
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid #555;
                padding: {UIConstants.SETTINGS_PADDING_STANDARD}px {UIConstants.TAB_PADDING_H}px;
                margin-right: {UIConstants.TAB_MARGIN_RIGHT}px;
                border-top-left-radius: {UIConstants.FRAME_RADIUS}px;
                border-top-right-radius: {UIConstants.FRAME_RADIUS}px;
            }}
            QTabBar::tab:selected {{
                background-color: #1e88e5;
                color: white;
            }}
            QTabBar::tab:hover {{
                background-color: #555;
            }}
        """)
    
    def on_width_changed(self, value: int) -> None:
        """Handle width change in real-time"""
        self.mark_settings_as_changed()
        self.app.settings_manager.set("overlay_width", value)
        self.app.overlay.resize(value, self.app.settings_manager.overlay_height)
        self.app.settings_manager.save_settings()
    
    def on_height_changed(self, value: int) -> None:
        """Handle height change in real-time"""
        self.mark_settings_as_changed()
        self.app.settings_manager.set("overlay_height", value)
        self.app.overlay.resize(self.app.settings_manager.overlay_width, value)
        self.app.settings_manager.save_settings()
    
    def on_opacity_changed(self, value: float) -> None:
        """Handle opacity change in real-time"""
        self.mark_settings_as_changed()
        self.app.settings_manager.set("overlay_opacity", value)
        self.app.overlay.update_background_opacity()
        self.app.settings_manager.save_settings()
    
    def on_confirm_quit_changed(self, state: int) -> None:
        """Handle confirm quit checkbox change"""
        self.mark_settings_as_changed()
        self.app.settings_manager.set("confirm_on_quit", bool(state))
        self.app.settings_manager.save_settings(debounce=False)
    
    def on_show_system_volume_changed(self, state: int) -> None:
        """Handle show system volume checkbox change"""
        self.mark_settings_as_changed()
        self.app.settings_manager.set("show_system_volume", bool(state))
        self.app.overlay.update_system_volume_visibility()
        self.app.settings_manager.save_settings(debounce=False)
    
    def on_always_show_filter_changed(self, state: int) -> None:
        """Handle always show filter checkbox change"""
        self.mark_settings_as_changed()
        self.app.settings_manager.set("always_show_filter", bool(state))
        self.app.overlay.update_filter_display_mode()
        self.app.settings_manager.save_settings(debounce=False)
    
    def on_hotkey_recorded(self, setting_key: str, new_hotkey: str) -> None:
        """Handle hotkey recording - save and reapply immediately"""
        self.mark_settings_as_changed()
        self.app.settings_manager.set(setting_key, new_hotkey)
        self.app.settings_manager.save_settings(debounce=False)
        self.app.setup_hotkeys()
    
    def on_save_settings_to_profile(self) -> None:
        """Save current settings to the active settings profile"""
        from PyQt5.QtWidgets import QMessageBox
        
        active_profile = self.app.settings_manager.get_active_settings_profile_name()
        self.app.settings_manager.save_to_settings_profile(active_profile)
        self.has_unsaved_settings_changes = False
        self.refresh_settings_profile_list()
        
        QMessageBox.information(
            self, "Saved",
            f"Settings saved to profile '{active_profile}'."
        )
    
    def on_save_colors_to_profile(self) -> None:
        """Save current colors to the active color profile"""
        from PyQt5.QtWidgets import QMessageBox
        
        active_profile = self.app.settings_manager.get_active_color_profile_name()
        self.app.settings_manager.save_to_color_profile(active_profile)
        self.has_unsaved_color_changes = False
        self.refresh_color_profile_list()
        
        QMessageBox.information(
            self, "Saved",
            f"Colors saved to profile '{active_profile}'."
        )
    
    def enter_resize_mode(self) -> None:
        """Enter resize mode - makes the overlay window resizable"""
        self.app.overlay.enter_resize_mode()
        self.hide()  # Hide settings while resizing
    
    def update_size_spinboxes(self) -> None:
        """Update the size spinboxes with current overlay dimensions"""
        self.width_spin.blockSignals(True)
        self.height_spin.blockSignals(True)
        self.width_spin.setValue(self.app.settings_manager.overlay_width)
        self.height_spin.setValue(self.app.settings_manager.overlay_height)
        self.width_spin.blockSignals(False)
        self.height_spin.blockSignals(False)
