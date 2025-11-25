"""
Example usage of the Meal Planning & Shopping Assistant Agent
"""

import os
from dotenv import load_dotenv
from observability.logger import setup_logger
from observability.tracer import setup_tracer
from agents.orchestrator import OrchestratorAgent

# Load environment variables
load_dotenv()

# Set up observability
setup_logger()
setup_tracer()


def example_basic_meal_planning():
    """Example: Basic meal planning"""
    print("\n=== Example 1: Basic Meal Planning ===\n")
    
    orchestrator = OrchestratorAgent()
    
    # Create session
    session_id = orchestrator.create_session(
        user_id="user1",
        initial_preferences={"dietary_restriction": "vegetarian"}
    )
    
    # Plan meals
    result = orchestrator.plan_meals(
        session_id=session_id,
        days=5,
        dietary_restrictions=["vegetarian"],
        preferences=["Italian"],
        budget=100.0
    )
    
    print(f"Planned {len(result['meal_plan']['meals'])} meals")
    print(f"Found {result['recipes']['recipes_found']} recipes")
    print(f"Generated shopping list with {result['shopping_list']['total_items']} items")


def example_with_memory():
    """Example: Using memory to remember preferences"""
    print("\n=== Example 2: Using Memory ===\n")
    
    orchestrator = OrchestratorAgent()
    
    # First session - set preferences
    session_id1 = orchestrator.create_session(user_id="user2")
    orchestrator.update_preferences(session_id1, {
        "favorite_cuisines": ["Mexican", "Thai"],
        "budget": 80.0
    })
    
    # Plan meals (agent remembers preferences)
    result1 = orchestrator.plan_meals(
        session_id=session_id1,
        days=3,
        preferences=["Mexican", "Thai"]
    )
    
    print(f"First plan: {len(result1['meal_plan']['meals'])} meals")
    
    # Second session - preferences are remembered
    session_id2 = orchestrator.create_session(user_id="user2")
    result2 = orchestrator.plan_meals(
        session_id=session_id2,
        days=3
    )
    
    print(f"Second plan (with memory): {len(result2['meal_plan']['meals'])} meals")


def example_nutrition_focused():
    """Example: Nutrition-focused meal planning"""
    print("\n=== Example 3: Nutrition-Focused Planning ===\n")
    
    orchestrator = OrchestratorAgent()
    
    session_id = orchestrator.create_session(user_id="user3")
    
    result = orchestrator.plan_meals(
        session_id=session_id,
        days=7,
        dietary_restrictions=["gluten-free"],
        include_nutrition=True,
        include_shopping_list=True
    )
    
    nutrition = result.get("nutrition")
    if nutrition:
        print(f"Total calories: {nutrition['total_calories']:.1f}")
        print(f"Protein: {nutrition['total_protein_g']:.1f}g")
        print("\nRecommendations:")
        for rec in nutrition.get("recommendations", []):
            print(f"  - {rec}")


def example_budget_conscious():
    """Example: Budget-conscious meal planning"""
    print("\n=== Example 4: Budget-Conscious Planning ===\n")
    
    orchestrator = OrchestratorAgent()
    
    session_id = orchestrator.create_session(user_id="user4")
    
    result = orchestrator.plan_meals(
        session_id=session_id,
        days=5,
        budget=50.0,  # Tight budget
        include_shopping_list=True
    )
    
    shopping_list = result.get("shopping_list", {})
    if shopping_list.get("estimated_cost"):
        cost = shopping_list["estimated_cost"]["total_estimate"]
        print(f"Estimated cost: ${cost:.2f}")
        print(f"Budget: $50.00")
        print(f"Remaining: ${50.0 - cost:.2f}")


if __name__ == "__main__":
    print("="*60)
    print("Meal Planning & Shopping Assistant - Examples")
    print("="*60)
    
    try:
        example_basic_meal_planning()
        example_with_memory()
        example_nutrition_focused()
        example_budget_conscious()
        
        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


