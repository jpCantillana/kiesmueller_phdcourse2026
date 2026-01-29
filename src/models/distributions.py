import copy
import math
from scipy.stats import poisson, binom

class PoissonDistribution:
    """Helper class for Poisson distribution calculations."""
    
    @staticmethod
    def pmf(k: int, lambd: float) -> float:
        """Probability mass function P(X = k)."""
        return poisson.pmf(k, lambd)
    
    @staticmethod
    def cdf(k: int, lambd: float) -> float:
        """Cumulative distribution function P(X ≤ k)."""
        return poisson.cdf(k, lambd)
    
    @staticmethod
    def sf(k: int, lambd: float) -> float:
        """Survival function P(X > k)."""
        return poisson.sf(k, lambd)

class BinomialDistribution:
    """Helper class for Binomial distribution calculations."""
    
    @staticmethod
    def pmf(k: int, n: int, p: float) -> float:
        """Probability mass function P(X = k)."""
        return binom.pmf(k, n, p)
    
    @staticmethod
    def cdf(k: int, n: int, p: float) -> float:
        """Cumulative distribution function P(X ≤ k)."""
        return binom.cdf(k, n, p)
    
    @staticmethod
    def sf(k: int, n: int, p: float) -> float:
        """Survival function P(X > k)."""
        return binom.sf(k, n, p)

class BackOrdersCentralDepotDistribution:
    """Helper class for Back Orders Central Depot distribution calculations."""
    
    @staticmethod
    def availability(S: int, lambd: float, k: int) -> float:
        """Calculate availability for Back Orders Central Depot model."""
        if k == 0:
            return PoissonDistribution.cdf(S, lambd)
        return PoissonDistribution.pmf(S + k, lambd)

class OnHandCentralDepotDistribution:
    """Helper class for On Hand Central Depot distribution calculations."""
    
    @staticmethod
    def availability(S: int, lambd: float, k: int) -> float:
        """Calculate availability for On Hand Central Depot model."""
        if k == 0:
            return PoissonDistribution.cdf(S, lambd)
        return PoissonDistribution.pmf(S - k, lambd)

class BackOrdersCentralDepotLocalDepotInducedDistribution:
    """Helper class for Back Orders Central Depot with Local Depot Induced distribution calculations."""
    
    @staticmethod
    def exponential_race_rate(lambda_list: list) -> float:
        """Calculate the rate of the minimum of independent exponential random variables."""
        return sum(lambda_list)
    
    @staticmethod
    def probability(back_orders: int, S_0: int, depot_rate: float, lamb: float, b_min: int = 30) -> float:
        """Calculate probability for Back Orders Central Depot with Local Depot Induced model."""
        prob = 0.0
        y = copy.deepcopy(back_orders)
        while True:
            binom_prob = BinomialDistribution.pmf(back_orders, y, depot_rate)
            prob += binom_prob * BackOrdersCentralDepotDistribution.availability(S_0, lamb, y)
            if PoissonDistribution.cdf(S_0+y, lamb) >= 1 - 1e-6 and y > b_min:
                break
            else:
                y += 1
        return prob
    
    @staticmethod
    def probability_outstanding_orders_at_local_depot(outstanding_orders: int, S_0: int, depot_rate: float, depot_leadtime: float, lamb: float, lead_time_i: float) -> float:
        """Calculate probability given central backorders."""
        prob = 0.0
        for j in range(0, outstanding_orders + 1):
            poisson_prob = PoissonDistribution.pmf(outstanding_orders - j, lamb * lead_time_i)
            back_orders_prob = BackOrdersCentralDepotLocalDepotInducedDistribution.probability(j, S_0, depot_rate, 1/depot_rate*lamb*depot_leadtime)
            prob += poisson_prob * back_orders_prob
        return prob

    @staticmethod
    def expected_backorders_at_central_depot(S_0: int, depot_rate: float, lamb: float, b_min:int = 30) -> float:
        """Calculate expected value for Back Orders Central Depot with Local Depot Induced model."""
        exp_value = 0.0
        i = 1
        while True:
            prob = BackOrdersCentralDepotLocalDepotInducedDistribution.probability(i, S_0, depot_rate, lamb)
            if prob < 1e-6 and i > b_min:
                break
            exp_value += i * prob
            i += 1
        return exp_value

    @staticmethod
    def expected_backorders_at_local_depot(S_0: int, S_i: int, lambd_i: float, sum_lamb: float, L_i: float, L_0: float) -> float:
        """Calculate expected back orders."""
        demand_part =  lambd_i * L_i
        rate = lambd_i / sum_lamb
        # back_order_part = BackOrdersCentralDepotLocalDepotInducedDistribution.expected_backorders_at_central_depot(S_0, rate, demand_part)
        back_order_part = BackOrdersCentralDepotLocalDepotInducedDistribution.expected_backorders_at_central_depot(S_0, lambd_i / sum_lamb, sum_lamb * L_0)
        outstanding_part = 0.0
        for j in range(S_i + 1):
            outstanding_part += (S_i - j) * BackOrdersCentralDepotLocalDepotInducedDistribution.probability_outstanding_orders_at_local_depot(j, S_0, rate, L_0, lambd_i , L_i)
        # print("demand_part:", demand_part, "back_order_part:", back_order_part, "outstanding_part:", outstanding_part)
        return demand_part + back_order_part - S_i + outstanding_part
        