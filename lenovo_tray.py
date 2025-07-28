#!/usr/bin/env python3
"""
Lenovo Legion Tray Application
A Qt5 system tray application to manage Lenovo laptop settings:
- Conservation Mode (Battery protection)
- FnLock (Function key behavior)
- Keyboard LED brightness
"""

import sys
import os
import subprocess
from enum import Enum
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QAction, 
                            QMessageBox, QWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QBrush, QFont


class SettingStatus(Enum):
    """Enum for different setting statuses"""
    CONSERVATION_DISABLED = 0
    CONSERVATION_ENABLED = 1
    
    FNLOCK_DISABLED = 0
    FNLOCK_ENABLED = 1
    
    KBD_LED_OFF = 0
    KBD_LED_MIN = 1
    KBD_LED_MAX = 2


class LenovoTrayApp(QWidget):
    """Main tray application class"""
    
    def __init__(self):
        super().__init__()
        
        self.base_folder = "/sys/devices/pci0000:00/0000:00:14.3/PNP0C09:00/VPC2004:00/"
        
        # System file paths
        self.conservation_file = os.path.join(self.base_folder, "conservation_mode")
        self.fnlock_file = os.path.join(self.base_folder, "fn_lock")
        self.kbd_led_file = os.path.join(self.base_folder, "leds/platform::kbd_backlight/brightness")
        
        # Current status cache
        self.conservation_status = SettingStatus.CONSERVATION_DISABLED
        self.fnlock_status = SettingStatus.FNLOCK_DISABLED
        self.kbd_led_status = SettingStatus.KBD_LED_OFF
        
        self.init_ui()
        self.read_initial_status()
        
        # Timer to periodically update status
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
    
    def init_ui(self):
        """Initialize the system tray UI"""
        self.setWindowTitle('Lenovo Legion Control')
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple icon (you can replace with a custom icon file)
        icon = self.create_icon()
        self.tray_icon.setIcon(icon)
        
        # Create context menu
        self.create_context_menu()
        
        # Set the context menu
        self.tray_icon.setContextMenu(self.context_menu)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Set tooltip
        self.update_tooltip()
    
    def create_icon(self):
        """Create a Vantage-style icon for the tray"""
        # Try to load SVG icon first
        icon_path = os.path.join(os.path.dirname(__file__), "vantage_icon.svg")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        
        # Fallback: Create programmatic icon
        # Create a 32x32 pixmap for better quality
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Vantage-style colors (red/orange gradient)
        gradient_color1 = Qt.red
        gradient_color2 = Qt.darkRed
        
        # Draw the main circular background
        painter.setBrush(QBrush(gradient_color1))
        painter.setPen(QPen(gradient_color2, 2))
        painter.drawEllipse(2, 2, 28, 28)
        
        # Draw the "V" letter in the center
        painter.setPen(QPen(Qt.white, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        # V shape coordinates
        # Left line of V
        painter.drawLine(10, 8, 16, 22)
        # Right line of V
        painter.drawLine(16, 22, 22, 8)
        
        # Add a small highlight for 3D effect
        painter.setPen(QPen(Qt.lightGray, 1))
        painter.drawArc(4, 4, 24, 24, 45 * 16, 90 * 16)  # Top-left arc highlight
        
        painter.end()
        
        return QIcon(pixmap)
    
    def create_conservation_icon(self, enabled=False):
        """Create an icon for conservation mode"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Battery outline
        painter.setPen(QPen(Qt.darkGray, 1))
        painter.drawRect(2, 4, 10, 8)
        painter.drawRect(12, 6, 2, 4)  # Battery tip
        
        # Fill based on status
        if enabled:
            # Green fill for conservation mode enabled
            painter.setBrush(QBrush(Qt.green))
            painter.setPen(Qt.NoPen)
            painter.drawRect(3, 5, 9, 6)
            # Add "eco" symbol
            painter.setPen(QPen(Qt.darkGreen, 1))
            painter.drawText(4, 10, "E")
        else:
            # Normal battery fill
            painter.setBrush(QBrush(Qt.gray))
            painter.setPen(Qt.NoPen)
            painter.drawRect(3, 5, 9, 6)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_fnlock_icon(self, enabled=False):
        """Create an icon for FnLock"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Key outline
        painter.setPen(QPen(Qt.darkGray, 1))
        painter.setBrush(QBrush(Qt.lightGray if not enabled else Qt.yellow))
        painter.drawRoundedRect(2, 6, 12, 8, 2, 2)
        
        # Fn text
        painter.setPen(QPen(Qt.black, 1))
        painter.setFont(QFont("Arial", 6, QFont.Bold))
        painter.drawText(4, 12, "Fn")
        
        # Lock indicator
        if enabled:
            painter.setPen(QPen(Qt.red, 2))
            painter.drawEllipse(10, 2, 4, 4)
            painter.drawLine(12, 6, 12, 4)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_keyboard_led_icon(self, level=0):
        """Create an icon for keyboard LED status"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Keyboard outline
        painter.setPen(QPen(Qt.darkGray, 1))
        painter.setBrush(QBrush(Qt.lightGray))
        painter.drawRoundedRect(1, 8, 14, 6, 1, 1)
        
        # Keys
        for i in range(3):
            painter.drawRect(2 + i * 4, 9, 3, 2)
            painter.drawRect(2 + i * 4, 11, 3, 2)
        
        # LED indicators based on level
        if level == 0:  # Off
            pass  # No additional drawing
        elif level == 1:  # Min
            painter.setBrush(QBrush(Qt.yellow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(6, 2, 4, 4)
        else:  # Max
            painter.setBrush(QBrush(Qt.yellow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(4, 1, 3, 3)
            painter.drawEllipse(6, 2, 4, 4)
            painter.drawEllipse(9, 1, 3, 3)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_refresh_icon(self):
        """Create a refresh icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Circular arrow
        painter.setPen(QPen(Qt.blue, 2))
        painter.drawArc(2, 2, 12, 12, 30 * 16, 300 * 16)
        
        # Arrow head
        painter.drawLine(12, 3, 14, 2)
        painter.drawLine(12, 3, 13, 5)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_exit_icon(self):
        """Create an exit icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # X mark
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(4, 4, 12, 12)
        painter.drawLine(4, 12, 12, 4)
        
        painter.end()
        return QIcon(pixmap)

    def create_context_menu(self):
        """Create the context menu for the tray icon"""
        self.context_menu = QMenu()
        
        # Conservation Mode action
        self.conservation_action = QAction("Conservation Mode: Loading...", self)
        self.conservation_action.triggered.connect(self.toggle_conservation_mode)
        self.context_menu.addAction(self.conservation_action)
        
        # FnLock action
        self.fnlock_action = QAction("FnLock: Loading...", self)
        self.fnlock_action.triggered.connect(self.toggle_fnlock)
        self.context_menu.addAction(self.fnlock_action)
        
        # Keyboard LED action
        self.kbd_led_action = QAction("Keyboard LEDs: Loading...", self)
        self.kbd_led_action.triggered.connect(self.cycle_kbd_leds)
        self.context_menu.addAction(self.kbd_led_action)
        
        # Separator
        self.context_menu.addSeparator()
        
        # Refresh action
        refresh_action = QAction("Refresh Status", self)
        refresh_action.setIcon(self.create_refresh_icon())
        refresh_action.triggered.connect(self.update_status)
        self.context_menu.addAction(refresh_action)
        
        # Separator
        self.context_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setIcon(self.create_exit_icon())
        exit_action.triggered.connect(self.exit_application)
        self.context_menu.addAction(exit_action)
    
    def read_file_value(self, filepath):
        """Read value from system file"""
        try:
            with open(filepath, 'r') as f:
                return f.read().strip()
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    def write_file_value(self, filepath, value):
        """Write value to system file using pkexec for GUI authentication"""
        try:
            # Use pkexec with tee to write the value
            # This will prompt for authentication via GUI if needed
            cmd = ['pkexec', 'tee', filepath]
            result = subprocess.run(cmd, input=value, text=True, 
                                  capture_output=True, timeout=30)
            
            if result.returncode == 0:
                print(f"Successfully wrote {value} to {filepath}")
                return True
            else:
                print(f"Failed to write to {filepath}: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"Timeout writing to {filepath}")
            return False
        except Exception as e:
            print(f"Exception writing to {filepath}: {e}")
            return False
    
    def read_initial_status(self):
        """Read initial status from all files"""
        # Conservation mode
        conservation_val = self.read_file_value(self.conservation_file)
        if conservation_val is not None:
            self.conservation_status = SettingStatus.CONSERVATION_ENABLED if conservation_val == "1" else SettingStatus.CONSERVATION_DISABLED
        
        # FnLock
        fnlock_val = self.read_file_value(self.fnlock_file)
        if fnlock_val is not None:
            self.fnlock_status = SettingStatus.FNLOCK_ENABLED if fnlock_val == "1" else SettingStatus.FNLOCK_DISABLED
        
        # Keyboard LEDs
        kbd_led_val = self.read_file_value(self.kbd_led_file)
        if kbd_led_val is not None:
            try:
                led_level = int(kbd_led_val)
                if led_level == 0:
                    self.kbd_led_status = SettingStatus.KBD_LED_OFF
                elif led_level == 1:
                    self.kbd_led_status = SettingStatus.KBD_LED_MIN
                else:  # 2 or higher
                    self.kbd_led_status = SettingStatus.KBD_LED_MAX
            except ValueError:
                self.kbd_led_status = SettingStatus.KBD_LED_OFF
        
        self.update_menu_text()
    
    def update_status(self):
        """Update status by reading from files"""
        self.read_initial_status()
        self.update_tooltip()
    
    def update_menu_text(self):
        """Update the menu action text based on current status"""
        # Conservation mode
        conservation_text = "Enabled" if self.conservation_status == SettingStatus.CONSERVATION_ENABLED else "Disabled"
        conservation_enabled = self.conservation_status == SettingStatus.CONSERVATION_ENABLED
        self.conservation_action.setText(f"Conservation Mode: {conservation_text}")
        self.conservation_action.setIcon(self.create_conservation_icon(conservation_enabled))
        
        # FnLock
        fnlock_text = "Enabled" if self.fnlock_status == SettingStatus.FNLOCK_ENABLED else "Disabled"
        fnlock_enabled = self.fnlock_status == SettingStatus.FNLOCK_ENABLED
        self.fnlock_action.setText(f"FnLock: {fnlock_text}")
        self.fnlock_action.setIcon(self.create_fnlock_icon(fnlock_enabled))
        
        # Keyboard LEDs
        if self.kbd_led_status == SettingStatus.KBD_LED_OFF:
            kbd_text = "Off"
            kbd_level = 0
        elif self.kbd_led_status == SettingStatus.KBD_LED_MIN:
            kbd_text = "Min"
            kbd_level = 1
        else:
            kbd_text = "Max"
            kbd_level = 2
        self.kbd_led_action.setText(f"Keyboard LEDs: {kbd_text}")
        self.kbd_led_action.setIcon(self.create_keyboard_led_icon(kbd_level))
    
    def update_tooltip(self):
        """Update the tray icon tooltip"""
        conservation_text = "On" if self.conservation_status == SettingStatus.CONSERVATION_ENABLED else "Off"
        fnlock_text = "On" if self.fnlock_status == SettingStatus.FNLOCK_ENABLED else "Off"
        
        if self.kbd_led_status == SettingStatus.KBD_LED_OFF:
            kbd_text = "Off"
        elif self.kbd_led_status == SettingStatus.KBD_LED_MIN:
            kbd_text = "Min"
        else:
            kbd_text = "Max"
        
        tooltip = f"Lenovo Control\nConservation: {conservation_text}\nFnLock: {fnlock_text}\nKBD LEDs: {kbd_text}"
        self.tray_icon.setToolTip(tooltip)
    
    def toggle_conservation_mode(self):
        """Toggle conservation mode between enabled and disabled"""
        if self.conservation_status == SettingStatus.CONSERVATION_ENABLED:
            new_value = "0"
            self.conservation_status = SettingStatus.CONSERVATION_DISABLED
        else:
            new_value = "1"
            self.conservation_status = SettingStatus.CONSERVATION_ENABLED
        
        if self.write_file_value(self.conservation_file, new_value):
            self.update_menu_text()
            self.update_tooltip()
            self.show_notification("Conservation Mode", 
                                 "Enabled" if new_value == "1" else "Disabled")
        else:
            # Revert status on failure
            self.conservation_status = SettingStatus.CONSERVATION_DISABLED if new_value == "1" else SettingStatus.CONSERVATION_ENABLED
    
    def toggle_fnlock(self):
        """Toggle FnLock between enabled and disabled"""
        if self.fnlock_status == SettingStatus.FNLOCK_ENABLED:
            new_value = "0"
            self.fnlock_status = SettingStatus.FNLOCK_DISABLED
        else:
            new_value = "1"
            self.fnlock_status = SettingStatus.FNLOCK_ENABLED
        
        if self.write_file_value(self.fnlock_file, new_value):
            self.update_menu_text()
            self.update_tooltip()
            self.show_notification("FnLock", 
                                 "Enabled" if new_value == "1" else "Disabled")
        else:
            # Revert status on failure
            self.fnlock_status = SettingStatus.FNLOCK_DISABLED if new_value == "1" else SettingStatus.FNLOCK_ENABLED
    
    def cycle_kbd_leds(self):
        """Cycle keyboard LEDs through Off -> Min -> Max -> Off"""
        if self.kbd_led_status == SettingStatus.KBD_LED_OFF:
            new_value = "1"
            self.kbd_led_status = SettingStatus.KBD_LED_MIN
            status_text = "Min"
        elif self.kbd_led_status == SettingStatus.KBD_LED_MIN:
            new_value = "2"
            self.kbd_led_status = SettingStatus.KBD_LED_MAX
            status_text = "Max"
        else:  # KBD_LED_MAX
            new_value = "0"
            self.kbd_led_status = SettingStatus.KBD_LED_OFF
            status_text = "Off"
        
        if self.write_file_value(self.kbd_led_file, new_value):
            self.update_menu_text()
            self.update_tooltip()
            self.show_notification("Keyboard LEDs", status_text)
        else:
            # Revert status on failure
            if new_value == "1":
                self.kbd_led_status = SettingStatus.KBD_LED_OFF
            elif new_value == "2":
                self.kbd_led_status = SettingStatus.KBD_LED_MIN
            else:
                self.kbd_led_status = SettingStatus.KBD_LED_MAX
    
    def show_notification(self, title, message):
        """Show system tray notification"""
        if self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 2000)
    
    def exit_application(self):
        """Exit the application"""
        # Clean up timers
        self.status_timer.stop()
        self.tray_icon.hide()
        QApplication.quit()
    
    def authenticate_sudo(self):
        """This method is no longer needed with pkexec approach"""
        return True
    
    def refresh_sudo_credentials(self):
        """This method is no longer needed with pkexec approach"""
        pass
    
    def check_sudo_validity(self):
        """This method is no longer needed with pkexec approach"""
        return True


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Check if system tray is available
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "System Tray",
                           "System tray is not available on this system.")
        sys.exit(1)
    
    # Don't quit when the last window is closed
    app.setQuitOnLastWindowClosed(False)
    
    # Create and show the tray application
    tray_app = LenovoTrayApp()
    
    # Start the application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()