"""
Centralized configuration for the Overtone application.
Contains constants, colors, defaults, and styles.
"""
from typing import Dict, Any


# =============================================================================
# APP INFO
# =============================================================================

class AppInfo:
    APP_NAME = "Overtone"
    VERSION = "0.5"
    DESCRIPTION = "A modern, lightweight volume mixer overlay for Windows with per-application volume control. If you like the " \
    "project, feel free to star and watch the repository on GitHub!"
    AUTHOR = "Peloro"
    GITHUB_URL = "https://github.com/Peloro"
    REPO_URL = "https://github.com/Peloro/overtone-volume-overlay"
    LICENSE = "MIT License"
    YEAR = "2025"
    ICON_FILE = "icon2_black.ico"


# =============================================================================
# UI CONSTANTS
# =============================================================================

class UIConstants:
    DEFAULT_OVERLAY_WIDTH = 300
    DEFAULT_OVERLAY_HEIGHT = 350
    MIN_OVERLAY_WIDTH = 300
    MIN_OVERLAY_HEIGHT = 350
    MAX_OVERLAY_WIDTH = 1000
    MAX_OVERLAY_HEIGHT = 1000
    
    APP_CONTROL_HEIGHT = 68
    TITLE_BAR_HEIGHT = 50
    MASTER_VOLUME_HEIGHT = 80
    FILTER_BAR_HEIGHT = 35
    PAGINATION_HEIGHT = 30
    WINDOW_MARGINS = 40
    RESERVED_HEIGHT = 235
    
    BUTTON_SIZE = 30
    BUTTON_HEIGHT = 24
    VOLUME_TEXT_WIDTH = 40
    
    REFRESH_INTERVAL = 5000
    FILTER_DEBOUNCE_MS = 150
    ERROR_FLASH_DURATION_MS = 300
    NAME_CACHE_TTL_SECONDS = 30.0
    
    DEFAULT_OPACITY = 0.95
    MIN_OPACITY = 0.1
    MAX_OPACITY = 1.0
    
    TITLE_FONT_SIZE = 14
    LABEL_FONT_SIZE = 11
    BUTTON_FONT_SIZE = 16
    CLOSE_BUTTON_FONT_SIZE = 20
    ICON_FONT_SIZE = 14
    
    LAYOUT_MARGIN = 10
    LAYOUT_SPACING = 5
    FRAME_MARGIN = 5
    FRAME_SPACING = 3
    CONTROL_SPACING = 5
    
    WINDOW_RADIUS = 10
    FRAME_RADIUS = 5
    BUTTON_RADIUS = 15
    SMALL_BUTTON_RADIUS = 3
    SLIDER_RADIUS = 3
    HANDLE_RADIUS = 7
    
    MIN_CONTROL_WIDTH = 200
    MIN_SLIDER_WIDTH = 80
    
    VOLUME_PERCENTAGE_FACTOR = 100
    
    ICON_SIZE_16 = 16
    ICON_SIZE_24 = 24
    ICON_SIZE_32 = 32
    ICON_SIZE_48 = 48
    FALLBACK_ICON_SIZE = 32
    
    TEXT_ELIDE_WIDTH = 280
    
    QUIT_DELAY_MS = 100
    RESIZE_DEBOUNCE_MS = 100
    
    SETTINGS_SAVE_DEBOUNCE_MS = 500
    OPACITY_DECIMAL_PLACES = 2
    
    LOG_MAX_BYTES = 5 * 1024 * 1024
    LOG_BACKUP_COUNT = 3
    
    JSON_INDENT = 4
    
    MAX_CACHE_SIZE = 100
    CACHE_CLEANUP_BATCH_SIZE = 20
    
    MARGIN_SIDES_COUNT = 4
    RGBA_COMPONENT_COUNT = 4
    
    SETTINGS_MIN_WIDTH = 450
    COLOR_BUTTON_MIN_HEIGHT = 30
    COLOR_BUTTON_MIN_WIDTH = 90
    COLOR_BUTTON_FONT_SIZE = 8
    
    WHEEL_SCROLL_DELTA = 5
    PAGINATION_LABEL_PADDING_H = 10
    FILTER_INPUT_PADDING_V = 5
    FILTER_INPUT_PADDING_H = 8
    
    SLIDER_HEIGHT = 20
    SLIDER_HANDLE_WIDTH = 14
    SLIDER_HANDLE_HEIGHT = 14
    SLIDER_HANDLE_MARGIN_OFFSET = -7
    SLIDER_GROOVE_HEIGHT = 6
    SLIDER_GROOVE_MARGIN = 7
    SLIDER_GROOVE_MARGIN_ZERO = 0
    
    MASTER_SLIDER_BORDER_WIDTH = 2
    MASTER_SLIDER_MARGIN = -5
    APP_SLIDER_BORDER_WIDTH = 1
    APP_SLIDER_MARGIN = -4
    
    OPACITY_STEP = 0.05
    
    STANDARD_BORDER_WIDTH = 1
    THICK_BORDER_WIDTH = 2
    
    STANDARD_PADDING = 3
    SMALL_PADDING = 2
    MEDIUM_PADDING = 5
    LARGE_PADDING = 8
    XLARGE_PADDING = 10
    BUTTON_PADDING_H = 15
    TAB_PADDING_H = 20
    
    CLEAR_BUTTON_FONT_SIZE = 16
    SETTINGS_ABOUT_TITLE_FONT_SIZE = 12
    SETTINGS_ABOUT_DESCRIPTION_FONT_SIZE = 12
    SETTINGS_ABOUT_FOOTER_FONT_SIZE = 11
    SETTINGS_INFO_FONT_SIZE = 10
    
    STRETCH_FACTOR_NONE = 0
    STRETCH_FACTOR_STANDARD = 1
    
    WINDOW_START_X = 0
    WINDOW_START_Y = 0
    
    SETTINGS_MARGIN_STANDARD = 10
    SETTINGS_MARGIN_TOP = 10
    SETTINGS_MARGIN_TOP_LARGE = 15
    SETTINGS_PADDING_SMALL = 5
    SETTINGS_PADDING_STANDARD = 8
    
    TAB_MARGIN_RIGHT = 2
    
    GROUP_BOX_BORDER_WIDTH = 2
    GROUP_BOX_MARGIN_TOP = 10
    GROUP_BOX_PADDING_TOP = 10
    GROUP_BOX_TITLE_LEFT = 10
    GROUP_BOX_TITLE_PADDING = 5
    
    ALPHA_CHANNEL_MAX = 255


