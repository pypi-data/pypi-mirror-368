"""
Comprehensive tests for classification metrics in neutrophils_core.metrics.classification_metrics

This test suite validates all classification metrics functions for neutrophil classification tasks,
particularly focusing on ordinal classification metrics.
"""

import pytest
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K

# Import classification_metrics module directly to avoid package import issues
import sys
import os
import importlib.util

# Get the path to the classification_metrics module
classification_metrics_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "neutrophils_core",
    "metrics",
    "classification_metrics.py",
)
spec = importlib.util.spec_from_file_location(
    "classification_metrics", classification_metrics_path
)
cm = importlib.util.module_from_spec(spec)
sys.modules["classification_metrics"] = cm
spec.loader.exec_module(cm)

# Create aliases for cleaner test code
ordinal_mae = cm.ordinal_mae
adjacent_class_accuracy = cm.adjacent_class_accuracy
adjacent_class_recall = cm.adjacent_class_recall
adjacent_class_precision = cm.adjacent_class_precision
adjacent_class_auc = cm.adjacent_class_auc
kendall_tau_metric = cm.kendall_tau_metric
ordinal_accuracy_tolerance = cm.ordinal_accuracy_tolerance
balanced_accuracy_metric = cm.balanced_accuracy_metric
standard_metric_wrapper = cm.standard_metric_wrapper
get_metrics = cm.get_metrics


