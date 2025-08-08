from causalboundingengine.scenario import Scenario
from causalboundingengine.algorithms.tianpearl import TianPearl
from causalboundingengine.algorithms.manski import Manski
from causalboundingengine.algorithms.entropybounds import Entropybounds
from causalboundingengine.algorithms.zhangbareinboim import ZhangBareinboim
from causalboundingengine.algorithms.causaloptim import CausalOptim
from causalboundingengine.algorithms.zaffalonbounds import Zaffalonbounds
from causalboundingengine.algorithms.autobound import Autobound



## Collection of scenarios for the Causal Bounding Engine
## Consult the documentation for more details.

# Binary Confounding
class BinaryConf(Scenario):
    AVAILABLE_ALGORITHMS = {
        'ATE': {
            'manski': Manski,
            'entropybounds': Entropybounds,
            'causaloptim': CausalOptim,
            'zaffalonbounds': Zaffalonbounds,
            'autobound': Autobound
        },
        'PNS': {
            'tianpearl': TianPearl,
            'entropybounds': Entropybounds,
            'causaloptim': CausalOptim,
            'zaffalonbounds': Zaffalonbounds,
            'autobound': Autobound
        }
    }

# Binary Instrumental Variable
class BinaryIV(Scenario):
    AVAILABLE_ALGORITHMS = {
        'ATE': {
            'causaloptim': CausalOptim,
            'zaffalonbounds': Zaffalonbounds,
            'autobound': Autobound
        },
        'PNS': {
            'causaloptim': CausalOptim,
            'zaffalonbounds': Zaffalonbounds,
            'autobound': Autobound
        }
    }


# Continuous Instrumental Variable
class ContIV(Scenario):
    AVAILABLE_ALGORITHMS = {
        'ATE': {
            'zhangbareinboim': ZhangBareinboim
        }
    }