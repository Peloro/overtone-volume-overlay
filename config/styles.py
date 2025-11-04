from .ui_constants import UIConstants
from .colors import Colors


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
                padding: {UIConstants.SMALL_PADDING}px;
            }}
        """
    
    @staticmethod
    def _get_button_stylesheet(bg_color: str, hover_color: str, font_size: int = None, bold: bool = False) -> str:
        """Helper to generate button stylesheet"""
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
        """Helper to generate slider stylesheet"""
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
