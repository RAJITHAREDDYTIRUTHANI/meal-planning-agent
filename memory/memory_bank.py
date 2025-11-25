"""
Memory Bank for long-term storage of user preferences and history
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import json
import os


class UserPreference(BaseModel):
    """User preference entry"""
    user_id: str
    preference_type: str  # e.g., "dietary_restriction", "cuisine", "budget"
    value: Any
    created_at: datetime
    last_updated: datetime


class MealHistory(BaseModel):
    """Historical meal plan entry"""
    user_id: str
    meal_plan: Dict[str, Any]
    date: datetime
    feedback: Optional[str] = None


class MemoryBank:
    """
    Memory Bank for long-term storage of user preferences, meal history,
    and other persistent data. This implements long-term memory for the agent.
    """
    
    def __init__(self, storage_path: str = "memory_storage.json"):
        """
        Initialize the memory bank.
        
        Args:
            storage_path: Path to JSON file for persistence
        """
        self.storage_path = storage_path
        self.preferences: Dict[str, List[UserPreference]] = {}  # user_id -> preferences
        self.meal_history: Dict[str, List[MealHistory]] = {}  # user_id -> meal history
        self.load_from_disk()
    
    def load_from_disk(self):
        """Load data from disk if file exists"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    # Load preferences
                    for user_id, prefs in data.get("preferences", {}).items():
                        self.preferences[user_id] = [
                            UserPreference(**p) for p in prefs
                        ]
                    # Load meal history
                    for user_id, history in data.get("meal_history", {}).items():
                        self.meal_history[user_id] = [
                            MealHistory(**h) for h in history
                        ]
            except Exception as e:
                print(f"Error loading memory bank: {e}")
    
    def save_to_disk(self):
        """Save data to disk"""
        try:
            data = {
                "preferences": {
                    user_id: [p.dict() for p in prefs]
                    for user_id, prefs in self.preferences.items()
                },
                "meal_history": {
                    user_id: [h.dict() for h in history]
                    for user_id, history in self.meal_history.items()
                }
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, default=str, indent=2)
        except Exception as e:
            print(f"Error saving memory bank: {e}")
    
    def add_preference(self, user_id: str, preference_type: str, value: Any):
        """
        Add or update a user preference.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference (e.g., "dietary_restriction")
            value: Preference value
        """
        if user_id not in self.preferences:
            self.preferences[user_id] = []
        
        # Check if preference already exists
        existing = next(
            (p for p in self.preferences[user_id] if p.preference_type == preference_type),
            None
        )
        
        now = datetime.now()
        if existing:
            existing.value = value
            existing.last_updated = now
        else:
            self.preferences[user_id].append(
                UserPreference(
                    user_id=user_id,
                    preference_type=preference_type,
                    value=value,
                    created_at=now,
                    last_updated=now
                )
            )
        
        self.save_to_disk()
    
    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get all preferences for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of preferences
        """
        prefs = self.preferences.get(user_id, [])
        return {p.preference_type: p.value for p in prefs}
    
    def get_preference(self, user_id: str, preference_type: str) -> Optional[Any]:
        """
        Get a specific preference for a user.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference
            
        Returns:
            Preference value or None
        """
        prefs = self.preferences.get(user_id, [])
        pref = next((p for p in prefs if p.preference_type == preference_type), None)
        return pref.value if pref else None
    
    def add_meal_history(self, user_id: str, meal_plan: Dict[str, Any], feedback: Optional[str] = None):
        """
        Add a meal plan to history.
        
        Args:
            user_id: User identifier
            meal_plan: Meal plan data
            feedback: Optional user feedback
        """
        if user_id not in self.meal_history:
            self.meal_history[user_id] = []
        
        self.meal_history[user_id].append(
            MealHistory(
                user_id=user_id,
                meal_plan=meal_plan,
                date=datetime.now(),
                feedback=feedback
            )
        )
        
        # Keep only last 50 entries per user
        if len(self.meal_history[user_id]) > 50:
            self.meal_history[user_id] = self.meal_history[user_id][-50:]
        
        self.save_to_disk()
    
    def get_meal_history(self, user_id: str, limit: int = 10) -> List[MealHistory]:
        """
        Get meal history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries to return
            
        Returns:
            List of meal history entries
        """
        history = self.meal_history.get(user_id, [])
        return history[-limit:] if limit else history
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user context including preferences and recent history.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user context
        """
        return {
            "preferences": self.get_preferences(user_id),
            "recent_meals": [
                {
                    "date": h.date.isoformat(),
                    "meals": h.meal_plan.get("meals", []),
                    "feedback": h.feedback
                }
                for h in self.get_meal_history(user_id, limit=5)
            ]
        }

