#!/usr/bin/env python3
"""
Loss functions for neutrophils classification, including ordinal loss functions
that respect the ranking nature of the classes (M -> MM -> BN -> SN).

This module provides two main categories of loss functions:
1. Standard Categorical Loss Functions - for traditional multi-class classification
2. Ordinal Loss Functions - for classification that respects biological ordering

All loss functions support class_weights parameter for handling imbalanced datasets.
Ordinal loss functions additionally support penalty/ordinal_penalty_strength parameters
for enforcing biological ordering constraints.
"""

import tensorflow as tf
import numpy as np

# =============================================================================
# STANDARD CATEGORICAL LOSS FUNCTIONS
# =============================================================================

def categorical_crossentropy(y_true, y_pred, class_weights=None):
    """
    Standard categorical crossentropy loss with class weights support.
    
    Args:
        y_true: Ground truth labels (one-hot encoded)
        y_pred: Predicted probabilities
        class_weights: Optional class weights array
        
    Returns:
        Categorical crossentropy loss value
    """
    # Standard categorical crossentropy
    loss = tf.keras.losses.categorical_crossentropy(y_true, y_pred)
    
    # Apply class weights if provided
    if class_weights is not None:
        class_weights = tf.cast(class_weights, tf.float32)
        # Get class indices from one-hot encoded y_true
        y_true_indices = tf.cast(tf.argmax(y_true, axis=-1), tf.int32)
        sample_weights = tf.gather(class_weights, y_true_indices)
        loss = loss * sample_weights
    
    return loss

def sparse_categorical_crossentropy(y_true, y_pred, class_weights=None):
    """
    Sparse categorical crossentropy loss for integer labels with class weights support.
    
    Args:
        y_true: Ground truth labels (integer class indices)
        y_pred: Predicted probabilities
        class_weights: Optional class weights array
        
    Returns:
        Sparse categorical crossentropy loss value
    """
    # Standard sparse categorical crossentropy
    loss = tf.keras.losses.sparse_categorical_crossentropy(y_true, y_pred)
    
    # Apply class weights if provided
    if class_weights is not None:
        class_weights = tf.cast(class_weights, tf.float32)
        y_true_indices = tf.cast(y_true, tf.int32)
        sample_weights = tf.gather(class_weights, y_true_indices)
        loss = loss * sample_weights
    
    return loss

def binary_crossentropy(y_true, y_pred, class_weights=None):
    """
    Binary crossentropy loss with class weights support.
    
    Args:
        y_true: Ground truth labels (one-hot encoded for binary classification)
        y_pred: Predicted probabilities
        class_weights: Optional class weights array
        
    Returns:
        Binary crossentropy loss value
    """
    # Standard binary crossentropy
    loss = tf.keras.losses.binary_crossentropy(y_true, y_pred)
    
    # Apply class weights if provided
    if class_weights is not None:
        class_weights = tf.cast(class_weights, tf.float32)
        # For binary classification, apply weights based on positive class
        y_true_indices = tf.cast(tf.argmax(y_true, axis=-1), tf.int32)
        sample_weights = tf.gather(class_weights, y_true_indices)
        loss = loss * sample_weights
    
    return loss

def categorical_focal_loss(y_true, y_pred, gamma=2.0, alpha=None, class_weights=None):
    """
    Focal loss for heavily imbalanced datasets with class weights support.
    
    Args:
        y_true: Ground truth labels (one-hot encoded)
        y_pred: Predicted probabilities
        gamma: Focusing parameter (higher gamma = more focus on hard examples)
        alpha: Optional class balancing parameter
        class_weights: Optional class weights array
        
    Returns:
        Focal loss value
    """
    # Add small epsilon to prevent log(0)
    epsilon = tf.keras.backend.epsilon()
    y_pred = tf.clip_by_value(y_pred, epsilon, 1 - epsilon)
    
    # Calculate focal loss
    ce_loss = -y_true * tf.math.log(y_pred)
    pt = tf.where(tf.equal(y_true, 1), y_pred, 1 - y_pred)
    focal_weight = tf.pow(1 - pt, gamma)
    
    focal_loss = focal_weight * ce_loss
    
    # Apply alpha balancing if provided
    if alpha is not None:
        alpha = tf.cast(alpha, tf.float32)
        alpha_t = tf.where(tf.equal(y_true, 1), alpha, 1 - alpha)
        focal_loss = alpha_t * focal_loss
    
    # Sum across classes for final focal loss
    focal_loss = tf.reduce_sum(focal_loss, axis=-1)
    
    # Apply class weights if provided
    if class_weights is not None:
        class_weights = tf.cast(class_weights, tf.float32)
        y_true_indices = tf.cast(tf.argmax(y_true, axis=-1), tf.int32)
        sample_weights = tf.gather(class_weights, y_true_indices)
        focal_loss = focal_loss * sample_weights
    
    return focal_loss

