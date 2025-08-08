from causalboundingengine.utils.data import Data

class Scenario:
    """
    Base class for scenarios in the Causal Bounding Engine.

    Each subclass must define the AVAILABLE_ALGORITHMS dictionary,
    which maps query types ('ATE', 'PNS') to supported algorithm classes.

    Upon initialization, this class creates AlgorithmDispatcher instances
    for both ATE and PNS queries using the provided data.
    """

    AVAILABLE_ALGORITHMS = {}  # To be overridden by child scenarios

    def __init__(self, X, Y, Z=None):
        """
        Initializes the scenario with data and sets up ATE and PNS dispatchers.

        Args:
            X: Treatment variable (array-like).
            Y: Outcome variable (array-like).
            Z: Optional instrument (array-like).
        """
        self.data = Data(X, Y, Z)
        self.ATE = AlgorithmDispatcher(self, 'ATE')
        self.PNS = AlgorithmDispatcher(self, 'PNS')

    def get_algorithms(self, query_type):
        """
        Returns a list of available algorithm names for a given query type.

        Args:
            query_type (str): Either 'ATE' or 'PNS'.

        Returns:
            list[str]: Names of supported algorithms.
        """
        return list(self.AVAILABLE_ALGORITHMS.get(query_type, {}).keys())


class AlgorithmDispatcher:
    """
    A dynamic dispatcher that exposes algorithms as methods via __getattr__.

    Attributes:
        scenario (Scenario): The scenario instance this dispatcher is bound to.
        query_type (str): The type of causal query ('ATE' or 'PNS').
    """

    def __init__(self, scenario, query_type):
        self.scenario = scenario
        self.query_type = query_type

    def __getattr__(self, name):
        """
        Dynamically resolves a method call to the appropriate algorithm class.

        Allows syntax like: scenario.ATE.manski() or scenario.PNS.entropybounds(theta=0.5)

        Args:
            name (str): Algorithm name (e.g., 'manski').

        Returns:
            Callable: A function that executes the bound algorithm with scenario data.
        """
        def _wrapped(*args, **kwargs):
            # Get the algorithm class and instantiate it
            cls = self.scenario.AVAILABLE_ALGORITHMS[self.query_type][name]()
            # Get the appropriate bound method (bound_ATE or bound_PNS)
            method = getattr(cls, f'bound_{self.query_type}')
            # Combine scenario data with any user-supplied kwargs
            combined_kwargs = {**self.scenario.data.unpack(), **kwargs}
            return method(*args, **combined_kwargs)

        return _wrapped

    def __dir__(self):
        """
        Adds available algorithm names to attribute suggestions (IntelliSense).

        Returns:
            list[str]: Default attributes + dynamically available algorithms.
        """
        base = super().__dir__()
        custom = list(self.scenario.AVAILABLE_ALGORITHMS.get(self.query_type, {}).keys())
        return base + custom
