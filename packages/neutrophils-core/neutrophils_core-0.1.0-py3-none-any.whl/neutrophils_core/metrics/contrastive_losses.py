"""
Contrastive Loss Functions for SimCLR and other contrastive learning methods.

This module implements various contrastive loss functions including:
- NCE (Noise Contrastive Estimation) loss with configurable negative sampling
- NT-Xent (Normalized Temperature-scaled Cross Entropy) loss 
- Batch-wise contrastive accuracy calculation
- Support for different similarity metrics (cosine, euclidean)
- Memory-efficient implementations for large batch sizes
"""

import tensorflow as tf
import numpy as np
from typing import Optional, Callable, Tuple, Dict
from enum import Enum
from sklearn.metrics import roc_auc_score


class SimilarityMetric(Enum):
    """Supported similarity metrics for contrastive learning."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"


class ContrastiveLosses:
    """Collection of contrastive loss functions and utilities."""
    
    @staticmethod
    def cosine_similarity(z1: tf.Tensor, z2: tf.Tensor, axis: int = -1) -> tf.Tensor:
        """
        Compute cosine similarity between two tensors.
        
        Args:
            z1: First tensor of shape [batch_size, embedding_dim]
            z2: Second tensor of shape [batch_size, embedding_dim]
            axis: Axis along which to compute similarity
            
        Returns:
            Cosine similarity tensor of shape [batch_size, batch_size]
        """
        z1_norm = tf.nn.l2_normalize(z1, axis=axis)
        z2_norm = tf.nn.l2_normalize(z2, axis=axis)
        return tf.matmul(z1_norm, z2_norm, transpose_b=True)
    
    @staticmethod
    def euclidean_similarity(z1: tf.Tensor, z2: tf.Tensor) -> tf.Tensor:
        """
        Compute negative euclidean distance as similarity.
        
        Args:
            z1: First tensor of shape [batch_size, embedding_dim]
            z2: Second tensor of shape [batch_size, embedding_dim]
            
        Returns:
            Negative euclidean distance tensor of shape [batch_size, batch_size]
        """
        # Expand dimensions for broadcasting
        z1_expanded = tf.expand_dims(z1, axis=1)  # [batch_size, 1, embedding_dim]
        z2_expanded = tf.expand_dims(z2, axis=0)  # [1, batch_size, embedding_dim]
        
        # Compute squared euclidean distance
        squared_diff = tf.reduce_sum(tf.square(z1_expanded - z2_expanded), axis=-1)
        
        # Return negative distance (higher similarity = smaller distance)
        return -tf.sqrt(squared_diff + 1e-8)
    
    @staticmethod
    def dot_product_similarity(z1: tf.Tensor, z2: tf.Tensor) -> tf.Tensor:
        """
        Compute dot product similarity.
        
        Args:
            z1: First tensor of shape [batch_size, embedding_dim]
            z2: Second tensor of shape [batch_size, embedding_dim]
            
        Returns:
            Dot product similarity tensor of shape [batch_size, batch_size]
        """
        return tf.matmul(z1, z2, transpose_b=True)
    
    @staticmethod
    def get_similarity_function(metric: SimilarityMetric) -> Callable:
        """Get similarity function by metric type."""
        if metric == SimilarityMetric.COSINE:
            return ContrastiveLosses.cosine_similarity
        elif metric == SimilarityMetric.EUCLIDEAN:
            return ContrastiveLosses.euclidean_similarity
        elif metric == SimilarityMetric.DOT_PRODUCT:
            return ContrastiveLosses.dot_product_similarity
        else:
            raise ValueError(f"Unsupported similarity metric: {metric}")


def nce_loss(z1: tf.Tensor, 
             z2: tf.Tensor,
             temperature: float = 0.1,
             negative_sampling_ratio: float = 1.0,
             similarity_metric: SimilarityMetric = SimilarityMetric.COSINE,
             memory_efficient: bool = True) -> tf.Tensor:
    """
    Noise Contrastive Estimation (NCE) loss with configurable negative sampling.
    
    Args:
        z1: First set of embeddings [batch_size, embedding_dim]
        z2: Second set of embeddings [batch_size, embedding_dim]  
        temperature: Temperature parameter for scaling similarities
        negative_sampling_ratio: Ratio of negatives to positives
        similarity_metric: Metric to use for computing similarities
        memory_efficient: Whether to use memory-efficient implementation
        
    Returns:
        NCE loss tensor
    """
    batch_size = tf.shape(z1)[0]
    batch_size = tf.cast(batch_size, tf.int32)
    
    # Ensure inputs are float32
    z1 = tf.cast(z1, tf.float32)
    z2 = tf.cast(z2, tf.float32)
    
    # Get similarity function
    sim_fn = ContrastiveLosses.get_similarity_function(similarity_metric)
    
    def standard_path():
        """Standard NCE loss calculation for smaller batches."""
        # Compute similarity matrix
        similarities = sim_fn(z1, z2) / temperature
        
        # Create positive mask (diagonal elements)
        positive_mask = tf.eye(batch_size, dtype=tf.bool)
        
        # Sample negatives based on ratio
        num_negatives = tf.cast(
            tf.cast(batch_size, tf.float32) * negative_sampling_ratio, tf.int32
        )
        num_negatives = tf.maximum(num_negatives, 1)  # Ensure at least 1 negative
        
        # Get positive similarities
        positive_similarities = tf.boolean_mask(similarities, positive_mask)
        
        # Get negative similarities (off-diagonal elements)
        negative_mask = tf.logical_not(positive_mask)
        negative_similarities = tf.boolean_mask(similarities, negative_mask)
        
        # Sample negatives if ratio < 1.0
        if negative_sampling_ratio < 1.0:
            negative_similarities = tf.random.shuffle(negative_similarities)[:num_negatives]
        
        # Compute NCE loss
        positive_loss = -tf.math.log_sigmoid(positive_similarities)
        negative_loss = -tf.math.log_sigmoid(-negative_similarities)
        
        # Combine losses
        total_positive_loss = tf.reduce_mean(positive_loss)
        total_negative_loss = tf.reduce_mean(negative_loss)
        
        return total_positive_loss + total_negative_loss

    if memory_efficient:
        return tf.cond(
            tf.greater(batch_size, 256),
            lambda: _memory_efficient_nce_loss(z1, z2, temperature, negative_sampling_ratio, sim_fn),
            standard_path
        )
    
    return standard_path()


def _memory_efficient_nce_loss(z1: tf.Tensor,
                              z2: tf.Tensor, 
                              temperature: float,
                              negative_sampling_ratio: float,
                              sim_fn: Callable) -> tf.Tensor:
    """Memory-efficient NCE loss for large batches."""
    batch_size = tf.shape(z1)[0]
    batch_size = tf.cast(batch_size, tf.int32)
    chunk_size = 128  # Process in chunks to save memory
    
    total_loss = tf.constant(0.0, dtype=tf.float32)
    num_chunks = tf.math.ceil(tf.cast(batch_size, tf.float32) / tf.cast(chunk_size, tf.float32))
    num_chunks = tf.cast(num_chunks, tf.int32)
    
    for i in tf.range(num_chunks):
        start_idx = i * chunk_size
        end_idx = tf.minimum((i + 1) * chunk_size, batch_size)
        
        z1_chunk = z1[start_idx:end_idx]
        z2_chunk = z2[start_idx:end_idx]
        
        # Compute similarities for chunk
        similarities = sim_fn(z1_chunk, z2_chunk) / temperature
        
        # Process chunk loss
        chunk_size_actual = end_idx - start_idx
        positive_mask = tf.eye(chunk_size_actual, dtype=tf.bool)
        
        positive_similarities = tf.boolean_mask(similarities, positive_mask)
        negative_similarities = tf.boolean_mask(similarities, tf.logical_not(positive_mask))
        
        # Sample negatives
        num_negatives = tf.cast(
            tf.cast(chunk_size_actual, tf.float32) * negative_sampling_ratio, tf.int32
        )
        num_negatives = tf.maximum(num_negatives, 1)  # Ensure at least 1 negative
        if negative_sampling_ratio < 1.0:
            negative_similarities = tf.random.shuffle(negative_similarities)[:num_negatives]
        
        # Compute chunk loss
        positive_loss = tf.reduce_mean(-tf.math.log_sigmoid(positive_similarities))
        negative_loss = tf.reduce_mean(-tf.math.log_sigmoid(-negative_similarities))
        
        total_loss += (positive_loss + negative_loss) / tf.cast(num_chunks, tf.float32)
    
    return total_loss


def nt_xent_loss(z1: tf.Tensor,
                 z2: tf.Tensor, 
                 temperature: float = 0.1,
                 similarity_metric: SimilarityMetric = SimilarityMetric.COSINE,
                 memory_efficient: bool = True) -> tf.Tensor:
    """
    Normalized Temperature-scaled Cross Entropy (NT-Xent) loss.
    
    This is the standard SimCLR loss function.
    
    Args:
        z1: First set of embeddings [batch_size, embedding_dim]
        z2: Second set of embeddings [batch_size, embedding_dim]
        temperature: Temperature parameter for scaling similarities
        similarity_metric: Metric to use for computing similarities
        memory_efficient: Whether to use memory-efficient implementation
        
    Returns:
        NT-Xent loss tensor
    """
    batch_size = tf.shape(z1)[0]
    batch_size = tf.cast(batch_size, tf.int32)
    
    # Ensure inputs are float32
    z1 = tf.cast(z1, tf.float32)
    z2 = tf.cast(z2, tf.float32)
    
    # Get similarity function
    sim_fn = ContrastiveLosses.get_similarity_function(similarity_metric)
    
    def standard_path():
        """Standard NT-Xent loss calculation for smaller batches."""
        # Concatenate z1 and z2 to create full batch
        z = tf.concat([z1, z2], axis=0)  # [2*batch_size, embedding_dim]
        
        # Compute similarity matrix
        similarities = sim_fn(z, z) / temperature  # [2*batch_size, 2*batch_size]
        
        # Create labels for positive pairs
        # For each sample i in z1, its positive is sample (i + batch_size) in z2
        # For each sample i in z2, its positive is sample (i - batch_size) in z1
        labels = tf.concat([
            tf.range(batch_size, 2 * batch_size, dtype=tf.int32),  # z1 positives are in z2
            tf.range(0, batch_size, dtype=tf.int32)                # z2 positives are in z1
        ], axis=0)
        
        # Mask out self-similarities (diagonal)
        mask = tf.logical_not(tf.eye(2 * batch_size, dtype=tf.bool))
        similarities = tf.where(mask, similarities, tf.constant(-1e9, dtype=similarities.dtype))
        
        # Compute cross entropy loss
        loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=labels, logits=similarities
        )
        
        return tf.reduce_mean(loss)

    if memory_efficient:
        return tf.cond(
            tf.greater(batch_size, 256),
            lambda: _memory_efficient_nt_xent_loss(z1, z2, temperature, sim_fn),
            standard_path
        )
    
    return standard_path()


def _memory_efficient_nt_xent_loss(z1: tf.Tensor,
                                  z2: tf.Tensor,
                                  temperature: float,
                                  sim_fn: Callable) -> tf.Tensor:
    """Memory-efficient NT-Xent loss for large batches."""
    batch_size = tf.shape(z1)[0]
    batch_size = tf.cast(batch_size, tf.int32)
    chunk_size = 128

    num_chunks = tf.math.ceil(tf.cast(batch_size, tf.float32) / tf.cast(chunk_size, tf.float32))
    num_chunks = tf.cast(num_chunks, tf.int32)

    def cond(i, total_loss):
        return i < num_chunks

    def body(i, total_loss):
        start_idx = i * chunk_size
        end_idx = tf.minimum((i + 1) * chunk_size, batch_size)

        z1_chunk = z1[start_idx:end_idx]
        z2_chunk = z2[start_idx:end_idx]

        # Compute NT-Xent for chunk
        chunk_z = tf.concat([z1_chunk, z2_chunk], axis=0)
        chunk_size_actual = end_idx - start_idx

        similarities = sim_fn(chunk_z, chunk_z) / temperature

        labels = tf.concat([
            tf.range(chunk_size_actual, 2 * chunk_size_actual, dtype=tf.int32),
            tf.range(0, chunk_size_actual, dtype=tf.int32)
        ], axis=0)

        indices = tf.range(2 * chunk_size_actual)
        mask = tf.not_equal(
            tf.expand_dims(indices, 0),
            tf.expand_dims(indices, 1)
        )
        similarities = tf.where(mask, similarities, tf.constant(-1e9, dtype=similarities.dtype))

        chunk_loss = tf.reduce_mean(
            tf.nn.sparse_softmax_cross_entropy_with_logits(
                labels=labels, logits=similarities
            )
        )

        total_loss = total_loss + (chunk_loss / tf.cast(num_chunks, tf.float32))
        return i + 1, total_loss

    i = tf.constant(0)
    total_loss = tf.constant(0.0, dtype=tf.float32)
    _, total_loss = tf.while_loop(cond, body, [i, total_loss], maximum_iterations=num_chunks)
    return total_loss


def contrastive_accuracy(z1: tf.Tensor,
                        z2: tf.Tensor,
                        similarity_metric: SimilarityMetric = SimilarityMetric.COSINE,
                        top_k: int = 1) -> tf.Tensor:
    """
    Compute batch-wise contrastive accuracy.
    
    Measures how often the true positive pair has the highest similarity
    among all possible pairs in the batch.
    
    Args:
        z1: First set of embeddings [batch_size, embedding_dim]
        z2: Second set of embeddings [batch_size, embedding_dim]
        similarity_metric: Metric to use for computing similarities
        top_k: Consider top-k predictions as correct
        
    Returns:
        Contrastive accuracy tensor
    """
    batch_size = tf.shape(z1)[0]
    batch_size = tf.cast(batch_size, tf.int32)
    
    # Ensure inputs are float32
    z1 = tf.cast(z1, tf.float32)
    z2 = tf.cast(z2, tf.float32)
    
    # Get similarity function
    sim_fn = ContrastiveLosses.get_similarity_function(similarity_metric)
    
    # Compute similarities
    similarities = sim_fn(z1, z2)  # [batch_size, batch_size]
    
    # True labels are diagonal (each z1[i] pairs with z2[i])
    true_labels = tf.range(batch_size, dtype=tf.int32)
    
    # Get top-k predictions
    _, top_k_indices = tf.nn.top_k(similarities, k=top_k)
    
    # Check if true label is in top-k predictions
    correct_predictions = tf.reduce_any(
        tf.equal(tf.expand_dims(true_labels, axis=1), top_k_indices),
        axis=1
    )
    
    return tf.reduce_mean(tf.cast(correct_predictions, tf.float32))


def supervised_contrastive_loss(embeddings: tf.Tensor,
                               labels: tf.Tensor,
                               temperature: float = 0.1,
                               similarity_metric: SimilarityMetric = SimilarityMetric.COSINE) -> tf.Tensor:
    """
    Supervised contrastive loss that uses label information.
    
    Args:
        embeddings: Embeddings tensor [batch_size, embedding_dim]
        labels: Class labels [batch_size]
        temperature: Temperature parameter
        similarity_metric: Similarity metric to use
        
    Returns:
        Supervised contrastive loss
    """
    batch_size = tf.shape(embeddings)[0]
    batch_size = tf.cast(batch_size, tf.int32)
    
    # Ensure inputs are float32
    embeddings = tf.cast(embeddings, tf.float32)
    labels = tf.cast(labels, tf.int32)
    
    # Get similarity function
    sim_fn = ContrastiveLosses.get_similarity_function(similarity_metric)
    
    # Compute similarities
    similarities = sim_fn(embeddings, embeddings) / temperature
    
    # Create positive mask (same class)
    labels_expanded = tf.expand_dims(labels, axis=1)
    positive_mask = tf.equal(labels_expanded, tf.transpose(labels_expanded))
    
    # Remove self-similarities
    positive_mask = tf.logical_and(
        positive_mask,
        tf.logical_not(tf.eye(batch_size, dtype=tf.bool))
    )
    
    # Compute loss for each anchor
    total_loss = 0.0
    
    for i in range(batch_size):
        # Get positive samples for anchor i
        positive_indices = tf.where(positive_mask[i])[:, 0]
        
        if tf.size(positive_indices) > 0:
            # Compute log-sum-exp for negatives
            negative_mask = tf.logical_not(positive_mask[i])
            negative_similarities = tf.boolean_mask(similarities[i], negative_mask)
            
            # For each positive, compute loss
            positive_similarities = tf.gather(similarities[i], positive_indices)
            
            for pos_sim in positive_similarities:
                # Combine positive with all negatives
                all_similarities = tf.concat([
                    tf.expand_dims(pos_sim, 0),
                    negative_similarities
                ], axis=0)
                
                # Compute softmax loss (positive should have highest probability)
                loss = -pos_sim + tf.reduce_logsumexp(all_similarities)
                total_loss += loss
    
    # Normalize by number of positive pairs
    num_positive_pairs = tf.reduce_sum(tf.cast(positive_mask, tf.float32))
    return total_loss / tf.maximum(num_positive_pairs, 1.0)


class ContrastiveLossTracker:
    """Utility class for tracking contrastive learning metrics during training."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all tracked metrics."""
        self.total_loss = 0.0
        self.total_accuracy = 0.0
        self.num_batches = 0
        self.loss_history = []
        self.accuracy_history = []
    
    def update(self, loss: float, accuracy: float):
        """Update tracked metrics with new batch results."""
        self.total_loss += loss
        self.total_accuracy += accuracy
        self.num_batches += 1
        self.loss_history.append(loss)
        self.accuracy_history.append(accuracy)
    
    def get_averages(self) -> Dict[str, float]:
        """Get average metrics across all batches."""
        if self.num_batches == 0:
            return {"avg_loss": 0.0, "avg_accuracy": 0.0}
        
        return {
            "avg_loss": self.total_loss / self.num_batches,
            "avg_accuracy": self.total_accuracy / self.num_batches,
            "num_batches": self.num_batches
        }
    
    def get_recent_averages(self, last_n: int = 10) -> Dict[str, float]:
        """Get average metrics for the last N batches."""
        if not self.loss_history:
            return {"recent_avg_loss": 0.0, "recent_avg_accuracy": 0.0}
        
        recent_losses = self.loss_history[-last_n:]
        recent_accuracies = self.accuracy_history[-last_n:]
        
        return {
            "recent_avg_loss": np.mean(recent_losses),
            "recent_avg_accuracy": np.mean(recent_accuracies),
            "recent_batches": len(recent_losses)
        }


