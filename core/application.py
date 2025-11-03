"""
Main Overtone Application Class
Coordinates all components and manages application lifecycle
"""
import sys
import os
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QIcon
import keyboard

from config import SettingsManager, UIConstants, Colors
from controllers import AudioController
from ui import VolumeOverlay, SystemTrayIcon
from .hotkey_handler import HotkeyHandler
from utils.logger import get_logger
from utils import batch_update

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
        
        # Initialize Colors with settings manager for customization
        Colors.set_settings_manager(self.settings_manager)
        
        self.audio_controller = AudioController()
        
        self.overlay = VolumeOverlay(self)
        self.overlay.hide()  # Start hidden to prevent flash on startup
        self.settings_dialog = None  # Lazy initialization
        
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
        # Set timer to be coalesced for better performance
        self.refresh_timer.setTimerType(Qt.CoarseTimer)
        
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
                logger.debug("Unregistered hotkey")
            except (KeyError, ValueError) as e:
                logger.debug(f"Hotkey already unregistered or invalid: {e}")
            except Exception as e:
                logger.error(f"Unexpected error unregistering hotkey: {e}")
        self._registered_hotkeys.clear()
        
        # Ensure any remaining global keyboard hooks are removed
        try:
            # Try unhook_all first as it's more thorough
            if hasattr(keyboard, 'unhook_all'):
                keyboard.unhook_all()
                logger.debug("keyboard.unhook_all() called")
            elif hasattr(keyboard, 'unhook_all_hotkeys'):
                keyboard.unhook_all_hotkeys()
                logger.debug("keyboard.unhook_all_hotkeys() called")
        except Exception as e:
            logger.debug(f"Error while unhooking keyboard listeners: {e}")
    
    def setup_hotkeys(self) -> None:
        """Setup global hotkeys"""
        self._unregister_hotkeys()
        
        # Batch hotkey registration for better performance
        hotkey_configs = [
            (self.settings_manager.hotkey_open, self.hotkey_handler.toggle_signal.emit),
            (self.settings_manager.hotkey_settings, self.hotkey_handler.settings_signal.emit),
            (self.settings_manager.hotkey_quit, self.hotkey_handler.quit_signal.emit),
        ]
        
        for hotkey, callback in hotkey_configs:
            if not self._validate_hotkey_format(hotkey):
                logger.warning(f"Invalid hotkey format: {hotkey}")
                continue
                
            try:
                hotkey_ref = keyboard.add_hotkey(hotkey, callback, suppress=False)
                self._registered_hotkeys.append(hotkey_ref)
                logger.debug(f"Registered hotkey: {hotkey}")
            except Exception as e:
                logger.error(f"Error registering hotkey '{hotkey}': {e}")
    
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
        # Lazy initialization - only create when first shown
        if self.settings_dialog is None:
            from ui import SettingsDialog
            self.settings_dialog = SettingsDialog(self)
            
        self.settings_dialog.show()
        self.settings_dialog.activateWindow()
        self.settings_dialog.raise_()
    
    def refresh_applications(self) -> None:
        """Refresh the list of applications"""
        self.overlay.refresh_applications()
    
    def update_settings(self) -> None:
        """Update application with new settings"""
        # Use context manager for batch updates to reduce repaints
        with batch_update(self.overlay):
            self.overlay.resize(self.settings_manager.overlay_width, self.settings_manager.overlay_height)
            self.overlay.update_background_opacity()
        
        self.setup_hotkeys()
        self.settings_manager.save_settings()
    
    def confirm_quit(self) -> None:
        """Show confirmation dialog before quitting (if enabled in settings)"""
        if not self.settings_manager.confirm_on_quit:
            self.quit_application()
            return
        
        from utils import set_window_icon
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Confirm Quit")
        msg_box.setText("Are you sure you want to quit Overtone?")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        set_window_icon(msg_box)
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
        
        # Stop all timers first
        if hasattr(self, 'refresh_timer') and self.refresh_timer:
            self.refresh_timer.stop()
        
        # Disconnect hotkey signals to prevent any callbacks during shutdown
        if hasattr(self, 'hotkey_handler') and self.hotkey_handler:
            try:
                self.hotkey_handler.toggle_signal.disconnect()
                self.hotkey_handler.settings_signal.disconnect()
                self.hotkey_handler.quit_signal.disconnect()
            except Exception:
                pass
        
        # Unregister keyboard hooks BEFORE cleaning up UI
        self._unregister_hotkeys()
        
        # Hide and clean up overlay first (it has controls that reference audio_controller)
        if hasattr(self, 'overlay') and self.overlay is not None:
            try:
                self.overlay.hide()
                # Clear controls to break references
                if hasattr(self.overlay, 'clear_all_controls'):
                    self.overlay.clear_all_controls()
                self.overlay.close()
            except Exception as e:
                logger.debug(f"Error cleaning up overlay: {e}")
        
        # Clean up settings dialog
        if hasattr(self, 'settings_dialog') and self.settings_dialog is not None:
            try:
                self.settings_dialog.hide()
                self.settings_dialog.close()
            except Exception as e:
                logger.debug(f"Error cleaning up settings dialog: {e}")
        
        # Clean up tray icon
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            try:
                if hasattr(self.tray_icon, 'cleanup'):
                    self.tray_icon.cleanup()
                else:
                    self.tray_icon.hide()
                    self.tray_icon.setContextMenu(None)
            except Exception as e:
                logger.debug(f"Error cleaning up tray icon: {e}")
        
        # Clean up audio controller (releases COM objects)
        if hasattr(self, 'audio_controller') and self.audio_controller:
            try:
                self.audio_controller.cleanup()
            except Exception as e:
                logger.debug(f"Error cleaning up audio controller: {e}")
        
        # Schedule widget deletion after event loop processes pending events
        for widget in (self.tray_icon, self.overlay, self.settings_dialog):
            if widget is not None:
                try:
                    widget.deleteLater()
                except Exception:
                    pass
        
        # Use QTimer to delay quit slightly to allow cleanup to complete
        QTimer.singleShot(UIConstants.QUIT_DELAY_MS, lambda: QApplication.quit() if QApplication.instance() else sys.exit(0))
