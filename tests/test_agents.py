"""
Basic tests for agent functionality
"""

import pytest
import os
from agents.orchestrator import OrchestratorAgent
from agents.meal_planner import MealPlannerAgent
from memory.session_service import InMemorySessionService
from memory.memory_bank import MemoryBank


def test_session_service():
    """Test session service functionality"""
    service = InMemorySessionService()
    
    # Create session
    session = service.create_session("test_user")
    assert session is not None
    assert session.user_id == "test_user"
    
    # Get session
    retrieved = service.get_session(session.session_id)
    assert retrieved is not None
    assert retrieved.session_id == session.session_id
    
    # Update context
    success = service.update_session_context(session.session_id, {"test": "value"})
    assert success is True
    
    retrieved = service.get_session(session.session_id)
    assert retrieved.context.get("test") == "value"


def test_memory_bank():
    """Test memory bank functionality"""
    # Use a test storage path
    bank = MemoryBank(storage_path="test_memory.json")
    
    # Add preference
    bank.add_preference("test_user", "dietary_restriction", "vegetarian")
    
    # Get preference
    prefs = bank.get_preferences("test_user")
    assert prefs["dietary_restriction"] == "vegetarian"
    
    # Add meal history
    bank.add_meal_history("test_user", {"meals": ["meal1", "meal2"]})
    
    # Get history
    history = bank.get_meal_history("test_user", limit=1)
    assert len(history) > 0
    
    # Cleanup
    import os
    if os.path.exists("test_memory.json"):
        os.remove("test_memory.json")


def test_meal_planner_agent():
    """Test meal planner agent"""
    agent = MealPlannerAgent()
    
    # Test meal planning (will use mock if no API key)
    result = agent.plan_meals(
        days=3,
        dietary_restrictions=["vegetarian"],
        preferences=["Italian"]
    )
    
    assert result is not None
    assert "meals" in result
    assert len(result["meals"]) > 0


def test_orchestrator_agent():
    """Test orchestrator agent"""
    agent = OrchestratorAgent()
    
    # Create session
    session_id = agent.create_session("test_user")
    assert session_id is not None
    
    # Plan meals (will use mock if no API key)
    result = agent.plan_meals(
        session_id=session_id,
        days=2,
        dietary_restrictions=["vegetarian"],
        include_shopping_list=True
    )
    
    assert result is not None
    assert "meal_plan" in result
    assert "shopping_list" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


