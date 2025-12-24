import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from utils import setup_logger, set_window_icon

logger = setup_logger("overtone", "overtone.log")


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    try:
        from core import VolumeOverlayApp
        overlay_app = VolumeOverlayApp()
        logger.info("Overtone application started successfully")
        
        result = app.exec_()
        
        logger.debug("Application event loop finished")
        
        # Final garbage collection after event loop exits
        import gc
        gc.collect()
        
        return result
        
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
        except Exception as e:
            logger.debug(f"Error displaying error dialog: {e}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
