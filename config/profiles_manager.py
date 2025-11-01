"""
Profiles Manager for Overtone Application
Handles creation, loading, saving, and management of settings profiles
"""
import json
import os
from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class ProfilesManager:
    """Manages settings profiles with file persistence"""
    
    DEFAULT_PROFILE_NAME = "Default"
    PROFILES_FILE = "profiles.json"
    
    def __init__(self, profiles_file: str = None):
        self.profiles_file = profiles_file or self.PROFILES_FILE
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.active_profile_name: str = self.DEFAULT_PROFILE_NAME
        self.load_profiles()
    
    @staticmethod
    def _get_default_profile_settings() -> Dict[str, Any]:
        """Get default settings for a new profile"""
        from config.settings_manager import SettingsManager
        return SettingsManager._get_default_settings()
    
    def load_profiles(self) -> None:
        """Load profiles from file or create default profile"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    self.profiles = data.get("profiles", {})
                    self.active_profile_name = data.get("active_profile", self.DEFAULT_PROFILE_NAME)
                logger.info(f"Profiles loaded from {self.profiles_file}")
            except Exception as e:
                logger.error(f"Error loading profiles: {e}", exc_info=True)
                self._create_default_profile()
        else:
            logger.info("No profiles file found, creating default profile")
            self._create_default_profile()
        
        # Ensure default profile always exists and can't be deleted
        if self.DEFAULT_PROFILE_NAME not in self.profiles:
            self._create_default_profile()
        
        # Ensure active profile exists
        if self.active_profile_name not in self.profiles:
            self.active_profile_name = self.DEFAULT_PROFILE_NAME
        
        self.save_profiles()
    
    def _create_default_profile(self) -> None:
        """Create the default profile"""
        self.profiles[self.DEFAULT_PROFILE_NAME] = self._get_default_profile_settings()
        self.active_profile_name = self.DEFAULT_PROFILE_NAME
    
    def save_profiles(self) -> None:
        """Save all profiles to file"""
        try:
            from .ui_constants import UIConstants
            data = {
                "profiles": self.profiles,
                "active_profile": self.active_profile_name
            }
            with open(self.profiles_file, 'w') as f:
                json.dump(data, f, indent=UIConstants.JSON_INDENT)
            logger.debug(f"Profiles saved to {self.profiles_file}")
        except Exception as e:
            logger.error(f"Error saving profiles: {e}", exc_info=True)
    
    def get_profile_names(self) -> List[str]:
        """Get list of all profile names"""
        return list(self.profiles.keys())
    
    def get_active_profile_name(self) -> str:
        """Get the name of the active profile"""
        return self.active_profile_name
    
    def get_active_profile_settings(self) -> Dict[str, Any]:
        """Get settings from the active profile"""
        return self.profiles.get(self.active_profile_name, {}).copy()
    
    def get_profile_settings(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get settings from a specific profile"""
        return self.profiles.get(profile_name, {}).copy() if profile_name in self.profiles else None
    
    def create_profile(self, profile_name: str, base_on_current: bool = True) -> bool:
        """Create a new profile"""
        if profile_name in self.profiles or not profile_name or not profile_name.strip():
            logger.warning(f"Invalid profile name or profile '{profile_name}' already exists")
            return False
        
        self.profiles[profile_name] = self.get_active_profile_settings() if base_on_current else self._get_default_profile_settings()
        self.save_profiles()
        logger.info(f"Profile '{profile_name}' created")
        return True
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile (cannot delete default profile)"""
        if profile_name == self.DEFAULT_PROFILE_NAME or profile_name not in self.profiles:
            logger.warning(f"Cannot delete '{profile_name}' - default or doesn't exist")
            return False
        
        if profile_name == self.active_profile_name:
            self.active_profile_name = self.DEFAULT_PROFILE_NAME
        
        del self.profiles[profile_name]
        self.save_profiles()
        logger.info(f"Profile '{profile_name}' deleted")
        return True
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """Rename a profile (cannot rename default profile)"""
        if old_name == self.DEFAULT_PROFILE_NAME or old_name not in self.profiles or \
           new_name in self.profiles or not new_name or not new_name.strip():
            logger.warning(f"Cannot rename '{old_name}' to '{new_name}'")
            return False
        
        self.profiles[new_name] = self.profiles.pop(old_name)
        if self.active_profile_name == old_name:
            self.active_profile_name = new_name
        
        self.save_profiles()
        logger.info(f"Profile renamed from '{old_name}' to '{new_name}'")
        return True
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different profile"""
        if profile_name not in self.profiles:
            logger.warning(f"Profile '{profile_name}' does not exist")
            return False
        
        self.active_profile_name = profile_name
        self.save_profiles()
        logger.info(f"Switched to profile '{profile_name}'")
        return True
    
    def save_current_settings_to_profile(self, profile_name: str, settings: Dict[str, Any]) -> bool:
        """Save current settings to a specific profile"""
        if profile_name not in self.profiles:
            logger.warning(f"Profile '{profile_name}' does not exist")
            return False
        
        self.profiles[profile_name] = settings.copy()
        self.save_profiles()
        logger.info(f"Settings saved to profile '{profile_name}'")
        return True
    
    def is_default_profile(self, profile_name: str) -> bool:
        """Check if a profile is the default profile"""
        return profile_name == self.DEFAULT_PROFILE_NAME