# Utility functions for easy access
def create_nce_loss_fn(temperature: float = 0.1,
                      negative_sampling_ratio: float = 1.0,
                      similarity_metric: str = "cosine",
                      memory_efficient: bool = True) -> Callable:
    """Create NCE loss function with specified parameters."""
    metric = SimilarityMetric(similarity_metric)
    
    def loss_fn(z1, z2):
        return nce_loss(z1, z2, temperature, negative_sampling_ratio, metric, memory_efficient)
    
    return loss_fn


def create_nt_xent_loss_fn(temperature: float = 0.1,
                          similarity_metric: str = "cosine",
                          memory_efficient: bool = True) -> Callable:
    """Create NT-Xent loss function with specified parameters."""
    metric = SimilarityMetric(similarity_metric)
    
    def loss_fn(z1, z2):
        return nt_xent_loss(z1, z2, temperature, metric, memory_efficient)
    
    return loss_fn


def create_contrastive_accuracy_fn(similarity_metric: str = "cosine",
                                  top_k: int = 1) -> Callable:
    """Create contrastive accuracy function with specified parameters."""
    metric = SimilarityMetric(similarity_metric)
    
    def accuracy_fn(z1, z2):
        return contrastive_accuracy(z1, z2, metric, top_k)
    
    return accuracy_fn


