"""
Settings Manager for Overtone Application
Handles loading, saving, and managing application settings
"""
import json
import os
from typing import Dict, Any
from .constants import UIConstants, Hotkeys


class SettingsManager:
    """Manages application settings with file persistence"""
    
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.settings: Dict[str, Any] = {}
        self._default_settings = self._get_default_settings()
        self.load_settings()
    
    @staticmethod
    def _get_default_settings() -> Dict[str, Any]:
        """Get default settings"""
        return {
            "overlay_width": UIConstants.DEFAULT_OVERLAY_WIDTH,
            "overlay_height": UIConstants.DEFAULT_OVERLAY_HEIGHT,
            "overlay_opacity": UIConstants.DEFAULT_OPACITY,
            "hotkey_open": Hotkeys.DEFAULT_HOTKEY_OPEN,
            "hotkey_settings": Hotkeys.DEFAULT_HOTKEY_SETTINGS,
            "hotkey_quit": Hotkeys.DEFAULT_HOTKEY_QUIT
        }
    
    def load_settings(self) -> None:
        """Load settings from file or use defaults"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                
                self.settings = self._default_settings.copy()
                self.settings.update(loaded_settings)
                
                self._validate_settings()
                
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = self._default_settings.copy()
        else:
            self.settings = self._default_settings.copy()
        
        self.save_settings()
    
    def _validate_settings(self) -> None:
        """Validate and clamp settings to acceptable ranges"""
        self.settings["overlay_width"] = max(
            UIConstants.MIN_OVERLAY_WIDTH,
            min(UIConstants.MAX_OVERLAY_WIDTH, self.settings.get("overlay_width", UIConstants.DEFAULT_OVERLAY_WIDTH))
        )
        self.settings["overlay_height"] = max(
            UIConstants.MIN_OVERLAY_HEIGHT,
            min(UIConstants.MAX_OVERLAY_HEIGHT, self.settings.get("overlay_height", UIConstants.DEFAULT_OVERLAY_HEIGHT))
        )
        
        self.settings["overlay_opacity"] = max(
            UIConstants.MIN_OPACITY,
            min(UIConstants.MAX_OPACITY, self.settings.get("overlay_opacity", UIConstants.DEFAULT_OPACITY))
        )
        
        if "hotkey_open" not in self.settings:
            self.settings["hotkey_open"] = Hotkeys.DEFAULT_HOTKEY_OPEN
        if "hotkey_settings" not in self.settings:
            self.settings["hotkey_settings"] = Hotkeys.DEFAULT_HOTKEY_SETTINGS
        if "hotkey_quit" not in self.settings:
            self.settings["hotkey_quit"] = Hotkeys.DEFAULT_HOTKEY_QUIT
    
    def save_settings(self) -> None:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value"""
        self.settings[key] = value
    
    def update(self, new_settings: Dict[str, Any]) -> None:
        """Update multiple settings at once"""
        self.settings.update(new_settings)
        self._validate_settings()
        self.save_settings()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.settings = self._default_settings.copy()
        self.save_settings()
    
    @property
    def overlay_width(self) -> int:
        return self.settings["overlay_width"]
    
    @property
    def overlay_height(self) -> int:
        return self.settings["overlay_height"]
    
    @property
    def overlay_opacity(self) -> float:
        return self.settings["overlay_opacity"]
    
    @property
    def hotkey_open(self) -> str:
        return self.settings["hotkey_open"]
    
    @property
    def hotkey_settings(self) -> str:
        return self.settings["hotkey_settings"]
    
    @property
    def hotkey_quit(self) -> str:
        return self.settings["hotkey_quit"]
