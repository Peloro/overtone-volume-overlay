<p align="center">
  <img src="assets/icon2.png" alt="Overtone Logo" width="200"/>
</p>

# Overtone - Volume Mixer Overlay for Windows

A modern, lightweight volume mixer overlay for Windows with per-application volume control, built with Python and PyQt5.

## Features

- 🎚️ **Per-Application Volume Control** - Individual sliders for each running application
- 🔊 **System Volume Control** - Master volume with quick mute/unmute
- 🎯 **Always-on-Top Overlay** - Draggable window that stays above other applications
- ⌨️ **Global Hotkeys** - Customizable keyboard shortcuts
- 🔍 **Application Filter** - Search and filter applications by name
- 🎨 **Theme Customization** - Customize all colors and appearance
- 👤 **Profile Management** - Multiple settings profiles for different use cases
- 💾 **System Tray Integration** - Runs in the background
- ✏️ **Editable Volume Values** - Click any percentage to type a precise value

## Installation

**Requirements:** Windows 10/11, Python 3.8+

```bash
git clone https://github.com/Peloro/overtone-volume-overlay.git
cd overtone-volume-overlay
pip install -r requirements.txt
python main.py
```

## Usage

**Default Hotkeys:**
- `Ctrl+/` - Toggle overlay
- `Ctrl+Shift+S` - Open settings
- `Ctrl+Q` - Quit application

**Controls:**
- Drag title bar to move window
- Click volume numbers to type precise values
- Use filter button (⌕) to search applications
- Navigate pages with arrow buttons (◀ ▶)
- Customize everything in Settings (⚙️)

## Configuration

Settings are automatically saved in `profiles.json`. Create multiple profiles for different use cases (Work, Gaming, etc.). All settings persist across sessions.

## Contributing

Contributions welcome! Fork the repository, create a feature branch, and submit a pull request. Follow PEP 8 style guidelines.

**Areas to contribute:** Bug fixes, new features, documentation, UI/UX improvements, performance optimization.

## License

MIT License - Copyright (c) 2025 Peloro

## Author

**Peloro** - [@Peloro](https://github.com/Peloro)

Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) and [pycaw](https://github.com/AndreMiras/pycaw)