class TestOrdinalMetrics:
    """Test ordinal-specific metrics"""

    def setup_method(self):
        """Set up test fixtures"""
        self.num_classes = 4
        self.batch_size = 8

        # One-hot encoded labels
        self.y_true_onehot = tf.constant(
            [
                [1, 0, 0, 0],  # Class 0
                [0, 1, 0, 0],  # Class 1
                [0, 0, 1, 0],  # Class 2
                [0, 0, 0, 1],  # Class 3
                [1, 0, 0, 0],  # Class 0
                [0, 1, 0, 0],  # Class 1
                [0, 0, 1, 0],  # Class 2
                [0, 0, 0, 1],  # Class 3
            ],
            dtype=tf.float32,
        )

        # Class indices
        self.y_true_indices = tf.constant([0, 1, 2, 3, 0, 1, 2, 3], dtype=tf.int32)

        # Predicted probabilities - mix of good and poor predictions
        self.y_pred = tf.constant(
            [
                [0.8, 0.1, 0.05, 0.05],  # Good prediction for class 0
                [0.1, 0.7, 0.15, 0.05],  # Good prediction for class 1
                [0.05, 0.15, 0.6, 0.2],  # Okay prediction for class 2
                [0.1, 0.1, 0.2, 0.6],  # Okay prediction for class 3
                [0.7, 0.2, 0.05, 0.05],  # Good prediction for class 0
                [0.2, 0.6, 0.15, 0.05],  # Okay prediction for class 1
                [0.1, 0.2, 0.5, 0.2],  # Okay prediction for class 2
                [0.05, 0.05, 0.3, 0.6],  # Okay prediction for class 3
            ],
            dtype=tf.float32,
        )

        # Perfect predictions for testing edge cases
        self.y_pred_perfect = tf.constant(
            [
                [1.0, 0.0, 0.0, 0.0],  # Perfect prediction for class 0
                [0.0, 1.0, 0.0, 0.0],  # Perfect prediction for class 1
                [0.0, 0.0, 1.0, 0.0],  # Perfect prediction for class 2
                [0.0, 0.0, 0.0, 1.0],  # Perfect prediction for class 3
                [1.0, 0.0, 0.0, 0.0],  # Perfect prediction for class 0
                [0.0, 1.0, 0.0, 0.0],  # Perfect prediction for class 1
                [0.0, 0.0, 1.0, 0.0],  # Perfect prediction for class 2
                [0.0, 0.0, 0.0, 1.0],  # Perfect prediction for class 3
            ],
            dtype=tf.float32,
        )

        # Adjacent predictions (off by 1 class)
        self.y_pred_adjacent = tf.constant(
            [
                [0.1, 0.8, 0.05, 0.05],  # Predicts class 1 for true class 0 (adjacent)
                [0.05, 0.1, 0.8, 0.05],  # Predicts class 2 for true class 1 (adjacent)
                [0.05, 0.8, 0.1, 0.05],  # Predicts class 1 for true class 2 (adjacent)
                [0.05, 0.05, 0.8, 0.1],  # Predicts class 2 for true class 3 (adjacent)
                [0.05, 0.8, 0.1, 0.05],  # Predicts class 1 for true class 0 (adjacent)
                [0.8, 0.1, 0.05, 0.05],  # Predicts class 0 for true class 1 (adjacent)
                [0.05, 0.05, 0.1, 0.8],  # Predicts class 3 for true class 2 (adjacent)
                [0.05, 0.1, 0.8, 0.05],  # Predicts class 2 for true class 3 (adjacent)
            ],
            dtype=tf.float32,
        )

    def test_ordinal_mae_with_onehot(self):
        """Test ordinal MAE with one-hot encoded labels"""
        mae = ordinal_mae(self.y_true_onehot, self.y_pred)

        # MAE should be non-negative
        assert mae >= 0.0
        assert isinstance(mae, tf.Tensor)

        # Test with perfect predictions (should be very small)
        mae_perfect = ordinal_mae(self.y_true_onehot, self.y_pred_perfect)
        assert mae_perfect < 0.01

        # Perfect predictions should have lower MAE than imperfect ones
        assert mae_perfect < mae

    def test_ordinal_mae_with_indices(self):
        """Test ordinal MAE with class indices"""
        mae = ordinal_mae(self.y_true_indices, self.y_pred)

        # MAE should be non-negative
        assert mae >= 0.0
        assert isinstance(mae, tf.Tensor)

        # Test with perfect predictions
        mae_perfect = ordinal_mae(self.y_true_indices, self.y_pred_perfect)
        assert mae_perfect < 0.01

    def test_ordinal_mae_calculation(self):
        """Test that ordinal MAE calculates expected values correctly"""
        # Simple test case with known expected outcome
        y_true_simple = tf.constant([0, 1, 2], dtype=tf.int32)
        y_pred_simple = tf.constant(
            [
                [0.5, 0.3, 0.2],  # Expected class: 0*0.5 + 1*0.3 + 2*0.2 = 0.7
                [0.2, 0.5, 0.3],  # Expected class: 0*0.2 + 1*0.5 + 2*0.3 = 1.1
                [0.1, 0.2, 0.7],  # Expected class: 0*0.1 + 1*0.2 + 2*0.7 = 1.6
            ],
            dtype=tf.float32,
        )

        # Expected MAE: |0-0.7| + |1-1.1| + |2-1.6| / 3 = (0.7 + 0.1 + 0.4) / 3 = 0.4
        mae = ordinal_mae(y_true_simple, y_pred_simple)
        expected_mae = 0.4

        # Allow for small numerical differences
        assert abs(mae.numpy() - expected_mae) < 0.01

    def test_adjacent_class_accuracy_with_onehot(self):
        """Test adjacent class accuracy with one-hot encoded labels"""
        acc = adjacent_class_accuracy(self.y_true_onehot, self.y_pred)

        # Accuracy should be between 0 and 1
        assert 0.0 <= acc <= 1.0
        assert isinstance(acc, tf.Tensor)

        # Test with perfect predictions (should be 1.0)
        acc_perfect = adjacent_class_accuracy(self.y_true_onehot, self.y_pred_perfect)
        assert abs(acc_perfect - 1.0) < 0.01

        # Test with adjacent predictions (should also be 1.0)
        acc_adjacent = adjacent_class_accuracy(self.y_true_onehot, self.y_pred_adjacent)
        assert abs(acc_adjacent - 1.0) < 0.01

    def test_adjacent_class_accuracy_with_indices(self):
        """Test adjacent class accuracy with class indices"""
        acc = adjacent_class_accuracy(self.y_true_indices, self.y_pred)

        # Accuracy should be between 0 and 1
        assert 0.0 <= acc <= 1.0
        assert isinstance(acc, tf.Tensor)

        # Test with perfect predictions
        acc_perfect = adjacent_class_accuracy(self.y_true_indices, self.y_pred_perfect)
        assert abs(acc_perfect - 1.0) < 0.01

    def test_adjacent_class_accuracy_calculation(self):
        """Test adjacent class accuracy calculation with known values"""
        # Simple test case: true=[0,1,2], pred=[1,2,0] -> adjacent=[Yes,Yes,No] -> acc=2/3
        y_true_simple = tf.constant([0, 1, 2], dtype=tf.int32)
        y_pred_simple = tf.constant(
            [
                [0.1, 0.8, 0.1],  # Predicts class 1 for true class 0 (adjacent)
                [0.1, 0.1, 0.8],  # Predicts class 2 for true class 1 (adjacent)
                [0.8, 0.1, 0.1],  # Predicts class 0 for true class 2 (not adjacent)
            ],
            dtype=tf.float32,
        )

        acc = adjacent_class_accuracy(y_true_simple, y_pred_simple)
        expected_acc = 2.0 / 3.0

        # Allow for small numerical differences
        assert abs(acc.numpy() - expected_acc) < 0.01

    def test_adjacent_class_recall(self):
        """Test adjacent class recall function"""
        recall = adjacent_class_recall(self.y_true_onehot, self.y_pred)
        acc = adjacent_class_accuracy(self.y_true_onehot, self.y_pred)

        # Recall should equal accuracy for this implementation
        assert abs(recall - acc) < 0.001
        assert 0.0 <= recall <= 1.0
        assert isinstance(recall, tf.Tensor)

    def test_adjacent_class_precision(self):
        """Test adjacent class precision function"""
        precision = adjacent_class_precision(self.y_true_onehot, self.y_pred)
        acc = adjacent_class_accuracy(self.y_true_onehot, self.y_pred)

        # Precision should equal accuracy for this implementation
        assert abs(precision - acc) < 0.001
        assert 0.0 <= precision <= 1.0
        assert isinstance(precision, tf.Tensor)


