from typing import Dict, List, Any
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QLineEdit)
from PyQt5.QtCore import Qt, QPoint, QTimer

from config import UIConstants, Colors, StyleSheets
from utils import create_standard_button, batch_update
from .app_control import AppVolumeControl
from .master_control import MasterVolumeControl


class VolumeOverlay(QWidget):
    
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.app_controls: Dict[str, AppVolumeControl] = {}
        self.all_sessions: List[Dict[str, Any]] = []
        self.filtered_sessions: List[Dict[str, Any]] = []
        self.current_page: int = 0
        self.drag_position: QPoint = QPoint()
        self.title_bar: QFrame = None
        self.filter_text: str = ""
        self.filter_visible: bool = False
        
        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.timeout.connect(self.apply_filter)
        
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(UIConstants.RESIZE_DEBOUNCE_MS)
        self._resize_timer.timeout.connect(self._handle_resize)
        
        self.hide()
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(self.app.settings_manager.overlay_width, self.app.settings_manager.overlay_height)
        self.move(UIConstants.WINDOW_START_X, UIConstants.WINDOW_START_Y)
        self.setMinimumSize(UIConstants.MIN_OVERLAY_WIDTH, UIConstants.MIN_OVERLAY_HEIGHT)
        self.setMaximumSize(UIConstants.MAX_OVERLAY_WIDTH, UIConstants.MAX_OVERLAY_HEIGHT)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(*[UIConstants.LAYOUT_MARGIN] * UIConstants.MARGIN_SIDES_COUNT)
        main_layout.setSizeConstraint(main_layout.SetNoConstraint)
        
        self.title_bar = self._create_title_bar()
        main_layout.addWidget(self.title_bar)
        
        self.master_control = MasterVolumeControl(self.app.audio_controller)
        main_layout.addWidget(self.master_control)
        self.master_control.setVisible(self.app.settings_manager.show_system_volume)
        
        self.filter_bar = self._create_filter_bar()
        main_layout.addWidget(self.filter_bar)
        self.update_filter_display_mode()
        
        self.container = QFrame()
        self.container.setMinimumHeight(0)
        self.container.setSizePolicy(self.container.sizePolicy().horizontalPolicy(), self.container.sizePolicy().Ignored)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setContentsMargins(*[UIConstants.FRAME_MARGIN] * UIConstants.MARGIN_SIDES_COUNT)
        self.container_layout.setSpacing(UIConstants.FRAME_SPACING)
        self.container_layout.addStretch(UIConstants.STRETCH_FACTOR_STANDARD)
        self.container.setStyleSheet(StyleSheets.get_frame_stylesheet())
        
        main_layout.addWidget(self.container, 1)
        
        self.pagination_frame = self._create_pagination_controls()
        main_layout.addWidget(self.pagination_frame)
        
        self.setLayout(main_layout)
        self.setObjectName("VolumeOverlay")
        self.setStyleSheet(StyleSheets.get_overlay_stylesheet())
        self.update_background_opacity()
    
    def _create_title_bar(self) -> QFrame:
        title_bar = QFrame()
        title_bar.setCursor(Qt.SizeAllCursor)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(UIConstants.FRAME_MARGIN, UIConstants.STRETCH_FACTOR_NONE, 
                                       UIConstants.FRAME_MARGIN, UIConstants.STRETCH_FACTOR_NONE)

        self.title_label = QLabel("Overtone")
        self.title_label.setStyleSheet(StyleSheets.get_title_label_stylesheet())
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        buttons = [
            ("⌕", self.toggle_filter, "Show/Hide filter", StyleSheets.get_settings_button_stylesheet()),
            ("⚙", self.app.show_settings, "Settings", StyleSheets.get_settings_button_stylesheet()),
            ("—", self.hide, "Minimize to tray", StyleSheets.get_minimize_button_stylesheet()),
            ("×", self.app.confirm_quit, "Quit application", StyleSheets.get_close_button_stylesheet())
        ]
        
        self.filter_toggle_btn = create_standard_button(*buttons[0])
        title_layout.addWidget(self.filter_toggle_btn)
        
        self.settings_btn = create_standard_button(*buttons[1])
        self.minimize_btn = create_standard_button(*buttons[2])
        self.close_btn = create_standard_button(*buttons[3])
        
        title_layout.addWidget(self.settings_btn)
        title_layout.addWidget(self.minimize_btn)
        title_layout.addWidget(self.close_btn)
        
        title_bar.setStyleSheet(StyleSheets.get_frame_stylesheet(bg_color=Colors.TITLE_BAR_BG))
        return title_bar
    
    def toggle_filter(self):
        if self.app.settings_manager.always_show_filter:
            return
        
        self.filter_visible = not self.filter_visible
        self.filter_bar.setVisible(self.filter_visible)
        
        if self.filter_visible:
            self.filter_input.setFocus()
        else:
            if self.filter_text:
                self.filter_input.clear()
        
        if hasattr(self, 'all_sessions'):
            self.update_page_display()
    
    def _create_filter_bar(self) -> QFrame:
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
        opacity = self.app.settings_manager.overlay_opacity
        
        self.setWindowOpacity(opacity)
    
    def update_system_volume_visibility(self):
        show_system_volume = self.app.settings_manager.show_system_volume
        self.master_control.setVisible(show_system_volume)
        
        if hasattr(self, 'all_sessions') and hasattr(self, 'container_layout'):
            self.update_page_display()
    
    def update_filter_display_mode(self):
        always_show = self.app.settings_manager.always_show_filter
        
        if always_show:
            self.filter_toggle_btn.setVisible(False)
            self.filter_bar.setVisible(True)
            self.filter_visible = True
        else:
            self.filter_toggle_btn.setVisible(True)
            self.filter_bar.setVisible(False)
            self.filter_visible = False
            if self.filter_text:
                self.filter_input.clear()
        
        if hasattr(self, 'all_sessions') and hasattr(self, 'container_layout'):
            self.update_page_display()
    
    def on_filter_changed(self, text: str) -> None:
        new_filter = text.lower().strip()
        if new_filter == self.filter_text:
            return
        self.filter_text = new_filter
        self.clear_filter_button.setVisible(bool(self.filter_text))
        self.current_page = 0
        self._filter_timer.start(UIConstants.FILTER_DEBOUNCE_MS)
    
    def clear_filter(self):
        self.filter_input.clear()
    
    def apply_filter(self) -> None:
        if self.filter_text:
            self.filtered_sessions = [s for s in self.all_sessions if self.filter_text in s['name'].lower()]
            self.filtered_sessions.sort(key=lambda s: s['name'].lower())
        else:
            self.filtered_sessions = self.all_sessions
        self.update_page_display()
    
    def refresh_applications(self) -> None:
        new_sessions = self.app.audio_controller.get_audio_sessions()
        
        # Always update if sessions changed (apps added/removed or volume/mute changed)
        if self.app.audio_controller.sessions_have_changed(self.all_sessions, new_sessions):
            self.all_sessions = new_sessions
            self.apply_filter()
        # Even if sessions haven't changed structurally, update existing controls
        # in case volume/mute changed externally
        elif self.all_sessions:
            self.all_sessions = new_sessions
            # Update existing controls without full refresh
            new_sessions_dict = {s['name']: s for s in new_sessions}
            for name, control in self.app_controls.items():
                if name in new_sessions_dict:
                    control.update_session(new_sessions_dict[name])
    
    def get_apps_per_page(self) -> int:
        reserved_height = UIConstants.RESERVED_HEIGHT
        
        if not self.app.settings_manager.show_system_volume:
            reserved_height -= UIConstants.MASTER_VOLUME_HEIGHT
        
        if not (self.app.settings_manager.always_show_filter or self.filter_visible):
            reserved_height -= UIConstants.FILTER_BAR_HEIGHT
        
        available_height = self.height() - reserved_height
        apps_that_fit = available_height // (UIConstants.APP_CONTROL_HEIGHT + UIConstants.FRAME_SPACING)
        
        return max(1, apps_that_fit)
    
    def _handle_no_sessions(self) -> None:
        self.clear_all_controls()
        self.page_label.setText("No matches" if self.filter_text and self.all_sessions else "0 / 0")
        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(False)
    
    def _calculate_pagination(self, apps_per_page: int) -> tuple[int, int, int]:
        total_pages = max(1, (len(self.filtered_sessions) + apps_per_page - 1) // apps_per_page)
        current_page = max(0, min(self.current_page, total_pages - 1))
        start_idx = current_page * apps_per_page
        return total_pages, current_page, start_idx
    
    def _update_controls_for_sessions(self, page_sessions: List[Dict[str, Any]]) -> None:
        current_names = {session['name'] for session in page_sessions}

        to_remove = set(self.app_controls.keys()) - current_names
        if to_remove:
            for name in to_remove:
                if widget := self.app_controls.pop(name, None):
                    self.container_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()

        for idx, session in enumerate(page_sessions):
            name = session['name']
            if control := self.app_controls.get(name):
                control.update_session(session)
            else:
                control = AppVolumeControl(session, self.app.audio_controller)
                self.container_layout.insertWidget(self.container_layout.count() - 1, control)
                self.app_controls[name] = control
    
    def _update_pagination_ui(self, current_page: int, total_pages: int) -> None:
        self.page_label.setText(f"{current_page + 1} / {total_pages}")
        self.previous_button.setEnabled(current_page > 0)
        self.next_button.setEnabled(current_page < total_pages - 1)
    
    def update_page_display(self) -> None:
        if not self.filtered_sessions:
            self._handle_no_sessions()
            return
        
        apps_per_page = self.get_apps_per_page()
        total_pages, current_page, start_idx = self._calculate_pagination(apps_per_page)
        self.current_page = current_page
        
        page_sessions = self.filtered_sessions[start_idx:start_idx + apps_per_page]
        
        with batch_update(self):
            self._update_controls_for_sessions(page_sessions)
            self._update_pagination_ui(current_page, total_pages)
    
    def clear_all_controls(self) -> None:
        with batch_update(self):
            for name, widget in list(self.app_controls.items()):
                try:
                    self.container_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()
                except Exception:
                    pass
            self.app_controls.clear()
            
            while self.container_layout.count() > UIConstants.STRETCH_FACTOR_STANDARD:
                item = self.container_layout.takeAt(0)
                if item and (widget := item.widget()):
                    try:
                        widget.setParent(None)
                        widget.deleteLater()
                    except Exception:
                        pass
    
    def previous_page(self) -> None:
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()
    
    def next_page(self) -> None:
        apps_per_page = self.get_apps_per_page()
        total_pages = max(1, (len(self.filtered_sessions) + apps_per_page - 1) // apps_per_page)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_page_display()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_resize_timer') and hasattr(self, 'all_sessions'):
            self._resize_timer.start()
    
    def _handle_resize(self):
        if hasattr(self, 'all_sessions'):
            self.update_page_display()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            event.ignore()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            event.ignore()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = QPoint()
            event.accept()
    
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_applications()
    
    def hideEvent(self, event):
        super().hideEvent(event)
        if hasattr(self, '_filter_timer') and self._filter_timer:
            self._filter_timer.stop()
        if hasattr(self, '_resize_timer') and self._resize_timer:
            self._resize_timer.stop()
    
    def closeEvent(self, event):
        if hasattr(self, '_filter_timer') and self._filter_timer:
            self._filter_timer.stop()
        if hasattr(self, '_resize_timer') and self._resize_timer:
            self._resize_timer.stop()
        
        event.ignore()
        self.app.hide_overlay()
    
    def apply_styles(self):
        self.setStyleSheet(StyleSheets.get_overlay_stylesheet())
        
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
        
        for app_control in self.app_controls.values():
            if hasattr(app_control, 'apply_styles'):
                app_control.apply_styles()
        
        self.update()
    
    def __del__(self):
        try:
            if hasattr(self, '_filter_timer') and self._filter_timer:
                self._filter_timer.stop()
            if hasattr(self, '_resize_timer') and self._resize_timer:
                self._resize_timer.stop()
        except Exception:
            pass
