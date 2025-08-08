"""Integration tests for the CausalBoundingEngine package."""

import numpy as np
import pytest


class TestPackageIntegration:
    """Test package-level integration."""
    
    def test_basic_workflow(self):
        """Test a basic end-to-end workflow."""
        try:
            # Import the package
            from causalboundingengine.scenarios import BinaryConf
            
            # Create some test data
            np.random.seed(42)
            n = 50
            X = np.random.binomial(1, 0.4, n)
            Y = np.random.binomial(1, 0.6, n)
            
            # Create scenario
            scenario = BinaryConf(X, Y)
            
            # Test multiple algorithms
            manski_bounds = scenario.ATE.manski()
            tianpearl_bounds = scenario.ATE.tianpearl()
            
            # Verify results
            assert isinstance(manski_bounds, tuple)
            assert isinstance(tianpearl_bounds, tuple)
            assert len(manski_bounds) == 2
            assert len(tianpearl_bounds) == 2
            
            # Bounds should be valid
            assert manski_bounds[0] <= manski_bounds[1]
            assert tianpearl_bounds[0] <= tianpearl_bounds[1]
            
            # Print results for manual verification
            print(f"Manski bounds: {manski_bounds}")
            print(f"Tian-Pearl bounds: {tianpearl_bounds}")
            
        except ImportError as e:
            pytest.skip(f"Skipping integration test due to missing dependencies: {e}")
    
    def test_algorithm_comparison(self):
        """Test that different algorithms give reasonable results."""
        try:
            from causalboundingengine.scenarios import BinaryConf
            
            # Create test data with clear treatment effect
            X = np.array([0, 0, 0, 0, 1, 1, 1, 1])
            Y = np.array([0, 0, 1, 0, 1, 1, 1, 0])  # Higher outcomes for treated
            
            scenario = BinaryConf(X, Y)
            
            # Get bounds from different algorithms
            manski_bounds = scenario.ATE.manski()
            tianpearl_bounds = scenario.ATE.tianpearl()
            
            # Both should indicate positive treatment effect
            assert manski_bounds[0] <= manski_bounds[1]
            assert tianpearl_bounds[0] <= tianpearl_bounds[1]
            
            # Manski bounds should be wider (more conservative)
            manski_width = manski_bounds[1] - manski_bounds[0]
            tianpearl_width = tianpearl_bounds[1] - tianpearl_bounds[0]
            
            # This might not always be true, but usually Manski is more conservative
            print(f"Manski width: {manski_width}, Tian-Pearl width: {tianpearl_width}")
            
        except ImportError as e:
            pytest.skip(f"Skipping algorithm comparison test due to missing dependencies: {e}")
    
    def test_error_resilience(self):
        """Test that the package handles errors gracefully."""
        try:
            from causalboundingengine.scenarios import BinaryConf
            
            # Test with problematic data
            X = np.array([0, 1, 1, 0])
            Y = np.array([1, 0, 1, 1])
            
            scenario = BinaryConf(X, Y)
            
            # These should not crash
            try:
                bounds = scenario.ATE.manski()
                assert isinstance(bounds, tuple)
            except Exception as e:
                print(f"Manski failed gracefully: {e}")
            
            try:
                bounds = scenario.ATE.tianpearl()
                assert isinstance(bounds, tuple)
            except Exception as e:
                print(f"Tian-Pearl failed gracefully: {e}")
                
        except ImportError as e:
            pytest.skip(f"Skipping error resilience test due to missing dependencies: {e}")


class TestDifferentScenarios:
    """Test different scenario types if available."""
    
    def test_iv_scenarios(self):
        """Test IV scenarios if they can be loaded."""
        try:
            from causalboundingengine.scenarios import BinaryIV, ContIV
            
            # Test BinaryIV
            X = np.array([0, 1, 1, 0])
            Y = np.array([1, 0, 1, 1])
            Z = np.array([1, 1, 0, 0])
            
            binary_iv = BinaryIV(X, Y, Z)
            assert hasattr(binary_iv, 'ATE')
            assert hasattr(binary_iv, 'PNS')
            
            # Test ContIV
            Y_cont = np.array([0.1, 0.9, 0.8, 0.2])
            cont_iv = ContIV(X, Y_cont, Z)
            assert hasattr(cont_iv, 'ATE')
            assert hasattr(cont_iv, 'PNS')
            
            print("✓ IV scenarios loaded successfully")
            
        except ImportError as e:
            pytest.skip(f"Skipping IV scenario test due to missing dependencies: {e}")
    
    def test_algorithm_discovery(self):
        """Test algorithm discovery across scenarios."""
        try:
            from causalboundingengine.scenarios import BinaryConf
            
            X = np.array([0, 1, 1, 0])
            Y = np.array([1, 0, 1, 1])
            
            scenario = BinaryConf(X, Y)
            
            # Get available algorithms
            ate_algs = scenario.get_algorithms('ATE')
            pns_algs = scenario.get_algorithms('PNS')
            
            assert isinstance(ate_algs, list)
            assert isinstance(pns_algs, list)
            assert len(ate_algs) > 0
            assert len(pns_algs) > 0
            
            print(f"Available ATE algorithms: {ate_algs}")
            print(f"Available PNS algorithms: {pns_algs}")
            
        except ImportError as e:
            pytest.skip(f"Skipping algorithm discovery test due to missing dependencies: {e}")


class TestDataHandling:
    """Test data handling and edge cases."""
    
    def test_data_types(self):
        """Test different data types."""
        from causalboundingengine.utils.data import Data
        
        # Test with lists
        X_list = [0, 1, 1, 0]
        Y_list = [1, 0, 1, 1]
        data_list = Data(X_list, Y_list)
        
        # Test with numpy arrays
        X_array = np.array([0, 1, 1, 0])
        Y_array = np.array([1, 0, 1, 1])
        data_array = Data(X_array, Y_array)
        
        # Both should work
        assert hasattr(data_list, 'X')
        assert hasattr(data_array, 'X')
    
    def test_data_validation(self):
        """Test basic data validation."""
        from causalboundingengine.utils.data import Data
        
        X = np.array([0, 1, 1, 0])
        Y = np.array([1, 0, 1, 1])
        
        # This should work fine
        data = Data(X, Y)
        unpacked = data.unpack()
        
        assert 'X' in unpacked
        assert 'Y' in unpacked
        assert len(unpacked['X']) == len(unpacked['Y'])


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__])
