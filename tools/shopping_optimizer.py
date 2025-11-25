"""
Shopping List Optimizer Tool - Custom tool for optimizing shopping lists
"""

from typing import List, Dict, Any, Set
from collections import defaultdict
from observability.logger import get_logger
from observability.tracer import get_tracer

logger = get_logger("shopping_optimizer")
tracer = get_tracer()


class ShoppingOptimizerTool:
    """
    Custom tool for optimizing shopping lists by grouping items,
    estimating costs, and organizing by store sections.
    """
    
    def __init__(self):
        """Initialize the shopping optimizer tool"""
        # Store section mappings
        self.store_sections = {
            "produce": ["lettuce", "tomato", "onion", "garlic", "pepper", "carrot", "celery", "potato", "apple", "banana", "orange"],
            "dairy": ["milk", "cheese", "yogurt", "butter", "cream", "eggs"],
            "meat": ["chicken", "beef", "pork", "fish", "turkey", "bacon", "sausage"],
            "pantry": ["flour", "sugar", "salt", "pepper", "oil", "vinegar", "rice", "pasta", "beans", "canned"],
            "frozen": ["frozen", "ice cream"],
            "bakery": ["bread", "bagel", "roll", "croissant"],
            "beverages": ["juice", "soda", "water", "coffee", "tea"],
        }
    
    def optimize_shopping_list(
        self,
        ingredients: List[str],
        group_by_section: bool = True,
        estimate_costs: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize a shopping list by grouping and organizing items.
        
        Args:
            ingredients: List of ingredient names
            group_by_section: Whether to group items by store section
            estimate_costs: Whether to estimate costs
            
        Returns:
            Optimized shopping list dictionary
        """
        span = tracer.start_span("optimize_shopping_list", ingredient_count=len(ingredients))
        
        try:
            # Deduplicate and normalize ingredients
            normalized = self._normalize_ingredients(ingredients)
            
            # Group by section if requested
            if group_by_section:
                grouped = self._group_by_section(normalized)
            else:
                grouped = {"all": normalized}
            
            # Estimate costs if requested
            cost_estimate = None
            if estimate_costs:
                cost_estimate = self._estimate_costs(normalized)
            
            result = {
                "items": normalized,
                "grouped_by_section": grouped if group_by_section else None,
                "total_items": len(normalized),
                "estimated_cost": cost_estimate,
                "sections": list(grouped.keys()) if group_by_section else None
            }
            
            tracer.add_event(span, "optimization_complete", items=len(normalized))
            tracer.end_span(span, success=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing shopping list: {e}")
            tracer.add_event(span, "error", error=str(e))
            tracer.end_span(span, success=False)
            return {"error": str(e), "items": ingredients}
    
    def _normalize_ingredients(self, ingredients: List[str]) -> List[str]:
        """
        Normalize and deduplicate ingredients.
        
        Args:
            ingredients: Raw ingredient list
            
        Returns:
            Normalized, deduplicated list
        """
        normalized = []
        seen = set()
        
        for ingredient in ingredients:
            # Normalize: lowercase, strip whitespace
            normalized_ing = ingredient.lower().strip()
            
            # Remove common prefixes/suffixes
            normalized_ing = normalized_ing.replace("fresh ", "").replace("dried ", "")
            
            # Check for duplicates
            if normalized_ing and normalized_ing not in seen:
                normalized.append(ingredient.strip())  # Keep original capitalization
                seen.add(normalized_ing)
        
        return normalized
    
    def _group_by_section(self, ingredients: List[str]) -> Dict[str, List[str]]:
        """
        Group ingredients by store section.
        
        Args:
            ingredients: List of ingredients
            
        Returns:
            Dictionary mapping section names to ingredient lists
        """
        grouped = defaultdict(list)
        unassigned = []
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            assigned = False
            
            # Check each section
            for section, keywords in self.store_sections.items():
                if any(keyword in ingredient_lower for keyword in keywords):
                    grouped[section].append(ingredient)
                    assigned = True
                    break
            
            if not assigned:
                unassigned.append(ingredient)
        
        # Add unassigned items to "other" section
        if unassigned:
            grouped["other"] = unassigned
        
        return dict(grouped)
    
    def _estimate_costs(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        Estimate costs for ingredients (mock implementation).
        In production, this would use actual price databases or APIs.
        
        Args:
            ingredients: List of ingredients
            
        Returns:
            Cost estimate dictionary
        """
        # Simple cost estimation based on ingredient type
        total = 0.0
        item_costs = {}
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            # Estimate based on ingredient category
            if any(word in ingredient_lower for word in ["chicken", "beef", "pork", "fish"]):
                cost = 8.0
            elif any(word in ingredient_lower for word in ["cheese", "milk", "yogurt"]):
                cost = 4.0
            elif any(word in ingredient_lower for word in ["lettuce", "tomato", "onion", "pepper"]):
                cost = 2.0
            elif any(word in ingredient_lower for word in ["pasta", "rice", "flour"]):
                cost = 3.0
            elif any(word in ingredient_lower for word in ["bread", "bagel"]):
                cost = 3.5
            else:
                cost = 3.0  # Default estimate
            
            item_costs[ingredient] = round(cost, 2)
            total += cost
        
        return {
            "total_estimate": round(total, 2),
            "item_costs": item_costs,
            "currency": "USD",
            "note": "Estimates are approximate and may vary by location"
        }
    
    def merge_shopping_lists(self, list1: List[str], list2: List[str]) -> List[str]:
        """
        Merge two shopping lists, deduplicating items.
        
        Args:
            list1: First shopping list
            list2: Second shopping list
            
        Returns:
            Merged, deduplicated list
        """
        span = tracer.start_span("merge_shopping_lists")
        
        try:
            combined = list1 + list2
            merged = self._normalize_ingredients(combined)
            
            tracer.end_span(span, success=True, merged_count=len(merged))
            return merged
            
        except Exception as e:
            logger.error(f"Error merging shopping lists: {e}")
            tracer.end_span(span, success=False)
            return list1 + list2

