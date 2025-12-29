"""
Centralized default values for settings and colors.
This module is the single source of truth for all default configurations.
"""
from typing import Dict, Any


def get_default_settings() -> Dict[str, Any]:
    """Get default non-color settings."""
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


def get_default_colors() -> Dict[str, Any]:
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


# Keys for filtering settings vs colors
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


def get_default_volume_profile() -> dict:
    """Get default volume profile settings.
    
    Volume profiles store per-application volume levels.
    Format: {"app_name": volume_percentage, ...}
    Example: {"firefox": 50, "discord": 80, "spotify": 100}
    """
    return {
        "app_volumes": {}  # Empty by default, users will add their apps
    }


# Volume profile uses dynamic keys (app names), so we just track the wrapper key
VOLUME_PROFILE_KEYS = ["app_volumes"]
