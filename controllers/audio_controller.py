"""
Audio Controller using pycaw library.
Handles getting and setting volume for individual applications.
Optimizations:
- Cache expensive display-name lookups per PID and exe path
- Maintain a PID->session cache for faster volume/mute updates
"""
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from typing import List, Optional, Dict, Any
from time import time
import win32gui
import win32process
import win32api
import os

from config import UIConstants
from utils.logger import get_logger

logger = get_logger(__name__)


class AudioController:
    def __init__(self) -> None:
        self._get_master_volume_interface()
        # Cache for display names by PID and exe path to avoid repeated expensive calls
        self._display_name_cache: Dict[int, str] = {}
        self._file_desc_cache: Dict[str, str] = {}
        # Cache for quick PID to session mapping; refreshed on each get_audio_sessions call
        self._pid_to_session: Dict[int, Any] = {}
        # Optional TTL in seconds for window-title based names in case titles change
        self._name_timestamps: Dict[int, float] = {}
        self._name_ttl_seconds: float = UIConstants.NAME_CACHE_TTL_SECONDS
    
    def _get_master_volume_interface(self) -> None:
        """Get the master volume interface"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.master_volume = cast(interface, POINTER(IAudioEndpointVolume))
            logger.info("Master volume interface initialized successfully")
        except Exception as e:
            logger.error(f"Error getting master volume interface: {e}", exc_info=True)
            self.master_volume = None
    
    def get_master_volume(self) -> float:
        """Get system master volume"""
        try:
            if self.master_volume:
                return self.master_volume.GetMasterVolumeLevelScalar()
        except Exception as e:
            logger.error(f"Error getting master volume: {e}")
        return 0.5
    
    def set_master_volume(self, volume: float) -> bool:
        """Set system master volume"""
        try:
            if self.master_volume:
                self.master_volume.SetMasterVolumeLevelScalar(volume, None)
                return True
        except Exception as e:
            logger.error(f"Error setting master volume: {e}")
        return False
    
    def get_master_mute(self) -> bool:
        """Get system master mute state"""
        try:
            if self.master_volume:
                return self.master_volume.GetMute()
        except Exception as e:
            logger.error(f"Error getting master mute: {e}")
        return False
    
    def set_master_mute(self, mute: bool) -> bool:
        """Set system master mute"""
        try:
            if self.master_volume:
                self.master_volume.SetMute(mute, None)
                return True
        except Exception as e:
            logger.error(f"Error setting master mute: {e}")
        return False
    
    def _get_file_description(self, exe_path: str) -> Optional[str]:
        """Get the file description from executable metadata"""
        cached = self._file_desc_cache.get(exe_path)
        if cached:
            return cached
        try:
            language, codepage = win32api.GetFileVersionInfo(exe_path, '\\VarFileInfo\\Translation')[0]
            string_file_info = f'\\StringFileInfo\\{language:04X}{codepage:04X}\\'
            
            for key in ('FileDescription', 'ProductName'):
                desc = win32api.GetFileVersionInfo(exe_path, string_file_info + key)
                if desc:
                    self._file_desc_cache[exe_path] = desc.strip()
                    return self._file_desc_cache[exe_path]
        except Exception:
            pass
        return None
    
    def _get_window_title_by_pid(self, pid: int) -> Optional[str]:
        """Get the main window title for a given process ID"""
        titles = []
        
        def enum_window_callback(hwnd, title_list):
            """Callback function for enumerating windows"""
            if win32gui.IsWindowVisible(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == pid:
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        title_list.append(title)
        
        try:
            win32gui.EnumWindows(enum_window_callback, titles)
            return titles[0] if titles else None
        except Exception as e:
            logger.debug(f"Error getting window title for PID {pid}: {e}")
        return None
    
    def _get_display_name(self, process_name: str, pid: int, process) -> str:
        """Get display name for a process, trying multiple methods"""
        now = time()
        cached = self._display_name_cache.get(pid)
        if cached and (now - self._name_timestamps.get(pid, 0)) < self._name_ttl_seconds:
            return cached

        # Try window title first
        display_name = self._get_window_title_by_pid(pid)
        
        # If no window title, try file description
        if not display_name:
            exe_getter = getattr(process, 'exe', lambda: None)
            exe_path = exe_getter()
            if exe_path and os.path.exists(exe_path):
                display_name = self._get_file_description(exe_path)
        
        # Fall back to process name
        if not display_name:
            display_name = process_name[:-4] if process_name.lower().endswith('.exe') else process_name
        
        self._display_name_cache[pid] = display_name
        self._name_timestamps[pid] = now
        return display_name
    
    def get_audio_sessions(self) -> List[Dict[str, Any]]:
        """Get all active audio sessions, grouped by display name"""
        sessions: List[Dict[str, Any]] = []
        # Reset PID map each refresh
        self._pid_to_session.clear()
        
        # Temporary dict to group sessions by name
        grouped_sessions: Dict[str, Dict[str, Any]] = {}
        
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
                    
                    # Update PID map for fast lookups on set operations
                    self._pid_to_session[pid] = session

                    # Group by display name
                    if display_name not in grouped_sessions:
                        # First session with this name
                        grouped_sessions[display_name] = {
                            'name': display_name,
                            'pids': [pid],
                            'sessions': [session],
                            'volume': volume,
                            'muted': muted
                        }
                    else:
                        # Additional session with same name - add to group
                        grouped_sessions[display_name]['pids'].append(pid)
                        grouped_sessions[display_name]['sessions'].append(session)
                        # Use average volume of all sessions
                        existing_vol = grouped_sessions[display_name]['volume']
                        count = len(grouped_sessions[display_name]['pids'])
                        grouped_sessions[display_name]['volume'] = (existing_vol * (count - 1) + volume) / count
                        # Muted if ANY session is muted
                        if muted:
                            grouped_sessions[display_name]['muted'] = True
            
            # Convert grouped sessions to list
            sessions = list(grouped_sessions.values())
            
        except Exception as e:
            logger.error(f"Error getting audio sessions: {e}", exc_info=True)
        
        return sessions
    
    def _get_or_refresh_session(self, pid: int):
        """Get session from cache or refresh from audio sessions"""
        session = self._pid_to_session.get(pid)
        if session:
            try:
                # Test if session is still valid
                session.SimpleAudioVolume.GetMute()
                return session
            except Exception:
                self._pid_to_session.pop(pid, None)
        
        # Refresh from all sessions
        for session in AudioUtilities.GetAllSessions():
            if session.Process and session.Process.pid == pid:
                self._pid_to_session[pid] = session
                return session
        return None
    
    def set_application_volume(self, pids, volume: float) -> bool:
        """Set volume for a specific application by PID(s)"""
        pids = [pids] if isinstance(pids, int) else pids
        try:
            success = False
            for pid in pids:
                if session := self._get_or_refresh_session(pid):
                    session.SimpleAudioVolume.SetMasterVolume(volume, None)
                    success = True
            return success
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False
    
    def get_application_mute(self, pids) -> bool:
        """Get mute state for a specific application by PID(s) - True if ANY are muted"""
        pids = [pids] if isinstance(pids, int) else pids
        try:
            for pid in pids:
                session = self._get_or_refresh_session(pid)
                if session and session.SimpleAudioVolume.GetMute():
                    return True
            return False
        except Exception as e:
            logger.error(f"Error getting mute state: {e}")
            return False
    
    def set_application_mute(self, pids, mute: bool) -> bool:
        """Mute or unmute a specific application by PID(s)"""
        pids = [pids] if isinstance(pids, int) else pids
        try:
            success = False
            for pid in pids:
                if session := self._get_or_refresh_session(pid):
                    session.SimpleAudioVolume.SetMute(mute, None)
                    success = True
            return success
        except Exception as e:
            logger.error(f"Error setting mute: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up resources"""
        # Clear caches
        self._display_name_cache.clear()
        self._file_desc_cache.clear()
        self._pid_to_session.clear()
        self._name_timestamps.clear()
        
        # Just set to None - comtypes will handle cleanup automatically
        self.master_volume = None
