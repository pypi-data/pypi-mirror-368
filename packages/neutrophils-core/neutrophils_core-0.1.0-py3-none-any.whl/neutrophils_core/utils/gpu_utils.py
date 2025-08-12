"""GPU configuration utilities."""

import tensorflow as tf


def setup_gpu(memory_limit_mb=None):
    """Configure GPU settings for TensorFlow.
    
    Args:
        memory_limit_mb: Optional memory limit in MB. If None, uses memory growth.
    """
    gpus = tf.config.experimental.list_physical_devices('GPU')

    if gpus:
        try:
            # Set memory growth for each GPU
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
                
                # Optionally set memory limit
                if memory_limit_mb:
                    tf.config.experimental.set_memory_limit(gpu, memory_limit_mb)
                    print(f"GPU memory limit set to {memory_limit_mb} MB")
            
            print(f"GPU memory growth enabled for {len(gpus)} GPU(s).")
            
            # Print available GPUs
            for i, gpu in enumerate(gpus):
                print(f"  GPU {i}: {gpu.name}")
                
        except RuntimeError as e:
            print(f"GPU setup error: {e}")  # Memory growth must be set before any tensors are allocated
    else:
        print("No GPUs found. Using CPU.")