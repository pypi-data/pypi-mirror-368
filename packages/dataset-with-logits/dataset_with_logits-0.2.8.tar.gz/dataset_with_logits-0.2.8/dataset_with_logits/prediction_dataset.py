import os
from typing import Any, Tuple

import pandas as pd
import torch
from torchvision.datasets import ImageFolder


class ImageNetWithLogits(ImageFolder):
    """
    A custom dataset that loads images from ImageNet and pairs them with
    pre-computed logits from a prediction CSV file.

    Args:
        root (str): The root directory of the ImageNet dataset.
        predictions_path (str): The path to the CSV file containing the predictions.
        transform (callable, optional): A function/transform that takes in an PIL image
            and returns a transformed version. E.g, `transforms.RandomCrop`.
    """
    def __init__(self, root: str, predictions_path: str, **kwargs):
        super().__init__(root, **kwargs)
        
        # Load predictions into a dictionary for fast lookup
        print(f"Loading predictions from {predictions_path}...")
        predictions_df = pd.read_csv(predictions_path)
        # Use the 'id' column (filename without extension) as the key
        self.predictions = predictions_df.set_index('id')['logits'].to_dict()
        print("Predictions loaded.")

    def __getitem__(self, index: int) -> Tuple[Any, int, torch.Tensor]:  # type: ignore[override]
        """
        Args:
            index (int): Index

        Returns:
            tuple: (sample, target, logits) where target is class_index of the
                   target class and logits are the pre-computed model outputs.
        """
        # Get the original image and label from the parent class
        path, target = self.samples[index]
        sample = self.loader(path)
        if self.transform is not None:
            sample = self.transform(sample)
        
        # Get the filename (without extension) to use as a key
        filename = os.path.splitext(os.path.basename(path))[0]
        
        # Retrieve the logits string from our dictionary
        logits_str = self.predictions.get(filename)
        
        if logits_str is None:
            # Handle cases where a prediction for an image might be missing
            raise KeyError(f"No prediction found for image ID: {filename}")
            
        # Convert the semicolon-separated string back to a tensor
        logits = torch.tensor([float(x) for x in logits_str.split(';')])
        
        return sample, target, logits

if __name__ == '__main__':
    import pandas as pd
    import torchvision.transforms as transforms

    def test_dataset_with_real_data():
        """
        A test for the ImageNetWithLogits dataset using the real ImageNet
        validation set and a real prediction file.
        """
        print("--- Running test for ImageNetWithLogits with real data ---")
        
        # --- Configuration ---
        IMAGENET_ROOT = "/home/gwe/datasets/imagenet-1k/processed/val"
        PREDICTIONS_PATH = "/u/home/gwe/source/predictions-on-datasets/predictions/mobilenet_v3_small-imagenet1k.csv"

        # --- Pre-test Checks ---
        if not os.path.isdir(IMAGENET_ROOT):
            print(f"Warning: ImageNet root directory not found at '{IMAGENET_ROOT}'. Skipping test.")
            return
        if not os.path.isfile(PREDICTIONS_PATH):
            print(f"Warning: Predictions CSV not found at '{PREDICTIONS_PATH}'. Skipping test.")
            return

        # 1. Read some sample predictions to use as our ground truth for the test
        print(f"Reading sample predictions from {PREDICTIONS_PATH}...")
        predictions_df = pd.read_csv(PREDICTIONS_PATH)
        if len(predictions_df) < 5:
            print("Warning: Not enough predictions in file to run a comprehensive test. Skipping.")
            return
        
        # Take a few samples from the start, middle, and end
        test_samples = pd.concat([
            predictions_df.head(2), 
            predictions_df.iloc[[len(predictions_df) // 2]], 
            predictions_df.tail(2)
        ]).reset_index(drop=True)
        
        print(f"Selected {len(test_samples)} samples to test.")

        # 2. Instantiate the dataset
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])
        
        dataset = ImageNetWithLogits(
            root=IMAGENET_ROOT,
            predictions_path=PREDICTIONS_PATH,
            transform=transform
        )
        
        # Create a quick lookup map from image filename to index for efficiency
        id_to_index_map = {os.path.splitext(os.path.basename(path))[0]: i for i, (path, _) in enumerate(dataset.samples)}

        # 3. Loop through test samples and verify each one
        for _, test_entry in test_samples.iterrows():
            test_id = test_entry['id']
            test_logits_str = test_entry['logits']
            test_logits_tensor = torch.tensor([float(x) for x in test_logits_str.split(';')])
            
            print(f"\n--- Verifying sample ID: {test_id} ---")

            # Find the index of the test image in the dataset
            test_index = id_to_index_map.get(test_id)
            
            if test_index is None:
                print(f"Error: Could not find image with ID '{test_id}' in the dataset at '{IMAGENET_ROOT}'.")
                continue  # Move to the next test sample

            # Test the __getitem__ method on the specific image
            print(f"Fetching item at index {test_index}...")
            sample, target, loaded_logits = dataset[test_index]
            
            # Verify the results
            print(f"  Sample shape: {sample.shape}")
            print(f"  Loaded logits shape: {loaded_logits.shape}")
            
            assert sample.shape == (3, 224, 224), "Sample shape is incorrect."
            assert loaded_logits.shape == (1000,), "Loaded logits shape is incorrect."
            assert torch.allclose(loaded_logits, test_logits_tensor), f"Loaded logits for {test_id} do not match the logits from the CSV file."
            print(f"  Assertions passed for ID: {test_id}")

        print("\n\n--- All tests successful! ---")

    test_dataset_with_real_data()

    test_dataset_with_real_data()
