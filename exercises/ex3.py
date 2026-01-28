## Divergent systems
import sys
from pathlib import Path

# Get the project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import src.models.distributions as dist

def main():
    S_0, S_1, S_2, S_3, = 4,1,1,2
    lambd_1, lambd_2, lambd_3 = 2/30, 3/30, 5/30
    sum_lamb = lambd_1 + lambd_2 + lambd_3
    L_0, L_1, L_2, L_3 = 2*7, 3*7, 3*7, 3*7
    
    # Outstanding orders in the central depot
    S_a = 5
    outstanding_orders = dist.PoissonDistribution.pmf(S_a, sum_lamb * L_0)
    print(f"Outstanding orders in central depot when S = {S_a}: {outstanding_orders}")
    # Units on Stock at central depot
    S_b = 1
    onhand_probability = dist.OnHandCentralDepotDistribution.availability(S_0, sum_lamb * L_0, S_b)
    print(f"Probability of having {S_b} units on stock at central depot when S = {S_0}: {onhand_probability}")
    # No backorders at central depot
    S_c = 0
    backorder_probability = dist.BackOrdersCentralDepotDistribution.availability(S_0, sum_lamb * L_0, S_c)
    print(f"Probability of having no backorders at central depot when S = {S_0}: {backorder_probability}")
    # 4 Backorders at the central depot, probability that 2 of them come from local depot 3
    S_d = 4
    backorder_probability_2_from_3 = dist.BackOrdersCentralDepotLocalDepotInducedDistribution.probability(2, S_0, lambd_3 / sum_lamb, sum_lamb * L_0)
    print(f"Probability that 2 out of {S_d} backorders at central depot come from local depot 3 when S = {S_0} and central backorders = {S_d}: {backorder_probability_2_from_3}")
    
    S_0, S_1, S_2, S_3, = 4,1,1,2
    lambd_1, lambd_2, lambd_3 = 2, 3, 5
    sum_lamb = lambd_1 + lambd_2 + lambd_3
    L_0, L_1, L_2, L_3 = 0.5, 0.1, 0.1, 0.1
    
    # # Probability distribution of the outstanding orders at the central depot
    # for outstanding_order in range(16):
    #     prob_outstanding_orders = dist.PoissonDistribution.pmf(outstanding_order, sum_lamb * L_0)
    #     print(f"Probability of having {outstanding_order} outstanding orders at central depot when S = {S_0}: {prob_outstanding_orders}")
    # # Probability distribution of backorders at the central depot
    # for backorder in range(16):
    #     prob_backorders = dist.BackOrdersCentralDepotDistribution.availability(S_0, sum_lamb * L_0, backorder)
    #     print(f"Probability of having {backorder} backorders at central depot when S = {S_0}: {prob_backorders}")
    # # Probability distribution of the backorders at the central deport coming from local depot 1
    # for backorder_local_1 in range(6):
    #     prob_backorders_local_1 = dist.BackOrdersCentralDepotLocalDepotInducedDistribution.probability(backorder_local_1, S_0, lambd_1 / sum_lamb, sum_lamb * L_0)
    #     print(f"Probability of having {backorder_local_1} backorders at central depot coming from local depot 1 when S = {S_0}: {prob_backorders_local_1}")
    # # Expected number of backorders at central depot induced by local depot 1
    # expected_backorders_central = dist.BackOrdersCentralDepotLocalDepotInducedDistribution.expected_backorders_at_central_depot(S_0, lambd_1 / sum_lamb, sum_lamb * L_0)
    # print(f"Expected number of backorders at central depot when S = {S_0}: {expected_backorders_central}")
    # # Probability distribution of the outstanding orders at local depot 1
    # for outstanding_order_local_1 in range(7):
    #     prob_outstanding_orders_local_1 = dist.BackOrdersCentralDepotLocalDepotInducedDistribution.probability_outstanding_orders_at_local_depot(outstanding_order_local_1, S_0, lambd_1 / sum_lamb, L_0, lambd_1 , L_1)
    #     print(f"Probability of having {outstanding_order_local_1} outstanding orders at local depot 1 when S = {S_0}: {prob_outstanding_orders_local_1}")
    
    # Expected number of backorders at local depot 1
    expected_backorders_local_1 = dist.BackOrdersCentralDepotLocalDepotInducedDistribution.expected_backorders_at_local_depot(S_0, S_1, lambd_1, sum_lamb , L_1, L_0)
    print(f"Expected number of backorders at local depot 1 when S = {S_0}: {expected_backorders_local_1}")
    # Expected number of backorders at local depot 2
    expected_backorders_local_2 = dist.BackOrdersCentralDepotLocalDepotInducedDistribution.expected_backorders_at_local_depot(S_0, S_2, lambd_2, sum_lamb , L_2, L_0)
    print(f"Expected number of backorders at local depot 2 when S = {S_0}: {expected_backorders_local_2}")
    # Expected number of backorders at local depot 3
    expected_backorders_local_3 = dist.BackOrdersCentralDepotLocalDepotInducedDistribution.expected_backorders_at_local_depot(S_0, S_3, lambd_3, sum_lamb , L_3, L_0)
    print(f"Expected number of backorders at local depot 3 when S = {S_0}: {expected_backorders_local_3}")
    
if __name__ == "__main__":
    main()