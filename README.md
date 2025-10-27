<p align="center">
  <img src="assets/icon2.png" alt="Overtone Logo" width="200"/>
</p>

# Overtone - Volume Mixer Overlay for Windows

A modern, lightweight volume mixer overlay for Windows with per-application volume control, built with Python and PyQt5.

## Features

- 🎚️ **Per-Application Volume Control** - Individual volume sliders for each running application
- 🔊 **System Volume Control** - Master volume control with quick mute/unmute
- 🎯 **Always-on-Top Overlay** - Frameless, draggable window that stays above other applications
- ⌨️ **Global Hotkeys** - Control the overlay from anywhere with customizable keyboard shortcuts
- 📄 **Smart Pagination** - Automatically adjusts to show complete application controls based on window size
- 💾 **System Tray Integration** - Runs in the background, accessible from the system tray
- ✏️ **Editable Volume Values** - Click any volume number to type a precise value
- 🎨 **Modern Dark UI** - Clean, minimalist interface with smooth controls

- ## Requirements

- Windows 10/11
- Python 3.8 or higher
- Administrator privileges (required for global hotkeys)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Peloro/overtone-volume-overlay.git
cd overtone-volume-overlay
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Application

Run the application with:
```bash
python main.py
```

The application starts minimized to the system tray. Double-click the tray icon or use the hotkey to open the overlay.

### Default Hotkeys

- **Ctrl+Shift+V** - Toggle Overtone overlay
- **Ctrl+Shift+S** - Open settings
- **Ctrl+Shift+Q** - Quit application

Note: On Windows, registering system-wide hotkeys typically requires administrator privileges. This application requests admin rights when built as an executable so the hotkeys work globally.

### Controls

**Overtone Overlay:**
- Drag the title bar to move the window
- Use sliders to adjust volume (0-100%)
- Click volume numbers to type exact values
- Click mute buttons (🔊/🔇) to toggle mute
- Use arrow buttons (◀ ▶) to navigate between pages
- Click ⚙️ to open settings
- Click × to hide the overlay

**Pagination:**
- The overlay automatically calculates how many applications fit in the current window size
- Resize the window to show more or fewer applications per page
- Use the navigation buttons to scroll through your applications

### Settings

Access settings via the system tray menu or hotkey (Ctrl+Shift+S):

- **Width/Height** - Customize overlay dimensions (300-1000px)
- **Opacity** - Adjust window transparency (0.1-1.0)
- **Hotkeys** - Configure custom keyboard shortcuts (format: ctrl+shift+key)

## Technical Details

### Architecture

- **volume_overlay.py** - Main application logic and UI
- **audio_controller.py** - Windows audio session management (pycaw)
- **system_tray.py** - System tray icon and menu
- **settings_dialog.py** - Configuration interface
- **main.py** - Application entry point

### Dependencies

- **PyQt5** - GUI framework
- **pycaw** - Windows Core Audio API wrapper
- **keyboard** - Global hotkey registration
- **comtypes** - COM interface support

## Configuration

Settings are automatically saved to `settings.json` in the application directory. The file includes:
- Window dimensions
- Opacity (adjustable in settings)
- Custom hotkey bindings

## Development

### Running from Source

```bash
# Install development dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Building

To create a standalone executable:

1. Ensure PyInstaller is installed:
```bash
pip install pyinstaller
```

2. Build the executable using the provided spec file:
```bash
python -m PyInstaller Overtone.spec --clean
```

Or simply run the build script:
```bash
build.bat
```

The executable will be created in the `dist` folder as `Overtone.exe`. This is a single-file executable that can be distributed without requiring Python installation.

**Note:** The first build may take several minutes as PyInstaller analyzes dependencies and packages everything together.

## Known Issues

- Requires administrator privileges for global hotkey functionality
- Some applications may not expose volume controls (system processes, protected apps)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- Audio control powered by [pycaw](https://github.com/AndreMiras/pycaw)

## Author

**Peloro**
- GitHub: [@Peloro](https://github.com/Peloro)

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/Peloro/overtone-volume-overlay/issues) on GitHub.
