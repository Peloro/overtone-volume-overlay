"""
Main Overtone Overlay Window
"""
from typing import Dict, List, Any
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QLineEdit)
from PyQt5.QtCore import Qt, QPoint, QTimer

from config import UIConstants, Colors, StyleSheets
from utils import create_standard_button, batch_update
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
        self.title_bar: QFrame = None
        self.filter_text: str = ""
        self.filter_visible: bool = False
        
        # Initialize filter timer
        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.timeout.connect(self.apply_filter)
        
        # Debounce resize events
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(UIConstants.RESIZE_DEBOUNCE_MS)
        self._resize_timer.timeout.connect(self._handle_resize)
        
        # Hide window before initializing UI to prevent flash on startup
        self.hide()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(self.app.settings_manager.overlay_width, self.app.settings_manager.overlay_height)
        self.move(0, 0)
        self.setMinimumSize(UIConstants.MIN_OVERLAY_WIDTH, UIConstants.MIN_OVERLAY_HEIGHT)
        self.setMaximumSize(UIConstants.MAX_OVERLAY_WIDTH, UIConstants.MAX_OVERLAY_HEIGHT)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(*[UIConstants.LAYOUT_MARGIN] * UIConstants.MARGIN_SIDES_COUNT)
        main_layout.setSizeConstraint(main_layout.SetNoConstraint)
        
        self.title_bar = self._create_title_bar()
        main_layout.addWidget(self.title_bar)
        
        self.master_control = MasterVolumeControl(self.app.audio_controller)
        main_layout.addWidget(self.master_control)
        # Set initial visibility based on settings
        self.master_control.setVisible(self.app.settings_manager.show_system_volume)
        
        self.filter_bar = self._create_filter_bar()
        main_layout.addWidget(self.filter_bar)
        # Set initial visibility based on settings
        self.update_filter_display_mode()
        
        self.container = QFrame()
        self.container.setMinimumHeight(0)
        self.container.setSizePolicy(self.container.sizePolicy().horizontalPolicy(), self.container.sizePolicy().Ignored)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setContentsMargins(*[UIConstants.FRAME_MARGIN] * UIConstants.MARGIN_SIDES_COUNT)
        self.container_layout.setSpacing(UIConstants.FRAME_SPACING)
        # Add stretch at the bottom to push all controls to the top
        self.container_layout.addStretch(1)
        self.container.setStyleSheet(StyleSheets.get_frame_stylesheet())
        
        main_layout.addWidget(self.container, 1)
        
        self.pagination_frame = self._create_pagination_controls()
        main_layout.addWidget(self.pagination_frame)
        
        self.setLayout(main_layout)
        self.setObjectName("VolumeOverlay")
        self.setStyleSheet(StyleSheets.get_overlay_stylesheet())
        # Opacity is set via setWindowOpacity in update_background_opacity
        self.update_background_opacity()
    
    def _create_title_bar(self) -> QFrame:
        """Create the title bar with dragging and control buttons"""
        title_bar = QFrame()
        title_bar.setCursor(Qt.SizeAllCursor)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(UIConstants.FRAME_MARGIN, 0, UIConstants.FRAME_MARGIN, 0)

        self.title_label = QLabel("Overtone")
        self.title_label.setStyleSheet(StyleSheets.get_title_label_stylesheet())
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        # Create filter toggle and control buttons
        buttons = [
            ("⌕", self.toggle_filter, "Show/Hide filter", StyleSheets.get_settings_button_stylesheet()),
            ("⚙", self.app.show_settings, "Settings", StyleSheets.get_settings_button_stylesheet()),
            ("—", self.hide, "Minimize to tray", StyleSheets.get_minimize_button_stylesheet()),
            ("×", self.app.confirm_quit, "Quit application", StyleSheets.get_close_button_stylesheet())
        ]
        
        self.filter_toggle_btn = create_standard_button(*buttons[0])
        title_layout.addWidget(self.filter_toggle_btn)
        
        # Store references to other buttons for style updates
        self.settings_btn = create_standard_button(*buttons[1])
        self.minimize_btn = create_standard_button(*buttons[2])
        self.close_btn = create_standard_button(*buttons[3])
        
        title_layout.addWidget(self.settings_btn)
        title_layout.addWidget(self.minimize_btn)
        title_layout.addWidget(self.close_btn)
        
        title_bar.setStyleSheet(StyleSheets.get_frame_stylesheet(bg_color=Colors.TITLE_BAR_BG))
        return title_bar
    
    def toggle_filter(self):
        """Toggle the visibility of the filter bar"""
        # Don't allow toggling if always_show_filter is enabled
        if self.app.settings_manager.always_show_filter:
            return
        
        self.filter_visible = not self.filter_visible
        self.filter_bar.setVisible(self.filter_visible)
        
        # Focus filter input when showing
        if self.filter_visible:
            self.filter_input.setFocus()
        else:
            # Clear filter when hiding and reapply to show all apps
            if self.filter_text:
                self.filter_input.clear()  # This triggers on_filter_changed -> apply_filter
        
        # Recalculate pagination since available space has changed
        if hasattr(self, 'all_sessions'):
            self.update_page_display()
    
    def _create_filter_bar(self) -> QFrame:
        """Create the search/filter bar"""
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(*[UIConstants.FRAME_MARGIN] * UIConstants.MARGIN_SIDES_COUNT)
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter applications...")
        self.filter_input.setStyleSheet(StyleSheets.get_filter_input_stylesheet())
        self.filter_input.textChanged.connect(self.on_filter_changed)
        
        self.clear_filter_button = QPushButton("×")
        self.clear_filter_button.setFixedSize(UIConstants.BUTTON_HEIGHT, UIConstants.BUTTON_HEIGHT)
        self.clear_filter_button.setStyleSheet(StyleSheets.get_clear_filter_button_stylesheet())
        self.clear_filter_button.clicked.connect(self.clear_filter)
        self.clear_filter_button.setVisible(False)
        self.clear_filter_button.setToolTip("Clear filter")
        
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.clear_filter_button)
        filter_frame.setStyleSheet(StyleSheets.get_frame_stylesheet())
        return filter_frame
    
    def _create_pagination_controls(self) -> QFrame:
        """Create pagination controls frame"""
        from utils import create_button
        
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        
        style = StyleSheets.get_pagination_button_stylesheet()
        self.previous_button = create_button("◀", self.previous_page, "", style, UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        
        self.page_label = QLabel("1 / 1")
        self.page_label.setStyleSheet(StyleSheets.get_page_label_stylesheet())
        self.page_label.setAlignment(Qt.AlignCenter)
        
        self.next_button = create_button("▶", self.next_page, "", style, UIConstants.BUTTON_SIZE, UIConstants.BUTTON_HEIGHT)
        
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.previous_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addStretch()
        
        pagination_frame.setStyleSheet(StyleSheets.get_frame_stylesheet())
        return pagination_frame
    
    def update_background_opacity(self):
        """Update background opacity based on settings"""
        opacity = self.app.settings_manager.overlay_opacity
        
        # Use setWindowOpacity for direct window transparency control
        self.setWindowOpacity(opacity)
    
    def update_system_volume_visibility(self):
        """Update the visibility of the system volume control based on settings"""
        show_system_volume = self.app.settings_manager.show_system_volume
        self.master_control.setVisible(show_system_volume)
        
        # Recalculate pagination since available space has changed
        # Only if the UI is fully initialized
        if hasattr(self, 'all_sessions') and hasattr(self, 'container_layout'):
            self.update_page_display()
    
    def update_filter_display_mode(self):
        """Update filter display based on always_show_filter setting"""
        always_show = self.app.settings_manager.always_show_filter
        
        if always_show:
            # Always show mode: hide toggle button, always show filter bar
            self.filter_toggle_btn.setVisible(False)
            self.filter_bar.setVisible(True)
            self.filter_visible = True
        else:
            # Toggle mode: show toggle button, hide filter bar (user can toggle it manually)
            self.filter_toggle_btn.setVisible(True)
            self.filter_bar.setVisible(False)
            self.filter_visible = False
            # Clear any active filter when switching to toggle mode
            if self.filter_text:
                self.filter_input.clear()
        
        # Recalculate pagination since available space may have changed
        # Only if the UI is fully initialized
        if hasattr(self, 'all_sessions') and hasattr(self, 'container_layout'):
            self.update_page_display()
    
    def on_filter_changed(self, text: str) -> None:
        """Handle filter text change"""
        new_filter = text.lower().strip()
        if new_filter == self.filter_text:
            return  # No change, skip processing
        self.filter_text = new_filter
        self.clear_filter_button.setVisible(bool(self.filter_text))
        self.current_page = 0
        self._filter_timer.start(UIConstants.FILTER_DEBOUNCE_MS)
    
    def clear_filter(self):
        """Clear the filter text"""
        self.filter_input.clear()
    
    def apply_filter(self) -> None:
        """Apply the current filter to sessions"""
        if self.filter_text:
            self.filtered_sessions = [s for s in self.all_sessions if self.filter_text in s['name'].lower()]
            self.filtered_sessions.sort(key=lambda s: s['name'].lower())
        else:
            self.filtered_sessions = self.all_sessions
        self.update_page_display()
    
    def refresh_applications(self) -> None:
        """Refresh the list of applications with volume controls"""
        new_sessions = self.app.audio_controller.get_audio_sessions()
        
        # Only update if sessions have actually changed (reduce unnecessary UI updates)
        if self.app.audio_controller.sessions_have_changed(self.all_sessions, new_sessions):
            self.all_sessions = new_sessions
            self.apply_filter()
    
    def get_apps_per_page(self) -> int:
        """Calculate how many apps can fit in current window height"""
        reserved_height = UIConstants.RESERVED_HEIGHT
        
        # Adjust for hidden components
        if not self.app.settings_manager.show_system_volume:
            reserved_height -= UIConstants.MASTER_VOLUME_HEIGHT
        
        if not (self.app.settings_manager.always_show_filter or self.filter_visible):
            reserved_height -= UIConstants.FILTER_BAR_HEIGHT
        
        # Calculate available height and apps that fit
        available_height = self.height() - reserved_height
        apps_that_fit = available_height // (UIConstants.APP_CONTROL_HEIGHT + UIConstants.FRAME_SPACING)
        
        return max(1, apps_that_fit)
    
    def _handle_no_sessions(self) -> None:
        """Handle display when there are no filtered sessions"""
        self.clear_all_controls()
        self.page_label.setText("No matches" if self.filter_text and self.all_sessions else "0 / 0")
        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(False)
    
    def _calculate_pagination(self, apps_per_page: int) -> tuple[int, int, int]:
        """
        Calculate pagination parameters
        
        Returns:
            Tuple of (total_pages, current_page, start_idx)
        """
        total_pages = max(1, (len(self.filtered_sessions) + apps_per_page - 1) // apps_per_page)
        current_page = max(0, min(self.current_page, total_pages - 1))
        start_idx = current_page * apps_per_page
        return total_pages, current_page, start_idx
    
    def _update_controls_for_sessions(self, page_sessions: List[Dict[str, Any]]) -> None:
        """Update or create controls for the given sessions"""
        current_names = {session['name'] for session in page_sessions}

        # Remove controls no longer on this page (batch operations)
        to_remove = set(self.app_controls.keys()) - current_names
        if to_remove:
            for name in to_remove:
                if widget := self.app_controls.pop(name, None):
                    self.container_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()

        # Add or update controls for sessions on this page
        for idx, session in enumerate(page_sessions):
            name = session['name']
            if control := self.app_controls.get(name):
                control.update_session(session)
            else:
                control = AppVolumeControl(session, self.app.audio_controller)
                # Insert before the stretch item (which is always last)
                self.container_layout.insertWidget(self.container_layout.count() - 1, control)
                self.app_controls[name] = control
    
    def _update_pagination_ui(self, current_page: int, total_pages: int) -> None:
        """Update pagination button states and label"""
        self.page_label.setText(f"{current_page + 1} / {total_pages}")
        self.previous_button.setEnabled(current_page > 0)
        self.next_button.setEnabled(current_page < total_pages - 1)
    
    def update_page_display(self) -> None:
        """Update the displayed applications based on current page"""
        if not self.filtered_sessions:
            self._handle_no_sessions()
            return
        
        apps_per_page = self.get_apps_per_page()
        total_pages, current_page, start_idx = self._calculate_pagination(apps_per_page)
        self.current_page = current_page
        
        page_sessions = self.filtered_sessions[start_idx:start_idx + apps_per_page]
        
        # Use context manager for batch operations for better performance
        with batch_update(self):
            self._update_controls_for_sessions(page_sessions)
            self._update_pagination_ui(current_page, total_pages)
    
    def clear_all_controls(self) -> None:
        """Clear all app controls from layout"""
        # Use context manager for batch operations
        with batch_update(self):
            # Clear app controls first
            for name, widget in list(self.app_controls.items()):
                try:
                    self.container_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()
                except Exception:
                    pass
            self.app_controls.clear()
            
            # Clear any remaining widgets in layout (excluding the stretch item)
            while self.container_layout.count() > 1:
                item = self.container_layout.takeAt(0)
                if item and (widget := item.widget()):
                    try:
                        widget.setParent(None)
                        widget.deleteLater()
                    except Exception:
                        pass
    
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
        """Handle window resize to update pagination - debounced"""
        super().resizeEvent(event)
        if hasattr(self, '_resize_timer') and hasattr(self, 'all_sessions'):
            self._resize_timer.start()
    
    def _handle_resize(self):
        """Actually handle the resize after debouncing"""
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
    
    def hideEvent(self, event):
        """Handle hide event - stop timers"""
        super().hideEvent(event)
        if hasattr(self, '_filter_timer') and self._filter_timer:
            self._filter_timer.stop()
        if hasattr(self, '_resize_timer') and self._resize_timer:
            self._resize_timer.stop()
    
    def closeEvent(self, event):
        """Handle close event - hide instead of closing"""
        # Stop timers during close
        if hasattr(self, '_filter_timer') and self._filter_timer:
            self._filter_timer.stop()
        if hasattr(self, '_resize_timer') and self._resize_timer:
            self._resize_timer.stop()
        
        event.ignore()
        self.app.hide_overlay()
    
    def apply_styles(self):
        """Reapply all styles to reflect color changes"""
        # Reapply overlay stylesheet
        self.setStyleSheet(StyleSheets.get_overlay_stylesheet())
        
        # Reapply component styles - all must be called as functions to get fresh color values
        style_updates = [
            (self.title_bar, lambda: StyleSheets.get_frame_stylesheet(bg_color=Colors.TITLE_BAR_BG)),
            (self.container, lambda: StyleSheets.get_frame_stylesheet(bg_color=Colors.CONTAINER_BG)),
            (getattr(self, 'pagination_frame', None), lambda: StyleSheets.get_frame_stylesheet()),
            (getattr(self, 'filter_bar', None), lambda: StyleSheets.get_frame_stylesheet()),
            (getattr(self, 'previous_button', None), StyleSheets.get_pagination_button_stylesheet),
            (getattr(self, 'next_button', None), StyleSheets.get_pagination_button_stylesheet),
            (getattr(self, 'page_label', None), StyleSheets.get_page_label_stylesheet),
            (getattr(self, 'filter_input', None), StyleSheets.get_filter_input_stylesheet),
            (getattr(self, 'clear_filter_button', None), StyleSheets.get_clear_filter_button_stylesheet),
            (getattr(self, 'title_label', None), StyleSheets.get_title_label_stylesheet),
            (getattr(self, 'filter_toggle_btn', None), StyleSheets.get_settings_button_stylesheet),
            (getattr(self, 'settings_btn', None), StyleSheets.get_settings_button_stylesheet),
            (getattr(self, 'minimize_btn', None), StyleSheets.get_minimize_button_stylesheet),
            (getattr(self, 'close_btn', None), StyleSheets.get_close_button_stylesheet),
        ]
        
        for widget, stylesheet_func in style_updates:
            if widget:
                widget.setStyleSheet(stylesheet_func() if callable(stylesheet_func) else stylesheet_func)
        
        # Reapply styles to all app controls
        for app_control in self.app_controls.values():
            if hasattr(app_control, 'apply_styles'):
                app_control.apply_styles()
        
        # Force update
        self.update()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            if hasattr(self, '_filter_timer') and self._filter_timer:
                self._filter_timer.stop()
            if hasattr(self, '_resize_timer') and self._resize_timer:
                self._resize_timer.stop()
        except Exception:
            pass
