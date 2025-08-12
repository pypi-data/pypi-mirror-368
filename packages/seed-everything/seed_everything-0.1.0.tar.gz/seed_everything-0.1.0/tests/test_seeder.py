import unittest
import random
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seed_everything import seed_everything


class TestSeedEverything(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Store original PYTHONHASHSEED if it exists
        self.original_pythonhashseed = os.environ.get('PYTHONHASHSEED')
    
    def tearDown(self):
        """Clean up after each test method."""
        # Restore original PYTHONHASHSEED
        if self.original_pythonhashseed is not None:
            os.environ['PYTHONHASHSEED'] = self.original_pythonhashseed
        elif 'PYTHONHASHSEED' in os.environ:
            del os.environ['PYTHONHASHSEED']
    
    def test_sets_pythonhashseed(self):
        """Test that seed_everything sets PYTHONHASHSEED environment variable."""
        seed_everything(42)
        self.assertEqual(os.environ['PYTHONHASHSEED'], '42')
        
        seed_everything(123)
        self.assertEqual(os.environ['PYTHONHASHSEED'], '123')
    
    def test_default_seed_value(self):
        """Test that default seed value is 42."""
        seed_everything()
        self.assertEqual(os.environ['PYTHONHASHSEED'], '42')
    
    def test_seeds_random_module(self):
        """Test that seed_everything seeds the random module."""
        seed_everything(42)
        first_value = random.random()
        
        seed_everything(42)
        second_value = random.random()
        
        self.assertEqual(first_value, second_value)
    
    def test_reproducibility(self):
        """Test that seed_everything produces reproducible results."""
        seed_everything(42)
        random_values_1 = [random.random() for _ in range(5)]
        
        seed_everything(42)
        random_values_2 = [random.random() for _ in range(5)]
        
        self.assertEqual(random_values_1, random_values_2)
    
    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different random sequences."""
        seed_everything(42)
        values_seed_42 = [random.random() for _ in range(5)]
        
        seed_everything(100)
        values_seed_100 = [random.random() for _ in range(5)]
        
        self.assertNotEqual(values_seed_42, values_seed_100)
    
    @patch('seed_everything.seeder.is_imported')
    @patch('seed_everything.seeder.seed_numpy')
    @patch('seed_everything.seeder.seed_torch')
    @patch('seed_everything.seeder.seed_tensorflow')
    @patch('seed_everything.seeder.seed_jax')
    def test_conditional_seeding(self, mock_seed_jax, mock_seed_tf, 
                                mock_seed_torch, mock_seed_numpy, 
                                mock_is_imported):
        """Test that seed_everything only seeds imported libraries."""
        # Mock is_imported to return True only for numpy and torch
        def mock_is_imported_func(module_name):
            return module_name in ['numpy', 'torch']
        
        mock_is_imported.side_effect = mock_is_imported_func
        
        seed_everything(42)
        
        # Verify is_imported was called for each optional library
        expected_modules = ['numpy', 'torch', 'tensorflow', 'jax']
        actual_calls = [call[0][0] for call in mock_is_imported.call_args_list]
        self.assertEqual(set(expected_modules), set(actual_calls))
        
        # Verify only numpy and torch seed functions were called
        mock_seed_numpy.assert_called_once_with(42)
        mock_seed_torch.assert_called_once_with(42)
        mock_seed_tf.assert_not_called()
        mock_seed_jax.assert_not_called()
    
    @patch('seed_everything.seeder.is_imported')
    def test_no_optional_libraries_imported(self, mock_is_imported):
        """Test seed_everything when no optional libraries are imported."""
        mock_is_imported.return_value = False
        
        # Should not raise any errors
        seed_everything(42)
        
        # Should still set PYTHONHASHSEED and seed random
        self.assertEqual(os.environ['PYTHONHASHSEED'], '42')
    
    @patch('seed_everything.seeder.is_imported')
    def test_all_optional_libraries_imported(self, mock_is_imported):
        """Test seed_everything when all optional libraries are imported."""
        mock_is_imported.return_value = True
        
        with patch('seed_everything.seeder.seed_numpy') as mock_numpy, \
             patch('seed_everything.seeder.seed_torch') as mock_torch, \
             patch('seed_everything.seeder.seed_tensorflow') as mock_tf, \
             patch('seed_everything.seeder.seed_jax') as mock_jax:
            
            seed_everything(42)
            
            # All seed functions should be called
            mock_numpy.assert_called_once_with(42)
            mock_torch.assert_called_once_with(42)
            mock_tf.assert_called_once_with(42)
            mock_jax.assert_called_once_with(42)


if __name__ == '__main__':
    unittest.main()
