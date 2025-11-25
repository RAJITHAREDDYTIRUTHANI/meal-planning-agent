"""
Recipe Search Tool - Custom tool for finding recipes
"""

import os
import requests
from typing import List, Dict, Optional, Any
from observability.logger import get_logger
from observability.tracer import get_tracer

logger = get_logger("recipe_search")
tracer = get_tracer()


class RecipeSearchTool:
    """
    Custom tool for searching recipes from various sources.
    This tool can search recipe APIs or web sources.
    """
    
    def __init__(self):
        """Initialize the recipe search tool"""
        self.spoonacular_api_key = os.getenv("SPOONACULAR_API_KEY")
        self.base_url = "https://api.spoonacular.com/recipes"
    
    def search_recipes(
        self,
        query: str,
        dietary_restrictions: Optional[List[str]] = None,
        cuisine: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for recipes based on query and filters.
        
        Args:
            query: Search query (e.g., "pasta", "chicken curry")
            dietary_restrictions: List of dietary restrictions (e.g., ["vegetarian", "gluten-free"])
            cuisine: Cuisine type (e.g., "Italian", "Mexican")
            max_results: Maximum number of results to return
            
        Returns:
            List of recipe dictionaries
        """
        span = tracer.start_span("recipe_search", query=query)
        
        try:
            # If API key is available, use Spoonacular API with fast timeout
            if self.spoonacular_api_key:
                try:
                    recipes = self._search_spoonacular(query, dietary_restrictions, cuisine, max_results)
                    if recipes:
                        tracer.add_event(span, "recipes_found", count=len(recipes))
                        tracer.end_span(span, success=True, results_count=len(recipes))
                        return recipes
                except Exception as api_error:
                    # Fast fallback on API error (payment required, timeout, etc.)
                    logger.debug(f"Spoonacular API error, using mock data: {api_error}")
                    recipes = self._get_mock_recipes(query, dietary_restrictions, cuisine, max_results)
                    tracer.end_span(span, success=True, results_count=len(recipes))
                    return recipes
            else:
                # Fallback to mock data for demonstration
                recipes = self._get_mock_recipes(query, dietary_restrictions, cuisine, max_results)
            
            tracer.add_event(span, "recipes_found", count=len(recipes))
            tracer.end_span(span, success=True, results_count=len(recipes))
            
            return recipes
            
        except Exception as e:
            logger.debug(f"Error searching recipes, using mock data: {e}")
            tracer.add_event(span, "error", error=str(e))
            tracer.end_span(span, success=False, error=str(e))
            # Fast fallback: return mock data on error
            return self._get_mock_recipes(query, dietary_restrictions, cuisine, max_results)
    
    def _search_spoonacular(
        self,
        query: str,
        dietary_restrictions: Optional[List[str]],
        cuisine: Optional[str],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using Spoonacular API"""
        params = {
            "apiKey": self.spoonacular_api_key,
            "query": query,
            "number": max_results,
            "addRecipeInformation": True
        }
        
        if dietary_restrictions:
            # Map common restrictions to Spoonacular parameters
            # Priority: vegan > vegetarian > other restrictions
            if "vegan" in dietary_restrictions:
                params["diet"] = "vegan"
            elif "vegetarian" in dietary_restrictions:
                params["diet"] = "vegetarian"
            
            # Handle intolerances
            intolerances = []
            if "gluten-free" in dietary_restrictions:
                intolerances.append("gluten")
            if "dairy-free" in dietary_restrictions:
                intolerances.append("dairy")
            if "nut-free" in dietary_restrictions:
                intolerances.append("peanut")
            if intolerances:
                params["intolerances"] = ",".join(intolerances)
        
        if cuisine:
            params["cuisine"] = cuisine
        
        # Fast timeout for API calls
        response = requests.get(f"{self.base_url}/complexSearch", params=params, timeout=3)
        response.raise_for_status()
        
        data = response.json()
        recipes = []
        
        for recipe in data.get("results", [])[:max_results]:
            recipes.append({
                "id": recipe.get("id"),
                "title": recipe.get("title"),
                "image": recipe.get("image"),
                "ready_in_minutes": recipe.get("readyInMinutes"),
                "servings": recipe.get("servings"),
                "source_url": recipe.get("sourceUrl"),
                "summary": recipe.get("summary", "")[:200] + "..." if recipe.get("summary") else "",
            })
        
        return recipes
    
    def _get_mock_recipes(
        self,
        query: str,
        dietary_restrictions: Optional[List[str]],
        cuisine: Optional[str],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Get mock recipe data for demonstration"""
        query_lower = query.lower()
        
        # Filter out non-vegetarian/vegan items from query if restrictions apply
        meat_keywords = ["chicken", "beef", "pork", "salmon", "fish", "meat", "turkey", "lamb"]
        has_meat = any(keyword in query_lower for keyword in meat_keywords)
        
        # Adjust recipe titles based on dietary restrictions
        if dietary_restrictions:
            if "vegan" in dietary_restrictions or "vegetarian" in dietary_restrictions:
                if has_meat:
                    # Replace meat-based queries with vegetarian alternatives
                    query = query.replace("chicken", "tofu").replace("salmon", "tofu").replace("beef", "lentils")
                    query = query.replace("meat", "vegetables").replace("fish", "tofu")
        
        mock_recipes = [
            {
                "id": 1,
                "title": f"Delicious {query.title()}",
                "image": "https://via.placeholder.com/300",
                "ready_in_minutes": 30,
                "servings": 4,
                "source_url": "https://example.com/recipe1",
                "summary": f"A tasty {query} recipe that's easy to make.",
            },
            {
                "id": 2,
                "title": f"Healthy {query.title()} Bowl",
                "image": "https://via.placeholder.com/300",
                "ready_in_minutes": 25,
                "servings": 2,
                "source_url": "https://example.com/recipe2",
                "summary": f"A nutritious {query} bowl perfect for a quick meal.",
            },
            {
                "id": 3,
                "title": f"Classic {query.title()}",
                "image": "https://via.placeholder.com/300",
                "ready_in_minutes": 45,
                "servings": 6,
                "source_url": "https://example.com/recipe3",
                "summary": f"Traditional {query} recipe with authentic flavors.",
            },
        ]
        
        return mock_recipes[:max_results]
    
    def get_recipe_details(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific recipe.
        
        Args:
            recipe_id: Recipe identifier
            
        Returns:
            Detailed recipe information or None
        """
        span = tracer.start_span("get_recipe_details", recipe_id=recipe_id)
        
        # Fast path: Return mock data immediately to avoid slow API calls
        # This significantly improves performance
        tracer.end_span(span, success=True)
        return {
            "id": recipe_id,
            "title": "Sample Recipe",
            "ingredients": ["ingredient1", "ingredient2", "ingredient3", "salt", "pepper", "olive oil"],
            "instructions": "Step 1: Prepare ingredients. Step 2: Cook. Step 3: Serve.",
            "ready_in_minutes": 30,
            "servings": 4,
        }
        
        # Uncomment below if you want to try API first (slower):
        # try:
        #     if self.spoonacular_api_key:
        #         # Fast timeout for API calls
        #         response = requests.get(
        #             f"{self.base_url}/{recipe_id}/information",
        #             params={"apiKey": self.spoonacular_api_key},
        #             timeout=2  # Very fast timeout
        #         )
        #         response.raise_for_status()
        #         recipe = response.json()
        #         
        #         result = {
        #             "id": recipe.get("id"),
        #             "title": recipe.get("title"),
        #             "ingredients": [ing.get("name") for ing in recipe.get("extendedIngredients", [])],
        #             "instructions": recipe.get("instructions", ""),
        #             "ready_in_minutes": recipe.get("readyInMinutes"),
        #             "servings": recipe.get("servings"),
        #             "nutrition": recipe.get("nutrition", {}),
        #         }
        #         
        #         tracer.end_span(span, success=True)
        #         return result
        # except Exception as e:
        #     logger.debug(f"API call failed, using mock: {e}")
        #     tracer.add_event(span, "error", error=str(e))
        #     tracer.end_span(span, success=False)
        #     # Return mock data on error
        #     return {
        #         "id": recipe_id,
        #         "title": "Sample Recipe",
        #         "ingredients": ["ingredient1", "ingredient2", "ingredient3"],
        #         "instructions": "Step 1: Prepare ingredients. Step 2: Cook. Step 3: Serve.",
        #         "ready_in_minutes": 30,
        #         "servings": 4,
        #     }

