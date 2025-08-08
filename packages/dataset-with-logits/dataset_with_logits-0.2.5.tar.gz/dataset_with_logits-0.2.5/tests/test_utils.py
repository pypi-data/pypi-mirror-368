"""
Tests for the dataset utilities.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from dataset_with_logits.utils import (construct_filename,
                                       construct_github_url,
                                       list_available_models,
                                       validate_predictions_file)


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_list_available_models(self):
        """Test listing available models."""
        models = list_available_models()
        
        self.assertIsInstance(models, dict)
        self.assertIn('imagenet1k', models)
        self.assertIn('resnet18', models['imagenet1k'])
        
        # Test specific dataset
        imagenet_models = list_available_models('imagenet1k')
        self.assertIn('imagenet1k', imagenet_models)
        self.assertIn('resnet18', imagenet_models['imagenet1k'])
        
        # Test invalid dataset
        with self.assertRaises(ValueError):
            list_available_models('invalid_dataset')
    
    def test_construct_filename(self):
        """Test filename construction."""
        filename = construct_filename('imagenet1k', 'resnet18', 'v0.1.0')
        expected = 'resnet18-imagenet1k-v0.1.0.csv'
        self.assertEqual(filename, expected)
        
        filename = construct_filename('cifar10', 'vit_b_16', 'v1.0.0')
        expected = 'vit_b_16-cifar10-v1.0.0.csv'
        self.assertEqual(filename, expected)
    
    def test_construct_github_url(self):
        """Test GitHub URL construction."""
        url = construct_github_url('imagenet1k', 'resnet18', 'v0.1.0')
        
        self.assertIn('github.com', url)
        self.assertIn('ViGeng/predictions-on-datasets', url)
        self.assertIn('resnet18-imagenet1k-v0.1.0.csv', url)
        self.assertIn('/raw/main/', url)
    
    def test_validate_predictions_file_not_exists(self):
        """Test validation of non-existent file."""
        with self.assertRaises(FileNotFoundError):
            validate_predictions_file('/nonexistent/file.csv')
    
    def test_validate_predictions_file_valid(self):
        """Test validation of valid predictions file."""
        # Create temporary valid CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('id,label,logits\n')
            f.write('image1,0,1.0;2.0;3.0\n')
            f.write('image2,1,0.5;1.5;2.5\n')
            temp_file = f.name
        
        try:
            result = validate_predictions_file(temp_file)
            
            self.assertTrue(result['validation_passed'])
            self.assertEqual(result['num_samples'], 2)
            self.assertIn('id', result['columns'])
            self.assertIn('logits', result['columns'])
            self.assertTrue(result['has_labels'])
            self.assertEqual(result['logits_dimension'], 3)
            
        finally:
            os.unlink(temp_file)
    
    def test_validate_predictions_file_invalid(self):
        """Test validation of invalid predictions file."""
        # Create temporary invalid CSV (missing required columns)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('wrong_column,other_column\n')
            f.write('value1,value2\n')
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError):
                validate_predictions_file(temp_file)
                
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()
