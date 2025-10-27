"""
Main Overtone Application Class
Coordinates all components and manages application lifecycle
"""
import sys
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMessageBox
import keyboard

from config import SettingsManager, UIConstants
from controllers import AudioController
from ui import VolumeOverlay, SettingsDialog, SystemTrayIcon
from .hotkey_handler import HotkeyHandler


class VolumeOverlayApp:
    """Main application coordinator"""
    
    def __init__(self):
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
        
        self.setup_hotkeys()
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_applications)
    
    @property
    def settings(self):
        """Backward compatibility: return settings dict"""
        return self.settings_manager.settings
    
    def setup_hotkeys(self):
        """Setup global hotkeys"""
        try:
            keyboard.unhook_all()
        except:
            pass
        
        try:
            keyboard.add_hotkey(
                self.settings_manager.hotkey_open,
                self.hotkey_handler.toggle_signal.emit,
                suppress=False
            )
            keyboard.add_hotkey(
                self.settings_manager.hotkey_settings,
                self.hotkey_handler.settings_signal.emit,
                suppress=False
            )
            keyboard.add_hotkey(
                self.settings_manager.hotkey_quit,
                self.hotkey_handler.quit_signal.emit,
                suppress=False
            )
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
    
    def toggle_overlay(self):
        """Toggle overlay visibility"""
        if self.overlay.isVisible():
            self.hide_overlay()
        else:
            self.show_overlay()
    
    def show_overlay(self):
        """Show the overlay"""
        self.refresh_applications()
        self.overlay.show()
        self.overlay.activateWindow()
        self.overlay.raise_()
        self.refresh_timer.start(UIConstants.REFRESH_INTERVAL)
    
    def hide_overlay(self):
        """Hide the overlay"""
        self.overlay.hide()
        self.refresh_timer.stop()
    
    def show_settings(self):
        """Show settings dialog"""
        self.settings_dialog.show()
        self.settings_dialog.activateWindow()
        self.settings_dialog.raise_()
    
    def refresh_applications(self):
        """Refresh the list of applications"""
        self.overlay.refresh_applications()
    
    def update_settings(self):
        """Update application with new settings"""
        self.overlay.resize(
            self.settings_manager.overlay_width,
            self.settings_manager.overlay_height
        )
        self.overlay.update_background_opacity()
        self.setup_hotkeys()
        self.settings_manager.save_settings()
    
    def confirm_quit(self):
        """Show confirmation dialog before quitting"""
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
    
    def quit_application(self):
        """Quit the application"""
        self.refresh_timer.stop()
        try:
            keyboard.unhook_all()
        except:
            pass
        self.tray_icon.hide()
        self.overlay.close()
        self.settings_dialog.close()
        sys.exit(0)
