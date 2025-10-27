"""
System Tray Icon and Menu
"""
import os
import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPolygon
from PyQt5.QtCore import Qt, QPoint
from utils.logger import get_logger

logger = get_logger(__name__)


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, app) -> None:
        self.app = app
        
        icon = self.create_icon()
        super().__init__(icon)
        
        self.setToolTip("Overtone")
        
        self.menu = QMenu()
        
        show_action = QAction("Show Overlay", self.menu)
        show_action.triggered.connect(self.on_show_overlay_clicked)
        self.menu.addAction(show_action)
        
        settings_action = QAction("Settings", self.menu)
        settings_action.triggered.connect(self.on_settings_clicked)
        self.menu.addAction(settings_action)
        
        self.menu.addSeparator()
        
        quit_action = QAction("Quit", self.menu)
        quit_action.triggered.connect(self.on_quit_clicked)
        self.menu.addAction(quit_action)
        
        self.setContextMenu(self.menu)
        
        self.activated.connect(self.on_activated)
    
    def create_icon(self) -> QIcon:
        """Create or load a tray icon, preserving transparency when available."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, 'assets')
        
        icon_files = ['icon2_black.ico', 'icon2.png'] if sys.platform.startswith('win') else ['icon2.png', 'icon2_black.ico']

        for icon_file in icon_files:
            icon_path = os.path.join(assets_dir, icon_file)
            
            # Skip if file doesn't exist
            if not os.path.exists(icon_path):
                continue

            # Try ICO on Windows
            if icon_file.endswith('.ico') and sys.platform.startswith('win'):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    logger.info(f"Loaded tray icon from ICO: {icon_path}")
                    return icon
                continue

            # Try PNG with alpha channel
            original = QPixmap(icon_path)
            if original.isNull():
                continue
            
            if icon_file.endswith('.png') and not original.hasAlphaChannel():
                continue

            icon = QIcon()
            for size in (16, 20, 24, 32, 40, 48):
                canvas = QPixmap(size, size)
                canvas.fill(Qt.transparent)
                painter = QPainter(canvas)
                painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
                scaled = original.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                offset = (size - scaled.width()) // 2, (size - scaled.height()) // 2
                painter.drawPixmap(*offset, scaled)
                painter.end()
                icon.addPixmap(canvas)

            logger.info(f"Loaded tray icon with alpha from: {icon_path}")
            return icon
        
        logger.warning("No icon files found, using fallback icon")
        return self._create_fallback_icon()
    
    def _create_fallback_icon(self) -> QIcon:
        """Create a simple fallback icon if no icon files are found"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(30, 136, 229))
        painter.setPen(Qt.NoPen)
        
        # Simple speaker icon - rectangle and triangle
        painter.drawRect(8, 12, 8, 8)
        painter.drawPolygon(QPolygon([QPoint(16, 12), QPoint(24, 8), QPoint(24, 24), QPoint(16, 20)]))
        
        painter.end()
        return QIcon(pixmap)
    
    def on_show_overlay_clicked(self) -> None:
        """Handle show overlay menu click"""
        self.app.show_overlay()
    
    def on_settings_clicked(self) -> None:
        """Handle settings menu click"""
        self.app.show_settings()
    
    def on_quit_clicked(self) -> None:
        """Handle quit menu click"""
        self.app.confirm_quit()
    
    def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.app.show_overlay()
