"""
Comprehensive tests for loss functions in neutrophils_core.metrics.loss_functions

This test suite validates all migrated loss functions from the classifier module
to ensure they work correctly in the neutrophils-core package structure.
"""

import pytest
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K

# Import loss_functions module directly to avoid package import issues
import sys
import os
import importlib.util

# Get the path to the loss_functions module
loss_functions_path = os.path.join(
    os.path.dirname(__file__), "..", "neutrophils_core", "metrics", "loss_functions.py"
)
spec = importlib.util.spec_from_file_location("loss_functions", loss_functions_path)
lf = importlib.util.module_from_spec(spec)
sys.modules["loss_functions"] = lf
spec.loader.exec_module(lf)

# Create aliases for cleaner test code
categorical_crossentropy = lf.categorical_crossentropy
sparse_categorical_crossentropy = lf.sparse_categorical_crossentropy
categorical_focal_loss = lf.categorical_focal_loss
categorical_dice_loss = lf.categorical_dice_loss
ordinal_crossentropy = lf.ordinal_crossentropy
ordinal_focal_loss = lf.ordinal_focal_loss
ordinal_dice_loss = lf.ordinal_dice_loss
soft_ordinal_loss = lf.soft_ordinal_loss
cumulative_ordinal_loss = lf.cumulative_ordinal_loss
get_loss_function = lf.get_loss_function
LOSS_FUNCTIONS = lf.LOSS_FUNCTIONS

class TestStandardCategoricalLossFunctions:
    """Test standard categorical loss functions"""

    def setup_method(self):
        """Set up test fixtures"""
        # Create sample data for 4-class classification
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

        self.class_weights = np.array([1.0, 2.0, 1.5, 1.2])  # Example class weights

    def test_categorical_crossentropy(self):
        """Test categorical crossentropy function"""
        loss = categorical_crossentropy(self.y_true_onehot, self.y_pred)

        # Loss should be finite and non-negative
        assert tf.reduce_all(tf.math.is_finite(loss))
        assert tf.reduce_all(loss >= 0.0)
        assert isinstance(loss, tf.Tensor)

        # Test with class weights
        weighted_loss = categorical_crossentropy(
            self.y_true_onehot, self.y_pred, class_weights=self.class_weights
        )
        assert tf.reduce_all(tf.math.is_finite(weighted_loss))
        assert tf.reduce_all(weighted_loss >= 0.0)
        assert isinstance(weighted_loss, tf.Tensor)

    def test_sparse_categorical_crossentropy(self):
        """Test sparse categorical crossentropy function"""
        loss = sparse_categorical_crossentropy(self.y_true_indices, self.y_pred)

        # Loss should be finite and non-negative
        assert tf.reduce_all(tf.math.is_finite(loss))
        assert tf.reduce_all(loss >= 0.0)
        assert isinstance(loss, tf.Tensor)

        # Test with class weights
        weighted_loss = sparse_categorical_crossentropy(
            self.y_true_indices, self.y_pred, class_weights=self.class_weights
        )
        assert tf.reduce_all(tf.math.is_finite(weighted_loss))
        assert tf.reduce_all(weighted_loss >= 0.0)
        assert isinstance(weighted_loss, tf.Tensor)

    def test_categorical_focal_loss(self):
        """Test categorical focal loss function"""
        loss = categorical_focal_loss(self.y_true_onehot, self.y_pred)

        # Loss should be finite and non-negative
        assert tf.reduce_all(tf.math.is_finite(loss))
        assert tf.reduce_all(loss >= 0.0)
        assert isinstance(loss, tf.Tensor)

        # Test with different gamma values
        loss_gamma1 = categorical_focal_loss(self.y_true_onehot, self.y_pred, gamma=1.0)
        loss_gamma3 = categorical_focal_loss(self.y_true_onehot, self.y_pred, gamma=3.0)

        assert isinstance(loss_gamma1, tf.Tensor)
        assert isinstance(loss_gamma3, tf.Tensor)

        # Test with alpha and class weights
        alpha = 0.25
        loss_weighted = categorical_focal_loss(
            self.y_true_onehot, self.y_pred, alpha=alpha, class_weights=self.class_weights
        )
        assert tf.reduce_all(tf.math.is_finite(loss_weighted))
        assert tf.reduce_all(loss_weighted >= 0.0)
        assert isinstance(loss_weighted, tf.Tensor)

    def test_categorical_dice_loss(self):
        """Test categorical dice loss function"""
        loss = categorical_dice_loss(self.y_true_onehot, self.y_pred)

        # Categorical dice loss should be between 0 and 1
        assert tf.reduce_all(loss >= 0.0) and tf.reduce_all(loss <= 1.0)
        assert isinstance(loss, tf.Tensor)

        # Test with class weights
        weighted_loss = categorical_dice_loss(
            self.y_true_onehot, self.y_pred, class_weights=self.class_weights
        )
        assert tf.reduce_all(weighted_loss >= 0.0) and tf.reduce_all(
            weighted_loss <= 1.0
        )
        assert isinstance(weighted_loss, tf.Tensor)

        # Test with perfect predictions
        perfect_pred = self.y_true_onehot
        perfect_loss = categorical_dice_loss(self.y_true_onehot, perfect_pred)
        assert tf.reduce_all(
            perfect_loss < 0.01
        )  # Should be very small for perfect prediction