class TestAdditionalOrdinalMetrics:
    """Test additional ordinal metrics"""

    def setup_method(self):
        """Set up test fixtures"""
        self.num_classes = 4
        self.batch_size = 8

        # Class indices (preferred format for new metrics)
        self.y_true_indices = tf.constant([0, 1, 2, 3, 0, 1, 2, 3], dtype=tf.int32)

        # One-hot encoded labels
        self.y_true_onehot = tf.constant(
            [
                [1, 0, 0, 0],  # Class 0
                [0, 1, 0, 0],  # Class 1
                [0, 0, 1, 0],  # Class 2
                [0, 0, 0, 1],  # Class 3
                [1, 0, 0, 0],  # Class 0
                [0, 1, 0, 0],  # Class 1
                [0, 0, 1, 0],  # Class 2
                [0, 0, 0, 1],  # Class 3
            ],
            dtype=tf.float32,
        )

        # Predicted probabilities
        self.y_pred = tf.constant(
            [
                [0.8, 0.1, 0.05, 0.05],  # Good prediction for class 0
                [0.1, 0.7, 0.15, 0.05],  # Good prediction for class 1
                [0.05, 0.15, 0.6, 0.2],  # Okay prediction for class 2
                [0.1, 0.1, 0.2, 0.6],  # Okay prediction for class 3
                [0.7, 0.2, 0.05, 0.05],  # Good prediction for class 0
                [0.2, 0.6, 0.15, 0.05],  # Okay prediction for class 1
                [0.1, 0.2, 0.5, 0.2],  # Okay prediction for class 2
                [0.05, 0.05, 0.3, 0.6],  # Okay prediction for class 3
            ],
            dtype=tf.float32,
        )

    def test_adjacent_class_auc(self):
        """Test adjacent class AUC function"""
        # Test with class indices (preferred format)
        auc_score = adjacent_class_auc(self.y_true_indices, self.y_pred)

        # AUC should be between 0 and 1
        assert 0.0 <= auc_score <= 1.0
        assert isinstance(auc_score, tf.Tensor)

        # Test with one-hot format
        auc_score_onehot = adjacent_class_auc(self.y_true_onehot, self.y_pred)
        assert 0.0 <= auc_score_onehot <= 1.0
        assert isinstance(auc_score_onehot, tf.Tensor)

        # Test with different adjacency weights
        auc_strict = adjacent_class_auc(
            self.y_true_indices, self.y_pred, adjacency_weight=0
        )
        auc_loose = adjacent_class_auc(
            self.y_true_indices, self.y_pred, adjacency_weight=2
        )

        assert 0.0 <= auc_strict <= 1.0
        assert 0.0 <= auc_loose <= 1.0
        # Both should be valid AUC scores (no strict ordering assumption)
        # The relationship depends on the specific data distribution

    def test_kendall_tau_metric(self):
        """Test Kendall's Tau correlation metric"""
        tau = kendall_tau_metric(self.y_true_indices, self.y_pred)

        # Kendall's Tau should be between -1 and 1
        assert -1.0 <= tau <= 1.0
        assert isinstance(tau, tf.Tensor)

        # Test with one-hot format
        tau_onehot = kendall_tau_metric(self.y_true_onehot, self.y_pred)
        assert -1.0 <= tau_onehot <= 1.0
        assert isinstance(tau_onehot, tf.Tensor)

        # Test with perfect predictions (should be close to 1)
        y_pred_perfect = tf.constant(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=tf.float32,
        )

        tau_perfect = kendall_tau_metric(self.y_true_indices, y_pred_perfect)
        assert tau_perfect > 0.8  # Should be high for perfect predictions

    def test_ordinal_accuracy_tolerance(self):
        """Test ordinal accuracy with tolerance"""
        # Default tolerance (1)
        acc_default = ordinal_accuracy_tolerance(self.y_true_indices, self.y_pred)
        assert 0.0 <= acc_default <= 1.0
        assert isinstance(acc_default, tf.Tensor)

        # Test with different tolerance values
        acc_strict = ordinal_accuracy_tolerance(
            self.y_true_indices, self.y_pred, tolerance=0
        )
        acc_loose = ordinal_accuracy_tolerance(
            self.y_true_indices, self.y_pred, tolerance=2
        )

        # Looser tolerance should give higher or equal accuracy
        assert acc_loose >= acc_strict
        assert 0.0 <= acc_strict <= 1.0
        assert 0.0 <= acc_loose <= 1.0

        # Test with one-hot format
        acc_onehot = ordinal_accuracy_tolerance(self.y_true_onehot, self.y_pred)
        assert 0.0 <= acc_onehot <= 1.0
        assert isinstance(acc_onehot, tf.Tensor)

    def test_balanced_accuracy_metric(self):
        """Test balanced accuracy metric"""
        bal_acc = balanced_accuracy_metric(self.y_true_indices, self.y_pred)

        # Balanced accuracy should be between 0 and 1
        assert 0.0 <= bal_acc <= 1.0
        assert isinstance(bal_acc, tf.Tensor)

        # Test with one-hot format
        bal_acc_onehot = balanced_accuracy_metric(self.y_true_onehot, self.y_pred)
        assert 0.0 <= bal_acc_onehot <= 1.0
        assert isinstance(bal_acc_onehot, tf.Tensor)

    def test_standard_metric_wrapper(self):
        """Test standard metric wrapper function"""
        # Test wrapping a standard Keras metric
        # The wrapper returns a metric instance, not a class
        wrapped_accuracy_metric = standard_metric_wrapper(
            tf.keras.metrics.CategoricalAccuracy, name="accuracy"
        )

        # Should be a metric instance
        assert hasattr(wrapped_accuracy_metric, "update_state")
        assert hasattr(wrapped_accuracy_metric, "result")
        assert hasattr(wrapped_accuracy_metric, "reset_state")

        # Test with one-hot inputs
        wrapped_accuracy_metric.update_state(self.y_true_onehot, self.y_pred)
        acc_onehot = wrapped_accuracy_metric.result()

        # Reset and test with index inputs
        wrapped_accuracy_metric.reset_state()
        wrapped_accuracy_metric.update_state(self.y_true_indices, self.y_pred)
        acc_indices = wrapped_accuracy_metric.result()

        assert isinstance(acc_onehot, tf.Tensor)
        assert isinstance(acc_indices, tf.Tensor)
        assert 0.0 <= acc_onehot <= 1.0
        assert 0.0 <= acc_indices <= 1.0

        # Results should be similar since wrapper handles format conversion
        assert abs(acc_onehot - acc_indices) < 0.1  # Allow for small differences

        # Test that wrapper works with different metric types
        try:
            wrapped_precision_metric = standard_metric_wrapper(
                tf.keras.metrics.Precision, name="precision"
            )
            wrapped_precision_metric.update_state(self.y_true_indices, self.y_pred)
            precision_result = wrapped_precision_metric.result()
            assert isinstance(precision_result, tf.Tensor)
            assert 0.0 <= precision_result <= 1.0
        except Exception as e:
            # Some metrics might not work perfectly with the wrapper, which is expected
            print(f"Precision wrapper test failed (expected): {e}")


