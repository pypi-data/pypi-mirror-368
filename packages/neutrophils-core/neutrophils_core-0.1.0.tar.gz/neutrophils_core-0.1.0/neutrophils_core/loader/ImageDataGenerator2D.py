#!/usr/bin/env python3
"""
Optimized version of ImageDataGenerator2D with performance improvements:
- Concurrent I/O operations
- Smart caching system
- Memory pooling
- Reduced memory allocations
"""

import tensorflow as tf
import numpy as np
import os
import SimpleITK as sitk
from datetime import datetime
from tqdm import tqdm
from skimage.exposure import rescale_intensity
from tensorflow.keras.utils import to_categorical
import random
import sys
import pandas as pd
from sklearn.utils import resample
import threading
from typing import List, Tuple, Optional, Dict, Any
import time
import logging

# Import our optimized components
from .cache_manager import get_global_cache_manager
from .concurrent_loader import ConcurrentImageLoader, BatchProcessor

# Import hierarchical labels utilities
try:
    from .hierarchical_labels import (
        NEUTROPHIL_HIERARCHY, get_head_info, convert_flat_label_to_hierarchical
    )
    HIERARCHICAL_LABELS_AVAILABLE = True
except ImportError:
    HIERARCHICAL_LABELS_AVAILABLE = False
    logging.warning("Hierarchical labels module not available. Multi-output models will not be supported.")

# Import augmentation functions
from .augmentations_2d import *

