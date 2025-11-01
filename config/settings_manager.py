"""
Settings Manager for Overtone Application
Handles loading, saving, and managing application settings
"""
import json
import os
from typing import Dict, Any
from PyQt5.QtCore import QTimer
from .ui_constants import UIConstants, Hotkeys
from .profiles_manager import ProfilesManager
from utils.logger import get_logger

logger = get_logger(__name__)


class SettingsManager:
    """Manages application settings with file persistence"""
    
    def __init__(self):
        self.settings: Dict[str, Any] = {}
        self._default_settings = self._get_default_settings()
        self._save_timer: QTimer = None
        self._save_debounce_ms = 500  # Wait 500ms after last change before saving
        self.profiles_manager = ProfilesManager()
        self.load_settings()
    
    def _setup_save_timer(self) -> None:
        """Setup debounced save timer"""
        if self._save_timer is None:
            self._save_timer = QTimer()
            self._save_timer.setSingleShot(True)
            self._save_timer.timeout.connect(self._do_save_settings)
    
    @staticmethod
    def _get_default_settings() -> Dict[str, Any]:
        """Get default settings"""
        return {
            "overlay_width": UIConstants.DEFAULT_OVERLAY_WIDTH,
            "overlay_height": UIConstants.DEFAULT_OVERLAY_HEIGHT,
            "overlay_opacity": UIConstants.DEFAULT_OPACITY,
            "hotkey_open": Hotkeys.DEFAULT_HOTKEY_OPEN,
            "hotkey_settings": Hotkeys.DEFAULT_HOTKEY_SETTINGS,
            "hotkey_quit": Hotkeys.DEFAULT_HOTKEY_QUIT,
            "confirm_on_quit": True,
            "show_system_volume": True,
            "always_show_filter": False,
            # Color customization
            "color_main_background": "rgba(30, 30, 30, {alpha})",
            "color_title_bar_bg": "rgba(43, 43, 43, 255)",
            "color_master_frame_bg": "rgba(30, 58, 95, 255)",
            "color_container_bg": "rgba(43, 43, 43, 255)",
            "color_app_control_bg": "rgba(50, 50, 50, 200)",
            "color_master_slider_handle": "#4caf50",
            "color_app_slider_handle": "#1e88e5",
            "color_primary_button_bg": "#1e88e5",
            "color_close_button_bg": "#d32f2f",
        }
    
    def load_settings(self) -> None:
        """Load settings from active profile"""
        # Load settings from the active profile
        profile_settings = self.profiles_manager.get_active_profile_settings()
        self.settings = self._default_settings.copy()
        self.settings.update(profile_settings)
        
        logger.info(f"Settings loaded from profile '{self.profiles_manager.get_active_profile_name()}'")
        
        self._validate_settings()
        self._setup_save_timer()
    
    def _do_save_settings(self) -> None:
        """Actually write settings to the active profile"""
        try:
            # Save current settings to the active profile
            active_profile = self.profiles_manager.get_active_profile_name()
            self.profiles_manager.save_current_settings_to_profile(active_profile, self.settings)
            logger.debug(f"Settings saved to profile '{active_profile}'")
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
    
    @staticmethod
    def _clamp_value(value, min_val, max_val) -> Any:
        """Clamp a value between min and max"""
        return max(min_val, min(max_val, value))
    
    def _validate_settings(self) -> None:
        """Validate and clamp settings to acceptable ranges"""
        self.settings["overlay_width"] = self._clamp_value(
            self.settings.get("overlay_width", UIConstants.DEFAULT_OVERLAY_WIDTH),
            UIConstants.MIN_OVERLAY_WIDTH, UIConstants.MAX_OVERLAY_WIDTH
        )
        self.settings["overlay_height"] = self._clamp_value(
            self.settings.get("overlay_height", UIConstants.DEFAULT_OVERLAY_HEIGHT),
            UIConstants.MIN_OVERLAY_HEIGHT, UIConstants.MAX_OVERLAY_HEIGHT
        )
        # Round opacity to 2 decimal places to avoid floating point precision issues
        self.settings["overlay_opacity"] = round(self._clamp_value(
            self.settings.get("overlay_opacity", UIConstants.DEFAULT_OPACITY),
            UIConstants.MIN_OPACITY, UIConstants.MAX_OPACITY
        ), 2)
        
        for key, default in [
            ("hotkey_open", Hotkeys.DEFAULT_HOTKEY_OPEN),
            ("hotkey_settings", Hotkeys.DEFAULT_HOTKEY_SETTINGS),
            ("hotkey_quit", Hotkeys.DEFAULT_HOTKEY_QUIT),
            ("confirm_on_quit", True),
            ("show_system_volume", True),
            ("always_show_filter", False)
        ]:
            self.settings.setdefault(key, default)
    
    def save_settings(self, debounce: bool = True) -> None:
        """
        Save settings to file
        
        Args:
            debounce: If True, debounce the save operation. If False, save immediately.
        """
        if debounce and self._save_timer is not None:
            # Restart the timer - this debounces rapid changes
            self._save_timer.stop()
            self._save_timer.start(self._save_debounce_ms)
        else:
            # Save immediately
            self._do_save_settings()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value"""
        # For overlay dimensions and opacity, clamp incoming values immediately
        if key == "overlay_width":
            try:
                v = int(value)
            except (TypeError, ValueError):
                v = UIConstants.DEFAULT_OVERLAY_WIDTH
            self.settings[key] = self._clamp_value(v, UIConstants.MIN_OVERLAY_WIDTH, UIConstants.MAX_OVERLAY_WIDTH)
        elif key == "overlay_height":
            try:
                v = int(value)
            except (TypeError, ValueError):
                v = UIConstants.DEFAULT_OVERLAY_HEIGHT
            self.settings[key] = self._clamp_value(v, UIConstants.MIN_OVERLAY_HEIGHT, UIConstants.MAX_OVERLAY_HEIGHT)
        elif key == "overlay_opacity":
            try:
                v = float(value)
            except (TypeError, ValueError):
                v = UIConstants.DEFAULT_OPACITY
            # Round to 2 decimal places to avoid floating point precision issues
            self.settings[key] = round(self._clamp_value(v, UIConstants.MIN_OPACITY, UIConstants.MAX_OPACITY), 2)
        else:
            self.settings[key] = value
    
    def update(self, new_settings: Dict[str, Any]) -> None:
        """Update multiple settings at once"""
        self.settings.update(new_settings)
        self._validate_settings()
        self.save_settings()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.settings = self._default_settings.copy()
        self.save_settings(debounce=False)  # Immediate save for explicit user action
    
    def __getattr__(self, name):
        """Dynamic property access for settings"""
        if name in self.settings:
            return self.settings[name]
        if name in self._default_settings:
            return self._default_settings[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    # Profile management methods
    def get_active_profile_name(self) -> str:
        """Get the name of the active profile"""
        return self.profiles_manager.get_active_profile_name()
    
    def get_profile_names(self) -> list:
        """Get list of all profile names"""
        return self.profiles_manager.get_profile_names()
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different profile and reload settings"""
        if self.profiles_manager.switch_profile(profile_name):
            self.load_settings()
            return True
        return False
    
    def create_profile(self, profile_name: str, base_on_current: bool = True) -> bool:
        """Create a new profile"""
        return self.profiles_manager.create_profile(profile_name, base_on_current)
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile"""
        result = self.profiles_manager.delete_profile(profile_name)
        if result and profile_name == self.profiles_manager.get_active_profile_name():
            # If we deleted the active profile, reload settings
            self.load_settings()
        return result
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """Rename a profile"""
        return self.profiles_manager.rename_profile(old_name, new_name)
    
    def save_to_profile(self, profile_name: str) -> bool:
        """Save current settings to a specific profile"""
        return self.profiles_manager.save_current_settings_to_profile(profile_name, self.settings)
    
    def is_default_profile(self, profile_name: str) -> bool:
        """Check if a profile is the default profile"""
        return self.profiles_manager.is_default_profile(profile_name)
