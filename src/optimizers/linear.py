import sys
from pathlib import Path

# Get the project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.item_approach import ItemApproach
from utils.data_loader import SparePart
from typing import List, Tuple, Dict

class LinearOptimizer:
    """Linear optimization approach (placeholder)."""
    
    @staticmethod
    def find(parts: List[SparePart], fulfillment_target: float) -> List[Tuple[SparePart, int]]:
        """Find optimal stock levels for parts within budget using linear programming."""
        model = LinearOptimizer.optimize(parts, fulfillment_target)
        model.optimize()
        allocation = []
        model_vars = model.getVars()
        for var in model_vars:
            if var.name[0] == "s":
                part_id = var.name.split("_")[1]
                stock_level = int(model.getVal(var))
                part = next(part for part in parts if part.part_id == part_id)
                allocation.append((part, stock_level))
        return allocation
    
    @staticmethod
    def find_availability(parts: List[SparePart], budget: float = 2000000, penalty: float = 1000000) -> List[Tuple[SparePart, int]]:
        """Find optimal stock levels for parts within budget using linear programming."""
        model = LinearOptimizer.optimize_availability(parts, budget, penalty=penalty)
        model.optimize()
        allocation = []
        model_vars = model.getVars()
        for var in model_vars:
            if var.name[0] == "s":
                part_id = var.name.split("_")[1]
                stock_level = int(model.getVal(var))
                part = next(part for part in parts if part.part_id == part_id)
                allocation.append((part, stock_level))
        return allocation
    
    @staticmethod
    def get_poisson_parameters(parts: List[SparePart], k_range:int = 10) -> Dict:
        """Get Poisson distribution parameters for each part."""
        p = {}
        for part in parts:
            p[part.part_id] = [ItemApproach.stock_level(part, k) for k in range(k_range)]
        return p

    @staticmethod
    def get_poisson_parameters_availability(parts: List[SparePart], k_range:int = 10) -> Dict:
        """Get Poisson distribution parameters for each part."""
        p = {}
        for part in parts:
            p[part.part_id] = [ItemApproach.calculate_availability(part, k)*100000000 for k in range(k_range)]
        return p
    
    @staticmethod
    def optimize(parts: List[SparePart], fulfillment_target: float, k_range:int = 10):
        from pyscipopt import Model, quicksum
        
        model = Model("Linear Optimization")
        
        # define placeholder for quantity variable
        s = {}
        # define placeholder for binary identifyer variable
        y = {}
        # placeholder for cost parameter
        c = {}
        
        for part in parts:
            s[part.part_id] = model.addVar(vtype="C", name=f"s_{part.part_id}", lb=0)
            c[part.part_id] = part.unit_cost
            for k in range(k_range):
                y[part.part_id, k] = model.addVar(vtype="B", name=f"y_{part.part_id}_{k}")
        
        model.setObjective(quicksum(c[part.part_id] * s[part.part_id] for part in parts), sense="minimize")
        
        # get the poisson parameters
        p = LinearOptimizer.get_poisson_parameters(parts, k_range)
        
        #placeholder for constraint fulfillment target
        total_rate = 0
        for part in parts:
            total_rate += part.mean_demand
        model.addCons(quicksum(part.mean_demand/total_rate * p[part.part_id][k] * y[part.part_id, k] for part in parts for k in range(k_range)) >= fulfillment_target)
        
        # each part can only have one stock level
        for part in parts:
            model.addCons(quicksum(y[part.part_id, k] for k in range(k_range)) == 1)
            
        # link stock level and binary variable
        for part in parts:
            model.addCons(s[part.part_id] == quicksum(k * y[part.part_id, k] for k in range(k_range)))
        
        return model
    
    def optimize_availability(parts: List[SparePart], budget: float = 2000000, k_range:int = 22, penalty: float = 1000000):
        from pyscipopt import Model, quicksum
        
        model = Model("Linear Availability Optimization")
        
        # define placeholder for quantity variable
        s = {}
        # define placeholder for binary identifyer variable
        y = {}
        # placeholder for cost parameter
        c = {}
        # relaxation of s > 0
        r = {}
        
        for part in parts:
            s[part.part_id] = model.addVar(vtype="C", name=f"s_{part.part_id}", lb=0)
            c[part.part_id] = part.unit_cost
            r[part.part_id] = model.addVar(vtype="C", name=f"r_{part.part_id}", lb=0)
            for k in range(k_range):
                y[part.part_id, k] = model.addVar(vtype="B", name=f"y_{part.part_id}_{k}")
        
        p = LinearOptimizer.get_poisson_parameters_availability(parts, k_range)
        model.setObjective(quicksum(p[part.part_id][k] * y[part.part_id, k] for part in parts for k in range(k_range)) + penalty * quicksum(r[part.part_id] for part in parts), sense="minimize")
        
        # budget constraint
        model.addCons(quicksum(c[part.part_id] * s[part.part_id] for part in parts) <= budget)
        
        # each part can only have one stock level
        for part in parts:
            model.addCons(quicksum(y[part.part_id, k] for k in range(k_range)) == 1)
            
        # link stock level and binary variable
        for part in parts:
            model.addCons(s[part.part_id] == quicksum(k * y[part.part_id, k] for k in range(k_range)))
        
        # relaxation definition: it accounts for the parts with s = 0
        for part in parts:
            model.addCons(r[part.part_id] >= 1 - s[part.part_id])

        
        return model