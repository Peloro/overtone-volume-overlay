<div align="center">

<img src="assets/icon2.png" alt="Overtone Logo" width="150"/>

# Overtone

**A modern, lightweight volume mixer overlay for Windows**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-41CD52?style=flat&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=flat&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#features) •
[Installation](#installation) •
[Usage](#usage) •
[Configuration](#configuration) •
[Contributing](#contributing)

---

</div>

## About

Overtone is a sleek, always-on-top volume mixer overlay that provides quick access to per-application audio control on Windows. Built with Python and PyQt5, it offers a modern alternative to the native Windows volume mixer with enhanced customization options and keyboard shortcuts.

## Features

<table>
<tr>
<td width="50%">

### Audio Control
- **Per-Application Volume** — Individual sliders for each running application
- **Master Volume Control** — Quick system-wide volume adjustment
- **One-Click Mute** — Instantly mute/unmute any application
- **Precise Input** — Click percentages to type exact values

<br>

</td>
<td width="50%">

### Productivity
- **Global Hotkeys** — Customizable keyboard shortcuts
- **Always-on-Top** — Draggable overlay that stays visible
- **System Tray** — Runs quietly in the background
- **Quick Filter** — Search applications by name

<br>

</td>
</tr>
<tr>
<td width="50%">

### Customization
- **Theme Editor** — Customize all colors and appearance
- **Profile System** — Multiple configurations for different use cases
- **Persistent Settings** — All preferences saved automatically

<br>

</td>
<td width="50%">

### User Experience
- **Lightweight** — Minimal resource footprint
- **Native Look** — Clean, modern Windows aesthetic
- **Paginated View** — Navigate through many applications easily

<br>

</td>
</tr>
</table>

## Installation

### Prerequisites

- **Windows 10/11**
- **Python 3.8** or higher

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Peloro/overtone-volume-overlay.git

# Navigate to the project directory
cd overtone-volume-overlay

# Install dependencies
pip install -r requirements.txt

# Launch Overtone
python main.py
```

### Dependencies

| Package | Version | Description |
|---------|---------|-------------|
| PyQt5 | 5.15.10 | GUI framework |
| pycaw | 20230407 | Windows audio control |
| comtypes | 1.2.0 | COM interface support |
| keyboard | 0.13.5 | Global hotkey handling |
| pywin32 | 306 | Windows API bindings |

## Usage

### Default Hotkeys

| Shortcut | Action |
|----------|--------|
| `Ctrl + /` | Toggle overlay visibility |
| `Ctrl + Shift + S` | Open settings |
| `Ctrl + Q` | Quit application |

### Controls

| Action | Description |
|--------|-------------|
| **Drag title bar** | Move the overlay window |
| **Click percentage** | Type a precise volume value |
| **Filter button** | Search applications by name |
| **Arrow buttons** | Navigate between pages |
| **Settings** | Access customization options |

## Configuration

All settings are automatically persisted in `profiles.json` located in the application directory.

### Profiles

Create multiple configuration profiles for different scenarios:

- **Gaming** — Boost game audio, reduce chat volume
- **Work** — Focus on communication apps
- **Music** — Prioritize media players
- **Movies** — Optimize for media consumption

Settings include window position, theme colors, hotkey bindings, and application-specific preferences.

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Contribution Areas

- Bug fixes and issue resolution
- New features and enhancements
- Documentation improvements
- UI/UX refinements
- Performance optimizations

Please follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines for Python code.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Author

<a href="https://github.com/Peloro">
  <img src="https://img.shields.io/badge/Peloro-181717?style=flat&logo=github&logoColor=white" alt="GitHub"/>
</a>

---

<div align="center">

**Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) and [pycaw](https://github.com/AndreMiras/pycaw)**

If you find this project useful, consider giving it a star!

</div>
