"""
Hotkey Recorder Widget
Allows users to record hotkey combinations by pressing keys
"""
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent

from config import UIConstants


class HotkeyRecorderButton(QPushButton):
    """
    A button that records hotkey combinations when clicked.
    Click the button to start recording, then press the desired key combination.
    """
    hotkey_changed = pyqtSignal(str)
    
    # Mapping Qt key codes to keyboard library key names
    _KEY_MAP = {
        Qt.Key_Control: 'ctrl',
        Qt.Key_Shift: 'shift',
        Qt.Key_Alt: 'alt',
        Qt.Key_Meta: 'win',
        Qt.Key_F1: 'f1',
        Qt.Key_F2: 'f2',
        Qt.Key_F3: 'f3',
        Qt.Key_F4: 'f4',
        Qt.Key_F5: 'f5',
        Qt.Key_F6: 'f6',
        Qt.Key_F7: 'f7',
        Qt.Key_F8: 'f8',
        Qt.Key_F9: 'f9',
        Qt.Key_F10: 'f10',
        Qt.Key_F11: 'f11',
        Qt.Key_F12: 'f12',
        Qt.Key_Escape: 'esc',
        Qt.Key_Tab: 'tab',
        Qt.Key_Space: 'space',
        Qt.Key_Return: 'enter',
        Qt.Key_Enter: 'enter',
        Qt.Key_Backspace: 'backspace',
        Qt.Key_Delete: 'delete',
        Qt.Key_Insert: 'insert',
        Qt.Key_Home: 'home',
        Qt.Key_End: 'end',
        Qt.Key_PageUp: 'pageup',
        Qt.Key_PageDown: 'pagedown',
        Qt.Key_Up: 'up',
        Qt.Key_Down: 'down',
        Qt.Key_Left: 'left',
        Qt.Key_Right: 'right',
    }
    
    _MODIFIER_KEYS = {Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta}
    
    def __init__(self, initial_hotkey: str = "", parent=None):
        super().__init__(parent)
        self._hotkey = initial_hotkey
        self._recording = False
        self._update_display()
        self.clicked.connect(self._start_recording)
        self.setFocusPolicy(Qt.StrongFocus)
        self._apply_style()
    
    def _apply_style(self):
        """Apply styling to the button"""
        base_style = f"""
            QPushButton {{
                background-color: #424242;
                color: white;
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid #666;
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: {UIConstants.MEDIUM_PADDING}px {UIConstants.MEDIUM_PADDING}px;
                text-align: left;
                min-height: 24px;
            }}
            QPushButton:hover {{
                background-color: #555;
                border-color: #888;
            }}
            QPushButton:focus {{
                border-color: #1e88e5;
            }}
        """
        self.setStyleSheet(base_style)
    
    def _apply_recording_style(self):
        """Apply recording state styling"""
        recording_style = f"""
            QPushButton {{
                background-color: #1e3a5f;
                color: #42a5f5;
                border: {UIConstants.STANDARD_BORDER_WIDTH}px solid #1e88e5;
                border-radius: {UIConstants.SMALL_BUTTON_RADIUS}px;
                padding: {UIConstants.MEDIUM_PADDING}px {UIConstants.MEDIUM_PADDING}px;
                text-align: left;
                min-height: 24px;
            }}
        """
        self.setStyleSheet(recording_style)
    
    def _update_display(self):
        """Update button text based on current state"""
        if self._recording:
            self.setText("Press keys... (Esc to cancel)")
        elif self._hotkey:
            self.setText(self._hotkey)
        else:
            self.setText("Click to record hotkey")
    
    def _start_recording(self):
        """Start recording mode"""
        self._recording = True
        self._apply_recording_style()
        self._update_display()
        self.setFocus()
    
    def _stop_recording(self, save_hotkey: bool = True):
        """Stop recording mode"""
        self._recording = False
        self._apply_style()
        self._update_display()
        self.clearFocus()
    
    def get_hotkey(self) -> str:
        """Get the current hotkey string"""
        return self._hotkey
    
    def set_hotkey(self, hotkey: str):
        """Set the hotkey string"""
        self._hotkey = hotkey
        self._update_display()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events for recording"""
        if not self._recording:
            super().keyPressEvent(event)
            return
        
        key = event.key()
        modifiers = event.modifiers()
        
        # Cancel on Escape (without modifiers)
        if key == Qt.Key_Escape and modifiers == Qt.NoModifier:
            self._stop_recording(save_hotkey=False)
            return
        
        # Ignore standalone modifier key presses - wait for a non-modifier key
        if key in self._MODIFIER_KEYS:
            return
        
        # Build hotkey string
        parts = []
        
        if modifiers & Qt.ControlModifier:
            parts.append('ctrl')
        if modifiers & Qt.ShiftModifier:
            parts.append('shift')
        if modifiers & Qt.AltModifier:
            parts.append('alt')
        if modifiers & Qt.MetaModifier:
            parts.append('win')
        
        # Get the key name
        key_name = self._get_key_name(key, event)
        
        if key_name:
            # Require at least one modifier for a valid hotkey
            if not parts:
                # Flash or show feedback that modifiers are required
                self.setText("Use Ctrl/Shift/Alt + key")
                return
            
            parts.append(key_name)
            new_hotkey = '+'.join(parts)
            
            self._hotkey = new_hotkey
            self._stop_recording()
            self.hotkey_changed.emit(new_hotkey)
    
    def _get_key_name(self, key: int, event: QKeyEvent) -> str:
        """Convert Qt key code to keyboard library key name"""
        # Check special keys first
        if key in self._KEY_MAP:
            return self._KEY_MAP[key]
        
        # For letter keys (A-Z), use the key code directly
        # Qt.Key_A is 0x41 (65), Qt.Key_Z is 0x5a (90)
        if Qt.Key_A <= key <= Qt.Key_Z:
            return chr(key).lower()
        
        # For number keys (0-9)
        # Qt.Key_0 is 0x30 (48), Qt.Key_9 is 0x39 (57)
        if Qt.Key_0 <= key <= Qt.Key_9:
            return chr(key)
        
        # For numpad keys
        if Qt.Key_0 <= key - 0x30 <= 9:  # Numpad keys offset
            return str(key - Qt.Key_0)
        
        # Fallback: try to get key name from text (for other characters)
        # Only use text if it's a printable character (not a control character)
        text = event.text()
        if text and len(text) == 1 and text.isprintable():
            return text.lower()
        
        return None
    
    def focusOutEvent(self, event):
        """Handle focus loss - stop recording"""
        if self._recording:
            self._stop_recording(save_hotkey=False)
        super().focusOutEvent(event)
