"""
Contrastive Data Generator for 3D SimCLR Learning

This module provides a specialized data generator that inherits from ImageDataGenerator3D
and implements contrastive learning specific functionality including:
- Augmented pair generation with different strategies per pair
- Efficient positive/negative pair sampling
- Support for both labeled and unlabeled data
- Memory-efficient batch processing for large 3D volumes
"""

import numpy as np
import random
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional
import tensorflow as tf

from .ImageDataGenerator3D import ImageDataGenerator3D


class ContrastiveDataGenerator3D(ImageDataGenerator3D):
    """
    Enhanced 3D Image Data Generator specifically designed for contrastive learning.
    
    Inherits from ImageDataGenerator3D and adds:
    - Different augmentation strategies per pair
    - Efficient positive/negative pair sampling
    - Advanced contrastive learning batch generation
    - Memory optimization for large datasets
    """
    
    def __init__(self,
                 df: pd.DataFrame,
                 batch_size: int,
                 data_dir: Union[str, Path],
                 classes: Optional[Dict[str, int]] = None,
                 X_col: str = "filepath",
                 Y_col: str = "stage",
                 augmentation_config_pair1: Optional[Dict] = None,
                 augmentation_config_pair2: Optional[Dict] = None,
                 negative_sampling_ratio: float = 1.0,
                 same_class_positive_ratio: float = 0.8,
                 enable_hard_negative_mining: bool = False,
                 memory_efficient_mode: bool = True,
                 **kwargs):
        """
        Initialize Contrastive Data Generator for 3D volumes.
        
        Args:
            df: DataFrame containing image paths and optional labels
            batch_size: Number of samples per batch
            data_dir: Root directory containing images
            classes: Dictionary mapping class names to indices (optional for unlabeled data)
            X_col: Column name for image paths
            Y_col: Column name for labels (optional)
            augmentation_config_pair1: Augmentation config for first pair element
            augmentation_config_pair2: Augmentation config for second pair element  
            negative_sampling_ratio: Ratio of negative to positive pairs
            same_class_positive_ratio: Ratio of same-class positive pairs (when labels available)
            enable_hard_negative_mining: Whether to use hard negative mining
            memory_efficient_mode: Enable memory optimizations for large datasets
            **kwargs: Additional arguments passed to ImageDataGenerator3D
        """
        
        # Force contrastive pair mode and disable standard label fitting
        kwargs.update({
            'contrastive_pair': True,
            'to_fit': False,  # We handle our own label logic
            'train': True,    # Always enable augmentations for contrastive learning
        })
        
        # Clean the dataframe to remove NaN values in the filepath column
        cleaned_df = df.dropna(subset=[X_col]).reset_index(drop=True)
        
        if len(cleaned_df) < len(df):
            print(f"Warning: Removed {len(df) - len(cleaned_df)} rows with NaN values in {X_col} column")
            print(f"Dataset size reduced from {len(df)} to {len(cleaned_df)} samples")
        
        super().__init__(
            df=cleaned_df,
            batch_size=batch_size,
            data_dir=data_dir,
            classes=classes,
            X_col=X_col,
            Y_col=Y_col,
            **kwargs
        )
        
        # Contrastive learning specific parameters
        self.augmentation_config_pair1 = augmentation_config_pair1 or self._default_strong_augmentation()
        self.augmentation_config_pair2 = augmentation_config_pair2 or self._default_weak_augmentation()
        self.negative_sampling_ratio = negative_sampling_ratio
        self.same_class_positive_ratio = same_class_positive_ratio
        self.enable_hard_negative_mining = enable_hard_negative_mining
        self.memory_efficient_mode = memory_efficient_mode
        
        # Check if we have labels for supervised contrastive learning
        self.has_labels = Y_col in self.df.columns and classes is not None
        
        # Pre-compute class indices for efficient sampling if labels available
        if self.has_labels:
            self._precompute_class_indices()
        
        # Hard negative mining cache (if enabled)
        self._hard_negatives_cache = {} if enable_hard_negative_mining else None

        print(f"Initialized ContrastiveDataGenerator3D with {len(self.df)} samples, \n"
              f"batch size {self.batch_size}, \n"
              f"image size {self.image_size}"
        )
    
    def _default_strong_augmentation(self) -> Dict:
        """Strong augmentation configuration for first pair element."""
        return {
            "order": ["noise", "rotate", "zoom", "offset", "blur"],
            "noise": {"std_factor": 0.15},      # Stronger noise
            "rotate": {"degree_max": 120},       # Larger rotation
            "zoom": {"zoom_factor": 0.1},        # More zoom variation
            "offset": {"px_max": 5},             # Larger offset
            "blur": {"kernel_sz": 3}             # Stronger blur
        }
    
    def _default_weak_augmentation(self) -> Dict:
        """Weak augmentation configuration for second pair element."""
        return {
            "order": ["noise", "rotate", "zoom", "offset"],
            "noise": {"std_factor": 0.05},      # Lighter noise
            "rotate": {"degree_max": 45},        # Smaller rotation
            "zoom": {"zoom_factor": 0.03},       # Less zoom variation
            "offset": {"px_max": 2}              # Smaller offset
        }
    
    def _precompute_class_indices(self):
        """Pre-compute indices for each class for efficient sampling."""
        self.class_indices = {}
        for class_name, class_idx in self.classes.items():
            mask = self.df[self.Y_col] == class_name
            self.class_indices[class_idx] = self.df[mask].index.tolist()
    
    def _generate_contrastive_pairs(self, indexes: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate enhanced contrastive pairs with different augmentation strategies.
        
        Args:
            indexes: List of sample indices
            
        Returns:
            Tuple of two augmented batches with different augmentation strengths
        """
        actual_batch_size = len(indexes)
        if self.mip:
            X1 = np.empty((actual_batch_size, self.image_size, self.image_size, 3))
            X2 = np.empty((actual_batch_size, self.image_size, self.image_size, 3))
        else:
            X1 = np.empty((actual_batch_size, self.image_size, self.image_size, self.image_size, 1))
            X2 = np.empty((actual_batch_size, self.image_size, self.image_size, self.image_size, 1))

        for i, idx in enumerate(indexes):
            try:
                # Validate that the filepath is not NaN
                filepath_value = self.df.iloc[idx][self.X_col]
                if pd.isna(filepath_value):
                    raise ValueError(f"NaN filepath found at index {idx}")
                
                image_path = self.data_dir / filepath_value
                
                # Load original image once
                original_img = self._load_raw_image(str(image_path))
                
                # Generate two different augmented versions with different strategies
                X1[i] = self._process_image_with_specific_augmentation(
                    original_img, self.augmentation_config_pair1
                )
                X2[i] = self._process_image_with_specific_augmentation(
                    original_img, self.augmentation_config_pair2
                )
                
            except Exception as e:
                raise ValueError(f"Failed to load {filepath_value} at index {idx}: {e}")

        return X1.astype(np.float32), X2.astype(np.float32)
    
    def _process_image_with_specific_augmentation(self, img_np: np.ndarray, aug_config: Dict) -> np.ndarray:
        """
        Process image with specific augmentation configuration.
        
        Args:
            img_np: Raw 3D image array
            aug_config: Specific augmentation configuration
            
        Returns:
            Processed and augmented image
        """
        # Import augmentations
        from . import augmentations_3d
        
        # Apply specific augmentation configuration
        if aug_config:
            img_np = augmentations_3d.apply_augmentations(
                img_np, 
                aug_config["order"],
                aug_config
            )
        
        # Standard intensity normalization
        from skimage.exposure import rescale_intensity
        img_np = rescale_intensity(
            img_np,
            in_range=tuple(np.percentile(img_np, (1, 99))),
            out_range=(0, 1)
        )

        # Resize to target dimensions
        from .ImageDataGenerator3D import pad_image, crop_center
        img_np = pad_image(img_np, padded_size=[self.image_size, self.image_size, self.image_size])
        img_np = crop_center(img_np, crop_size=[self.image_size, self.image_size, self.image_size])

        # Generate MIP if requested
        if self.mip:
            img_mip_0 = img_np.max(axis=0)
            img_mip_1 = img_np.max(axis=1)
            img_mip_2 = img_np.max(axis=2)
            return np.stack([img_mip_0, img_mip_1, img_mip_2], axis=-1)

        return np.expand_dims(img_np, axis=-1)
    
    def generate_positive_pairs(self, batch_size: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate positive pairs for contrastive learning.
        
        Args:
            batch_size: Override batch size (uses self.batch_size if None)
            
        Returns:
            Tuple of positive pair batches (X1, X2)
        """
        effective_batch_size = batch_size or self.batch_size
        
        if self.has_labels and random.random() < self.same_class_positive_ratio:
            # Generate same-class positive pairs
            indexes = self._sample_same_class_pairs(effective_batch_size)
        else:
            # Generate random positive pairs (same image, different augmentations)
            # Ensure we only select from valid indices (non-NaN filepaths)
            valid_indices = self.df[~pd.isna(self.df[self.X_col])].index.tolist()
            if not valid_indices:
                raise ValueError("No valid samples found - all filepaths are NaN")
            indexes = random.choices(valid_indices, k=effective_batch_size)
        
        return self._generate_contrastive_pairs(indexes)
    
    def generate_negative_pairs(self, batch_size: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate negative pairs for contrastive learning.
        
        Args:
            batch_size: Override batch size (uses self.batch_size if None)
            
        Returns:
            Tuple of negative pair batches (X1, X2)
        """
        effective_batch_size = batch_size or self.batch_size
        
        if self.enable_hard_negative_mining:
            indexes1, indexes2 = self._sample_hard_negative_pairs(effective_batch_size)
        else:
            indexes1, indexes2 = self._sample_random_negative_pairs(effective_batch_size)
        
        # Generate pairs from different images
        X1 = self._generate_X_from_indexes(indexes1)
        X2 = self._generate_X_from_indexes(indexes2)
        
        return X1, X2
    
    def _sample_same_class_pairs(self, batch_size: int) -> List[int]:
        """Sample pairs from the same class when labels are available."""
        indexes = []
        for _ in range(batch_size):
            # Randomly select a class
            class_idx = random.choice(list(self.class_indices.keys()))
            class_samples = self.class_indices[class_idx]
            
            if len(class_samples) > 0:
                indexes.append(random.choice(class_samples))
            else:
                # Fallback to random sampling from valid indices
                valid_indices = self.df[~pd.isna(self.df[self.X_col])].index.tolist()
                if valid_indices:
                    indexes.append(random.choice(valid_indices))
                else:
                    raise ValueError("No valid samples found - all filepaths are NaN")
        
        return indexes
    
    def _sample_random_negative_pairs(self, batch_size: int) -> Tuple[List[int], List[int]]:
        """Sample random negative pairs from different images."""
        # Get valid indices (non-NaN filepaths)
        valid_indices = self.df[~pd.isna(self.df[self.X_col])].index.tolist()
        if not valid_indices:
            raise ValueError("No valid samples found - all filepaths are NaN")
        
        indexes1 = random.choices(valid_indices, k=batch_size)
        indexes2 = []
        
        for idx1 in indexes1:
            # Ensure different images for negative pairs
            idx2 = idx1
            while idx2 == idx1:
                idx2 = random.choice(valid_indices)
            indexes2.append(idx2)
        
        return indexes1, indexes2
    
    def _sample_hard_negative_pairs(self, batch_size: int) -> Tuple[List[int], List[int]]:
        """Sample hard negative pairs using cached difficulty scores."""
        # This is a placeholder for hard negative mining
        # In practice, this would use embeddings from previous training iterations
        # to identify hard negatives (samples that are difficult to distinguish)
        
        # For now, fall back to random sampling
        return self._sample_random_negative_pairs(batch_size)
    
    def _generate_X_from_indexes(self, indexes: List[int]) -> np.ndarray:
        """Generate batch from specific indexes with pair1 augmentation."""
        if self.mip:
            X = np.empty((len(indexes), self.image_size, self.image_size, 3))
        else:
            X = np.empty((len(indexes), self.image_size, self.image_size, self.image_size, 1))

        for i, idx in enumerate(indexes):
            try:
                # Validate that the filepath is not NaN
                filepath_value = self.df.iloc[idx][self.X_col]
                if pd.isna(filepath_value):
                    raise ValueError(f"NaN filepath found at index {idx}")
                
                image_path = self.data_dir / filepath_value
                original_img = self._load_raw_image(str(image_path))
                X[i] = self._process_image_with_specific_augmentation(
                    original_img, self.augmentation_config_pair1
                )
            except Exception as e:
                raise ValueError(f"Failed to load {filepath_value} at index {idx}: {e}")

        return X.astype(np.float32)
    
    def get_contrastive_batch(self) -> Dict[str, np.ndarray]:
        """
        Generate a complete contrastive learning batch with positive and negative pairs.
        
        Returns:
            Dictionary containing positive and negative pairs with labels
        """
        # Calculate positive and negative batch sizes
        pos_batch_size = self.batch_size // 2
        neg_batch_size = int(self.batch_size * self.negative_sampling_ratio) // 2
        
        # Generate positive pairs (same image, different augmentations)
        pos_X1, pos_X2 = self.generate_positive_pairs(pos_batch_size)
        pos_labels = np.ones(pos_batch_size, dtype=np.int32)
        
        # Generate negative pairs (different images)
        neg_X1, neg_X2 = self.generate_negative_pairs(neg_batch_size)
        neg_labels = np.zeros(neg_batch_size, dtype=np.int32)
        
        # Combine positive and negative pairs
        X1 = np.concatenate([pos_X1, neg_X1], axis=0)
        X2 = np.concatenate([pos_X2, neg_X2], axis=0)
        labels = np.concatenate([pos_labels, neg_labels], axis=0)
        
        # Shuffle the combined batch
        indices = np.arange(len(labels))
        np.random.shuffle(indices)
        
        return {
            'X1': X1[indices],
            'X2': X2[indices], 
            'labels': labels[indices],
            'positive_pairs': pos_batch_size,
            'negative_pairs': neg_batch_size
        }
    
    def update_hard_negatives_cache(self, embeddings: np.ndarray, labels: np.ndarray, difficulties: np.ndarray):
        """
        Update hard negatives cache with difficulty scores from training.
        
        Args:
            embeddings: Feature embeddings from current batch
            labels: Ground truth or pseudo labels
            difficulties: Difficulty scores for each sample
        """
        if self._hard_negatives_cache is not None:
            # This would be implemented to store hard negative examples
            # based on training feedback for future sampling
            pass
    
    def get_augmentation_visualization_batch(self, num_samples: int = 4) -> Dict:
        """
        Generate a batch showing different augmentation strategies for visualization.
        
        Args:
            num_samples: Number of samples to visualize
            
        Returns:
            Dictionary with original, pair1, and pair2 augmented versions
        """
        # Get valid indices (non-NaN filepaths)
        valid_indices = self.df[~pd.isna(self.df[self.X_col])].index.tolist()
        if not valid_indices:
            raise ValueError("No valid samples found - all filepaths are NaN")
        indexes = random.choices(valid_indices, k=num_samples)
        
        if self.mip:
            original = np.empty((num_samples, self.image_size, self.image_size, 3))
            pair1 = np.empty((num_samples, self.image_size, self.image_size, 3)) 
            pair2 = np.empty((num_samples, self.image_size, self.image_size, 3))
        else:
            original = np.empty((num_samples, self.image_size, self.image_size, self.image_size, 1))
            pair1 = np.empty((num_samples, self.image_size, self.image_size, self.image_size, 1))
            pair2 = np.empty((num_samples, self.image_size, self.image_size, self.image_size, 1))
        
        for i, idx in enumerate(indexes):
            # Validate that the filepath is not NaN
            filepath_value = self.df.iloc[idx][self.X_col]
            if pd.isna(filepath_value):
                raise ValueError(f"NaN filepath found at index {idx}")
            
            image_path = self.data_dir / filepath_value
            original_img = self._load_raw_image(str(image_path))
            
            # Original (minimal processing)
            original[i] = self._process_image_with_specific_augmentation(original_img, {})
            
            # Pair 1 (strong augmentation)
            pair1[i] = self._process_image_with_specific_augmentation(
                original_img, self.augmentation_config_pair1
            )
            
            # Pair 2 (weak augmentation)
            pair2[i] = self._process_image_with_specific_augmentation(
                original_img, self.augmentation_config_pair2
            )
        
        return {
            'original': original,
            'pair1_strong_aug': pair1,
            'pair2_weak_aug': pair2,
            'filepaths': [self.df.iloc[idx][self.X_col] for idx in indexes],
            'augmentation_config_pair1': self.augmentation_config_pair1,
            'augmentation_config_pair2': self.augmentation_config_pair2
        }


# Utility functions for creating contrastive generators
def create_contrastive_generator(df: pd.DataFrame,
                               batch_size: int,
                               data_dir: Union[str, Path],
                               classes: Optional[Dict[str, int]] = None,
                               augmentation_config_pair1: Optional[Dict] = None,
                               augmentation_config_pair2: Optional[Dict] = None,
                               **kwargs) -> ContrastiveDataGenerator3D:
    """
    Create a contrastive data generator with sensible defaults.
    
    Args:
        df: DataFrame with image paths and optional labels
        batch_size: Batch size
        data_dir: Data directory
        classes: Class mapping (optional, for supervised contrastive learning)
        augmentation_config_pair1: Strong augmentation config
        augmentation_config_pair2: Weak augmentation config
        **kwargs: Additional arguments for ContrastiveDataGenerator3D
        
    Returns:
        Configured ContrastiveDataGenerator3D
    """
    return ContrastiveDataGenerator3D(
        df=df,
        batch_size=batch_size,
        data_dir=data_dir,
        classes=classes,
        augmentation_config_pair1=augmentation_config_pair1,
        augmentation_config_pair2=augmentation_config_pair2,
        **kwargs
    )


def create_unlabeled_contrastive_generator(unlabeled_df: pd.DataFrame,
                                         batch_size: int,
                                         data_dir: Union[str, Path],
                                         **kwargs) -> ContrastiveDataGenerator3D:
    """
    Create a contrastive generator specifically for unlabeled data.
    
    Args:
        unlabeled_df: DataFrame with image paths (no labels required)
        batch_size: Batch size
        data_dir: Data directory
        **kwargs: Additional arguments
        
    Returns:
        ContrastiveDataGenerator3D configured for unlabeled data
    """
    return ContrastiveDataGenerator3D(
        df=unlabeled_df,
        batch_size=batch_size,
        data_dir=data_dir,
        classes=None,  # No classes for unlabeled data
        **kwargs
    )