import numpy as np

class AlgUtil:
    """
    Utility class for algorithms.
    """
    @staticmethod
    def get_trivial_Ceils(query):
        """
        Get trivial Ceils for the given query.

        Args:
            query (str): The query type (e.g., 'ATE' or 'PNS').

        Returns:
            tuple: A tuple containing the lower and upper bounds.
        """
        if query == 'ATE':
            return -1, 1
        elif query == 'PNS':
            return 0, 1
        else:
            raise ValueError(f"Unknown query type: {query}")
               
    @staticmethod
    def flatten_bounds_to_trivial_ceils(query, bound_lower, bound_upper, failed):
        # Flatten bounds to trivial ceils and ensure numpy float types
        trivial_lower, trivial_upper = AlgUtil.get_trivial_Ceils(query)
        if failed or (bound_upper > trivial_upper):
            bound_upper = np.float64(trivial_upper)
        else:
            bound_upper = np.float64(bound_upper)
        if failed or (bound_lower < trivial_lower):
            bound_lower = np.float64(trivial_lower)
        else:
            bound_lower = np.float64(bound_lower)
        return bound_lower, bound_upper
    
    @staticmethod
    def flatten_bounds_to_trivial_ceils_vectorized(query, bound_lower, bound_upper, failed):
        """
        Vectorized version: Flatten bounds to trivial ceils for pandas Series.
        Args:
            query (str): The query type (e.g., 'ATE' or 'PNS').
            bound_lower (pd.Series): Lower bounds.
            bound_upper (pd.Series): Upper bounds.
            failed (pd.Series): Boolean mask for failed bounds.
        Returns:
            tuple: (flattened_lower, flattened_upper) as pd.Series
        """
        import numpy as np
        trivial_lower, trivial_upper = AlgUtil.get_trivial_Ceils(query)
        # Set upper to trivial_upper if failed or upper > trivial_upper
        upper = bound_upper.where(~(failed | (bound_upper > trivial_upper)), trivial_upper)
        # Set lower to trivial_lower if failed or lower < trivial_lower
        lower = bound_lower.where(~(failed | (bound_lower < trivial_lower)), trivial_lower)
        return lower, upper