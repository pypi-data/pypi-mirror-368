"""
Centralized project state management with single source of truth.

This module implements a clean architecture with clear separation of concerns:
- CentralizedProjectState: Single source of truth for all project state
- StateUpdateManager: Handles atomic state updates
- StateNotificationManager: Handles client notifications when state changes
- PeriodicGitMonitor: Monitors git changes via polling instead of file watching
"""

import asyncio
import logging
import os
import time
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from pathlib import Path

from .models import (
    ProjectState, FileItem, MonitoredFolder, GitFileChange, 
    GitDetailedStatus, TabInfo
)
from .git_manager import GitManager

logger = logging.getLogger(__name__)


@dataclass
class GitStateSnapshot:
    """Complete snapshot of git state at a point in time."""
    is_git_repo: bool
    branch_name: Optional[str]
    head_commit_hash: Optional[str]
    staged_changes: List[GitFileChange]
    unstaged_changes: List[GitFileChange]
    untracked_files: List[GitFileChange]
    
    @property
    def status_summary(self) -> Dict[str, int]:
        """Compute summary from detailed changes."""
        return {
            "modified": len([f for f in self.unstaged_changes if f.change_type in ['M', 'T']]),
            "added": len([f for f in self.staged_changes if f.change_type in ['A', 'M', 'T']]),
            "deleted": len([f for f in self.staged_changes if f.change_type == 'D']),
            "untracked": len(self.untracked_files)
        }
    
    @property
    def detailed_status(self) -> GitDetailedStatus:
        """Convert to GitDetailedStatus model."""
        return GitDetailedStatus(
            head_commit_hash=self.head_commit_hash,
            staged_changes=self.staged_changes,
            unstaged_changes=self.unstaged_changes,
            untracked_files=self.untracked_files
        )
    
    def __eq__(self, other) -> bool:
        """Compare two snapshots for equality."""
        if not isinstance(other, GitStateSnapshot):
            return False
        return (
            self.is_git_repo == other.is_git_repo and
            self.branch_name == other.branch_name and
            self.head_commit_hash == other.head_commit_hash and
            self.staged_changes == other.staged_changes and
            self.unstaged_changes == other.unstaged_changes and
            self.untracked_files == other.untracked_files
        )


