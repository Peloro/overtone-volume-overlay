"""
Overtone Application
A system tray application for controlling volume of individual applications
"""
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

def main() -> int:
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    try:
        from core import VolumeOverlayApp
        overlay_app = VolumeOverlayApp()
        return app.exec_()
    except Exception as e:
        print(f"Fatal error during initialization: {e}")
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
            error_dialog.exec_()
        except Exception:
            pass  # If even the error dialog fails, just print to console
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
