"""
Auto-updater module for checking and downloading updates from GitHub
"""
import os
import sys
import tempfile
import zipfile
import shutil
import subprocess
import json
from typing import Optional, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError

from config import AppInfo


class Updater:
    """Handles checking for updates and downloading new versions from GitHub"""
    
    # GitHub API endpoints
    COMMITS_API_URL = "https://api.github.com/repos/Peloro/overtone-volume-overlay/commits/main"
    DOWNLOAD_URL = "https://github.com/Peloro/overtone-volume-overlay/archive/refs/heads/main.zip"
    
    # Key for storing commit hash in profiles.json
    COMMIT_KEY = "current_commit"
    
    def __init__(self):
        self.current_version = AppInfo.VERSION
        self.app_dir = self._get_app_dir()
        self.profiles_path = os.path.join(self.app_dir, "profiles.json")
        self.current_commit = self._load_current_commit()
        self.latest_commit: Optional[str] = None
        self.commit_message: Optional[str] = None
        self.commit_author: Optional[str] = None
        self.commit_date: Optional[str] = None
    
    def _get_app_dir(self) -> str:
        """Get the application directory"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def _load_profiles(self) -> dict:
        """Load the profiles.json file"""
        try:
            if os.path.exists(self.profiles_path):
                with open(self.profiles_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading profiles.json: {e}")
        return {}
    
    def _save_profiles(self, data: dict):
        """Save the profiles.json file"""
        try:
            with open(self.profiles_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving profiles.json: {e}")
    
    def _load_current_commit(self) -> Optional[str]:
        """Load the current commit hash from profiles.json"""
        profiles = self._load_profiles()
        return profiles.get(self.COMMIT_KEY)
    
    def _save_current_commit(self, commit_hash: str):
        """Save the current commit hash to profiles.json"""
        profiles = self._load_profiles()
        profiles[self.COMMIT_KEY] = commit_hash
        self._save_profiles(profiles)
    
    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check GitHub for the latest commit on main branch.
        
        Returns:
            Tuple of (update_available, commit_message, commit_details)
        """
        try:
            request = Request(
                self.COMMITS_API_URL,
                headers={
                    'User-Agent': f'{AppInfo.APP_NAME}/{AppInfo.VERSION}',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            self.latest_commit = data.get('sha', '')[:7]  # Short hash
            full_hash = data.get('sha', '')
            
            commit_data = data.get('commit', {})
            self.commit_message = commit_data.get('message', 'No message')
            
            author_data = commit_data.get('author', {})
            self.commit_author = author_data.get('name', 'Unknown')
            self.commit_date = author_data.get('date', '')[:10]  # Just date part
            
            # Build details string
            details = f"Author: {self.commit_author}\nDate: {self.commit_date}\nCommit: {self.latest_commit}"
            
            # Check if we have a new commit
            if self.current_commit is None:
                # First run - save current commit and don't prompt update
                self._save_current_commit(full_hash)
                return False, None, None
            
            # Compare commits
            update_available = full_hash != self.current_commit and self.current_commit is not None
            
            if update_available:
                return True, self.commit_message, details
            else:
                return False, self.commit_message, details
            
        except URLError as e:
            print(f"Network error checking for updates: {e}")
            return False, None, None
        except json.JSONDecodeError as e:
            print(f"Error parsing update response: {e}")
            return False, None, None
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return False, None, None
    
    def download_and_install(self, progress_callback=None) -> bool:
        """
        Download and install the latest update.
        
        Args:
            progress_callback: Optional callback(downloaded, total) for progress
            
        Returns:
            True if update was downloaded and ready to install
        """
        try:
            # Create temp directory for download
            temp_dir = tempfile.mkdtemp(prefix='overtone_update_')
            zip_path = os.path.join(temp_dir, 'update.zip')
            
            # Download the update
            request = Request(
                self.DOWNLOAD_URL,
                headers={'User-Agent': f'{AppInfo.APP_NAME}/{AppInfo.VERSION}'}
            )
            
            with urlopen(request, timeout=60) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                block_size = 8192
                
                with open(zip_path, 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        f.write(buffer)
                        
                        if progress_callback and total_size:
                            progress_callback(downloaded, total_size)
            
            # Extract update
            extract_dir = os.path.join(temp_dir, 'extracted')
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the actual content directory (GitHub zips have a root folder)
            contents = os.listdir(extract_dir)
            if len(contents) == 1 and os.path.isdir(os.path.join(extract_dir, contents[0])):
                source_dir = os.path.join(extract_dir, contents[0])
            else:
                source_dir = extract_dir
            
            # Create update script that will run after app closes
            self._create_update_script(source_dir, self.app_dir, temp_dir)
            
            return True
            
        except Exception as e:
            print(f"Error downloading update: {e}")
            # Clean up temp directory on failure
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            return False
    
    def _create_update_script(self, source_dir: str, app_dir: str, temp_dir: str):
        """Create a batch script to apply the update after app closes"""
        
        script_path = os.path.join(temp_dir, 'apply_update.bat')
        
        # Batch script content
        script = f'''@echo off
echo Updating Overtone...
timeout /t 2 /nobreak > nul

:: Copy new files
xcopy /s /y /q "{source_dir}\\*" "{app_dir}\\"

:: Restart application
cd /d "{app_dir}"
start "" "python" "main.py"

:: Clean up
rmdir /s /q "{temp_dir}"
'''
        
        with open(script_path, 'w') as f:
            f.write(script)
        
        # Store script path for later execution
        self._update_script_path = script_path
    
    def apply_update_and_restart(self):
        """Launch the update script and exit the application"""
        if hasattr(self, '_update_script_path') and os.path.exists(self._update_script_path):
            # Update the commit hash before restarting
            if self.latest_commit:
                # Get the full hash from API again for accuracy
                try:
                    request = Request(
                        self.COMMITS_API_URL,
                        headers={
                            'User-Agent': f'{AppInfo.APP_NAME}/{AppInfo.VERSION}',
                            'Accept': 'application/vnd.github.v3+json'
                        }
                    )
                    with urlopen(request, timeout=10) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        full_hash = data.get('sha', '')
                        self._save_current_commit(full_hash)
                except:
                    pass
            
            # Start the update script
            subprocess.Popen(
                ['cmd', '/c', self._update_script_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            # Exit the application
            sys.exit(0)
    
    def mark_as_updated(self):
        """Mark the current version as up-to-date (save latest commit hash)"""
        try:
            request = Request(
                self.COMMITS_API_URL,
                headers={
                    'User-Agent': f'{AppInfo.APP_NAME}/{AppInfo.VERSION}',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                full_hash = data.get('sha', '')
                self._save_current_commit(full_hash)
                self.current_commit = full_hash
        except Exception as e:
            print(f"Error marking as updated: {e}")


def check_for_updates_async(callback):
    """
    Check for updates in a background thread.
    
    Args:
        callback: Function to call with (update_available, commit_message, details)
    """
    from PyQt5.QtCore import QThread, pyqtSignal
    
    class UpdateChecker(QThread):
        finished = pyqtSignal(bool, str, str)
        
        def __init__(self):
            super().__init__()
            self.updater = Updater()
        
        def run(self):
            available, message, details = self.updater.check_for_updates()
            self.finished.emit(available, message or '', details or '')
    
    checker = UpdateChecker()
    checker.finished.connect(callback)
    checker.start()
    
    return checker  # Return to keep reference alive
