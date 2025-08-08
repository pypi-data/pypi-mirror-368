"""Test core algorithms that don't require heavy dependencies."""

import numpy as np
import pytest


class TestManski:
    """Test Manski bounds algorithm."""
    
    def test_manski_basic(self):
        """Test basic Manski functionality."""
        from causalboundingengine.algorithms.manski import Manski
        
        X = np.array([0, 1, 1, 0])
        Y = np.array([1, 0, 1, 1])
        
        alg = Manski()
        bounds = alg.bound_ATE(X=X, Y=Y)
        
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]
        assert -1 <= bounds[0] <= 1
        assert -1 <= bounds[1] <= 1
    
    def test_manski_edge_cases(self):
        """Test Manski with edge cases."""
        from causalboundingengine.algorithms.manski import Manski
        
        alg = Manski()
        
        # All treated
        X = np.array([1, 1, 1, 1])
        Y = np.array([1, 0, 1, 0])
        bounds = alg.bound_ATE(X=X, Y=Y)
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        
        # All control
        X = np.array([0, 0, 0, 0])
        Y = np.array([1, 0, 1, 0])
        bounds = alg.bound_ATE(X=X, Y=Y)
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
    
    def test_manski_consistent_data(self):
        """Test Manski with realistic data."""
        from causalboundingengine.algorithms.manski import Manski
        
        # Create realistic binary treatment/outcome data
        np.random.seed(42)
        n = 100
        X = np.random.binomial(1, 0.5, n)
        Y = np.random.binomial(1, 0.6, n)  # outcome probability
        
        alg = Manski()
        bounds = alg.bound_ATE(X=X, Y=Y)
        
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]
        assert -1 <= bounds[0] <= 1
        assert -1 <= bounds[1] <= 1


class TestTianPearl:
    """Test Tian-Pearl bounds algorithm."""
    
    def test_tianpearl_basic(self):
        """Test basic Tian-Pearl functionality."""
        from causalboundingengine.algorithms.tianpearl import TianPearl
        
        X = np.array([0, 1, 1, 0])
        Y = np.array([1, 0, 1, 1])
        
        alg = TianPearl()
        bounds = alg.bound_ATE(X=X, Y=Y)
        
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]
    
    def test_tianpearl_pns_functionality(self):
        """Test that Tian-Pearl can compute PNS bounds."""
        from causalboundingengine.algorithms.tianpearl import TianPearl
        
        X = np.array([0, 1, 1, 0])
        Y = np.array([1, 0, 1, 1])
        
        alg = TianPearl()
        
        # Tian-Pearl should be able to compute PNS bounds
        bounds = alg.bound_PNS(X=X, Y=Y)
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] <= bounds[1]


class TestAlgorithmInterface:
    """Test the base algorithm interface."""
    
    def test_bound_methods_exist(self):
        """Test that bound methods exist on concrete algorithms."""
        from causalboundingengine.algorithms.manski import Manski
        
        alg = Manski()
        assert hasattr(alg, 'bound_ATE')
        assert hasattr(alg, 'bound_PNS')
        assert callable(alg.bound_ATE)
        assert callable(alg.bound_PNS)
    
    def test_error_handling(self):
        """Test error handling in algorithms."""
        from causalboundingengine.algorithms.manski import Manski
        
        alg = Manski()
        
        # Test with invalid data (should handle gracefully)
        X = np.array([])
        Y = np.array([])
        
        # Should return trivial bounds without crashing
        bounds = alg.bound_ATE(X=X, Y=Y)
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
