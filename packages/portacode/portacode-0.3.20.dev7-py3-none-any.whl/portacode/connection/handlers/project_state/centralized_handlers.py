"""
Updated handlers that use the centralized project state manager.

These handlers replace the old handlers with clean interfaces to the
centralized state management system.
"""

import logging
from typing import Any, Dict

from ..base import AsyncHandler
from .centralized_manager import get_or_create_centralized_manager

logger = logging.getLogger(__name__)


class CentralizedProjectStateFolderExpandHandler(AsyncHandler):
    """Handler for expanding project folders using centralized state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_folder_expand"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Expand a folder in project state."""
        server_project_id = message.get("project_id")
        folder_path = message.get("folder_path")
        source_client_session = message.get("source_client_session")
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not folder_path:
            raise ValueError("folder_path is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        logger.info("Expanding folder %s for session %s", folder_path, source_client_session)
        
        # Get centralized manager
        manager = get_or_create_centralized_manager(self.context, self.control_channel)
        
        # Expand folder
        success = await manager.expand_folder(source_client_session, folder_path)
        
        return {
            "event": "project_state_folder_expand_response",
            "project_id": server_project_id,
            "folder_path": folder_path,
            "success": success
        }


class CentralizedProjectStateFolderCollapseHandler(AsyncHandler):
    """Handler for collapsing project folders using centralized state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_folder_collapse"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Collapse a folder in project state."""
        server_project_id = message.get("project_id")
        folder_path = message.get("folder_path")
        source_client_session = message.get("source_client_session")
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not folder_path:
            raise ValueError("folder_path is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        logger.info("Collapsing folder %s for session %s", folder_path, source_client_session)
        
        # Get centralized manager
        manager = get_or_create_centralized_manager(self.context, self.control_channel)
        
        # Collapse folder
        success = await manager.collapse_folder(source_client_session, folder_path)
        
        return {
            "event": "project_state_folder_collapse_response",
            "project_id": server_project_id,
            "folder_path": folder_path,
            "success": success
        }


class CentralizedProjectStateFileOpenHandler(AsyncHandler):
    """Handler for opening files using centralized state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_file_open"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Open a file in project state."""
        server_project_id = message.get("project_id")
        file_path = message.get("file_path")
        source_client_session = message.get("source_client_session")
        set_active = message.get("set_active", True)
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not file_path:
            raise ValueError("file_path is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        logger.info("Opening file %s for session %s", file_path, source_client_session)
        
        # Get centralized manager
        manager = get_or_create_centralized_manager(self.context, self.control_channel)
        
        # Open file
        success = await manager.open_file_tab(source_client_session, file_path, set_active)
        
        return {
            "event": "project_state_file_open_response",
            "project_id": server_project_id,
            "file_path": file_path,
            "success": success,
            "set_active": set_active
        }


class CentralizedProjectStateTabCloseHandler(AsyncHandler):
    """Handler for closing tabs using centralized state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_tab_close"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Close a tab in project state."""
        server_project_id = message.get("project_id")
        tab_id = message.get("tab_id")
        source_client_session = message.get("source_client_session")
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not tab_id:
            raise ValueError("tab_id is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        logger.info("Closing tab %s for session %s", tab_id, source_client_session)
        
        # Get centralized manager
        manager = get_or_create_centralized_manager(self.context, self.control_channel)
        
        # Close tab
        success = await manager.close_tab(source_client_session, tab_id)
        
        return {
            "event": "project_state_tab_close_response",
            "project_id": server_project_id,
            "tab_id": tab_id,
            "success": success
        }


class CentralizedProjectStateGitStageHandler(AsyncHandler):
    """Handler for staging files using centralized state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_git_stage"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Stage a file in git."""
        server_project_id = message.get("project_id")
        file_path = message.get("file_path")
        source_client_session = message.get("source_client_session")
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not file_path:
            raise ValueError("file_path is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        logger.info("Staging file %s for session %s", file_path, source_client_session)
        
        # Get centralized manager
        manager = get_or_create_centralized_manager(self.context, self.control_channel)
        
        # Stage file
        success = await manager.stage_file(source_client_session, file_path)
        
        return {
            "event": "project_state_git_stage_response",
            "project_id": server_project_id,
            "file_path": file_path,
            "success": success
        }


class CentralizedProjectStateGitUnstageHandler(AsyncHandler):
    """Handler for unstaging files using centralized state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_git_unstage"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Unstage a file in git."""
        server_project_id = message.get("project_id")
        file_path = message.get("file_path")
        source_client_session = message.get("source_client_session")
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not file_path:
            raise ValueError("file_path is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        logger.info("Unstaging file %s for session %s", file_path, source_client_session)
        
        # Get centralized manager
        manager = get_or_create_centralized_manager(self.context, self.control_channel)
        
        # Unstage file
        success = await manager.unstage_file(source_client_session, file_path)
        
        return {
            "event": "project_state_git_unstage_response",
            "project_id": server_project_id,
            "file_path": file_path,
            "success": success
        }


class CentralizedProjectStateGitRevertHandler(AsyncHandler):
    """Handler for reverting files using centralized state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_git_revert"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Revert a file in git."""
        server_project_id = message.get("project_id")
        file_path = message.get("file_path")
        source_client_session = message.get("source_client_session")
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not file_path:
            raise ValueError("file_path is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        logger.info("Reverting file %s for session %s", file_path, source_client_session)
        
        # Get centralized manager
        manager = get_or_create_centralized_manager(self.context, self.control_channel)
        
        # Revert file
        success = await manager.revert_file(source_client_session, file_path)
        
        return {
            "event": "project_state_git_revert_response",
            "project_id": server_project_id,
            "file_path": file_path,
            "success": success
        }


class CentralizedProjectStateSetActiveTabHandler(AsyncHandler):
    """Handler for setting active tab using centralized state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_set_active_tab"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Set active tab in project state."""
        server_project_id = message.get("project_id")
        tab_id = message.get("tab_id")  # Can be None to clear active tab
        source_client_session = message.get("source_client_session")
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        logger.info("Setting active tab %s for session %s", tab_id, source_client_session)
        
        # Note: Active tab is deprecated in the new centralized system
        # This handler maintains compatibility but does nothing
        logger.info("Active tab functionality is deprecated in centralized system")
        
        return {
            "event": "project_state_set_active_tab_response",
            "project_id": server_project_id,
            "tab_id": tab_id,
            "success": True
        }


class CentralizedProjectStateDiffOpenHandler(AsyncHandler):
    """Handler for opening diff tabs using centralized state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_diff_open"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Open a diff tab comparing file versions at different git timeline points."""
        server_project_id = message.get("project_id")
        file_path = message.get("file_path")
        from_ref = message.get("from_ref")
        to_ref = message.get("to_ref")
        from_hash = message.get("from_hash")
        to_hash = message.get("to_hash")
        source_client_session = message.get("source_client_session")
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not file_path:
            raise ValueError("file_path is required")
        if not from_ref:
            raise ValueError("from_ref is required")
        if not to_ref:
            raise ValueError("to_ref is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        # Validate reference types
        valid_refs = {'head', 'staged', 'working', 'commit'}
        if from_ref not in valid_refs:
            raise ValueError(f"Invalid from_ref: {from_ref}. Must be one of {valid_refs}")
        if to_ref not in valid_refs:
            raise ValueError(f"Invalid to_ref: {to_ref}. Must be one of {valid_refs}")
        
        # Validate commit hashes are provided when needed
        if from_ref == 'commit' and not from_hash:
            raise ValueError("from_hash is required when from_ref='commit'")
        if to_ref == 'commit' and not to_hash:
            raise ValueError("to_hash is required when to_ref='commit'")
        
        logger.info("Opening diff tab %s (%s->%s) for session %s", 
                   file_path, from_ref, to_ref, source_client_session)
        
        # Get centralized manager
        manager = get_or_create_centralized_manager(self.context, self.control_channel)
        
        # For now, return success but don't actually implement diff tabs
        # This would need to be implemented in the centralized manager
        logger.info("Diff tab functionality not yet implemented in centralized system")
        
        return {
            "event": "project_state_diff_open_response",
            "project_id": server_project_id,
            "file_path": file_path,
            "from_ref": from_ref,
            "to_ref": to_ref,
            "from_hash": from_hash,
            "to_hash": to_hash,
            "success": False,  # Not implemented yet
            "error": "Diff tab functionality not yet implemented in centralized system"
        }


# Handler for explicit client session cleanup
async def handle_centralized_client_session_cleanup(handler, payload: Dict[str, Any], 
                                                   source_client_session: str) -> Dict[str, Any]:
    """Handle cleanup of a client session using centralized manager."""
    client_session_id = payload.get('client_session_id')
    
    if not client_session_id:
        logger.error("client_session_id is required for client session cleanup")
        return {
            "event": "client_session_cleanup_response",
            "success": False,
            "error": "client_session_id is required"
        }
    
    logger.info("Handling centralized cleanup for client session: %s", client_session_id)
    
    # Get centralized manager
    manager = get_or_create_centralized_manager(handler.context, handler.control_channel)
    
    # Clean up the client session
    await manager.cleanup_project_state(client_session_id)
    
    logger.info("Centralized client session cleanup completed: %s", client_session_id)
    
    return {
        "event": "client_session_cleanup_response",
        "client_session_id": client_session_id,
        "success": True
    }