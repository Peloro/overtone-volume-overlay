import json
import os
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseProfilesManager(ABC):
    """Base class for profile managers - handles common profile operations."""
    
    DEFAULT_PROFILE_NAME = "Default"
    
    def __init__(self, profiles_file: str, profile_type: str):
        self.profiles_file = profiles_file
        self.profile_type = profile_type  # For logging purposes
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.active_profile_name: str = self.DEFAULT_PROFILE_NAME
        self.load_profiles()
    
    @staticmethod
    @abstractmethod
    def _get_default_profile_settings() -> Dict[str, Any]:
        """Get default settings for this profile type. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_valid_keys(self) -> List[str]:
        """Get the list of valid keys for this profile type. Must be implemented by subclasses."""
        pass
    
    def load_profiles(self) -> None:
        """Load profiles from file."""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    self.profiles = data.get("profiles", {})
                    self.active_profile_name = data.get("active_profile", self.DEFAULT_PROFILE_NAME)
                logger.info(f"{self.profile_type} profiles loaded from {self.profiles_file}")
            except Exception as e:
                logger.error(f"Error loading {self.profile_type} profiles: {e}", exc_info=True)
                self._create_default_profile()
        else:
            logger.info(f"No {self.profile_type} profiles file found, creating default profile")
            self._create_default_profile()
        
        if self.DEFAULT_PROFILE_NAME not in self.profiles:
            self._create_default_profile()
        
        if self.active_profile_name not in self.profiles:
            self.active_profile_name = self.DEFAULT_PROFILE_NAME
        
        self.save_profiles()
    
    def _create_default_profile(self) -> None:
        """Create the default profile."""
        self.profiles[self.DEFAULT_PROFILE_NAME] = self._get_default_profile_settings()
        self.active_profile_name = self.DEFAULT_PROFILE_NAME
    
    def save_profiles(self) -> None:
        """Save profiles to file."""
        try:
            from .ui_constants import UIConstants
            data = {
                "profiles": self.profiles,
                "active_profile": self.active_profile_name
            }
            with open(self.profiles_file, 'w') as f:
                json.dump(data, f, indent=UIConstants.JSON_INDENT)
            logger.debug(f"{self.profile_type} profiles saved to {self.profiles_file}")
        except Exception as e:
            logger.error(f"Error saving {self.profile_type} profiles: {e}", exc_info=True)
    
    def get_profile_names(self) -> List[str]:
        """Get list of all profile names."""
        return list(self.profiles.keys())
    
    def get_active_profile_name(self) -> str:
        """Get the active profile name."""
        return self.active_profile_name
    
    def get_active_profile_settings(self) -> Dict[str, Any]:
        """Get settings from the active profile."""
        return self.profiles.get(self.active_profile_name, {}).copy()
    
    def get_profile_settings(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get settings from a specific profile."""
        return self.profiles.get(profile_name, {}).copy() if profile_name in self.profiles else None
    
    def create_profile(self, profile_name: str, base_on_current: bool = True) -> bool:
        """Create a new profile."""
        if profile_name in self.profiles or not profile_name or not profile_name.strip():
            logger.warning(f"Invalid profile name or {self.profile_type} profile '{profile_name}' already exists")
            return False
        
        self.profiles[profile_name] = self.get_active_profile_settings() if base_on_current else self._get_default_profile_settings()
        self.save_profiles()
        logger.info(f"{self.profile_type} profile '{profile_name}' created")
        return True
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile."""
        if profile_name == self.DEFAULT_PROFILE_NAME or profile_name not in self.profiles:
            logger.warning(f"Cannot delete {self.profile_type} profile '{profile_name}' - default or doesn't exist")
            return False
        
        if profile_name == self.active_profile_name:
            self.active_profile_name = self.DEFAULT_PROFILE_NAME
        
        del self.profiles[profile_name]
        self.save_profiles()
        logger.info(f"{self.profile_type} profile '{profile_name}' deleted")
        return True
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """Rename a profile."""
        if old_name == self.DEFAULT_PROFILE_NAME or old_name not in self.profiles or \
           new_name in self.profiles or not new_name or not new_name.strip():
            logger.warning(f"Cannot rename {self.profile_type} profile '{old_name}' to '{new_name}'")
            return False
        
        self.profiles[new_name] = self.profiles.pop(old_name)
        if self.active_profile_name == old_name:
            self.active_profile_name = new_name
        
        self.save_profiles()
        logger.info(f"{self.profile_type} profile renamed from '{old_name}' to '{new_name}'")
        return True
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different profile."""
        if profile_name not in self.profiles:
            logger.warning(f"{self.profile_type} profile '{profile_name}' does not exist")
            return False
        
        self.active_profile_name = profile_name
        self.save_profiles()
        logger.info(f"Switched to {self.profile_type} profile '{profile_name}'")
        return True
    
    def save_current_settings_to_profile(self, profile_name: str, settings: Dict[str, Any]) -> bool:
        """Save settings to a profile, filtering by valid keys."""
        if profile_name not in self.profiles:
            logger.warning(f"{self.profile_type} profile '{profile_name}' does not exist")
            return False
        
        valid_keys = self.get_valid_keys()
        filtered_settings = {k: v for k, v in settings.items() if k in valid_keys}
        self.profiles[profile_name] = filtered_settings
        self.save_profiles()
        logger.info(f"{self.profile_type} settings saved to profile '{profile_name}'")
        return True
    
    def is_default_profile(self, profile_name: str) -> bool:
        """Check if a profile is the default profile."""
        return profile_name == self.DEFAULT_PROFILE_NAME


class SettingsProfilesManager(BaseProfilesManager):
    """Manager for settings profiles - handles application settings separately from colors."""
    
    PROFILES_FILE = "settings_profiles.json"
    SETTINGS_KEYS = [
        "overlay_width",
        "overlay_height",
        "overlay_opacity",
        "hotkey_open",
        "hotkey_settings",
        "hotkey_quit",
        "confirm_on_quit",
        "show_system_volume",
        "always_show_filter",
    ]
    
    def __init__(self, profiles_file: str = None):
        super().__init__(profiles_file or self.PROFILES_FILE, "Settings")
    
    @staticmethod
    def _get_default_profile_settings() -> Dict[str, Any]:
        """Get default settings."""
        from .ui_constants import UIConstants, Hotkeys
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
    
    def get_valid_keys(self) -> List[str]:
        return self.SETTINGS_KEYS


class ColorProfilesManager(BaseProfilesManager):
    """Manager for color profiles - handles color scheme configurations separately from settings."""
    
    PROFILES_FILE = "color_profiles.json"
    COLOR_KEYS = [
        "color_main_background",
        "color_title_bar_bg",
        "color_master_frame_bg",
        "color_container_bg",
        "color_app_control_bg",
        "color_master_slider_handle",
        "color_app_slider_handle",
        "color_primary_button_bg",
        "color_close_button_bg",
        "color_text_white",
    ]
    
    def __init__(self, profiles_file: str = None):
        super().__init__(profiles_file or self.PROFILES_FILE, "Color")
    
    @staticmethod
    def _get_default_profile_settings() -> Dict[str, Any]:
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
    
    def get_valid_keys(self) -> List[str]:
        return self.COLOR_KEYS