class CentralizedProjectState:
    """Single source of truth for all project state."""
    
    def __init__(self, client_session_id: str, project_folder_path: str):
        self.client_session_id = client_session_id
        self.project_folder_path = project_folder_path
        
        # Single source of truth for git state
        self._git_snapshot: Optional[GitStateSnapshot] = None
        self._last_git_status_hash: Optional[str] = None
        
        # File system state
        self._monitored_folders: List[MonitoredFolder] = []
        self._items: List[FileItem] = []
        
        # Open tabs state
        self._open_tabs: Dict[str, TabInfo] = {}
        
        # State version for change detection
        self._state_version = 0
        
    # Git state properties (single source of truth)
    @property
    def is_git_repo(self) -> bool:
        return self._git_snapshot.is_git_repo if self._git_snapshot else False
        
    @property
    def git_branch(self) -> Optional[str]:
        return self._git_snapshot.branch_name if self._git_snapshot else None
        
    @property
    def git_status_summary(self) -> Dict[str, int]:
        return self._git_snapshot.status_summary if self._git_snapshot else {
            "modified": 0, "added": 0, "deleted": 0, "untracked": 0
        }
        
    @property
    def git_detailed_status(self) -> GitDetailedStatus:
        return self._git_snapshot.detailed_status if self._git_snapshot else GitDetailedStatus(
            head_commit_hash=None, staged_changes=[], unstaged_changes=[], untracked_files=[]
        )
    
    # File system state properties
    @property
    def monitored_folders(self) -> List[MonitoredFolder]:
        return self._monitored_folders.copy()
        
    @property
    def items(self) -> List[FileItem]:
        return self._items.copy()
        
    # Open tabs properties
    @property
    def open_tabs(self) -> List[TabInfo]:
        """Return open tabs as a list for backward compatibility."""
        return list(self._open_tabs.values())
        
    @property
    def open_tabs_dict(self) -> Dict[str, TabInfo]:
        """Return open tabs as a dict (internal use)."""
        return self._open_tabs.copy()
        
    @property  
    def active_tab(self) -> Optional[TabInfo]:
        """Backward compatibility: active_tab is deprecated in centralized system."""
        return None
    
    @property
    def state_version(self) -> int:
        """Version number that increments when state changes."""
        return self._state_version
    
    def update_git_state(self, new_snapshot: GitStateSnapshot) -> bool:
        """Update git state atomically. Returns True if state changed."""
        if self._git_snapshot != new_snapshot:
            logger.info("Git state changed for session %s", self.client_session_id)
            old_snapshot = self._git_snapshot
            self._git_snapshot = new_snapshot
            self._state_version += 1
            
            # Update file tree git status to match new git state
            self._sync_file_tree_git_status(old_snapshot, new_snapshot)
            return True
        else:
            # Force sync even if git state hasn't changed, in case items have changed
            if self._items and self._git_snapshot:
                self._sync_file_tree_git_status(None, self._git_snapshot)
        return False
    
    def _sync_file_tree_git_status(self, old_snapshot: Optional[GitStateSnapshot], 
                                  new_snapshot: GitStateSnapshot):
        """Sync git status information from git state to file tree items."""
        print(f"🔍 SYNC: _sync_file_tree_git_status called with {len(self._items)} items")
        
        # Build a map of file paths to their git status information
        file_git_status = {}
        
        # Process staged changes
        for change in new_snapshot.staged_changes:
            file_path = change.file_abs_path
            file_git_status[file_path] = {
                "is_tracked": True,
                "status": change.change_type,
                "is_staged": True,
                "is_ignored": False
            }
        
        # Process unstaged changes (may override staged status for mixed files)
        for change in new_snapshot.unstaged_changes:
            file_path = change.file_abs_path
            if file_path in file_git_status:
                # Mixed staging: both staged and unstaged changes
                file_git_status[file_path]["is_staged"] = "mixed"
                # Keep the unstaged change type as the primary status
                file_git_status[file_path]["status"] = change.change_type
            else:
                file_git_status[file_path] = {
                    "is_tracked": True,
                    "status": change.change_type,
                    "is_staged": False,
                    "is_ignored": False
                }
        
        # Process untracked files
        for change in new_snapshot.untracked_files:
            file_path = change.file_abs_path
            file_git_status[file_path] = {
                "is_tracked": False,
                "status": "untracked",
                "is_staged": False,
                "is_ignored": False
            }
        
        # Update file tree items with git status
        for item in self._items:
            item_path = item.path
            
            if item_path in file_git_status:
                # Direct file match
                git_info = file_git_status[item_path]
                item.is_git_tracked = git_info["is_tracked"]
                item.git_status = git_info["status"]
                item.is_staged = git_info["is_staged"]
                item.is_ignored = git_info["is_ignored"]
            elif item.is_directory:
                # For directories, check if they contain any git changes
                dir_has_changes = False
                dir_status = None
                dir_is_staged = False
                
                for file_path, git_info in file_git_status.items():
                    # Check if this file is inside the directory
                    expected_prefix = item_path + os.sep
                    if file_path.startswith(expected_prefix):
                        dir_has_changes = True
                        # Use the first status we find for the directory
                        if dir_status is None:
                            dir_status = git_info["status"] 
                            dir_is_staged = git_info["is_staged"]
                        break
                
                if dir_has_changes:
                    # Set git tracked status based on the type of change
                    item.is_git_tracked = dir_status != "untracked"
                    item.git_status = dir_status
                    item.is_staged = dir_is_staged
                    item.is_ignored = False
                else:
                    # Directory has no git changes, check if it's tracked at all
                    # For now, assume directories without changes are clean/tracked if in a repo
                    if new_snapshot.is_git_repo:
                        item.is_git_tracked = True
                        item.git_status = None  # Clean/unchanged
                        item.is_staged = False
                        item.is_ignored = False
                    else:
                        item.is_git_tracked = False
                        item.git_status = None
                        item.is_staged = False
                        item.is_ignored = False
            else:
                # File not in git status map - either clean tracked file or ignored
                if new_snapshot.is_git_repo:
                    item.is_git_tracked = True
                    item.git_status = None  # Clean/unchanged
                    item.is_staged = False
                    item.is_ignored = False
                else:
                    item.is_git_tracked = False
                    item.git_status = None
                    item.is_staged = False
                    item.is_ignored = False
    
    def update_file_system_state(self, monitored_folders: List[MonitoredFolder], 
                                items: List[FileItem]) -> bool:
        """Update file system state atomically. Returns True if state changed."""
        if (self._monitored_folders != monitored_folders or 
            self._items != items):
            logger.info("File system state changed for session %s", self.client_session_id)
            self._monitored_folders = monitored_folders
            self._items = items
            self._state_version += 1
            
            # Apply current git state to new items
            if self._git_snapshot:
                self._sync_file_tree_git_status(None, self._git_snapshot)
            
            return True
        return False
    
    def update_tabs_state(self, open_tabs: Dict[str, TabInfo]) -> bool:
        """Update tabs state atomically. Returns True if state changed."""
        if self._open_tabs != open_tabs:
            logger.info("Tabs state changed for session %s", self.client_session_id)
            self._open_tabs = open_tabs
            self._state_version += 1
            return True
        return False
    
    def _sync_file_tree_git_status(self, old_snapshot: Optional[GitStateSnapshot], 
                                  new_snapshot: GitStateSnapshot):
        """Sync file tree git status with new git snapshot."""
        if not new_snapshot.is_git_repo:
            # Clear all git status from files
            for item in self._items:
                if not item.is_directory:
                    item.is_git_tracked = False
                    item.git_status = None
                    item.is_staged = False
            return
        
        # Create lookup maps for efficient updates
        staged_files = {f.file_abs_path: f for f in new_snapshot.staged_changes}
        unstaged_files = {f.file_abs_path: f for f in new_snapshot.unstaged_changes}
        untracked_files = {f.file_abs_path for f in new_snapshot.untracked_files}
        
        # Update git status for all files
        for item in self._items:
            if item.is_directory:
                continue
                
            file_path = item.path
            
            if file_path in staged_files:
                item.is_git_tracked = True
                item.git_status = staged_files[file_path].change_type.lower()
                item.is_staged = True
            elif file_path in unstaged_files:
                item.is_git_tracked = True
                item.git_status = unstaged_files[file_path].change_type.lower()
                item.is_staged = False
            elif file_path in untracked_files:
                item.is_git_tracked = False
                item.git_status = "untracked"
                item.is_staged = False
            else:
                # File is tracked but has no changes
                item.is_git_tracked = True
                item.git_status = None
                item.is_staged = False
    
    def to_legacy_project_state(self) -> ProjectState:
        """Convert to legacy ProjectState model for compatibility."""
        return ProjectState(
            client_session_id=self.client_session_id,
            project_folder_path=self.project_folder_path,
            is_git_repo=self.is_git_repo,
            git_branch=self.git_branch,
            git_status_summary=self.git_status_summary,
            git_detailed_status=self.git_detailed_status,
            monitored_folders=self._monitored_folders,
            items=self._items,
            open_tabs=self._open_tabs,
            active_tab=None  # Deprecated field
        )


