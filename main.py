"""
Overtone Application
A system tray application for controlling volume of individual applications
"""
import sys
from PyQt5.QtWidgets import QApplication
from core import VolumeOverlayApp

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    try:
        overlay_app = VolumeOverlayApp()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