# =============================================================================
# HOTKEYS
# =============================================================================

class Hotkeys:
    DEFAULT_HOTKEY_OPEN = "ctrl+/"
    DEFAULT_HOTKEY_SETTINGS = "ctrl+shift+s"
    DEFAULT_HOTKEY_QUIT = "ctrl+q"


# =============================================================================
# DEFAULTS
# =============================================================================

def get_default_settings() -> Dict[str, Any]:
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


# =============================================================================
# COLORS
# =============================================================================

def _build_defaults_dict():
    """Build the _DEFAULTS dict from centralized defaults."""
    defaults = get_default_colors()
    return {
        "MAIN_BACKGROUND": defaults["color_main_background"],
        "TITLE_BAR_BG": defaults["color_title_bar_bg"],
        "MASTER_FRAME_BG": defaults["color_master_frame_bg"],
        "CONTAINER_BG": defaults["color_container_bg"],
        "APP_CONTROL_BG": defaults["color_app_control_bg"],
        "MASTER_SLIDER_HANDLE": defaults["color_master_slider_handle"],
        "APP_SLIDER_HANDLE": defaults["color_app_slider_handle"],
        "PRIMARY_BUTTON_BG": defaults["color_primary_button_bg"],
        "CLOSE_BUTTON_BG": defaults["color_close_button_bg"],
        "TEXT_WHITE": defaults["color_text_white"],
    }


