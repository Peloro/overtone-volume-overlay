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
            "hotkey_quit": Hotkeys.DEFAULT_HOTKEY_QUIT,
            "confirm_on_quit": True
        }
    
    def load_settings(self) -> None:
        """Load settings from file or use defaults"""
        self.settings = self._default_settings.copy()
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings.update(json.load(f))
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        self._validate_settings()
        self.save_settings()
    
    def _clamp_value(self, key: str, min_val, max_val, default) -> Any:
        """Clamp a setting value between min and max"""
        return max(min_val, min(max_val, self.settings.get(key, default)))
    
    def _validate_settings(self) -> None:
        """Validate and clamp settings to acceptable ranges"""
        self.settings["overlay_width"] = self._clamp_value(
            "overlay_width", UIConstants.MIN_OVERLAY_WIDTH, 
            UIConstants.MAX_OVERLAY_WIDTH, UIConstants.DEFAULT_OVERLAY_WIDTH
        )
        self.settings["overlay_height"] = self._clamp_value(
            "overlay_height", UIConstants.MIN_OVERLAY_HEIGHT,
            UIConstants.MAX_OVERLAY_HEIGHT, UIConstants.DEFAULT_OVERLAY_HEIGHT
        )
        self.settings["overlay_opacity"] = self._clamp_value(
            "overlay_opacity", UIConstants.MIN_OPACITY,
            UIConstants.MAX_OPACITY, UIConstants.DEFAULT_OPACITY
        )
        
        for key, default in [
            ("hotkey_open", Hotkeys.DEFAULT_HOTKEY_OPEN),
            ("hotkey_settings", Hotkeys.DEFAULT_HOTKEY_SETTINGS),
            ("hotkey_quit", Hotkeys.DEFAULT_HOTKEY_QUIT),
            ("confirm_on_quit", True)
        ]:
            self.settings.setdefault(key, default)
    
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
    
    @property
    def confirm_on_quit(self) -> bool:
        return self.settings.get("confirm_on_quit", True)
