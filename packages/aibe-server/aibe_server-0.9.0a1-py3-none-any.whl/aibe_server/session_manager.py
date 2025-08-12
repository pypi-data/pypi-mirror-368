"""
SessionManager - Centralized session management utility
Eliminates duplicate session validation and management logic
Direct port from SessionManager.cjs with exact functional parity
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import uuid


class SessionManager:
    """
    Session management for browser tab isolation using sessionStorage tabIds
    Exact port of Node.js SessionManager.cjs functionality
    """
    
    def __init__(self):
        # In-memory session store for tab isolation (using sessionStorage tabIds)
        self.session_store: Dict[str, Dict[str, Any]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def validate_session(self, session_id: str) -> Dict[str, Any]:
        """
        Validate and retrieve session data
        
        Args:
            session_id: The session ID to validate
            
        Returns:
            Dict with keys: session, sessionInfo, error (error is None if valid)
        """
        session = self.session_store.get(session_id)
        session_info = self.active_sessions.get(session_id)
        
        if not session:
            return {
                "session": None,
                "sessionInfo": None,
                "error": {
                    "message": f"Session {session_id} not found",
                    "availableSessions": list(self.session_store.keys())
                }
            }
        
        return {
            "session": session,
            "sessionInfo": session_info,  # sessionInfo may not exist for all sessions
            "error": None
        }
    
    def validate_session_with_response(self, session_id: str, response_handler) -> Optional[Dict[str, Any]]:
        """
        Validate session and return 404 response if invalid
        
        Args:
            session_id: The session ID to validate
            response_handler: Function to call with error response
            
        Returns:
            Dict with {session, sessionInfo} if valid, None if response sent
        """
        result = self.validate_session(session_id)
        
        if result["error"]:
            response_handler(404, {
                "error": result["error"]["message"],
                "availableSessions": result["error"]["availableSessions"]
            })
            return None
        
        return result
    
    def get_or_create_session(self, tab_id: str) -> Dict[str, Any]:
        """
        Get or create session from session_store
        
        Args:
            tab_id: The tab ID to use as session identifier
            
        Returns:
            The session object
        """
        if tab_id not in self.session_store:
            self.session_store[tab_id] = {
                "sessionId": tab_id,
                "actorCommands": [],
                "created": datetime.now().isoformat(),
                "unprocessedEvents": [],
                "processedEvents": [],
                "retrievedActorCommands": []
            }
        
        return self.session_store[tab_id]
    
    def register_session(self, session_id: str, session_info: Dict[str, Any]) -> None:
        """
        Register a new session in the active_sessions registry
        
        Args:
            session_id: The session ID
            session_info: Session information object
        """
        self.active_sessions[session_id] = {
            **session_info,
            "lastActivity": datetime.now().isoformat()
        }
    
    def update_session_activity(self, session_id: str) -> None:
        """
        Update the last activity timestamp for a session
        
        Args:
            session_id: The session ID to update
        """
        session_info = self.active_sessions.get(session_id)
        if session_info:
            session_info["lastActivity"] = datetime.now().isoformat()
    
    def get_session_registry(self) -> List[Dict[str, Any]]:
        """
        Get all active sessions for discovery
        
        Returns:
            Array of session information objects
        """
        sessions = []
        for session_id, session_info in self.active_sessions.items():
            sessions.append({
                "sessionId": session_id,
                **session_info
            })
        return sessions
    
    def cleanup_expired_sessions(self, max_age_ms: int = 24 * 60 * 60 * 1000) -> int:
        """
        Clean up expired sessions
        
        Args:
            max_age_ms: Maximum age in milliseconds before cleanup (default: 24 hours)
            
        Returns:
            Number of sessions cleaned up
        """
        now = datetime.now()
        max_age_delta = timedelta(milliseconds=max_age_ms)
        expired_sessions = []
        
        for session_id, session_info in self.active_sessions.items():
            last_activity = datetime.fromisoformat(session_info["lastActivity"])
            if now - last_activity > max_age_delta:
                expired_sessions.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_sessions:
            self.active_sessions.pop(session_id, None)
            self.session_store.pop(session_id, None)
        
        return len(expired_sessions)
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data without validation (for middleware use)
        
        Args:
            session_id: The session ID
            
        Returns:
            Session data or None if not found
        """
        return self.session_store.get(session_id)
    
    def has_session(self, session_id: str) -> bool:
        """
        Check if a session exists
        
        Args:
            session_id: The session ID to check
            
        Returns:
            True if session exists
        """
        return session_id in self.session_store
    
    def get_all_session_ids(self) -> List[str]:
        """
        Get all session IDs
        
        Returns:
            Array of session IDs
        """
        return list(self.session_store.keys())
        
    def close_session(self, session_id: str) -> bool:
        """
        Explicitly close and remove a session
        
        Args:
            session_id: The session ID to close
            
        Returns:
            True if session was found and closed, False otherwise
        """
        session_found = False
        
        if session_id in self.active_sessions:
            self.active_sessions.pop(session_id)
            session_found = True
            
        if session_id in self.session_store:
            self.session_store.pop(session_id)
            session_found = True
            
        return session_found