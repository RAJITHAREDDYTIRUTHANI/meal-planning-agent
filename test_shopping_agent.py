"""
Test script for the Shopping List Agent
"""

from agents.shopping_list import ShoppingListAgent
from tools.shopping_optimizer import ShoppingOptimizerTool

def test_shopping_agent():
    """Test the shopping list agent"""
    print("="*60)
    print("Testing Shopping List Agent")
    print("="*60 + "\n")
    
    # Initialize the agent
    agent = ShoppingListAgent()
    print("[OK] Shopping List Agent initialized\n")
    
    # Sample meal recipes (mock data)
    meal_recipes = {
        "Pasta with Marinara": {
            "id": 1,
            "title": "Pasta with Marinara",
            "summary": "Classic Italian pasta dish with tomato sauce"
        },
        "Caesar Salad": {
            "id": 2,
            "title": "Caesar Salad",
            "summary": "Fresh romaine lettuce with caesar dressing"
        },
        "Grilled Chicken": {
            "id": 3,
            "title": "Grilled Chicken",
            "summary": "Tender grilled chicken breast with herbs"
        }
    }
    
    print("Sample meal recipes:")
    for meal, recipe in meal_recipes.items():
        print(f"  - {meal}: {recipe['summary']}")
    print()
    
    # Generate shopping list
    print("Generating shopping list...")
    result = agent.generate_shopping_list(
        meal_recipes=meal_recipes,
        optimize=True
    )
    
    print("\n" + "="*60)
    print("SHOPPING LIST RESULTS")
    print("="*60 + "\n")
    
    shopping_list = result.get("shopping_list", {})
    
    print(f"Total items: {shopping_list.get('total_items', 0)}")
    print(f"Optimized: {result.get('optimized', False)}")
    
    # Show grouped items
    if shopping_list.get("grouped_by_section"):
        print("\nItems grouped by store section:")
        for section, items in shopping_list["grouped_by_section"].items():
            print(f"\n  [{section.upper()}]:")
            for item in items:
                print(f"     • {item}")
    
    # Show cost estimate
    if shopping_list.get("estimated_cost"):
        cost = shopping_list["estimated_cost"]
        print(f"\n[COST ESTIMATE]:")
        print(f"   Total: ${cost.get('total_estimate', 0):.2f} {cost.get('currency', 'USD')}")
        print(f"   Note: {cost.get('note', '')}")
        
        if cost.get("item_costs"):
            print(f"\n   Item costs:")
            for item, price in list(cost["item_costs"].items())[:5]:  # Show first 5
                print(f"     • {item}: ${price:.2f}")
            if len(cost["item_costs"]) > 5:
                print(f"     ... and {len(cost['item_costs']) - 5} more items")
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)


def test_shopping_optimizer_tool():
    """Test the shopping optimizer tool directly"""
    print("\n" + "="*60)
    print("Testing Shopping Optimizer Tool")
    print("="*60 + "\n")
    
    tool = ShoppingOptimizerTool()
    
    # Sample ingredients
    ingredients = [
        "chicken breast",
        "lettuce",
        "tomato",
        "onion",
        "garlic",
        "pasta",
        "olive oil",
        "salt",
        "pepper",
        "cheese",
        "milk",
        "bread",
        "chicken breast",  # Duplicate to test deduplication
        "Fresh tomato"  # Test normalization
    ]
    
    print(f"Input ingredients ({len(ingredients)} items):")
    for ing in ingredients:
        print(f"  - {ing}")
    print()
    
    # Optimize
    result = tool.optimize_shopping_list(
        ingredients=ingredients,
        group_by_section=True,
        estimate_costs=True
    )
    
    print(f"[OK] Optimized to {result['total_items']} unique items")
    print(f"[OK] Grouped into {len(result.get('grouped_by_section', {}))} sections")
    print(f"[OK] Estimated cost: ${result.get('estimated_cost', {}).get('total_estimate', 0):.2f}")
    
    print("\nGrouped items:")
    for section, items in result.get("grouped_by_section", {}).items():
        print(f"\n  {section.upper()}:")
        for item in items:
            print(f"    • {item}")


if __name__ == "__main__":
    try:
        test_shopping_agent()
        test_shopping_optimizer_tool()
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback
        traceback.print_exc()

