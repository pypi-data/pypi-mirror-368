"""
Classification metrics for neutrophil classification tasks.

This module provides specialized metrics for ordinal classification,
specifically designed for neutrophil maturation stage classification.
"""

import tensorflow as tf
from tensorflow.keras import backend as K
import numpy as np


def ordinal_mae(y_true, y_pred):
    """
    Mean Absolute Error for ordinal classification.

    Args:
        y_true: Ground truth labels (class indices)
        y_pred: Predicted probabilities

    Returns:
        Mean absolute error between predicted and true class indices
    """
    # Convert one-hot to class indices if needed
    if len(K.int_shape(y_true)) > 1 and K.int_shape(y_true)[-1] > 1:
        y_true_indices = K.argmax(y_true, axis=-1)
    else:
        y_true_indices = K.flatten(y_true)

    # Calculate expected class from predictions
    num_classes = K.int_shape(y_pred)[-1]
    class_indices = K.cast(K.arange(num_classes), K.floatx())
    y_pred_expected = K.sum(y_pred * class_indices, axis=-1)

    # Calculate MAE
    return K.mean(K.abs(K.cast(y_true_indices, K.floatx()) - y_pred_expected))


def adjacent_class_accuracy(y_true, y_pred):
    """
    Accuracy allowing for adjacent class predictions to be considered correct.

    Args:
        y_true: Ground truth labels (class indices)
        y_pred: Predicted probabilities

    Returns:
        Adjacent class accuracy score
    """
    # Convert one-hot to class indices if needed
    if len(K.int_shape(y_true)) > 1 and K.int_shape(y_true)[-1] > 1:
        y_true_indices = K.argmax(y_true, axis=-1)
    else:
        y_true_indices = K.flatten(y_true)

    y_pred_indices = K.argmax(y_pred, axis=-1)

    # Check if prediction is within ±1 of true class
    diff = K.abs(
        K.cast(y_true_indices, K.floatx()) - K.cast(y_pred_indices, K.floatx())
    )
    adjacent_correct = K.cast(diff <= 1.0, K.floatx())

    return K.mean(adjacent_correct)


def adjacent_class_recall(y_true, y_pred):
    """
    Recall allowing for adjacent class predictions to be considered correct.

    Args:
        y_true: Ground truth labels (class indices)
        y_pred: Predicted probabilities

    Returns:
        Adjacent class recall score
    """
    return adjacent_class_accuracy(y_true, y_pred)


def adjacent_class_precision(y_true, y_pred):
    """
    Precision allowing for adjacent class predictions to be considered correct.

    Args:
        y_true: Ground truth labels (class indices)
        y_pred: Predicted probabilities

    Returns:
        Adjacent class precision score
    """
    return adjacent_class_accuracy(y_true, y_pred)


