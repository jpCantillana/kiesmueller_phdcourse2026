from typing import List
import csv
from dataclasses import dataclass

@dataclass
class SparePart:
    part_id: str
    unit_cost: float
    mean_demand: float  # λ parameter for Poisson
    repair_time: float
    holding_cost: float
    shortage_cost: float
    
def load_spare_parts(filepath: str) -> List[SparePart]:
    """Load spare parts data from CSV file without Pandas."""
    parts = []
    
    with open(filepath, mode='r', encoding='utf-8') as f:
        # DictReader maps the information in each row to a dict
        reader = csv.DictReader(f)
        
        for row in reader:
            part = SparePart(
                part_id=row['part_id'],
                unit_cost=float(row['unit_cost']),
                mean_demand=float(row['mean_demand']),
                repair_time=float(row['repair_time']),
                holding_cost=float(row['holding_cost']),
                shortage_cost=float(row['shortage_cost'])
            )
            parts.append(part)
            
    return parts