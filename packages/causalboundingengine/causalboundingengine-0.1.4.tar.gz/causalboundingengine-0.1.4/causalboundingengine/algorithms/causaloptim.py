# causalboundingengine/algorithms/causaloptim.py

import numpy as np
from causalboundingengine.algorithms.algorithm import Algorithm
from causalboundingengine.utils.r_utils import ensure_r_ready
import pandas as pd

class CausalOptim(Algorithm):
    # This implementation integrates with the R package `causaloptim`:
    #   https://github.com/sachsmc/causaloptim
    # 
    # Developed by Sachs et al., it provides methods for symbolic derivation and
    # bounding of causal effects. This package uses it via `rpy2` for selected algorithms.


    def _compute_ATE(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray = None, r_path: str = None, **kwargs) -> tuple[float, float]:
        """
        Computes bounds on the Average Treatment Effect (ATE) using causaloptim (via rpy2 + R).
        Accepts optional instrument/confounder Z.
        """
        ensure_r_ready(r_path)

        if Z is not None:
            result = CausalOptim._run_experiment("ATE",
                       graph_str="(Z -+ X, X -+ Y, Ur -+ X, Ur -+ Y)", 
                       leftside=[1, 0, 0, 0], 
                       latent=[0, 0, 0, 1], 
                       nvals=[2, 2, 2, 2], 
                       rlconnect=[0, 0, 0, 0], 
                       monotone=[0, 0, 0, 0],
                        df=pd.DataFrame({'Y': Y, 'X': X, 'Z': Z}))

            bound_lower = result['lower_bound']
            bound_upper = result['upper_bound']
            return bound_lower, bound_upper

        else:
            result = CausalOptim._run_experiment("ATE",
                       graph_str="(X -+ Y, Ur -+ X, Ur -+ Y)", 
                       leftside=[0, 0, 0], 
                       latent=[0, 0, 1], 
                       nvals=[2, 2, 2], 
                       rlconnect=[0, 0, 0], 
                       monotone=[0, 0, 0],
                        df=pd.DataFrame({'Y': Y, 'X': X}))

            bound_lower = result['lower_bound']
            bound_upper = result['upper_bound']
            return bound_lower, bound_upper

    def _compute_PNS(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray = None, r_path: str = None, **kwargs) -> tuple[float, float]:
        """
        Computes bounds on the Probability of Necessity and Sufficiency (PNS) using causaloptim (via rpy2 + R).
        Accepts optional instrument/confounder Z.
        """
        ensure_r_ready(r_path)

        if Z is not None:
            result = CausalOptim._run_experiment("PNS",  
                       graph_str="(Z -+ X, X -+ Y, Ur -+ X, Ur -+ Y)", 
                       leftside=[1, 0, 0, 0], 
                       latent=[0, 0, 0, 1], 
                       nvals=[2, 2, 2, 2], 
                       rlconnect=[0, 0, 0, 0], 
                       monotone=[0, 0, 0, 0],
                        df=pd.DataFrame({'Y': Y, 'X': X, 'Z': Z}))

            bound_lower = result['lower_bound']
            bound_upper = result['upper_bound']
            return bound_lower, bound_upper
        else:
            result = CausalOptim._run_experiment("PNS",
            graph_str="(X -+ Y, Ur -+ X, Ur -+ Y)", 
            leftside=[0, 0, 0], 
            latent=[0, 0, 1], 
            nvals=[2, 2, 2], 
            rlconnect=[0, 0, 0], 
            monotone=[0, 0, 0],
            df=pd.DataFrame({'Y': Y, 'X': X}))

            bound_lower = result['lower_bound']
            bound_upper = result['upper_bound']
            return bound_lower, bound_upper
        

    @staticmethod
    def _run_experiment(query, graph_str, leftside, latent, nvals, rlconnect, monotone, df):
        """
        Run a complete causal bounds experiment using R's global environment.
        
        Note: This function is not thread-safe. It resets the global R environment
        using rm(list=ls()) and closeAllConnections().

        Parameters:
            graph_str: String defining the DAG in igraph syntax
            leftside, latent, nvals: vertex attributes
            rlconnect, monotone: edge attributes
            prob_dict: dictionary of probabilities, e.g., {'p00_0': 0.2, ...}

        Returns:
            tuple: (lower_bound, upper_bound) from causaloptim
        """
        from rpy2.robjects import r, globalenv, IntVector, FloatVector
        from rpy2.robjects.environments import Environment
        from rpy2.robjects.packages import importr
        from rpy2.robjects import IntVector, FloatVector
        importr('causaloptim')
        importr('base')

        prob_dict, has_z = CausalOptim._extract_prob_dict(df)
        

        # Reset R state (clears variables, closes open files/connections)
        r('closeAllConnections(); rm(list=ls())')

        # Load required libraries (disabled, uncomment if needed)
        #importr("igraph")
        #importr("causaloptim")

        # Create the graph
        r(f'graph <- igraph::graph_from_literal{graph_str}')

        # Assign vectors to R
        num_vertices = len(r('V(graph)'))
        # Only assign attributes if their length matches the number of vertices/edges
        if leftside and len(leftside) == num_vertices:
            globalenv["leftside"] = IntVector(leftside)
            r('V(graph)$leftside <- leftside')
        if latent and len(latent) == num_vertices:
            globalenv["latent"] = IntVector(latent)
            r('V(graph)$latent <- latent')
        if nvals and len(nvals) == num_vertices:
            globalenv["nvals"] = IntVector(nvals)
            r('V(graph)$nvals <- nvals')
        num_edges = len(r('E(graph)'))
        if rlconnect and len(rlconnect) == num_edges:
            globalenv["rlconnect"] = IntVector(rlconnect)
            r('E(graph)$rlconnect <- rlconnect')
        if monotone and len(monotone) == num_edges:
            globalenv["monotone"] = IntVector(monotone)
            r('E(graph)$edge.monotone <- monotone')

        # Inject probabilities
        for key, val in prob_dict.items():
            globalenv[key] = FloatVector([val])

        if query == "ATE":
            r("""
                query <- "p{Y(X = 1) = 1} - p{Y(X = 0) = 1}"
              """)
        elif query == "PNS":
            r("""
                query <- "p{Y(X = 1) = 1; Y(X = 0) = 0}"
              """)
        else:
            raise ValueError("Query must be either 'ATE' or 'PNS'")


        # Compute bounds
        if has_z:
            r("""
                obj <- analyze_graph(graph, constraints = NULL, effectt = query)
                bounds <- optimize_effect_2(obj)
                boundsfunc <- interpret_bounds(bounds = bounds$bounds, obj$parameters)
                bounds_result <- boundsfunc(
                  p00_0 = p00_0, p00_1 = p00_1,
                  p10_0 = p10_0, p10_1 = p10_1,
                  p01_0 = p01_0, p01_1 = p01_1,
                  p11_0 = p11_0, p11_1 = p11_1
                )
            """)
        else:
            # Remove any reference to Z in the graph string for the no-instrument case
            # and ensure the graph string only contains X, Y, Ur, etc.
            # Also, make sure the graph string is correct for this case before calling this function.
            r("""
                obj <- analyze_graph(graph, constraints = NULL, effectt = query)
                bounds <- optimize_effect_2(obj)
                boundsfunc <- interpret_bounds(bounds = bounds$bounds, obj$parameters)
                bounds_result <- boundsfunc(
                  p00 = p00,
                  p10 = p10,
                  p01 = p01,
                  p11 = p11
                )
            """)


        # Fetch and return result
        bounds = r("bounds_result")
        lb = bounds[0][0]
        ub = bounds[1][0]

        return {'lower_bound': lb, 'upper_bound': ub}

    @staticmethod
    def _extract_prob_dict(df):
        """
        Given a DataFrame with binary columns Y, X, and optionally Z,
        compute the conditional probabilities in the format expected by causaloptim.

        Returns:
            tuple: (dict, has_z) where dict is the probability dictionary,
                   has_z is True if Z is present, False otherwise.
        """
        if 'Z' in df.columns:
            # Count joint occurrences
            joint_counts = df.groupby(['Y', 'X', 'Z']).size().reset_index(name='count')

            # Count total occurrences of each Z
            z_counts = df['Z'].value_counts().to_dict()

            # Compute conditional probabilities
            joint_counts['p_yx_z'] = joint_counts.apply(
                lambda row: row['count'] / z_counts[row['Z']], axis=1
            )

            # Convert to lookup dict
            marg_dict = {
                (int(row.Y), int(row.X), int(row.Z)): row.p_yx_z
                for _, row in joint_counts.iterrows()
            }

            # Helper to safely extract or return 0
            def get_prob(y, x, z):
                return marg_dict.get((y, x, z), 0.0)

            # Build final dictionary in causaloptim format
            return {
                'p00_0': get_prob(0, 0, 0),
                'p10_0': get_prob(1, 0, 0),
                'p01_0': get_prob(0, 1, 0),
                'p11_0': get_prob(1, 1, 0),
                'p00_1': get_prob(0, 0, 1),
                'p10_1': get_prob(1, 0, 1),
                'p01_1': get_prob(0, 1, 1),
                'p11_1': get_prob(1, 1, 1),
            }, True
        else:
            # No Z: just joint probabilities P(Y, X)
            joint_counts = df.groupby(['Y', 'X']).size().reset_index(name='count')
            total = len(df)
            joint_counts['p_yx'] = joint_counts['count'] / total
            marg_dict = {
                (int(row.Y), int(row.X)): row.p_yx
                for _, row in joint_counts.iterrows()
            }
            def get_prob(y, x):
                return marg_dict.get((y, x), 0.0)
            prob_dict = {
                'p00': get_prob(0, 0),
                'p10': get_prob(1, 0),
                'p01': get_prob(0, 1),
                'p11': get_prob(1, 1),
            }
            return prob_dict, False
