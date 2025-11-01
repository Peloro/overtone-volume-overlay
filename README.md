<p align="center">
  <img src="assets/icon2.png" alt="Overtone Logo" width="200"/>
</p>

# Overtone - Volume Mixer Overlay for Windows

A modern, lightweight volume mixer overlay for Windows with per-application volume control, built with Python and PyQt5.

## Features

### Core Functionality
- 🎚️ **Per-Application Volume Control** - Individual volume sliders for each running application with real-time updates
- 🔊 **System Volume Control** - Master volume control with quick mute/unmute (can be toggled on/off)
- 🎯 **Always-on-Top Overlay** - Frameless, draggable window that stays above other applications
- ⌨️ **Global Hotkeys** - Control the overlay from anywhere with customizable keyboard shortcuts
- 📄 **Smart Pagination** - Automatically calculates and adjusts displayed applications based on window size
- 💾 **System Tray Integration** - Runs in the background, accessible from the system tray
- ✏️ **Editable Volume Values** - Click any volume number to type a precise value (0-100%)

### Advanced Features
- 🔍 **Application Filter** - Search and filter applications by name with real-time results
  - Toggle filter bar on/off or set it to always show
  - Clear button for quick filter reset
  - Debounced search for optimal performance
- 🎨 **Full Theme Customization** - Customize all colors including:
  - Background colors (title bar, master control, container, app controls)
  - Slider colors (master and app sliders)
  - Button colors (primary and close buttons)
  - Text colors
  - One-click reset to defaults
- 👤 **Profile Management** - Create, switch, and manage multiple settings profiles
  - Save different configurations for different use cases
  - Switch between profiles instantly
  - Rename and delete custom profiles
  - Protected default profile that can't be deleted
- ⚙️ **Comprehensive Settings** - Fine-tune every aspect:
  - Adjustable window size (300-1000px)
  - Opacity control (0.1-1.0)
  - Customizable hotkeys for all actions
  - Behavior options (quit confirmation, system volume visibility, filter display mode)

## Screenshots

<!-- Add screenshots here to showcase the application -->
<!-- Example:
![Main Overlay](screenshots/overlay.png)
![Settings Dialog](screenshots/settings.png)
![Color Customization](screenshots/colors.png)
![Profile Management](screenshots/profiles.png)
-->

*Screenshots coming soon! Feel free to contribute screenshots of your setup.*

## What's New in Version 1.0.0

- ✨ **Profile System** - Create and manage multiple settings configurations
- 🎨 **Full Theme Customization** - Customize every color in the interface
- 🔍 **Application Filter** - Search and filter applications by name
- ⚙️ **Enhanced Settings** - Tabbed interface with organized options
- 🎛️ **Toggleable System Volume** - Show/hide master volume control
- 💡 **Smart Filter Display** - Toggle filter bar or set to always show
- 🚀 **Performance Improvements** - Debounced events, optimized rendering
- 🧹 **Better Resource Management** - Proper cleanup and memory handling
- 📝 **Comprehensive Logging** - Detailed logs for troubleshooting

## Requirements

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

## Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Run Overtone**: `python main.py`
3. **Access from tray**: Look for the Overtone icon in your system tray
4. **Open overlay**: Press `Ctrl+Shift+V` or double-click the tray icon
5. **Customize**: Press `Ctrl+Shift+S` to open settings

That's it! You're ready to control your application volumes.

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

All hotkeys are fully customizable in settings!

### Controls

**Overtone Overlay:**
- **Title Bar**: Drag to move the window anywhere on screen
- **Volume Sliders**: Use sliders or mouse scroll wheel to adjust volume (0-100%)
- **Volume Values**: Click on any volume percentage to type a precise value
- **Mute Buttons**: Click 🔊/🔇 to toggle mute for individual apps or system
- **Filter Button (⌕)**: Toggle the application filter bar (unless set to always show)
- **Settings Button (⚙️)**: Open the settings dialog
- **Minimize Button (—)**: Hide overlay to system tray
- **Close Button (×)**: Quit the application (with optional confirmation)

