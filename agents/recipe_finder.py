"""
Recipe Finder Agent - LLM-powered agent for finding recipes
"""

import os
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from tools.recipe_search import RecipeSearchTool
from observability.logger import get_logger
from observability.tracer import get_tracer, trace_operation

logger = get_logger("recipe_finder")
tracer = get_tracer()


class RecipeFinderAgent:
    """
    LLM-powered agent that finds and retrieves recipes based on meal plans.
    Uses custom RecipeSearchTool to search for recipes.
    """
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the recipe finder agent.
        
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
        self.recipe_tool = RecipeSearchTool()
    
    @trace_operation("find_recipes")
    def find_recipes_for_meals(
        self,
        meals: List[Dict[str, Any]],
        dietary_restrictions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Find recipes for a list of meals.
        Uses parallel processing for faster execution.
        
        Args:
            meals: List of meal dictionaries from meal plan
            dietary_restrictions: List of dietary restrictions
            
        Returns:
            Dictionary mapping meals to recipes
        """
        span = tracer.start_span("recipe_finder_find", meal_count=len(meals))
        
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import time
            
            meal_recipes = {}
            
            def process_meal(meal):
                """Process a single meal to find recipe"""
                meal_name = meal.get("name", "")
                meal_type = meal.get("meal_type", "")
                
                try:
                    # Fast path: Skip LLM calls entirely for speed, use meal name directly
                    # Uncomment below if you want LLM query generation (slower):
                    # if self.model:
                    #     try:
                    #         search_query = self._generate_search_query(meal_name, meal_type)
                    #     except Exception:
                    #         search_query = meal_name
                    # else:
                    #     search_query = meal_name
                    search_query = meal_name  # Fast path: use meal name directly
                    
                    # Search for recipes using the tool
                    recipes = self.recipe_tool.search_recipes(
                        query=search_query,
                        dietary_restrictions=dietary_restrictions,
                        max_results=3
                    )
                    
                    if recipes:
                        # Fast path: Use first recipe directly (skip LLM selection for speed)
                        # Uncomment below if you want LLM recipe selection (slower):
                        # try:
                        #     best_recipe = self._select_best_recipe(meal, recipes)
                        # except Exception:
                        #     best_recipe = recipes[0] if recipes else None
                        best_recipe = recipes[0]  # Fast path: use first recipe
                        return meal_name, best_recipe
                    else:
                        return meal_name, None
                        
                except Exception as e:
                    logger.warning(f"Error processing meal {meal_name}: {e}")
                    return meal_name, None
            
            # Use parallel processing for faster execution
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_meal = {executor.submit(process_meal, meal): meal for meal in meals}
                
                for future in as_completed(future_to_meal):
                    try:
                        meal_name, recipe = future.result(timeout=5)  # 5 second timeout per meal
                        meal_recipes[meal_name] = recipe
                        tracer.add_event(span, "recipe_found", meal=meal_name)
                    except Exception as e:
                        meal = future_to_meal[future]
                        meal_name = meal.get("name", "")
                        logger.warning(f"Timeout or error for meal {meal_name}: {e}")
                        meal_recipes[meal_name] = None
            
            elapsed = time.time() - start_time
            logger.info(f"Processed {len(meals)} meals in {elapsed:.2f} seconds (parallel)")
            
            result = {
                "meal_recipes": meal_recipes,
                "total_meals": len(meals),
                "recipes_found": len([r for r in meal_recipes.values() if r is not None])
            }
            
            tracer.end_span(span, success=True, recipes_found=result["recipes_found"])
            return result
            
        except Exception as e:
            logger.error(f"Error finding recipes: {e}")
            tracer.add_event(span, "error", error=str(e))
            tracer.end_span(span, success=False)
            # Return empty recipes on error
            return {"error": str(e), "meal_recipes": {meal.get("name", ""): None for meal in meals}}
    
    def _generate_search_query(self, meal_name: str, meal_type: str) -> str:
        """
        Generate a search query for recipe search.
        Uses LLM to create an optimized search query with fast timeout.
        """
        if self.model:
            prompt = f"Generate a concise recipe search query (2-4 words) for: {meal_name} ({meal_type}). Return only the query, no explanation."
            try:
                # Use threading timeout for fast failure
                from threading import Thread
                import queue
                result_queue = queue.Queue()
                
                def call_llm():
                    try:
                        response = self.model.generate_content(prompt)
                        result_queue.put(response.text.strip())
                    except Exception as e:
                        result_queue.put(None)
                
                thread = Thread(target=call_llm, daemon=True)
                thread.start()
                thread.join(timeout=2)  # 2 second timeout
                
                if thread.is_alive():
                    # Timeout occurred
                    return meal_name
                
                result = result_queue.get_nowait() if not result_queue.empty() else None
                if result:
                    return result
            except Exception as e:
                logger.debug(f"LLM query generation failed, using meal name: {e}")
        
        # Fast fallback: use meal name directly
        return meal_name
    
    def _select_best_recipe(
        self,
        meal: Dict[str, Any],
        recipes: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Select the best recipe from a list of candidates.
        Uses LLM to evaluate and select the most appropriate recipe with fast timeout.
        """
        if not recipes:
            return None
        
        # Fast path: if only one recipe, return it immediately
        if len(recipes) == 1:
            return recipes[0]
        
        if self.model:
            # Build prompt to select best recipe
            recipes_text = "\n".join([
                f"{i+1}. {r.get('title', '')} - {r.get('summary', '')[:100]}"
                for i, r in enumerate(recipes)
            ])
            
            prompt = f"""
            Given this meal requirement: {meal.get('name', '')} ({meal.get('meal_type', '')})
            
            Select the best matching recipe from these options:
            {recipes_text}
            
            Return only the number (1-{len(recipes)}) of the best match.
            """
            
            try:
                # Use threading timeout for fast failure
                from threading import Thread
                import queue
                result_queue = queue.Queue()
                
                def call_llm():
                    try:
                        response = self.model.generate_content(prompt)
                        text = response.text.strip().split()[0]
                        selection = int(text)
                        result_queue.put(selection)
                    except Exception as e:
                        result_queue.put(None)
                
                thread = Thread(target=call_llm, daemon=True)
                thread.start()
                thread.join(timeout=2)  # 2 second timeout
                
                if thread.is_alive():
                    # Timeout occurred
                    return recipes[0]
                
                selection = result_queue.get_nowait() if not result_queue.empty() else None
                if selection and 1 <= selection <= len(recipes):
                    return recipes[selection - 1]
            except Exception as e:
                logger.debug(f"LLM recipe selection failed, using first recipe: {e}")
        
        # Fast fallback: return first recipe
        return recipes[0]
    
    def get_recipe_ingredients(self, recipe: Dict[str, Any]) -> List[str]:
        """
        Extract ingredients from a recipe.
        
        Args:
            recipe: Recipe dictionary
            
        Returns:
            List of ingredient names
        """
        recipe_id = recipe.get("id")
        if recipe_id:
            details = self.recipe_tool.get_recipe_details(recipe_id)
            if details and "ingredients" in details:
                return details["ingredients"]
        
        # Fallback: return empty list
        return []


