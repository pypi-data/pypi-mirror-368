#!/usr/bin/env python3
"""
Utilities for handling multi-output models (staged and hierarchical classifiers).
"""

import numpy as np
import tensorflow as tf


def transform_labels_for_multihead(labels, num_classes=4, label_format='one_hot'):
    """
    Transform single labels to multi-head format for staged/hierarchical models.
    
    Args:
        labels: Input labels (either integer indices or one-hot encoded)
        num_classes: Number of classes (default=4 for M,MM,BN,SN)
        label_format: Format of input labels ('class_indices' or 'one_hot')
        
    Returns:
        Dictionary with 'stage' and 'subclass' labels
    """
    # Convert to numpy if tensorflow tensor
    if tf.is_tensor(labels):
        labels = labels.numpy()
    
    # Convert to one-hot if needed
    if label_format == 'class_indices' or len(labels.shape) == 1:
        labels_onehot = tf.keras.utils.to_categorical(labels, num_classes)
    else:
        labels_onehot = labels
    
    # Stage labels: M,MM (0,1) -> Early (0), BN,SN (2,3) -> Late (1)
    stage_labels = np.zeros((len(labels_onehot), 2))
    for i, label in enumerate(labels_onehot):
        class_idx = np.argmax(label)
        if class_idx in [0, 1]:  # M, MM
            stage_labels[i] = [1, 0]  # Early
        else:  # BN, SN
            stage_labels[i] = [0, 1]  # Late
    
    return {
        'stage': stage_labels,
        'subclass': labels_onehot
    }


def create_multihead_data_generator(base_generator, classifier_type='standard'):
    """
    Wrap a data generator to produce multi-head labels for staged/hierarchical models.
    
    Args:
        base_generator: Base data generator
        classifier_type: Type of classifier ('standard', 'staged', 'hierarchical')
        
    Returns:
        Generator that yields (X, y_multihead) for multi-output models
    """
    if classifier_type == 'standard':
        # For standard models, just yield the base generator
        for batch_x, batch_y in base_generator:
            yield batch_x, batch_y
    else:
        # For staged/hierarchical models, transform labels
        for batch_x, batch_y in base_generator:
            if isinstance(batch_y, dict):
                # Already transformed
                yield batch_x, batch_y
            else:
                # Transform single labels to multi-head
                y_multihead = transform_labels_for_multihead(batch_y)
                yield batch_x, y_multihead


class MultiHeadSequence(tf.keras.utils.Sequence):
    """
    Keras Sequence wrapper for multi-head data generation.
    
    This class wraps an existing Sequence and transforms its labels
    for use with staged or hierarchical models.
    """
    
    def __init__(self, base_sequence, classifier_type='standard', num_classes=4):
        """
        Initialize the multi-head sequence.
        
        Args:
            base_sequence: Base keras Sequence
            classifier_type: Type of classifier ('standard', 'staged', 'hierarchical')
            num_classes: Number of classes
        """
        self.base_sequence = base_sequence
        self.classifier_type = classifier_type
        self.num_classes = num_classes
    
    def __len__(self):
        return len(self.base_sequence)
    
    def __getitem__(self, idx):
        batch_x, batch_y = self.base_sequence[idx]
        
        if self.classifier_type == 'standard':
            return batch_x, batch_y
        else:
            # Transform labels for multi-head models
            y_multihead = transform_labels_for_multihead(
                batch_y, 
                num_classes=self.num_classes,
                label_format='one_hot' if len(batch_y.shape) > 1 else 'class_indices'
            )
            return batch_x, y_multihead
    
    def on_epoch_end(self):
        if hasattr(self.base_sequence, 'on_epoch_end'):
            self.base_sequence.on_epoch_end()


def verify_multihead_labels(y_multihead, batch_size=None):
    """
    Verify that multi-head labels are correctly formatted.
    
    Args:
        y_multihead: Dictionary with 'stage' and 'subclass' labels
        batch_size: Expected batch size (optional)
        
    Returns:
        bool: True if labels are correctly formatted
    """
    if not isinstance(y_multihead, dict):
        return False, "Labels should be a dictionary"
    
    required_keys = ['stage', 'subclass']
    for key in required_keys:
        if key not in y_multihead:
            return False, f"Missing key: {key}"
    
    stage_labels = y_multihead['stage']
    subclass_labels = y_multihead['subclass']
    
    # Check shapes
    if len(stage_labels.shape) != 2 or stage_labels.shape[1] != 2:
        return False, f"Stage labels should have shape (batch_size, 2), got {stage_labels.shape}"
    
    if len(subclass_labels.shape) != 2 or subclass_labels.shape[1] != 4:
        return False, f"Subclass labels should have shape (batch_size, 4), got {subclass_labels.shape}"
    
    if stage_labels.shape[0] != subclass_labels.shape[0]:
        return False, "Stage and subclass labels should have same batch size"
    
    if batch_size is not None and stage_labels.shape[0] != batch_size:
        return False, f"Expected batch size {batch_size}, got {stage_labels.shape[0]}"
    
    return True, "Labels are correctly formatted"


def print_multihead_label_summary(y_multihead, class_names=None):
    """
    Print a summary of multi-head labels for debugging.
    
    Args:
        y_multihead: Dictionary with 'stage' and 'subclass' labels
        class_names: Optional list of class names
    """
    if class_names is None:
        class_names = ['M', 'MM', 'BN', 'SN']
    
    stage_labels = y_multihead['stage']
    subclass_labels = y_multihead['subclass']
    
    print("Multi-head Label Summary:")
    print(f"  Batch size: {stage_labels.shape[0]}")
    print(f"  Stage labels shape: {stage_labels.shape}")
    print(f"  Subclass labels shape: {subclass_labels.shape}")
    
    # Show distribution
    stage_counts = np.sum(stage_labels, axis=0)
    subclass_counts = np.sum(subclass_labels, axis=0)
    
    print(f"  Stage distribution: Early={stage_counts[0]:.0f}, Late={stage_counts[1]:.0f}")
    print(f"  Subclass distribution: {dict(zip(class_names, subclass_counts))}")
    
    # Show consistency check
    subclass_indices = np.argmax(subclass_labels, axis=1)
    stage_indices = np.argmax(stage_labels, axis=1)
    
    expected_stages = np.where(subclass_indices < 2, 0, 1)  # M,MM->0, BN,SN->1
    consistent = np.mean(stage_indices == expected_stages)
    print(f"  Stage-subclass consistency: {consistent:.1%}")