**Application Filter:**
- Click the search icon (⌕) or set to always show in settings
- Type to filter applications in real-time
- Click × in filter box to clear
- Filtered results update pagination automatically

**Pagination:**
- Smart automatic calculation based on window height
- Accounts for visible/hidden system volume and filter bar
- Use arrow buttons (◀ ▶) to navigate between pages
- Page counter shows current position (e.g., "1 / 3")
- Resize the window to display more or fewer applications per page

### Settings

Access settings via the system tray menu or hotkey (Ctrl+Shift+S). The settings dialog has four tabs:

#### Settings Tab
- **Overlay Size**: Width and height (300-1000px) with real-time preview
- **Appearance**: Opacity slider (0.1-1.0) with live updates
- **Behavior Options**:
  - Confirm on quit - Ask before closing the application
  - Show system volume - Display/hide master volume control
  - Always show filter - Keep filter bar visible or toggle on demand
- **Hotkeys**: Customize all keyboard shortcuts with format hints

#### Colors Tab
Full theme customization with color pickers for:
- **Background Colors**: Title bar, master control, container, app controls
- **Slider Colors**: Master slider handle, app slider handles
- **Button Colors**: Primary buttons, close button
- **Text Colors**: All text elements
- **Reset to Defaults**: One-click restore of default color scheme

#### Profiles Tab
Manage multiple settings configurations:
- **Active Profile Display**: Shows current profile with unsaved changes indicator
- **Profile List**: All available profiles with active/default markers
- **Actions**:
  - Switch to Selected - Load a different profile
  - Save to Active Profile - Save current settings
  - New Profile - Create new profile based on current settings
  - Rename - Rename custom profiles (default protected)
  - Delete - Remove custom profiles (default protected)

#### About Tab
- Application information and version
- Feature list
- Author and repository links
- License information

## Tips & Tricks

### Workflow Optimization
- **Quick Access**: Keep the overlay on a secondary monitor for always-visible controls
- **Profile Switching**: Create profiles for different scenarios (e.g., "Work", "Gaming", "Streaming")
- **Filter Shortcuts**: Use the filter to quickly find applications when you have many running
- **Resize for Density**: Make the window taller to see more apps at once, or shorter for a compact view

### Customization Ideas
- **Theme Matching**: Customize colors to match your desktop theme or favorite color scheme
- **Minimal Setup**: Hide the system volume control if you only need per-app controls
- **Always-Visible Filter**: Enable "Always show filter" if you frequently search for apps
- **Opacity Tweaks**: Lower opacity for a subtle overlay that doesn't obstruct your view

### Hotkey Suggestions
- Keep default hotkeys or customize to avoid conflicts with other applications
- Use memorable combinations like `Ctrl+Alt+V` for volume overlay
- Set quick access to settings for frequent adjustments

### Troubleshooting
- **Hotkeys Not Working**: Ensure the application is running with administrator privileges
- **Apps Not Showing**: Some system apps may not expose audio sessions - this is normal
- **Performance**: If you have many audio apps, use the filter to reduce visible items
- **Color Changes Not Applying**: Try switching profiles or restarting the overlay

## Technical Details

### Architecture

The application follows a modular MVC-inspired architecture:

**Core Components:**
- `core/application.py` - Main application coordinator and lifecycle manager
- `core/hotkey_handler.py` - Global hotkey signal handler

**Controllers:**
- `controllers/audio_controller.py` - Windows audio session management (pycaw wrapper)

**UI Components:**
- `ui/main_window.py` - Main overlay window (VolumeOverlay class)
- `ui/app_control.py` - Individual application volume controls
- `ui/master_control.py` - System master volume control
- `ui/settings_dialog.py` - Settings dialog with tabbed interface
- `ui/system_tray.py` - System tray icon and menu
- `ui/base_volume_control.py` - Base class for volume controls

