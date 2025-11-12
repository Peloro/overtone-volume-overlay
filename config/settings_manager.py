import json
import os
from typing import Dict, Any
from PyQt5.QtCore import QTimer
from .ui_constants import UIConstants, Hotkeys
from .profiles_manager import ProfilesManager
from utils.logger import get_logger

logger = get_logger(__name__)


class SettingsManager:
    
    def __init__(self):
        self.settings: Dict[str, Any] = {}
        self._default_settings = self._get_default_settings()
        self._save_timer: QTimer = None
        self._save_debounce_ms = UIConstants.SETTINGS_SAVE_DEBOUNCE_MS
        self.profiles_manager = ProfilesManager()
        self.load_settings()
    
    def _setup_save_timer(self) -> None:
        if self._save_timer is None:
            self._save_timer = QTimer()
            self._save_timer.setSingleShot(True)
            self._save_timer.timeout.connect(self._do_save_settings)
    
    @staticmethod
    def _get_default_settings() -> Dict[str, Any]:
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
        profile_settings = self.profiles_manager.get_active_profile_settings()
        self.settings = self._default_settings.copy()
        self.settings.update(profile_settings)
        
        logger.info(f"Settings loaded from profile '{self.profiles_manager.get_active_profile_name()}'")
        
        self._validate_settings()
        self._setup_save_timer()
    
    def _do_save_settings(self) -> None:
        try:
            active_profile = self.profiles_manager.get_active_profile_name()
            self.profiles_manager.save_current_settings_to_profile(active_profile, self.settings)
            logger.debug(f"Settings saved to profile '{active_profile}'")
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
        self.save_settings(debounce=False)
    
    def __getattr__(self, name):
        if name in self.settings:
            return self.settings[name]
        if name in self._default_settings:
            return self._default_settings[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def get_active_profile_name(self) -> str:
        return self.profiles_manager.get_active_profile_name()
    
    def get_profile_names(self) -> list:
        return self.profiles_manager.get_profile_names()
    
    def switch_profile(self, profile_name: str) -> bool:
        if self.profiles_manager.switch_profile(profile_name):
            self.load_settings()
            return True
        return False
    
    def create_profile(self, profile_name: str, base_on_current: bool = True) -> bool:
        return self.profiles_manager.create_profile(profile_name, base_on_current)
    
    def delete_profile(self, profile_name: str) -> bool:
        was_active = profile_name == self.profiles_manager.get_active_profile_name()
        result = self.profiles_manager.delete_profile(profile_name)
        if result and was_active:
            self.load_settings()
        return result
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        return self.profiles_manager.rename_profile(old_name, new_name)
    
    def save_to_profile(self, profile_name: str) -> bool:
        return self.profiles_manager.save_current_settings_to_profile(profile_name, self.settings)
    
    def is_default_profile(self, profile_name: str) -> bool:
        return self.profiles_manager.is_default_profile(profile_name)
