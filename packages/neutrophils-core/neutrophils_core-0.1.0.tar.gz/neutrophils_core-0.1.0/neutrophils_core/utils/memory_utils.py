#!/usr/bin/env python3
"""
Memory Management Utilities for SimCLR Training

This module provides utilities to manage TensorFlow memory leaks and optimize
memory usage during SimCLR training.
"""

import gc
import time
import os
import tensorflow as tf
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TensorFlowMemoryManager:
    """
    Comprehensive TensorFlow memory management utility.
    """
    
    @staticmethod
    def aggressive_cleanup():
        """
        Perform aggressive TensorFlow memory cleanup.
        """
        logger.info("Starting aggressive TensorFlow memory cleanup...")
        
        # 1. Clear Keras backend session
        tf.keras.backend.clear_session()
        
        # 2. Reset computational graph
        try:
            tf.compat.v1.reset_default_graph()
        except AttributeError:
            pass  # TF 2.x doesn't have this in some configurations
        
        # 3. Clear any cached operations
        try:
            tf.compat.v1.get_default_session().close()
        except (AttributeError, TypeError):
            pass  # No active session or TF 2.x
        
        # 4. Force GPU memory cleanup
        TensorFlowMemoryManager._reset_gpu_memory()
        
        # 5. Multiple garbage collection passes
        for i in range(5):
            collected = gc.collect()
            logger.debug(f"GC pass {i+1}: collected {collected} objects")
            time.sleep(0.2)
        
        # 6. Wait for cleanup to propagate
        time.sleep(1)
        logger.info("TensorFlow memory cleanup completed")
    
    @staticmethod
    def _reset_gpu_memory():
        """
        Reset GPU memory allocation.
        """
        try:
            # Get GPU devices
            gpus = tf.config.list_physical_devices('GPU')
            if not gpus:
                return
            
            logger.info(f"Resetting memory for {len(gpus)} GPU(s)")
            
            # For each GPU, try to reset memory growth
            for i, gpu in enumerate(gpus):
                try:
                    # Reset memory growth
                    tf.config.experimental.set_memory_growth(gpu, True)
                    logger.debug(f"Reset memory growth for GPU {i}: {gpu.name}")
                except RuntimeError as e:
                    logger.warning(f"Could not reset memory growth for GPU {i}: {e}")
                except Exception as e:
                    logger.warning(f"Unexpected error resetting GPU {i} memory: {e}")
                    
        except Exception as e:
            logger.warning(f"Error during GPU memory reset: {e}")
    
    @staticmethod
    def clear_session_and_rebuild():
        """
        Clear session and rebuild TensorFlow environment from scratch.
        """
        logger.info("Clearing TensorFlow session and rebuilding...")
        
        # Clear everything
        TensorFlowMemoryManager.aggressive_cleanup()
        
        # Reinitialize GPU configuration
        try:
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logger.info(f"Reinitialized {len(gpus)} GPU(s) with memory growth")
        except Exception as e:
            logger.warning(f"Error reinitializing GPUs: {e}")

class DataGeneratorMemoryManager:
    """
    Memory management utilities for data generators.
    """
    
    @staticmethod
    def cleanup_generator(generator):
        """
        Cleanup a data generator and its associated resources.
        """
        if generator is None:
            return
            
        logger.info("Cleaning up data generator...")
        
        try:
            # Call custom cleanup if available
            if hasattr(generator, 'cleanup_memory'):
                generator.cleanup_memory()
                logger.debug("Called generator's cleanup_memory method")
            
            # Clear specific attributes that might hold references
            attrs_to_clear = [
                '_dataset_iterator', '_optimized_dataset', '_dataset_ref',
                '_first_epoch_progress', '_image_cache'
            ]
            
            for attr in attrs_to_clear:
                if hasattr(generator, attr):
                    try:
                        delattr(generator, attr)
                        logger.debug(f"Cleared generator attribute: {attr}")
                    except Exception as e:
                        logger.warning(f"Error clearing attribute {attr}: {e}")
            
            # Force garbage collection
            del generator
            gc.collect()
            
            logger.info("Data generator cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during generator cleanup: {e}")

class ModelMemoryManager:
    """
    Memory management utilities for TensorFlow models.
    """
    
    @staticmethod
    def cleanup_model(model):
        """
        Cleanup a TensorFlow model and its resources.
        """
        if model is None:
            return
            
        logger.info("Cleaning up TensorFlow model...")
        
        try:
            # Clear model weights and internal state
            if hasattr(model, 'reset_states'):
                model.reset_states()
            
            # Delete the model
            del model
            
            # Force garbage collection
            gc.collect()
            
            logger.info("Model cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during model cleanup: {e}")