def adjacent_class_auc(y_true, y_pred, adjacency_weight=1):
    """
    AUC considering adjacent classes as positive for each class

    Args:
        y_true: Ground truth labels (class indices, not one-hot)
        y_pred: Predicted probabilities
        adjacency_weight: Maximum allowed class difference to consider as positive (default=1)

    Returns:
        Macro-averaged AUC with adjacency tolerance
    """
    # Convert one-hot to class indices if needed
    if len(K.int_shape(y_true)) > 1 and K.int_shape(y_true)[-1] > 1:
        y_true = K.argmax(y_true, axis=-1)
    elif len(K.int_shape(y_true)) == 1 or K.int_shape(y_true)[-1] == 1:
        y_true = K.flatten(y_true)

    # Get number of classes
    num_classes = K.int_shape(y_pred)[-1]

    # Calculate per-class AUC with adjacency tolerance
    class_aucs = []
    for class_idx in range(num_classes):
        # Create binary labels: 1 if true class is within adjacency_weight of current class, 0 otherwise
        class_diff_true = K.abs(K.cast(y_true, K.floatx()) - float(class_idx))
        binary_labels = K.cast(class_diff_true <= float(adjacency_weight), K.floatx())

        # Create binary scores: sum of probabilities for adjacent classes
        binary_scores = tf.zeros_like(y_pred[:, 0], dtype=K.floatx())
        for adj_idx in range(num_classes):
            if abs(adj_idx - class_idx) <= adjacency_weight:
                binary_scores = binary_scores + y_pred[:, adj_idx]

        # Calculate AUC using TensorFlow's AUC metric
        # Note: We use a simplified correlation-based approach since we need this to be differentiable
        # and work within the metric function constraints

        # Sort by predicted scores (descending)
        sorted_indices = tf.argsort(binary_scores, direction="DESCENDING")
        sorted_labels = tf.gather(binary_labels, sorted_indices)

        # Calculate cumulative true positives and false positives
        cum_tp = tf.cumsum(sorted_labels)
        cum_fp = tf.cumsum(1.0 - sorted_labels)

        # Get total positives and negatives
        total_positives = tf.reduce_sum(binary_labels)
        total_negatives = tf.reduce_sum(1.0 - binary_labels)

        # Calculate TPR and FPR
        tpr = tf.where(
            total_positives > 0, cum_tp / total_positives, tf.zeros_like(cum_tp)
        )
        fpr = tf.where(
            total_negatives > 0, cum_fp / total_negatives, tf.zeros_like(cum_fp)
        )

        # Calculate AUC using trapezoidal rule (simplified)
        # Add boundary points
        tpr_with_bounds = tf.concat([[0.0], tpr, [1.0]], axis=0)
        fpr_with_bounds = tf.concat([[0.0], fpr, [1.0]], axis=0)

        # Calculate differences
        fpr_diffs = fpr_with_bounds[1:] - fpr_with_bounds[:-1]
        tpr_heights = (tpr_with_bounds[1:] + tpr_with_bounds[:-1]) / 2.0

        # Calculate AUC
        auc = tf.reduce_sum(fpr_diffs * tpr_heights)

        # Handle edge cases
        auc = tf.where(total_positives > 0, auc, 0.5)  # If no positives, AUC = 0.5
        auc = tf.where(total_negatives > 0, auc, 0.5)  # If no negatives, AUC = 0.5

        class_aucs.append(auc)

    # Return macro-averaged AUC
    return K.mean(K.stack(class_aucs))


def kendall_tau_metric(y_true, y_pred):
    """
    Kendall's tau correlation coefficient for ordinal classification
    Simplified version for use as a Keras metric

    Args:
        y_true: Ground truth labels (class indices, not one-hot)
        y_pred: Predicted probabilities

    Returns:
        Kendall's tau correlation coefficient
    """
    # Convert one-hot to class indices if needed (consistent with ordinal_crossentropy)
    if len(K.int_shape(y_true)) > 1 and K.int_shape(y_true)[-1] > 1:
        y_true = K.argmax(y_true, axis=-1)
    elif len(K.int_shape(y_true)) == 1 or K.int_shape(y_true)[-1] == 1:
        # y_true is class indices, flatten if needed
        y_true = K.flatten(y_true)

    # Convert predictions to expected value (weighted average of class indices)
    num_classes = K.int_shape(y_pred)[-1]
    class_indices = K.cast(K.arange(num_classes), K.floatx())
    y_pred_expected = K.sum(y_pred * class_indices, axis=-1)

    # Cast to float for correlation calculation
    y_true_float = K.cast(y_true, K.floatx())

    # Calculate correlation (simplified version)
    # Note: This is a simplified correlation, not true Kendall's tau
    y_true_mean = K.mean(y_true_float)
    y_pred_mean = K.mean(y_pred_expected)

    numerator = K.mean((y_true_float - y_true_mean) * (y_pred_expected - y_pred_mean))
    denominator = K.sqrt(
        K.mean(K.square(y_true_float - y_true_mean))
        * K.mean(K.square(y_pred_expected - y_pred_mean))
    )

    # Avoid division by zero
    correlation = tf.where(denominator > 0, numerator / denominator, 0.0)

    return correlation