def categorical_dice_loss(y_true, y_pred, smooth=1e-7, class_weights=None):
    """
    Categorical dice loss for multi-class classification with class weights support.
    
    Args:
        y_true: Ground truth labels (one-hot encoded)
        y_pred: Predicted probabilities
        smooth: Smoothing factor to avoid division by zero (default=1e-7)
        class_weights: Optional class weights array
        
    Returns:
        Categorical dice loss value
    """
    # Convert to float32 for numerical stability
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    
    # Calculate intersection and union for each class
    intersection = tf.reduce_sum(y_true * y_pred, axis=0)
    union = tf.reduce_sum(y_true, axis=0) + tf.reduce_sum(y_pred, axis=0)
    
    # Calculate dice coefficient for each class
    dice_coeff = (2.0 * intersection + smooth) / (union + smooth)
    
    # Apply class weights if provided
    if class_weights is not None:
        class_weights = tf.cast(class_weights, tf.float32)
        # Normalize class weights to have mean of 1.0 to prevent negative loss
        normalized_weights = class_weights / tf.reduce_mean(class_weights)
        dice_coeff = dice_coeff * normalized_weights
    
    # Return 1 - mean dice coefficient as loss
    return 1.0 - tf.reduce_mean(dice_coeff)

# =============================================================================
# ORDINAL LOSS FUNCTIONS
# =============================================================================

def ordinal_crossentropy(y_true, y_pred, class_weights=None, penalty=1.0):
    """
    Ordinal crossentropy loss that penalizes violations of ordinal structure.
    
    This loss function combines standard categorical crossentropy with an ordinal
    penalty term that increases the loss when predictions violate the natural
    ordering of classes (M -> MM -> BN -> SN).
    
    Args:
        y_true: Ground truth labels (integer class indices, not one-hot)
        y_pred: Predicted probabilities (softmax output)
        class_weights: Optional array of class weights
        penalty: Strength of ordinal penalty component (default=1.0)
        
    Returns:
        Ordinal crossentropy loss value
    """
    # Standard categorical crossentropy
    y_true_one_hot = tf.one_hot(tf.cast(y_true, tf.int32), tf.shape(y_pred)[-1])
    base_loss = tf.keras.losses.categorical_crossentropy(y_true_one_hot, y_pred)
    
    # Apply class weights after computing the loss if provided
    if class_weights is not None:
        class_weights = tf.cast(class_weights, tf.float32)
        y_true_indices = tf.cast(y_true, tf.int32)
        sample_weights = tf.gather(class_weights, y_true_indices)
        base_loss = base_loss * sample_weights
    
    # Ordinal penalty component
    num_classes = tf.shape(y_pred)[-1]
    
    # Create class distance matrix (penalty increases with distance)
    class_indices = tf.range(num_classes, dtype=tf.float32)
    distance_matrix = tf.abs(
        tf.expand_dims(class_indices, 0) - tf.expand_dims(class_indices, 1)
    )
    
    # Apply ordinal penalty to predicted probabilities
    ordinal_penalty = tf.reduce_sum(
        y_pred * tf.gather(distance_matrix, tf.cast(y_true, tf.int32)), axis=-1
    )
    
    # Combine base loss with ordinal penalty (weighted)
    total_loss = base_loss + penalty * ordinal_penalty
    
    return total_loss


