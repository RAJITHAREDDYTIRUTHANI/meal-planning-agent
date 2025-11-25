"""
In-memory session service for managing user sessions
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel


class Session(BaseModel):
    """Represents a user session"""
    session_id: str
    user_id: str
    created_at: datetime
    last_accessed: datetime
    context: Dict[str, Any]
    preferences: Dict[str, Any]
    
    class Config:
        arbitrary_types_allowed = True


class InMemorySessionService:
    """
    In-memory session service for managing user sessions and state.
    This implements session management for the agent system.
    """
    
    def __init__(self, session_timeout_minutes: int = 60):
        """
        Initialize the session service.
        
        Args:
            session_timeout_minutes: Minutes before a session expires
        """
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
    
    def create_session(self, user_id: str, initial_context: Optional[Dict[str, Any]] = None) -> Session:
        """
        Create a new session for a user.
        
        Args:
            user_id: Unique user identifier
            initial_context: Optional initial context data
            
        Returns:
            Created session object
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_accessed=now,
            context=initial_context or {},
            preferences={}
        )
        
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object or None if not found/expired
        """
        session = self.sessions.get(session_id)
        
        if session is None:
            return None
        
        # Check if session expired
        if datetime.now() - session.last_accessed > self.session_timeout:
            self.delete_session(session_id)
            return None
        
        # Update last accessed time
        session.last_accessed = datetime.now()
        return session
    
    def update_session_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """
        Update session context.
        
        Args:
            session_id: Session identifier
            context_updates: Dictionary of context updates
            
        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            return False
        
        session.context.update(context_updates)
        session.last_accessed = datetime.now()
        return True
    
    def update_preferences(self, session_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences in session.
        
        Args:
            session_id: Session identifier
            preferences: Dictionary of preference updates
            
        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            return False
        
        session.preferences.update(preferences)
        session.last_accessed = datetime.now()
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.
        
        Returns:
            Number of sessions removed
        """
        now = datetime.now()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session.last_accessed > self.session_timeout
        ]
        
        for sid in expired:
            del self.sessions[sid]
        
        return len(expired)
    
    def get_user_sessions(self, user_id: str) -> list[Session]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of active sessions
        """
        return [
            session for session in self.sessions.values()
            if session.user_id == user_id
        ]

