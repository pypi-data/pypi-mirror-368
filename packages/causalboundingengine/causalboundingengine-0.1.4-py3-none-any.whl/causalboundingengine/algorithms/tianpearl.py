import numpy as np
from causalboundingengine.algorithms.algorithm import Algorithm

class TianPearl(Algorithm):
    
    def _compute_PNS(self, X: np.ndarray, Y: np.ndarray) -> tuple[float, float]:
        # Nonparametric bounds without assuming exogeneity
        p_xy = np.mean((X == 1) & (Y == 1))
        p_x0y0 = np.mean((X == 0) & (Y == 0))

        lower = 0.0
        upper = p_xy + p_x0y0

        return lower, upper
