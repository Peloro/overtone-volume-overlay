"""
System Tray Icon and Menu
"""
import os
import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPolygon
from PyQt5.QtCore import Qt, QPoint


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, app):
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
    
    def create_icon(self):
        """Create or load a tray icon, preserving transparency when available."""
        candidate_order = ['icon2.ico', 'icon2.png'] if sys.platform.startswith('win') else ['icon2.png', 'icon2.ico']
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, 'assets')

        for icon_file in candidate_order:
            icon_path = os.path.join(assets_dir, icon_file)
            if not os.path.exists(icon_path):
                continue

            if icon_file.lower().endswith('.ico') and sys.platform.startswith('win'):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    print(f"Loaded tray icon from ICO: {icon_path}")
                    return icon

            original = QPixmap(icon_path)
            if original.isNull():
                continue

            if icon_file.lower().endswith('.png') and not original.hasAlphaChannel():
                print(f"Skipping PNG without alpha channel: {icon_path}")
                continue

            icon = QIcon()
            for size in (16, 20, 24, 32, 40, 48):
                canvas = QPixmap(size, size)
                canvas.fill(Qt.transparent)
                painter = QPainter(canvas)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                scaled = original.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                x = (size - scaled.width()) // 2
                y = (size - scaled.height()) // 2
                painter.drawPixmap(x, y, scaled)
                painter.end()
                icon.addPixmap(canvas)

            print(f"Loaded tray icon with alpha from: {icon_path}")
            return icon
        
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setBrush(QColor(30, 136, 229))
        painter.setPen(QColor(30, 136, 229))
        
        painter.drawRect(10, 25, 15, 14)
        polygon = QPolygon([
            QPoint(25, 25),
            QPoint(35, 15),
            QPoint(35, 49),
            QPoint(25, 39)
        ])
        painter.drawPolygon(polygon)
        
        painter.setPen(QColor(30, 136, 229))
        painter.drawArc(38, 20, 15, 10, 0, 180 * 16)
        painter.drawArc(38, 34, 15, 10, 180 * 16, 180 * 16)
        painter.drawArc(45, 15, 15, 15, 0, 180 * 16)
        painter.drawArc(45, 34, 15, 15, 180 * 16, 180 * 16)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def on_show_overlay_clicked(self):
        """Handle show overlay menu click"""
        self.app.show_overlay()
    
    def on_settings_clicked(self):
        """Handle settings menu click"""
        self.app.show_settings()
    
    def on_quit_clicked(self):
        """Handle quit menu click"""
        self.app.confirm_quit()
    
    def on_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.app.show_overlay()