class StateUpdateManager:
    """Manages atomic updates to project state."""
    
    def __init__(self, git_manager: GitManager):
        self.git_manager = git_manager
        
    async def refresh_git_state(self, state: CentralizedProjectState) -> bool:
        """Refresh git state from repository using hash-based change detection. Returns True if state changed."""
        try:
            # Check if .git directory exists
            git_dir = os.path.join(state.project_folder_path, '.git')
            is_git_repo = os.path.exists(git_dir)
            
            if not is_git_repo:
                # No git repository - reset hash and set empty state
                state._last_git_status_hash = None
                empty_snapshot = GitStateSnapshot(
                    is_git_repo=False,
                    branch_name=None,
                    head_commit_hash=None,
                    staged_changes=[],
                    unstaged_changes=[],
                    untracked_files=[]
                )
                return state.update_git_state(empty_snapshot)
            
            # Reinitialize git manager if needed
            if not self.git_manager.is_git_repo:
                self.git_manager.reinitialize()
            
            # Use hash-based change detection for performance
            current_git_hash = self.git_manager.compute_git_status_hash()
            
            # Only compute detailed status if hash changed
            if current_git_hash == state._last_git_status_hash:
                logger.debug("Git status hash unchanged for %s, skipping detailed computation", 
                           state.client_session_id)
                return False
            
            logger.debug("Git status hash changed for %s: %s -> %s", 
                        state.client_session_id, state._last_git_status_hash, current_git_hash)
            
            # Hash changed, compute detailed status
            branch_name = self.git_manager.get_branch_name()
            detailed_status = self.git_manager.get_detailed_status()
            
            new_snapshot = GitStateSnapshot(
                is_git_repo=True,
                branch_name=branch_name,
                head_commit_hash=detailed_status.head_commit_hash,
                staged_changes=detailed_status.staged_changes,
                unstaged_changes=detailed_status.unstaged_changes,
                untracked_files=detailed_status.untracked_files
            )
            
            # Update hash and state
            state._last_git_status_hash = current_git_hash
            changed = state.update_git_state(new_snapshot)
            
            return changed
            
        except Exception as e:
            logger.error("Error refreshing git state for %s: %s", 
                        state.client_session_id, e)
            return False
    
    async def refresh_file_system_state(self, state: CentralizedProjectState) -> bool:
        """Refresh file system state. Returns True if state changed."""
        try:
            # This would rebuild monitored folders and items
            # For now, we'll keep the existing logic but make it atomic
            # TODO: Implement clean file system scanning here
            return False  # Placeholder
            
        except Exception as e:
            logger.error("Error refreshing file system state for %s: %s", 
                        state.client_session_id, e)
            return False


