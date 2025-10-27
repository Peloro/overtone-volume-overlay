"""
UI Constants and Colors for Overtone Application
"""

class AppInfo:
    """Application information constants"""
    APP_NAME = "Overtone"
    VERSION = "1.0.0"
    DESCRIPTION = "A modern, lightweight volume mixer overlay for Windows with per-application volume control. If you like the" \
    "project, feel free to star and watch the repository on GitHub!"
    AUTHOR = "Peloro"
    GITHUB_URL = "https://github.com/Peloro"
    REPO_URL = "https://github.com/Peloro/overtone-volume-overlay"
    LICENSE = "MIT License"
    YEAR = "2025"


class UIConstants:
    """UI dimension and timing constants"""
    DEFAULT_OVERLAY_WIDTH = 300
    DEFAULT_OVERLAY_HEIGHT = 300
    MIN_OVERLAY_WIDTH = 280  # Reduced to allow 300x400 but still prevent extreme deformation
    MIN_OVERLAY_HEIGHT = 350
    MAX_OVERLAY_WIDTH = 1000
    MAX_OVERLAY_HEIGHT = 1000
    
    APP_CONTROL_HEIGHT = 68  # Approximate height of each app control
    TITLE_BAR_HEIGHT = 50
    MASTER_VOLUME_HEIGHT = 80
    FILTER_BAR_HEIGHT = 35
    PAGINATION_HEIGHT = 30
    WINDOW_MARGINS = 40
    RESERVED_HEIGHT = 235  # Increased to account for filter bar
    
    BUTTON_SIZE = 30
    BUTTON_HEIGHT = 24
    VOLUME_TEXT_WIDTH = 40
    
    REFRESH_INTERVAL = 3000
    FILTER_DEBOUNCE_MS = 150  # Debounce time for filter input
    ERROR_FLASH_DURATION_MS = 300  # Duration for error visual feedback
    NAME_CACHE_TTL_SECONDS = 15.0  # TTL for cached application names
    
    DEFAULT_OPACITY = 0.9
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
    CONTROL_SPACING = 3
    
    WINDOW_RADIUS = 10
    FRAME_RADIUS = 5
    BUTTON_RADIUS = 15
    SMALL_BUTTON_RADIUS = 3
    SLIDER_RADIUS = 3
    HANDLE_RADIUS = 7
    
    # Minimum control widths
    MIN_CONTROL_WIDTH = 200
    MIN_SLIDER_WIDTH = 80


class Colors:
    """Color constants using RGBA values"""
    MAIN_BACKGROUND = "rgba(30, 30, 30, {alpha})"
    TITLE_BAR_BG = "rgba(43, 43, 43, 255)"
    MASTER_FRAME_BG = "rgba(30, 58, 95, 255)"
    CONTAINER_BG = "rgba(43, 43, 43, 255)"
    APP_CONTROL_BG = "rgba(50, 50, 50, 200)"
    DIALOG_BG = "#2b2b2b"
    INPUT_BG = "#424242"
    DARK_INPUT_BG = "#1a2332"
    
    SETTINGS_BUTTON_BG = "#455a64"
    SETTINGS_BUTTON_HOVER = "#607d8b"
    MINIMIZE_BUTTON_BG = "#757575"
    MINIMIZE_BUTTON_HOVER = "#9e9e9e"
    CLOSE_BUTTON_BG = "#d32f2f"
    CLOSE_BUTTON_HOVER = "#f44336"
    PRIMARY_BUTTON_BG = "#1e88e5"
    PRIMARY_BUTTON_HOVER = "#42a5f5"
    SECONDARY_BUTTON_BG = "#424242"
    SECONDARY_BUTTON_HOVER = "#555"
    DISABLED_BUTTON_BG = "#2a2a2a"
    
    MASTER_SLIDER_HANDLE = "#4caf50"
    MASTER_SLIDER_HANDLE_BORDER = "#2e7d32"
    MASTER_SLIDER_HANDLE_HOVER = "#66bb6a"
    APP_SLIDER_HANDLE = "#1e88e5"
    APP_SLIDER_HANDLE_BORDER = "#1565c0"
    APP_SLIDER_HANDLE_HOVER = "#42a5f5"
    SLIDER_GROOVE_BG = "#555"
    SLIDER_GROOVE_BORDER = "#999"
    
    BORDER_COLOR = "#666"
    PRIMARY_BORDER = "#4caf50"
    GROUP_BORDER = "#555"
    SEPARATOR_COLOR = "#555"
    
    TEXT_WHITE = "white"
    TEXT_GRAY = "gray"
    TEXT_LIGHT_GRAY = "#aaa"
    TEXT_DISABLED = "#555"


class Hotkeys:
    """Default hotkey configurations"""
    DEFAULT_HOTKEY_OPEN = "ctrl+shift+v"
    DEFAULT_HOTKEY_SETTINGS = "ctrl+shift+s"
    DEFAULT_HOTKEY_QUIT = "ctrl+shift+q"