def ordinal_focal_loss(
    y_true,
    y_pred,
    gamma=2.0,
    alpha=None,
    class_weights=None,
    penalty=1.0,
):
    """
    Ordinal focal loss combining focal loss with ordinal ranking penalties.
    
    Args:
        y_true: Ground truth labels (integer class indices)
        y_pred: Predicted probabilities (softmax output)
        gamma: Focusing parameter (higher gamma = more focus on hard examples)
        alpha: Optional class balancing parameter
        class_weights: Optional array of class weights
        penalty: Strength of ordinal penalty component (default=1.0)
        
    Returns:
        Ordinal focal loss value
    """
    # Convert to one-hot for focal loss calculation
    num_classes = tf.shape(y_pred)[-1]
    y_true_one_hot = tf.one_hot(tf.cast(y_true, tf.int32), num_classes)
    
    # Add small epsilon to prevent log(0)
    epsilon = tf.keras.backend.epsilon()
    y_pred = tf.clip_by_value(y_pred, epsilon, 1 - epsilon)
    
    # Calculate focal loss
    ce_loss = -y_true_one_hot * tf.math.log(y_pred)
    pt = tf.where(tf.equal(y_true_one_hot, 1), y_pred, 1 - y_pred)
    focal_weight = tf.pow(1 - pt, gamma)
    
    focal_loss = focal_weight * ce_loss
    
    # Apply alpha balancing if provided
    if alpha is not None:
        alpha = tf.cast(alpha, tf.float32)
        alpha_t = tf.where(tf.equal(y_true_one_hot, 1), alpha, 1 - alpha)
        focal_loss = alpha_t * focal_loss
    
    # Sum across classes for final focal loss
    focal_loss = tf.reduce_sum(focal_loss, axis=-1)
    
    # Add ordinal penalty component
    if penalty > 0:
        # Calculate ordinal distances
        class_indices = tf.range(num_classes, dtype=tf.float32)
        predicted_class = tf.cast(tf.argmax(y_pred, axis=-1), tf.float32)
        true_class = tf.cast(y_true, tf.float32)
        
        ordinal_distances = tf.abs(true_class - predicted_class)
        ordinal_penalty = (
            penalty
            * ordinal_distances
            / tf.cast(num_classes - 1, tf.float32)
        )
        
        focal_loss = focal_loss + ordinal_penalty
    
    # Apply class weights if provided
    if class_weights is not None:
        class_weights = tf.cast(class_weights, tf.float32)
        y_true_indices = tf.cast(y_true, tf.int32)
        sample_weights = tf.gather(class_weights, y_true_indices)
        focal_loss = focal_loss * sample_weights
    
    return focal_loss


def ordinal_dice_loss(
    y_true, y_pred, smooth=1e-7, class_weights=None, penalty=1.0
):
    """
    Ordinal dice loss that combines dice loss with ordinal ranking penalty.
    
    This loss function respects the ordinal nature of classes while using dice-based
    overlap calculation. It penalizes predictions that violate the ordinal structure
    more heavily than those that maintain ranking consistency.
    
    Args:
        y_true: Ground truth labels (integer class indices, not one-hot)
        y_pred: Predicted probabilities (softmax output)
        smooth: Smoothing factor for dice calculation (default=1e-7)
        class_weights: Optional class weights array
        penalty: Strength of ordinal penalty component (default=1.0)
        
    Returns:
        Ordinal dice loss value
    """
    # Convert y_true to one-hot for dice calculation
    num_classes = tf.shape(y_pred)[-1]
    y_true_one_hot = tf.one_hot(tf.cast(y_true, tf.int32), num_classes)
    
    # Calculate base dice loss
    base_dice_loss = categorical_dice_loss(y_true_one_hot, y_pred, smooth, class_weights)
    
    # Calculate ordinal penalty
    # Get predicted class indices
    y_pred_classes = tf.cast(tf.argmax(y_pred, axis=-1), tf.float32)
    y_true_float = tf.cast(y_true, tf.float32)
    
    # Calculate ordinal penalty based on distance between true and predicted classes
    ordinal_distances = tf.abs(y_true_float - y_pred_classes)
    ordinal_penalty = tf.reduce_mean(ordinal_distances)
    
    # Normalize ordinal penalty by maximum possible distance
    max_distance = tf.cast(num_classes - 1, tf.float32)
    normalized_ordinal_penalty = ordinal_penalty / max_distance
    
    # Combine dice loss with ordinal penalty
    total_loss = base_dice_loss + penalty * normalized_ordinal_penalty
    
    return total_loss


