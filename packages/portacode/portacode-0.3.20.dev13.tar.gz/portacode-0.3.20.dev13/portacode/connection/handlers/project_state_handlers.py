"""Project state handlers - modular architecture.

This module serves as a compatibility layer that imports all the project state
handlers from the new modular structure. This ensures existing code continues
to work while providing access to the new architecture.

The original monolithic file has been broken down into a modular structure
located in the project_state/ subdirectory. All functionality, logging, and
documentation has been preserved while improving maintainability.

For detailed information about the new structure, see:
project_state/README.md
"""

# Import everything from the modular structure for backward compatibility
from .project_state import *

# Use the new centralized handlers for better performance and reliability
from .project_state.centralized_handlers import (
    CentralizedProjectStateFolderExpandHandler as ProjectStateFolderExpandHandler,
    CentralizedProjectStateFolderCollapseHandler as ProjectStateFolderCollapseHandler,
    CentralizedProjectStateFileOpenHandler as ProjectStateFileOpenHandler,
    CentralizedProjectStateTabCloseHandler as ProjectStateTabCloseHandler,
    CentralizedProjectStateSetActiveTabHandler as ProjectStateSetActiveTabHandler,
    CentralizedProjectStateDiffOpenHandler as ProjectStateDiffOpenHandler,
    CentralizedProjectStateGitStageHandler as ProjectStateGitStageHandler,
    CentralizedProjectStateGitUnstageHandler as ProjectStateGitUnstageHandler,
    CentralizedProjectStateGitRevertHandler as ProjectStateGitRevertHandler,
    handle_centralized_client_session_cleanup as handle_client_session_cleanup
)

from .project_state.centralized_manager import (
    get_or_create_centralized_manager as get_or_create_project_state_manager,
    reset_global_centralized_manager as reset_global_project_state_manager,
    debug_global_centralized_manager_state as debug_global_manager_state
)

from .project_state.utils import generate_tab_key

# Re-export with the old private function names for backward compatibility
_get_or_create_project_state_manager = get_or_create_project_state_manager
_reset_global_project_state_manager = reset_global_project_state_manager
_debug_global_manager_state = debug_global_manager_state
