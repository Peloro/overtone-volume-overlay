"""
Unified Profiles Manager - stores both settings and color profiles in a single file
with separate sections to keep them organized.

File structure (profiles.json):
{
    "settings": {
        "active_profile": "Default",
        "profiles": { ... }
    },
    "colors": {
        "active_profile": "Default", 
        "profiles": { ... }
    }
}
"""
import json
import os
from typing import Dict, Any, List
from utils import get_logger

logger = get_logger(__name__)

PROFILES_FILE = "profiles.json"
DEFAULT_PROFILE_NAME = "Default"


class UnifiedProfilesManager:
    """Manages both settings and color profiles in a single file."""
    
    SETTINGS_KEYS = [
        "overlay_width", "overlay_height", "overlay_opacity",
        "hotkey_open", "hotkey_settings", "hotkey_quit",
        "confirm_on_quit", "show_system_volume", "always_show_filter",
    ]
    
    COLOR_KEYS = [
        "color_main_background", "color_title_bar_bg", "color_master_frame_bg",
        "color_container_bg", "color_app_control_bg", "color_master_slider_handle",
        "color_app_slider_handle", "color_primary_button_bg", "color_close_button_bg",
        "color_text_white",
    ]
    
    def __init__(self, profiles_file: str = None):
        self.profiles_file = profiles_file or PROFILES_FILE
        self.data = {"settings": {}, "colors": {}}
        self._load()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        from .constants import UIConstants, Hotkeys
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
    
    def _get_default_colors(self) -> Dict[str, Any]:
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
    
    def _load(self) -> None:
        """Load profiles from file."""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    self.data = json.load(f)
                logger.info(f"Profiles loaded from {self.profiles_file}")
            except Exception as e:
                logger.error(f"Error loading profiles: {e}", exc_info=True)
                self.data = {"settings": {}, "colors": {}}
        else:
            self.data = {"settings": {}, "colors": {}}
        
        # Ensure structure exists
        self._ensure_defaults("settings", self._get_default_settings)
        self._ensure_defaults("colors", self._get_default_colors)
        self._save()
    
    def _ensure_defaults(self, section: str, get_defaults) -> None:
        """Ensure a section has proper structure and default profile."""
        if section not in self.data or not isinstance(self.data[section], dict):
            self.data[section] = {}
        
        if "profiles" not in self.data[section]:
            self.data[section]["profiles"] = {}
        
        if "active_profile" not in self.data[section]:
            self.data[section]["active_profile"] = DEFAULT_PROFILE_NAME
        
        if DEFAULT_PROFILE_NAME not in self.data[section]["profiles"]:
            self.data[section]["profiles"][DEFAULT_PROFILE_NAME] = get_defaults()
        
        if self.data[section]["active_profile"] not in self.data[section]["profiles"]:
            self.data[section]["active_profile"] = DEFAULT_PROFILE_NAME
    
    def _save(self) -> None:
        """Save all profiles to file."""
        try:
            from .constants import UIConstants
            with open(self.profiles_file, 'w') as f:
                json.dump(self.data, f, indent=UIConstants.JSON_INDENT)
            logger.debug("Profiles saved")
        except Exception as e:
            logger.error(f"Error saving profiles: {e}", exc_info=True)
    
    # ========== Generic Profile Operations ==========
    
    def _get_section(self, profile_type: str) -> Dict:
        return self.data["settings" if profile_type == "settings" else "colors"]
    
    def _get_valid_keys(self, profile_type: str) -> List[str]:
        return self.SETTINGS_KEYS if profile_type == "settings" else self.COLOR_KEYS
    
    def _get_defaults(self, profile_type: str) -> Dict[str, Any]:
        return self._get_default_settings() if profile_type == "settings" else self._get_default_colors()
    
    def get_profile_names(self, profile_type: str) -> List[str]:
        return list(self._get_section(profile_type)["profiles"].keys())
    
    def get_active_profile_name(self, profile_type: str) -> str:
        return self._get_section(profile_type)["active_profile"]
    
    def get_active_profile_settings(self, profile_type: str) -> Dict[str, Any]:
        section = self._get_section(profile_type)
        return section["profiles"].get(section["active_profile"], {}).copy()
    
    def create_profile(self, profile_type: str, profile_name: str, base_on_current: bool = True) -> bool:
        section = self._get_section(profile_type)
        if profile_name in section["profiles"] or not profile_name or not profile_name.strip():
            return False
        
        if base_on_current:
            section["profiles"][profile_name] = self.get_active_profile_settings(profile_type)
        else:
            section["profiles"][profile_name] = self._get_defaults(profile_type)
        
        self._save()
        logger.info(f"{profile_type} profile '{profile_name}' created")
        return True
    
    def delete_profile(self, profile_type: str, profile_name: str) -> bool:
        section = self._get_section(profile_type)
        if profile_name == DEFAULT_PROFILE_NAME or profile_name not in section["profiles"]:
            return False
        
        if section["active_profile"] == profile_name:
            section["active_profile"] = DEFAULT_PROFILE_NAME
        
        del section["profiles"][profile_name]
        self._save()
        logger.info(f"{profile_type} profile '{profile_name}' deleted")
        return True
    
    def rename_profile(self, profile_type: str, old_name: str, new_name: str) -> bool:
        section = self._get_section(profile_type)
        if old_name == DEFAULT_PROFILE_NAME or old_name not in section["profiles"] or \
           new_name in section["profiles"] or not new_name or not new_name.strip():
            return False
        
        section["profiles"][new_name] = section["profiles"].pop(old_name)
        if section["active_profile"] == old_name:
            section["active_profile"] = new_name
        
        self._save()
        logger.info(f"{profile_type} profile renamed from '{old_name}' to '{new_name}'")
        return True
    
    def switch_profile(self, profile_type: str, profile_name: str) -> bool:
        section = self._get_section(profile_type)
        if profile_name not in section["profiles"]:
            return False
        
        section["active_profile"] = profile_name
        self._save()
        logger.info(f"Switched to {profile_type} profile '{profile_name}'")
        return True
    
    def save_to_profile(self, profile_type: str, profile_name: str, settings: Dict[str, Any]) -> bool:
        section = self._get_section(profile_type)
        if profile_name not in section["profiles"]:
            return False
        
        valid_keys = self._get_valid_keys(profile_type)
        section["profiles"][profile_name] = {k: v for k, v in settings.items() if k in valid_keys}
        self._save()
        return True
    
    def is_default_profile(self, profile_name: str) -> bool:
        return profile_name == DEFAULT_PROFILE_NAME


