"""
Main Overtone Overlay Window
"""
from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QLineEdit)
from PyQt5.QtCore import Qt, QPoint, QTimer

from config.constants import UIConstants, Colors, StyleSheets
from .app_control import AppVolumeControl
from .master_control import MasterVolumeControl


class VolumeOverlay(QWidget):
    """Main overlay window for volume control"""
    
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        # Map of app_name -> AppVolumeControl
        self.app_controls: Dict[str, AppVolumeControl] = {}
        self.all_sessions: List[Dict[str, Any]] = []
        self.filtered_sessions: List[Dict[str, Any]] = []
        self.current_page: int = 0
        self.drag_position: QPoint = QPoint()
        self.title_bar: Optional[QFrame] = None
        self.filter_text: str = ""
        
        # Initialize filter timer
        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.timeout.connect(self.apply_filter)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(self.app.settings_manager.overlay_width, self.app.settings_manager.overlay_height)
        self.move(0, 0)
        self.setMinimumSize(UIConstants.MIN_OVERLAY_WIDTH, UIConstants.MIN_OVERLAY_HEIGHT)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(*[UIConstants.LAYOUT_MARGIN] * 4)
        main_layout.setSizeConstraint(main_layout.SetNoConstraint)
        
        self.title_bar = self._create_title_bar()
        main_layout.addWidget(self.title_bar)
        
        self.master_control = MasterVolumeControl(self.app.audio_controller)
        main_layout.addWidget(self.master_control)
        
        self.filter_bar = self._create_filter_bar()
        main_layout.addWidget(self.filter_bar)
        
        self.container = QFrame()
        self.container.setMinimumHeight(0)
        self.container.setSizePolicy(self.container.sizePolicy().horizontalPolicy(), self.container.sizePolicy().Ignored)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setContentsMargins(*[UIConstants.FRAME_MARGIN] * 4)
        self.container_layout.setSpacing(UIConstants.FRAME_SPACING)
        self.container.setStyleSheet(StyleSheets.get_frame_stylesheet())
        
        main_layout.addWidget(self.container, 1)
        
        self.pagination_frame = self._create_pagination_controls()
        main_layout.addWidget(self.pagination_frame)
        
        self.setLayout(main_layout)
        self.setObjectName("VolumeOverlay")
        self.setStyleSheet(StyleSheets.get_overlay_stylesheet())
        self.update_background_opacity()
    
    def _create_button(self, text: str, callback, tooltip: str, stylesheet: str) -> QPushButton:
        """Create a standard button with common properties"""
        btn = QPushButton(text)
        btn.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_SIZE)
        btn.setStyleSheet(stylesheet)
        btn.clicked.connect(callback)
        btn.setToolTip(tooltip)
        return btn
    
    def _create_title_bar(self) -> QFrame:
        """Create the title bar with dragging and control buttons"""
        title_bar = QFrame()
        title_bar.setCursor(Qt.SizeAllCursor)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(UIConstants.FRAME_MARGIN, 0, UIConstants.FRAME_MARGIN, 0)

        title_label = QLabel("Overtone")
        title_label.setStyleSheet(StyleSheets.get_title_label_stylesheet())
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        for text, callback, tooltip, stylesheet in [
            ("⚙", self.app.show_settings, "Settings", StyleSheets.get_settings_button_stylesheet()),
            ("—", self.hide, "Minimize to tray", StyleSheets.get_minimize_button_stylesheet()),
            ("×", self.app.confirm_quit, "Quit application", StyleSheets.get_close_button_stylesheet())
        ]:
            title_layout.addWidget(self._create_button(text, callback, tooltip, stylesheet))
        
        title_bar.setStyleSheet(StyleSheets.get_frame_stylesheet(bg_color=Colors.TITLE_BAR_BG))
        return title_bar
    
    def _create_filter_bar(self) -> QFrame:
        """Create the search/filter bar"""
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(*[UIConstants.FRAME_MARGIN] * 4)
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter applications...")
        self.filter_input.setStyleSheet(StyleSheets.get_filter_input_stylesheet())
        self.filter_input.textChanged.connect(self.on_filter_changed)
        
        self.clear_filter_btn = QPushButton("×")
        self.clear_filter_btn.setFixedSize(UIConstants.BUTTON_HEIGHT, UIConstants.BUTTON_HEIGHT)
        self.clear_filter_btn.setStyleSheet(StyleSheets.get_clear_filter_button_stylesheet())
        self.clear_filter_btn.clicked.connect(self.clear_filter)
        self.clear_filter_btn.setVisible(False)
        self.clear_filter_btn.setToolTip("Clear filter")
        
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.clear_filter_btn)
        filter_frame.setStyleSheet(StyleSheets.get_frame_stylesheet())
        return filter_frame
    
    def _create_pagination_controls(self) -> QFrame:
        """Create pagination controls frame"""
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        
        self.prev_btn = self._create_button("◀", self.previous_page, "", StyleSheets.get_pagination_button_stylesheet())
        self.prev_btn.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        
        self.page_label = QLabel("1 / 1")
        self.page_label.setStyleSheet(StyleSheets.get_page_label_stylesheet())
        self.page_label.setAlignment(Qt.AlignCenter)
        
        self.next_btn = self._create_button("▶", self.next_page, "", StyleSheets.get_pagination_button_stylesheet())
        self.next_btn.setFixedSize(UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        
        pagination_layout.addStretch()
        for widget in (self.prev_btn, self.page_label, self.next_btn):
            pagination_layout.addWidget(widget)
        pagination_layout.addStretch()
        
        pagination_frame.setStyleSheet(StyleSheets.get_frame_stylesheet())
        return pagination_frame
    
    def update_background_opacity(self):
        """Update background opacity based on settings"""
        opacity = self.app.settings_manager.overlay_opacity
        
        # Use setWindowOpacity for direct window transparency control
        self.setWindowOpacity(opacity)
    
    def on_filter_changed(self, text: str) -> None:
        """Handle filter text change"""
        self.filter_text = text.lower().strip()
        self.clear_filter_btn.setVisible(bool(self.filter_text))
        self.current_page = 0
        self._filter_timer.start(UIConstants.FILTER_DEBOUNCE_MS)
    
    def clear_filter(self):
        """Clear the filter text"""
        self.filter_input.clear()
    
    def apply_filter(self) -> None:
        """Apply the current filter to sessions"""
        self.filtered_sessions = self.all_sessions if not self.filter_text else [
            s for s in self.all_sessions if self.filter_text in s['name'].lower()
        ]
        self.filtered_sessions.sort(key=lambda s: s['name'].lower())
        self.update_page_display()
    
    def refresh_applications(self) -> None:
        """Refresh the list of applications with volume controls"""
        self.all_sessions = self.app.audio_controller.get_audio_sessions()
        self.apply_filter()
    
    def get_apps_per_page(self) -> int:
        """Calculate how many apps can fit in current window height"""
        return max(1, (self.height() - UIConstants.RESERVED_HEIGHT) // UIConstants.APP_CONTROL_HEIGHT)
    
    def update_page_display(self) -> None:
        """Update the displayed applications based on current page"""
        if not self.filtered_sessions:
            self._clear_all_controls()
            self.page_label.setText("No matches" if self.filter_text and self.all_sessions else "0 / 0")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return
        
        apps_per_page = self.get_apps_per_page()
        total_pages = max(1, (len(self.filtered_sessions) + apps_per_page - 1) // apps_per_page)
        self.current_page = max(0, min(self.current_page, total_pages - 1))
        
        start_idx = self.current_page * apps_per_page
        page_sessions = self.filtered_sessions[start_idx:start_idx + apps_per_page]
        current_names = {session['name'] for session in page_sessions}

        # Remove controls no longer on this page
        for name in set(self.app_controls.keys()) - current_names:
            if widget := self.app_controls.pop(name, None):
                self.container_layout.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()

        # Add or update controls for sessions on this page
        for session in page_sessions:
            name = session['name']
            if control := self.app_controls.get(name):
                if hasattr(control, 'update_session'):
                    control.update_session(session)
            else:
                control = AppVolumeControl(session, self.app.audio_controller)
                self.container_layout.addWidget(control)
                self.app_controls[name] = control
        
        self._ensure_container_stretch()
        self.page_label.setText(f"{self.current_page + 1} / {total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)
    
    def _clear_all_controls(self) -> None:
        """Clear all app controls from layout"""
        for widget in list(self.app_controls.values()):
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
        self.app_controls.clear()
        
        while self.container_layout.count():
            if item := self.container_layout.takeAt(0):
                if widget := item.widget():
                    widget.deleteLater()
        self._ensure_container_stretch()

    def _ensure_container_stretch(self) -> None:
        """Ensure there is a stretch at the end of the container layout"""
        if not (count := self.container_layout.count()) or not (
            last_item := self.container_layout.itemAt(count - 1)
        ) or not last_item.spacerItem():
            self.container_layout.addStretch()
    
    def previous_page(self) -> None:
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()
    
    def next_page(self) -> None:
        """Go to next page"""
        apps_per_page = self.get_apps_per_page()
        total_pages = max(1, (len(self.filtered_sessions) + apps_per_page - 1) // apps_per_page)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_page_display()
    
    def resizeEvent(self, event):
        """Handle window resize to update pagination"""
        super().resizeEvent(event)
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
