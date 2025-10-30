"""
UI Dimension and Timing Constants
"""


class UIConstants:
    """UI dimension and timing constants"""
    DEFAULT_OVERLAY_WIDTH = 300
    DEFAULT_OVERLAY_HEIGHT = 350
    MIN_OVERLAY_WIDTH = 300
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


class Hotkeys:
    """Default hotkey configurations"""
    DEFAULT_HOTKEY_OPEN = "ctrl+shift+v"
    DEFAULT_HOTKEY_SETTINGS = "ctrl+shift+s"
    DEFAULT_HOTKEY_QUIT = "ctrl+shift+q"
