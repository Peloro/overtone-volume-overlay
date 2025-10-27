"""
Audio Controller using pycaw library.
Handles getting and setting volume for individual applications.
"""
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from typing import List, Optional, Dict, Any


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
                    if process_name.lower().endswith('.exe'):
                        process_name = process_name[:-4]
                    
                    sessions.append({
                        'name': process_name,
                        'pid': session.Process.pid,
                        'volume': volume,
                        'muted': muted,
                        'session': session
                    })
        except Exception as e:
            print(f"Error getting audio sessions: {e}")
        
        return sessions
    
    def _find_session_by_pid(self, pid: int):
        """
        Find audio session by PID (helper method to avoid duplicate code)
        Uses get_audio_sessions to avoid duplicating iteration logic
        """
        sessions = self.get_audio_sessions()
        for session_info in sessions:
            if session_info['pid'] == pid:
                return session_info['session'].SimpleAudioVolume
        return None
    
    def set_application_volume(self, pid: int, volume: float) -> bool:
        """Set volume for a specific application by PID"""
        try:
            volume_interface = self._find_session_by_pid(pid)
            if volume_interface:
                volume_interface.SetMasterVolume(volume, None)
                return True
        except Exception as e:
            print(f"Error setting volume: {e}")
        return False
    
    def set_application_mute(self, pid: int, mute: bool) -> bool:
        """Mute or unmute a specific application by PID"""
        try:
            volume_interface = self._find_session_by_pid(pid)
            if volume_interface:
                volume_interface.SetMute(mute, None)
                return True
        except Exception as e:
            print(f"Error setting mute: {e}")
        return False
