"""File system monitoring for project state changes.

This module provides the FileSystemWatcher class which monitors file system
changes using the watchdog library and triggers project state updates when
files or directories are modified.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Set

logger = logging.getLogger(__name__)

# Cross-platform file system monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
    logger.info("Watchdog library available for file system monitoring")
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    logger.warning("Watchdog library not available - file system monitoring disabled")


class FileSystemWatcher:
    """Watches file system changes for project folders."""
    
    def __init__(self, project_manager):
        self.project_manager = project_manager  # Reference to ProjectStateManager
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[FileSystemEventHandler] = None
        self.watched_paths: Set[str] = set()
        # Store reference to the event loop for thread-safe async task creation
        try:
            self.event_loop = asyncio.get_running_loop()
            logger.info("🔍 [TRACE] ✅ Captured event loop reference for file system watcher: %s", self.event_loop)
        except RuntimeError:
            self.event_loop = None
            logger.error("🔍 [TRACE] ❌ No running event loop found - file system events may not work correctly")
        
        logger.info("🔍 [TRACE] WATCHDOG_AVAILABLE: %s", WATCHDOG_AVAILABLE)
        if WATCHDOG_AVAILABLE:
            logger.info("🔍 [TRACE] Initializing file system watcher...")
            self._initialize_watcher()
        else:
            logger.error("🔍 [TRACE] ❌ Watchdog not available - file monitoring disabled")
    
    def _initialize_watcher(self):
        """Initialize file system watcher."""
        if not WATCHDOG_AVAILABLE:
            logger.warning("Watchdog not available, file monitoring disabled")
            return
        
        class ProjectEventHandler(FileSystemEventHandler):
            def __init__(self, manager, watcher):
                self.manager = manager
                self.watcher = watcher
                super().__init__()
            
            def on_any_event(self, event):
                logger.info("🔍 [TRACE] FileSystemWatcher detected event: %s on path: %s", event.event_type, event.src_path)
                
                # Skip debug files to avoid feedback loops
                if event.src_path.endswith('project_state_debug.json'):
                    logger.info("🔍 [TRACE] Skipping debug file: %s", event.src_path)
                    return
                
                # Only process events that represent actual content changes
                # Skip opened/closed events that don't indicate file modifications
                if event.event_type in ('opened', 'closed'):
                    logger.info("🔍 [TRACE] Skipping opened/closed event: %s", event.event_type)
                    return
                
                # Skip all .git folder events - git monitoring is handled by centralized periodic polling
                path_parts = Path(event.src_path).parts
                if '.git' in path_parts:
                    logger.debug("Skipping .git folder event (centralized monitoring active): %s", event.src_path)
                    return
                else:
                    logger.info("🔍 [TRACE] Processing non-git file event: %s", event.src_path)
                    # Only log significant file changes, not every single event
                    if event.event_type in ['created', 'deleted'] or event.src_path.endswith(('.py', '.js', '.html', '.css', '.json', '.md')):
                        logger.debug("File system event: %s - %s", event.event_type, os.path.basename(event.src_path))
                    else:
                        logger.debug("File event: %s", os.path.basename(event.src_path))
                
                # Schedule async task in the main event loop from this watchdog thread
                logger.info("🔍 [TRACE] About to schedule async handler - event_loop exists: %s, closed: %s", 
                           self.watcher.event_loop is not None, 
                           self.watcher.event_loop.is_closed() if self.watcher.event_loop else "N/A")
                
                if self.watcher.event_loop and not self.watcher.event_loop.is_closed():
                    try:
                        future = asyncio.run_coroutine_threadsafe(
                            self.manager._handle_file_change(event), 
                            self.watcher.event_loop
                        )
                        logger.info("🔍 [TRACE] ✅ Successfully scheduled file change handler for: %s", event.src_path)
                    except Exception as e:
                        logger.error("🔍 [TRACE] ❌ Failed to schedule file change handler: %s", e)
                else:
                    logger.error("🔍 [TRACE] ❌ No event loop available to handle file change: %s", event.src_path)
        
        self.event_handler = ProjectEventHandler(self.project_manager, self)
        self.observer = Observer()
    
    def start_watching(self, path: str):
        """Start watching a specific path."""
        if not WATCHDOG_AVAILABLE or not self.observer:
            logger.warning("Watchdog not available, cannot start watching: %s", path)
            return
        
        if path not in self.watched_paths:
            try:
                # Use recursive=False to watch only direct contents of each folder
                self.observer.schedule(self.event_handler, path, recursive=False)
                self.watched_paths.add(path)
                logger.info("Started watching path (non-recursive): %s", path)
                
                if not self.observer.is_alive():
                    self.observer.start()
                    logger.info("Started file system observer")
            except Exception as e:
                logger.error("Error starting file watcher for %s: %s", path, e)
        else:
            logger.debug("Path already being watched: %s", path)
    
    def start_watching_git_directory(self, git_path: str):
        """Start watching a .git directory for git status changes."""
        # DISABLED: Git monitoring is now handled by centralized hash-based periodic polling
        logger.debug("Git directory monitoring disabled - using centralized periodic polling: %s", git_path)
        return
    
    def stop_watching(self, path: str):
        """Stop watching a specific path."""
        if not WATCHDOG_AVAILABLE or not self.observer:
            return
        
        if path in self.watched_paths:
            # Note: watchdog doesn't have direct path removal, would need to recreate observer
            self.watched_paths.discard(path)
            logger.debug("Stopped watching path: %s", path)
    
    def stop_all(self):
        """Stop all file watching."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            self.watched_paths.clear()