class TrainingMemoryManager:
    """
    Comprehensive memory management for training loops.
    """
    
    def __init__(self):
        self.cleanup_managers = [
            TensorFlowMemoryManager,
            DataGeneratorMemoryManager,
            ModelMemoryManager
        ]
    
    def cleanup_training_iteration(self, **kwargs):
        """
        Comprehensive cleanup after a training iteration.
        
        Args:
            **kwargs: Dictionary containing objects to cleanup:
                - generator: Data generator
                - model: TensorFlow model
                - simclr_model: SimCLR model
                - encoder: Encoder model
                - optimizer: Optimizer
                - dataset: Dataset object
        """
        logger.info("Starting comprehensive training iteration cleanup...")
        
        # Cleanup individual components
        generator = kwargs.get('generator')
        if generator:
            DataGeneratorMemoryManager.cleanup_generator(generator)
        
        # Cleanup models
        for model_key in ['model', 'simclr_model', 'encoder']:
            model = kwargs.get(model_key)
            if model:
                ModelMemoryManager.cleanup_model(model)
        
        # Cleanup other objects
        for obj_key in ['optimizer', 'dataset']:
            obj = kwargs.get(obj_key)
            if obj:
                try:
                    del obj
                    logger.debug(f"Deleted {obj_key}")
                except Exception as e:
                    logger.warning(f"Error deleting {obj_key}: {e}")
        
        # Aggressive TensorFlow cleanup
        TensorFlowMemoryManager.clear_session_and_rebuild()
        
        logger.info("Comprehensive cleanup completed")
    
    def monitor_memory_usage(self, stage="") -> Optional[float]:
        """
        Monitor and log current memory usage.
        
        Returns:
            Memory usage in GB, or None if monitoring failed
        """
        try:
            import psutil
            process = psutil.Process()
            mem_info = process.memory_info()
            mem_gb = mem_info.rss / (1024 ** 3)
            logger.info(f"Memory usage {stage}: {mem_gb:.3f} GB")
            return mem_gb
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
            return None
        except Exception as e:
            logger.error(f"Error monitoring memory: {e}")
            return None

def setup_memory_efficient_training():
    """
    Setup TensorFlow for memory-efficient training.
    """
    logger.info("Setting up memory-efficient TensorFlow configuration...")
    
    # Configure GPU memory growth
    try:
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logger.info(f"Enabled memory growth for {len(gpus)} GPU(s)")
    except Exception as e:
        logger.warning(f"Could not configure GPU memory growth: {e}")
    
    # Set TensorFlow logging level to reduce memory overhead
    tf.get_logger().setLevel('ERROR')
    
    # Disable XLA JIT compilation by default (can cause memory issues)
    os.environ.setdefault('TF_XLA_FLAGS', '--tf_xla_enable_xla_devices=false')
    
    logger.info("Memory-efficient TensorFlow configuration completed")

def get_memory_usage_summary() -> Dict[str, Any]:
    """
    Get comprehensive memory usage summary.
    
    Returns:
        Dictionary with memory usage information
    """
    summary = {}
    
    try:
        import psutil
        
        # System memory
        mem = psutil.virtual_memory()
        summary['system'] = {
            'total_gb': mem.total / (1024 ** 3),
            'available_gb': mem.available / (1024 ** 3),
            'percent_used': mem.percent,
            'used_gb': mem.used / (1024 ** 3)
        }
        
        # Process memory
        process = psutil.Process()
        proc_mem = process.memory_info()
        summary['process'] = {
            'rss_gb': proc_mem.rss / (1024 ** 3),
            'vms_gb': proc_mem.vms / (1024 ** 3)
        }
        
        # GPU memory (if available)
        try:
            import pynvml
            pynvml.nvmlInit()
            gpu_count = pynvml.nvmlDeviceGetCount()
            
            summary['gpu'] = []
            for i in range(gpu_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                summary['gpu'].append({
                    'id': i,
                    'total_gb': mem_info.total / (1024 ** 3),
                    'used_gb': mem_info.used / (1024 ** 3),
                    'free_gb': mem_info.free / (1024 ** 3),
                    'percent_used': (mem_info.used / mem_info.total) * 100
                })
                
        except ImportError:
            summary['gpu'] = "pynvml not available"
        except Exception as e:
            summary['gpu'] = f"GPU monitoring error: {e}"
            
    except ImportError:
        summary['error'] = "psutil not available for memory monitoring"
    except Exception as e:
        summary['error'] = f"Memory monitoring error: {e}"
    
    return summary