"""
Meal Planner Agent - LLM-powered agent for planning meals
"""

import os
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from observability.logger import get_logger
from observability.tracer import get_tracer, trace_operation

logger = get_logger("meal_planner")
tracer = get_tracer()


class MealPlannerAgent:
    """
    LLM-powered agent that suggests meal plans based on user preferences,
    dietary restrictions, and nutritional goals.
    """
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the meal planner agent.
        
        Args:
            model_name: Name of the Gemini model to use
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found. Agent will use mock responses.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        
        self.model_name = model_name
    
    @trace_operation("plan_meals")
    def plan_meals(
        self,
        days: int,
        dietary_restrictions: Optional[List[str]] = None,
        preferences: Optional[List[str]] = None,
        budget: Optional[float] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a meal plan for specified number of days.
        
        Args:
            days: Number of days to plan for
            dietary_restrictions: List of dietary restrictions (e.g., ["vegetarian", "gluten-free"])
            preferences: List of cuisine preferences (e.g., ["Italian", "Mexican"])
            budget: Budget constraint in USD
            user_context: Additional user context from memory
            
        Returns:
            Dictionary with meal plan
        """
        span = tracer.start_span(
            "meal_planner_plan",
            days=days,
            restrictions=dietary_restrictions,
            preferences=preferences
        )
        
        try:
            # Build prompt for the LLM
            prompt = self._build_planning_prompt(
                days, dietary_restrictions, preferences, budget, user_context
            )
            
            if self.model:
                # Use Gemini to generate meal plan with fast timeout
                try:
                    from threading import Thread
                    import queue
                    result_queue = queue.Queue()
                    
                    def call_llm():
                        try:
                            response = self.model.generate_content(prompt)
                            result_queue.put(response.text)
                        except Exception as e:
                            result_queue.put(None)
                    
                    thread = Thread(target=call_llm, daemon=True)
                    thread.start()
                    thread.join(timeout=5)  # 5 second timeout
                    
                    if thread.is_alive():
                        # Timeout occurred - use mock data
                        logger.warning("LLM timeout, using mock meal plan")
                        meal_plan = self._generate_mock_meal_plan(days, dietary_restrictions, preferences)
                    else:
                        response_text = result_queue.get_nowait() if not result_queue.empty() else None
                        if response_text:
                            meal_plan = self._parse_llm_response(response_text, days)
                        else:
                            # LLM failed, use mock
                            meal_plan = self._generate_mock_meal_plan(days, dietary_restrictions, preferences)
                except Exception as e:
                    logger.warning(f"LLM call failed, using mock meal plan: {e}")
                    meal_plan = self._generate_mock_meal_plan(days, dietary_restrictions, preferences)
            else:
                # Fallback to mock response
                logger.info("Using mock meal plan (no API key)")
                meal_plan = self._generate_mock_meal_plan(days, dietary_restrictions, preferences)
            
            tracer.add_event(span, "meal_plan_generated", meal_count=len(meal_plan.get("meals", [])))
            tracer.end_span(span, success=True)
            
            return meal_plan
            
        except Exception as e:
            logger.error(f"Error planning meals: {e}")
            tracer.add_event(span, "error", error=str(e))
            tracer.end_span(span, success=False)
            # Return mock plan on error
            return self._generate_mock_meal_plan(days, dietary_restrictions, preferences)
    
    def _build_planning_prompt(
        self,
        days: int,
        dietary_restrictions: Optional[List[str]],
        preferences: Optional[List[str]],
        budget: Optional[float],
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build the prompt for meal planning"""
        prompt_parts = [
            f"Create a {days}-day meal plan with breakfast, lunch, and dinner for each day.",
        ]
        
        if dietary_restrictions:
            prompt_parts.append(f"Dietary restrictions: {', '.join(dietary_restrictions)}")
        
        if preferences:
            prompt_parts.append(f"Cuisine preferences: {', '.join(preferences)}")
        
        if budget:
            prompt_parts.append(f"Budget constraint: ${budget} for all meals")
        
        if user_context and user_context.get("preferences"):
            prefs = user_context["preferences"]
            if prefs.get("favorite_cuisines"):
                prompt_parts.append(f"Favorite cuisines: {prefs['favorite_cuisines']}")
            if prefs.get("disliked_foods"):
                prompt_parts.append(f"Avoid: {prefs['disliked_foods']}")
        
        prompt_parts.append("\nFormat the response as a JSON object with:")
        prompt_parts.append("- 'meals': array of meal objects, each with 'day', 'meal_type' (breakfast/lunch/dinner), 'name', 'description'")
        prompt_parts.append("- 'summary': brief summary of the meal plan")
        
        return "\n".join(prompt_parts)
    
    def _parse_llm_response(self, response_text: str, days: int) -> Dict[str, Any]:
        """Parse LLM response into structured meal plan"""
        # In a real implementation, this would parse JSON from the response
        # For now, return a structured format
        try:
            import json
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Could not parse LLM response as JSON: {e}")
        
        # Fallback to mock plan
        return self._generate_mock_meal_plan(days, None, None)
    
    def _generate_mock_meal_plan(
        self,
        days: int,
        dietary_restrictions: Optional[List[str]],
        preferences: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Generate a mock meal plan for demonstration"""
        meals = []
        meal_types = ["breakfast", "lunch", "dinner"]
        
        # Sample meal names - categorized by dietary type
        meal_options = {
            "breakfast": {
                "vegetarian": ["Oatmeal with berries", "Scrambled eggs with toast", "Greek yogurt parfait", "Avocado toast", "Pancakes with fruit"],
                "vegan": ["Oatmeal with berries", "Avocado toast", "Smoothie bowl", "Chia pudding", "Fruit salad"],
                "default": ["Oatmeal with berries", "Scrambled eggs with toast", "Greek yogurt parfait", "Avocado toast"]
            },
            "lunch": {
                "vegetarian": ["Caesar salad", "Vegetable stir-fry", "Quinoa bowl", "Caprese sandwich", "Lentil soup"],
                "vegan": ["Caesar salad (vegan)", "Vegetable stir-fry", "Quinoa bowl", "Hummus wrap", "Lentil soup"],
                "default": ["Caesar salad", "Chicken wrap", "Vegetable stir-fry", "Quinoa bowl"]
            },
            "dinner": {
                "vegetarian": ["Pasta with marinara", "Tofu curry", "Mushroom risotto", "Vegetable lasagna", "Stuffed peppers"],
                "vegan": ["Pasta with marinara", "Tofu curry", "Lentil curry", "Vegetable stir-fry", "Chickpea curry"],
                "default": ["Pasta with marinara", "Grilled chicken with vegetables", "Tofu curry", "Salmon with rice"]
            }
        }
        
        # Select appropriate meal options based on dietary restrictions
        selected_meals = {}
        for meal_type in ["breakfast", "lunch", "dinner"]:
            if dietary_restrictions:
                if "vegan" in dietary_restrictions:
                    selected_meals[meal_type] = meal_options[meal_type].get("vegan", meal_options[meal_type]["default"])
                elif "vegetarian" in dietary_restrictions:
                    selected_meals[meal_type] = meal_options[meal_type].get("vegetarian", meal_options[meal_type]["default"])
                else:
                    selected_meals[meal_type] = meal_options[meal_type]["default"]
            else:
                selected_meals[meal_type] = meal_options[meal_type]["default"]
        
        for day in range(1, days + 1):
            for meal_type in meal_types:
                import random
                meal_name = random.choice(selected_meals[meal_type])
                meals.append({
                    "day": day,
                    "meal_type": meal_type,
                    "name": meal_name,
                    "description": f"A delicious {meal_name.lower()} for {meal_type}"
                })
        
        return {
            "meals": meals,
            "summary": f"Generated {days}-day meal plan with {len(meals)} meals",
            "days": days,
            "dietary_restrictions": dietary_restrictions or [],
            "preferences": preferences or []
        }