# ========== Wrapper Classes for Backwards Compatibility ==========

class SettingsProfilesManager:
    """Wrapper for settings profiles - maintains API compatibility."""
    
    _shared_manager: UnifiedProfilesManager = None
    
    def __init__(self, profiles_file: str = None):
        if SettingsProfilesManager._shared_manager is None:
            SettingsProfilesManager._shared_manager = UnifiedProfilesManager(profiles_file)
        self._manager = SettingsProfilesManager._shared_manager
    
    def get_profile_names(self) -> List[str]:
        return self._manager.get_profile_names("settings")
    
    def get_active_profile_name(self) -> str:
        return self._manager.get_active_profile_name("settings")
    
    def get_active_profile_settings(self) -> Dict[str, Any]:
        return self._manager.get_active_profile_settings("settings")
    
    def create_profile(self, name: str, base_on_current: bool = True) -> bool:
        return self._manager.create_profile("settings", name, base_on_current)
    
    def delete_profile(self, name: str) -> bool:
        return self._manager.delete_profile("settings", name)
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        return self._manager.rename_profile("settings", old_name, new_name)
    
    def switch_profile(self, name: str) -> bool:
        return self._manager.switch_profile("settings", name)
    
    def save_current_settings_to_profile(self, name: str, settings: Dict[str, Any]) -> bool:
        return self._manager.save_to_profile("settings", name, settings)
    
    def is_default_profile(self, name: str) -> bool:
        return self._manager.is_default_profile(name)


class ColorProfilesManager:
    """Wrapper for color profiles - maintains API compatibility."""
    
    def __init__(self, profiles_file: str = None):
        # Share the same manager instance
        if SettingsProfilesManager._shared_manager is None:
            SettingsProfilesManager._shared_manager = UnifiedProfilesManager(profiles_file)
        self._manager = SettingsProfilesManager._shared_manager
    
    def get_profile_names(self) -> List[str]:
        return self._manager.get_profile_names("colors")
    
    def get_active_profile_name(self) -> str:
        return self._manager.get_active_profile_name("colors")
    
    def get_active_profile_settings(self) -> Dict[str, Any]:
        return self._manager.get_active_profile_settings("colors")
    
    def create_profile(self, name: str, base_on_current: bool = True) -> bool:
        return self._manager.create_profile("colors", name, base_on_current)
    
    def delete_profile(self, name: str) -> bool:
        return self._manager.delete_profile("colors", name)
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        return self._manager.rename_profile("colors", old_name, new_name)
    
    def switch_profile(self, name: str) -> bool:
        return self._manager.switch_profile("colors", name)
    
    def save_current_settings_to_profile(self, name: str, settings: Dict[str, Any]) -> bool:
        return self._manager.save_to_profile("colors", name, settings)
    
    def is_default_profile(self, name: str) -> bool:
        return self._manager.is_default_profile(name)


# For backwards compatibility
BaseProfilesManager = UnifiedProfilesManager