def calculate_contrastive_metrics_np(similarity_matrix: np.ndarray, k_values: list = [1, 3, 5]) -> Dict:
    """
    Calculates a suite of contrastive metrics from a numpy similarity matrix.
    This function is designed for post-hoc analysis and uses numpy for calculations.

    Args:
        similarity_matrix: A [batch_size, batch_size] numpy array of similarity scores
                           where the diagonal represents the positive pairs.
        k_values: A list of integers for which top-k metrics will be calculated.

    Returns:
        A dictionary containing aggregated metrics. The structure is:
        {
            'auc': float,
            'top_1': {'accuracy': float, 'precision': float, ...},
            'top_3': {'accuracy': float, 'precision': float, ...},
            ...
        }
    """
    batch_size = similarity_matrix.shape[0]
    if batch_size == 0:
        return {}

    true_labels_vector = np.arange(batch_size)

    # --- AUC Calculation ---
    # For each anchor (row), we have a binary classification problem:
    # Is the retrieved item the correct positive pair?
    all_aucs = []
    for i in range(batch_size):
        # The true label for the i-th anchor is the i-th item.
        y_true = (true_labels_vector == i).astype(int)
        y_score = similarity_matrix[i, :]
        
        # Remove the anchor itself from its list of candidates
        y_true_auc = np.delete(y_true, i)
        y_score_auc = np.delete(y_score, i)

        # Ensure there are both positive and negative samples to calculate AUC
        if len(np.unique(y_true_auc)) > 1:
            try:
                all_aucs.append(roc_auc_score(y_true_auc, y_score_auc))
            except ValueError:
                # This can happen if all scores are identical, etc.
                continue

    avg_auc = np.mean(all_aucs) if all_aucs else 0.0

    # --- Top-K Metrics ---
    # Get top-k predictions by sorting similarities for each anchor
    top_k_indices = np.argsort(similarity_matrix, axis=1)[:, ::-1]

    results = {'auc': avg_auc}
    for k in k_values:
        # For each anchor, check if the true positive is in the top k predictions
        top_k_preds = top_k_indices[:, :k]
        
        # Recall@k (and Accuracy@k) is the proportion of anchors where the true positive was found
        hits = np.any(top_k_preds == true_labels_vector[:, np.newaxis], axis=1)
        recall_at_k = np.mean(hits)

        # Precision@k: For each anchor, precision is 1/k if the positive is found, 0 otherwise.
        # The average precision@k is recall@k / k.
        precision_at_k = recall_at_k / k

        if (precision_at_k + recall_at_k) > 0:
            f1_at_k = 2 * (precision_at_k * recall_at_k) / (precision_at_k + recall_at_k)
        else:
            f1_at_k = 0.0

        results[f'top_{k}'] = {
            'accuracy': recall_at_k,
            'recall': recall_at_k,
            'precision': precision_at_k,
            'f1_score': f1_at_k
        }
        
    return results
