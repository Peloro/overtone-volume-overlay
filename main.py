"""
Overtone Application
A system tray application for controlling volume of individual applications
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from utils.logger import setup_logger

# Setup logging
logger = setup_logger("overtone", "overtone.log")

def main() -> int:
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    try:
        from core import VolumeOverlayApp
        overlay_app = VolumeOverlayApp()
        logger.info("Overtone application started successfully")
        return app.exec_()
    except Exception as e:
        logger.critical(f"Fatal error during initialization: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        
        # Show error dialog to user
        try:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Overtone - Fatal Error")
            error_dialog.setText("Failed to start Overtone")
            error_dialog.setInformativeText(str(e))
            error_dialog.setDetailedText(traceback.format_exc())
            error_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            
            # Set window icon (use .ico for better Windows compatibility)
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon2_black.ico')
            if os.path.exists(icon_path):
                error_dialog.setWindowIcon(QIcon(icon_path))
            
            error_dialog.exec_()
        except Exception:
            pass  # If even the error dialog fails, just print to console
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