@tf.keras.utils.register_keras_serializable(package="neutrophils_core", name="balanced_accuracy_metric")
def balanced_accuracy_metric(y_true, y_pred):
    """
    Balanced accuracy metric for imbalanced classification

    Balanced accuracy is the average of recall obtained on each class.
    This metric is particularly useful for imbalanced datasets as it gives
    equal weight to all classes regardless of their frequency.

    Args:
        y_true: Ground truth labels (class indices, not one-hot)
        y_pred: Predicted probabilities

    Returns:
        Balanced accuracy score (average of per-class recalls)
    """
    # Convert one-hot to class indices if needed (consistent with ordinal_crossentropy)
    if len(K.int_shape(y_true)) > 1 and K.int_shape(y_true)[-1] > 1:
        y_true = K.argmax(y_true, axis=-1)
    elif len(K.int_shape(y_true)) == 1 or K.int_shape(y_true)[-1] == 1:
        # y_true is class indices, flatten if needed
        y_true = K.flatten(y_true)

    # Convert predictions to class indices
    y_pred_class = K.argmax(y_pred, axis=-1)

    # Get number of classes
    num_classes = K.int_shape(y_pred)[-1]

    # Calculate per-class recall (sensitivity)
    class_recalls = []
    for class_idx in range(num_classes):
        # True positives: correctly predicted instances of this class
        true_class_mask = K.cast(K.equal(y_true, class_idx), K.floatx())
        pred_class_mask = K.cast(K.equal(y_pred_class, class_idx), K.floatx())

        # True positives for this class
        tp = K.sum(true_class_mask * pred_class_mask)

        # Total true instances of this class (true positives + false negatives)
        total_true = K.sum(true_class_mask)

        # Calculate recall for this class (avoid division by zero)
        class_recall = tf.where(total_true > 0, tp / total_true, 0.0)
        class_recalls.append(class_recall)

    # Return average of per-class recalls (balanced accuracy)
    return K.mean(K.stack(class_recalls))


def ordinal_accuracy_tolerance(y_true, y_pred, tolerance=1):
    """
    Ordinal accuracy with specified tolerance

    Args:
        y_true: Ground truth labels (class indices, not one-hot)
        y_pred: Predicted probabilities
        tolerance: Maximum allowed class difference to consider as correct

    Returns:
        Accuracy within the specified tolerance
    """
    # Convert one-hot to class indices if needed (consistent with ordinal_crossentropy)
    if len(K.int_shape(y_true)) > 1 and K.int_shape(y_true)[-1] > 1:
        y_true = K.argmax(y_true, axis=-1)
    elif len(K.int_shape(y_true)) == 1 or K.int_shape(y_true)[-1] == 1:
        # y_true is class indices, flatten if needed
        y_true = K.flatten(y_true)

    # Convert predictions to class indices
    y_pred_class = K.argmax(y_pred, axis=-1)

    # Calculate difference between true and predicted classes
    class_diff = K.abs(K.cast(y_true, K.floatx()) - K.cast(y_pred_class, K.floatx()))

    # Count predictions within tolerance as correct
    tolerance_correct = K.cast(class_diff <= float(tolerance), K.floatx())

    return K.mean(tolerance_correct)


def standard_metric_wrapper(metric_class, **kwargs):
    """
    Create a wrapper for standard metrics that handles dimension conversion for ordinal mode

    Args:
        metric_class: The metric class to wrap
        **kwargs: Arguments to pass to the metric constructor

    Returns:
        Wrapped metric that handles both one-hot and class index inputs
    """

    class WrappedMetric(metric_class):
        def __init__(self, **metric_kwargs):
            super().__init__(**metric_kwargs)

        def update_state(self, y_true, y_pred, sample_weight=None):
            # Convert class indices to one-hot if needed for standard metrics
            if len(K.int_shape(y_true)) == 1 or (
                len(K.int_shape(y_true)) > 1 and K.int_shape(y_true)[-1] == 1
            ):
                # y_true is class indices, convert to one-hot
                num_classes = K.int_shape(y_pred)[-1]
                if num_classes is not None:
                    y_true = tf.one_hot(
                        tf.cast(K.flatten(y_true), tf.int32),
                        num_classes,
                        dtype=K.floatx(),
                    )

            return super().update_state(y_true, y_pred, sample_weight)

    return WrappedMetric(**kwargs)


