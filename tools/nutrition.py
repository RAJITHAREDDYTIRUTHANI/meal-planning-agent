"""
Nutrition Analysis Tool - Custom tool for analyzing nutritional content
"""

from typing import Dict, List, Any, Optional
from observability.logger import get_logger
from observability.tracer import get_tracer

logger = get_logger("nutrition")
tracer = get_tracer()


class NutritionAnalysisTool:
    """
    Custom tool for analyzing nutritional content of meals and recipes.
    Provides nutritional summaries and recommendations.
    """
    
    def __init__(self):
        """Initialize the nutrition analysis tool"""
        pass
    
    def analyze_meal_nutrition(self, meals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze nutritional content of a list of meals.
        
        Args:
            meals: List of meal dictionaries with recipe information
            
        Returns:
            Dictionary with nutritional analysis
        """
        span = tracer.start_span("analyze_meal_nutrition", meal_count=len(meals))
        
        try:
            # Calculate total nutrition (mock implementation)
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            for meal in meals:
                # In a real implementation, this would fetch actual nutrition data
                # For now, we estimate based on meal type
                nutrition = self._estimate_nutrition(meal)
                total_calories += nutrition["calories"]
                total_protein += nutrition["protein"]
                total_carbs += nutrition["carbs"]
                total_fat += nutrition["fat"]
            
            analysis = {
                "total_calories": round(total_calories, 2),
                "total_protein_g": round(total_protein, 2),
                "total_carbs_g": round(total_carbs, 2),
                "total_fat_g": round(total_fat, 2),
                "meals_analyzed": len(meals),
                "recommendations": self._generate_recommendations(total_calories, total_protein, total_carbs, total_fat)
            }
            
            tracer.add_event(span, "analysis_complete", calories=total_calories)
            tracer.end_span(span, success=True)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing nutrition: {e}")
            tracer.add_event(span, "error", error=str(e))
            tracer.end_span(span, success=False)
            return {"error": str(e)}
    
    def _estimate_nutrition(self, meal: Dict[str, Any]) -> Dict[str, float]:
        """
        Estimate nutrition for a meal (mock implementation).
        In production, this would use actual nutrition databases.
        """
        # Simple estimation based on meal title/type
        title = meal.get("title", "").lower()
        
        # Default values
        calories = 500
        protein = 25
        carbs = 50
        fat = 20
        
        # Adjust based on meal type
        if "salad" in title or "bowl" in title:
            calories = 400
            protein = 20
            carbs = 40
            fat = 15
        elif "pasta" in title or "noodle" in title:
            calories = 600
            protein = 20
            carbs = 80
            fat = 15
        elif "chicken" in title or "meat" in title:
            calories = 550
            protein = 40
            carbs = 30
            fat = 25
        elif "soup" in title:
            calories = 300
            protein = 15
            carbs = 35
            fat = 10
        
        return {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        }
    
    def _generate_recommendations(
        self,
        calories: float,
        protein: float,
        carbs: float,
        fat: float
    ) -> List[str]:
        """Generate nutritional recommendations"""
        recommendations = []
        
        # Daily targets (can be customized per user)
        target_calories = 2000
        target_protein = 100
        target_carbs = 250
        target_fat = 65
        
        if calories < target_calories * 0.8:
            recommendations.append("Consider adding more calorie-dense foods to meet daily needs")
        elif calories > target_calories * 1.2:
            recommendations.append("Meal plan is high in calories - consider lighter options")
        
        if protein < target_protein * 0.7:
            recommendations.append("Add more protein sources like lean meats, beans, or tofu")
        
        if carbs < target_carbs * 0.7:
            recommendations.append("Include more whole grains and vegetables for balanced carbs")
        
        if fat > target_fat * 1.3:
            recommendations.append("Consider reducing high-fat foods for better balance")
        
        if not recommendations:
            recommendations.append("Nutritional balance looks good!")
        
        return recommendations
    
    def compare_nutrition(self, meal_plan_1: Dict[str, Any], meal_plan_2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare nutritional content of two meal plans.
        
        Args:
            meal_plan_1: First meal plan
            meal_plan_2: Second meal plan
            
        Returns:
            Comparison analysis
        """
        span = tracer.start_span("compare_nutrition")
        
        try:
            nutrition_1 = self.analyze_meal_nutrition(meal_plan_1.get("meals", []))
            nutrition_2 = self.analyze_meal_nutrition(meal_plan_2.get("meals", []))
            
            comparison = {
                "plan_1": nutrition_1,
                "plan_2": nutrition_2,
                "differences": {
                    "calories_diff": nutrition_1["total_calories"] - nutrition_2["total_calories"],
                    "protein_diff": nutrition_1["total_protein_g"] - nutrition_2["total_protein_g"],
                    "carbs_diff": nutrition_1["total_carbs_g"] - nutrition_2["total_carbs_g"],
                    "fat_diff": nutrition_1["total_fat_g"] - nutrition_2["total_fat_g"],
                }
            }
            
            tracer.end_span(span, success=True)
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing nutrition: {e}")
            tracer.end_span(span, success=False)
            return {"error": str(e)}

