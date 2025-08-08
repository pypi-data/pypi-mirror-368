"""
Tests for dataset-with-logits package.
"""

import gzip
import os
import tempfile

import pandas as pd
import pytest
import torch
import torchvision.transforms as transforms

from dataset_with_logits import ImageNet, list_available_models
from dataset_with_logits.utils.download import (construct_filename,
                                                construct_github_url)


def create_mock_predictions_file(file_path, num_samples=10, num_classes=1000):
    """Create a mock predictions file for testing."""
    data = []
    for i in range(num_samples):
        logits = [f"{torch.randn(1).item():.6f}" for _ in range(num_classes)]
        logits_str = ";".join(logits)
        data.append({
            'id': f'ILSVRC2012_val_{i:08d}',
            'label': i % num_classes,
            'logits': logits_str
        })
    
    df = pd.DataFrame(data)
    
    if file_path.endswith('.gz'):
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            df.to_csv(f, index=False)
    else:
        df.to_csv(file_path, index=False)


def create_mock_imagenet_structure(root_dir, num_classes=5, samples_per_class=3):
    """Create a mock ImageNet directory structure for testing."""
    os.makedirs(root_dir, exist_ok=True)
    
    for class_idx in range(num_classes):
        class_dir = os.path.join(root_dir, f'class_{class_idx:03d}')
        os.makedirs(class_dir, exist_ok=True)
        
        for sample_idx in range(samples_per_class):
            # Create a simple white image file
            from PIL import Image
            img = Image.new('RGB', (224, 224), color='white')
            img_path = os.path.join(class_dir, f'ILSVRC2012_val_{class_idx * samples_per_class + sample_idx:08d}.JPEG')
            img.save(img_path)


class TestUtils:
    """Test utility functions."""
    
    def test_list_available_models(self):
        """Test listing available models."""
        models = list_available_models()
        
        assert isinstance(models, dict)
        assert 'imagenet1k' in models
        assert 'resnet18' in models['imagenet1k']
        assert 'vit_l_16' in models['imagenet1k']
    
    def test_construct_filename(self):
        """Test filename construction."""
        filename = construct_filename('imagenet1k', 'resnet18', 'val', 'v0.1.0')
        expected = 'resnet18-IMAGENET1K_V1-imagenet1k-val.csv.gz'
        assert filename == expected
    
    def test_construct_github_url(self):
        """Test GitHub URL construction."""
        url = construct_github_url('imagenet1k', 'resnet18', 'val', 'v0.1.0')
        expected_parts = [
            'https://github.com/ViGeng/predictions-on-datasets/raw/main',
            'dataset_processing/predictions/imagenet1k/val',
            'resnet18-IMAGENET1K_V1-imagenet1k-val.csv.gz'
        ]
        expected = '/'.join(expected_parts)
        assert url == expected


class TestValidation:
    """Test validation utilities."""
    
    def test_validate_csv_file(self):
        """Test validating a CSV predictions file."""
        # Import validation locally
        from dataset_with_logits.utils.validation import \
            validate_predictions_file
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            create_mock_predictions_file(f.name, num_samples=5, num_classes=10)
            
            result = validate_predictions_file(f.name)
            
            assert result['valid'] is True
            assert result['num_predictions'] == 5
            assert result['num_classes'] == 10
            assert 'id' in result['columns']
            assert 'logits' in result['columns']
            
            os.unlink(f.name)
    
    def test_validate_gzipped_file(self):
        """Test validating a gzipped CSV predictions file."""
        # Import validation locally
        from dataset_with_logits.utils.validation import \
            validate_predictions_file
        
        with tempfile.NamedTemporaryFile(suffix='.csv.gz', delete=False) as f:
            create_mock_predictions_file(f.name, num_samples=5, num_classes=10)
            
            result = validate_predictions_file(f.name)
            
            assert result['valid'] is True
            assert result['num_predictions'] == 5
            assert result['num_classes'] == 10
            
            os.unlink(f.name)
    
    def test_validate_invalid_file(self):
        """Test validating an invalid predictions file."""
        # Import validation locally
        from dataset_with_logits.utils.validation import \
            validate_predictions_file
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Create invalid CSV (missing required columns)
            df = pd.DataFrame({'wrong_column': [1, 2, 3]})
            df.to_csv(f.name, index=False)
            
            result = validate_predictions_file(f.name)
            
            assert result['valid'] is False
            assert 'error' in result
            
            os.unlink(f.name)


