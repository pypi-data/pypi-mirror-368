import numpy as np
import pytest


def test_package_imports():
    """Test that core package components can be imported."""
    try:
        from causalboundingengine.scenario import Scenario
        from causalboundingengine.utils.data import Data
        from causalboundingengine.algorithms.manski import Manski
        from causalboundingengine.algorithms.tianpearl import TianPearl
        assert True, "Core imports successful"
    except ImportError as e:
        pytest.fail(f"Failed to import core package components: {e}")


def test_basic_data_structure():
    """Test basic data structure creation."""
    from causalboundingengine.utils.data import Data
    
    X = np.array([0, 1, 1, 0])
    Y = np.array([1, 0, 1, 1])
    
    data = Data(X, Y)
    assert hasattr(data, 'X')
    assert hasattr(data, 'Y')
    assert data.Z is None
    
    unpacked = data.unpack()
    assert 'X' in unpacked
    assert 'Y' in unpacked
    np.testing.assert_array_equal(unpacked['X'], X)
    np.testing.assert_array_equal(unpacked['Y'], Y)


def test_manski_basic():
    """Test basic Manski algorithm functionality."""
    from causalboundingengine.algorithms.manski import Manski
    
    X = np.array([0, 1, 1, 0])
    Y = np.array([1, 0, 1, 1])
    
    alg = Manski()
    bounds = alg.bound_ATE(X=X, Y=Y)
    
    assert isinstance(bounds, tuple)
    assert len(bounds) == 2
    assert bounds[0] <= bounds[1], "Lower bound should be <= upper bound"
    assert -1 <= bounds[0] <= 1, "Bounds should be in [-1, 1]"
    assert -1 <= bounds[1] <= 1, "Bounds should be in [-1, 1]"


def test_scenario_integration():
    """Test BinaryConf scenario with Manski algorithm."""
    try:
        from causalboundingengine.scenarios import BinaryConf
        
        X = np.array([0, 1, 1, 0])
        Y = np.array([1, 0, 1, 1])
        
        scenario = BinaryConf(X, Y)
        
        # Test that scenario has required attributes
        assert hasattr(scenario, 'ATE')
        assert hasattr(scenario, 'PNS')
        assert hasattr(scenario, 'data')
        
        # Test Manski bounds
        bounds = scenario.ATE.manski()
        
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]
        
    except ImportError as e:
        pytest.skip(f"Skipping scenario test due to missing dependencies: {e}")
    except Exception as e:
        pytest.fail(f"Scenario integration test failed: {e}")