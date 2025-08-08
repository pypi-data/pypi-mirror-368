import logging
from abc import ABC, abstractmethod
from causalboundingengine.utils.alg_util import AlgUtil

logger = logging.getLogger(__name__)

class Algorithm(ABC):
    def bound_ATE(self, *args, **kwargs) -> tuple[float, float]:
        failed = False
        try:
            lower, upper = self._compute_ATE(*args, **kwargs)
        except Exception as e:
            logger.warning("Failed to compute ATE bounds: %s", e)
            failed = True
            lower, upper = None, None

        return AlgUtil.flatten_bounds_to_trivial_ceils('ATE', lower, upper, failed)

    def bound_PNS(self, *args, **kwargs) -> tuple[float, float]:
        failed = False
        try:
            lower, upper = self._compute_PNS(*args, **kwargs)
        except Exception as e:
            logger.warning("Failed to compute PNS bounds: %s", e)
            failed = True
            lower, upper = None, None

        return AlgUtil.flatten_bounds_to_trivial_ceils('PNS', lower, upper, failed)

    def _compute_ATE(self, *args, **kwargs) -> tuple[float, float]:
        raise NotImplementedError("This algorithm does not implement ATE bounding.")

    def _compute_PNS(self, *args, **kwargs) -> tuple[float, float]:
        raise NotImplementedError("This algorithm does not implement PNS bounding.")