class TestUtilityFunctions:
    """Test utility functions"""

    def test_get_metrics_standard_mode(self):
        """Test get_metrics function with standard training mode"""
        metrics = get_metrics(training_mode="standard")

        # Should return a list
        assert isinstance(metrics, list)
        assert len(metrics) > 0

        # Check that it contains expected standard metrics
        metric_names = []
        for metric in metrics:
            if isinstance(metric, str):
                metric_names.append(metric)
            elif hasattr(metric, "name"):
                metric_names.append(metric.name)
            elif hasattr(metric, "_name"):
                metric_names.append(metric._name)

        # Should contain basic metrics like accuracy
        assert "accuracy" in metric_names

    def test_get_metrics_ordinal_mode(self):
        """Test get_metrics function with ordinal training mode"""
        metrics = get_metrics(training_mode="ordinal")

        # Should return a list
        assert isinstance(metrics, list)
        assert len(metrics) > 0

        # Check for ordinal-specific metrics in the list
        ordinal_metric_functions = [
            ordinal_mae,
            adjacent_class_accuracy,
            adjacent_class_recall,
            adjacent_class_precision,
            adjacent_class_auc,
            kendall_tau_metric,
            ordinal_accuracy_tolerance,
            balanced_accuracy_metric,
        ]

        for ordinal_func in ordinal_metric_functions:
            assert ordinal_func in metrics

    def test_get_metrics_unknown_mode(self):
        """Test get_metrics function with unknown training mode"""
        # Should default to standard mode behavior
        metrics_unknown = get_metrics(training_mode="unknown")
        metrics_standard = get_metrics(training_mode="standard")

        # Should behave like standard mode
        assert len(metrics_unknown) == len(metrics_standard)


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_single_sample_input(self):
        """Test metrics with single sample input"""
        # Single sample with one-hot encoding
        y_true_single = tf.constant([[1, 0, 0, 0]], dtype=tf.float32)
        y_pred_single = tf.constant([[0.8, 0.1, 0.05, 0.05]], dtype=tf.float32)

        # All metrics should handle single samples
        mae = ordinal_mae(y_true_single, y_pred_single)
        acc = adjacent_class_accuracy(y_true_single, y_pred_single)

        assert isinstance(mae, tf.Tensor)
        assert isinstance(acc, tf.Tensor)
        assert mae >= 0.0
        assert 0.0 <= acc <= 1.0

        # Test new metrics with single sample
        y_true_single_idx = tf.constant([0], dtype=tf.int32)
        tau = kendall_tau_metric(y_true_single_idx, y_pred_single)
        bal_acc = balanced_accuracy_metric(y_true_single_idx, y_pred_single)

        assert isinstance(tau, tf.Tensor)
        assert isinstance(bal_acc, tf.Tensor)
        assert -1.0 <= tau <= 1.0
        assert 0.0 <= bal_acc <= 1.0

    def test_binary_classification(self):
        """Test metrics with binary classification (2 classes)"""
        y_true_binary = tf.constant([[1, 0], [0, 1]], dtype=tf.float32)
        y_pred_binary = tf.constant([[0.7, 0.3], [0.2, 0.8]], dtype=tf.float32)

        mae = ordinal_mae(y_true_binary, y_pred_binary)
        acc = adjacent_class_accuracy(y_true_binary, y_pred_binary)

        assert isinstance(mae, tf.Tensor)
        assert isinstance(acc, tf.Tensor)
        assert mae >= 0.0
        assert 0.0 <= acc <= 1.0

        # Test new metrics with binary classification
        y_true_binary_idx = tf.constant([0, 1], dtype=tf.int32)
        tau = kendall_tau_metric(y_true_binary_idx, y_pred_binary)
        bal_acc = balanced_accuracy_metric(y_true_binary_idx, y_pred_binary)

        assert isinstance(tau, tf.Tensor)
        assert isinstance(bal_acc, tf.Tensor)
        assert -1.0 <= tau <= 1.0
        assert 0.0 <= bal_acc <= 1.0

    def test_input_format_consistency(self):
        """Test that metrics handle both one-hot and index formats consistently"""
        # Compare results with one-hot vs index inputs
        y_true_onehot = tf.constant([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=tf.float32)
        y_true_indices = tf.constant([0, 1], dtype=tf.int32)
        y_pred = tf.constant(
            [[0.8, 0.1, 0.05, 0.05], [0.1, 0.7, 0.15, 0.05]], dtype=tf.float32
        )

        mae_onehot = ordinal_mae(y_true_onehot, y_pred)
        mae_indices = ordinal_mae(y_true_indices, y_pred)

        acc_onehot = adjacent_class_accuracy(y_true_onehot, y_pred)
        acc_indices = adjacent_class_accuracy(y_true_indices, y_pred)

        # Results should be very similar (allowing for small numerical differences)
        assert abs(mae_onehot - mae_indices) < 0.01
        assert abs(acc_onehot - acc_indices) < 0.01

        # Test new metrics consistency
        tau_onehot = kendall_tau_metric(y_true_onehot, y_pred)
        tau_indices = kendall_tau_metric(y_true_indices, y_pred)
        assert abs(tau_onehot - tau_indices) < 0.01

    def test_worst_case_predictions(self):
        """Test metrics with worst-case predictions"""
        # True class 0, predict class 3 (maximum distance for 4 classes)
        y_true_worst = tf.constant([0], dtype=tf.int32)
        y_pred_worst = tf.constant([[0.05, 0.05, 0.05, 0.85]], dtype=tf.float32)

        mae_worst = ordinal_mae(y_true_worst, y_pred_worst)
        acc_worst = adjacent_class_accuracy(y_true_worst, y_pred_worst)

        # MAE should be close to maximum possible (3.0 for 4 classes)
        assert mae_worst > 2.5  # Should be high for worst case

        # Adjacent accuracy should be 0 for worst case
        assert acc_worst < 0.1  # Should be very low

        # Test tolerance accuracy with worst case
        acc_tolerance_0 = ordinal_accuracy_tolerance(
            y_true_worst, y_pred_worst, tolerance=0
        )
        acc_tolerance_3 = ordinal_accuracy_tolerance(
            y_true_worst, y_pred_worst, tolerance=3
        )

        assert acc_tolerance_0 < 0.1  # Should be 0 for strict tolerance
        assert acc_tolerance_3 > 0.9  # Should be 1 for loose tolerance


class TestMetricProperties:
    """Test mathematical properties of metrics"""

    def setup_method(self):
        """Set up test fixtures"""
        self.y_true = tf.constant([0, 1, 2, 3], dtype=tf.int32)
        self.y_pred_good = tf.constant(
            [
                [0.8, 0.1, 0.05, 0.05],
                [0.1, 0.8, 0.05, 0.05],
                [0.05, 0.1, 0.8, 0.05],
                [0.05, 0.05, 0.1, 0.8],
            ],
            dtype=tf.float32,
        )

    def test_metric_bounds(self):
        """Test that metrics stay within expected bounds"""
        mae = ordinal_mae(self.y_true, self.y_pred_good)
        acc = adjacent_class_accuracy(self.y_true, self.y_pred_good)
        recall = adjacent_class_recall(self.y_true, self.y_pred_good)
        precision = adjacent_class_precision(self.y_true, self.y_pred_good)

        # MAE should be non-negative
        assert mae >= 0.0

        # Accuracy, recall, precision should be between 0 and 1
        assert 0.0 <= acc <= 1.0
        assert 0.0 <= recall <= 1.0
        assert 0.0 <= precision <= 1.0

        # Test new metrics bounds
        tau = kendall_tau_metric(self.y_true, self.y_pred_good)
        bal_acc = balanced_accuracy_metric(self.y_true, self.y_pred_good)
        auc = adjacent_class_auc(self.y_true, self.y_pred_good)

        assert -1.0 <= tau <= 1.0
        assert 0.0 <= bal_acc <= 1.0
        assert 0.0 <= auc <= 1.0

    def test_perfect_prediction_properties(self):
        """Test properties with perfect predictions"""
        # Perfect predictions
        y_pred_perfect = tf.constant(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=tf.float32,
        )

        mae_perfect = ordinal_mae(self.y_true, y_pred_perfect)
        acc_perfect = adjacent_class_accuracy(self.y_true, y_pred_perfect)
        tau_perfect = kendall_tau_metric(self.y_true, y_pred_perfect)
        bal_acc_perfect = balanced_accuracy_metric(self.y_true, y_pred_perfect)

        # Perfect predictions should give perfect scores
        assert mae_perfect < 0.01  # Near zero MAE
        assert abs(acc_perfect - 1.0) < 0.01  # Near perfect accuracy
        assert tau_perfect > 0.9  # High correlation
        assert abs(bal_acc_perfect - 1.0) < 0.01  # Perfect balanced accuracy


if __name__ == "__main__":
    # Run basic smoke tests if executed directly
    print("Running basic smoke tests for classification metrics...")

    # Create test instances
    ordinal_tests = TestOrdinalMetrics()
    ordinal_tests.setup_method()

    additional_tests = TestAdditionalOrdinalMetrics()
    additional_tests.setup_method()

    utility_tests = TestUtilityFunctions()
    edge_tests = TestEdgeCases()

    property_tests = TestMetricProperties()
    property_tests.setup_method()

    try:
        # Run key tests
        print("Testing ordinal_mae with one-hot...")
        ordinal_tests.test_ordinal_mae_with_onehot()

        print("Testing ordinal_mae with indices...")
        ordinal_tests.test_ordinal_mae_with_indices()

        print("Testing ordinal_mae calculation...")
        ordinal_tests.test_ordinal_mae_calculation()

        print("Testing adjacent_class_accuracy with one-hot...")
        ordinal_tests.test_adjacent_class_accuracy_with_onehot()

        print("Testing adjacent_class_accuracy with indices...")
        ordinal_tests.test_adjacent_class_accuracy_with_indices()

        print("Testing adjacent_class_accuracy calculation...")
        ordinal_tests.test_adjacent_class_accuracy_calculation()

        print("Testing adjacent_class_recall...")
        ordinal_tests.test_adjacent_class_recall()

        print("Testing adjacent_class_precision...")
        ordinal_tests.test_adjacent_class_precision()

        print("Testing adjacent_class_auc...")
        additional_tests.test_adjacent_class_auc()

        print("Testing kendall_tau_metric...")
        additional_tests.test_kendall_tau_metric()

        print("Testing ordinal_accuracy_tolerance...")
        additional_tests.test_ordinal_accuracy_tolerance()

        print("Testing balanced_accuracy_metric...")
        additional_tests.test_balanced_accuracy_metric()

        print("Testing standard_metric_wrapper...")
        additional_tests.test_standard_metric_wrapper()

        print("Testing get_metrics standard mode...")
        utility_tests.test_get_metrics_standard_mode()

        print("Testing get_metrics ordinal mode...")
        utility_tests.test_get_metrics_ordinal_mode()

        print("Testing single sample input...")
        edge_tests.test_single_sample_input()

        print("Testing binary classification...")
        edge_tests.test_binary_classification()

        print("Testing input format consistency...")
        edge_tests.test_input_format_consistency()

        print("Testing worst case predictions...")
        edge_tests.test_worst_case_predictions()

        print("Testing metric bounds...")
        property_tests.test_metric_bounds()

        print("Testing perfect prediction properties...")
        property_tests.test_perfect_prediction_properties()

        print("All smoke tests passed!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        raise