**Configuration:**
- `config/settings_manager.py` - Settings persistence and management
- `config/profiles_manager.py` - Profile system for multiple configurations
- `config/colors.py` - Theme color management
- `config/styles.py` - Stylesheet generation
- `config/ui_constants.py` - UI constants and defaults
- `config/app_info.py` - Application metadata

**Utilities:**
- `utils/logger.py` - Logging configuration
- `utils/ui_helpers.py` - UI helper functions

**Entry Point:**
- `main.py` - Application initialization with error handling

### Key Features Implementation

**Performance Optimizations:**
- Debounced resize events (100ms) to reduce unnecessary recalculations
- Debounced filter search (configurable) for smooth typing
- Coarse timer for application refresh (500ms)
- Batch UI updates with setUpdatesEnabled for smoother rendering
- Session diffing to avoid unnecessary UI updates
- Efficient memory cleanup with proper widget deletion

**Profile System:**
- JSON-based profile storage in `profiles.json`
- Active profile tracking
- Default profile protection (cannot be deleted/renamed)
- Profile switching with automatic settings reload
- Unsaved changes tracking with visual indicator

**Color Customization:**
- Dynamic stylesheet generation based on user colors
- RGBA and hex color support
- Real-time color preview in settings
- Cascading style updates across all components

**Hotkey Management:**
- Validation of hotkey format before registration
- Proper cleanup of keyboard hooks on exit
- Signal-based hotkey handling for thread safety
- Support for modifier keys (ctrl, shift, alt, win) and special keys

### Dependencies

- **PyQt5** (5.15+) - Modern GUI framework with extensive widget library
- **pycaw** - Windows Core Audio API wrapper for audio control
- **keyboard** - Global hotkey registration and handling
- **comtypes** - COM interface support for Windows APIs

## Configuration

Settings are automatically saved and managed through two JSON files:

### `settings.json`
Contains the current active settings (deprecated, now uses profiles):
- Window dimensions (width, height)
- Opacity level
- Color theme customizations
- Behavioral settings
- Custom hotkey bindings

### `profiles.json`
Contains all saved profiles:
```json
{
  "profiles": {
    "Default": { /* default settings */ },
    "Work": { /* work profile settings */ },
    "Gaming": { /* gaming profile settings */ }
  },
  "active_profile": "Default"
}
```

Both files are automatically created with defaults if not found. Changes are saved with debouncing (500ms) to reduce disk I/O, except for explicit user actions which save immediately.

## Development

### Running from Source

```bash
# Install development dependencies
pip install -r requirements.txt

# Run the application
python main.py
```


### Project Structure

```
Overtone/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── settings.json          # User settings (legacy)
├── profiles.json          # Profile configurations
├── core/                  # Core application logic
│   ├── application.py     # Main app coordinator
│   └── hotkey_handler.py  # Hotkey signal handler
├── controllers/           # Business logic controllers
│   └── audio_controller.py # Audio session management
├── ui/                    # User interface components
│   ├── main_window.py     # Main overlay window
│   ├── app_control.py     # App volume controls
│   ├── master_control.py  # System volume control
│   ├── settings_dialog.py # Settings UI
│   ├── system_tray.py     # System tray integration
│   └── base_volume_control.py # Base control class
├── config/                # Configuration management
│   ├── settings_manager.py    # Settings persistence
│   ├── profiles_manager.py    # Profile management
│   ├── colors.py             # Theme colors
│   ├── styles.py             # Stylesheet generation
│   ├── ui_constants.py       # UI constants
│   └── app_info.py           # App metadata
├── utils/                 # Utility functions
│   ├── logger.py          # Logging setup
│   └── ui_helpers.py      # UI helper functions
└── assets/                # Images and icons
    └── icon2.png
```

## Contributing

Contributions are welcome! Here's how you can help:

### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone https://github.com/Peloro/overtone-volume-overlay.git
   cd overtone-volume-overlay
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the existing code style and architecture
   - Add comments for complex logic
   - Test your changes thoroughly

4. **Submit a Pull Request**
   - Describe your changes clearly
   - Reference any related issues
   - Ensure all features work as expected

### Areas for Contribution

- 🐛 **Bug Fixes** - Report or fix bugs you encounter
- ✨ **New Features** - Propose and implement new functionality
- 📝 **Documentation** - Improve README, code comments, or wiki
- 🎨 **UI/UX** - Enhance the user interface and experience
- 🧪 **Testing** - Add tests or improve test coverage
- 🌍 **Localization** - Add support for multiple languages
- ⚡ **Performance** - Optimize code for better performance

### Code Guidelines

- Follow PEP 8 style guidelines for Python code
- Use type hints where appropriate
- Keep functions focused and well-documented
- Maintain the existing project structure
- Test on Windows 10 and Windows 11 if possible


## License

This project is open source and available under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2025 Peloro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- Audio control powered by [pycaw](https://github.com/AndreMiras/pycaw)

## Author

**Peloro**
- GitHub: [@Peloro](https://github.com/Peloro)


## FAQ

### General Questions

**Q: Why does the application need administrator privileges?**  
A: Administrator privileges are required for global hotkey registration on Windows. Without them, hotkeys won't work outside the application window.

**Q: Can I use Overtone on multiple monitors?**  
A: Yes! The overlay can be dragged to any position on any monitor and will remember its location.

**Q: Does Overtone work with all applications?**  
A: Overtone works with any application that uses the Windows audio session API. Some system applications may not expose their audio sessions.

**Q: Will my settings be saved when I close the application?**  
A: Yes, all settings are automatically saved to `profiles.json`. The current profile's settings persist across sessions.

### Profiles

**Q: What's the difference between profiles and settings?**  
A: Profiles allow you to save complete sets of settings and switch between them instantly. You can have different profiles for work, gaming, or any other use case.

**Q: Can I delete the Default profile?**  
A: No, the Default profile is protected and cannot be deleted or renamed. It serves as a fallback and reference.

**Q: What happens to unsaved changes when I switch profiles?**  
A: Changes are marked with an asterisk (*) in the Profiles tab. You can save them to the current profile or switch without saving to discard changes.

### Customization

**Q: Can I change the color scheme?**  
A: Yes! The Colors tab in settings allows you to customize every color in the interface, including backgrounds, sliders, buttons, and text.

**Q: How do I reset colors to default?**  
A: In the Colors tab, click the "Reset Colors to Default" button at the bottom.

**Q: Can I hide the system volume control?**  
A: Yes, in Settings → Settings tab, uncheck "Show system volume control in overlay".

### Troubleshooting

**Q: The overlay isn't showing when I press the hotkey**  
A: Ensure the application is running (check system tray). Also verify your hotkey isn't conflicting with another application.

**Q: Some applications aren't showing in the list**  
A: Only applications actively playing or capable of playing audio appear in the list. Some system apps may not expose audio sessions.

**Q: The application crashes on startup**  
A: Check the `overtone.log` file in the application directory for error details. You may need to delete `settings.json` and `profiles.json` to reset to defaults.

**Q: Hotkeys stopped working after changing them**  
A: Ensure your hotkey format is correct (e.g., `ctrl+shift+v`). Invalid formats will prevent registration. Check the log file for validation errors.

## Support

If you encounter any issues or have questions:

- 📝 **Report Bugs**: [Open an issue](https://github.com/Peloro/overtone-volume-overlay/issues) on GitHub
- 💡 **Request Features**: Use the GitHub issues page to suggest new features
- 📖 **Documentation**: Check this README and the About tab in the application
- 📊 **Logs**: Check `overtone.log` in the application directory for detailed error information
- ⭐ **Show Support**: Star the repository if you find Overtone useful!
