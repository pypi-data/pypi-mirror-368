"""Project State Management Package

This package provides a modular architecture for managing project state in the
Portacode application, including file system monitoring, git integration,
tab management, and real-time state synchronization.

The package is organized into the following modules:

- models: Data structures and models (ProjectState, FileItem, TabInfo, etc.)
- git_manager: Git operations and repository management
- file_system_watcher: File system change monitoring
- manager: Central project state coordinator (legacy)
- centralized_manager: New centralized state manager with single source of truth
- handlers: Request handlers for various operations (legacy)
- centralized_handlers: New handlers using centralized state management
- utils: Utility functions and helpers

Usage (New Centralized System):
    from project_state.centralized_manager import get_or_create_centralized_manager
    from project_state.centralized_handlers import CentralizedProjectStateFolderExpandHandler
    from project_state.centralized_state import CentralizedProjectState

Usage (Legacy System):
    from project_state.manager import get_or_create_project_state_manager
    from project_state.handlers import ProjectStateFolderExpandHandler
    from project_state.models import ProjectState, FileItem
"""

# Public API exports
from .models import (
    ProjectState,
    FileItem,
    TabInfo,
    MonitoredFolder,
    GitFileChange,
    GitDetailedStatus
)

# Legacy manager (for backwards compatibility)
from .manager import (
    ProjectStateManager,
    get_or_create_project_state_manager,
    reset_global_project_state_manager,
    debug_global_manager_state
)

# New centralized system
from .centralized_manager import (
    CentralizedProjectStateManager,
    get_or_create_centralized_manager
)

from .centralized_state import (
    CentralizedProjectState,
    GitStateSnapshot,
    StateUpdateManager,
    StateNotificationManager,
    PeriodicGitMonitor
)

from .git_manager import GitManager
from .file_system_watcher import FileSystemWatcher

# Legacy handlers (for backwards compatibility)
from .handlers import (
    ProjectStateFolderExpandHandler,
    ProjectStateFolderCollapseHandler,
    ProjectStateFileOpenHandler,
    ProjectStateTabCloseHandler,
    ProjectStateSetActiveTabHandler,
    ProjectStateDiffOpenHandler,
    ProjectStateGitStageHandler,
    ProjectStateGitUnstageHandler,
    ProjectStateGitRevertHandler,
    handle_client_session_cleanup
)

# New centralized handlers
from .centralized_handlers import (
    CentralizedProjectStateFolderExpandHandler,
    CentralizedProjectStateFolderCollapseHandler,
    CentralizedProjectStateFileOpenHandler,
    CentralizedProjectStateTabCloseHandler,
    CentralizedProjectStateGitStageHandler,
    CentralizedProjectStateGitUnstageHandler,
    CentralizedProjectStateGitRevertHandler,
    handle_centralized_client_session_cleanup
)

from .utils import generate_tab_key, generate_tab_id

__all__ = [
    # Models
    'ProjectState',
    'FileItem',
    'TabInfo',
    'MonitoredFolder',
    'GitFileChange',
    'GitDetailedStatus',
    
    # Core classes
    'ProjectStateManager',  # Legacy
    'CentralizedProjectStateManager',  # New
    'CentralizedProjectState',  # New
    'GitStateSnapshot',  # New
    'StateUpdateManager',  # New
    'StateNotificationManager',  # New
    'PeriodicGitMonitor',  # New
    'GitManager',
    'FileSystemWatcher',
    
    # Manager functions (Legacy)
    'get_or_create_project_state_manager',
    'reset_global_project_state_manager',
    'debug_global_manager_state',
    
    # Manager functions (New)
    'get_or_create_centralized_manager',
    
    # Legacy Handlers
    'ProjectStateFolderExpandHandler',
    'ProjectStateFolderCollapseHandler',
    'ProjectStateFileOpenHandler',
    'ProjectStateTabCloseHandler',
    'ProjectStateSetActiveTabHandler',
    'ProjectStateDiffOpenHandler',
    'ProjectStateGitStageHandler',
    'ProjectStateGitUnstageHandler',
    'ProjectStateGitRevertHandler',
    'handle_client_session_cleanup',
    
    # New Centralized Handlers
    'CentralizedProjectStateFolderExpandHandler',
    'CentralizedProjectStateFolderCollapseHandler',
    'CentralizedProjectStateFileOpenHandler',
    'CentralizedProjectStateTabCloseHandler',
    'CentralizedProjectStateGitStageHandler',
    'CentralizedProjectStateGitUnstageHandler',
    'CentralizedProjectStateGitRevertHandler',
    'handle_centralized_client_session_cleanup',
    
    # Utils
    'generate_tab_key',
    'generate_tab_id'
]