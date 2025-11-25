"""
Main entry point for the Meal Planning & Shopping Assistant Agent
"""

import os
import sys
from dotenv import load_dotenv
from observability.logger import setup_logger, get_logger
from observability.tracer import setup_tracer
from agents.orchestrator import OrchestratorAgent

# Load environment variables
load_dotenv()

# Set up observability
setup_logger(level=os.getenv("LOG_LEVEL", "INFO"))
setup_tracer()

logger = get_logger("main")


def main():
    """Main function to run the meal planning agent"""
    logger.info("Starting Meal Planning & Shopping Assistant Agent")
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning(
            "GEMINI_API_KEY not found in environment. "
            "The agent will use mock responses. "
            "Set GEMINI_API_KEY in .env file for full functionality."
        )
    
    # Initialize orchestrator agent
    orchestrator = OrchestratorAgent()
    
    # Example usage
    print("\n" + "="*60)
    print("Meal Planning & Shopping Assistant Agent")
    print("="*60 + "\n")
    
    # Create a session for a user
    user_id = "demo_user"
    session_id = orchestrator.create_session(
        user_id=user_id,
        initial_preferences={
            "dietary_restriction": "vegetarian",
            "cuisine_preferences": ["Italian", "Mexican"]
        }
    )
    
    print(f"Created session: {session_id}\n")
    
    # Plan meals for 3 days
    print("Planning meals for 3 days...")
    result = orchestrator.plan_meals(
        session_id=session_id,
        days=3,
        dietary_restrictions=["vegetarian"],
        preferences=["Italian", "Mexican"],
        budget=75.0,
        include_nutrition=True,
        include_shopping_list=True
    )
    
    # Display results
    print("\n" + "="*60)
    print("MEAL PLAN RESULTS")
    print("="*60 + "\n")
    
    meal_plan = result.get("meal_plan", {})
    print(f"Summary: {meal_plan.get('summary', 'N/A')}")
    print(f"Days: {meal_plan.get('days', 'N/A')}")
    print(f"Total meals: {len(meal_plan.get('meals', []))}\n")
    
    # Display meals
    print("Meals:")
    for meal in meal_plan.get("meals", [])[:6]:  # Show first 6 meals
        print(f"  Day {meal.get('day')} - {meal.get('meal_type').title()}: {meal.get('name')}")
    
    # Display shopping list
    shopping_list = result.get("shopping_list", {})
    if shopping_list:
        print("\n" + "="*60)
        print("SHOPPING LIST")
        print("="*60 + "\n")
        
        print(f"Total items: {shopping_list.get('total_items', 0)}")
        
        if shopping_list.get("grouped_by_section"):
            print("\nItems by section:")
            for section, items in shopping_list["grouped_by_section"].items():
                print(f"\n  {section.upper()}:")
                for item in items:
                    print(f"    - {item}")
        
        if shopping_list.get("estimated_cost"):
            cost = shopping_list["estimated_cost"]
            print(f"\nEstimated cost: ${cost.get('total_estimate', 0):.2f} {cost.get('currency', 'USD')}")
    
    # Display nutrition analysis
    nutrition = result.get("nutrition")
    if nutrition:
        print("\n" + "="*60)
        print("NUTRITION ANALYSIS")
        print("="*60 + "\n")
        
        print(f"Total calories: {nutrition.get('total_calories', 0):.1f}")
        print(f"Protein: {nutrition.get('total_protein_g', 0):.1f}g")
        print(f"Carbs: {nutrition.get('total_carbs_g', 0):.1f}g")
        print(f"Fat: {nutrition.get('total_fat_g', 0):.1f}g")
        
        if nutrition.get("recommendations"):
            print("\nRecommendations:")
            for rec in nutrition["recommendations"]:
                print(f"  - {rec}")
    
    print("\n" + "="*60)
    print("Done!")
    print("="*60 + "\n")
    
    # Display session info
    session_info = orchestrator.get_session_info(session_id)
    if session_info:
        print(f"Session info: User {session_info['user_id']}, "
              f"Created at {session_info['created_at']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        sys.exit(1)


