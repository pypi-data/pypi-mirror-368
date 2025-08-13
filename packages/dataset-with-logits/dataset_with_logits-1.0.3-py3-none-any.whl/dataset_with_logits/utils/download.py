"""
Download utilities for prediction files from multiple hosting backends.
Supports Hugging Face Hub and GitHub Releases.
"""

import logging
import os
import sys
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

# Hosting backend configuration
GITHUB_REPO = "ViGeng/predictions-on-datasets"
HUGGINGFACE_REPO = "ViGeng/prediction-datasets"
HUGGINGFACE_BASE = f"https://huggingface.co/datasets/{HUGGINGFACE_REPO}/resolve/main"

# Available datasets and models
AVAILABLE_DATASETS = {
    'imagenet1k': {
        'resnet18': 'ResNet-18 (11.7M parameters)',
        'resnet50': 'ResNet-50 (25.6M parameters)', 
        'resnet101': 'ResNet-101 (44.5M parameters)',
        'resnet152': 'ResNet-152 (60.2M parameters)',
        'vit_b_16': 'Vision Transformer Base (86M parameters)',
        'vit_l_16': 'Vision Transformer Large (304M parameters)',
        'mobilenet_v3_small': 'MobileNet V3 Small (2.5M parameters)',
        'mobilenet_v3_large': 'MobileNet V3 Large (5.5M parameters)',
    },
    'cifar10': {
        'resnet18': 'ResNet-18 for CIFAR-10',
        'vit_b_16': 'Vision Transformer Base for CIFAR-10',
    },
    'cifar100': {
        'resnet50': 'ResNet-50 for CIFAR-100',
    }
}


