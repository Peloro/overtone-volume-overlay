import json
import os
from typing import Dict, Any
from PyQt5.QtCore import QTimer
from .config import UIConstants, Hotkeys, get_default_settings, get_default_colors
from .profiles_manager import SettingsProfilesManager, ColorProfilesManager, VolumeProfilesManager
from utils import get_logger

logger = get_logger(__name__)


class SettingsManager:
    
    def __init__(self):
        self.settings: Dict[str, Any] = {}
        self._default_settings = get_default_settings()
        self._default_colors = get_default_colors()
        self._save_timer: QTimer = None
        self._save_debounce_ms = UIConstants.SETTINGS_SAVE_DEBOUNCE_MS
        
        # Separate profile managers for settings and colors
        self.settings_profiles_manager = SettingsProfilesManager()
        self.color_profiles_manager = ColorProfilesManager()
        self.volume_profiles_manager = VolumeProfilesManager()
        
        self.load_settings()
    
    def _setup_save_timer(self) -> None:
        if self._save_timer is None:
            self._save_timer = QTimer()
            self._save_timer.setSingleShot(True)
            self._save_timer.timeout.connect(self._do_save_settings)
    
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
    
    # ========== Generic Profile Methods ==========
    
    def _get_profile_manager(self, profile_type: str):
        """Get the profile manager for the given type."""
        managers = {
            "settings": self.settings_profiles_manager,
            "colors": self.color_profiles_manager,
            "volumes": self.volume_profiles_manager
        }
        return managers.get(profile_type)
    
    def get_active_profile_name(self, profile_type: str) -> str:
        """Get the active profile name for a profile type."""
        return self._get_profile_manager(profile_type).get_active_profile_name()
    
    def get_profile_names(self, profile_type: str) -> list:
        """Get all profile names for a profile type."""
        return self._get_profile_manager(profile_type).get_profile_names()
    
    def switch_profile(self, profile_type: str, profile_name: str) -> bool:
        """Switch to a different profile."""
        manager = self._get_profile_manager(profile_type)
        if manager.switch_profile(profile_name):
            if profile_type in ("settings", "colors"):
                self.load_settings()
            return True
        return False
    
    def create_profile(self, profile_type: str, profile_name: str, base_on_current: bool = True) -> bool:
        """Create a new profile."""
        return self._get_profile_manager(profile_type).create_profile(profile_name, base_on_current)
    
    def delete_profile(self, profile_type: str, profile_name: str) -> bool:
        """Delete a profile."""
        manager = self._get_profile_manager(profile_type)
        was_active = profile_name == manager.get_active_profile_name()
        result = manager.delete_profile(profile_name)
        if result and was_active and profile_type in ("settings", "colors"):
            self.load_settings()
        return result
    
    def rename_profile(self, profile_type: str, old_name: str, new_name: str) -> bool:
        """Rename a profile."""
        return self._get_profile_manager(profile_type).rename_profile(old_name, new_name)
    
    def save_to_profile(self, profile_type: str, profile_name: str, settings: dict = None) -> bool:
        """Save settings to a profile."""
        if settings is None:
            settings = self.settings
        return self._get_profile_manager(profile_type).save_current_settings_to_profile(profile_name, settings)
    
    def is_default_profile(self, profile_type: str, profile_name: str) -> bool:
        """Check if a profile is the default."""
        return self._get_profile_manager(profile_type).is_default_profile(profile_name)
    
    # ========== Convenience Methods (backwards compatibility) ==========
    
    # Settings profile shortcuts
    def get_active_settings_profile_name(self) -> str:
        return self.get_active_profile_name("settings")
    
    def get_settings_profile_names(self) -> list:
        return self.get_profile_names("settings")
    
    def switch_settings_profile(self, profile_name: str) -> bool:
        return self.switch_profile("settings", profile_name)
    
    def create_settings_profile(self, profile_name: str, base_on_current: bool = True) -> bool:
        return self.create_profile("settings", profile_name, base_on_current)
    
    def delete_settings_profile(self, profile_name: str) -> bool:
        return self.delete_profile("settings", profile_name)
    
    def rename_settings_profile(self, old_name: str, new_name: str) -> bool:
        return self.rename_profile("settings", old_name, new_name)
    
    def save_to_settings_profile(self, profile_name: str) -> bool:
        return self.save_to_profile("settings", profile_name)
    
    def is_default_settings_profile(self, profile_name: str) -> bool:
        return self.is_default_profile("settings", profile_name)
    
    # Color profile shortcuts
    def get_active_color_profile_name(self) -> str:
        return self.get_active_profile_name("colors")
    
    def get_color_profile_names(self) -> list:
        return self.get_profile_names("colors")
    
    def switch_color_profile(self, profile_name: str) -> bool:
        return self.switch_profile("colors", profile_name)
    
    def create_color_profile(self, profile_name: str, base_on_current: bool = True) -> bool:
        return self.create_profile("colors", profile_name, base_on_current)
    
    def delete_color_profile(self, profile_name: str) -> bool:
        return self.delete_profile("colors", profile_name)
    
    def rename_color_profile(self, old_name: str, new_name: str) -> bool:
        return self.rename_profile("colors", old_name, new_name)
    
    def save_to_color_profile(self, profile_name: str) -> bool:
        return self.save_to_profile("colors", profile_name)
    
    def is_default_color_profile(self, profile_name: str) -> bool:
        return self.is_default_profile("colors", profile_name)

    # Volume profile shortcuts
    def get_active_volume_profile_name(self) -> str:
        return self.get_active_profile_name("volumes")
    
    def get_volume_profile_names(self) -> list:
        return self.get_profile_names("volumes")
    
    def get_volume_profile_settings(self, profile_name: str = None) -> dict:
        """Get volume profile settings. If profile_name is None, returns active profile."""
        if profile_name is None:
            return self.volume_profiles_manager.get_active_profile_settings()
        # Get specific profile settings
        section = self.volume_profiles_manager._manager._get_section("volumes")
        return section["profiles"].get(profile_name, {"app_volumes": {}}).copy()
    
    def switch_volume_profile(self, profile_name: str) -> bool:
        return self.switch_profile("volumes", profile_name)
    
    def create_volume_profile(self, profile_name: str, base_on_current: bool = False) -> bool:
        return self.create_profile("volumes", profile_name, base_on_current)
    
    def delete_volume_profile(self, profile_name: str) -> bool:
        return self.delete_profile("volumes", profile_name)
    
    def rename_volume_profile(self, old_name: str, new_name: str) -> bool:
        return self.rename_profile("volumes", old_name, new_name)
    
    def save_to_volume_profile(self, profile_name: str, app_volumes: dict) -> bool:
        """Save app volumes to a volume profile."""
        settings = {"app_volumes": app_volumes}
        return self.save_to_profile("volumes", profile_name, settings)
    
    def is_default_volume_profile(self, profile_name: str) -> bool:
        return self.is_default_profile("volumes", profile_name)
    
    def get_app_volumes_from_profile(self, profile_name: str = None) -> dict:
        """Get the app_volumes dict from a volume profile."""
        profile = self.get_volume_profile_settings(profile_name)
        return profile.get("app_volumes", {})
