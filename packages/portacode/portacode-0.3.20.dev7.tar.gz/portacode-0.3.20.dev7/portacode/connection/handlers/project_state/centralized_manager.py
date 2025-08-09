"""
Centralized project state manager with single source of truth architecture.

This replaces the old ProjectStateManager with a cleaner design:
- Single source of truth for all state
- Clear separation between state updates and client notifications  
- Periodic git monitoring instead of file system watching for git changes
- Atomic state updates to prevent inconsistencies
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Set
from pathlib import Path

from .centralized_state import (
    CentralizedProjectState, StateUpdateManager, StateNotificationManager,
    PeriodicGitMonitor, GitStateSnapshot
)
from .git_manager import GitManager
from .simplified_file_watcher import SimplifiedFileSystemWatcher
from .models import MonitoredFolder, FileItem, TabInfo
from .utils import generate_tab_id

logger = logging.getLogger(__name__)


class CentralizedProjectStateManager:
    """Centralized project state manager with single source of truth."""
    
    def __init__(self, context: Dict, control_channel):
        self.context = context
        self.control_channel = control_channel
        
        # State storage
        self._project_states: Dict[str, CentralizedProjectState] = {}
        self._git_managers: Dict[str, GitManager] = {}
        self._update_managers: Dict[str, StateUpdateManager] = {}
        
        # Managers
        self._notification_manager = StateNotificationManager(control_channel)
        self._git_monitor = PeriodicGitMonitor(self)
        self._file_watcher: Optional[SimplifiedFileSystemWatcher] = None
        
        # File system change tracking
        self._pending_file_changes: Set[str] = set()
        self._debounce_timer: Optional[asyncio.Task] = None
        
        logger.info("Initialized CentralizedProjectStateManager")
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active client session IDs."""
        return list(self._project_states.keys())
    
    async def initialize_project_state(self, client_session_id: str, 
                                     project_folder_path: str) -> CentralizedProjectState:
        """Initialize project state for a client session."""
        logger.info("Initializing centralized project state for session: %s, path: %s", 
                   client_session_id, project_folder_path)
        
        # Create centralized project state
        state = CentralizedProjectState(client_session_id, project_folder_path)
        self._project_states[client_session_id] = state
        
        # Initialize git manager
        git_manager = GitManager(project_folder_path)
        self._git_managers[client_session_id] = git_manager
        
        # Initialize update manager
        update_manager = StateUpdateManager(git_manager)
        self._update_managers[client_session_id] = update_manager
        
        # Initialize file system watcher if not already done
        if self._file_watcher is None:
            self._file_watcher = SimplifiedFileSystemWatcher(self)
        
        # Perform initial state refresh
        await self._refresh_all_state(client_session_id)
        
        # Start monitoring if this is the first project
        if len(self._project_states) == 1:
            self._git_monitor.start_monitoring()
        
        # Start watching the project folder
        self._file_watcher.start_watching(project_folder_path)
        
        logger.info("Successfully initialized project state for session: %s", client_session_id)
        return state
    
    async def cleanup_project_state(self, client_session_id: str):
        """Clean up project state for a client session."""
        logger.info("Cleaning up project state for session: %s", client_session_id)
        
        if client_session_id in self._project_states:
            state = self._project_states[client_session_id]
            
            # Stop watching the project folder
            if self._file_watcher:
                self._file_watcher.stop_watching(state.project_folder_path)
            
            # Clean up state
            del self._project_states[client_session_id]
            del self._git_managers[client_session_id]
            del self._update_managers[client_session_id]
            
            logger.info("Cleaned up project state for session: %s", client_session_id)
        
        # Stop monitoring if no more projects
        if len(self._project_states) == 0:
            self._git_monitor.stop_monitoring()
    
    def get_project_state(self, client_session_id: str) -> Optional[CentralizedProjectState]:
        """Get project state for a client session."""
        return self._project_states.get(client_session_id)
    
    async def refresh_git_state(self, client_session_id: str) -> bool:
        """Refresh git state for a specific project. Returns True if changed."""
        state = self._project_states.get(client_session_id)
        update_manager = self._update_managers.get(client_session_id)
        
        if not state or not update_manager:
            return False
        
        # Update git state atomically
        changed = await update_manager.refresh_git_state(state)
        
        if changed:
            # Notify client of changes
            await self._notification_manager.notify_if_changed(state)
        
        return changed
    
    async def refresh_file_system_state(self, client_session_id: str) -> bool:
        """Refresh file system state for a specific project. Returns True if changed."""
        state = self._project_states.get(client_session_id)
        if not state:
            return False
        
        # For now, use the existing file system scanning logic
        # TODO: Replace with clean implementation in StateUpdateManager
        changed = await self._scan_and_update_file_system(state)
        
        if changed:
            # Notify client of changes  
            await self._notification_manager.notify_if_changed(state)
        
        return changed
    
    async def _refresh_all_state(self, client_session_id: str):
        """Refresh all state for a project (git + file system)."""
        await self.refresh_git_state(client_session_id)
        await self.refresh_file_system_state(client_session_id)
    
    async def _scan_and_update_file_system(self, state: CentralizedProjectState) -> bool:
        """Scan file system and update state. Temporary implementation."""
        try:
            # Create root monitored folder if not exists
            if not state.monitored_folders:
                root_folder = MonitoredFolder(
                    folder_path=state.project_folder_path,
                    is_expanded=True
                )
                monitored_folders = [root_folder]
            else:
                monitored_folders = state.monitored_folders
            
            # Scan files in monitored folders
            items = []
            for folder in monitored_folders:
                if folder.is_expanded and os.path.exists(folder.folder_path):
                    folder_items = self._scan_folder_items(folder.folder_path)
                    items.extend(folder_items)
            
            # Update state atomically
            return state.update_file_system_state(monitored_folders, items)
            
        except Exception as e:
            logger.error("Error scanning file system for %s: %s", 
                        state.client_session_id, e)
            return False
    
    def _scan_folder_items(self, folder_path: str) -> List[FileItem]:
        """Scan items in a folder. Temporary implementation."""
        items = []
        try:
            with os.scandir(folder_path) as entries:
                for entry in entries:
                    # Skip all hidden files including .git - git monitoring is handled separately
                    if entry.name.startswith('.'):
                        continue
                    
                    stat_info = entry.stat()
                    item = FileItem(
                        name=entry.name,
                        path=entry.path,
                        is_directory=entry.is_dir(),
                        parent_path=folder_path,
                        size=stat_info.st_size if not entry.is_dir() else 0,
                        modified_time=stat_info.st_mtime,
                        is_git_tracked=False,  # Will be updated by git state sync
                        git_status=None,
                        is_staged=False,
                        is_hidden=entry.name.startswith('.'),
                        is_ignored=False,
                        children=None,
                        is_loaded=True
                    )
                    items.append(item)
        except Exception as e:
            logger.error("Error scanning folder %s: %s", folder_path, e)
        
        return items
    
    # File system event handling
    async def handle_file_change(self, file_path: str):
        """Handle file system change event."""
        logger.debug("File change detected: %s", file_path)
        
        # Find affected projects
        affected_sessions = []
        for session_id, state in self._project_states.items():
            if file_path.startswith(state.project_folder_path):
                affected_sessions.append(session_id)
        
        if affected_sessions:
            self._pending_file_changes.add(file_path)
            await self._debounce_file_changes(affected_sessions)
    
    async def _debounce_file_changes(self, affected_sessions: List[str]):
        """Debounce file changes to avoid excessive updates."""
        # Cancel existing timer
        if self._debounce_timer and not self._debounce_timer.done():
            self._debounce_timer.cancel()
        
        # Set new timer
        self._debounce_timer = asyncio.create_task(
            self._process_file_changes_after_delay(affected_sessions)
        )
    
    async def _process_file_changes_after_delay(self, affected_sessions: List[str]):
        """Process file changes after debounce delay."""
        try:
            await asyncio.sleep(0.5)  # Debounce delay
            
            # Process changes for affected sessions
            for session_id in affected_sessions:
                await self.refresh_file_system_state(session_id)
            
            self._pending_file_changes.clear()
            
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Error processing file changes: %s", e)
    
    # Tab management methods
    async def open_file_tab(self, client_session_id: str, file_path: str, 
                           set_active: bool = True) -> bool:
        """Open a file tab."""
        state = self._project_states.get(client_session_id)
        if not state:
            return False
        
        tab_id = generate_tab_id(file_path, "file")
        tab = TabInfo(
            tab_id=tab_id,
            tab_type="file",
            title=os.path.basename(file_path),
            file_path=file_path
        )
        
        open_tabs = state.open_tabs.copy()
        open_tabs[tab_id] = tab
        
        changed = state.update_tabs_state(open_tabs)
        if changed:
            await self._notification_manager.notify_if_changed(state)
        
        return True
    
    async def close_tab(self, client_session_id: str, tab_id: str) -> bool:
        """Close a tab."""
        state = self._project_states.get(client_session_id)
        if not state:
            return False
        
        open_tabs = state.open_tabs.copy()
        if tab_id in open_tabs:
            del open_tabs[tab_id]
            changed = state.update_tabs_state(open_tabs)
            if changed:
                await self._notification_manager.notify_if_changed(state)
            return True
        
        return False
    
    # Folder management methods
    async def expand_folder(self, client_session_id: str, folder_path: str) -> bool:
        """Expand a folder."""
        state = self._project_states.get(client_session_id)
        if not state:
            return False
        
        # Skip .git directories entirely
        if '.git' in Path(folder_path).parts or folder_path.endswith('.git'):
            logger.debug("Skipping expansion of .git directory: %s", folder_path)
            return False
        
        monitored_folders = state.monitored_folders.copy()
        
        # Find and expand the folder
        found = False
        for folder in monitored_folders:
            if folder.folder_path == folder_path:
                folder.is_expanded = True
                found = True
                break
        
        # Add folder if not in monitored list
        if not found:
            new_folder = MonitoredFolder(folder_path=folder_path, is_expanded=True)
            monitored_folders.append(new_folder)
        
        # Update state and refresh file system
        items = state.items.copy()
        if state.update_file_system_state(monitored_folders, items):
            await self.refresh_file_system_state(client_session_id)
            return True
        
        return False
    
    async def collapse_folder(self, client_session_id: str, folder_path: str) -> bool:
        """Collapse a folder."""
        state = self._project_states.get(client_session_id)
        if not state:
            return False
        
        monitored_folders = state.monitored_folders.copy()
        
        # Find and collapse the folder
        for folder in monitored_folders:
            if folder.folder_path == folder_path:
                folder.is_expanded = False
                break
        
        # Update state and refresh file system
        items = state.items.copy()
        if state.update_file_system_state(monitored_folders, items):
            await self.refresh_file_system_state(client_session_id)
            return True
        
        return False
    
    # Git operation methods
    async def stage_file(self, client_session_id: str, file_path: str) -> bool:
        """Stage a file."""
        git_manager = self._git_managers.get(client_session_id)
        if not git_manager:
            return False
        
        success = git_manager.stage_file(file_path)
        if success:
            # Force refresh git state
            await self.refresh_git_state(client_session_id)
        
        return success
    
    async def unstage_file(self, client_session_id: str, file_path: str) -> bool:
        """Unstage a file."""
        git_manager = self._git_managers.get(client_session_id)
        if not git_manager:
            return False
        
        success = git_manager.unstage_file(file_path)
        if success:
            # Force refresh git state
            await self.refresh_git_state(client_session_id)
        
        return success
    
    async def revert_file(self, client_session_id: str, file_path: str) -> bool:
        """Revert a file."""
        git_manager = self._git_managers.get(client_session_id)
        if not git_manager:
            return False
        
        success = git_manager.revert_file(file_path)
        if success:
            # Force refresh git state
            await self.refresh_git_state(client_session_id)
        
        return success
    
    # Client notification methods
    async def send_update_to_client(self, client_session_id: str, 
                                   server_project_id: Optional[str] = None):
        """Send update to client (force notification)."""
        state = self._project_states.get(client_session_id)
        if state:
            await self._notification_manager.force_notification(state, server_project_id)


# Global instance management
_global_manager: Optional[CentralizedProjectStateManager] = None

def get_or_create_centralized_manager(context: Dict, 
                                     control_channel) -> CentralizedProjectStateManager:
    """Get or create the global centralized project state manager."""
    global _global_manager
    
    if _global_manager is None:
        _global_manager = CentralizedProjectStateManager(context, control_channel)
        logger.info("Created new centralized project state manager")
    
    return _global_manager