class StateNotificationManager:
    """Manages client notifications when state changes."""
    
    def __init__(self, control_channel):
        self.control_channel = control_channel
        self._last_sent_versions: Dict[str, int] = {}
    
    async def notify_if_changed(self, state: CentralizedProjectState, 
                               server_project_id: Optional[str] = None) -> bool:
        """Send notification to client if state has changed. Returns True if sent."""
        client_session_id = state.client_session_id
        current_version = state.state_version
        last_sent_version = self._last_sent_versions.get(client_session_id, -1)
        
        if current_version > last_sent_version:
            await self._send_state_update(state, server_project_id)
            self._last_sent_versions[client_session_id] = current_version
            return True
        return False
    
    async def force_notification(self, state: CentralizedProjectState,
                                server_project_id: Optional[str] = None):
        """Force send notification regardless of version."""
        await self._send_state_update(state, server_project_id)
        self._last_sent_versions[state.client_session_id] = state.state_version
    
    async def _send_state_update(self, state: CentralizedProjectState,
                                server_project_id: Optional[str] = None):
        """Send project state update to client."""
        logger.info("Sending project state update for session: %s", 
                   state.client_session_id)
        
        payload = {
            "event": "project_state_update",
            "project_id": server_project_id or state.client_session_id,
            "project_folder_path": state.project_folder_path,
            "is_git_repo": state.is_git_repo,
            "git_branch": state.git_branch,
            "git_status_summary": state.git_status_summary,
            "git_detailed_status": {
                "head_commit_hash": state.git_detailed_status.head_commit_hash,
                "staged_changes": [
                    {
                        "file_abs_path": f.file_abs_path,
                        "file_rel_path": f.file_repo_path,
                        "change_type": f.change_type
                    } for f in state.git_detailed_status.staged_changes
                ],
                "unstaged_changes": [
                    {
                        "file_abs_path": f.file_abs_path,
                        "file_rel_path": f.file_repo_path,
                        "change_type": f.change_type
                    } for f in state.git_detailed_status.unstaged_changes
                ],
                "untracked_files": [
                    {
                        "file_abs_path": f.file_abs_path,
                        "file_rel_path": f.file_repo_path,
                        "change_type": f.change_type
                    } for f in state.git_detailed_status.untracked_files
                ]
            },
            "monitored_folders": [
                {
                    "folder_path": mf.folder_path,
                    "is_expanded": mf.is_expanded
                } for mf in state.monitored_folders
            ],
            "open_tabs": [
                {
                    "tab_id": tab.tab_id,
                    "tab_type": tab.tab_type,
                    "title": tab.title,
                    "file_path": tab.file_path,
                    "from_ref": tab.from_ref,
                    "to_ref": tab.to_ref,
                    "from_hash": tab.from_hash,
                    "to_hash": tab.to_hash
                } for tab in state.open_tabs_dict.values()
            ],
            "items": [
                {
                    "name": item.name,
                    "path": item.path,
                    "is_directory": item.is_directory,
                    "parent_path": item.parent_path,
                    "size": item.size,
                    "modified_time": item.modified_time,
                    "is_git_tracked": item.is_git_tracked,
                    "git_status": item.git_status,
                    "is_staged": item.is_staged,
                    "is_hidden": item.is_hidden,
                    "is_ignored": item.is_ignored,
                    "children": item.children,
                    "is_loaded": item.is_loaded
                } for item in state.items
            ]
        }
        
        try:
            await self.control_channel.send(payload)
            logger.debug("Successfully sent project state update for session: %s", 
                        state.client_session_id)
        except Exception as e:
            logger.error("Failed to send project state update for session %s: %s", 
                        state.client_session_id, e)