def get_metrics(training_mode="standard"):
    """
    Get a list of specific metrics

    Args:
        training_mode: Training mode ('standard' or 'ordinal')

    Returns:
        List of metric functions
    """
    if training_mode == "ordinal":
        # For ordinal mode, use wrapped metrics that handle dimension conversion
        # and automatically include ordinal-specific metrics
        metrics = [
            standard_metric_wrapper(
                tf.keras.metrics.CategoricalAccuracy, name="accuracy"
            ),  # Use CategoricalAccuracy for multi-class
            standard_metric_wrapper(tf.keras.metrics.Recall, name="recall"),
            standard_metric_wrapper(tf.keras.metrics.AUC, name="auc"),
            standard_metric_wrapper(tf.keras.metrics.Precision, name="precision"),
            standard_metric_wrapper(
                tf.keras.metrics.F1Score, name="f1_score", average="macro"
            ),
            standard_metric_wrapper(
                tf.keras.metrics.SpecificityAtSensitivity,
                sensitivity=0.5,
                name="specificity",
            ),
        ]

        # Auto-include ordinal metrics for ordinal training mode
        metrics.extend(
            [
                ordinal_mae,
                adjacent_class_accuracy,
                adjacent_class_recall,
                adjacent_class_precision,
                adjacent_class_auc,
                kendall_tau_metric,
                ordinal_accuracy_tolerance,
                balanced_accuracy_metric,
            ]
        )
    else:
        # For standard mode, use regular metrics
        metrics = [
            "accuracy",
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.F1Score(name="f1_score", average="macro"),
            tf.keras.metrics.SpecificityAtSensitivity(0.5, name="specificity"),
            balanced_accuracy_metric, # added for unbalanced datasets performance metrics
        ]

    return metrics


# =============================================================================
# CONTRASTIVE LEARNING METRICS
# =============================================================================

def contrastive_accuracy(z_i, z_j, temperature=0.1):
    """
    Compute contrastive accuracy metric.
    
    Contrastive accuracy measures how often the model correctly identifies
    positive pairs compared to negative pairs in the batch.
    
    Args:
        z_i: Feature representations from first augmentation [batch_size, feature_dim]
        z_j: Feature representations from second augmentation [batch_size, feature_dim]
        temperature: Temperature parameter for scaling similarities
        
    Returns:
        Contrastive accuracy value between 0 and 1
    """
    batch_size = tf.shape(z_i)[0]
    
    # Normalize feature representations
    z_i = tf.nn.l2_normalize(z_i, axis=1)
    z_j = tf.nn.l2_normalize(z_j, axis=1)
    
    # Concatenate all representations
    representations = tf.concat([z_i, z_j], axis=0)
    
    # Compute similarity matrix
    similarity_matrix = tf.matmul(representations, representations, transpose_b=True)
    similarity_matrix = similarity_matrix / temperature
    
    # Create labels for positive pairs
    labels = tf.concat([
        tf.range(batch_size, 2 * batch_size),
        tf.range(0, batch_size)
    ], axis=0)
    
    # Mask out self-similarities
    mask = tf.eye(2 * batch_size, dtype=tf.bool)
    similarity_matrix = tf.where(mask, -tf.float32.max, similarity_matrix)
    
    # Get predictions (highest similarity)
    predictions = tf.argmax(similarity_matrix, axis=1)
    
    # Compute accuracy
    correct_predictions = tf.equal(predictions, tf.cast(labels, tf.int64))
    accuracy = tf.reduce_mean(tf.cast(correct_predictions, tf.float32))
    
    return accuracy


