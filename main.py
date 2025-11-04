"""
Overtone Application
A system tray application for controlling volume of individual applications
"""
import sys
import traceback
import atexit
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from utils.logger import setup_logger
from utils import set_window_icon

logger = setup_logger("overtone", "overtone.log")

# Global reference to the application instance for cleanup
_app_instance = None

def cleanup_on_exit():
    """Cleanup function to ensure proper shutdown of COM objects"""
    global _app_instance
    try:
        if _app_instance is not None:
            logger.debug("Performing final cleanup on exit")
            # Ensure audio controller is cleaned up
            if hasattr(_app_instance, 'audio_controller') and _app_instance.audio_controller is not None:
                try:
                    _app_instance.audio_controller.cleanup()
                    _app_instance.audio_controller = None
                except Exception as e:
                    logger.debug(f"Error in exit cleanup: {e}")
            
            # Force garbage collection
            import gc
            gc.collect()
            
            _app_instance = None
    except Exception as e:
        logger.debug(f"Error in cleanup_on_exit: {e}")

def main() -> int:
    """Main entry point for the application"""
    global _app_instance
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Register cleanup function to run before interpreter exits
    atexit.register(cleanup_on_exit)
    
    try:
        from core import VolumeOverlayApp
        overlay_app = VolumeOverlayApp()
        _app_instance = overlay_app  # Store global reference for cleanup
        logger.info("Overtone application started successfully")
        
        result = app.exec_()
        
        # Explicitly cleanup before returning
        logger.debug("Application event loop finished, performing cleanup")
        _app_instance = None
        
        # Force garbage collection after Qt event loop exits
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
        except Exception:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