class ColorsMeta(type):
    def __getattribute__(cls, name):
        customizable = {
            "MAIN_BACKGROUND", "TITLE_BAR_BG", "MASTER_FRAME_BG", 
            "CONTAINER_BG", "APP_CONTROL_BG", "MASTER_SLIDER_HANDLE",
            "APP_SLIDER_HANDLE", "PRIMARY_BUTTON_BG", "CLOSE_BUTTON_BG",
            "TEXT_WHITE"
        }
        
        if name in customizable:
            defaults = super().__getattribute__("_DEFAULTS")
            settings_mgr = super().__getattribute__("_settings_manager")
            
            if settings_mgr:
                setting_key = f"color_{name.lower()}"
                return settings_mgr.get(setting_key, defaults[name])
            return defaults[name]
        
        return super().__getattribute__(name)


class Colors(metaclass=ColorsMeta):
    _settings_manager = None
    _DEFAULTS = _build_defaults_dict()
    
    DIALOG_BG = "#2b2b2b"
    INPUT_BG = "#424242"
    DARK_INPUT_BG = "#1a2332"
    
    SETTINGS_BUTTON_BG = "#455a64"
    SETTINGS_BUTTON_HOVER = "#607d8b"
    MINIMIZE_BUTTON_BG = "#757575"
    MINIMIZE_BUTTON_HOVER = "#9e9e9e"
    CLOSE_BUTTON_HOVER = "#f44336"
    PRIMARY_BUTTON_HOVER = "#42a5f5"
    SECONDARY_BUTTON_BG = "#424242"
    SECONDARY_BUTTON_HOVER = "#555"
    DISABLED_BUTTON_BG = "#2a2a2a"
    
    MASTER_SLIDER_HANDLE_BORDER = "#2e7d32"
    MASTER_SLIDER_HANDLE_HOVER = "#66bb6a"
    APP_SLIDER_HANDLE_BORDER = "#1565c0"
    APP_SLIDER_HANDLE_HOVER = "#42a5f5"
    SLIDER_GROOVE_BG = "#555"
    SLIDER_GROOVE_BORDER = "#999"
    
    BORDER_COLOR = "#666"
    PRIMARY_BORDER = "#4caf50"
    GROUP_BORDER = "#555"
    SEPARATOR_COLOR = "#555"
    
    TEXT_GRAY = "gray"
    TEXT_LIGHT_GRAY = "#aaa"
    TEXT_DISABLED = "#555"
    
    @classmethod
    def set_settings_manager(cls, settings_manager):
        cls._settings_manager = settings_manager


# =============================================================================
# STYLESHEETS
# =============================================================================

