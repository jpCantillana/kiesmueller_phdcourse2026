import math
from scipy.stats import poisson

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