def soft_ordinal_loss(y_true, y_pred, sigma=1.0, class_weights=None, penalty=1.0):
    """
    Soft ordinal loss using Gaussian-weighted distance penalties.
    
    Args:
        y_true: Ground truth labels (integer class indices)
        y_pred: Predicted probabilities (softmax output)
        sigma: Standard deviation for Gaussian weighting
        class_weights: Optional array of class weights
        penalty: Strength of ordinal penalty component (default=1.0)
        
    Returns:
        Soft ordinal loss value
    """
    # Convert to appropriate types
    y_true = tf.cast(y_true, tf.float32)
    num_classes = tf.shape(y_pred)[-1]
    
    # Create class indices
    class_indices = tf.range(num_classes, dtype=tf.float32)
    
    # Calculate expected class index from predictions
    predicted_class = tf.reduce_sum(y_pred * class_indices, axis=-1)
    
    # Calculate distance-based loss with Gaussian weighting
    distances = tf.abs(y_true - predicted_class)
    gaussian_weights = tf.exp(-0.5 * tf.square(distances / sigma))
    
    # Base loss component
    base_loss = tf.square(distances)
    
    # Apply Gaussian weighting (closer predictions get lower penalty)
    soft_loss = base_loss * (1.0 - gaussian_weights)
    
    # Apply penalty scaling
    soft_loss = soft_loss * penalty
    
    # Apply class weights if provided
    if class_weights is not None:
        class_weights = tf.cast(class_weights, tf.float32)
        y_true_indices = tf.cast(y_true, tf.int32)
        sample_weights = tf.gather(class_weights, y_true_indices)
        soft_loss = soft_loss * sample_weights
    
    return soft_loss


def cumulative_ordinal_loss(y_true, y_pred, class_weights=None, penalty=1.0):
    """
    Cumulative ordinal loss using cumulative probability modeling.
    
    Args:
        y_true: Ground truth labels (integer class indices)
        y_pred: Predicted probabilities (softmax output)
        class_weights: Optional array of class weights
        penalty: Strength of ordinal penalty component
        
    Returns:
        Cumulative ordinal loss value
    """
    # Convert y_true to cumulative binary targets
    num_classes = tf.shape(y_pred)[-1]
    y_true_int = tf.cast(y_true, tf.int32)
    
    # Create cumulative targets: [1,1,1,0] for class 2 out of 4 classes
    class_indices = tf.range(num_classes - 1, dtype=tf.int32)
    cumulative_targets = tf.cast(
        tf.expand_dims(y_true_int, -1) > tf.expand_dims(class_indices, 0), tf.float32
    )
    
    # Convert predictions to cumulative probabilities
    cumulative_probs = tf.cumsum(y_pred[:, :-1], axis=-1)
    
    # Binary crossentropy for each cumulative probability
    epsilon = tf.keras.backend.epsilon()
    cumulative_probs = tf.clip_by_value(cumulative_probs, epsilon, 1 - epsilon)
    
    loss_per_threshold = -(
        cumulative_targets * tf.math.log(cumulative_probs)
        + (1 - cumulative_targets) * tf.math.log(1 - cumulative_probs)
    )
    
    # Sum over all thresholds
    cumulative_loss = tf.reduce_sum(loss_per_threshold, axis=-1)
    
    # Apply penalty scaling
    cumulative_loss = cumulative_loss * penalty
    
    # Apply class weights if provided
    if class_weights is not None:
        class_weights = tf.cast(class_weights, tf.float32)
        sample_weights = tf.gather(class_weights, y_true_int)
        cumulative_loss = cumulative_loss * sample_weights
    
    return cumulative_loss

