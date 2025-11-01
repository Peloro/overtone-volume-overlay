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
    
    REFRESH_INTERVAL = 5000  # Increased to 5s to reduce CPU usage
    FILTER_DEBOUNCE_MS = 150  # Debounce time for filter input
    ERROR_FLASH_DURATION_MS = 300  # Duration for error visual feedback
    NAME_CACHE_TTL_SECONDS = 30.0  # Increased TTL to reduce window enumeration
    
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
    
    # Volume conversion
    VOLUME_PERCENTAGE_FACTOR = 100
    
    # System tray icon sizes
    ICON_SIZE_16 = 16
    ICON_SIZE_24 = 24
    ICON_SIZE_32 = 32
    ICON_SIZE_48 = 48
    FALLBACK_ICON_SIZE = 32
    
    # Text eliding
    TEXT_ELIDE_WIDTH = 280
    
    # Application timing
    QUIT_DELAY_MS = 100
    RESIZE_DEBOUNCE_MS = 100
    
    # Settings
    SETTINGS_SAVE_DEBOUNCE_MS = 500
    OPACITY_DECIMAL_PLACES = 2
    
    # Logging
    LOG_MAX_BYTES = 5 * 1024 * 1024  # 5MB
    LOG_BACKUP_COUNT = 3
    
    # Profiles
    JSON_INDENT = 4
    
    # Cache limits
    MAX_CACHE_SIZE = 100
    CACHE_CLEANUP_BATCH_SIZE = 20
    
    # Layout constants
    MARGIN_SIDES_COUNT = 4  # top, right, bottom, left
    RGBA_COMPONENT_COUNT = 4  # red, green, blue, alpha
    
    # Settings Dialog
    SETTINGS_MIN_WIDTH = 450
    COLOR_BUTTON_MIN_HEIGHT = 30
    COLOR_BUTTON_MIN_WIDTH = 90
    COLOR_BUTTON_FONT_SIZE = 8


class Hotkeys:
    """Default hotkey configurations"""
    DEFAULT_HOTKEY_OPEN = "ctrl+/"
    DEFAULT_HOTKEY_SETTINGS = "ctrl+shift+s"
    DEFAULT_HOTKEY_QUIT = "ctrl+q"
