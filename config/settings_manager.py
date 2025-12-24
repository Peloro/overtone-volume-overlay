import json
import os
from typing import Dict, Any
from PyQt5.QtCore import QTimer
from .ui_constants import UIConstants, Hotkeys
from .profiles_manager import SettingsProfilesManager, ColorProfilesManager
from utils.logger import get_logger

logger = get_logger(__name__)


class SettingsManager:
    
    def __init__(self):
        self.settings: Dict[str, Any] = {}
        self._default_settings = self._get_default_settings()
        self._default_colors = self._get_default_colors()
        self._save_timer: QTimer = None
        self._save_debounce_ms = UIConstants.SETTINGS_SAVE_DEBOUNCE_MS
        
        # Separate profile managers for settings and colors
        self.settings_profiles_manager = SettingsProfilesManager()
        self.color_profiles_manager = ColorProfilesManager()
        
        self.load_settings()
    
    def _setup_save_timer(self) -> None:
        if self._save_timer is None:
            self._save_timer = QTimer()
            self._save_timer.setSingleShot(True)
            self._save_timer.timeout.connect(self._do_save_settings)
    
    @staticmethod
    def _get_default_settings() -> Dict[str, Any]:
        """Get default non-color settings."""
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
        }
    
    @staticmethod
    def _get_default_colors() -> Dict[str, Any]:
        """Get default color settings."""
        return {
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
    
    def load_settings(self) -> None:
        """Load settings from both profile managers."""
        # Start with defaults
        self.settings = self._default_settings.copy()
        self.settings.update(self._default_colors)
        
        # Load settings from settings profile
        settings_profile = self.settings_profiles_manager.get_active_profile_settings()
        self.settings.update(settings_profile)
        
        # Load colors from color profile
        color_profile = self.color_profiles_manager.get_active_profile_settings()
        self.settings.update(color_profile)
        
        logger.info(f"Settings loaded from profile '{self.settings_profiles_manager.get_active_profile_name()}', "
                    f"colors from '{self.color_profiles_manager.get_active_profile_name()}'")
        
        self._validate_settings()
        self._setup_save_timer()
    
    def _do_save_settings(self) -> None:
        """Save settings to both profile managers."""
        try:
            # Save non-color settings to settings profile
            active_settings_profile = self.settings_profiles_manager.get_active_profile_name()
            self.settings_profiles_manager.save_current_settings_to_profile(active_settings_profile, self.settings)
            
            # Save color settings to color profile
            active_color_profile = self.color_profiles_manager.get_active_profile_name()
            self.color_profiles_manager.save_current_settings_to_profile(active_color_profile, self.settings)
            
            logger.debug(f"Settings saved to profiles")
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
    
    @staticmethod
    def _clamp_value(value, min_val, max_val) -> Any:
        return max(min_val, min(max_val, value))
    
    def _validate_settings(self) -> None:
        self.settings["overlay_width"] = self._clamp_value(
            self.settings.get("overlay_width", UIConstants.DEFAULT_OVERLAY_WIDTH),
            UIConstants.MIN_OVERLAY_WIDTH, UIConstants.MAX_OVERLAY_WIDTH
        )
        self.settings["overlay_height"] = self._clamp_value(
            self.settings.get("overlay_height", UIConstants.DEFAULT_OVERLAY_HEIGHT),
            UIConstants.MIN_OVERLAY_HEIGHT, UIConstants.MAX_OVERLAY_HEIGHT
        )
        self.settings["overlay_opacity"] = round(self._clamp_value(
            self.settings.get("overlay_opacity", UIConstants.DEFAULT_OPACITY),
            UIConstants.MIN_OPACITY, UIConstants.MAX_OPACITY
        ), UIConstants.OPACITY_DECIMAL_PLACES)
        
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
        if debounce and self._save_timer is not None:
            self._save_timer.stop()
            self._save_timer.start(self._save_debounce_ms)
        else:
            self._do_save_settings()
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
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
            self.settings[key] = round(self._clamp_value(v, UIConstants.MIN_OPACITY, UIConstants.MAX_OPACITY), UIConstants.OPACITY_DECIMAL_PLACES)
        else:
            self.settings[key] = value
    
    def update(self, new_settings: Dict[str, Any]) -> None:
        self.settings.update(new_settings)
        self._validate_settings()
        self.save_settings()
    
    def reset_to_defaults(self) -> None:
        self.settings = self._default_settings.copy()
        self.settings.update(self._default_colors)
        self.save_settings(debounce=False)
    
    def reset_colors_to_defaults(self) -> None:
        """Reset only color settings to defaults."""
        self.settings.update(self._default_colors)
        self.save_settings(debounce=False)
    
    def reset_settings_to_defaults(self) -> None:
        """Reset only non-color settings to defaults."""
        self.settings.update(self._default_settings)
        self.save_settings(debounce=False)
    
    def __getattr__(self, name):
        if name in self.settings:
            return self.settings[name]
        if name in self._default_settings:
            return self._default_settings[name]
        if name in self._default_colors:
            return self._default_colors[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    # ========== Settings Profile Methods ==========
    
    def get_active_settings_profile_name(self) -> str:
        """Get the active settings profile name."""
        return self.settings_profiles_manager.get_active_profile_name()
    
    def get_settings_profile_names(self) -> list:
        """Get all settings profile names."""
        return self.settings_profiles_manager.get_profile_names()
    
    def switch_settings_profile(self, profile_name: str) -> bool:
        """Switch to a different settings profile."""
        if self.settings_profiles_manager.switch_profile(profile_name):
            self.load_settings()
            return True
        return False
    
    def create_settings_profile(self, profile_name: str, base_on_current: bool = True) -> bool:
        """Create a new settings profile."""
        return self.settings_profiles_manager.create_profile(profile_name, base_on_current)
    
    def delete_settings_profile(self, profile_name: str) -> bool:
        """Delete a settings profile."""
        was_active = profile_name == self.settings_profiles_manager.get_active_profile_name()
        result = self.settings_profiles_manager.delete_profile(profile_name)
        if result and was_active:
            self.load_settings()
        return result
    
    def rename_settings_profile(self, old_name: str, new_name: str) -> bool:
        """Rename a settings profile."""
        return self.settings_profiles_manager.rename_profile(old_name, new_name)
    
    def save_to_settings_profile(self, profile_name: str) -> bool:
        """Save current settings to a settings profile."""
        return self.settings_profiles_manager.save_current_settings_to_profile(profile_name, self.settings)
    
    def is_default_settings_profile(self, profile_name: str) -> bool:
        """Check if a settings profile is the default."""
        return self.settings_profiles_manager.is_default_profile(profile_name)
    
    # ========== Color Profile Methods ==========
    
    def get_active_color_profile_name(self) -> str:
        """Get the active color profile name."""
        return self.color_profiles_manager.get_active_profile_name()
    
    def get_color_profile_names(self) -> list:
        """Get all color profile names."""
        return self.color_profiles_manager.get_profile_names()
    
    def switch_color_profile(self, profile_name: str) -> bool:
        """Switch to a different color profile."""
        if self.color_profiles_manager.switch_profile(profile_name):
            self.load_settings()
            return True
        return False
    
    def create_color_profile(self, profile_name: str, base_on_current: bool = True) -> bool:
        """Create a new color profile."""
        return self.color_profiles_manager.create_profile(profile_name, base_on_current)
    
    def delete_color_profile(self, profile_name: str) -> bool:
        """Delete a color profile."""
        was_active = profile_name == self.color_profiles_manager.get_active_profile_name()
        result = self.color_profiles_manager.delete_profile(profile_name)
        if result and was_active:
            self.load_settings()
        return result
    
    def rename_color_profile(self, old_name: str, new_name: str) -> bool:
        """Rename a color profile."""
        return self.color_profiles_manager.rename_profile(old_name, new_name)
    
    def save_to_color_profile(self, profile_name: str) -> bool:
        """Save current colors to a color profile."""
        return self.color_profiles_manager.save_current_settings_to_profile(profile_name, self.settings)
    
    def is_default_color_profile(self, profile_name: str) -> bool:
        """Check if a color profile is the default."""
        return self.color_profiles_manager.is_default_profile(profile_name)
    
    # ========== Legacy compatibility methods ==========
    # These are kept for backward compatibility with existing code
    
    def get_active_profile_name(self) -> str:
        """Legacy: Get the active settings profile name."""
        return self.get_active_settings_profile_name()
    
    def get_profile_names(self) -> list:
        """Legacy: Get all settings profile names."""
        return self.get_settings_profile_names()
    
    def switch_profile(self, profile_name: str) -> bool:
        """Legacy: Switch to a different settings profile."""
        return self.switch_settings_profile(profile_name)
    
    def create_profile(self, profile_name: str, base_on_current: bool = True) -> bool:
        """Legacy: Create a new settings profile."""
        return self.create_settings_profile(profile_name, base_on_current)
    
    def delete_profile(self, profile_name: str) -> bool:
        """Legacy: Delete a settings profile."""
        return self.delete_settings_profile(profile_name)
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """Legacy: Rename a settings profile."""
        return self.rename_settings_profile(old_name, new_name)
    
    def save_to_profile(self, profile_name: str) -> bool:
        """Legacy: Save current settings to a settings profile."""
        return self.save_to_settings_profile(profile_name)
    
    def is_default_profile(self, profile_name: str) -> bool:
        """Legacy: Check if a settings profile is the default."""
        return self.is_default_settings_profile(profile_name)
