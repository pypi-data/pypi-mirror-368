"""
3D Image Data Generator for neutrophil classification.

This module provides an enhanced 3D data generator that integrates with neutrophils-core
architecture patterns and supports both labeled and unlabeled data loading for 
contrastive learning scenarios.

Features:
    - Enhanced TensorFlow PyDataset integration
    - Support for contrastive learning data pairs
    - Configurable 3D augmentations
    - Memory-efficient batch processing
    - Compatible with existing neutrophils-core patterns
"""

import tensorflow as tf
import numpy as np
import os
from pathlib import Path
import SimpleITK as sitk
from datetime import datetime
from tqdm import tqdm
from tensorflow.keras.utils import to_categorical
import random
import multiprocessing
from typing import Optional, Dict, List, Tuple, Union

from neutrophils_core.loader import augmentations_3d, data_utils


class ImageDataGenerator3D(tf.keras.utils.PyDataset):
    """
    Enhanced 3D Image Data Generator for neutrophil classification and contrastive learning.
    
    This generator supports:
    - Standard supervised learning with labels
    - Contrastive learning with augmented pairs
    - Autoencoder training with input-output pairs
    - Maximum Intensity Projection (MIP) generation
    - Memory-efficient batch processing
    """
    
    def __init__(self, 
                 df: 'pd.DataFrame',
                 batch_size: int,
                 data_dir: Union[str, Path],
                 classes: Optional[Dict[str, int]] = None,
                 X_col: str = "filepath",
                 Y_col: str = "stage",
                 to_fit: bool = True,
                 shuffle: bool = True,
                 train: bool = True,
                 mip: bool = False,
                 augmentation_config: Optional[Dict] = None,
                 drop_remainder: bool = False,
                 image_size: int = 69,
                 get_paths: bool = False,
                 autoencoder_pair: bool = False,
                 contrastive_pair: bool = False,
                 cache_images: bool = False,
                 intensity_input_percentiles: Tuple[float, float] = (1, 99),
                 intensity_out_range: Tuple[float, float] = (0, 1),
                 **kwargs):
        """
        Initialize 3D Image Data Generator.
        
        Args:
            df: DataFrame containing image paths and labels
            batch_size: Number of samples per batch
            data_dir: Root directory containing images
            classes: Dictionary mapping class names to indices
            X_col: Column name for image paths
            Y_col: Column name for labels
            to_fit: Whether to return labels (training mode)
            shuffle: Whether to shuffle data between epochs
            train: Whether to apply augmentations
            mip: Whether to generate Maximum Intensity Projections
            augmentation_config: Configuration for 3D augmentations
            drop_remainder: Whether to drop incomplete final batch
            image_size: Target image size (cubic volumes)
            get_paths: Whether to return file paths with batches
            autoencoder_pair: Whether to return (X, X) pairs for autoencoders
            contrastive_pair: Whether to return augmented pairs for contrastive learning
            cache_images: Whether to cache loaded images in memory
            intensity_percentiles: Percentiles for intensity normalization
            intensity_out_range: Output range for intensity normalization
        """
        super().__init__(**kwargs)

        self.df = df.copy()
        self.batch_size = batch_size
        self.data_dir = Path(data_dir)
        self.X_col = X_col
        self.Y_col = Y_col
        self.to_fit = to_fit
        self.shuffle = shuffle
        self.classes = classes or {}
        self.train = train
        self.mip = mip
        self.image_size = image_size
        self.get_paths = get_paths
        self.autoencoder_pair = autoencoder_pair
        self.contrastive_pair = contrastive_pair
        self.cache_images = cache_images
        self.intensity_input_percentiles = intensity_input_percentiles
        self.intensity_out_range = intensity_out_range
        
        # Set up augmentation configuration
        self.augmentation_config = augmentation_config or self._default_augmentation_config()
        
        # Image cache for memory optimization
        self._image_cache = {} if cache_images else None
        
        # Calculate dataset size
        if drop_remainder:
            self.n = (len(self.df) // self.batch_size) * self.batch_size
        else:
            self.n = len(self.df)

        if self.shuffle:
            self.shuffle_data()

    def _default_augmentation_config(self) -> Dict:
        """Default augmentation configuration for 3D volumes."""
        return {
            "order": ["noise", "rotate", "zoom", "offset", "blur"],
            "noise": {"std_factor": 0.1},
            "rotate": {"degree_max": 90},
            "zoom": {"zoom_factor": 0.05},
            "offset": {"px_max": 3},
            "blur": {"kernel_sz": 2}
        }

    def shuffle_data(self):
        """Shuffle the dataset."""
        self.df = self.df.sample(frac=1).reset_index(drop=True)

    def on_epoch_end(self):
        """Called at the end of each epoch."""
        if self.shuffle:
            self.shuffle_data()
        
        # Clear cache if enabled to manage memory
        if self._image_cache is not None and len(self._image_cache) > 1000:
            self._image_cache.clear()

    def __len__(self) -> int:
        """Calculate the number of batches per epoch."""
        return int(np.ceil(self.n / float(self.batch_size)))

    def __getitem__(self, index: int) -> Union[Tuple, np.ndarray]:
        """
        Generate one batch of data.
        
        Args:
            index: Batch index
            
        Returns:
            Batch data in various formats depending on configuration
        """
        # Generate batch indices
        start_idx = index * self.batch_size
        end_idx = min((index + 1) * self.batch_size, self.n)
        indexes = list(range(start_idx, end_idx))

        # Fill incomplete batches by random sampling
        while len(indexes) < self.batch_size:
            indexes.append(random.choice(range(self.n)))

        # Generate batch data
        if self.contrastive_pair:
            X1, X2 = self._generate_contrastive_pairs(indexes)
            
            if self.get_paths:
                paths = self._generate_paths(indexes)
                return (X1, X2), paths
            else:
                return X1, X2
                
        else:
            X = self._generate_X(indexes)
            
            if self.get_paths:
                paths = self._generate_paths(indexes)
                
                if self.to_fit:
                    if self.autoencoder_pair:
                        return X, X, paths
                    else:
                        y = self._generate_y(indexes)
                        return X, y, paths
                else:
                    return X, paths
            else:
                if self.to_fit:
                    if self.autoencoder_pair:
                        return X, X
                    else:
                        y = self._generate_y(indexes)
                        return X, y
                else:
                    return X

    def _generate_paths(self, indexes: List[int]) -> List[str]:
        """Generate file paths for the given indices."""
        return [self.df.iloc[idx][self.X_col] for idx in indexes]

    def _generate_X(self, indexes: List[int]) -> np.ndarray:
        """
        Generate input data batch.
        
        Args:
            indexes: List of sample indices
            
        Returns:
            Batch of processed images
        """
        # Initialize batch array
        if self.mip:
            X = np.empty((self.batch_size, self.image_size, self.image_size, 3))
        else:
            X = np.empty((self.batch_size, self.image_size, self.image_size, self.image_size, 1))

        # Load and process images
        for i, idx in enumerate(indexes):
            try:
                image_path = self.data_dir / self.df.iloc[idx][self.X_col]
                X[i] = self._load_and_process_image(str(image_path))
            except Exception as e:
                raise ValueError(f"Failed to load {self.df.iloc[idx][self.X_col]} at index {idx}: {e}")

        return X.astype(np.float32)

    def _generate_contrastive_pairs(self, indexes: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate augmented pairs for contrastive learning.
        
        Args:
            indexes: List of sample indices
            
        Returns:
            Tuple of two augmented batches (X1, X2)
        """
        if self.mip:
            X1 = np.empty((self.batch_size, self.image_size, self.image_size, 3))
            X2 = np.empty((self.batch_size, self.image_size, self.image_size, 3))
        else:
            X1 = np.empty((self.batch_size, self.image_size, self.image_size, self.image_size, 1))
            X2 = np.empty((self.batch_size, self.image_size, self.image_size, self.image_size, 1))

        for i, idx in enumerate(indexes):
            try:
                image_path = self.data_dir / self.df.iloc[idx][self.X_col]
                
                # Load original image
                original_img = self._load_raw_image(str(image_path))
                
                # Generate two different augmented versions
                X1[i] = self._process_image_with_augmentation(original_img)
                X2[i] = self._process_image_with_augmentation(original_img)
                
            except Exception as e:
                raise ValueError(f"Failed to load {self.df.iloc[idx][self.X_col]} at index {idx}: {e}")

        return X1.astype(np.float32), X2.astype(np.float32)

    def _generate_y(self, indexes: List[int]) -> np.ndarray:
        """
        Generate label batch.
        
        Args:
            indexes: List of sample indices
            
        Returns:
            One-hot encoded labels
        """
        y = np.empty((self.batch_size), dtype=int)

        for i, idx in enumerate(indexes):
            y[i] = self.classes[self.df.iloc[idx][self.Y_col]]

        num_classes = max(self.classes.values()) + 1
        return to_categorical(y, num_classes=num_classes)

    def _load_raw_image(self, image_path: str) -> np.ndarray:
        """
        Load raw image from file with optional caching.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Raw 3D numpy array
        """
        # Check cache first
        if self._image_cache is not None and image_path in self._image_cache:
            return self._image_cache[image_path].copy()
        
        # Load image using SimpleITK
        img_sitk = sitk.ReadImage(image_path)
        img_np = sitk.GetArrayFromImage(img_sitk)
        
        # Cache if enabled
        if self._image_cache is not None:
            self._image_cache[image_path] = img_np.copy()
        
        return img_np

    def _process_image_with_augmentation(self, img_np: np.ndarray) -> np.ndarray:
        """
        Process image with augmentation pipeline.
        
        Args:
            img_np: Raw 3D image array
            
        Returns:
            Processed and augmented image
        """
        return data_utils.process_image_3d(
            img_np,
            image_size=self.image_size,
            mip=self.mip,
            train=self.train,
            augmentation_config=self.augmentation_config,
            intensity_input_percentiles=self.intensity_input_percentiles,
            intensity_out_range=self.intensity_out_range
        )

    def _load_and_process_image(self, image_path: str) -> np.ndarray:
        """
        Load and process a single image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Processed image ready for model input
        """
        img_np = self._load_raw_image(image_path)
        return self._process_image_with_augmentation(img_np)

    def get_sample_batch(self, num_samples: int = 4) -> Dict:
        """
        Get a sample batch for visualization and debugging.
        
        Args:
            num_samples: Number of samples to return
            
        Returns:
            Dictionary containing sample data and metadata
        """
        original_batch_size = self.batch_size
        self.batch_size = num_samples
        
        try:
            if self.contrastive_pair:
                X1, X2 = self[0]
                sample_data = {
                    'X1': X1,
                    'X2': X2,
                    'type': 'contrastive_pairs'
                }
            else:
                if self.to_fit:
                    X, y = self[0]
                    sample_data = {
                        'X': X,
                        'y': y,
                        'type': 'supervised'
                    }
                else:
                    X = self[0]
                    sample_data = {
                        'X': X,
                        'type': 'inference'
                    }
            
            # Add metadata
            sample_data.update({
                'image_size': self.image_size,
                'mip': self.mip,
                'num_samples': num_samples,
                'augmentation_config': self.augmentation_config if self.train else None
            })
            
            return sample_data
            
        finally:
            self.batch_size = original_batch_size


# Utility functions for creating data generators
def create_labeled_generator(df: 'pd.DataFrame', 
                           batch_size: int,
                           data_dir: Union[str, Path],
                           classes: Dict[str, int],
                           **kwargs) -> ImageDataGenerator3D:
    """
    Create a data generator for labeled data (supervised learning).
    
    Args:
        df: DataFrame with image paths and labels
        batch_size: Batch size
        data_dir: Data directory
        classes: Class name to index mapping
        **kwargs: Additional arguments for ImageDataGenerator3D
        
    Returns:
        Configured ImageDataGenerator3D for supervised learning
    """
    return ImageDataGenerator3D(
        df=df,
        batch_size=batch_size,
        data_dir=data_dir,
        classes=classes,
        to_fit=True,
        **kwargs
    )


def create_contrastive_generator(df: 'pd.DataFrame',
                               batch_size: int,
                               data_dir: Union[str, Path],
                               **kwargs) -> ImageDataGenerator3D:
    """
    Create a data generator for contrastive learning.
    
    Args:
        df: DataFrame with image paths (labels not required)
        batch_size: Batch size
        data_dir: Data directory
        **kwargs: Additional arguments for ImageDataGenerator3D
        
    Returns:
        Configured ImageDataGenerator3D for contrastive learning
    """
    return ImageDataGenerator3D(
        df=df,
        batch_size=batch_size,
        data_dir=data_dir,
        to_fit=False,
        contrastive_pair=True,
        train=True,  # Enable augmentations for contrastive learning
        **kwargs
    )