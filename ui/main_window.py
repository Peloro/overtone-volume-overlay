"""
Main Overtone Overlay Window
"""
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QLineEdit)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QIcon

from config.constants import UIConstants, Colors, StyleSheets
from .app_control import AppVolumeControl
from .master_control import MasterVolumeControl


class VolumeOverlay(QWidget):
    """Main overlay window for volume control"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app_controls = {}
        self.all_sessions = []
        self.filtered_sessions = []
        self.current_page = 0
        self.drag_position = QPoint()
        self.title_bar = None
        self._last_apps_per_page = None
        self.filter_text = ""
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(
            self.app.settings_manager.overlay_width,
            self.app.settings_manager.overlay_height
        )
        
        self.move(0, 0)
        
        self.setMinimumSize(
            UIConstants.MIN_OVERLAY_WIDTH,
            UIConstants.MIN_OVERLAY_HEIGHT
        )
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(
            UIConstants.LAYOUT_MARGIN,
            UIConstants.LAYOUT_MARGIN,
            UIConstants.LAYOUT_MARGIN,
            UIConstants.LAYOUT_MARGIN
        )
        main_layout.setSizeConstraint(main_layout.SetNoConstraint)
        
        self.title_bar = self._create_title_bar()
        main_layout.addWidget(self.title_bar)
        
        self.master_control = MasterVolumeControl(self.app.audio_controller)
        main_layout.addWidget(self.master_control)
        
        # Add filter/search bar
        self.filter_bar = self._create_filter_bar()
        main_layout.addWidget(self.filter_bar)
        
        self.container = QFrame()
        self.container.setMinimumHeight(0)
        self.container.setSizePolicy(
            self.container.sizePolicy().horizontalPolicy(),
            self.container.sizePolicy().Ignored
        )
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setContentsMargins(
            UIConstants.FRAME_MARGIN,
            UIConstants.FRAME_MARGIN,
            UIConstants.FRAME_MARGIN,
            UIConstants.FRAME_MARGIN
        )
        self.container_layout.setSpacing(UIConstants.FRAME_SPACING)
        
        self.container.setStyleSheet(StyleSheets.get_frame_stylesheet())
        
        main_layout.addWidget(self.container, 1)
        
        self.pagination_frame = self._create_pagination_controls()
        main_layout.addWidget(self.pagination_frame)
        
        self.setLayout(main_layout)

        # Try to set the application/window icon as well (affects taskbar and alt-tab)
        icon = self._load_app_icon()
        if icon is not None:
            self.setWindowIcon(icon)
        
        self.setObjectName("VolumeOverlay")
        self.setStyleSheet(StyleSheets.get_overlay_stylesheet())
        self.update_background_opacity()
    
    def _create_title_bar(self) -> QFrame:
        """Create the title bar with dragging and control buttons"""
        title_bar = QFrame()
        title_bar.setCursor(Qt.SizeAllCursor)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(
            UIConstants.FRAME_MARGIN,
            0,
            UIConstants.FRAME_MARGIN,
            0,
        )

        title_label = QLabel("Overtone")
        title_label.setStyleSheet(StyleSheets.get_title_label_stylesheet())
        
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_SIZE)
        settings_btn.setStyleSheet(StyleSheets.get_settings_button_stylesheet())
        settings_btn.clicked.connect(self.app.show_settings)
        settings_btn.setToolTip("Settings")
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_SIZE)
        close_btn.setStyleSheet(StyleSheets.get_close_button_stylesheet())
        close_btn.clicked.connect(self.hide)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(settings_btn)
        title_layout.addWidget(close_btn)
        
        title_bar.setStyleSheet(StyleSheets.get_frame_stylesheet(
            bg_color=Colors.TITLE_BAR_BG
        ))
        
        return title_bar
    
    def _create_filter_bar(self) -> QFrame:
        """Create the search/filter bar"""
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(
            UIConstants.FRAME_MARGIN,
            UIConstants.FRAME_MARGIN,
            UIConstants.FRAME_MARGIN,
            UIConstants.FRAME_MARGIN
        )
        
        # Search input field
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter applications...")
        self.filter_input.setStyleSheet(StyleSheets.get_filter_input_stylesheet())
        self.filter_input.textChanged.connect(self.on_filter_changed)
        
        # Clear button
        self.clear_filter_btn = QPushButton("×")
        self.clear_filter_btn.setFixedSize(UIConstants.BUTTON_HEIGHT, UIConstants.BUTTON_HEIGHT)
        self.clear_filter_btn.setStyleSheet(StyleSheets.get_clear_filter_button_stylesheet())
        self.clear_filter_btn.clicked.connect(self.clear_filter)
        self.clear_filter_btn.setVisible(False)  # Hidden initially
        self.clear_filter_btn.setToolTip("Clear filter")
        
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.clear_filter_btn)
        
        filter_frame.setStyleSheet(StyleSheets.get_frame_stylesheet())
        
        return filter_frame

    def _assets_dir(self) -> str:
        """Return absolute path to the assets directory."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'assets')

    def _load_app_icon(self) -> QIcon:
        """Load an application icon as QIcon for window/taskbar.

        Prefers ICO on Windows, otherwise PNG. Returns None if neither loads.
        """
        assets_dir = self._assets_dir()
        ico_path = os.path.join(assets_dir, 'icon2.ico')
        png_path = os.path.join(assets_dir, 'icon2.png')

        # Prefer ICO on Windows for best taskbar integration
        if os.path.exists(ico_path):
            icon = QIcon(ico_path)
            if not icon.isNull():
                return icon
        if os.path.exists(png_path):
            icon = QIcon(png_path)
            if not icon.isNull():
                return icon
        return None
    
    def _create_pagination_controls(self) -> QFrame:
        """Create pagination controls frame"""
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.prev_btn.setStyleSheet(StyleSheets.get_pagination_button_stylesheet())
        self.prev_btn.clicked.connect(self.previous_page)
        
        self.page_label = QLabel("1 / 1")
        self.page_label.setStyleSheet(StyleSheets.get_page_label_stylesheet())
        self.page_label.setAlignment(Qt.AlignCenter)
        
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        self.next_btn.setStyleSheet(StyleSheets.get_pagination_button_stylesheet())
        self.next_btn.clicked.connect(self.next_page)
        
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addStretch()
        
        pagination_frame.setStyleSheet(StyleSheets.get_frame_stylesheet())
        
        return pagination_frame
    
    def update_background_opacity(self):
        """Update background opacity based on settings"""
        opacity = self.app.settings_manager.overlay_opacity
        
        # Use setWindowOpacity for direct window transparency control
        self.setWindowOpacity(opacity)
    
    def on_filter_changed(self, text):
        """Handle filter text change"""
        self.filter_text = text.lower().strip()
        self.clear_filter_btn.setVisible(bool(self.filter_text))
        self.current_page = 0  # Reset to first page when filter changes
        self.apply_filter()
    
    def clear_filter(self):
        """Clear the filter text"""
        self.filter_input.clear()
    
    def apply_filter(self):
        """Apply the current filter to sessions"""
        if not self.filter_text:
            self.filtered_sessions = self.all_sessions
        else:
            self.filtered_sessions = [
                session for session in self.all_sessions
                if self.filter_text in session['name'].lower()
            ]
        self.update_page_display()
    
    def refresh_applications(self):
        """Refresh the list of applications with volume controls"""
        self.all_sessions = self.app.audio_controller.get_audio_sessions()
        self.apply_filter()
    
    def get_apps_per_page(self) -> int:
        """Calculate how many apps can fit in current window height"""
        available_height = self.height() - UIConstants.RESERVED_HEIGHT
        
        apps_per_page = max(1, available_height // UIConstants.APP_CONTROL_HEIGHT)
        return apps_per_page
    
    def update_page_display(self):
        """Update the displayed applications based on current page"""
        if not self.filtered_sessions:
            self._clear_all_controls()
            # Show different message if filtering vs no apps
            if self.filter_text and self.all_sessions:
                self.page_label.setText("No matches")
            else:
                self.page_label.setText("0 / 0")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return
        
        apps_per_page = self.get_apps_per_page()
        total_apps = len(self.filtered_sessions)
        total_pages = max(1, (total_apps + apps_per_page - 1) // apps_per_page)
        
        self.current_page = max(0, min(self.current_page, total_pages - 1))
        
        start_idx = self.current_page * apps_per_page
        end_idx = min(start_idx + apps_per_page, total_apps)
        page_sessions = self.filtered_sessions[start_idx:end_idx]
        
        current_app_names = {session['name'] for session in page_sessions}
        displayed_app_names = set(self.app_controls.keys())
        
        if current_app_names != displayed_app_names:
            self._clear_all_controls()
            
            for session in page_sessions:
                control = AppVolumeControl(session, self.app.audio_controller)
                self.container_layout.addWidget(control)
                self.app_controls[session['name']] = control
            
            self.container_layout.addStretch()
        
        self.page_label.setText(f"{self.current_page + 1} / {total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)
    
    def _clear_all_controls(self):
        """Clear all app controls from layout"""
        for widget in self.app_controls.values():
            self.container_layout.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
        self.app_controls.clear()
        
        if self.container_layout.count() > 0:
            item = self.container_layout.takeAt(0)
            if item:
                del item
    
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()
    
    def next_page(self):
        """Go to next page"""
        apps_per_page = self.get_apps_per_page()
        total_pages = max(1, (len(self.filtered_sessions) + apps_per_page - 1) // apps_per_page)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_page_display()
    
    def resizeEvent(self, event):
        """Handle window resize to update pagination"""
        super().resizeEvent(event)
        new_apps_per_page = self.get_apps_per_page()
        
        if self._last_apps_per_page != new_apps_per_page:
            self.current_page = 0
            self._last_apps_per_page = new_apps_per_page
            if hasattr(self, 'all_sessions'):
                self.update_page_display()
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            event.ignore()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            event.ignore()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.drag_position = QPoint()
            event.accept()
    
    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        self.refresh_applications()
    
    def closeEvent(self, event):
        """Handle close event - just hide instead of closing"""
        event.ignore()
        self.hide()