def contrastive_top_k_accuracy(z_i, z_j, k=5, temperature=0.1):
    """
    Compute contrastive top-k accuracy metric.
    
    Measures how often the correct positive pair is within the top-k
    most similar representations.
    
    Args:
        z_i: Feature representations from first augmentation [batch_size, feature_dim]
        z_j: Feature representations from second augmentation [batch_size, feature_dim]
        k: Number of top predictions to consider
        temperature: Temperature parameter for scaling similarities
        
    Returns:
        Top-k contrastive accuracy value between 0 and 1
    """
    batch_size = tf.shape(z_i)[0]
    
    # Normalize feature representations
    z_i = tf.nn.l2_normalize(z_i, axis=1)
    z_j = tf.nn.l2_normalize(z_j, axis=1)
    
    # Concatenate all representations
    representations = tf.concat([z_i, z_j], axis=0)
    
    # Compute similarity matrix
    similarity_matrix = tf.matmul(representations, representations, transpose_b=True)
    similarity_matrix = similarity_matrix / temperature
    
    # Create labels for positive pairs
    labels = tf.concat([
        tf.range(batch_size, 2 * batch_size),
        tf.range(0, batch_size)
    ], axis=0)
    
    # Mask out self-similarities
    mask = tf.eye(2 * batch_size, dtype=tf.bool)
    similarity_matrix = tf.where(mask, -tf.float32.max, similarity_matrix)
    
    # Get top-k predictions
    _, top_k_indices = tf.nn.top_k(similarity_matrix, k=k)
    
    # Check if true labels are in top-k predictions
    labels_expanded = tf.expand_dims(labels, 1)  # [2*batch_size, 1]
    top_k_correct = tf.reduce_any(tf.equal(top_k_indices, labels_expanded), axis=1)
    
    # Compute top-k accuracy
    top_k_accuracy = tf.reduce_mean(tf.cast(top_k_correct, tf.float32))
    
    return top_k_accuracy


def feature_uniformity(features):
    """
    Compute feature uniformity metric for contrastive learning.
    
    Uniformity measures how uniformly distributed the learned features are
    on the unit hypersphere. Higher uniformity indicates better feature
    distribution and reduced feature collapse.
    
    Args:
        features: Normalized feature representations [batch_size, feature_dim]
        
    Returns:
        Uniformity score (lower is better, ideally around -2 for uniform distribution)
        
    References:
        - Wang & Isola (2020). "Understanding Contrastive Representation Learning through Alignment and Uniformity on the Hypersphere"
    """
    # Ensure features are normalized
    features = tf.nn.l2_normalize(features, axis=1)
    
    # Compute pairwise similarities
    similarity_matrix = tf.matmul(features, features, transpose_b=True)
    
    # Remove self-similarities (diagonal)
    batch_size = tf.shape(features)[0]
    mask = tf.eye(batch_size, dtype=tf.bool)
    off_diagonal_similarities = tf.boolean_mask(similarity_matrix, ~mask)
    
    # Compute uniformity as log of average pairwise similarity
    # For uniform distribution on unit sphere, this should be around -2
    uniformity = tf.math.log(tf.reduce_mean(tf.exp(2.0 * off_diagonal_similarities)))
    
    return uniformity


def feature_alignment(z_i, z_j):
    """
    Compute feature alignment metric for contrastive learning.
    
    Alignment measures how well aligned positive pairs are in the feature space.
    Lower alignment indicates better preservation of semantic similarity.
    
    Args:
        z_i: Feature representations from first augmentation [batch_size, feature_dim]
        z_j: Feature representations from second augmentation [batch_size, feature_dim]
        
    Returns:
        Alignment score (lower is better, around 0 for well-aligned features)
        
    References:
        - Wang & Isola (2020). "Understanding Contrastive Representation Learning through Alignment and Uniformity on the Hypersphere"
    """
    # Normalize features
    z_i = tf.nn.l2_normalize(z_i, axis=1)
    z_j = tf.nn.l2_normalize(z_j, axis=1)
    
    # Compute positive pair similarities
    positive_similarities = tf.reduce_sum(z_i * z_j, axis=1)
    
    # Alignment is the negative average similarity of positive pairs
    alignment = -tf.reduce_mean(positive_similarities)
    
    return alignment


