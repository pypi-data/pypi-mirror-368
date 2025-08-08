"""
Base dataset class for datasets with pre-computed logits.
"""

import gzip
import os
import warnings
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Tuple

import pandas as pd
import torch
from torchvision.datasets import ImageFolder


class BaseDatasetWithLogits(ImageFolder, ABC):
    """
    Abstract base class for datasets with pre-computed model logits.
    
    This class provides common functionality for all dataset classes in the package.
    """
    
    def __init__(
        self,
        root: str,
        model: str,
        split: str = "val",
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
        version: str = "latest",
        auto_download: bool = True,
        cache_dir: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the dataset.
        
        Args:
            root: Root directory of the dataset (should contain class folders).
            model: Model name for predictions (e.g., 'resnet18', 'vit_l_16').
            split: Dataset split (e.g., 'val', 'test').
            transform: Image transformations to apply.
            target_transform: Target transformations to apply.
            version: Version of predictions to use ('latest' or specific version).
            auto_download: Whether to automatically download prediction files.
            cache_dir: Directory to cache downloaded files.
        """
        super().__init__(root, transform=transform, target_transform=target_transform, **kwargs)
        
        self.model = model
        self.split = split
        self.version = version
        self.auto_download = auto_download
        self.cache_dir = cache_dir or self._get_default_cache_dir()
        
        # Load predictions
        predictions_path = self._get_predictions_path()
        self._load_predictions(predictions_path)
    
    @abstractmethod
    def _get_dataset_name(self) -> str:
        """Return the dataset name (e.g., 'imagenet', 'cifar10')."""
        pass
    
    @abstractmethod  
    def _get_available_models(self) -> dict:
        """Return dictionary of available models for this dataset."""
        pass
    
    def _get_default_cache_dir(self) -> str:
        """Get the default cache directory."""
        home_dir = os.path.expanduser("~")
        cache_dir = os.path.join(home_dir, ".cache", "dataset_with_logits")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
    
    def _get_predictions_path(self) -> str:
        """Get the path to the predictions file."""
        from ..utils.download import download_predictions
        
        if self.auto_download:
            return download_predictions(
                dataset=self._get_dataset_name(),
                model=self.model,
                split=self.split,
                version=self.version,
                cache_dir=self.cache_dir
            )
        else:
            # Look for local file
            filename = self._construct_filename()
            local_paths = [
                os.path.join(self.cache_dir, filename),
                os.path.join(".", filename),
                filename
            ]
            
            for path in local_paths:
                if os.path.exists(path):
                    return path
            
            raise FileNotFoundError(
                f"Predictions file '{filename}' not found. "
                f"Set auto_download=True to download automatically."
            )
    
    def _construct_filename(self) -> str:
        """Construct the filename for predictions."""
        from ..utils.download import construct_filename
        
        dataset_name = self._get_dataset_name()
        if self.version == "latest":
            # For now, default to v0.1.0 - you can make this smarter later
            version = "v0.1.0"
        else:
            version = self.version
            
        return construct_filename(dataset_name, self.model, self.split, version)
    
    def _load_predictions(self, predictions_path: str) -> None:
        """Load predictions from CSV file (handles both .csv and .csv.gz files)."""
        print(f"Loading predictions from {predictions_path}...")
        
        try:
            # Check if file is gzipped based on extension
            if predictions_path.endswith('.gz'):
                with gzip.open(predictions_path, 'rt', encoding='utf-8') as f:
                    predictions_df = pd.read_csv(f)
            else:
                predictions_df = pd.read_csv(predictions_path)
            
            # Validate CSV format
            required_columns = {'id', 'logits'}
            if not required_columns.issubset(predictions_df.columns):
                raise ValueError(
                    f"CSV must contain columns: {required_columns}. "
                    f"Found: {set(predictions_df.columns)}"
                )
            
            # Create lookup dictionary
            self.predictions = predictions_df.set_index('id')['logits'].to_dict()
            
            # Store metadata
            self.predictions_path = predictions_path
            self.num_predictions = len(self.predictions)
            
            print(f"Loaded {self.num_predictions} predictions.")
            
            # Warn if predictions count doesn't match images
            if len(self.samples) > 0 and abs(len(self.samples) - self.num_predictions) > 100:
                warnings.warn(
                    f"Number of images ({len(self.samples)}) and predictions "
                    f"({self.num_predictions}) differ significantly. "
                    f"Some images may not have corresponding predictions."
                )
                
        except Exception as e:
            raise RuntimeError(f"Failed to load predictions from {predictions_path}: {str(e)}")
    
    def __getitem__(self, index: int) -> Tuple[Any, Any, torch.Tensor]:  # type: ignore[override]
        """
        Get a sample from the dataset.
        
        Returns:
            Tuple of (image, label, logits) where:
            - image: PIL Image or transformed tensor
            - label: Integer class label
            - logits: Tensor of model outputs
        """
        # Get image and label from parent class
        path, target = self.samples[index]
        sample = self.loader(path)
        if self.transform is not None:
            sample = self.transform(sample)
        if self.target_transform is not None:
            target = self.target_transform(target)
        
        # Get filename for prediction lookup
        filename = os.path.splitext(os.path.basename(path))[0]
        
        # Retrieve logits
        logits_str = self.predictions.get(filename)
        if logits_str is None:
            raise KeyError(
                f"No predictions found for image '{filename}'. "
                f"Ensure the predictions file contains this image ID."
            )
        
        # Parse logits string to tensor
        try:
            logits = torch.tensor([float(x) for x in logits_str.split(';')])
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid logits format for image '{filename}': {str(e)}")
        
        return sample, target, logits
    
    def get_info(self) -> dict:
        """Get information about the dataset and predictions."""
        return {
            'dataset': self._get_dataset_name(),
            'model': self.model,
            'version': self.version,
            'predictions_path': getattr(self, 'predictions_path', 'Unknown'),
            'num_predictions': getattr(self, 'num_predictions', 0),
            'num_images': len(self.samples),
            'available_models': list(self._get_available_models().keys()),
        }
