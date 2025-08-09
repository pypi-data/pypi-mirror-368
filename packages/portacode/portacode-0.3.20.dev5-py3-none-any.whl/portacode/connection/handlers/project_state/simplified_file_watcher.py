"""
Simplified file system monitoring for the centralized project state system.

This replaces the complex FileSystemWatcher with a cleaner implementation that:
- Only monitors regular files and folders (not git directories)
- Works directly with the centralized manager
- Avoids the recursive event loops and flooding issues
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from .centralized_manager import CentralizedProjectStateManager

logger = logging.getLogger(__name__)

# Cross-platform file system monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
    logger.info("Watchdog library available for simplified file system monitoring")
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    logger.warning("Watchdog library not available - file system monitoring disabled")


class SimplifiedFileSystemWatcher:
    """Simplified file system watcher that only monitors regular files and folders."""
    
    def __init__(self, manager: 'CentralizedProjectStateManager'):
        self.manager = manager
        self.observer: Optional[Observer] = None
        self.event_handler: Optional['SimplifiedEventHandler'] = None
        self.watched_paths: Set[str] = set()
        self.event_loop = asyncio.get_running_loop()
        
        if WATCHDOG_AVAILABLE:
            self._initialize_observer()
            logger.info("Initialized simplified file system watcher")
        else:
            logger.warning("File system monitoring not available - watchdog not installed")
    
    def _initialize_observer(self):
        """Initialize the watchdog observer and event handler."""
        if not WATCHDOG_AVAILABLE:
            return
        
        self.event_handler = SimplifiedEventHandler(self.manager, self)
        self.observer = Observer()
    
    def start_watching(self, path: str):
        """Start watching a specific path for regular file/folder changes."""
        if not WATCHDOG_AVAILABLE or not self.observer:
            logger.warning("Cannot start watching %s - watchdog not available", path)
            return
        
        if path not in self.watched_paths:
            try:
                # Only watch for non-git file changes
                self.observer.schedule(self.event_handler, path, recursive=False)
                self.watched_paths.add(path)
                logger.info("Started watching path for file changes: %s", path)
                
                if not self.observer.is_alive():
                    self.observer.start()
                    logger.info("Started simplified file system observer")
            except Exception as e:
                logger.error("Error starting file watcher for %s: %s", path, e)
        else:
            logger.debug("Path already being watched: %s", path)
    
    def stop_watching(self, path: str):
        """Stop watching a specific path."""
        if not WATCHDOG_AVAILABLE or not self.observer:
            return
        
        if path in self.watched_paths:
            # Note: watchdog doesn't have direct path removal, would need to recreate observer
            self.watched_paths.discard(path)
            logger.debug("Stopped watching path: %s", path)
    
    def stop_all(self):
        """Stop all file system monitoring."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped simplified file system observer")


class SimplifiedEventHandler(FileSystemEventHandler):
    """Simplified event handler that only processes regular file/folder events."""
    
    def __init__(self, manager: 'CentralizedProjectStateManager', 
                 watcher: SimplifiedFileSystemWatcher):
        super().__init__()
        self.manager = manager
        self.watcher = watcher
    
    def on_any_event(self, event):
        """Handle any file system event."""
        if not event.src_path:
            return
        
        # Skip git directories entirely - they're handled by periodic polling
        path_parts = Path(event.src_path).parts
        if '.git' in path_parts:
            logger.debug("Skipping git directory event: %s", event.src_path)
            return
        
        # Skip opened/closed events that don't indicate file modifications
        if event.event_type in ('opened', 'closed'):
            logger.debug("Skipping opened/closed event: %s", event.event_type)
            return
        
        # Only process meaningful file/folder changes
        if event.event_type in ('created', 'deleted', 'modified', 'moved'):
            logger.debug("Processing file system event: %s - %s", 
                        event.event_type, os.path.basename(event.src_path))
            
            # Schedule async handling in the main event loop
            if self.watcher.event_loop and not self.watcher.event_loop.is_closed():
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.manager.handle_file_change(event.src_path),
                        self.watcher.event_loop
                    )
                    logger.debug("Scheduled file change handler for: %s", event.src_path)
                except Exception as e:
                    logger.error("Failed to schedule file change handler: %s", e)
            else:
                logger.error("No event loop available to handle file change: %s", event.src_path)