def hierarchical_loss(y_true, y_pred, alpha=0.3, beta=0.7, penalty_weight=0.1, class_weights=None):
    """
    Hierarchical loss function for multi-output models with contradiction penalty.
    
    This loss function is designed for models with two outputs:
    - stage: Early (M, MM) vs Late (BN, SN) classification
    - subclass: Full 4-class classification (M, MM, BN, SN)
    
    The loss includes a contradiction penalty that penalizes when the stage
    and subclass predictions are inconsistent with each other.
    
    For multi-output models, Keras automatically passes the outputs as a list
    or dictionary. This function handles both cases.
    
    Args:
        y_true: Ground truth labels - can be dict, list, or individual tensors
        y_pred: Model predictions - can be dict, list, or individual tensors
        alpha: Weight for stage loss (default=0.3)
        beta: Weight for subclass loss (default=0.7)
        penalty_weight: Weight for contradiction penalty (default=0.1)
        class_weights: Optional dictionary with class weights for each output
        
    Returns:
        Combined hierarchical loss value
    """
    # Handle different input formats from Keras multi-output models
    if isinstance(y_true, dict) and isinstance(y_pred, dict):
        # Dictionary format
        stage_true = y_true['stage']
        stage_pred = y_pred['stage']
        subclass_true = y_true['subclass']
        subclass_pred = y_pred['subclass']
    elif isinstance(y_true, (list, tuple)) and isinstance(y_pred, (list, tuple)):
        # List/tuple format - assume order [stage, subclass]
        stage_true = y_true[0]
        stage_pred = y_pred[0]
        subclass_true = y_true[1]
        subclass_pred = y_pred[1]
    else:
        # Fallback - assume single tensor (shouldn't happen for multi-output)
        raise ValueError(
            "Hierarchical loss requires multi-output format. "
            f"Got y_true type: {type(y_true)}, y_pred type: {type(y_pred)}"
        )
    
    # Standard losses for each head
    stage_weights = class_weights.get('stage', None) if class_weights else None
    subclass_weights = class_weights.get('subclass', None) if class_weights else None
    
    stage_loss = categorical_crossentropy(stage_true, stage_pred, stage_weights)
    subclass_loss = categorical_crossentropy(subclass_true, subclass_pred, subclass_weights)
    
    # Hierarchical contradiction penalty
    # Map subclass to stage: M,MM -> Early (0), BN,SN -> Late (1)
    subclass_to_stage = tf.constant([0.0, 0.0, 1.0, 1.0], dtype=tf.float32)  # M,MM,BN,SN -> Early,Early,Late,Late
    
    # Get predicted subclass probabilities and compute expected stage
    subclass_probs = tf.nn.softmax(subclass_pred)
    expected_stage_from_subclass = tf.reduce_sum(
        subclass_probs * subclass_to_stage, axis=-1
    )
    
    # Get actual stage prediction (probability of Late stage)
    stage_probs = tf.nn.softmax(stage_pred)
    predicted_late_stage = stage_probs[:, 1]  # Probability of Late stage
    
    # Contradiction penalty: penalize when stage and subclass predictions don't align
    contradiction_penalty = tf.square(predicted_late_stage - expected_stage_from_subclass)
    
    # Combine losses
    total_loss = (alpha * stage_loss +
                 beta * subclass_loss +
                 penalty_weight * contradiction_penalty)
    
    return total_loss

# =============================================================================
# SERIALIZABLE WRAPPER CLASSES
# =============================================================================

