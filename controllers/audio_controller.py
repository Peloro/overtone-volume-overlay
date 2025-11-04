"""
Audio Controller using pycaw library.
Handles getting and setting volume for individual applications.
Optimizations:
- Cache expensive display-name lookups per PID and exe path
- Maintain a PID->session cache for faster volume/mute updates
- Use functools.lru_cache for memoization
"""
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL, COMError
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from typing import List, Optional, Dict, Any, TypeAlias
from functools import lru_cache
from time import time
import atexit
import win32gui
import win32process
import win32api
import os
import sys

from config import UIConstants
from utils.logger import get_logger

logger = get_logger(__name__)

# Type aliases for better readability
SessionDict: TypeAlias = Dict[str, Any]
PIDList: TypeAlias = List[int]
CacheDict: TypeAlias = Dict[int, str]


class AudioController:
    """Audio controller with caching optimizations"""
    # Constants
    _EXE_EXTENSION = '.exe'
    _EXE_EXTENSION_LENGTH = 4  # Length of ".exe"
    
    def __init__(self) -> None:
        # Flag to track if cleanup has been called
        self._cleaned_up = False
        # Flag to track if we're in interpreter shutdown
        self._is_shutting_down = False
        
        self._get_master_volume_interface()
        
        # Cache for display names by PID and exe path to avoid repeated expensive calls
        self._display_name_cache: CacheDict = {}
        # Cache for quick PID to session mapping; refreshed on each get_audio_sessions call
        self._pid_to_session: Dict[int, Any] = {}
        # Optional TTL in seconds for window-title based names in case titles change
        self._name_timestamps: Dict[int, float] = {}
        self._name_ttl_seconds: float = UIConstants.NAME_CACHE_TTL_SECONDS
        # Cache for process exe paths to avoid repeated process.exe() calls
        self._pid_to_exe_cache: Dict[int, Optional[str]] = {}
        # Cache window titles to avoid repeated enumeration
        self._window_title_cache: Dict[int, Optional[str]] = {}
        # Maximum cache sizes to prevent memory bloat
        self._max_cache_size = UIConstants.MAX_CACHE_SIZE
        
        # Register cleanup on exit to ensure proper COM cleanup
        atexit.register(self._safe_cleanup)
    
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
    
    @staticmethod
    @lru_cache(maxsize=128)
    def _get_file_description(exe_path: str) -> Optional[str]:
        """Get the file description from executable metadata (cached with LRU)"""
        try:
            language, codepage = win32api.GetFileVersionInfo(exe_path, '\\VarFileInfo\\Translation')[0]
            string_file_info = f'\\StringFileInfo\\{language:04X}{codepage:04X}\\'
            
            for key in ('FileDescription', 'ProductName'):
                desc = win32api.GetFileVersionInfo(exe_path, string_file_info + key)
                if desc:
                    return desc.strip()
        except Exception:
            pass
        return None
    
    def _get_window_title_by_pid(self, pid: int) -> Optional[str]:
        """Get the main window title for a given process ID"""
        # Check cache first
        now = time()
        if pid in self._window_title_cache:
            cached_time = self._name_timestamps.get(f"win_{pid}", 0)
            if now - cached_time < self._name_ttl_seconds:
                return self._window_title_cache[pid]
        
        try:
            # Try to find window directly by PID instead of enumerating all
            def enum_window_callback(hwnd, result_list):
                """Callback function for enumerating windows"""
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                        if window_pid == pid:
                            title = win32gui.GetWindowText(hwnd)
                            if title:
                                result_list.append(title)
                                return False  # Stop enumeration early
                except Exception:
                    pass
                return True
            
            titles = []
            win32gui.EnumWindows(enum_window_callback, titles)
            result = titles[0] if titles else None
            
            # Cache the result (even if None)
            self._window_title_cache[pid] = result
            self._name_timestamps[f"win_{pid}"] = now
            return result
        except Exception as e:
            logger.debug(f"Error getting window title for PID {pid}: {e}")
        return None
    
    def _get_display_name(self, process_name: str, pid: int, process) -> str:
        """Get display name for a process, trying multiple methods"""
        now = time()
        if (cached := self._display_name_cache.get(pid)) and (now - self._name_timestamps.get(pid, 0)) < self._name_ttl_seconds:
            return cached

        # Try window title, then file description, finally process name
        display_name = self._get_window_title_by_pid(pid)
        
        if not display_name:
            # Use cached exe path or fetch and cache it
            exe_path = self._pid_to_exe_cache.get(pid)
            if exe_path is None:
                try:
                    exe_path = getattr(process, 'exe', lambda: None)()
                    # Limit cache size
                    if len(self._pid_to_exe_cache) >= self._max_cache_size:
                        # Remove oldest entries (simple FIFO)
                        old_pids = list(self._pid_to_exe_cache.keys())[:UIConstants.CACHE_CLEANUP_BATCH_SIZE]
                        for old_pid in old_pids:
                            self._pid_to_exe_cache.pop(old_pid, None)
                    self._pid_to_exe_cache[pid] = exe_path
                except Exception:
                    exe_path = None
                    self._pid_to_exe_cache[pid] = None
            
            if exe_path and os.path.exists(exe_path):
                display_name = self._get_file_description(exe_path)
        
        if not display_name:
            display_name = process_name[:-self._EXE_EXTENSION_LENGTH] if process_name.lower().endswith(self._EXE_EXTENSION) else process_name
        
        # Limit cache size
        if len(self._display_name_cache) >= self._max_cache_size:
            # Remove expired entries first
            expired = [k for k, v in self._name_timestamps.items() if now - v >= self._name_ttl_seconds]
            for k in expired:
                self._display_name_cache.pop(k, None)
                self._name_timestamps.pop(k, None)
            # If still too large, remove oldest entries (simple FIFO)
            if len(self._display_name_cache) >= self._max_cache_size:
                old_pids = list(self._display_name_cache.keys())[:UIConstants.CACHE_CLEANUP_BATCH_SIZE]
                for old_pid in old_pids:
                    self._display_name_cache.pop(old_pid, None)
                    self._name_timestamps.pop(old_pid, None)
        
        self._display_name_cache[pid] = display_name
        self._name_timestamps[pid] = now
        return display_name
    
    def get_audio_sessions(self) -> List[SessionDict]:
        """Get all active audio sessions, grouped by display name"""
        sessions: List[SessionDict] = []
        # Reset PID map each refresh
        self._pid_to_session.clear()
        
        # Temporary dict to group sessions by name
        grouped_sessions: Dict[str, SessionDict] = {}
        
        try:
            audio_sessions = AudioUtilities.GetAllSessions()
            
            for session in audio_sessions:
                if not session.Process:
                    continue
                    
                try:
                    volume = session.SimpleAudioVolume.GetMasterVolume()
                    muted = session.SimpleAudioVolume.GetMute()
                except Exception:
                    continue  # Skip invalid sessions
                
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
                    group = grouped_sessions[display_name]
                    group['pids'].append(pid)
                    group['sessions'].append(session)
                    # Use average volume of all sessions
                    count = len(group['pids'])
                    group['volume'] = (group['volume'] * (count - 1) + volume) / count
                    # Muted if ANY session is muted
                    if muted:
                        group['muted'] = True
            
            # Convert grouped sessions to list (sorted for consistency)
            sessions = sorted(grouped_sessions.values(), key=lambda x: x['name'].lower())
            
        except Exception as e:
            logger.error(f"Error getting audio sessions: {e}", exc_info=True)
        
        return sessions
    
    @staticmethod
    def sessions_have_changed(old_sessions: List[SessionDict], new_sessions: List[SessionDict]) -> bool:
        """
        Check if sessions have meaningfully changed.
        Compares session names and PIDs to detect changes.
        """
        if len(old_sessions) != len(new_sessions):
            return True
        
        # Compare session names and PIDs as a quick check
        old_set = {(s['name'], tuple(s['pids'])) for s in old_sessions}
        new_set = {(s['name'], tuple(s['pids'])) for s in new_sessions}
        
        return old_set != new_set
    
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
    
    def _normalize_pids(self, pids):
        """Convert single PID to list"""
        return pids if isinstance(pids, list) else [pids]
    
    def set_application_volume(self, pids, volume: float) -> bool:
        """Set volume for a specific application by PID(s)"""
        try:
            success = False
            for pid in self._normalize_pids(pids):
                if session := self._get_or_refresh_session(pid):
                    session.SimpleAudioVolume.SetMasterVolume(volume, None)
                    success = True
            return success
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False
    
    def get_application_mute(self, pids) -> bool:
        """Get mute state for a specific application by PID(s) - True if ANY are muted"""
        try:
            return any(session.SimpleAudioVolume.GetMute() 
                      for pid in self._normalize_pids(pids) 
                      if (session := self._get_or_refresh_session(pid)))
        except Exception as e:
            logger.error(f"Error getting mute state: {e}")
            return False
    
    def set_application_mute(self, pids, mute: bool) -> bool:
        """Mute or unmute a specific application by PID(s)"""
        try:
            success = False
            for pid in self._normalize_pids(pids):
                if session := self._get_or_refresh_session(pid):
                    session.SimpleAudioVolume.SetMute(mute, None)
                    success = True
            return success
        except Exception as e:
            logger.error(f"Error setting mute: {e}")
            return False
    
    def _safe_cleanup(self) -> None:
        """Safe cleanup for atexit registration"""
        try:
            if not self._cleaned_up:
                self._is_shutting_down = True
                self.cleanup()
        except Exception:
            pass  # Suppress all errors during atexit cleanup
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if self._cleaned_up:
            return  # Prevent double cleanup
        
        logger.debug("Starting audio controller cleanup")
        
        try:
            # Clear all session references first to break circular references
            if hasattr(self, '_pid_to_session'):
                # Store references temporarily to release them properly
                sessions_to_cleanup = list(self._pid_to_session.values())
                self._pid_to_session.clear()
                
                # Explicitly release each session
                for session in sessions_to_cleanup:
                    try:
                        # Set to None to allow Python to handle cleanup
                        session = None
                    except Exception:
                        pass
                
                # Clear the list
                del sessions_to_cleanup
            
            # Clear caches
            if hasattr(self, '_display_name_cache'):
                self._display_name_cache.clear()
            if hasattr(self, '_name_timestamps'):
                self._name_timestamps.clear()
            if hasattr(self, '_pid_to_exe_cache'):
                self._pid_to_exe_cache.clear()
            if hasattr(self, '_window_title_cache'):
                self._window_title_cache.clear()
            
            # Clear LRU cache
            try:
                if hasattr(self, '_get_file_description'):
                    self._get_file_description.cache_clear()
            except Exception as e:
                logger.debug(f"Error clearing LRU cache: {e}")
            
            # Release master volume interface safely
            if hasattr(self, 'master_volume') and self.master_volume is not None:
                try:
                    # Store reference and set to None immediately to avoid double-release
                    master_vol_ref = self.master_volume
                    self.master_volume = None
                    
                    # Only manually release if not in interpreter shutdown
                    # During shutdown, let Python handle it automatically
                    if not self._is_shutting_down:
                        try:
                            # Manually release the COM reference count
                            # Use comtypes' internal release mechanism
                            del master_vol_ref
                        except Exception:
                            pass
                    else:
                        # During shutdown, just delete the reference
                        del master_vol_ref
                    
                    logger.debug("Master volume interface cleared")
                except (COMError, ValueError) as e:
                    # Catch COM-specific errors silently as they're expected during shutdown
                    logger.debug(f"COM cleanup error (expected during shutdown): {e}")
                except Exception as e:
                    logger.debug(f"Error clearing master volume interface: {e}")
            
            # Force garbage collection to clean up COM references
            # But only if not in interpreter shutdown to avoid issues
            if not self._is_shutting_down:
                try:
                    import gc
                    gc.collect()
                    logger.debug("Forced garbage collection for COM cleanup")
                except Exception as e:
                    logger.debug(f"Error during garbage collection: {e}")
            
            self._cleaned_up = True
            logger.debug("Audio controller cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
            self._cleaned_up = True  # Mark as cleaned up even if error occurred
    
    def __del__(self):
        """Destructor to ensure cleanup is called"""
        try:
            # Check if we're in interpreter shutdown
            if sys is None or not hasattr(sys, 'meta_path'):
                # Interpreter is shutting down, don't do anything
                return
            
            if not getattr(self, '_cleaned_up', False):
                self._is_shutting_down = True
                self._safe_cleanup()
        except Exception:
            pass  # Suppress all errors in destructor
