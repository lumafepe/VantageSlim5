# VantageSlim5

A Qt system tray application for managing Lenovo vantage settings for the Legion Slim5 14APH8.

## Features

- **Conservation Mode**: Toggle battery conservation mode (extends battery life by limiting charge to ~60%)
- **FnLock**: Toggle function key behavior (F1-F12 vs media keys)
- **Keyboard LEDs**: Cycle through keyboard backlight brightness levels (Off → Min → Max → Off)

## Requirements

- Python 3.6+
- PyQt5
- A GUI authentication method:
  - `pkexec` (PolicyKit - recommended, works on most modern Linux distributions)
  - Terminal-based `sudo` as fallback

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make the script executable:
```bash
chmod +x lenovo_tray.py
```

## Usage

Run the application:
```bash
python3 lenovo_tray.py
```

The application will appear as a system tray icon. Right-click the icon to access the menu with the following options:

- **Conservation Mode**: Click to toggle between Enabled/Disabled
- **FnLock**: Click to toggle between Enabled/Disabled  
- **Keyboard LEDs**: Click to cycle through Off/Min/Max brightness
- **Refresh Status**: Manually refresh the current status
- **Exit**: Close the application

## System Files

The application manages the following system files:
- `/sys/devices/pci0000:00/0000:00:14.3/PNP0C09:00/VPC2004:00/conservation_mode`
- `/sys/devices/pci0000:00/0000:00:14.3/PNP0C09:00/VPC2004:00/fn_lock`
- `/sys/devices/pci0000:00/0000:00:14.3/PNP0C09:00/VPC2004:00/leds/platform::kbd_backlight/brightness`

## Authentication

The application uses your system's default authentication GUI to request administrator privileges when writing to system files:

1. **Primary method**: `pkexec` - Uses your desktop environment's native authentication dialog (GNOME, KDE, XFCE, etc.)
2. **Fallback**: Terminal-based `sudo` if `pkexec` is not available

You'll be prompted for your password when making changes. The application automatically detects the best available authentication method for your system and uses your desktop environment's native authentication dialog.

## Troubleshooting

- **System tray not available**: Make sure you're running a desktop environment that supports system tray
- **Permission denied**: 
  - Make sure you're in the sudo group
  - Ensure PolicyKit is installed: `sudo apt install policykit-1`
- **Files not found**: The system file paths are specific to the Lenovo Legion Slim5 14APH8. Check if the files exist on your system
- **Authentication dialog not appearing**: 
  - Make sure your desktop environment's polkit agent is running

## Compatibility

This application is designed for Lenovo Legion Slim5 14APH8 laptops but may work with other Lenovo models that have the same system file paths.
- **Authentication dialog not appearing**: Try installing a different authentication method or check if your polkit agent is running