import sys
from pathlib import Path

# Get the project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.item_approach import ItemApproach
from utils.data_loader import SparePart
from typing import List, Tuple, Dict
from math import ceil
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
    def calculate_individual_availability(parts: List[SparePart], stock_levels: Dict, is_inverted: bool = False) -> float:
        """Calculate total availability for current stock levels."""
        improvement_dict = {k: 0 for k in list(stock_levels.keys())}
        for part in parts:
            base_value = ItemApproach.calculate_availability(part, stock_levels[part.part_id]) * 100000000
            new_value = ItemApproach.calculate_availability(part, stock_levels[part.part_id] + 1) * 100000000
            if not is_inverted:
                improvement_dict[part.part_id] = (base_value - new_value)/part.unit_cost
            else:
                improvement_dict[part.part_id] = (new_value - base_value)/part.unit_cost
        return improvement_dict

    @staticmethod
    def calculate_investment(parts, allocation):
        total_investment = 0
        for part in parts:
            total_investment += ItemApproach.calculate_total_cost(part, allocation[part.part_id])
        return total_investment

    @staticmethod
    def find(parts: List[SparePart], fulfillment_target: float) -> List[Tuple[SparePart, int]]:
        """Find optimal stock levels for parts within budget."""
        # Initial stock levels and costs
        stock_levels = {part.part_id: 0 for part in parts}
        
        while True:
            best_increase = None
            best_part = None
            
            improvement_dict = GreedyOptimizer.calculate_improvement(parts, stock_levels)
            print("\n Improvement dict:", improvement_dict)
            for part in parts:
                if best_increase is None or improvement_dict[part.part_id] > best_increase:
                    best_increase = improvement_dict[part.part_id]
                    best_part = part
            stock_levels[best_part.part_id] += 1
            current_fill_rate = ItemApproach.aggregated_service_level(parts, stock_levels)
            
            if current_fill_rate >= fulfillment_target:
                return [(part, stock_levels[part.part_id]) for part in parts]
    
    @staticmethod
    def find_availability(parts: List[SparePart], budget: float = 2000000) -> float:
        """Find optimal availability."""
        stock_levels = {part.part_id: 0 for part in parts}
        
        while True:
            best_increase = None
            best_part = None
            
            improvement_dict = GreedyOptimizer.calculate_individual_availability(parts, stock_levels)
            print("\n Improvement dict:", improvement_dict)
            for part in parts:
                if best_increase is None or improvement_dict[part.part_id] > best_increase:
                    best_increase = improvement_dict[part.part_id]
                    best_part = part
            stock_levels[best_part.part_id] += 1
            investment = GreedyOptimizer.calculate_investment(parts, stock_levels)
            if investment > budget:
                stock_levels[best_part.part_id] += -1
                return [(part, stock_levels[part.part_id]) for part in parts]
    
    @staticmethod
    def repair_availability_fixed(parts: List[SparePart], stock_levels: dict, budget: float = 2000000) -> dict:
        """Reduce stock levels to meet budget, avoiding zero stock when possible."""
        
        while True:
            current_investment = GreedyOptimizer.calculate_investment(parts, stock_levels)
            
            # Check if we're within budget
            if current_investment <= budget:
                return stock_levels
            
            # Phase 1: Try to reduce parts with stock > 1 (avoid zero)
            best_part = None
            best_ratio = float('inf')
            
            improvement_dict = GreedyOptimizer.calculate_individual_availability(
                parts, stock_levels, is_inverted=True
            )
            
            # First pass: only consider parts with stock > 1
            for part in parts:
                if stock_levels[part.part_id] > 1:
                    ratio = improvement_dict[part.part_id]
                    if ratio < best_ratio:
                        best_ratio = ratio
                        best_part = part
            
            # If found a part with stock > 1, reduce it
            if best_part is not None:
                stock_levels[best_part.part_id] -= 1
                continue
            
            # Phase 2: If no parts with stock > 1, consider parts with stock = 1
            best_part = None
            best_ratio = float('inf')
            
            for part in parts:
                if stock_levels[part.part_id] == 1:
                    ratio = improvement_dict[part.part_id]
                    if ratio < best_ratio:
                        best_ratio = ratio
                        best_part = part
            
            # If found a part with stock = 1, reduce it (to 0)
            if best_part is not None:
                stock_levels[best_part.part_id] -= 1
                continue
            
            # If we reach here, all stocks are at 0
            # This means initial allocation was wrong or budget is too small
            return stock_levels
    
    @staticmethod
    def find_availability_fixed(parts: List[SparePart], budget: float = 2000000) -> float:
        """Find optimal availability."""
        stock_levels = {part.part_id: max(0, ceil(part.mean_demand*part.repair_time - 2)) for part in parts}
        
        if GreedyOptimizer.calculate_investment(parts, stock_levels) > budget:
            # Initial stock levels exceed budget!
            stock_levels = GreedyOptimizer.repair_availability_fixed(parts, stock_levels, budget)
        
        while True:
            best_increase = None
            best_part = None
            
            improvement_dict = GreedyOptimizer.calculate_individual_availability(parts, stock_levels)
            print("\n Improvement dict:", improvement_dict)
            for part in parts:
                if best_increase is None or improvement_dict[part.part_id] > best_increase:
                    best_increase = improvement_dict[part.part_id]
                    best_part = part
            stock_levels[best_part.part_id] += 1
            investment = GreedyOptimizer.calculate_investment(parts, stock_levels)
            if investment > budget:
                stock_levels[best_part.part_id] += -1
                return [(part, stock_levels[part.part_id]) for part in parts]
    
    @staticmethod
    def find_cost_effective_allocation(parts: List[SparePart], budget:float=2000000) -> float:
        """Find optimal availability."""
        stock_levels = {part.part_id: max(0, ceil(part.mean_demand*part.repair_time - 2)) for part in parts}
        
        if GreedyOptimizer.calculate_investment(parts, stock_levels) > budget:
            # Initial stock levels exceed budget!
            stock_levels = GreedyOptimizer.repair_availability_fixed(parts, stock_levels, budget)
        
        while True:
            best_increase = None
            best_part = None
            
            improvement_dict = GreedyOptimizer.calculate_individual_availability(parts, stock_levels)
            investment = GreedyOptimizer.calculate_investment(parts, stock_levels)
            print("\n Improvement dict:", improvement_dict)
            for part in parts:
                if best_increase is None or improvement_dict[part.part_id] > best_increase:
                    if investment + part.unit_cost > budget:
                        continue
                    best_increase = improvement_dict[part.part_id]
                    best_part = part
            if best_part is None:
                return [(part, stock_levels[part.part_id]) for part in parts]
            else:
                stock_levels[best_part.part_id] += 1
        