class TestImageNetDataset:
    """Test ImageNet dataset class."""
    
    def test_dataset_creation_without_download(self):
        """Test creating dataset without auto-download."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock ImageNet structure
            imagenet_dir = os.path.join(temp_dir, 'imagenet')
            create_mock_imagenet_structure(imagenet_dir, num_classes=3, samples_per_class=2)
            
            # Create mock predictions file
            predictions_file = os.path.join(temp_dir, 'resnet18-IMAGENET1K_V1-imagenet1k-val.csv.gz')
            create_mock_predictions_file(predictions_file, num_samples=6, num_classes=1000)
            
            # Create dataset
            dataset = ImageNet(
                root=imagenet_dir,
                model='resnet18',
                split='val',
                auto_download=False,
                cache_dir=temp_dir
            )
            
            assert len(dataset) == 6  # 3 classes * 2 samples
            assert dataset.model == 'resnet18'
            assert dataset.split == 'val'
    
    def test_dataset_getitem(self):
        """Test getting items from dataset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock ImageNet structure
            imagenet_dir = os.path.join(temp_dir, 'imagenet')
            create_mock_imagenet_structure(imagenet_dir, num_classes=2, samples_per_class=1)
            
            # Create mock predictions file with specific IDs
            predictions_file = os.path.join(temp_dir, 'resnet18-IMAGENET1K_V1-imagenet1k-val.csv.gz')
            create_mock_predictions_file(predictions_file, num_samples=2, num_classes=1000)
            
            # Create dataset with transforms
            transform = transforms.Compose([
                transforms.ToTensor(),
            ])
            
            dataset = ImageNet(
                root=imagenet_dir,
                model='resnet18',
                transform=transform,
                auto_download=False,
                cache_dir=temp_dir
            )
            
            # Test getting an item
            image, label, logits = dataset[0]
            
            assert isinstance(image, torch.Tensor)
            assert image.shape == (3, 224, 224)  # RGB image tensor
            assert isinstance(label, int)
            assert isinstance(logits, torch.Tensor)
            assert logits.shape == (1000,)  # ImageNet has 1000 classes
    
    def test_dataset_info(self):
        """Test getting dataset info."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock setup
            imagenet_dir = os.path.join(temp_dir, 'imagenet')
            create_mock_imagenet_structure(imagenet_dir, num_classes=2, samples_per_class=1)
            
            predictions_file = os.path.join(temp_dir, 'resnet18-IMAGENET1K_V1-imagenet1k-val.csv.gz')
            create_mock_predictions_file(predictions_file, num_samples=2, num_classes=1000)
            
            dataset = ImageNet(
                root=imagenet_dir,
                model='resnet18',
                auto_download=False,
                cache_dir=temp_dir
            )
            
            info = dataset.get_info()
            
            assert info['dataset'] == 'imagenet1k'
            assert info['model'] == 'resnet18'
            assert info['num_predictions'] == 2
            assert info['num_images'] == 2
            assert 'resnet18' in info['available_models']


def test_integration():
    """Integration test with real-like scenario."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create realistic mock setup
        imagenet_dir = os.path.join(temp_dir, 'imagenet')
        create_mock_imagenet_structure(imagenet_dir, num_classes=10, samples_per_class=5)
        
        predictions_file = os.path.join(temp_dir, 'resnet18-IMAGENET1K_V1-imagenet1k-val.csv.gz')
        create_mock_predictions_file(predictions_file, num_samples=50, num_classes=1000)
        
        # Create dataset
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        dataset = ImageNet(
            root=imagenet_dir,
            model='resnet18',
            transform=transform,
            auto_download=False,
            cache_dir=temp_dir
        )
        
        # Test with DataLoader
        from torch.utils.data import DataLoader
        
        loader = DataLoader(dataset, batch_size=8, shuffle=True)
        
        for images, labels, logits in loader:
            assert images.shape[0] <= 8  # Batch size
            assert images.shape[1:] == (3, 224, 224)  # Image shape
            assert labels.shape[0] == images.shape[0]
            assert logits.shape == (images.shape[0], 1000)
            
            # Test that we can compute predictions
            predictions = torch.argmax(logits, dim=1)
            assert predictions.shape == labels.shape
            
            break  # Just test first batch


if __name__ == "__main__":
    # Run tests manually if pytest not available
    import traceback
    
    test_classes = [TestUtils, TestValidation, TestImageNetDataset]
    
    print("Running tests for dataset-with-logits...")
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n=== {test_class.__name__} ===")
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    print(f"  {method_name}... ", end="")
                    method = getattr(instance, method_name)
                    method()
                    print("✅ PASSED")
                    passed += 1
                except Exception as e:
                    print(f"❌ FAILED: {e}")
                    traceback.print_exc()
                    failed += 1
    
    # Run integration test
    print(f"\n=== Integration Test ===")
    try:
        print(f"  test_integration... ", end="")
        test_integration()
        print("✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
        traceback.print_exc()
        failed += 1
    
    print(f"\n" + "="*50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"❌ {failed} tests failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"❌ {failed} tests failed")
