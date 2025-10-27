"""
Main Overtone Application Class
Coordinates all components and manages application lifecycle
"""
import sys
from typing import Optional
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMessageBox
import keyboard

from config import SettingsManager, UIConstants
from controllers import AudioController
from ui import VolumeOverlay, SettingsDialog, SystemTrayIcon
from .hotkey_handler import HotkeyHandler


class VolumeOverlayApp:
    """Main application coordinator"""
    
    def __init__(self) -> None:
        self.settings_manager = SettingsManager()
        
        self.audio_controller = AudioController()
        
        self.overlay = VolumeOverlay(self)
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
    
    def _validate_hotkey_format(self, hotkey: str) -> bool:
        """Validate hotkey format before registration"""
        if not hotkey or not isinstance(hotkey, str):
            return False
        # Basic validation: check if it contains valid modifier keys
        valid_modifiers = ['ctrl', 'shift', 'alt', 'win']
        parts = hotkey.lower().split('+')
        if len(parts) < 2:
            return False
        # At least one modifier and one key
        has_modifier = any(mod in parts for mod in valid_modifiers)
        return has_modifier
    
    def _unregister_hotkeys(self) -> None:
        """Unregister only our hotkeys"""
        for hotkey_ref in self._registered_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey_ref)
            except (KeyError, ValueError):
                pass  # Hotkey wasn't registered or already removed
        self._registered_hotkeys.clear()
    
    def setup_hotkeys(self) -> None:
        """Setup global hotkeys"""
        # First, unregister existing hotkeys
        self._unregister_hotkeys()
        
        hotkeys_to_register = [
            (self.settings_manager.hotkey_open, self.hotkey_handler.toggle_signal.emit),
            (self.settings_manager.hotkey_settings, self.hotkey_handler.settings_signal.emit),
            (self.settings_manager.hotkey_quit, self.hotkey_handler.quit_signal.emit),
        ]
        
        for hotkey, callback in hotkeys_to_register:
            if not self._validate_hotkey_format(hotkey):
                print(f"Warning: Invalid hotkey format: {hotkey}")
                continue
            
            try:
                hotkey_ref = keyboard.add_hotkey(
                    hotkey,
                    callback,
                    suppress=False
                )
                self._registered_hotkeys.append(hotkey_ref)
            except Exception as e:
                print(f"Error registering hotkey '{hotkey}': {e}")
    
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
        self.overlay.hide()
        self.refresh_timer.stop()
    
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
        self.overlay.resize(
            self.settings_manager.overlay_width,
            self.settings_manager.overlay_height
        )
        self.overlay.update_background_opacity()
        self.setup_hotkeys()
        self.settings_manager.save_settings()
    
    def confirm_quit(self) -> None:
        """Show confirmation dialog before quitting (if enabled in settings)"""
        # Check if confirmation is enabled
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
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
            QPushButton {
                background-color: #424242;
                color: white;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 5px 15px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:default {
                background-color: #1e88e5;
                border: 1px solid #1565c0;
            }
            QPushButton:default:hover {
                background-color: #42a5f5;
            }
        """)
        
        msg_box.show()
        msg_box.raise_()
        msg_box.activateWindow()
        
        result = msg_box.exec_()
        if result == QMessageBox.Yes:
            self.quit_application()
    
    def quit_application(self) -> None:
        """Quit the application"""
        self.refresh_timer.stop()
        
        # Unregister our hotkeys
        self._unregister_hotkeys()
        
        # Cleanup audio controller
        if hasattr(self, 'audio_controller'):
            self.audio_controller.cleanup()
        
        self.tray_icon.hide()
        self.overlay.close()
        self.settings_dialog.close()
        sys.exit(0)
