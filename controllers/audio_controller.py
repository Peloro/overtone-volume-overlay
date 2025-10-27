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

from config.constants import UIConstants


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
        # Check cache first
        cached = self._file_desc_cache.get(exe_path)
        if cached:
            return cached
        try:
            language, codepage = win32api.GetFileVersionInfo(exe_path, '\\VarFileInfo\\Translation')[0]
            string_file_info = f'\\StringFileInfo\\{language:04X}{codepage:04X}\\'
            
            # Try FileDescription first (this is usually the display name)
            description = win32api.GetFileVersionInfo(exe_path, string_file_info + 'FileDescription')
            if description:
                desc = description.strip()
                self._file_desc_cache[exe_path] = desc
                return desc
            
            # Fallback to ProductName
            product_name = win32api.GetFileVersionInfo(exe_path, string_file_info + 'ProductName')
            if product_name:
                name = product_name.strip()
                self._file_desc_cache[exe_path] = name
                return name
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
        # Serve from cache if fresh
        now = time()
        cached = self._display_name_cache.get(pid)
        ts = self._name_timestamps.get(pid, 0)
        if cached and (now - ts) < self._name_ttl_seconds:
            return cached

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
        
        # Cache the computed name
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
            print(f"Error getting audio sessions: {e}")
        
        return sessions
    
    def set_application_volume(self, pids, volume: float) -> bool:
        """Set volume for a specific application by PID(s)
        
        Args:
            pids: Either a single PID (int) or a list of PIDs
            volume: Volume level to set (0.0 to 1.0)
        """
        # Normalize to list
        if isinstance(pids, int):
            pids = [pids]
        
        success = False
        try:
            for pid in pids:
                # Try fast path from cache first
                session = self._pid_to_session.get(pid)
                if session and session.Process:
                    try:
                        session.SimpleAudioVolume.SetMasterVolume(volume, None)
                        success = True
                        continue
                    except Exception:
                        # Process might have ended, remove from cache
                        self._pid_to_session.pop(pid, None)

                # Fallback to enumerating all sessions
                audio_sessions = AudioUtilities.GetAllSessions()
                for session in audio_sessions:
                    if session.Process and session.Process.pid == pid:
                        session.SimpleAudioVolume.SetMasterVolume(volume, None)
                        # update cache
                        self._pid_to_session[pid] = session
                        success = True
                        break
        except Exception as e:
            print(f"Error setting volume: {e}")
        return success
    
    def get_application_mute(self, pids) -> bool:
        """Get mute state for a specific application by PID(s)
        
        Args:
            pids: Either a single PID (int) or a list of PIDs
            
        Returns:
            True if ANY of the sessions are muted
        """
        # Normalize to list
        if isinstance(pids, int):
            pids = [pids]
        
        try:
            for pid in pids:
                # Try fast path from cache first
                session = self._pid_to_session.get(pid)
                if session and session.Process:
                    try:
                        if session.SimpleAudioVolume.GetMute():
                            return True
                        continue
                    except Exception:
                        # Process might have ended, remove from cache
                        self._pid_to_session.pop(pid, None)

                # Fallback to enumerating all sessions
                audio_sessions = AudioUtilities.GetAllSessions()
                for session in audio_sessions:
                    if session.Process and session.Process.pid == pid:
                        mute_state = session.SimpleAudioVolume.GetMute()
                        # update cache
                        self._pid_to_session[pid] = session
                        if mute_state:
                            return True
                        break
        except Exception as e:
            print(f"Error getting mute state: {e}")
        return False
    
    def set_application_mute(self, pids, mute: bool) -> bool:
        """Mute or unmute a specific application by PID(s)
        
        Args:
            pids: Either a single PID (int) or a list of PIDs
            mute: Mute state to set
        """
        # Normalize to list
        if isinstance(pids, int):
            pids = [pids]
        
        success = False
        try:
            for pid in pids:
                # Try fast path from cache first
                session = self._pid_to_session.get(pid)
                if session and session.Process:
                    try:
                        session.SimpleAudioVolume.SetMute(mute, None)
                        success = True
                        continue
                    except Exception:
                        # Process might have ended, remove from cache
                        self._pid_to_session.pop(pid, None)

                audio_sessions = AudioUtilities.GetAllSessions()
                for session in audio_sessions:
                    if session.Process and session.Process.pid == pid:
                        session.SimpleAudioVolume.SetMute(mute, None)
                        # update cache
                        self._pid_to_session[pid] = session
                        success = True
                        break
        except Exception as e:
            print(f"Error setting mute: {e}")
        return success
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self._display_name_cache.clear()
        self._file_desc_cache.clear()
        self._pid_to_session.clear()
        self._name_timestamps.clear()