class TestOrdinalLossFunctions:
    """Test ordinal-specific loss functions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.num_classes = 4
        self.batch_size = 8

        # Class indices for ordinal functions
        self.y_true_indices = tf.constant([0, 1, 2, 3, 0, 1, 2, 3], dtype=tf.int32)

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

        self.class_weights = np.array([1.0, 2.0, 1.5, 1.2])
        self.penalty = 0.5 

    def test_ordinal_crossentropy(self):
        """Test ordinal crossentropy loss function"""
        loss = ordinal_crossentropy(self.y_true_indices, self.y_pred)

        # Loss should be finite (not NaN or inf) and non-negative
        assert tf.reduce_all(
            tf.math.is_finite(loss)
        ), f"Loss contains non-finite values: {loss.numpy()}"
        assert tf.reduce_all(
            loss >= 0.0
        ), f"Loss contains negative values: {loss.numpy()}"
        assert isinstance(loss, tf.Tensor)

        # Test with class weights and penalty
        weighted_loss = ordinal_crossentropy(
            self.y_true_indices, self.y_pred, class_weights=self.class_weights, penalty=self.penalty
        )
        assert tf.reduce_all(
            tf.math.is_finite(weighted_loss)
        ), f"Weighted loss contains non-finite values: {weighted_loss.numpy()}"
        assert tf.reduce_all(
            weighted_loss >= 0.0
        ), f"Weighted loss contains negative values: {weighted_loss.numpy()}"
        assert isinstance(weighted_loss, tf.Tensor)

    def test_ordinal_focal_loss(self):
        """Test ordinal focal loss function"""
        loss = ordinal_focal_loss(self.y_true_indices, self.y_pred)

        assert tf.reduce_all(loss > 0.0)  # Loss should be positive
        assert isinstance(loss, tf.Tensor)

        # Test with different gamma values
        loss_gamma1 = ordinal_focal_loss(self.y_true_indices, self.y_pred, gamma=1.0)
        loss_gamma3 = ordinal_focal_loss(self.y_true_indices, self.y_pred, gamma=3.0)

        assert isinstance(loss_gamma1, tf.Tensor)
        assert isinstance(loss_gamma3, tf.Tensor)

        # Test with alpha, class weights, and penalty
        alpha = 0.25
        loss_weighted = ordinal_focal_loss(
            self.y_true_indices, self.y_pred, alpha=alpha, class_weights=self.class_weights, penalty=self.penalty
        )
        assert tf.reduce_all(loss_weighted > 0.0)
        assert isinstance(loss_weighted, tf.Tensor)

    def test_ordinal_dice_loss(self):
        """Test ordinal dice loss function"""
        loss = ordinal_dice_loss(self.y_true_indices, self.y_pred)

        assert tf.reduce_all(loss >= 0.0)  # Loss should be non-negative
        assert isinstance(loss, tf.Tensor)

        # Test with class weights and penalty
        weighted_loss = ordinal_dice_loss(
            self.y_true_indices, self.y_pred, class_weights=self.class_weights, penalty=self.penalty
        )
        assert tf.reduce_all(weighted_loss >= 0.0)
        assert isinstance(weighted_loss, tf.Tensor)

    def test_soft_ordinal_loss(self):
        """Test soft ordinal loss function"""
        loss = soft_ordinal_loss(self.y_true_indices, self.y_pred)

        assert tf.reduce_all(loss >= 0.0)  # Loss should be non-negative
        assert isinstance(loss, tf.Tensor)

        # Test with different sigma values
        loss_tight = soft_ordinal_loss(self.y_true_indices, self.y_pred, sigma=0.5)
        loss_loose = soft_ordinal_loss(self.y_true_indices, self.y_pred, sigma=2.0)

        assert isinstance(loss_tight, tf.Tensor)
        assert isinstance(loss_loose, tf.Tensor)

        # Test with class weights and penalty
        weighted_loss = soft_ordinal_loss(
            self.y_true_indices, self.y_pred, class_weights=self.class_weights, penalty=self.penalty
        )
        assert tf.reduce_all(weighted_loss >= 0.0)
        assert isinstance(weighted_loss, tf.Tensor)

    def test_cumulative_ordinal_loss(self):
        """Test cumulative ordinal loss function"""
        # For cumulative loss, we need cumulative probabilities
        y_pred_cumulative = tf.constant(
            [
                [0.8, 0.9, 0.95, 1.0],  # Class 0
                [0.2, 0.8, 0.95, 1.0],  # Class 1
                [0.1, 0.3, 0.8, 1.0],  # Class 2
                [0.05, 0.15, 0.35, 1.0],  # Class 3
                [0.75, 0.85, 0.9, 1.0],  # Class 0
                [0.25, 0.75, 0.9, 1.0],  # Class 1
                [0.15, 0.35, 0.75, 1.0],  # Class 2
                [0.1, 0.2, 0.4, 1.0],  # Class 3
            ],
            dtype=tf.float32,
        )

        loss = cumulative_ordinal_loss(self.y_true_indices, y_pred_cumulative)

        assert tf.reduce_all(loss >= 0.0)  # Loss should be non-negative
        assert isinstance(loss, tf.Tensor)

        # Test with class weights and penalty
        weighted_loss = cumulative_ordinal_loss(
            self.y_true_indices, y_pred_cumulative, class_weights=self.class_weights, penalty=self.penalty
        )
        assert tf.reduce_all(weighted_loss >= 0.0)
        assert isinstance(weighted_loss, tf.Tensor)


class TestUtilityFunctions:
    """Test utility functions and configurations"""

    def test_get_loss_function(self):
        """Test get_loss_function utility"""
        # Test getting standard loss functions
        categorical_dice_fn = get_loss_function("categorical_dice_loss")
        assert categorical_dice_fn == categorical_dice_loss

        categorical_crossentropy_fn = get_loss_function("categorical_crossentropy")
        assert categorical_crossentropy_fn == categorical_crossentropy

        sparse_categorical_crossentropy_fn = get_loss_function("sparse_categorical_crossentropy")
        assert sparse_categorical_crossentropy_fn == sparse_categorical_crossentropy

        categorical_focal_fn = get_loss_function("categorical_focal_loss")
        assert categorical_focal_fn == categorical_focal_loss

        ordinal_fn = get_loss_function("ordinal_crossentropy")
        assert ordinal_fn == ordinal_crossentropy

        # Test with additional parameters (should return partial function)
        ordinal_penalty_fn = get_loss_function(
            "ordinal_crossentropy", penalty=2.0
        )
        assert callable(ordinal_penalty_fn)
        # Test that it's not the same as the original function
        assert ordinal_penalty_fn != ordinal_crossentropy

        # Test unknown loss function (should raise error)
        try:
            unknown_fn = get_loss_function("unknown_loss")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected behavior

    def test_loss_functions_dictionary(self):
        """Test LOSS_FUNCTIONS dictionary"""
        # Test that all expected loss functions are in the dictionary
        expected_losses = [
            "categorical_crossentropy",
            "sparse_categorical_crossentropy",
            "categorical_focal_loss",
            "categorical_dice_loss",
            "ordinal_crossentropy",
            "ordinal_focal_loss",
            "ordinal_dice_loss",
            "soft_ordinal_loss",
            "cumulative_ordinal_loss",
        ]

        for loss_name in expected_losses:
            assert loss_name in LOSS_FUNCTIONS

        # Test that functions in dictionary are callable
        for loss_name, loss_fn in LOSS_FUNCTIONS.items():
            # All entries should be callable functions
            assert callable(loss_fn), f"Loss function {loss_name} should be callable"


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_input_format_handling(self):
        """Test that functions handle different input formats correctly"""
        # Test with one-hot encoded labels
        y_true_onehot = tf.constant([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=tf.float32)
        y_pred = tf.constant(
            [[0.8, 0.1, 0.05, 0.05], [0.1, 0.7, 0.15, 0.05]], dtype=tf.float32
        )

        # Test with class indices
        y_true_indices = tf.constant([0, 1], dtype=tf.int32)

        # Test with indices (normal usage)
        loss1 = ordinal_crossentropy(y_true_indices, y_pred)
        assert isinstance(loss1, tf.Tensor)

        # For one-hot encoded inputs, we need to convert back to indices first
        y_true_indices_from_onehot = tf.argmax(y_true_onehot, axis=-1)
        loss2 = ordinal_crossentropy(y_true_indices_from_onehot, y_pred)

        assert isinstance(loss2, tf.Tensor)
        # Results should be similar (allowing for small numerical differences)
        assert tf.reduce_all(tf.abs(loss1 - loss2) < 0.1)

    def test_class_weights_shape(self):
        """Test that class weights work with correct shapes"""
        y_true = tf.constant([0, 1, 2, 3], dtype=tf.int32)
        y_pred = tf.constant(
            [
                [0.8, 0.1, 0.05, 0.05],
                [0.1, 0.7, 0.15, 0.05],
                [0.05, 0.15, 0.6, 0.2],
                [0.1, 0.1, 0.2, 0.6],
            ],
            dtype=tf.float32,
        )

        # Test with correct class weights shape
        class_weights = np.array([1.0, 2.0, 1.5, 1.2])  # 4 classes

        loss = ordinal_crossentropy(y_true, y_pred, class_weights=class_weights)
        assert isinstance(loss, tf.Tensor)
        assert tf.reduce_all(loss > 0.0)


if __name__ == "__main__":
    # Run basic smoke tests if executed directly
    print("Running basic smoke tests for loss functions...")

    # Create test instances
    standard_tests = TestStandardCategoricalLossFunctions()
    standard_tests.setup_method()

    ordinal_tests = TestOrdinalLossFunctions()
    ordinal_tests.setup_method()

    utility_tests = TestUtilityFunctions()
    edge_tests = TestEdgeCases()

    try:
        # Run a few key tests
        print("Testing categorical_crossentropy...")
        standard_tests.test_categorical_crossentropy()

        print("Testing sparse_categorical_crossentropy...")
        standard_tests.test_sparse_categorical_crossentropy()

        print("Testing categorical_focal_loss...")
        standard_tests.test_categorical_focal_loss()

        print("Testing categorical_dice_loss...")
        standard_tests.test_categorical_dice_loss()

        print("Testing ordinal_crossentropy...")
        ordinal_tests.test_ordinal_crossentropy()

        print("Testing ordinal_focal_loss...")
        ordinal_tests.test_ordinal_focal_loss()

        print("Testing ordinal_dice_loss...")
        ordinal_tests.test_ordinal_dice_loss()

        print("Testing soft_ordinal_loss...")
        ordinal_tests.test_soft_ordinal_loss()

        print("Testing cumulative_ordinal_loss...")
        ordinal_tests.test_cumulative_ordinal_loss()

        print("Testing get_loss_function...")
        utility_tests.test_get_loss_function()

        print("Testing LOSS_FUNCTIONS dictionary...")
        utility_tests.test_loss_functions_dictionary()

        print("Testing input format handling...")
        edge_tests.test_input_format_handling()

        print("All smoke tests passed!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        raise