@tf.keras.utils.register_keras_serializable(package="neutrophils_core", name="SerializableLoss")
class SerializableLoss(tf.keras.losses.Loss):
    """
    Base class for serializable loss functions with parameters.
    
    This solves the functools.partial serialization issue by creating
    proper Keras Loss classes that implement get_config() and from_config().
    """
    
    def __init__(self, loss_fn, loss_name, **kwargs):
        print(f"Creating SerializableLoss instance: {loss_name}")
        """
        Initialize serializable loss wrapper.
        
        Args:
            loss_fn: The actual loss function to wrap
            loss_name: Name of the loss function for serialization
            **kwargs: Parameters for the loss function
        """
        super().__init__(name=loss_name)
        self.loss_fn = loss_fn
        self.loss_name = loss_name
        self.loss_kwargs = kwargs
    
    def call(self, y_true, y_pred):
        """Call the wrapped loss function with stored parameters."""
        return self.loss_fn(y_true, y_pred, **self.loss_kwargs)
    
    def get_config(self):
        """Get configuration for serialization."""
        config = super().get_config()
        config.update({
            'loss_name': self.loss_name,
            'loss_kwargs': self.loss_kwargs
        })
        return config
    
    @classmethod
    def from_config(cls, config):
        """Recreate loss from configuration."""
        loss_name = config.pop('loss_name')
        loss_kwargs = config.pop('loss_kwargs', {})
        
        # Get the original loss function
        if loss_name not in LOSS_FUNCTIONS:
            raise ValueError(f"Unknown loss function: {loss_name}")
        
        loss_fn = LOSS_FUNCTIONS[loss_name]
        return cls(loss_fn, loss_name, **loss_kwargs)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_loss_function(loss_name, **kwargs):
    """
    Get a loss function by name with optional parameters.
    
    Args:
        loss_name: Name of the loss function
        **kwargs: Additional parameters for the loss function
        
    Returns:
        Configured loss function (serializable)
    """
    if loss_name not in LOSS_FUNCTIONS:
        raise ValueError(
            f"Unknown loss function: {loss_name}. Available: {list(LOSS_FUNCTIONS.keys())}"
        )
    
    loss_fn = LOSS_FUNCTIONS[loss_name]
    
    print("Using loss function:", loss_name)
    
    # If kwargs provided, create serializable wrapper instead of functools.partial
    if kwargs:
        print(f"Creating serializable loss wrapper with parameters: {list(kwargs.keys())}")
        return SerializableLoss(loss_fn, loss_name, **kwargs)
    
    return loss_fn


# =============================================================================
# CONTRASTIVE LEARNING LOSS FUNCTIONS
# =============================================================================

def nce_loss(z_i, z_j, temperature=0.1, negative_samples=None):
    """
    Noise Contrastive Estimation (NCE) loss for contrastive learning.
    
    NCE loss treats the problem as a binary classification task, distinguishing
    between positive pairs and negative samples. This implementation supports
    both in-batch negatives and explicit negative sampling.
    
    Args:
        z_i: Feature representations from first augmentation [batch_size, feature_dim]
        z_j: Feature representations from second augmentation [batch_size, feature_dim]
        temperature: Temperature parameter for scaling similarities
        negative_samples: Optional explicit negative samples [num_negatives, feature_dim]
        
    Returns:
        NCE loss value
        
    References:
        - Gutmann & Hyvärinen (2010). "Noise-contrastive estimation: A new estimation 
          principle for unnormalized statistical models"
        - Oord et al. (2018). "Representation Learning with Contrastive Predictive Coding"
    """
    batch_size = tf.shape(z_i)[0]
    feature_dim = tf.shape(z_i)[1]
    
    # Normalize feature representations
    z_i = tf.nn.l2_normalize(z_i, axis=1)
    z_j = tf.nn.l2_normalize(z_j, axis=1)
    
    # Compute positive similarities
    positive_similarities = tf.reduce_sum(z_i * z_j, axis=1)  # [batch_size]
    positive_logits = positive_similarities / temperature
    
    # Compute negative similarities
    if negative_samples is not None:
        # Use explicit negative samples
        negative_samples = tf.nn.l2_normalize(negative_samples, axis=1)
        
        # Compute similarities with negatives for each positive pair
        z_i_expanded = tf.expand_dims(z_i, 1)  # [batch_size, 1, feature_dim]
        negative_similarities = tf.reduce_sum(
            z_i_expanded * tf.expand_dims(negative_samples, 0), axis=2
        )  # [batch_size, num_negatives]
        negative_logits = negative_similarities / temperature
    else:
        # Use in-batch negatives (all other samples in the batch)
        # Create similarity matrix between all z_i and z_j
        similarity_matrix = tf.matmul(z_i, z_j, transpose_b=True) / temperature
        
        # Mask out positive pairs (diagonal elements)
        mask = tf.eye(batch_size, dtype=tf.bool)
        negative_logits = tf.boolean_mask(
            tf.reshape(similarity_matrix, [-1]), 
            tf.reshape(~mask, [-1])
        )
        negative_logits = tf.reshape(negative_logits, [batch_size, batch_size - 1])
    
    # Combine positive and negative logits
    # Positive label = 1, Negative labels = 0
    positive_labels = tf.ones([batch_size, 1])
    negative_labels = tf.zeros_like(negative_logits)
    
    all_logits = tf.concat([tf.expand_dims(positive_logits, 1), negative_logits], axis=1)
    all_labels = tf.concat([positive_labels, negative_labels], axis=1)
    
    # Compute binary cross-entropy loss
    loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=all_labels, logits=all_logits)
    loss = tf.reduce_mean(loss)
    
    return loss


