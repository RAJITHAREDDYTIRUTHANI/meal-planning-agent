"""
Online Ordering Service - Integration with grocery delivery services
"""

from typing import Dict, List, Optional, Any
from observability.logger import get_logger

logger = get_logger("ordering_service")


class OrderingService:
    """Service for online grocery ordering and checkout assistance"""
    
    def __init__(self):
        """Initialize ordering service"""
        self.supported_services = [
            "Instacart",
            "Amazon Fresh",
            "Walmart Grocery",
            "Kroger",
            "Target",
            "Whole Foods"
        ]
    
    def generate_order_links(
        self,
        shopping_list: Dict[str, Any],
        preferred_service: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate order links for different grocery services.
        
        Args:
            shopping_list: Shopping list data
            preferred_service: Preferred grocery service
            
        Returns:
            Dictionary with order links and instructions
        """
        items = []
        if shopping_list.get("grouped_by_section"):
            for section_items in shopping_list["grouped_by_section"].values():
                items.extend(section_items)
        
        # Generate search queries for each item
        order_data = {
            "items": items,
            "total_items": len(items),
            "services": {}
        }
        
        # Generate links for each service
        for service in self.supported_services:
            order_data["services"][service] = {
                "name": service,
                "search_url": self._generate_search_url(service, items[:5]),  # First 5 items
                "cart_url": f"https://www.{service.lower().replace(' ', '')}.com/cart",
                "available": True
            }
        
        if preferred_service:
            order_data["recommended_service"] = preferred_service
        
        return order_data
    
    def _generate_search_url(self, service: str, items: List[str]) -> str:
        """Generate search URL for a service"""
        base_urls = {
            "Instacart": "https://www.instacart.com/store/search",
            "Amazon Fresh": "https://www.amazon.com/s?k",
            "Walmart Grocery": "https://www.walmart.com/search",
            "Kroger": "https://www.kroger.com/search",
            "Target": "https://www.target.com/s",
            "Whole Foods": "https://www.amazon.com/wholefoods/search"
        }
        
        base = base_urls.get(service, "https://www.google.com/search")
        query = "+".join(items[:3])  # First 3 items
        return f"{base}?q={query}"
    
    def get_checkout_tips(
        self,
        shopping_list: Dict[str, Any],
        budget: Optional[float] = None
    ) -> List[str]:
        """
        Get checkout assistance tips.
        
        Args:
            shopping_list: Shopping list data
            budget: Budget constraint
            
        Returns:
            List of checkout tips
        """
        tips = []
        
        total_cost = shopping_list.get("estimated_cost", {}).get("total_estimate", 0)
        total_items = shopping_list.get("total_items", 0)
        
        if budget and total_cost > budget:
            tips.append(f"⚠️ Your estimated cost (${total_cost:.2f}) exceeds your budget (${budget:.2f})")
            tips.append("💡 Consider removing non-essential items or looking for store-brand alternatives")
        elif budget:
            remaining = budget - total_cost
            tips.append(f"✅ You're within budget! ${remaining:.2f} remaining")
        
        if total_items > 20:
            tips.append("💡 You have many items. Consider splitting into multiple trips or using online ordering")
        
        tips.append("💳 Have your payment method ready")
        tips.append("📱 Check for digital coupons before checkout")
        tips.append("🔄 Review your list to avoid impulse purchases")
        
        return tips

