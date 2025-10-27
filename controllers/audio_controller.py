"""
Audio Controller using pycaw library.
Handles getting and setting volume for individual applications.
"""
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from typing import List, Optional, Dict, Any
import win32gui
import win32process
import win32api
import os


class AudioController:
    def __init__(self):
        self._get_master_volume_interface()
    
    def _get_master_volume_interface(self):
        """Get the master volume interface"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.master_volume = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            print(f"Error getting master volume interface: {e}")
            self.master_volume = None
    
    def get_master_volume(self) -> float:
        """Get system master volume"""
        try:
            if self.master_volume:
                return self.master_volume.GetMasterVolumeLevelScalar()
        except Exception as e:
            print(f"Error getting master volume: {e}")
        return 0.5
    
    def set_master_volume(self, volume: float) -> bool:
        """Set system master volume"""
        try:
            if self.master_volume:
                self.master_volume.SetMasterVolumeLevelScalar(volume, None)
                return True
        except Exception as e:
            print(f"Error setting master volume: {e}")
        return False
    
    def get_master_mute(self) -> bool:
        """Get system master mute state"""
        try:
            if self.master_volume:
                return self.master_volume.GetMute()
        except Exception as e:
            print(f"Error getting master mute: {e}")
        return False
    
    def set_master_mute(self, mute: bool) -> bool:
        """Set system master mute"""
        try:
            if self.master_volume:
                self.master_volume.SetMute(mute, None)
                return True
        except Exception as e:
            print(f"Error setting master mute: {e}")
        return False
    
    def _get_file_description(self, exe_path: str) -> Optional[str]:
        """Get the file description from executable metadata"""
        try:
            language, codepage = win32api.GetFileVersionInfo(exe_path, '\\VarFileInfo\\Translation')[0]
            string_file_info = f'\\StringFileInfo\\{language:04X}{codepage:04X}\\'
            
            # Try FileDescription first (this is usually the display name)
            description = win32api.GetFileVersionInfo(exe_path, string_file_info + 'FileDescription')
            if description:
                return description.strip()
            
            # Fallback to ProductName
            product_name = win32api.GetFileVersionInfo(exe_path, string_file_info + 'ProductName')
            if product_name:
                return product_name.strip()
        except:
            pass
        
        return None
    
    def _get_window_title_by_pid(self, pid: int) -> Optional[str]:
        """Get the main window title for a given process ID"""
        window_title = None
        
        def callback(hwnd, titles):
            if win32gui.IsWindowVisible(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    title = win32gui.GetWindowText(hwnd)
                    if title:  # Only add non-empty titles
                        titles.append(title)
        
        titles = []
        try:
            win32gui.EnumWindows(callback, titles)
            if titles:
                # Get the first non-empty title (usually the main window)
                window_title = titles[0]
        except Exception as e:
            print(f"Error getting window title for PID {pid}: {e}")
        
        return window_title
    
    def _get_display_name(self, process_name: str, pid: int, process) -> str:
        """Get display name for a process, trying multiple methods"""
        display_name = None
        
        # Method 1: Try to get window title
        window_title = self._get_window_title_by_pid(pid)
        if window_title:
            display_name = window_title
        
        # Method 2: If no window title, try to get file description from executable metadata
        if not display_name:
            try:
                exe_path = process.exe()
                if exe_path and os.path.exists(exe_path):
                    file_desc = self._get_file_description(exe_path)
                    if file_desc:
                        display_name = file_desc
            except:
                pass
        
        # Method 3: Fallback to process name without .exe extension
        if not display_name:
            if process_name.lower().endswith('.exe'):
                display_name = process_name[:-4]
            else:
                display_name = process_name
        
        return display_name
    
    def get_audio_sessions(self) -> List[Dict[str, Any]]:
        """Get all active audio sessions"""
        sessions: List[Dict[str, Any]] = []
        
        try:
            audio_sessions = AudioUtilities.GetAllSessions()
            
            for session in audio_sessions:
                if session.Process:
                    volume = session.SimpleAudioVolume.GetMasterVolume()
                    muted = session.SimpleAudioVolume.GetMute()
                    
                    process_name = session.Process.name()
                    pid = session.Process.pid
                    
                    # Get display name (window title, file description, or process name)
                    display_name = self._get_display_name(process_name, pid, session.Process)
                    
                    sessions.append({
                        'name': display_name,
                        'pid': pid,
                        'volume': volume,
                        'muted': muted,
                        'session': session
                    })
        except Exception as e:
            print(f"Error getting audio sessions: {e}")
        
        return sessions
    
    def set_application_volume(self, pid: int, volume: float) -> bool:
        """Set volume for a specific application by PID"""
        try:
            audio_sessions = AudioUtilities.GetAllSessions()
            for session in audio_sessions:
                if session.Process and session.Process.pid == pid:
                    session.SimpleAudioVolume.SetMasterVolume(volume, None)
                    return True
        except Exception as e:
            print(f"Error setting volume: {e}")
        return False
    
    def set_application_mute(self, pid: int, mute: bool) -> bool:
        """Mute or unmute a specific application by PID"""
        try:
            audio_sessions = AudioUtilities.GetAllSessions()
            for session in audio_sessions:
                if session.Process and session.Process.pid == pid:
                    session.SimpleAudioVolume.SetMute(mute, None)
                    return True
        except Exception as e:
            print(f"Error setting mute: {e}")
        return False
