import numpy as np
import pytest
from causalboundingengine.algorithms.manski import Manski
from causalboundingengine.algorithms.tianpearl import TianPearl


class TestManskiAlgorithm:
    """Test Manski bounds algorithm directly."""
    
    def setup_method(self):
        """Set up test data."""
        self.X = np.array([0, 1, 1, 0, 1])
        self.Y = np.array([1, 0, 1, 0, 1])
        self.algorithm = Manski()
    
    def test_ate_computation(self):
        """Test ATE bound computation."""
        bounds = self.algorithm.bound_ATE(self.X, self.Y)
        
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]
        assert bounds[0] >= -1.0
        assert bounds[1] <= 1.0
    
    def test_pns_returns_trivial_bounds(self):
        """Test that PNS returns trivial bounds for Manski."""
        # Manski doesn't implement PNS, so it should return trivial bounds (0, 1)
        bounds = self.algorithm.bound_PNS(self.X, self.Y)
        assert bounds == (0.0, 1.0)
    
    def test_extreme_cases(self):
        """Test extreme data cases."""
        # All treated, all positive outcomes
        X_all_treated = np.array([1, 1, 1, 1])
        Y_all_one = np.array([1, 1, 1, 1])
        
        bounds = self.algorithm.bound_ATE(X_all_treated, Y_all_one)
        # When only treated samples, p1=1, p0=0 (default), so bounds are (0, 1)
        assert bounds == (0.0, 1.0)
        
        # All control, varied outcomes
        X_all_control = np.array([0, 0, 0, 0])
        Y_varied = np.array([1, 0, 1, 0])
        
        bounds = self.algorithm.bound_ATE(X_all_control, Y_varied)
        # When only control samples, p1=0 (default), p0=0.5, so bounds are (-1, 0.5)
        assert bounds == (-1.0, 0.5)


class TestTianPearlAlgorithm:
    """Test Tian-Pearl bounds algorithm directly."""
    
    def setup_method(self):
        """Set up test data."""
        self.X = np.array([0, 1, 1, 0, 1])
        self.Y = np.array([1, 0, 1, 0, 1])
        self.algorithm = TianPearl()
    
    def test_ate_computation(self):
        """Test ATE bound computation."""
        bounds = self.algorithm.bound_ATE(self.X, self.Y)
        
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]
        assert bounds[0] >= -1.0
        assert bounds[1] <= 1.0
    
    def test_pns_computation(self):
        """Test PNS bound computation."""
        bounds = self.algorithm.bound_PNS(self.X, self.Y)
        
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]
        assert bounds[0] >= 0.0  # PNS is in [0, 1]
        assert bounds[1] <= 1.0
    
    def test_bounds_tighter_than_manski(self):
        """Test that Tian-Pearl bounds are typically tighter than Manski."""
        # Use larger dataset for more reliable comparison
        np.random.seed(42)
        n = 200
        X = np.random.binomial(1, 0.3, n)
        Y = np.random.binomial(1, 0.6, n)
        
        manski = Manski()
        tianpearl = TianPearl()
        
        manski_bounds = manski.bound_ATE(X, Y)
        tianpearl_bounds = tianpearl.bound_ATE(X, Y)
        
        manski_width = manski_bounds[1] - manski_bounds[0]
        tianpearl_width = tianpearl_bounds[1] - tianpearl_bounds[0]
        
        # Tian-Pearl should generally be tighter (smaller width)
        assert tianpearl_width <= manski_width + 1e-10  # Small tolerance for numerical errors
    
    def test_consistent_results(self):
        """Test that results are consistent across multiple calls."""
        bounds1 = self.algorithm.bound_ATE(self.X, self.Y)
        bounds2 = self.algorithm.bound_ATE(self.X, self.Y)
        
        assert bounds1 == bounds2
        
        pns1 = self.algorithm.bound_PNS(self.X, self.Y)
        pns2 = self.algorithm.bound_PNS(self.X, self.Y)
        
        assert pns1 == pns2
