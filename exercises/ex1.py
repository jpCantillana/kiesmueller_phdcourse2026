import sys
import sys
from pathlib import Path

# Get the project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.data_loader import load_spare_parts
from src.models.item_approach import ItemApproach
from src.optimizers.greedy import GreedyOptimizer

def main(data_file: str):
    """Run exercise 1 with given data file."""
    
    print(f"Loading data from {data_file}")
    parts = load_spare_parts(data_file)
    
    print("\n=== Item Approach Analysis ===")
    for part in parts:
        optimal_S = ItemApproach.find_best_stock_level(part, 0.95)
        total_cost = ItemApproach.calculate_total_cost(part, optimal_S)
        
        print(f"\nPart {part.part_id}:")
        print(f"  Optimal base stock: {optimal_S}")
        print(f"  Expected total cost: €{total_cost:.2f}")
    
    print("\n=== System approach Allocation ===")

    fulfillment_target = 0.95
    allocation = GreedyOptimizer.find(parts, fulfillment_target)
    for part, stock_level in allocation:
        print(f"Part {part.part_id}; Stock Level = {stock_level}; Total Cost = €{ItemApproach.calculate_total_cost(part, stock_level):.2f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ex1.py <data_file.csv>")
        sys.exit(1)
    
    main(sys.argv[1])