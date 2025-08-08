"""Test scenario classes and their interfaces."""

import numpy as np
import pytest


class TestDataClass:
    """Test the Data class."""
    
    def test_data_creation(self):
        """Test basic Data class creation."""
        from causalboundingengine.utils.data import Data
        
        X = np.array([0, 1, 1, 0])
        Y = np.array([1, 0, 1, 1])
        
        data = Data(X, Y)
        
        assert hasattr(data, 'X')
        assert hasattr(data, 'Y')
        assert hasattr(data, 'Z')
        assert data.Z is None
        
        np.testing.assert_array_equal(data.X, X)
        np.testing.assert_array_equal(data.Y, Y)
    
    def test_data_with_instrument(self):
        """Test Data class with instrument."""
        from causalboundingengine.utils.data import Data
        
        X = np.array([0, 1, 1, 0])
        Y = np.array([1, 0, 1, 1])
        Z = np.array([1, 1, 0, 0])
        
        data = Data(X, Y, Z)
        
        assert data.Z is not None
        np.testing.assert_array_equal(data.Z, Z)
    
    def test_data_unpack(self):
        """Test unpacking data."""
        from causalboundingengine.utils.data import Data
        
        X = np.array([0, 1, 1, 0])
        Y = np.array([1, 0, 1, 1])
        
        # Without instrument
        data = Data(X, Y)
        unpacked = data.unpack()
        
        assert isinstance(unpacked, dict)
        assert 'X' in unpacked
        assert 'Y' in unpacked
        assert 'Z' not in unpacked
        
        # With instrument
        Z = np.array([1, 1, 0, 0])
        data_z = Data(X, Y, Z)
        unpacked_z = data_z.unpack()
        
        assert 'X' in unpacked_z
        assert 'Y' in unpacked_z
        assert 'Z' in unpacked_z


class TestScenarioBase:
    """Test base scenario functionality."""
    
    def test_scenario_creation(self):
        """Test basic scenario creation."""
        from causalboundingengine.scenario import Scenario
        
        X = np.array([0, 1, 1, 0])
        Y = np.array([1, 0, 1, 1])
        
        scenario = Scenario(X, Y)
        assert hasattr(scenario, 'data')
        assert hasattr(scenario, 'ATE')
        assert hasattr(scenario, 'PNS')
    
    def test_algorithm_dispatcher(self):
        """Test AlgorithmDispatcher functionality."""
        from causalboundingengine.scenario import AlgorithmDispatcher, Scenario
        
        X = np.array([0, 1, 1, 0])
        Y = np.array([1, 0, 1, 1])
        
        scenario = Scenario(X, Y)
        dispatcher = AlgorithmDispatcher(scenario, 'ATE')
        
        assert hasattr(dispatcher, 'scenario')
        assert hasattr(dispatcher, 'query_type')
        assert dispatcher.query_type == 'ATE'


class TestBinaryConfScenario:
    """Test BinaryConf scenario."""
    
    def test_binaryconf_creation(self):
        """Test BinaryConf scenario creation."""
        try:
            from causalboundingengine.scenarios import BinaryConf
            
            X = np.array([0, 1, 1, 0])
            Y = np.array([1, 0, 1, 1])
            
            scenario = BinaryConf(X, Y)
            
            assert hasattr(scenario, 'data')
            assert hasattr(scenario, 'ATE')
            assert hasattr(scenario, 'PNS')
            assert hasattr(scenario, 'AVAILABLE_ALGORITHMS')
            
            # Check algorithm availability
            assert 'ATE' in scenario.AVAILABLE_ALGORITHMS
            assert 'PNS' in scenario.AVAILABLE_ALGORITHMS
            assert 'manski' in scenario.AVAILABLE_ALGORITHMS['ATE']
            assert 'tianpearl' in scenario.AVAILABLE_ALGORITHMS['ATE']
            
        except ImportError as e:
            pytest.skip(f"Skipping BinaryConf test due to missing dependencies: {e}")
    
    def test_binaryconf_manski_integration(self):
        """Test BinaryConf with Manski algorithm."""
        try:
            from causalboundingengine.scenarios import BinaryConf
            
            X = np.array([0, 1, 1, 0])
            Y = np.array([1, 0, 1, 1])
            
            scenario = BinaryConf(X, Y)
            
            # Test Manski bounds
            bounds = scenario.ATE.manski()
            
            assert isinstance(bounds, tuple)
            assert len(bounds) == 2
            assert bounds[0] <= bounds[1]
            
        except ImportError as e:
            pytest.skip(f"Skipping BinaryConf integration test due to missing dependencies: {e}")
    
    def test_get_algorithms(self):
        """Test getting available algorithms."""
        try:
            from causalboundingengine.scenarios import BinaryConf
            
            X = np.array([0, 1, 1, 0])
            Y = np.array([1, 0, 1, 1])
            
            scenario = BinaryConf(X, Y)
            
            ate_algorithms = scenario.get_algorithms('ATE')
            pns_algorithms = scenario.get_algorithms('PNS')
            
            assert isinstance(ate_algorithms, list)
            assert isinstance(pns_algorithms, list)
            assert 'manski' in ate_algorithms
            assert 'tianpearl' in ate_algorithms
            
        except ImportError as e:
            pytest.skip(f"Skipping algorithm list test due to missing dependencies: {e}")


class TestIVScenarios:
    """Test IV scenarios if available."""
    
    def test_binary_iv_creation(self):
        """Test BinaryIV scenario creation."""
        try:
            from causalboundingengine.scenarios import BinaryIV
            
            X = np.array([0, 1, 1, 0])
            Y = np.array([1, 0, 1, 1])
            Z = np.array([1, 1, 0, 0])
            
            scenario = BinaryIV(X, Y, Z)
            
            assert hasattr(scenario, 'data')
            assert hasattr(scenario, 'ATE')
            assert hasattr(scenario, 'PNS')
            assert scenario.data.Z is not None
            
        except ImportError as e:
            pytest.skip(f"Skipping BinaryIV test due to missing dependencies: {e}")
    
    def test_cont_iv_creation(self):
        """Test ContIV scenario creation."""
        try:
            from causalboundingengine.scenarios import ContIV
            
            X = np.array([0, 1, 1, 0])
            Y = np.array([0.1, 0.9, 0.8, 0.2])  # Continuous outcome
            Z = np.array([1, 1, 0, 0])
            
            scenario = ContIV(X, Y, Z)
            
            assert hasattr(scenario, 'data')
            assert hasattr(scenario, 'ATE')
            assert hasattr(scenario, 'PNS')
            assert scenario.data.Z is not None
            
            # ContIV should have zhangbareinboim algorithm
            ate_algorithms = scenario.get_algorithms('ATE')
            assert 'zhangbareinboim' in ate_algorithms
            
        except ImportError as e:
            pytest.skip(f"Skipping ContIV test due to missing dependencies: {e}")