def crop_center_2d(image, crop_size=[69,69]):
    """Optimized center cropping"""
    height, width = image.shape[:2]
    start_y = max((height - crop_size[0]) // 2, 0)
    start_x = max((width - crop_size[1]) // 2, 0)
    if image.ndim == 3:
        return image[start_y:start_y + crop_size[0], start_x:start_x + crop_size[1], :]
    else:
        return image[start_y:start_y + crop_size[0], start_x:start_x + crop_size[1]]

def pad_image_2d(image, padded_size=[69,69]):
    """Optimized image padding"""
    pad_0 = [0,0]
    pad_1 = [0,0]
    current_shape = image.shape[:2]

    for i in range(2):
        if current_shape[i] < padded_size[i]:
            pad_0[i] = (padded_size[i]-current_shape[i])//2
            pad_1[i] = padded_size[i] - current_shape[i] - pad_0[i]
    
    if image.ndim == 3:
        padded_image = np.pad(image, ((pad_0[0], pad_1[0]), (pad_0[1], pad_1[1]), (0,0)), mode='constant', constant_values=0)
    else:
        padded_image = np.pad(image, ((pad_0[0], pad_1[0]), (pad_0[1], pad_1[1])), mode='constant', constant_values=0)
    return padded_image

class ImageDataGenerator2D(tf.keras.utils.PyDataset):
    """Optimized 2D Image Data Generator with performance improvements"""
    
    def __init__(self,
                df,
                batch_size,
                data_dir,
                X_col="filepath",
                Y_col="label_id",
                to_fit=True,
                shuffle=True,
                train=True,
                augmentation_config=None,
                drop_remainder=False,
                image_size=96,
                num_channels=1,
                get_paths=False,
                autoencoder_pair=False,
                label_format='one_hot',
                num_classes=4,
                sampling_strategy='none',
                projection_mode='single',
                projection_shuffle=False,
                padding_strategy='repeat_random',
                deterministic_padding=True,
                # Hierarchical label parameters
                classifier_type='standard',
                # New optimization parameters
                enable_caching=True,
                cache_size_mb=1024,
                max_workers=4,
                enable_memory_pool=True,
                prefetch_batches=2,
                # Bias prevention parameters
                normalization_method='percentile',
                normalization_params=None,
                **kwargs):
        """
        Optimized ImageDataGenerator2D with performance improvements
        
        Original Parameters:
        :param df: Dataframe containing image path and classes
        :param batch_size: Size of batches
        :param data_dir: Directory containing images
        :param X_col: Column name for image paths
        :param Y_col: Column name for labels
        :param to_fit: Whether to return labels
        :param shuffle: Whether to shuffle data
        :param train: Whether in training mode (affects augmentations)
        :param augmentation_config: Configuration for augmentations
        :param drop_remainder: Whether to drop incomplete batches
        :param image_size: Target image size (assumes square images)
        :param num_channels: Number of channels in output
        :param get_paths: Whether to return image paths
        :param autoencoder_pair: Whether to return (X, X) for autoencoders
        :param label_format: 'one_hot' or 'class_indices'
        :param num_classes: Number of classes for one-hot encoding
        :param sampling_strategy: 'none', 'oversampling', 'undersampling'
        :param projection_mode: 'single' or 'multi' for different projection handling
        :param projection_shuffle: Whether to shuffle projections in multi mode
        :param padding_strategy: Strategy for remainder batches
        :param deterministic_padding: Use deterministic padding for reproducibility
        :param classifier_type: Type of classifier ('standard', 'staged', 'hierarchical')
        
        Bias Prevention Parameters:
        :param normalization_method: Intensity normalization method
            - 'percentile': Original percentile-based (default)
            - 'tanh_bounded': Tanh-bounded normalization (ELIMINATES BIAS)
            - 'z_score': Z-score normalization
            - 'l2_normalize': L2 normalization
            - 'robust': Robust z-score with tanh bounding
        
        New Optimization Parameters:
        :param enable_caching: Enable intelligent caching system
        :param cache_size_mb: Maximum cache size in MB
        :param max_workers: Number of worker threads for concurrent loading
        :param enable_memory_pool: Enable memory pooling for batch arrays
        :param prefetch_batches: Number of batches to prefetch ahead
        """
        super().__init__(**kwargs)
        
        # Original parameters
        self.df = df.copy()
        self.batch_size = batch_size
        if data_dir is None:
            data_dir = ""

        self.data_dir = data_dir
        self.X_col = X_col
        self.Y_col = Y_col
        self.to_fit = to_fit
        self.shuffle = shuffle
        self.train = train
        self.augmentation_config = augmentation_config
        self.image_size = image_size
        self.num_channels = num_channels
        self.get_paths = get_paths
        self.autoencoder_pair = autoencoder_pair
        self.label_format = label_format
        self.num_classes = num_classes
        self.projection_mode = projection_mode
        self.projection_shuffle = projection_shuffle
        self.padding_strategy = padding_strategy
        self.deterministic_padding = deterministic_padding
        self.drop_remainder = drop_remainder
        self.classifier_type = classifier_type
        
        # Bias prevention parameters
        self.normalization_method = normalization_method
        self.normalization_params = normalization_params if normalization_params is not None else {}
        
        # Initialize hierarchical label support
        self.is_hierarchical = classifier_type in ['staged', 'hierarchical']
        if self.is_hierarchical:
            if not HIERARCHICAL_LABELS_AVAILABLE:
                raise ImportError("Hierarchical labels module not available. Cannot use staged/hierarchical classifiers.")
            
            # Get hierarchy information
            self.hierarchy_info = get_head_info(NEUTROPHIL_HIERARCHY)
            
            # Define the mapping based on classifier type
            if classifier_type == 'staged':
                # For staged classifier: stage (binary) + subclass (4-class)
                self.head_mapping = {
                    'stage': 'coarse',    # Binary: early vs late
                    'subclass': 'stage'   # 4-class: M, MM, BN, SN
                }
            elif classifier_type == 'hierarchical':
                # For hierarchical classifier: same as staged but with contradiction penalty
                self.head_mapping = {
                    'stage': 'coarse',    # Binary: early vs late
                    'subclass': 'stage'   # 4-class: M, MM, BN, SN
                }
            
            print(f"Hierarchical data generator initialized for {classifier_type} classifier")
            print(f"Head mapping: {self.head_mapping}")
        else:
            self.hierarchy_info = None
            self.head_mapping = None
        
        # Optimization parameters
        self.enable_caching = enable_caching
        self.max_workers = max_workers
        self.enable_memory_pool = enable_memory_pool
        self.prefetch_batches = prefetch_batches
        
        # Initialize optimization components
        if self.enable_caching:
            self.cache_manager = get_global_cache_manager()
            self.image_loader = self.cache_manager.get_loader()
        else:
            self.cache_manager = None
            self.image_loader = None
        
        # Initialize batch processor
        self.batch_processor = BatchProcessor(
            batch_size=batch_size,
            image_size=(image_size, image_size),
            num_channels=num_channels,
            max_workers=max_workers,
            enable_memory_pool=enable_memory_pool
        )
        
        # Apply oversampling if requested
        print(f"Original dataset size: {len(self.df)}")
        if sampling_strategy and train:
            print("Applying oversampling to balance class distribution...")
            self.df = self._apply_oversampling(self.df, self.Y_col)
            print(f"Dataset size after oversampling: {len(self.df)}")
        else:
            print("Oversampling not applied or not in training mode, using original dataset size.")

        # Store original dataset size for improved remainder handling
        self.original_dataset_size = len(self.df)
        
        # Set effective dataset size based on drop_remainder
        if drop_remainder:
            self.n = (len(self.df) // self.batch_size) * self.batch_size
        else:
            self.n = len(self.df)

        if self.shuffle:
            self.shuffle_data()
        
        # Prefetching state
        self._prefetch_futures = {}
        self._prefetch_lock = threading.Lock()
        
        # Performance statistics
        self._stats = {
            'total_batches_loaded': 0,
            'total_load_time': 0.0,
            'cache_enabled': enable_caching,
            'concurrent_workers': max_workers
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Validate DataFrame on initialization
        self._validate_dataframe()

    def shuffle_data(self):
        """Shuffle the dataframe"""
        self.df = self.df.sample(frac=1).reset_index(drop=True)

    def on_epoch_end(self):
        """Called at the end of each epoch"""
        if self.shuffle:
            self.shuffle_data()
        
        # Print performance stats
        if self._stats['total_batches_loaded'] > 0:
            avg_time = self._stats['total_load_time'] / self._stats['total_batches_loaded']
            self.logger.info(f"Average batch load time: {avg_time:.3f}s")
            
            if self.image_loader:
                cache_stats = self.image_loader.get_cache_stats()
                self.logger.info(f"Cache hit rate: {cache_stats['hit_rate']:.2%}")

    def __getitem__(self, index):
        """Generate one batch of data with optimized loading"""
        start_time = time.time()
        
        # Validate batch index
        if index >= len(self):
            raise IndexError(f"Batch index {index} out of range. Only {len(self)} batches available.")
        
        start_idx = index * self.batch_size
        end_idx = min((index + 1) * self.batch_size, self.original_dataset_size)
        indexes = list(np.arange(start_idx, end_idx))
        actual_batch_size = len(indexes)
        
        # Handle remainder batch based on strategy
        if actual_batch_size < self.batch_size:
            if self.drop_remainder:
                raise IndexError(f"Batch {index} has size {actual_batch_size} but drop_remainder=True")
            elif self.padding_strategy == 'none':
                pass
            elif self.padding_strategy == 'repeat_last':
                last_idx = indexes[-1]
                while len(indexes) < self.batch_size:
                    indexes.append(last_idx)
            elif self.padding_strategy == 'cycle':
                cycle_idx = 0
                while len(indexes) < self.batch_size:
                    indexes.append(cycle_idx % self.original_dataset_size)
                    cycle_idx += 1
            elif self.padding_strategy == 'repeat_random':
                if self.deterministic_padding:
                    rng = np.random.RandomState(42 + index)
                    while len(indexes) < self.batch_size:
                        indexes.append(rng.choice(self.original_dataset_size))
                else:
                    while len(indexes) < self.batch_size:
                        indexes.append(random.choice(range(self.original_dataset_size)))
            else:
                raise ValueError(f"Unknown padding_strategy: {self.padding_strategy}")

        # Prefetch next batch if enabled
        if self.prefetch_batches > 0 and index + 1 < len(self):
            self._prefetch_next_batch(index + 1)

        # Generate batch data
        X = self._generate_X(indexes, actual_batch_size)

        if self.get_paths:
            paths = self._generate_paths(indexes)

        # Update statistics
        end_time = time.time()
        self._stats['total_batches_loaded'] += 1
        self._stats['total_load_time'] += (end_time - start_time)

        # Return appropriate data structure
        if self.to_fit:
            if self.get_paths:
                if self.autoencoder_pair:
                    return X, X, paths
                else:
                    y = self._generate_y(indexes, actual_batch_size)
                    return X, y, paths
            else:
                if self.autoencoder_pair:
                    return X, X
                else:
                    y = self._generate_y(indexes, actual_batch_size)
                    return X, y
        else:
            if self.get_paths:
                return X, paths
            else:
                return X

    def __len__(self):
        """Return the number of batches with improved drop_remainder handling."""
        if self.drop_remainder:
            return self.original_dataset_size // self.batch_size
        else:
            return int(np.ceil(self.original_dataset_size / float(self.batch_size)))
    
    def _generate_paths(self, indexes):
        """Generate file paths for given indexes with None checking"""
        paths = []
        for idx in indexes:
            filepath = self.df.iloc[idx][self.X_col]
            if filepath is not None and filepath != '':
                paths.append(filepath)
            else:
                raise ValueError(f"Invalid filepath at index {idx}: {filepath}. Check your DataFrame for missing or None values in column '{self.X_col}'.")
        return paths

    def _generate_X(self, indexes, actual_batch_size=None):
        """Generate X data with optimized concurrent loading"""
        # Determine output batch size
        if self.padding_strategy == 'none' and actual_batch_size is not None and actual_batch_size < self.batch_size:
            output_batch_size = actual_batch_size
        else:
            output_batch_size = self.batch_size

        # Get image paths with None checking
        image_paths = []
        for idx in indexes:
            filepath = self.df.iloc[idx][self.X_col]
            if filepath is not None and filepath != '':
                image_paths.append(os.path.join(self.data_dir, filepath))
            else:
                raise ValueError(f"Invalid filepath at index {idx}: {filepath}. Check your DataFrame for missing or None values in column '{self.X_col}'.")
        
        # Use optimized batch processor if enabled, otherwise fallback
        if self.enable_caching or self.max_workers > 1:
            try:
                X = self.batch_processor.process_batch_concurrent(
                    image_paths=image_paths,
                    load_func=self._load_raw_image,
                    process_func=self._process_image,
                    cache_loader=self.image_loader
                )
                
                # Ensure correct batch size
                if X.shape[0] != output_batch_size:
                    # Resize array if needed
                    X_resized = np.empty((output_batch_size, self.image_size, self.image_size, self.num_channels), dtype=np.float32)
                    copy_size = min(X.shape[0], output_batch_size)
                    X_resized[:copy_size] = X[:copy_size]
                    X = X_resized
                
                return X.astype(np.float32)
                
            except Exception as e:
                self.logger.error(f"Error in optimized batch loading: {e}")
                # Fallback to original implementation
                return self._generate_X_fallback(indexes, actual_batch_size)
        else:
            # Use original implementation if optimizations disabled
            return self._generate_X_fallback(indexes, actual_batch_size)

    def _generate_X_fallback(self, indexes, actual_batch_size=None):
        """Fallback to original X generation method"""
        if self.padding_strategy == 'none' and actual_batch_size is not None and actual_batch_size < self.batch_size:
            output_batch_size = actual_batch_size
        else:
            output_batch_size = self.batch_size
            
        X = np.empty((output_batch_size, self.image_size, self.image_size, self.num_channels))

        for i, idx in enumerate(indexes):
            try:
                filepath = self.df.iloc[idx][self.X_col]
                if filepath is not None and filepath != '':
                    X[i,] = self._load_2d_image(filepath)
                else:
                    raise ValueError(f"Invalid filepath at index {idx}: {filepath}. Check your DataFrame for missing or None values in column '{self.X_col}'.")
            except Exception as e:
                raise ValueError(f"Failed to load {self.df.iloc[idx][self.X_col]} at index {idx}: {e}")
        return X.astype(np.float32)

    def _generate_y(self, indexes, actual_batch_size=None):
        """Generate y data with support for variable batch sizes and hierarchical labels."""
        if self.padding_strategy == 'none' and actual_batch_size is not None and actual_batch_size < self.batch_size:
            output_batch_size = actual_batch_size
        else:
            output_batch_size = self.batch_size
        
        # Get flat labels first
        flat_labels = np.empty((output_batch_size), dtype=int)
        for i, idx in enumerate(indexes):
            flat_labels[i] = self.df.iloc[idx][self.Y_col]
        
        # Handle hierarchical labels for multi-output models
        if self.is_hierarchical:
            return self._generate_hierarchical_labels(flat_labels, output_batch_size)
        else:
            # Standard single-output labels
            if self.label_format == 'class_indices':
                return flat_labels
            else:
                return to_categorical(flat_labels, num_classes=self.num_classes)
    
    def _generate_hierarchical_labels(self, flat_labels, output_batch_size):
        """Generate hierarchical labels for multi-output models"""
        hierarchical_labels = {}
        
        for model_head, hierarchy_head in self.head_mapping.items():
            head_labels = np.empty((output_batch_size), dtype=int)
            
            for i, flat_label in enumerate(flat_labels):
                # Convert flat label (class index) to hierarchical labels
                # First convert index to class name
                class_names = ['M', 'MM', 'BN', 'SN']  # Standard neutrophil classes
                if flat_label >= len(class_names):
                    raise ValueError(f"Invalid class index {flat_label}, expected 0-{len(class_names)-1}")
                
                class_name = class_names[flat_label]
                
                # Convert to hierarchical format using the existing utility
                hierarchical = convert_flat_label_to_hierarchical(
                    class_name, self.hierarchy_info, source_head='stage'
                )
                
                # Extract the label for this specific head
                head_labels[i] = hierarchical[hierarchy_head]
            
            # Apply label format (one-hot or class indices)
            if self.label_format == 'class_indices':
                hierarchical_labels[model_head] = head_labels
            else:
                # One-hot encode based on the number of classes for this head
                num_classes_for_head = self.hierarchy_info[hierarchy_head]['num_classes']
                hierarchical_labels[model_head] = to_categorical(head_labels, num_classes=num_classes_for_head)
        
        return hierarchical_labels

    def _load_raw_image(self, image_path: str) -> np.ndarray:
        """Load raw image data"""
        img_sitk = sitk.ReadImage(image_path)
        return sitk.GetArrayFromImage(img_sitk)

    def _process_image(self, img_np: np.ndarray) -> np.ndarray:
        """Process a single image with all transformations"""
        # Handle different projection modes
        if self.projection_mode == 'single':
            img_np = img_np[:, -96:, 0]
            img_np = self._apply_augmentations(img_np)
            img_np = self._normalize_intensity(img_np, method=self.normalization_method, **self.normalization_params)
            
        elif self.projection_mode == 'multi':
            h = img_np.shape[0]
            projection_width = 96
            proj1 = img_np[:, :projection_width, 0]
            proj2 = img_np[:, projection_width:2*projection_width, 0]
            proj3 = img_np[:, -projection_width:, 0]
            
            # Process projections
            proj1 = self._apply_augmentations(proj1)
            proj1 = self._normalize_intensity(proj1, method=self.normalization_method, **self.normalization_params)
            proj2 = self._apply_augmentations(proj2)
            proj2 = self._normalize_intensity(proj2, method=self.normalization_method, **self.normalization_params)
            proj3 = self._apply_augmentations(proj3)
            proj3 = self._normalize_intensity(proj3, method=self.normalization_method, **self.normalization_params)
            
            projections = [proj1, proj2, proj3]
            
            if self.projection_shuffle and self.train:
                random.shuffle(projections)
            
            img_np = np.stack(projections, axis=-1)
        else:
            raise ValueError(f"Unknown projection_mode: {self.projection_mode}")

        # Pad and crop to target size
        target_size_2d = [self.image_size, self.image_size]
        img_np = pad_image_2d(img_np, padded_size=target_size_2d)
        img_np = crop_center_2d(img_np, crop_size=target_size_2d)


        # Ensure channel dimension matches expected num_channels
        if img_np.ndim == 2:
            img_np = np.expand_dims(img_np, axis=-1)
            if  self.num_channels == 1 :
                pass  # Already has 1 channel
            elif self.num_channels > 1:
                img_np = np.repeat(img_np, self.num_channels, axis=-1)
        elif img_np.ndim == 3 and img_np.shape[-1] != self.num_channels:
            if self.num_channels == 1 and img_np.shape[-1] > 1:
                img_np = img_np[..., :1]
            elif self.num_channels > 1 and img_np.shape[-1] == 1:
                img_np = np.repeat(img_np, self.num_channels, axis=-1)
            
        if img_np.shape[-1] != self.num_channels:
             raise ValueError(f"Image channel mismatch: expected {self.num_channels}, got {img_np.shape[-1]}")

        return img_np

    def _load_2d_image(self, image_path):
        """Original image loading method (kept for compatibility)"""
        full_path = os.path.join(self.data_dir, image_path)
        img_np = self._load_raw_image(full_path)
        return self._process_image(img_np)
    
    def _apply_augmentations(self, img_np):
        """Apply augmentations to a single 2D image"""
        if not self.train or not self.augmentation_config:
            return img_np
            
        for aug_config in self.augmentation_config:
            aug_name = aug_config.get('name')
            if aug_name:
                aug_params = {k: v for k, v in aug_config.items() if k != 'name'}
                
                try:
                    if aug_name == 'random_flip':
                        img_np = random_flip_2d(img_np, **aug_params)
                    elif aug_name == 'random_rotation':
                        img_np = random_rotation_2d(img_np, **aug_params)
                    elif aug_name == 'random_zoom':
                        img_np = random_zoom_2d(img_np, **aug_params)
                    elif aug_name == 'random_translation':
                        img_np = random_translation_2d(img_np, **aug_params)
                    elif aug_name == 'random_contrast':
                        img_np = random_contrast_2d(img_np, **aug_params)
                    elif aug_name == 'random_brightness':
                        img_np = random_brightness_2d(img_np, **aug_params)
                    else:
                        self.logger.warning(f"Unknown augmentation '{aug_name}' skipped")
                except NameError:
                    self.logger.warning(f"Augmentation function '{aug_name}' not available")
        return img_np
    
    def _normalize_intensity(self, img_np, method='percentile', **kwargs):
        """
        Normalize intensity of a single 2D image with multiple methods
        
        Args:
            img_np: Input image array
            method: Normalization method
                - 'percentile': Original percentile-based normalization
                - 'tanh_bounded': Tanh-bounded normalization (BIAS-FREE SOLUTION)
                - 'z_score': Z-score normalization
                - 'l2_normalize': L2 normalization
                - 'robust': Robust z-score with tanh bounding
            **kwargs: Method-specific parameters
        """
        if method == 'percentile':
            lp = kwargs.get('low_percentile', 75)
            hp = kwargs.get('high_percentile', 99)

            # Configurable percentile-based normalization
            low_percentile = kwargs.get('low_percentile', 75)
            high_percentile = kwargs.get('high_percentile', 99)
            out_range = kwargs.get('out_range', (0, 1))
            if isinstance(out_range, list):
                out_range = tuple(out_range)
            
            min_val, max_val = np.percentile(img_np, (low_percentile, high_percentile))
            if max_val > min_val:
                img_np = rescale_intensity(img_np, in_range=(min_val, max_val), out_range=out_range)
            else:
                fallback_value = kwargs.get('fallback_value', 0.5 if min_val != 0 else 0.0)
                img_np = np.full_like(img_np, fallback_value)
                
        elif method == 'tanh_bounded':
            # BIAS-FREE SOLUTION: Tanh-bounded normalization with configurable parameters
            # This method eliminates early/late dominance bias
            
            # Configurable parameters
            epsilon = kwargs.get('epsilon', 1e-7)
            scale_factor = kwargs.get('scale_factor', 1.0)
            output_range = kwargs.get('output_range', (0, 1))
            
            # Step 1: Add epsilon to prevent all-zero inputs
            img_np = img_np + epsilon
            
            # Step 2: Z-score normalize per image
            mean = np.mean(img_np)
            std = np.std(img_np)
            if std > epsilon:
                img_np = (img_np - mean) / std
            else:
                # Handle constant images
                img_np = np.zeros_like(img_np)
            
            # Step 3: Apply tanh with configurable scaling
            img_np = np.tanh(img_np * scale_factor)
            
            # Step 4: Scale to specified output range
            img_np = (img_np + 1.0) / 2.0  # First to [0, 1]
            if output_range != (0, 1):
                img_np = img_np * (output_range[1] - output_range[0]) + output_range[0]
            
        elif method == 'z_score':
            # Configurable z-score normalization
            epsilon = kwargs.get('epsilon', 1e-7)
            clip_range = kwargs.get('clip_range', (-3, 3))
            output_range = kwargs.get('output_range', (0, 1))
            
            img_np = img_np + epsilon
            mean = np.mean(img_np)
            std = np.std(img_np)
            if std > epsilon:
                img_np = (img_np - mean) / std
                # Clip extreme values
                img_np = np.clip(img_np, clip_range[0], clip_range[1])
                # Scale to output range
                clip_span = clip_range[1] - clip_range[0]
                img_np = (img_np - clip_range[0]) / clip_span
                if output_range != (0, 1):
                    img_np = img_np * (output_range[1] - output_range[0]) + output_range[0]
            else:
                fallback_value = kwargs.get('fallback_value', 0.5)
                img_np = np.full_like(img_np, fallback_value)
                
        elif method == 'l2_normalize':
            # Configurable L2 normalization per image
            epsilon = kwargs.get('epsilon', 1e-7)
            preserve_range = kwargs.get('preserve_range', True)
            output_range = kwargs.get('output_range', (0, 1))
            
            img_np = img_np + epsilon
            norm = np.linalg.norm(img_np.flatten())
            if norm > epsilon:
                img_np = img_np / norm
            else:
                img_np = np.full_like(img_np, 1.0 / np.sqrt(img_np.size))
            
            # Scale to output range if requested
            if preserve_range:
                img_np = (img_np - np.min(img_np)) / (np.max(img_np) - np.min(img_np) + epsilon)
                if output_range != (0, 1):
                    img_np = img_np * (output_range[1] - output_range[0]) + output_range[0]
            
        elif method == 'robust':
            # Configurable robust normalization with outlier handling
            epsilon = kwargs.get('epsilon', 1e-7)
            mad_factor = kwargs.get('mad_factor', 1.4826)  # Factor to make MAD consistent with std
            tanh_scale = kwargs.get('tanh_scale', 2.0)     # Scale factor for tanh
            output_range = kwargs.get('output_range', (0, 1))
            
            img_np = img_np + epsilon
            
            # Use median and MAD for robust statistics
            median = np.median(img_np)
            mad = np.median(np.abs(img_np - median))
            
            if mad > epsilon:
                # Robust z-score
                img_np = (img_np - median) / (mad_factor * mad)
                # Apply tanh for soft clipping with configurable scale
                img_np = np.tanh(img_np / tanh_scale)
                # Scale to output range
                img_np = (img_np + 1.0) / 2.0
                if output_range != (0, 1):
                    img_np = img_np * (output_range[1] - output_range[0]) + output_range[0]
            else:
                fallback_value = kwargs.get('fallback_value', 0.5)
                img_np = np.full_like(img_np, fallback_value)
                
        else:
            raise ValueError(f"Unknown normalization method: {method}")
            
        return img_np.astype(np.float32)
    
    def _apply_oversampling(self, df, oversample_col):
        """Apply oversampling to balance class distribution."""
        class_counts = df[oversample_col].value_counts().sort_index()
        print(f"Original class distribution:\n{class_counts}")
        
        max_count = class_counts.max()
        balanced_dfs = []
        
        for class_label in sorted(class_counts.index):
            count = class_counts[class_label]
            class_df = df[df[oversample_col] == class_label]
            
            if count < max_count:
                resampled_df = resample(
                    class_df,
                    replace=True,
                    n_samples=max_count,
                    random_state=42
                )
                balanced_dfs.append(resampled_df)
                print(f"Class {class_label}: {count} -> {max_count} samples")
            else:
                balanced_dfs.append(class_df)
                print(f"Class {class_label}: {count} samples (no change)")
        
        balanced_df = pd.concat(balanced_dfs, ignore_index=True)
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        print(f"Final class distribution:\n{balanced_df[oversample_col].value_counts().sort_index()}")
        return balanced_df

    def _prefetch_next_batch(self, next_index: int):
        """Prefetch the next batch asynchronously"""
        if next_index >= len(self):
            return
            
        with self._prefetch_lock:
            if next_index in self._prefetch_futures:
                return  # Already prefetching
            
            # Get indexes for next batch
            start_idx = next_index * self.batch_size
            end_idx = min((next_index + 1) * self.batch_size, self.original_dataset_size)
            indexes = list(np.arange(start_idx, end_idx))
            
            # Get image paths with None checking
            image_paths = []
            for idx in indexes:
                filepath = self.df.iloc[idx][self.X_col]
                if filepath is not None and filepath != '':
                    image_paths.append(os.path.join(self.data_dir, filepath))
                else:
                    # Skip prefetching for invalid paths rather than raising error
                    self.logger.warning(f"Skipping prefetch for invalid filepath at index {idx}: {filepath}")
                    return
            
            # Submit prefetch task
            if self.image_loader:
                self.image_loader.prefetch_batch(image_paths)

    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        stats = self._stats.copy()
        
        if self.image_loader:
            cache_stats = self.image_loader.get_cache_stats()
            stats.update(cache_stats)
        
        if self.batch_processor:
            processor_stats = self.batch_processor.get_stats()
            stats.update(processor_stats)
        
        return stats

    def _validate_dataframe(self):
        """Validate DataFrame for missing or invalid file paths"""
        if self.X_col not in self.df.columns:
            raise ValueError(f"Column '{self.X_col}' not found in DataFrame. Available columns: {list(self.df.columns)}")
        
        if self.Y_col not in self.df.columns:
            raise ValueError(f"Column '{self.Y_col}' not found in DataFrame. Available columns: {list(self.df.columns)}")
        
        # Check for None or empty file paths
        null_paths = self.df[self.X_col].isnull().sum()
        empty_paths = (self.df[self.X_col] == '').sum()
        
        if null_paths > 0:
            self.logger.warning(f"Found {null_paths} null file paths in column '{self.X_col}'")
            # Get indices of null paths for debugging
            null_indices = self.df[self.df[self.X_col].isnull()].index.tolist()
            self.logger.warning(f"Null path indices: {null_indices[:10]}...")  # Show first 10
            
        if empty_paths > 0:
            self.logger.warning(f"Found {empty_paths} empty file paths in column '{self.X_col}'")
            # Get indices of empty paths for debugging
            empty_indices = self.df[self.df[self.X_col] == ''].index.tolist()
            self.logger.warning(f"Empty path indices: {empty_indices[:10]}...")  # Show first 10
        
        if null_paths > 0 or empty_paths > 0:
            raise ValueError(
                f"DataFrame contains {null_paths} null and {empty_paths} empty file paths in column '{self.X_col}'. "
                f"Please clean your data before using the ImageDataGenerator."
            )
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'batch_processor'):
            self.batch_processor.shutdown()