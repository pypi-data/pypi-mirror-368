#!/usr/bin/env python3
"""
Optimized ImageDataGenerator3D that inherits from the original and overrides
performance-critical methods while maintaining the Keras workflow compatibility.

This implementation combines the best of both worlds:
- Maintains the original ImageDataGenerator3D API and Keras compatibility
- Incorporates tf.data.Dataset optimizations for significant performance gains
- Uses proper neutrophils_core.loader.augmentations_3d module
- Supports all original features (MIP, caching, contrastive pairs, etc.)
"""

import tensorflow as tf
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional
import multiprocessing as mp
import time
import logging
from concurrent.futures import ThreadPoolExecutor
import SimpleITK as sitk
from skimage.exposure import rescale_intensity

from tqdm import tqdm
# Import neutrophils-core modules
from .ImageDataGenerator3D import ImageDataGenerator3D
from . import augmentations_3d, data_utils

logger = logging.getLogger(__name__)


class OptimizedImageDataGenerator3D(ImageDataGenerator3D):
    """
    Optimized version of ImageDataGenerator3D that maintains Keras compatibility
    while providing significant performance improvements through tf.data.Dataset
    optimizations and parallel processing.
    
    Key optimizations:
    - tf.data.Dataset with prefetching and parallel processing
    - Optimized image loading with caching
    - GPU-accelerated augmentation pipeline
    - Memory-efficient batch processing
    - Maintains all original features and API compatibility
    """
    
    def __init__(self, 
                 df: pd.DataFrame,
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
                 intensity_input_percentiles: Tuple[float, float] = (1, 99),
                 intensity_out_range: Tuple[float, float] = (0, 1),
                 # New optimization parameters
                 use_tf_data_optimization: bool = True,
                 num_parallel_calls: int = None,
                 prefetch_buffer_size: int = None,
                 use_gpu_augmentation: bool = True,
                 memory_limit_mb: int = 2048,
                 is_debug: bool = False,
                 **kwargs):
        """
        Initialize optimized ImageDataGenerator3D.
        
        Args:
            All original ImageDataGenerator3D parameters plus:
            use_tf_data_optimization: Whether to use tf.data.Dataset optimizations
            num_parallel_calls: Number of parallel calls for data processing
            prefetch_buffer_size: Buffer size for prefetching
            use_gpu_augmentation: Whether to use GPU for augmentations
            memory_limit_mb: Memory limit for caching in MB
        """
        # Store drop_remainder before calling parent init
        self.drop_remainder = drop_remainder
        
        # Secure image loading: Check for path existence before proceeding
        if not is_debug:
            data_dir_path = Path(data_dir)
            
            # Add a progress bar for path validation
            tqdm.pandas(desc="Validating image paths")
            valid_mask = df[X_col].progress_apply(lambda x: (data_dir_path / str(x)).exists())
            
            if not valid_mask.all():
                invalid_count = (~valid_mask).sum()
                logger.warning(f"Found {invalid_count} missing image files. "
                               f"These entries will be removed from the dataframe.")
                df = df[valid_mask].reset_index(drop=True)

        # Initialize parent class
        super().__init__(
            df=df, batch_size=batch_size, data_dir=data_dir, classes=classes,
            X_col=X_col, Y_col=Y_col, to_fit=to_fit, shuffle=shuffle, train=train,
            mip=mip, augmentation_config=augmentation_config, drop_remainder=drop_remainder,
            image_size=image_size, get_paths=get_paths, autoencoder_pair=autoencoder_pair,
            contrastive_pair=contrastive_pair,
            intensity_input_percentiles=intensity_input_percentiles,
            intensity_out_range=intensity_out_range,
            **kwargs
        )
        
        # Optimization settings
        self.use_tf_data_optimization = use_tf_data_optimization
        self.num_parallel_calls = num_parallel_calls or min(mp.cpu_count(), 8)
        self.prefetch_buffer_size = prefetch_buffer_size or tf.data.AUTOTUNE
        self.use_gpu_augmentation = use_gpu_augmentation
        self.memory_limit_mb = memory_limit_mb
        self.is_debug = is_debug
        
        # Setup GPU memory management
        self._setup_gpu_memory()
        
        # Create optimized tf.data.Dataset if enabled
        if self.use_tf_data_optimization:
            self._create_optimized_dataset()
            self._use_optimized_dataset = True
            logger.info("Optimized tf.data.Dataset created for enhanced performance")
        else:
            self._use_optimized_dataset = False
            logger.info("Using original ImageDataGenerator3D implementation")
            
        self._first_epoch_progress = None
        self._is_first_epoch = True
    
    def _setup_gpu_memory(self):
        """Setup GPU memory management for efficient processing."""
        gpus = tf.config.list_physical_devices('GPU')
        if gpus and self.use_gpu_augmentation:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logger.info(f"GPU memory growth enabled for {len(gpus)} GPU(s)")
            except RuntimeError as e:
                logger.warning(f"GPU setup warning: {e}")
                self.use_gpu_augmentation = False
        else:
            self.use_gpu_augmentation = False
    
    def _create_optimized_dataset(self):
        """
        Create optimized tf.data.Dataset pipeline.
        This method defines processing functions locally to avoid capturing 'self'
        and creating reference cycles, which can cause memory leaks.
        """
        # Validate and filter DataFrame to ensure no NaN values in file paths
        valid_mask = self.df[self.X_col].notna() & (self.df[self.X_col] != '')
        if not valid_mask.all():
            invalid_count = (~valid_mask).sum()
            print(f"Warning: Found {invalid_count} invalid file paths, filtering them out")
            self.df = self.df[valid_mask].reset_index(drop=True)

        # Create file path dataset - ensure all paths are strings
        file_paths = [str(self.data_dir / str(path)) for path in self.df[self.X_col].values if pd.notna(path) and path != '']
        if not file_paths:
            raise ValueError("No valid file paths found in DataFrame")

        # --- Local function definitions to break reference cycle ---

        # Capture necessary attributes from 'self' into local variables
        image_size = self.image_size
        mip = self.mip
        train = self.train
        augmentation_config = self.augmentation_config
        use_gpu_augmentation = self.use_gpu_augmentation
        is_debug = self.is_debug
        intensity_input_percentiles = self.intensity_input_percentiles
        intensity_out_range = self.intensity_out_range

        def _load_raw_image(file_path_tensor: tf.Tensor) -> np.ndarray:
            """Loads and processes a single image."""
            try:
                if is_debug:
                    # In debug mode, generate a dummy image instead of reading from a file
                    shape = [image_size, image_size, image_size]
                    img_np = np.random.rand(*shape).astype(np.float32)
                else:
                    file_path_str = file_path_tensor.numpy().decode('utf-8')
                    img_sitk = sitk.ReadImage(file_path_str)
                    img_np = sitk.GetArrayFromImage(img_sitk).astype(np.float32)

                return data_utils.process_image_3d(
                    img_np,
                    image_size=image_size,
                    mip=mip,
                    train=train,
                    augmentation_config=augmentation_config,
                    intensity_input_percentiles=intensity_input_percentiles,
                    intensity_out_range=intensity_out_range
                )
            except Exception as e:
                file_path_str = "dummy_file" if is_debug else file_path_tensor.numpy().decode('utf-8')
                logger.error(f"Error processing image {file_path_str}: {e}", exc_info=True)
                shape = [image_size, image_size, 3] if mip else [image_size, image_size, image_size, 1]
                return np.zeros(shape, dtype=np.float32)

        @tf.function
        def _load_and_preprocess(file_path: tf.Tensor) -> tf.Tensor:
            """Wraps the loading function in tf.py_function."""
            tout_type = tf.float32
            image = tf.py_function(func=_load_raw_image, inp=[file_path], Tout=tout_type)
            shape = [image_size, image_size, 3] if mip else [image_size, image_size, image_size, 1]
            image.set_shape(shape)
            return image

        @tf.function
        def _apply_gpu_aug(image: tf.Tensor, strong: bool) -> tf.Tensor:
            """Applies GPU-based augmentations using the modular augmentation framework."""
            if augmentation_config and augmentation_config.get("order"):
                # Use the full augmentation pipeline if an order is specified
                aug_params = augmentation_config.copy()
                if strong:
                    # Modify params for strong augmentation if needed
                    if "noise" in aug_params:
                        aug_params["noise"]["std_factor"] = aug_params["noise"].get("strong_std_factor", 0.15)
                    if "brightness" in aug_params:
                        aug_params["brightness"]["brightness_range"] = aug_params["brightness"].get("strong_brightness_range", 0.2)
                    if "contrast" in aug_params:
                        aug_params["contrast"]["contrast_range"] = aug_params["contrast"].get("strong_contrast_range", (0.8, 1.2))
                    if "rotate" in aug_params:
                        aug_params["rotate"]["degree_max"] = aug_params["rotate"].get("strong_degree_max", 30.0)

                return augmentations_3d.apply_gpu_augmentations(
                    image,
                    augmentation_order=aug_params["order"],
                    augmentation_params=aug_params,
                    intensity_out_range=intensity_out_range
                )
            else:
                # Fallback to a default set of augmentations if no config is provided
                noise_std, brightness_range, contrast_range = (0.15, 0.2, 0.2) if strong else (0.05, 0.1, 0.1)
                rotation_angle_max = 30.0 if strong else 15.0

                default_params = {
                    "order": ["rotate", "noise", "brightness", "contrast"],
                    "rotate": {"degree_max": rotation_angle_max},
                    "noise": {"std_factor": noise_std},
                    "brightness": {"brightness_range": brightness_range},
                    "contrast": {"contrast_range": (1 - contrast_range, 1 + contrast_range)}
                }
                return augmentations_3d.apply_gpu_augmentations(
                    image,
                    augmentation_order=default_params["order"],
                    augmentation_params=default_params,
                    intensity_out_range=intensity_out_range
                )


        @tf.function
        def _create_contrastive_pair(image: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
            """Creates a pair of augmented images for contrastive learning."""
            if use_gpu_augmentation and not mip:
                return _apply_gpu_aug(image, True), _apply_gpu_aug(image, False)
            return image, image

        # --- Dataset construction using local functions ---
        dataset = tf.data.Dataset.from_tensor_slices(file_paths)
        if self.shuffle:
            dataset = dataset.shuffle(buffer_size=len(file_paths), reshuffle_each_iteration=True)
        
        dataset = dataset.map(_load_and_preprocess, num_parallel_calls=self.num_parallel_calls)
        
        # Caching is removed from here to be handled by the consumer of the dataset,
        # which allows for correct ordering with .take() and .repeat()
        
        if self.contrastive_pair:
            dataset = dataset.map(_create_contrastive_pair, num_parallel_calls=self.num_parallel_calls)
        elif self.autoencoder_pair:
            dataset = dataset.map(lambda x: (x, x))
        elif self.to_fit:
            if self.Y_col in self.df.columns and self.classes:
                labels_df = self.df.loc[self.df[self.X_col].isin([Path(p).name for p in file_paths])]
                labels = [self.classes[val] for val in labels_df[self.Y_col] if val in self.classes]
                if len(labels) == len(file_paths):
                    label_dataset = tf.data.Dataset.from_tensor_slices(labels)
                    dataset = tf.data.Dataset.zip((dataset, label_dataset))
                else:
                    logger.warning(f"Label count ({len(labels)}) doesn't match file count ({len(file_paths)}), proceeding without labels.")
        elif self.get_paths:
            # For inference with metadata, yield (image, metadata_dict)
            meta_dict = {'filepath': self.df[self.X_col].values.astype(str)}
            if self.Y_col in self.df.columns and self.classes:
                # Reverse map class indices to string names for metadata
                rev_classes = {v: k for k, v in self.classes.items()}
                # Get the integer class ID from the dataframe's Y_col
                class_ids = self.df[self.Y_col].map(self.classes)
                # Map integer IDs back to string names
                labels_str = class_ids.map(rev_classes).fillna('').values.astype(str)
                meta_dict['label'] = labels_str
            
            meta_dataset = tf.data.Dataset.from_tensor_slices(meta_dict)
            dataset = tf.data.Dataset.zip((dataset, meta_dataset))

        dataset = dataset.batch(self.batch_size, drop_remainder=self.drop_remainder)
        self._optimized_dataset = dataset.prefetch(self.prefetch_buffer_size)
        self._dataset_iterator = None
        
        # Add reference to dataset for cleanup
        self._dataset_ref = self._optimized_dataset

    def _estimate_cache_size(self) -> float:
        """Estimate cache size in MB."""
        # Rough estimate: image_size^3 * 4 bytes * num_samples / (1024^2)
        size_mb = (self.image_size ** 3 * 4 * len(self.df)) / (1024 ** 2)
        return size_mb
    
    def __getitem__(self, index: int):
        """
        Override the original __getitem__ method to use optimized dataset when enabled.
        
        Args:
            index: Batch index
            
        Returns:
            Batch data in the same format as original ImageDataGenerator3D
        """
        if self.use_tf_data_optimization and self._use_optimized_dataset:
            if self._is_first_epoch and self.train:
                if self._first_epoch_progress is None:
                    # The progress bar is now for the first epoch warm-up, not caching
                    self._first_epoch_progress = tqdm(total=len(self), desc="First Epoch Warm-up")
                self._first_epoch_progress.update(1)

            batch = self._get_optimized_batch(index)
            
            if self._is_first_epoch and self._first_epoch_progress is not None and self._first_epoch_progress.n >= self._first_epoch_progress.total:
                self._first_epoch_progress.close()
                self._first_epoch_progress = None
                self._is_first_epoch = False

            return batch
        else:
            # Fall back to original implementation
            return super().__getitem__(index)
    
    def _get_optimized_batch(self, index: int):
        """Get batch using optimized tf.data.Dataset."""
        # Initialize iterator if needed
        if self._dataset_iterator is None:
            self._dataset_iterator = iter(self._optimized_dataset)
        
        try:
            batch = next(self._dataset_iterator)
            
            # Convert TensorFlow tensors to NumPy arrays for compatibility
            if isinstance(batch, tuple):
                # Handle cases where the dataset yields tuples (e.g., (data, label) or (data, metadata))
                if len(batch) == 2:
                    x, y = batch
                    x_np = x.numpy()

                    if self.contrastive_pair or self.autoencoder_pair:
                        # (x1, x2) for contrastive/autoencoder
                        return x_np, y.numpy()
                    
                    elif self.to_fit:
                        # (x, y) for supervised learning
                        y_np = y.numpy()
                        if len(self.classes) > 1 and y_np.ndim == 1:
                            from tensorflow.keras.utils import to_categorical
                            y_np = to_categorical(y_np, num_classes=len(self.classes))
                        return x_np, y_np

                    elif self.get_paths:
                        # (x, meta_dict) for inference
                        # y is a dictionary of tensors
                        y_np = {k: v.numpy() for k, v in y.items()}
                        return x_np, y_np
                    
                    else:
                        # Fallback for any other tuple of 2
                        return x_np, y.numpy() if hasattr(y, 'numpy') else y
                
                else:
                    # Handle other tuple formats (e.g., > 2 items)
                    return tuple(t.numpy() if hasattr(t, 'numpy') else t for t in batch)
            else:
                # Single tensor (e.g., inference without get_paths)
                return batch.numpy()
                
        except (StopIteration, tf.errors.OutOfRangeError):
            # Reset iterator when dataset is exhausted
            self.on_epoch_end()
            return self._get_optimized_batch(index)
    
    def on_epoch_end(self):
        """Called at the end of each epoch."""
        super().on_epoch_end()
        
        # Reset optimized dataset iterator
        if self._use_optimized_dataset:
            self._dataset_iterator = iter(self._optimized_dataset)
        
        if self._first_epoch_progress is not None:
            self._first_epoch_progress.close()
            self._first_epoch_progress = None
        self._is_first_epoch = False
    
    def cleanup_memory(self):
        """Explicitly cleanup memory references to break cycles."""
        try:
            # Clear dataset iterator
            if hasattr(self, '_dataset_iterator') and self._dataset_iterator is not None:
                del self._dataset_iterator
                self._dataset_iterator = None
            
            # Clear dataset reference
            if hasattr(self, '_optimized_dataset'):
                del self._optimized_dataset
                self._optimized_dataset = None
            
            if hasattr(self, '_dataset_ref'):
                del self._dataset_ref
                self._dataset_ref = None
            
            # Clear progress bar
            if hasattr(self, '_first_epoch_progress') and self._first_epoch_progress is not None:
                self._first_epoch_progress.close()
                self._first_epoch_progress = None
            
            # Clear image cache
            self.clear_image_cache()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            logger.info("OptimizedImageDataGenerator3D memory cleanup completed")
            
        except Exception as e:
            logger.warning(f"Error during memory cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure proper cleanup."""
        try:
            self.cleanup_memory()
        except Exception:
            pass  # Ignore errors during destruction
    
    def clear_image_cache(self):
        """Clear the image cache to release memory."""
        if self._image_cache is not None:
            self._image_cache.clear()
            logger.info("Image cache cleared")
    
    def benchmark_performance(self, num_batches: int = 10) -> Dict[str, float]:
        """
        Benchmark data loading performance.
        
        Args:
            num_batches: Number of batches to benchmark
            
        Returns:
            Performance metrics dictionary
        """
        logger.info(f"Benchmarking OptimizedImageDataGenerator3D with {num_batches} batches...")
        
        # Warm up
        for i in range(min(2, num_batches)):
            _ = self[i]
        
        # Benchmark
        start_time = time.time()
        batch_times = []
        
        for i in range(num_batches):
            batch_start = time.time()
            batch_data = self[i]
            
            # Force evaluation
            if isinstance(batch_data, tuple):
                for data in batch_data:
                    if hasattr(data, 'mean'):
                        _ = data.mean()
                    elif isinstance(data, np.ndarray):
                        _ = np.mean(data)
            else:
                if hasattr(batch_data, 'mean'):
                    _ = batch_data.mean()
                elif isinstance(batch_data, np.ndarray):
                    _ = np.mean(data)
            
            batch_time = time.time() - batch_start
            batch_times.append(batch_time)
            
            if i % 5 == 0:
                logger.info(f"Batch {i+1}/{num_batches}: {batch_time:.4f}s")
        
        total_time = time.time() - start_time
        
        metrics = {
            'total_time': total_time,
            'avg_batch_time': np.mean(batch_times),
            'std_batch_time': np.std(batch_times),
            'min_batch_time': np.min(batch_times),
            'max_batch_time': np.max(batch_times),
            'throughput_samples_per_sec': (num_batches * self.batch_size) / total_time
        }
        
        logger.info("OptimizedImageDataGenerator3D Performance Results:")
        for key, value in metrics.items():
            logger.info(f"  {key}: {value:.4f}")
        
        return metrics
    
    def get_tf_dataset(self) -> tf.data.Dataset:
        """
        Get the underlying tf.data.Dataset for direct use with tf.keras.Model.fit().
        
        Returns:
            tf.data.Dataset optimized for training
        """
        if self._use_optimized_dataset:
            return self._optimized_dataset
        else:
            raise ValueError("tf.data optimization is not enabled. Set use_tf_data_optimization=True")
    
    def disable_optimization(self):
        """Disable tf.data optimization and fall back to original implementation."""
        self._use_optimized_dataset = False
        logger.info("Disabled tf.data optimization, using original implementation")
    
    def enable_optimization(self):
        """Enable tf.data optimization."""
        if self.use_tf_data_optimization:
            self._use_optimized_dataset = True
            logger.info("Enabled tf.data optimization")
        else:
            logger.warning("Cannot enable optimization: use_tf_data_optimization=False")
    
    def generate_positive_pairs(self, batch_size: int = None):
        """
        Generate positive pairs for contrastive learning.
        This method provides compatibility with embedding visualization code.
        
        Args:
            batch_size: Batch size (uses generator's batch_size if None)
            
        Returns:
            Tuple of (X1, X2) where X1 and X2 are augmented versions of the same images
        """
        if batch_size is None:
            batch_size = self.batch_size
        
        # Get a batch using the optimized dataset if available
        if self._use_optimized_dataset:
            batch = self._get_optimized_batch(0)
            if isinstance(batch, tuple) and len(batch) == 2:
                X1, X2 = batch
                return X1, X2
            else:
                # If not contrastive pairs, duplicate the batch
                return batch, batch
        else:
            # Fall back to parent class method if available
            if hasattr(super(), 'generate_positive_pairs'):
                return super().generate_positive_pairs(batch_size)
            else:
                # Create contrastive pairs manually
                batch = self[0]  # Get first batch
                if isinstance(batch, tuple) and len(batch) == 2:
                    X1, X2 = batch
                    return X1, X2
                else:
                    # If not contrastive pairs, duplicate the batch
                    return batch, batch
    
    def get_contrastive_batch(self):
        """
        Get a contrastive batch in the format expected by embedding visualization.
        
        Returns:
            Dictionary with 'X1', 'X2', and optionally 'labels'
        """
        batch = self[0]  # Get first batch
        
        if isinstance(batch, tuple) and len(batch) == 2:
            if self.contrastive_pair:
                # Contrastive pairs: (X1, X2)
                X1, X2 = batch
                return {'X1': X1, 'X2': X2, 'type': 'contrastive'}
            elif self.to_fit:
                # Supervised learning: (X, y)
                X, y = batch
                return {'X1': X, 'X2': X, 'labels': y, 'type': 'supervised'}
            else:
                # Other tuple format
                X1, X2 = batch
                return {'X1': X1, 'X2': X2, 'type': 'unknown'}
        else:
            # Single tensor
            return {'X1': batch, 'X2': batch, 'type': 'single'}
    
    def get_sample_batch(self, num_samples: int = None):
        """
        Get a sample batch for visualization purposes.
        
        Args:
            num_samples: Number of samples (uses batch_size if None)
            
        Returns:
            Dictionary with sample data
        """
        if num_samples is None:
            num_samples = min(self.batch_size, 8)  # Limit for visualization
        
        # Get a batch
        batch_data = self.get_contrastive_batch()
        
        # Limit to requested number of samples
        for key in ['X1', 'X2', 'labels']:
            if key in batch_data and batch_data[key] is not None:
                if hasattr(batch_data[key], '__len__') and len(batch_data[key]) > num_samples:
                    batch_data[key] = batch_data[key][:num_samples]
        
        return batch_data


# Convenience function for creating optimized generators
def create_optimized_labeled_generator(df: pd.DataFrame,
                                     batch_size: int,
                                     data_dir: Union[str, Path],
                                     classes: Dict[str, int],
                                     **kwargs) -> OptimizedImageDataGenerator3D:
    """
    Create an optimized data generator for labeled data (supervised learning).
    
    Args:
        df: DataFrame with image paths and labels
        batch_size: Batch size
        data_dir: Data directory
        classes: Class name to index mapping
        **kwargs: Additional arguments for OptimizedImageDataGenerator3D
        
    Returns:
        Configured OptimizedImageDataGenerator3D for supervised learning
    """
    # Set default optimization settings if not provided
    default_kwargs = {
        'to_fit': True,
        'use_tf_data_optimization': True,
    }
    
    # Update defaults with provided kwargs (kwargs take precedence)
    final_kwargs = {**default_kwargs, **kwargs}
    
    return OptimizedImageDataGenerator3D(
        df=df,
        batch_size=batch_size,
        data_dir=data_dir,
        classes=classes,
        **final_kwargs
    )


def create_optimized_contrastive_generator(df: pd.DataFrame,
                                         batch_size: int,
                                         data_dir: Union[str, Path],
                                         **kwargs) -> OptimizedImageDataGenerator3D:
    """
    Create an optimized data generator for contrastive learning.
    
    Args:
        df: DataFrame with image paths (labels not required)
        batch_size: Batch size
        data_dir: Data directory
        **kwargs: Additional arguments for OptimizedImageDataGenerator3D
        
    Returns:
        Configured OptimizedImageDataGenerator3D for contrastive learning
    """
    # Set default optimization settings if not provided
    default_kwargs = {
        'to_fit': False,
        'contrastive_pair': True,
        'train': True,  # Enable augmentations for contrastive learning
        'use_tf_data_optimization': True,
    }
    
    # Update defaults with provided kwargs (kwargs take precedence)
    final_kwargs = {**default_kwargs, **kwargs}
    
    return OptimizedImageDataGenerator3D(
        df=df,
        batch_size=batch_size,
        data_dir=data_dir,
        **final_kwargs
    )