class StyleSheets:
    """Reusable stylesheet templates"""
    
    @staticmethod
    def get_frame_stylesheet(bg_color: str = None, border_radius: int = None, padding: int = None) -> str:
        """Get common frame stylesheet with customizable parameters"""
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
        """Get main overlay stylesheet"""
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
                padding: 2px;
            }}
        """
    
    @staticmethod
    def get_settings_button_stylesheet() -> str:
        return f"""
            QPushButton {{
                background-color: {Colors.SETTINGS_BUTTON_BG};
                color: {Colors.TEXT_WHITE};
                border: none;
                border-radius: {UIConstants.BUTTON_RADIUS}px;
                font-size: {UIConstants.BUTTON_FONT_SIZE}px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SETTINGS_BUTTON_HOVER};
            }}
        """
    
    @staticmethod
    def get_minimize_button_stylesheet() -> str:
        return f"""
            QPushButton {{
                background-color: {Colors.MINIMIZE_BUTTON_BG};
                color: {Colors.TEXT_WHITE};
                border: none;
                border-radius: {UIConstants.BUTTON_RADIUS}px;
                font-size: {UIConstants.CLOSE_BUTTON_FONT_SIZE}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.MINIMIZE_BUTTON_HOVER};
            }}
        """
    
    @staticmethod
    def get_close_button_stylesheet() -> str:
        return f"""
            QPushButton {{
                background-color: {Colors.CLOSE_BUTTON_BG};
                color: {Colors.TEXT_WHITE};
                border: none;
                border-radius: {UIConstants.BUTTON_RADIUS}px;
                font-size: {UIConstants.CLOSE_BUTTON_FONT_SIZE}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.CLOSE_BUTTON_HOVER};
            }}
        """
    
    @staticmethod
    def get_master_slider_stylesheet() -> str:
        return f"""
            QSlider::groove:horizontal {{
                border: 1px solid {Colors.SLIDER_GROOVE_BORDER};
                height: 6px;
                background: {Colors.SLIDER_GROOVE_BG};
                border-radius: {UIConstants.SLIDER_RADIUS}px;
            }}
            QSlider::handle:horizontal {{
                background: {Colors.MASTER_SLIDER_HANDLE};
                border: 2px solid {Colors.MASTER_SLIDER_HANDLE_BORDER};
                width: 14px;
                margin: -5px 0;
                border-radius: {UIConstants.HANDLE_RADIUS}px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {Colors.MASTER_SLIDER_HANDLE_HOVER};
            }}
        """
    
    @staticmethod
    def get_app_slider_stylesheet() -> str:
        return f"""
            QSlider::groove:horizontal {{
                border: 1px solid {Colors.SLIDER_GROOVE_BORDER};
                height: 6px;
                background: {Colors.SLIDER_GROOVE_BG};
                border-radius: {UIConstants.SLIDER_RADIUS}px;
            }}
            QSlider::handle:horizontal {{
                background: {Colors.APP_SLIDER_HANDLE};
                border: 1px solid {Colors.APP_SLIDER_HANDLE_BORDER};
                width: 14px;
                margin: -4px 0;
                border-radius: {UIConstants.HANDLE_RADIUS}px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {Colors.APP_SLIDER_HANDLE_HOVER};
            }}
        """
    
    @staticmethod
    def get_volume_text_stylesheet(border_color: str = None) -> str:
        if border_color is None:
            border_color = Colors.BORDER_COLOR
        return f"""
            QLineEdit {{
                background-color: {Colors.INPUT_BG};
                border: 1px solid {border_color};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: 3px;
                color: {Colors.TEXT_WHITE};
                font-size: {UIConstants.LABEL_FONT_SIZE}px;
            }}
        """
    
    @staticmethod
    def get_master_volume_text_stylesheet() -> str:
        return f"""
            QLineEdit {{
                background-color: {Colors.DARK_INPUT_BG};
                border: 1px solid {Colors.PRIMARY_BORDER};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: 3px;
                color: {Colors.TEXT_WHITE};
                font-weight: bold;
                font-size: {UIConstants.LABEL_FONT_SIZE}px;
            }}
        """
    
    @staticmethod
    def get_mute_button_stylesheet(is_master: bool = False) -> str:
        bg_color = Colors.DARK_INPUT_BG if is_master else Colors.SECONDARY_BUTTON_BG
        border_color = Colors.PRIMARY_BORDER if is_master else Colors.BORDER_COLOR
        hover_color = Colors.MASTER_SLIDER_HANDLE_BORDER if is_master else Colors.SECONDARY_BUTTON_HOVER
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                border: {"2px" if is_master else "1px"} solid {border_color};
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
                background-color: {Colors.SECONDARY_BUTTON_BG};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                font-size: {UIConstants.ICON_FONT_SIZE}px;
                color: {Colors.TEXT_WHITE};
            }}
            QPushButton:hover {{
                background-color: {Colors.SECONDARY_BUTTON_HOVER};
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
                padding: 0px 10px;
            }}
        """
    
    @staticmethod
    def get_filter_input_stylesheet() -> str:
        return f"""
            QLineEdit {{
                background-color: {Colors.INPUT_BG};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: 5px 8px;
                color: {Colors.TEXT_WHITE};
                font-size: {UIConstants.LABEL_FONT_SIZE}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Colors.PRIMARY_BUTTON_BG};
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
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                font-size: 16px;
                font-weight: bold;
                color: {Colors.TEXT_LIGHT_GRAY};
            }}
            QPushButton:hover {{
                background-color: {Colors.CLOSE_BUTTON_BG};
                color: {Colors.TEXT_WHITE};
            }}
        """

