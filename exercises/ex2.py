import sys
from pathlib import Path

# Get the project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.data_loader import load_spare_parts
from src.models.item_approach import ItemApproach
from src.optimizers.greedy import GreedyOptimizer
from src.optimizers.linear import LinearOptimizer

def calculate_total_availability(parts, allocation):
    individual_availabilities = 1
    for part in parts:
        # print(1 - ItemApproach.calculate_availability(part, allocation[part.part_id]))
        individual_availabilities *= (1 - ItemApproach.calculate_availability(part, allocation[part.part_id]))
    return individual_availabilities

def main(data_file: str, budget: float = 200000):
    print(f"Loading data from {data_file}")
    parts = load_spare_parts(data_file)
    
    print("\n=== System approach Availability Optimization ===")
    allocation_greedy = GreedyOptimizer.find_availability(parts, budget=budget)
    print("\n--- Greedy Optimization Allocation ---")
    for part, stock_level in allocation_greedy:
        print(f"Part {part.part_id}; Stock Level = {stock_level}; Total Cost = €{ItemApproach.calculate_total_cost(part, stock_level):.2f}, Availability = {ItemApproach.calculate_availability(part, stock_level)*1000000:.4f}e-6")
    greedy_allocation = calculate_total_availability(parts, {part.part_id: stock_level for part, stock_level in allocation_greedy})
    print("\nTotal Availability (Greedy):", greedy_allocation)
    
    print("\n--- Greedy Optimization Allocation --- Fixed Target ---")
    allocation_greedy_fixed = GreedyOptimizer.find_availability_fixed(parts, budget=budget)
    for part, stock_level in allocation_greedy_fixed:
        print(f"Part {part.part_id}; Stock Level = {stock_level}; Total Cost = €{ItemApproach.calculate_total_cost(part, stock_level):.2f}, Availability = {ItemApproach.calculate_availability(part, stock_level)*1000000:.4f}e-6")
    greedy_allocation_fixed = calculate_total_availability(parts, {part.part_id: stock_level for part, stock_level in allocation_greedy_fixed})
    print("\nTotal Availability (Greedy Fixed):", greedy_allocation_fixed)

    print("\n--- Greedy Optimization --- Improved Target ---")
    allocation_greedy_cost_effective = GreedyOptimizer.find_cost_effective_allocation(parts, budget=budget)
    for part, stock_level in allocation_greedy_cost_effective:
        print(f"Part {part.part_id}; Stock Level = {stock_level}; Total Cost = €{ItemApproach.calculate_total_cost(part, stock_level):.2f}, Availability = {ItemApproach.calculate_availability(part, stock_level)*1000000:.4f}e-6")
    greedy_allocation_cost_effective = calculate_total_availability(parts, {part.part_id: stock_level for part, stock_level in allocation_greedy_cost_effective})
    print("\nTotal Availability (Greedy Cost Effective):", greedy_allocation_cost_effective)
    
    print("\n--- Linear Optimization Allocation, penalty = 0 ---")
    allocation_linear = LinearOptimizer.find_availability(parts, budget=budget, penalty=0)
    for part, stock_level in allocation_linear:
        print(f"Part {part.part_id}; Stock Level = {stock_level}; Total Cost = €{ItemApproach.calculate_total_cost(part, stock_level):.2f}, Availability = {ItemApproach.calculate_availability(part, stock_level)*1000000:.4f}e-6")
    linear_allocation = calculate_total_availability(parts, {part.part_id: stock_level for part, stock_level in allocation_linear})
    print("\nTotal Availability (Linear) with penalty 0:", linear_allocation)
    
    # print("\n--- Linear Optimization Allocation, penalty = 1000000 ---")
    # allocation_linear = LinearOptimizer.find_availability(parts, budget=budget, penalty=1000000)
    # for part, stock_level in allocation_linear:
    #     print(f"Part {part.part_id}; Stock Level = {stock_level}; Total Cost = €{ItemApproach.calculate_total_cost(part, stock_level):.2f}, Availability = {ItemApproach.calculate_availability(part, stock_level)*1000000:.4f}e-6")
    # linear_allocation_2 = calculate_total_availability(parts, {part.part_id: stock_level for part, stock_level in allocation_linear})
    # print("\nTotal Availability (Linear) with penalty 1000000:", linear_allocation_2)

    print("\n--- Linear Optimization Allocation, penalty = 100000000 ---")
    allocation_linear = LinearOptimizer.find_availability(parts, budget=budget, penalty=100000000)
    for part, stock_level in allocation_linear:
        print(f"Part {part.part_id}; Stock Level = {stock_level}; Total Cost = €{ItemApproach.calculate_total_cost(part, stock_level):.2f}, Availability = {1 -ItemApproach.calculate_availability(part, stock_level):.8f}")
    linear_allocation_3 = calculate_total_availability(parts, {part.part_id: stock_level for part, stock_level in allocation_linear})
    print("\nTotal Availability (Linear) with penalty 100000000:", linear_allocation_3)
    
    print("\n=== Comparison to optimal bound ===")
    print(f"Greedy Allocation to penalty 0: {(-(greedy_allocation - linear_allocation)/linear_allocation)*100:.8f}%")
    print(f"Greedy Fixed Allocation to penalty 0: {(-(greedy_allocation_fixed - linear_allocation)/linear_allocation)*100:.8f}%")
    print(f"Greedy Cost Effective Allocation to penalty 0: {(-(greedy_allocation_cost_effective - linear_allocation)/linear_allocation)*100:.8f}%")
    # print(f"Greedy Allocation to penalty 1000000: {greedy_allocation/linear_allocation_2 - 1:.8f}%")
    # print(f"Greedy Fixed Allocation to penalty 1000000: {greedy_allocation_fixed/linear_allocation_2 - 1:.8f}%")
    # print(f"Greedy Cost Effective Allocation to penalty 1000000: {greedy_allocation_cost_effective/linear_allocation_2 - 1:.8f}%")
    print(f"Greedy Allocation to penalty 100000000: {(-(greedy_allocation - linear_allocation_3)/linear_allocation_3)*100:.8f}%")
    print(f"Greedy Fixed Allocation to penalty 100000000: {(-(greedy_allocation_fixed - linear_allocation_3)/linear_allocation_3)*100:.8f}%")
    print(f"Greedy Cost Effective Allocation to penalty 100000000: {(-(greedy_allocation_cost_effective - linear_allocation_3)/linear_allocation_3)*100:.8f}%")

if __name__ == "__main__":
    if len(sys.argv) not in [2,3]:
        print("Usage: python ex2.py <data_file.csv>")
        sys.exit(1)
    if len(sys.argv) == 2:
        main(sys.argv[1])
    if len(sys.argv) == 3:
        main(sys.argv[1], float(sys.argv[2]))