class PeriodicGitMonitor:
    """Monitors git changes via periodic polling instead of file watching."""
    
    def __init__(self, state_manager: 'CentralizedProjectStateManager', 
                 poll_interval: float = 0.5):
        self.state_manager = state_manager
        self.poll_interval = poll_interval
        self._monitor_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
    
    def start_monitoring(self):
        """Start periodic git monitoring."""
        if self._monitor_task is None or self._monitor_task.done():
            self._stop_event.clear()
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info("Started periodic git monitoring (interval: %ss)", 
                       self.poll_interval)
    
    def stop_monitoring(self):
        """Stop periodic git monitoring."""
        if self._monitor_task and not self._monitor_task.done():
            self._stop_event.set()
            self._monitor_task.cancel()
            logger.info("Stopped periodic git monitoring")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while not self._stop_event.is_set():
            try:
                # Check all active projects for git changes
                any_changes = False
                for client_session_id in self.state_manager.get_active_sessions():
                    changed = await self.state_manager.refresh_git_state(client_session_id)
                    if changed:
                        any_changes = True
                
                # Write debug state periodically even if no changes (keeps file fresh)
                if hasattr(self.state_manager, '_write_debug_state'):
                    self.state_manager._write_debug_state()
                
                # Wait for next poll interval
                await asyncio.wait_for(self._stop_event.wait(), 
                                     timeout=self.poll_interval)
                break  # Stop event was set
                
            except asyncio.TimeoutError:
                # Timeout is expected, continue monitoring
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in git monitoring loop: %s", e)
                await asyncio.sleep(self.poll_interval)