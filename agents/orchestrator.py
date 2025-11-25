"""
Orchestrator Agent - Main coordinator for the meal planning system
"""

from typing import Dict, List, Optional, Any
from .meal_planner import MealPlannerAgent
from .recipe_finder import RecipeFinderAgent
from .shopping_list import ShoppingListAgent
from tools.nutrition import NutritionAnalysisTool
from memory.session_service import InMemorySessionService
from memory.memory_bank import MemoryBank
from observability.logger import get_logger, setup_logger
from observability.tracer import get_tracer, setup_tracer, trace_operation

logger = get_logger("orchestrator")
tracer = get_tracer()


class OrchestratorAgent:
    """
    Main orchestrator agent that coordinates the meal planning workflow.
    Manages sessions, memory, and coordinates between specialized agents.
    """
    
    def __init__(self):
        """Initialize the orchestrator agent"""
        # Initialize sub-agents
        self.meal_planner = MealPlannerAgent()
        self.recipe_finder = RecipeFinderAgent()
        self.shopping_list_agent = ShoppingListAgent()
        
        # Initialize tools
        self.nutrition_tool = NutritionAnalysisTool()
        
        # Initialize session and memory services
        self.session_service = InMemorySessionService()
        self.memory_bank = MemoryBank()
        
        logger.info("Orchestrator agent initialized")
    
    def create_session(self, user_id: str, initial_preferences: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session for a user.
        
        Args:
            user_id: Unique user identifier
            initial_preferences: Optional initial preferences
            
        Returns:
            Session ID
        """
        span = tracer.start_span("create_session", user_id=user_id)
        
        # Load user context from memory bank
        user_context = self.memory_bank.get_user_context(user_id)
        
        # Merge with initial preferences
        if initial_preferences:
            user_context["preferences"].update(initial_preferences)
        
        # Create session
        session = self.session_service.create_session(
            user_id=user_id,
            initial_context={
                "user_context": user_context,
                "preferences": user_context.get("preferences", {})
            }
        )
        
        tracer.end_span(span, success=True, session_id=session.session_id)
        logger.info(f"Created session {session.session_id} for user {user_id}")
        
        return session.session_id
    
    @trace_operation("plan_meals_complete")
    def plan_meals(
        self,
        session_id: str,
        days: int,
        dietary_restrictions: Optional[List[str]] = None,
        preferences: Optional[List[str]] = None,
        budget: Optional[float] = None,
        include_nutrition: bool = True,
        include_shopping_list: bool = True
    ) -> Dict[str, Any]:
        """
        Complete meal planning workflow: plan meals, find recipes, generate shopping list.
        
        Args:
            session_id: Session identifier
            days: Number of days to plan for
            dietary_restrictions: List of dietary restrictions
            preferences: List of cuisine preferences
            budget: Budget constraint
            include_nutrition: Whether to include nutrition analysis
            include_shopping_list: Whether to generate shopping list
            
        Returns:
            Complete meal plan with recipes and shopping list
        """
        span = tracer.start_span("orchestrator_plan_meals", session_id=session_id, days=days)
        
        try:
            # Get session
            session = self.session_service.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            user_context = session.context.get("user_context", {})
            
            # Step 1: Plan meals (Sequential agent workflow)
            logger.info(f"Step 1: Planning meals for {days} days")
            meal_plan = self.meal_planner.plan_meals(
                days=days,
                dietary_restrictions=dietary_restrictions,
                preferences=preferences,
                budget=budget,
                user_context=user_context
            )
            
            tracer.add_event(span, "meals_planned", meal_count=len(meal_plan.get("meals", [])))
            
            # Step 2: Find recipes for meals
            logger.info("Step 2: Finding recipes for meals")
            recipe_results = self.recipe_finder.find_recipes_for_meals(
                meals=meal_plan.get("meals", []),
                dietary_restrictions=dietary_restrictions
            )
            
            tracer.add_event(span, "recipes_found", count=recipe_results.get("recipes_found", 0))
            
            # Step 3: Generate shopping list (if requested)
            shopping_list = None
            if include_shopping_list:
                logger.info("Step 3: Generating shopping list")
                shopping_list_result = self.shopping_list_agent.generate_shopping_list(
                    meal_recipes=recipe_results.get("meal_recipes", {}),
                    optimize=True
                )
                shopping_list = shopping_list_result.get("shopping_list")
            
            # Step 4: Analyze nutrition (if requested)
            nutrition_analysis = None
            if include_nutrition:
                logger.info("Step 4: Analyzing nutrition")
                meals_with_recipes = [
                    {"title": meal.get("name"), **recipe_results.get("meal_recipes", {}).get(meal.get("name"), {})}
                    for meal in meal_plan.get("meals", [])
                    if recipe_results.get("meal_recipes", {}).get(meal.get("name"))
                ]
                nutrition_analysis = self.nutrition_tool.analyze_meal_nutrition(meals_with_recipes)
            
            # Update session context
            self.session_service.update_session_context(session_id, {
                "last_meal_plan": meal_plan,
                "last_recipes": recipe_results,
                "last_shopping_list": shopping_list
            })
            
            # Save to memory bank
            self.memory_bank.add_meal_history(
                user_id=session.user_id,
                meal_plan=meal_plan
            )
            
            # Save preferences to memory
            if dietary_restrictions:
                for restriction in dietary_restrictions:
                    self.memory_bank.add_preference(
                        user_id=session.user_id,
                        preference_type="dietary_restriction",
                        value=restriction
                    )
            
            if preferences:
                self.memory_bank.add_preference(
                    user_id=session.user_id,
                    preference_type="cuisine_preferences",
                    value=preferences
                )
            
            result = {
                "meal_plan": meal_plan,
                "recipes": recipe_results,
                "shopping_list": shopping_list,
                "nutrition": nutrition_analysis,
                "session_id": session_id
            }
            
            tracer.end_span(span, success=True)
            logger.info(f"Meal planning complete for session {session_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in meal planning workflow: {e}")
            tracer.add_event(span, "error", error=str(e))
            tracer.end_span(span, success=False)
            raise
    
    def update_preferences(
        self,
        session_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Update user preferences.
        
        Args:
            session_id: Session identifier
            preferences: Dictionary of preferences to update
            
        Returns:
            True if successful
        """
        session = self.session_service.get_session(session_id)
        if not session:
            return False
        
        # Update session preferences
        self.session_service.update_preferences(session_id, preferences)
        
        # Update memory bank
        for key, value in preferences.items():
            self.memory_bank.add_preference(
                user_id=session.user_id,
                preference_type=key,
                value=value
            )
        
        logger.info(f"Updated preferences for session {session_id}")
        return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information dictionary
        """
        session = self.session_service.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_accessed": session.last_accessed.isoformat(),
            "preferences": session.preferences,
            "context_keys": list(session.context.keys())
        }


