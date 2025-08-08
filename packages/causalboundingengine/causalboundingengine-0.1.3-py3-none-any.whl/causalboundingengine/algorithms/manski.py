import numpy as np
from causalboundingengine.algorithms.algorithm import Algorithm

class Manski(Algorithm):
    def _compute_ATE(self, X: np.ndarray, Y: np.ndarray) -> tuple[float, float]:
        # p1, p0: observed means in the treated/untreated groups
        p1 = np.mean(Y[X == 1]) if np.any(X == 1) else 0.0
        p0 = np.mean(Y[X == 0]) if np.any(X == 0) else 0.0

        # π1, π0: group sizes
        p_x1 = np.mean(X == 1)       # π1  ≡ P(X=1)
        p_x0 = 1.0 - p_x1            # π0  ≡ P(X=0)

        # Manski (1990) worst-case bounds
        lower = p1 * p_x1 - p0 * p_x0 - p_x1    
        upper = p1 * p_x1 + p_x0 - p0 * p_x0

        return min(lower, upper), max(lower, upper)
