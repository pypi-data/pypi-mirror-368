import numpy as np
import pytest
from causalboundingengine.scenarios import BinaryIV, ContIV


class TestBinaryIVScenario:
    """Test BinaryIV scenario for instrumental variable analysis."""
    
    def setup_method(self):
        """Set up test data."""
        # IV data with some correlation structure
        np.random.seed(42)
        n = 50
        
        # Generate correlated Z, X, Y
        self.Z = np.random.binomial(1, 0.5, n)  # Instrument
        self.X = np.random.binomial(1, 0.3 + 0.4 * self.Z, n)  # Treatment influenced by Z
        self.Y = np.random.binomial(1, 0.4 + 0.3 * self.X, n)  # Outcome influenced by X
    
    def test_scenario_creation(self):
        """Test BinaryIV scenario creation."""
        scenario = BinaryIV(self.X, self.Y, self.Z)
        assert scenario is not None
        assert len(scenario.data.X) == len(self.X)
        assert len(scenario.data.Y) == len(self.Y)
        assert len(scenario.data.Z) == len(self.Z)
    
    def test_autobound_algorithm(self):
        """Test AutoBound algorithm in IV setting."""
        scenario = BinaryIV(self.X, self.Y, self.Z)
        
        # AutoBound should be available for IV scenarios
        assert 'autobound' in scenario.get_algorithms('ATE')
        
        bounds = scenario.ATE.autobound()
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]
        assert bounds[0] >= -1.0
        assert bounds[1] <= 1.0
    
    def test_invalid_iv_data(self):
        """Test error handling with invalid IV data."""
        # Mismatched lengths
        Z_bad = np.array([0, 1])
        X_good = np.array([0, 1, 1])
        Y_good = np.array([1, 0, 1])
        
        with pytest.raises(ValueError):
            BinaryIV(X_good, Y_good, Z_bad)


class TestContIVScenario:
    """Test ContIV scenario for continuous outcomes."""
    
    def setup_method(self):
        """Set up test data."""
        # Binary instrument and treatment with continuous outcome
        self.Z = np.array([0, 1, 1, 0, 1])  # Binary instrument
        self.X = np.array([0, 1, 1, 0, 1])  # Binary treatment
        self.Y = np.array([0.1, 0.8, 0.6, 0.2, 0.9])  # Continuous outcome [0,1]
    
    def test_scenario_creation(self):
        """Test ContIV scenario creation."""
        scenario = ContIV(self.X, self.Y, self.Z)
        assert scenario is not None
        assert len(scenario.data.X) == len(self.X)
        assert len(scenario.data.Y) == len(self.Y)
        assert len(scenario.data.Z) == len(self.Z)
    
    def test_zhangbareinboim_algorithm(self):
        """Test Zhang-Bareinboim algorithm."""
        scenario = ContIV(self.X, self.Y, self.Z)
        
        # Zhang-Bareinboim should be available
        assert 'zhangbareinboim' in scenario.get_algorithms('ATE')
        
        bounds = scenario.ATE.zhangbareinboim()
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]
    
    def test_continuous_outcome_bounds(self):
        """Test that continuous outcomes are properly handled."""
        # Y values should be in [0, 1] for ContIV
        Y_good = np.array([0.0, 0.5, 1.0, 0.3, 0.7])
        scenario = ContIV(self.X, Y_good, self.Z)
        
        # Should work without errors
        bounds = scenario.ATE.zhangbareinboim()
        assert isinstance(bounds, tuple)
    
    def test_out_of_bounds_outcome(self):
        """Test handling of outcome values outside [0,1]."""
        # Y values outside [0, 1] - should still work but may not be optimal
        Y_outside = np.array([-0.1, 1.5, 0.5, 0.3, 0.7])
        scenario = ContIV(self.X, Y_outside, self.Z)
        
        # Should not crash, though results may not be meaningful
        bounds = scenario.ATE.zhangbareinboim()
        assert isinstance(bounds, tuple)