def nt_xent_loss(z_i, z_j, temperature=0.1):
    """
    Normalized Temperature-scaled Cross-Entropy (NT-Xent) loss for contrastive learning.
    
    NT-Xent loss is the standard contrastive loss used in SimCLR and other 
    contrastive learning frameworks. It treats each positive pair as a separate
    classification problem against all other samples in the batch.
    
    Args:
        z_i: Feature representations from first augmentation [batch_size, feature_dim]
        z_j: Feature representations from second augmentation [batch_size, feature_dim]
        temperature: Temperature parameter for scaling similarities
        
    Returns:
        NT-Xent loss value
        
    References:
        - Chen et al. (2020). "A Simple Framework for Contrastive Learning of Visual Representations"
        - He et al. (2020). "Momentum Contrast for Unsupervised Visual Representation Learning"
    """
    batch_size = tf.shape(z_i)[0]
    
    # Normalize feature representations
    z_i = tf.nn.l2_normalize(z_i, axis=1)
    z_j = tf.nn.l2_normalize(z_j, axis=1)
    
    # Concatenate all representations
    representations = tf.concat([z_i, z_j], axis=0)  # [2 * batch_size, feature_dim]
    
    # Compute similarity matrix
    similarity_matrix = tf.matmul(representations, representations, transpose_b=True)
    similarity_matrix = similarity_matrix / temperature
    
    # Create labels for positive pairs
    # For i-th sample: positive pair is at index (i + batch_size) % (2 * batch_size)
    labels = tf.concat([
        tf.range(batch_size, 2 * batch_size),  # z_i -> z_j
        tf.range(0, batch_size)                # z_j -> z_i
    ], axis=0)
    
    # Mask out self-similarities (diagonal elements)
    mask = tf.eye(2 * batch_size, dtype=tf.bool)
    similarity_matrix = tf.where(mask, -tf.float32.max, similarity_matrix)
    
    # Compute cross-entropy loss
    loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
        labels=labels, 
        logits=similarity_matrix
    )
    
    return tf.reduce_mean(loss)


def supervised_contrastive_loss(features, labels, temperature=0.1):
    """
    Supervised Contrastive Loss that leverages label information.
    
    This loss extends contrastive learning to supervised settings by treating
    samples with the same label as positives and samples with different labels
    as negatives. Useful for combining contrastive learning with classification.
    
    Args:
        features: Feature representations [batch_size, feature_dim]
        labels: Class labels [batch_size] (integer labels)
        temperature: Temperature parameter for scaling similarities
        
    Returns:
        Supervised contrastive loss value
        
    References:
        - Khosla et al. (2020). "Supervised Contrastive Learning"
    """
    batch_size = tf.shape(features)[0]
    
    # Normalize features
    features = tf.nn.l2_normalize(features, axis=1)
    
    # Compute similarity matrix
    similarity_matrix = tf.matmul(features, features, transpose_b=True) / temperature
    
    # Create positive mask (same labels)
    labels = tf.expand_dims(labels, 1)
    positive_mask = tf.equal(labels, tf.transpose(labels))
    positive_mask = tf.cast(positive_mask, tf.float32)
    
    # Remove self-similarities
    self_mask = tf.eye(batch_size, dtype=tf.float32)
    positive_mask = positive_mask - self_mask
    
    # Compute logits
    max_similarity = tf.reduce_max(similarity_matrix, axis=1, keepdims=True)
    similarity_matrix = similarity_matrix - max_similarity  # For numerical stability
    
    # Compute positive and negative terms
    exp_similarities = tf.exp(similarity_matrix)
    
    # Sum over all samples (both positive and negative)
    denominator = tf.reduce_sum(exp_similarities, axis=1, keepdims=True)
    
    # Sum over positive samples only
    numerator = tf.reduce_sum(positive_mask * exp_similarities, axis=1, keepdims=True)
    
    # Avoid division by zero
    numerator = tf.maximum(numerator, tf.keras.backend.epsilon())
    
    # Compute loss for each sample
    log_prob = tf.math.log(numerator) - tf.math.log(denominator)
    
    # Average over positive pairs
    num_positives = tf.reduce_sum(positive_mask, axis=1)
    num_positives = tf.maximum(num_positives, 1.0)  # Avoid division by zero
    
    loss = -tf.reduce_sum(log_prob) / tf.reduce_sum(num_positives)
    
    return loss