def representation_rank(features, eps=1e-6):
    """
    Compute the effective rank of feature representations.
    
    Higher rank indicates more diverse and informative features,
    while lower rank suggests feature collapse or redundancy.
    
    Args:
        features: Feature representations [batch_size, feature_dim]
        eps: Small epsilon for numerical stability
        
    Returns:
        Effective rank of the feature matrix
    """
    # Center the features
    features_centered = features - tf.reduce_mean(features, axis=0, keepdims=True)
    
    # Compute SVD
    s, _, _ = tf.linalg.svd(features_centered, full_matrices=False)
    
    # Normalize singular values
    s_normalized = s / (tf.reduce_sum(s) + eps)
    
    # Compute entropy-based effective rank
    # Effective rank = exp(entropy of normalized singular values)
    entropy = -tf.reduce_sum(s_normalized * tf.math.log(s_normalized + eps))
    effective_rank = tf.exp(entropy)
    
    return effective_rank


class ContrastiveMetricsCallback(tf.keras.callbacks.Callback):
    """
    Callback to compute and log contrastive learning metrics during training.
    
    This callback computes various contrastive metrics at the end of each epoch
    and logs them for monitoring training progress.
    """
    
    def __init__(self, validation_data=None, temperature=0.1, log_frequency=1):
        """
        Initialize the contrastive metrics callback.
        
        Args:
            validation_data: Validation data generator that returns (z_i, z_j) pairs
            temperature: Temperature parameter for similarity calculations
            log_frequency: How often to compute metrics (every N epochs)
        """
        super().__init__()
        self.validation_data = validation_data
        self.temperature = temperature
        self.log_frequency = log_frequency
        
    def on_epoch_end(self, epoch, logs=None):
        if logs is None:
            logs = {}
            
        if epoch % self.log_frequency == 0 and self.validation_data is not None:
            # Get a batch of validation data
            try:
                z_i, z_j = next(iter(self.validation_data))
                
                # Compute contrastive metrics
                cont_acc = contrastive_accuracy(z_i, z_j, self.temperature)
                cont_top5_acc = contrastive_top_k_accuracy(z_i, z_j, temperature=self.temperature, k=5)
                uniformity = feature_uniformity(z_i)
                alignment = feature_alignment(z_i, z_j)
                rank = representation_rank(z_i)
                
                # Log metrics
                logs['val_contrastive_accuracy'] = float(cont_acc.numpy())
                logs['val_contrastive_top5_accuracy'] = float(cont_top5_acc.numpy())
                logs['val_feature_uniformity'] = float(uniformity.numpy())
                logs['val_feature_alignment'] = float(alignment.numpy())
                logs['val_representation_rank'] = float(rank.numpy())
                
                print(f"\nContrastive Metrics - Epoch {epoch + 1}:")
                print(f"  Contrastive Accuracy: {cont_acc:.4f}")
                print(f"  Contrastive Top-5 Accuracy: {cont_top5_acc:.4f}")
                print(f"  Feature Uniformity: {uniformity:.4f}")
                print(f"  Feature Alignment: {alignment:.4f}")
                print(f"  Representation Rank: {rank:.4f}")
                
            except Exception as e:
                print(f"Warning: Could not compute contrastive metrics: {e}")


def get_contrastive_metrics(temperature=0.1):
    """
    Get a list of contrastive learning metrics.
    
    Args:
        temperature: Temperature parameter for similarity calculations
        
    Returns:
        List of contrastive metric functions
    """
    def contrastive_acc(z_i, z_j):
        return contrastive_accuracy(z_i, z_j, temperature)
    
    def contrastive_top5_acc(z_i, z_j):
        return contrastive_top_k_accuracy(z_i, z_j, temperature=temperature, k=5)
    
    return [
        contrastive_acc,
        contrastive_top5_acc,
        feature_uniformity,
        feature_alignment,
        representation_rank
    ]
