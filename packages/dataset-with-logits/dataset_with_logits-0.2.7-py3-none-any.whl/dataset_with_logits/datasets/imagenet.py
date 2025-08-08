"""
ImageNet dataset with pre-computed model logits.
"""

from typing import Callable, Optional

from .base import BaseDatasetWithLogits


class ImageNet(BaseDatasetWithLogits):
    """
    ImageNet dataset with pre-computed model logits.
    
    This dataset loads ImageNet images paired with pre-computed logits from various models.
    Perfect for knowledge distillation, model analysis, and efficient research workflows.
    
    Args:
        root (str): Root directory of ImageNet dataset (should contain class folders).
        model (str): Model name for predictions (e.g., 'resnet18', 'vit_l_16').
        transform (callable, optional): Image transformations to apply.
        target_transform (callable, optional): Target transformations to apply.
        version (str): Version of predictions to use ('latest' or specific version).
        auto_download (bool): Whether to automatically download prediction files.
        cache_dir (str, optional): Directory to cache downloaded files.
        
    Example:
        >>> import torchvision.transforms as transforms
        >>> from dataset_with_logits import ImageNet
        >>> 
        >>> transform = transforms.Compose([
        ...     transforms.Resize(256),
        ...     transforms.CenterCrop(224),
        ...     transforms.ToTensor(),
        ... ])
        >>> 
        >>> dataset = ImageNet(
        ...     root='/path/to/imagenet/val',
        ...     model='resnet18',
        ...     transform=transform,
        ...     auto_download=True
        ... )
        >>> 
        >>> image, label, logits = dataset[0]
        >>> print(f"Image shape: {image.shape}")
        >>> print(f"Label: {label}")
        >>> print(f"Logits shape: {logits.shape}")
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
        super().__init__(
            root=root,
            model=model,
            split=split,
            transform=transform,
            target_transform=target_transform,
            version=version,
            auto_download=auto_download,
            cache_dir=cache_dir,
            **kwargs
        )
    
    def _get_dataset_name(self) -> str:
        """Return the dataset name."""
        return "imagenet1k"
    
    def _get_available_models(self) -> dict:
        """Return dictionary of available models for ImageNet."""
        return {
            'resnet18': 'ResNet-18 (11.7M parameters)',
            'resnet50': 'ResNet-50 (25.6M parameters)',
            'resnet101': 'ResNet-101 (44.5M parameters)',
            'resnet152': 'ResNet-152 (60.2M parameters)',
            'vit_b_16': 'Vision Transformer Base (86M parameters)',
            'vit_l_16': 'Vision Transformer Large (304M parameters)',
            'mobilenet_v3_small': 'MobileNet V3 Small (2.5M parameters)',
            'mobilenet_v3_large': 'MobileNet V3 Large (5.5M parameters)',
            'efficientnet_b0': 'EfficientNet-B0 (5.3M parameters)',
            'efficientnet_b4': 'EfficientNet-B4 (19M parameters)',
        }
