class ColorsMeta(type):
    """Metaclass to make color attributes dynamic"""
    def __getattribute__(cls, name):
        # List of customizable color attributes
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
    """Color constants using RGBA values - can be overridden by settings"""
    # These are default values, but will be replaced by settings_manager values
    _settings_manager = None
    
    # Default color values
    _DEFAULTS = {
        "MAIN_BACKGROUND": "rgba(30, 30, 30, {alpha})",
        "TITLE_BAR_BG": "rgba(43, 43, 43, 255)",
        "MASTER_FRAME_BG": "rgba(30, 58, 95, 255)",
        "CONTAINER_BG": "rgba(43, 43, 43, 255)",
        "APP_CONTROL_BG": "rgba(50, 50, 50, 200)",
        "MASTER_SLIDER_HANDLE": "#4caf50",
        "APP_SLIDER_HANDLE": "#1e88e5",
        "PRIMARY_BUTTON_BG": "#1e88e5",
        "CLOSE_BUTTON_BG": "#d32f2f",
        "TEXT_WHITE": "white",
    }
    
    # Static colors (not customizable)
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
        """Set the settings manager to use for color customization"""
        cls._settings_manager = settings_manager