class StyleSheets:
    
    @staticmethod
    def get_frame_stylesheet(bg_color: str = None, border_radius: int = None, padding: int = None) -> str:
        if bg_color is None:
            bg_color = Colors.CONTAINER_BG
        if border_radius is None:
            border_radius = UIConstants.FRAME_RADIUS
        if padding is None:
            padding = UIConstants.FRAME_MARGIN
        
        return f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: {border_radius}px;
                padding: {padding}px;
            }}
        """
    
    @staticmethod
    def get_overlay_stylesheet() -> str:
        return f"""
            QWidget#VolumeOverlay {{
                background-color: rgba(30, 30, 30, 255);
                border-radius: {UIConstants.WINDOW_RADIUS}px;
            }}
            QLabel {{ color: {Colors.TEXT_WHITE}; }}
        """
    
    @staticmethod
    def get_title_label_stylesheet() -> str:
        return f"""
            color: {Colors.TEXT_WHITE};
            font-weight: bold;
            font-size: {UIConstants.TITLE_FONT_SIZE}px;
        """
    
    @staticmethod
    def get_label_stylesheet() -> str:
        return f"""
            QLabel {{
                color: {Colors.TEXT_WHITE};
                font-size: {UIConstants.LABEL_FONT_SIZE}px;
                font-weight: bold;
                padding: {UIConstants.SMALL_PADDING}px;
            }}
        """
    
    @staticmethod
    def _get_button_stylesheet(bg_color: str, hover_color: str, font_size: int = None, bold: bool = False) -> str:
        font_size = font_size or UIConstants.BUTTON_FONT_SIZE
        weight = "font-weight: bold;" if bold else ""
        return f"""
            QPushButton {{
                background-color: {bg_color}; color: {Colors.TEXT_WHITE};
                border: none; border-radius: {UIConstants.BUTTON_RADIUS}px;
                font-size: {font_size}px; {weight}
            }}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """
    
    @staticmethod
    def get_settings_button_stylesheet() -> str:
        return StyleSheets._get_button_stylesheet(Colors.SETTINGS_BUTTON_BG, Colors.SETTINGS_BUTTON_HOVER)
    
    @staticmethod
    def get_minimize_button_stylesheet() -> str:
        return StyleSheets._get_button_stylesheet(Colors.MINIMIZE_BUTTON_BG, Colors.MINIMIZE_BUTTON_HOVER, 
                                                   UIConstants.CLOSE_BUTTON_FONT_SIZE, True)
    
    @staticmethod
    def get_close_button_stylesheet() -> str:
        return StyleSheets._get_button_stylesheet(Colors.CLOSE_BUTTON_BG, Colors.CLOSE_BUTTON_HOVER, 
                                                   UIConstants.CLOSE_BUTTON_FONT_SIZE, True)
    
    @staticmethod
    def _get_slider_stylesheet(handle_color: str, border_color: str, hover_color: str, 
                               border_width: int = None, margin: int = None) -> str:
        if border_width is None:
            border_width = UIConstants.APP_SLIDER_BORDER_WIDTH
        if margin is None:
            margin = UIConstants.APP_SLIDER_MARGIN
            
        return f"""
            QSlider {{
                height: {UIConstants.SLIDER_HEIGHT}px;
            }}
            QSlider::groove:horizontal {{
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid {Colors.SLIDER_GROOVE_BORDER};
                height: {UIConstants.SLIDER_GROOVE_HEIGHT}px; 
                background: {Colors.SLIDER_GROOVE_BG};
                border-radius: {UIConstants.SLIDER_RADIUS}px;
                margin: {UIConstants.SLIDER_GROOVE_MARGIN_ZERO}px {UIConstants.SLIDER_GROOVE_MARGIN}px;
            }}
            QSlider::sub-page:horizontal {{
                background: {Colors.SLIDER_GROOVE_BG};
                border-radius: {UIConstants.SLIDER_RADIUS}px;
            }}
            QSlider::handle:horizontal {{
                background: {handle_color}; 
                border: {border_width}px solid {border_color};
                width: {UIConstants.SLIDER_HANDLE_WIDTH}px; 
                height: {UIConstants.SLIDER_HANDLE_HEIGHT}px;
                margin: {margin}px {UIConstants.SLIDER_HANDLE_MARGIN_OFFSET}px; 
                border-radius: {UIConstants.HANDLE_RADIUS}px;
            }}
            QSlider::handle:horizontal:hover {{ 
                background: {hover_color}; 
            }}
        """
    
    @staticmethod
    def get_master_slider_stylesheet() -> str:
        return StyleSheets._get_slider_stylesheet(Colors.MASTER_SLIDER_HANDLE, Colors.MASTER_SLIDER_HANDLE_BORDER, 
                                                   Colors.MASTER_SLIDER_HANDLE_HOVER, 
                                                   UIConstants.MASTER_SLIDER_BORDER_WIDTH, 
                                                   UIConstants.MASTER_SLIDER_MARGIN)
    
    @staticmethod
    def get_app_slider_stylesheet() -> str:
        return StyleSheets._get_slider_stylesheet(Colors.APP_SLIDER_HANDLE, Colors.APP_SLIDER_HANDLE_BORDER, 
                                                   Colors.APP_SLIDER_HANDLE_HOVER,
                                                   UIConstants.APP_SLIDER_BORDER_WIDTH,
                                                   UIConstants.APP_SLIDER_MARGIN)
    
    @staticmethod
    def get_volume_text_stylesheet(border_color: str = None) -> str:
        if border_color is None:
            border_color = Colors.BORDER_COLOR
        return f"""
            QLineEdit {{
                background-color: {Colors.INPUT_BG};
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid {border_color};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: {UIConstants.STANDARD_PADDING}px;
                color: {Colors.TEXT_WHITE};
                font-size: {UIConstants.LABEL_FONT_SIZE}px;
            }}
        """
    
    @staticmethod
    def get_master_volume_text_stylesheet() -> str:
        return f"""
            QLineEdit {{
                background-color: {Colors.DARK_INPUT_BG};
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid {Colors.MASTER_SLIDER_HANDLE};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: {UIConstants.STANDARD_PADDING}px;
                color: {Colors.TEXT_WHITE};
                font-weight: bold;
                font-size: {UIConstants.LABEL_FONT_SIZE}px;
            }}
        """
    
    @staticmethod
    def get_mute_button_stylesheet(is_master: bool = False) -> str:
        bg_color = Colors.DARK_INPUT_BG if is_master else Colors.SECONDARY_BUTTON_BG
        border_color = Colors.MASTER_SLIDER_HANDLE if is_master else Colors.BORDER_COLOR
        hover_color = Colors.MASTER_SLIDER_HANDLE if is_master else Colors.SECONDARY_BUTTON_HOVER
        border_width = UIConstants.THICK_BORDER_WIDTH if is_master else UIConstants.STANDARD_BORDER_WIDTH
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                border: {border_width}px solid {border_color};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                font-size: {UIConstants.ICON_FONT_SIZE}px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """
    
    @staticmethod
    def get_pagination_button_stylesheet() -> str:
        return f"""
            QPushButton {{
                background-color: {Colors.APP_CONTROL_BG};
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid {Colors.PRIMARY_BUTTON_BG};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                font-size: {UIConstants.ICON_FONT_SIZE}px;
                color: {Colors.TEXT_WHITE};
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_BUTTON_BG};
            }}
            QPushButton:disabled {{
                background-color: {Colors.DISABLED_BUTTON_BG};
                color: {Colors.TEXT_DISABLED};
            }}
        """
    
    @staticmethod
    def get_page_label_stylesheet() -> str:
        return f"""
            QLabel {{
                color: {Colors.TEXT_LIGHT_GRAY};
                font-size: {UIConstants.LABEL_FONT_SIZE}px;
                padding: 0px {UIConstants.PAGINATION_LABEL_PADDING_H}px;
            }}
        """
    
    @staticmethod
    def get_filter_input_stylesheet() -> str:
        return f"""
            QLineEdit {{
                background-color: {Colors.INPUT_BG};
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid {Colors.BORDER_COLOR};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: {UIConstants.FILTER_INPUT_PADDING_V}px {UIConstants.FILTER_INPUT_PADDING_H}px;
                color: {Colors.TEXT_WHITE};
                font-size: {UIConstants.LABEL_FONT_SIZE}px;
            }}
            QLineEdit:focus {{
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid {Colors.PRIMARY_BUTTON_BG};
            }}
            QLineEdit::placeholder {{
                color: {Colors.TEXT_GRAY};
            }}
        """
    
    @staticmethod
    def get_clear_filter_button_stylesheet() -> str:
        return f"""
            QPushButton {{
                background-color: {Colors.SECONDARY_BUTTON_BG};
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid {Colors.BORDER_COLOR};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                font-size: {UIConstants.CLEAR_BUTTON_FONT_SIZE}px;
                font-weight: bold;
                color: {Colors.TEXT_LIGHT_GRAY};
            }}
            QPushButton:hover {{
                background-color: {Colors.CLOSE_BUTTON_BG};
                color: {Colors.TEXT_WHITE};
            }}
        """


__all__ = [
    'AppInfo', 'UIConstants', 'Hotkeys',
    'get_default_settings', 'get_default_colors', 'get_default_volume_profile',
    'SETTINGS_KEYS', 'COLOR_KEYS', 'VOLUME_PROFILE_KEYS',
    'Colors', 'StyleSheets'
]
