from typing import List, Dict, Any

class OptimizationEngine:
    def optimize_basket(self, current_basket: List[Dict], max_budget: float, available_alternatives: Dict[str, List[Dict]]) -> Dict:
        """
        current_basket: List of selected items.
        max_budget: The hard constraint budget.
        available_alternatives: Map of category/item -> list of alternatives with prices and scores.
        
        Returns the optimized basket and savings.
        """
        # Knapsack logic for optimization
        # For this prototype, we'll implement a greedy fallback approach 
        # to swap the lowest value-for-money items with cheaper acceptable alternatives 
        # until the budget is met.
        
        current_total = sum(item.get("price", 0) * item.get("quantity", 1) for item in current_basket)
        if current_total <= max_budget:
            return {
                "optimized_basket": current_basket,
                "current_total": current_total,
                "optimized_total": current_total,
                "savings": 0,
                "changed_products": []
            }
            
        optimized_basket = []
        changed = []
        running_total = 0
        
        # Sort current basket by price descending (try to optimize most expensive first)
        sorted_basket = sorted(current_basket, key=lambda x: x.get("price", 0), reverse=True)
        
        for item in sorted_basket:
            item_cat = item.get("category")
            alts = available_alternatives.get(item_cat, [])
            
            # Find a cheaper alternative that brings us closer to budget
            swapped = False
            for alt in sorted(alts, key=lambda x: x.get("price", 0)):
                if alt.get("price", 0) < item.get("price", 0):
                    # We swap
                    optimized_basket.append(alt)
                    changed.append({
                        "from": item.get("name"),
                        "to": alt.get("name"),
                        "saved": item.get("price", 0) - alt.get("price", 0)
                    })
                    running_total += alt.get("price", 0) * item.get("quantity", 1)
                    swapped = True
                    break
                    
            if not swapped:
                optimized_basket.append(item)
                running_total += item.get("price", 0) * item.get("quantity", 1)
                
        return {
            "optimized_basket": optimized_basket,
            "current_total": current_total,
            "optimized_total": running_total,
            "savings": current_total - running_total,
            "changed_products": changed
        }

optimization_engine = OptimizationEngine()
