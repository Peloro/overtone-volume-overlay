"""
Main Overtone Application Class
Coordinates all components and manages application lifecycle
"""
import sys
import os
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
import keyboard

from config import SettingsManager, UIConstants
from controllers import AudioController
from ui import VolumeOverlay, SettingsDialog, SystemTrayIcon
from .hotkey_handler import HotkeyHandler
from utils.logger import get_logger

logger = get_logger(__name__)


class VolumeOverlayApp:
    """Main application coordinator"""
    
    # Hotkey validation constants
    _VALID_MODIFIERS = {'ctrl', 'shift', 'alt', 'win'}
    _VALID_KEYS = {
        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
        'esc', 'tab', 'space', 'enter', 'backspace', 'delete', 'insert',
        'home', 'end', 'pageup', 'pagedown', 'up', 'down', 'left', 'right'
    }
    
    def __init__(self) -> None:
        self.settings_manager = SettingsManager()
        
        self.audio_controller = AudioController()
        
        self.overlay = VolumeOverlay(self)
        self.overlay.hide()  # Start hidden to prevent flash on startup
        self.settings_dialog = SettingsDialog(self)
        
        self.tray_icon = SystemTrayIcon(self)
        self.tray_icon.show()
        
        self.hotkey_handler = HotkeyHandler()
        self.hotkey_handler.toggle_signal.connect(self.toggle_overlay)
        self.hotkey_handler.settings_signal.connect(self.show_settings)
        self.hotkey_handler.quit_signal.connect(self.confirm_quit)
        
        # Store hotkey references for cleanup
        self._registered_hotkeys: list = []
        
        self.setup_hotkeys()
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_applications)
        
        logger.info("VolumeOverlayApp initialized successfully")
    
    def _validate_hotkey_format(self, hotkey: str) -> bool:
        """Validate hotkey format before registration"""
        if not hotkey or not isinstance(hotkey, str):
            return False
        
        parts = hotkey.lower().split('+')
        
        # Must have at least modifier + key
        if len(parts) < 2:
            return False
        
        # Check for valid modifiers
        has_modifier = any(mod in parts for mod in self._VALID_MODIFIERS)
        
        if not has_modifier:
            return False
        
        # Last part should be the key (not a modifier)
        key_part = parts[-1]
        if key_part in self._VALID_MODIFIERS:
            logger.warning(f"Hotkey '{hotkey}' has no key specified")
            return False
        
        # Check for valid key length (single char or known key names)
        if len(key_part) > 1 and key_part not in self._VALID_KEYS:
            logger.warning(f"Hotkey '{hotkey}' has invalid key: {key_part}")
            return False
        
        return True
    
    def _unregister_hotkeys(self) -> None:
        """Unregister only our hotkeys"""
        for hotkey_ref in self._registered_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey_ref)
                logger.debug(f"Unregistered hotkey")
            except (KeyError, ValueError) as e:
                logger.debug(f"Hotkey already unregistered or invalid: {e}")
            except Exception as e:
                logger.error(f"Unexpected error unregistering hotkey: {e}")
        self._registered_hotkeys.clear()
    
    def setup_hotkeys(self) -> None:
        """Setup global hotkeys"""
        self._unregister_hotkeys()
        
        for hotkey, callback in [
            (self.settings_manager.hotkey_open, self.hotkey_handler.toggle_signal.emit),
            (self.settings_manager.hotkey_settings, self.hotkey_handler.settings_signal.emit),
            (self.settings_manager.hotkey_quit, self.hotkey_handler.quit_signal.emit),
        ]:
            if self._validate_hotkey_format(hotkey):
                try:
                    self._registered_hotkeys.append(keyboard.add_hotkey(hotkey, callback, suppress=False))
                    logger.debug(f"Registered hotkey: {hotkey}")
                except Exception as e:
                    logger.error(f"Error registering hotkey '{hotkey}': {e}")
            else:
                logger.warning(f"Invalid hotkey format: {hotkey}")
    
    def toggle_overlay(self) -> None:
        """Toggle overlay visibility"""
        if self.overlay.isVisible():
            self.hide_overlay()
        else:
            self.show_overlay()
    
    def show_overlay(self) -> None:
        """Show the overlay"""
        self.refresh_applications()
        self.overlay.show()
        self.overlay.activateWindow()
        self.overlay.raise_()
        self.refresh_timer.start(UIConstants.REFRESH_INTERVAL)
    
    def hide_overlay(self) -> None:
        """Hide the overlay"""
        self.refresh_timer.stop()
        
        # Clear app controls before hiding to prevent dangling references
        if hasattr(self.overlay, 'clear_all_controls'):
            self.overlay.clear_all_controls()
        
        self.overlay.hide()
    
    def show_settings(self) -> None:
        """Show settings dialog"""
        self.settings_dialog.show()
        self.settings_dialog.activateWindow()
        self.settings_dialog.raise_()
    
    def refresh_applications(self) -> None:
        """Refresh the list of applications"""
        self.overlay.refresh_applications()
    
    def update_settings(self) -> None:
        """Update application with new settings"""
        self.overlay.resize(self.settings_manager.overlay_width, self.settings_manager.overlay_height)
        self.overlay.update_background_opacity()
        self.setup_hotkeys()
        self.settings_manager.save_settings()
    
    def confirm_quit(self) -> None:
        """Show confirmation dialog before quitting (if enabled in settings)"""
        if not self.settings_manager.confirm_on_quit:
            self.quit_application()
            return
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Confirm Quit")
        msg_box.setText("Are you sure you want to quit Overtone?")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        
        # Set window icon (use .ico for better Windows compatibility)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon2_black.ico')
        if os.path.exists(icon_path):
            msg_box.setWindowIcon(QIcon(icon_path))
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #2b2b2b; color: white; }
            QMessageBox QLabel { color: white; }
            QPushButton {
                background-color: #424242; color: white; border: 1px solid #666;
                border-radius: 3px; padding: 5px 15px; min-width: 60px;
            }
            QPushButton:hover { background-color: #555; }
            QPushButton:default { background-color: #1e88e5; border: 1px solid #1565c0; }
            QPushButton:default:hover { background-color: #42a5f5; }
        """)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self.quit_application()
    
    def quit_application(self) -> None:
        """Quit the application"""
        logger.info("Shutting down Overtone application")
        self.refresh_timer.stop()
        self._unregister_hotkeys()
        if hasattr(self, 'audio_controller'):
            self.audio_controller.cleanup()
        
        for widget in (self.tray_icon, self.overlay, self.settings_dialog):
            if hasattr(widget, 'hide'):
                widget.hide()
            if hasattr(widget, 'close'):
                widget.close()
        sys.exit(0)