def create_contrastive_loss_function(loss_type="nt_xent", temperature=0.1, **kwargs):
    """
    Factory function to create contrastive loss functions with fixed parameters.
    
    Args:
        loss_type: Type of contrastive loss ("nt_xent", "nce", "supervised")
        temperature: Temperature parameter for scaling
        **kwargs: Additional parameters specific to each loss type
        
    Returns:
        Configured loss function
    """
    if loss_type == "nt_xent":
        def loss_fn(z_i, z_j):
            return nt_xent_loss(z_i, z_j, temperature=temperature)
        return loss_fn
    
    elif loss_type == "nce":
        negative_samples = kwargs.get("negative_samples", None)
        def loss_fn(z_i, z_j):
            return nce_loss(z_i, z_j, temperature=temperature, negative_samples=negative_samples)
        return loss_fn
    
    elif loss_type == "supervised":
        def loss_fn(features, labels):
            return supervised_contrastive_loss(features, labels, temperature=temperature)
        return loss_fn
    
    else:
        raise ValueError(f"Unknown contrastive loss type: {loss_type}")


# =============================================================================
# FUNCTION REGISTRY AND EXPORTS
# =============================================================================

# Loss function categories for validation
STANDARD_LOSS_FUNCTIONS = {
    "categorical_crossentropy",
    "sparse_categorical_crossentropy",
    "binary_crossentropy",
    "categorical_focal_loss",
    "categorical_dice_loss"
}

ORDINAL_LOSS_FUNCTIONS = {
    "ordinal_crossentropy",
    "ordinal_focal_loss",
    "ordinal_dice_loss",
    "soft_ordinal_loss",
    "cumulative_ordinal_loss"
}

CONTRASTIVE_LOSS_FUNCTIONS = {
    "nce_loss",
    "nt_xent_loss",
    "supervised_contrastive_loss"
}

# Dictionary of available loss functions for easy access
LOSS_FUNCTIONS = {
    # Standard Categorical Loss Functions
    "categorical_crossentropy": categorical_crossentropy,
    "sparse_categorical_crossentropy": sparse_categorical_crossentropy,
    "binary_crossentropy": binary_crossentropy,
    "categorical_focal_loss": categorical_focal_loss,
    "categorical_dice_loss": categorical_dice_loss,
    
    # Ordinal Loss Functions
    "ordinal_crossentropy": ordinal_crossentropy,
    "ordinal_focal_loss": ordinal_focal_loss,
    "ordinal_dice_loss": ordinal_dice_loss,
    "soft_ordinal_loss": soft_ordinal_loss,
    "cumulative_ordinal_loss": cumulative_ordinal_loss,
    
    # Multi-output Loss Functions
    "hierarchical_loss": hierarchical_loss,
    
    # Contrastive Loss Functions
    "nce_loss": nce_loss,
    "nt_xent_loss": nt_xent_loss,
    "supervised_contrastive_loss": supervised_contrastive_loss,
    "create_contrastive_loss_function": create_contrastive_loss_function,
}

# Export main functions
__all__ = [
    # Standard Categorical Loss Functions
    "categorical_crossentropy",
    "sparse_categorical_crossentropy",
    "binary_crossentropy",
    "categorical_focal_loss",
    "categorical_dice_loss",
    
    # Ordinal Loss Functions
    "ordinal_crossentropy",
    "ordinal_focal_loss",
    "ordinal_dice_loss",
    "soft_ordinal_loss",
    "cumulative_ordinal_loss",
    
    # Multi-output Loss Functions
    "hierarchical_loss",
    
    # Utility Functions
    "get_loss_function",
    
    # Function Registry
    "LOSS_FUNCTIONS",
    "STANDARD_LOSS_FUNCTIONS",
    "ORDINAL_LOSS_FUNCTIONS",
]