def get_cache_dir() -> str:
    """Get the default cache directory for downloaded files."""
    home_dir = os.path.expanduser("~")
    cache_dir = os.path.join(home_dir, ".cache", "dataset_with_logits")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def list_available_models(dataset: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """
    List all available prediction models.
    
    Args:
        dataset: If specified, return models only for this dataset.
        
    Returns:
        Dictionary mapping dataset names to available models.
    """
    if dataset is None:
        return AVAILABLE_DATASETS
    elif dataset in AVAILABLE_DATASETS:
        return {dataset: AVAILABLE_DATASETS[dataset]}
    else:
        available = list(AVAILABLE_DATASETS.keys())
        raise ValueError(f"Dataset '{dataset}' not available. Available: {available}")


def construct_filename(dataset: str, model: str, split: str = "val", version: str = "v0.1.0") -> str:
    """
    Construct the filename for prediction files.
    
    Args:
        dataset: Dataset name (e.g., 'imagenet1k', 'cifar10').
        model: Model name (e.g., 'resnet18', 'vit_l_16').
        split: Dataset split (e.g., 'val', 'test').
        version: Version string (e.g., 'v0.1.0').
        
    Returns:
        Filename following the pattern: {model}-IMAGENET1K_V1-{dataset}-{split}.csv.gz
    """
    # Map model names to their full torchvision model names
    model_mappings = {
        'resnet18': 'resnet18-IMAGENET1K_V1',
        'resnet50': 'resnet50-IMAGENET1K_V1',
        'resnet101': 'resnet101-IMAGENET1K_V1', 
        'resnet152': 'resnet152-IMAGENET1K_V1',
        'vit_b_16': 'vit_b_16-IMAGENET1K_V1',
        'vit_l_16': 'vit_l_16-IMAGENET1K_V1',
        'mobilenet_v3_small': 'mobilenet_v3_small-IMAGENET1K_V1',
        'mobilenet_v3_large': 'mobilenet_v3_large-IMAGENET1K_V1',
    }
    
    model_full_name = model_mappings.get(model, model)
    return f"{model_full_name}-{dataset}-{split}.csv.gz"


def construct_huggingface_url(dataset: str, model: str, split: str = "val", version: str = "v0.1.0") -> str:
    """
    Construct the Hugging Face Hub URL for downloading prediction files.
    
    Args:
        dataset: Dataset name.
        model: Model name.
        split: Dataset split.
        version: Version string.
        
    Returns:
        Full URL to the prediction file on Hugging Face Hub.
    """
    filename = construct_filename(dataset, model, split, version)
    return f"{HUGGINGFACE_BASE}/{dataset}/{split}/{filename}"


def construct_github_release_url(dataset: str, model: str, split: str = "val", version: str = "v0.1.0") -> str:
    """
    Construct the GitHub releases URL for downloading prediction files.
    
    Args:
        dataset: Dataset name.
        model: Model name.
        split: Dataset split.
        version: Version string.
        
    Returns:
        Full URL to the prediction file in GitHub releases.
    """
    filename = construct_filename(dataset, model, split, version)
    return f"https://github.com/{GITHUB_REPO}/releases/download/{version}/{filename}"


def download_predictions(
    dataset: str,
    model: str,
    split: str = "val",
    version: str = "latest",
    cache_dir: Optional[str] = None,
    force_download: bool = False,
    backends: Optional[List[str]] = None
) -> str:
    """
    Download prediction file from multiple hosting backends with fallback support.

    Args:
        dataset: Dataset name (e.g., 'imagenet1k', 'cifar10').
        model: Model name (e.g., 'resnet18', 'vit_l_16').
        split: Dataset split (e.g., 'val', 'test').
        version: Version to download ('latest' or specific version like 'v0.1.0').
        cache_dir: Directory to save the file. If None, uses default cache dir.
        force_download: Whether to re-download even if file exists locally.
        backends: List of backends to try in order. If None, uses default priority.

    Returns:
        Path to the downloaded file.

    Raises:
        ValueError: If dataset/model combination is not available.
        RuntimeError: If download fails from all backends.
    """
    logger = logging.getLogger(__name__)
    # Validate inputs
    if dataset not in AVAILABLE_DATASETS:
        available = list(AVAILABLE_DATASETS.keys())
        raise ValueError(f"Dataset '{dataset}' not available. Available: {available}")
    
    if model not in AVAILABLE_DATASETS[dataset]:
        available = list(AVAILABLE_DATASETS[dataset].keys())
        raise ValueError(f"Model '{model}' not available for {dataset}. Available: {available}")
    
    # Handle version
    if version == "latest":
        version = "v0.1.0"  # Default to latest stable version
    
    # Set up paths
    if cache_dir is None:
        cache_dir = get_cache_dir()
    
    filename = construct_filename(dataset, model, split, version)
    local_path = os.path.join(cache_dir, filename)

    # Check if file already exists and we don't want to force download
    if os.path.exists(local_path) and not force_download:
        logger.info(f"Using cached predictions: {local_path}")
        return local_path

    # Define backends to try (in order of preference)
    if backends is None:
        backends = ['huggingface', 'github_release']

    # Try each backend in order
    for backend in backends:
        logger.info(f"🔄 Trying {backend} backend...")

        try:
            if backend == 'huggingface':
                url = construct_huggingface_url(dataset, model, split, version)
            elif backend == 'github_release':
                url = construct_github_release_url(dataset, model, split, version)
            else:
                logger.warning(f"⚠️  Unknown backend: {backend}")
                continue

            logger.info(f"📥 Downloading {filename} from {backend}...")
            logger.info(f"🔗 URL: {url}")

            # Create directory if it doesn't exist
            os.makedirs(cache_dir, exist_ok=True)

            # Download with progress (for large files)
            def show_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    sys.stdout.write(f"\rProgress: {percent}%")
                    sys.stdout.flush()

            urllib.request.urlretrieve(url, local_path, reporthook=show_progress)
            sys.stdout.write('\n') # new line after progress bar
            logger.info(f"✅ Successfully downloaded from {backend}")
            logger.info(f"📁 Saved to: {local_path}")

            return local_path

        except Exception as e:
            logger.error(f"❌ Failed to download from {backend}: {str(e)}")
            # Clean up partial download
            if os.path.exists(local_path):
                os.remove(local_path)
            continue
    
    # If we get here, all backends failed
    raise RuntimeError(
        f"Failed to download {filename} from all backends: {backends}. "
        f"Please check your internet connection and try again."
    )


def clear_cache(cache_dir: Optional[str] = None) -> None:
    """
    Clear the downloaded predictions cache.

    Args:
        cache_dir: Cache directory to clear. If None, clears default cache dir.
    """
    logger = logging.getLogger(__name__)
    if cache_dir is None:
        cache_dir = get_cache_dir()

    if os.path.exists(cache_dir):
        import shutil
        shutil.rmtree(cache_dir)
        logger.info(f"Cache cleared: {cache_dir}")
    else:
        logger.warning("Cache directory doesn't exist.")
