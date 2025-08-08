

import math
import cvxpy as cp
import numpy as np
from causalboundingengine.algorithms.algorithm import Algorithm

class Entropybounds(Algorithm):
    def _compute_ATE(self, X: np.ndarray, Y: np.ndarray, theta: float) -> tuple[float, float]:
        """
        Adapted from:
        https://github.com/ziwei-jiang/Approximate-Causal-Effect-Identification-under-Weak-Confounding
        Copyright (c) 2021 Ziwei Jiang
        Licensed under the MIT License
        """
        # Estimate P(X) and P(Y|X) from data
        x      = np.mean(X)
        x_bar  = 1 - x
        y_x    = np.mean(Y[X == 1])
        y_barx = 1 - y_x

        # Build observational joint P(Y,X)
        pyx = np.array([[y_x * x, y_barx * x],
                        [0.5 * x_bar, 0.5 * x_bar]]).T

        # Solve for bounds on P(Y=1 | do(X=1)) and P(Y=1 | do(X=0))
        lb11, ub11, _ = Entropybounds._ATE_optimization_cf(pyx, ub=theta, p=1, q=1)
        lb10, ub10, _ = Entropybounds._ATE_optimization_cf(pyx, ub=theta, p=1, q=0)

        # Calculate ATE bounds
        lower = lb11 - ub10
        upper = ub11 - lb10
        return lower, upper
    

    def _compute_PNS(self, X: np.ndarray, Y: np.ndarray, theta: float) -> tuple[float, float]:
        # ---------- 1.  empirical quantities (constants) ----------
        p_x1 = float(np.mean(X))
        p_x0 = 1.0 - p_x1

        #  P(Y=1 | X)
        p_y1_x1 = float(np.mean(Y[X == 1])) if np.any(X == 1) else 0.0
        p_y1_x0 = float(np.mean(Y[X == 0])) if np.any(X == 0) else 0.0

        # ---------- 2.  decision variable : joint P(Y1,Y0,X) ----------
        # state order (row-major, X fastest):
        # (y1,y0,x) = (0,0,0) … (0,0,1) … (1,1,1)  ⇒  8 states
        q = cp.Variable(8)

        # ---------- 3.  basic probability constraints ----------
        constraints = [
            cp.sum(q) == 1,
            q >= 0
        ]

        # ---------- 4.  match the observable distribution P(Y=1 ,  X) ----------
        #   Y=1 with X=1  ⇔  Y1=1 ,  x=1   → indices 5 and 7
        constraints.append(q[5] + q[7] == p_y1_x1 * p_x1)

        #   Y=1 with X=0  ⇔  Y0=1 ,  x=0   → indices 2 and 6
        constraints.append(q[2] + q[6] == p_y1_x0 * p_x0)

        # ---------- 5.  mutual-information (entropy) constraint ----------
        #
        # selector S :  P(Y1,Y0) = S @ q    (4×8  constant)
        S = np.zeros((4, 8))
        S[0, [0, 1]] = 1          # (0,0)
        S[1, [2, 3]] = 1          # (0,1)
        S[2, [4, 5]] = 1          # (1,0)
        S[3, [6, 7]] = 1          # (1,1)
        p_y1y0 = S @ q            # length-4 affine expression

        # replicator T :  product dist  r  =  T @ p_y1y0   (8×4  constant)
        T = np.zeros((8, 4))
        for k in range(4):
            T[2 * k,     k] = p_x0      # x = 0
            T[2 * k + 1, k] = p_x1      # x = 1
        r = T @ p_y1y0                  # length-8 affine expression

        # KL-divergence  (I((Y1,Y0);X) in bits)
        kl_bits = cp.sum(cp.kl_div(q, r)) / math.log(2)
        constraints.append(kl_bits <= theta)

        # ---------- 6.  objective :  PNS = P(Y1=1 , Y0=0) ----------
        # indices with (y1=1, y0=0):  x=0 → 4 ,  x=1 → 5
        pns = q[4] + q[5]

        # ---------- 7.  optimise ----------
        lb_prob = cp.Problem(cp.Minimize(pns), constraints)
        ub_prob = cp.Problem(cp.Maximize(pns), constraints)
        lb_prob.solve(solver=cp.SCS)
        ub_prob.solve(solver=cp.SCS)

        return lb_prob.value, ub_prob.value

    @staticmethod
    def _ATE_optimization_cf(pyx, ub=1, p =0, q=0):
        # Adapted from:
        # https://github.com/ziwei-jiang/Approximate-Causal-Effect-Identification-under-Weak-Confounding
        # Copyright (c) 2021 Ziwei Jiang
        # Licensed under the MIT License

        ##### for P(Y=p|do(X=q)) #####
        nx = pyx.shape[1]
        ny = pyx.shape[0]
        px = pyx.sum(axis=0)
        # uy_x: 1x(nx*ny) vector
        uy_x = cp.Variable(nx*ny)
        v1 = np.zeros(nx*ny)
        v1[p*nx:p*nx+nx] = px
        pydox = uy_x @ v1
        v2 = np.zeros((ny, nx*ny))
        for i in range(ny):
            v2[i, i*nx:(i+1)*nx] = px
        # qy: 1xny vector 
        qy = uy_x @ v2.T
        # qyx: 1x(nx*ny) vector
        qyx = qy @ v2
        v3 = np.zeros((nx*ny))
        for i in range(ny):
            v3[i*nx:(i+1)*nx] = px
        uyx = cp.multiply(uy_x, v3)
        dkl = cp.kl_div(uyx, qyx)/math.log(2)
        I = cp.sum(dkl)
        v4 = np.zeros((nx*ny, ny))
        for i in range(ny):
            v4[nx*i+q, i] = px[q]
        v5 = np.zeros((nx*ny, nx))
        for i in range(nx):
            v5[i:nx*ny:nx, i] = 1
        constraints  = [uy_x @ v4 == pyx[:,q],
                        uy_x@v5 == np.ones(nx), 
                        uy_x >= 0, uy_x <= 1,
                        I <= ub]
        max_obj = cp.Maximize(pydox)
        min_obj = cp.Minimize(pydox)
        t = 0
        max_prob = cp.Problem(max_obj, constraints)
        max_prob.solve(solver=cp.SCS)
        t += max_prob.solver_stats.solve_time
        min_prob = cp.Problem(min_obj, constraints)
        min_prob.solve(solver=cp.SCS)
        t += min_prob.solver_stats.solve_time
        return min_prob.value, max_prob.value, t
    

    