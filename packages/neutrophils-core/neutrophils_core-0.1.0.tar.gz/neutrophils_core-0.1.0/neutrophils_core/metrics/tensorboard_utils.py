"""TensorBoard logging utilities."""

import os
import numpy as np
import tensorflow as tf
import io
import contextlib


def setup_tensorboard_logging(log_dir, config=None):
    """
    Unified TensorBoard setup function to prevent GraphDef conflicts
    
    Args:
        log_dir: Directory for TensorBoard logs
        config: Configuration dictionary for logging
    
    Returns:
        tuple: (tensorboard_callback, file_writer)
    """
    print(f"Setting up TensorBoard logging for: {log_dir}")
    
    # Clean up any existing conflicting files
    if os.path.exists(log_dir):
        existing_files = [f for f in os.listdir(log_dir) if f.startswith('events.out.tfevents')]
        if existing_files:
            print(f"Warning: Found {len(existing_files)} existing TensorBoard event files")
            for event_file in existing_files:
                try:
                    os.remove(os.path.join(log_dir, event_file))
                except Exception as e:
                    print(f"Warning: Could not remove {event_file}: {e}")
    
    os.makedirs(log_dir, exist_ok=True)
    
    # Determine if this is a staged/hierarchical model from config
    classifier_type = 'standard'
    if config and 'model' in config:
        model_config = config['model']
        if 'classifier' in model_config:
            classifier_config = model_config['classifier']
            classifier_type = classifier_config.get('type', 'standard')
    
    # Create TensorBoard callback with metric renaming for staged/hierarchical models
    if classifier_type in ['staged', 'hierarchical']:
        print(f"Detected {classifier_type} model - configuring TensorBoard to rename subclass metrics to standard names")
        tensorboard_callback = FilteredTensorBoard(
            log_dir=log_dir,
            histogram_freq=1,
            write_graph=False,
            write_images=False,
            update_freq='epoch',
            profile_batch=0,
            classifier_type=classifier_type
        )
    else:
        tensorboard_callback = tf.keras.callbacks.TensorBoard(
            log_dir=log_dir,
            histogram_freq=1,
            write_graph=False,
            write_images=False,
            update_freq='epoch',
            profile_batch=0
        )
    
    # Create file writer for custom summaries
    file_writer = tf.summary.create_file_writer(log_dir)
    
    # Log configuration if provided
    if config:
        with file_writer.as_default():
            config_text = "# 2D Neutrophils Classifier Configuration\n\n"
            
            # Format configurations as markdown
            for section_name, section_config in config.items():
                config_text += f"## {section_name.title()} Configuration\n\n"
                if isinstance(section_config, dict):
                    for key, value in section_config.items():
                        config_text += f"- **{key}**: {value}\n"
                else:
                    config_text += f"- {section_config}\n"
                config_text += "\n"
            
            tf.summary.text("configuration", config_text, step=0)
    
    return tensorboard_callback, file_writer


class FilteredTensorBoard(tf.keras.callbacks.TensorBoard):
    """
    Custom TensorBoard callback that renames subclass metrics to standard names for staged/hierarchical models.
    
    Since Keras automatically prefixes metrics with output names (e.g., subclass_accuracy),
    this callback renames them to standard names (e.g., accuracy) while keeping stage metrics.
    """
    
    def __init__(self, classifier_type='staged', **kwargs):
        super().__init__(**kwargs)
        self.classifier_type = classifier_type
        print(f"FilteredTensorBoard: Initialized for {classifier_type} model")
        print(f"FilteredTensorBoard: Will rename subclass metrics to standard names and keep stage metrics")
    
    def on_epoch_end(self, epoch, logs=None):
        """Rename subclass metrics to standard names while keeping stage metrics."""
        if logs is None:
            logs = {}
        
        # Create renamed logs
        renamed_logs = {}
        
        for key, value in logs.items():
            # Rename subclass metrics to standard classification metric names
            if key.startswith('subclass_'):
                # Remove 'subclass_' prefix to get standard metric name
                standard_name = key.replace('subclass_', '')
                renamed_logs[standard_name] = value
            elif key.startswith('val_subclass_'):
                # Remove 'subclass_' from validation metrics
                standard_name = key.replace('val_subclass_', 'val_')
                renamed_logs[standard_name] = value
            # Keep stage metrics as they are (binary classification metrics)
            elif key.startswith('stage_') or key.startswith('val_stage_'):
                renamed_logs[key] = value
            # Keep all other metrics (including losses)
            else:
                renamed_logs[key] = value
        
        # Log information about renaming (only on first epoch)
        if epoch == 0:
            renamed_metrics = []
            for key in logs.keys():
                if key.startswith('subclass_'):
                    standard_name = key.replace('subclass_', '')
                    renamed_metrics.append(f"{key} -> {standard_name}")
                elif key.startswith('val_subclass_'):
                    standard_name = key.replace('val_subclass_', 'val_')
                    renamed_metrics.append(f"{key} -> {standard_name}")
            
            if renamed_metrics:
                print(f"FilteredTensorBoard: Renamed subclass metrics to standard names:")
                for rename in renamed_metrics:
                    print(f"  {rename}")
                print(f"FilteredTensorBoard: Also kept stage metrics for hierarchical information")
        
        # Call parent with renamed logs
        super().on_epoch_end(epoch, renamed_logs)


class ImageCallback(tf.keras.callbacks.Callback):
    """Custom callback to log input images to TensorBoard during training"""
    # TODO: add confusion matrix plotting on each epoch end
    
    def __init__(self, logdir, data, class_id_to_name, n_images=10):
        super().__init__()
        self.logdir = logdir
        self.n_images = n_images
        self.class_id_to_name = class_id_to_name
        
        # Extract and prepare images and labels
        if isinstance(data, tuple) and len(data) == 2:
            images, labels = data
            self.images = np.array(images[:n_images]) if isinstance(images, list) else np.array(images[:n_images])
            
            # Handle labels (could be one-hot encoded or class IDs)
            if len(labels.shape) > 1:  # One-hot encoded
                self.labels = np.argmax(labels[:n_images], axis=1)
            else:  # Already class IDs
                self.labels = labels[:n_images]
        else:
            raise ValueError("Data should be a tuple of (images, labels)")
        
        # Handle multi-channel images
        if len(self.images.shape) == 4 and self.images.shape[-1] > 1:
            num_channels = self.images.shape[-1]
            combined_images = []
            
            for i in range(len(self.images)):
                channels = [self.images[i, :, :, ch] for ch in range(num_channels)]
                combined_image = np.concatenate(channels, axis=1)
                combined_image = np.expand_dims(combined_image, axis=-1)
                combined_images.append(combined_image)
            
            self.images = np.array(combined_images)
        elif len(self.images.shape) == 3:
            self.images = np.expand_dims(self.images, axis=-1)
        
        # Normalize images
        if self.images.max() > 1.0:
            self.images = self.images / 255.0
        
        self.writer = tf.summary.create_file_writer(logdir)
    
    def on_train_begin(self, logs=None):
        """Log input images at the beginning of training"""
        with self.writer.as_default():
            class_groups = {}
            for i, label in enumerate(self.labels):
                class_name = self.class_id_to_name.get(label, f"Class_{label}")
                if class_name not in class_groups:
                    class_groups[class_name] = []
                class_groups[class_name].append(i)
            
            for class_name, image_indices in class_groups.items():
                class_images = np.stack([self.images[i] for i in image_indices], axis=0)
                tf.summary.image(
                    name=f"input_samples_train/{class_name}",
                    data=class_images,
                    max_outputs=len(class_images),
                    step=0
                )