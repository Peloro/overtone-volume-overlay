"""
Overtone Application
A system tray application for controlling volume of individual applications
"""
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from utils.logger import setup_logger
from utils import set_window_icon

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
        
        try:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Overtone - Fatal Error")
            error_dialog.setText("Failed to start Overtone")
            error_dialog.setInformativeText(str(e))
            error_dialog.setDetailedText(traceback.format_exc())
            error_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            set_window_icon(error_dialog)
            error_dialog.exec_()
        except Exception:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
