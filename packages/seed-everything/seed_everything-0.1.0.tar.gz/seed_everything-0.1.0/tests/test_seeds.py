import unittest
import random
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seed_everything.seeds import is_imported, seed_random


class TestSeedsModule(unittest.TestCase):
    
    def test_is_imported_existing_module(self):
        """Test is_imported with modules that should exist."""
        self.assertTrue(is_imported('sys'))
        self.assertTrue(is_imported('os'))
        self.assertTrue(is_imported('random'))
    
    def test_is_imported_nonexistent_module(self):
        """Test is_imported with non-existent module."""
        self.assertFalse(is_imported('nonexistent_module_xyz123'))
    
    def test_seed_random_reproducibility(self):
        """Test that seed_random produces reproducible results."""
        seed_random(42)
        first_value = random.random()
        
        seed_random(42)
        second_value = random.random()
        
        self.assertEqual(first_value, second_value)
    
    def test_seed_random_different_seeds(self):
        """Test that different seeds produce different results."""
        seed_random(42)
        value_42 = random.random()
        
        seed_random(100)
        value_100 = random.random()
        
        self.assertNotEqual(value_42, value_100)


class TestOptionalLibrarySeeding(unittest.TestCase):
    """Test seeding functions for optional libraries using mocks."""
    
    def test_seed_numpy_mock(self):
        """Test seed_numpy with mocked numpy."""
        with patch.dict('sys.modules', {'numpy': MagicMock()}):
            from seed_everything.seeds import seed_numpy
            
            # Get the mocked numpy module
            import sys
            mock_numpy = sys.modules['numpy']
            
            seed_numpy(42)
            
            mock_numpy.random.seed.assert_called_once_with(42)
    
    def test_seed_torch_mock_no_cuda(self):
        """Test seed_torch with mocked torch (no CUDA)."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        with patch.dict('sys.modules', {'torch': mock_torch}):
            from seed_everything.seeds import seed_torch
            
            seed_torch(42)
            
            mock_torch.manual_seed.assert_called_once_with(42)
            mock_torch.cuda.is_available.assert_called_once()
            # CUDA functions should not be called
            mock_torch.cuda.manual_seed.assert_not_called()
            mock_torch.cuda.manual_seed_all.assert_not_called()
    
    def test_seed_torch_mock_with_cuda(self):
        """Test seed_torch with mocked torch (with CUDA)."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        
        with patch.dict('sys.modules', {'torch': mock_torch}):
            from seed_everything.seeds import seed_torch
            
            seed_torch(42)
            
            mock_torch.manual_seed.assert_called_once_with(42)
            mock_torch.cuda.manual_seed.assert_called_once_with(42)
            mock_torch.cuda.manual_seed_all.assert_called_once_with(42)
            self.assertTrue(mock_torch.backends.cudnn.deterministic)
            self.assertFalse(mock_torch.backends.cudnn.benchmark)
    
    def test_seed_tensorflow_mock(self):
        """Test seed_tensorflow with mocked tensorflow."""
        mock_tf = MagicMock()
        
        with patch.dict('sys.modules', {'tensorflow': mock_tf}):
            from seed_everything.seeds import seed_tensorflow
            
            seed_tensorflow(42)
            
            mock_tf.random.set_seed.assert_called_once_with(42)
    
    def test_seed_jax_mock(self):
        """Test seed_jax with mocked jax."""
        mock_jax = MagicMock()
        
        with patch.dict('sys.modules', {'jax': mock_jax}):
            from seed_everything.seeds import seed_jax
            
            seed_jax(42)
            
            mock_jax.random.PRNGKey.assert_called_once_with(42)


if __name__ == '__main__':
    unittest.main()
