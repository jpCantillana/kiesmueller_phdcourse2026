import sys
from pathlib import Path

# Get the project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.item_approach import ItemApproach
from utils.data_loader import SparePart
from typing import List, Tuple, Dict
import copy

class GreedyOptimizer:
    """Greedy algorithm for budget-constrained optimization."""
    
    @staticmethod
    def calculate_improvement(parts: List[SparePart], stock_levels: Dict) -> float:
        """Calculate total improvement in fill rate for current stock levels."""
        improvement_dict = {k: 0 for k in list(stock_levels.keys())}
        base_value = ItemApproach.aggregated_service_level(parts, stock_levels)
        for part in parts:
            temporary_stock_levels = copy.deepcopy(stock_levels)
            temporary_stock_levels[part.part_id] += 1
            new_value = ItemApproach.aggregated_service_level(parts, temporary_stock_levels)
            improvement_dict[part.part_id] = (new_value - base_value)/part.unit_cost
        return improvement_dict

    @staticmethod
    def find(parts: List[SparePart], fulfillment_target: float) -> List[Tuple[SparePart, int]]:
        """Find optimal stock levels for parts within budget."""
        # Initial stock levels and costs
        stock_levels = {part.part_id: 0 for part in parts}
        
        while True:
            best_increase = None
            best_part = None
            
            improvement_dict = GreedyOptimizer.calculate_improvement(parts, stock_levels)
            for part in parts:
                if best_increase is None or improvement_dict[part.part_id] > best_increase:
                    best_increase = improvement_dict[part.part_id]
                    best_part = part
            stock_levels[best_part.part_id] += 1
            current_fill_rate = ItemApproach.aggregated_service_level(parts, stock_levels)
            
            if current_fill_rate >= fulfillment_target:
                return [(part, stock_levels[part.part_id]) for part in parts]
        