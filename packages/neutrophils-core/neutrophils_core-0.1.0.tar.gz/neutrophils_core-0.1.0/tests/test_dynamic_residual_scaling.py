#!/usr/bin/env python3
"""
Pytest tests for DynamicResidualScaling layer

Tests the functionality, edge cases, and correctness of the dynamic residual
scaling strategies for bias correction in neural networks.
"""

import pytest
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Lambda
from tensorflow.keras.models import Model

from neutrophils_core.models.dynamic_residual_scaling import (
    DynamicResidualScaling,
    create_adaptive_lambda_scaling,
    create_magnitude_ratio_lambda_scaling
)


class TestDynamicResidualScaling:
    """Test class for DynamicResidualScaling layer"""
    
    @pytest.fixture
    def sample_inputs(self):
        """Create sample input tensors for testing"""
        batch_size = 4
        height, width, channels = 8, 8, 16
        
        # Create inputs with different magnitudes to test scaling
        main_path = tf.random.normal((batch_size, height, width, channels), mean=0.0, stddev=2.0)
        residual_path = tf.random.normal((batch_size, height, width, channels), mean=0.0, stddev=0.5)
        
        return main_path, residual_path
    
    @pytest.fixture
    def input_shapes(self):
        """Input shapes for building layers"""
        shape = (None, 8, 8, 16)
        return [shape, shape]
    
    def test_layer_creation_with_valid_strategies(self):
        """Test that layer can be created with all valid strategies"""
        valid_strategies = ['adaptive_norm', 'learned_balance', 'magnitude_ratio', 'spectral_norm']
        
        for strategy in valid_strategies:
            layer = DynamicResidualScaling(strategy=strategy)
            assert layer.strategy == strategy
            assert layer.alpha == 0.5  # default value
    
    def test_layer_creation_with_invalid_strategy(self):
        """Test that invalid strategy raises ValueError"""
        with pytest.raises(ValueError, match="Strategy must be one of"):
            DynamicResidualScaling(strategy='invalid_strategy')
    
    def test_parameter_validation(self):
        """Test parameter validation during initialization"""
        # Test invalid alpha
        with pytest.raises(ValueError, match="alpha must be between 0.0 and 1.0"):
            DynamicResidualScaling(alpha=-0.1)
        
        with pytest.raises(ValueError, match="alpha must be between 0.0 and 1.0"):
            DynamicResidualScaling(alpha=1.5)
        
        # Test invalid momentum
        with pytest.raises(ValueError, match="momentum must be between 0.0 and 1.0"):
            DynamicResidualScaling(momentum=-0.1)
        
        with pytest.raises(ValueError, match="momentum must be between 0.0 and 1.0"):
            DynamicResidualScaling(momentum=1.5)
        
        # Test invalid scale bounds
        with pytest.raises(ValueError, match="min_scale .* must be less than max_scale"):
            DynamicResidualScaling(min_scale=2.0, max_scale=1.0)
    
    def test_build_with_wrong_input_count(self):
        """Test that build fails with wrong number of inputs"""
        layer = DynamicResidualScaling()
        
        with pytest.raises(ValueError, match="expects exactly 2 inputs"):
            layer.build([(None, 8, 8, 16)])  # Only one input shape
        
        with pytest.raises(ValueError, match="expects exactly 2 inputs"):
            layer.build([(None, 8, 8, 16), (None, 8, 8, 16), (None, 8, 8, 16)])  # Three inputs
    
    def test_build_with_mismatched_shapes(self):
        """Test that build fails with mismatched input shapes"""
        layer = DynamicResidualScaling()
        
        with pytest.raises(ValueError, match="Input shapes must match"):
            layer.build([(None, 8, 8, 16), (None, 8, 8, 32)])  # Different channel counts
    
    def test_call_with_wrong_input_count(self, sample_inputs):
        """Test that call fails with wrong number of inputs"""
        layer = DynamicResidualScaling()
        layer.build([(None, 8, 8, 16), (None, 8, 8, 16)])
        
        main_path, _ = sample_inputs
        
        with pytest.raises(ValueError, match="expects exactly 2 inputs"):
            layer([main_path])  # Only one input
    
    def test_adaptive_norm_strategy(self, sample_inputs, input_shapes):
        """Test adaptive_norm strategy functionality"""
        layer = DynamicResidualScaling(strategy='adaptive_norm', alpha=0.5)
        layer.build(input_shapes)
        
        main_path, residual_path = sample_inputs
        
        # Test training mode
        output_train = layer([main_path, residual_path], training=True)
        assert output_train.shape == main_path.shape
        assert not tf.reduce_any(tf.math.is_nan(output_train))
        
        # Test inference mode
        output_inference = layer([main_path, residual_path], training=False)
        assert output_inference.shape == main_path.shape
        assert not tf.reduce_any(tf.math.is_nan(output_inference))
        
        # Check that running statistics are updated during training
        initial_main_norm = layer.running_main_norm.numpy()
        initial_residual_norm = layer.running_residual_norm.numpy()
        
        # Run another training step
        _ = layer([main_path, residual_path], training=True)
        
        # Statistics should have changed
        assert layer.running_main_norm.numpy() != initial_main_norm
        assert layer.running_residual_norm.numpy() != initial_residual_norm
    
    def test_learned_balance_strategy(self, sample_inputs, input_shapes):
        """Test learned_balance strategy functionality"""
        layer = DynamicResidualScaling(strategy='learned_balance')
        layer.build(input_shapes)
        
        main_path, residual_path = sample_inputs
        
        # Check that learnable weights are created
        assert hasattr(layer, 'main_weight')
        assert hasattr(layer, 'residual_weight')
        assert layer.main_weight.trainable
        assert layer.residual_weight.trainable
        
        # Test forward pass
        output = layer([main_path, residual_path])
        assert output.shape == main_path.shape
        assert not tf.reduce_any(tf.math.is_nan(output))
    
    def test_magnitude_ratio_strategy(self, sample_inputs, input_shapes):
        """Test magnitude_ratio strategy functionality"""
        layer = DynamicResidualScaling(strategy='magnitude_ratio', alpha=0.7)
        layer.build(input_shapes)
        
        main_path, residual_path = sample_inputs
        
        output = layer([main_path, residual_path], training=True)
        assert output.shape == main_path.shape
        assert not tf.reduce_any(tf.math.is_nan(output))
        
        # Test that running statistics are created and updated
        assert hasattr(layer, 'running_main_norm')
        assert hasattr(layer, 'running_residual_norm')
    
    def test_spectral_norm_strategy(self, sample_inputs, input_shapes):
        """Test spectral_norm strategy functionality"""
        layer = DynamicResidualScaling(strategy='spectral_norm')
        layer.build(input_shapes)
        
        main_path, residual_path = sample_inputs
        
        output = layer([main_path, residual_path])
        assert output.shape == main_path.shape
        assert not tf.reduce_any(tf.math.is_nan(output))
    
    def test_scaling_factor_clipping(self, input_shapes):
        """Test that scaling factors are properly clipped"""
        layer = DynamicResidualScaling(
            strategy='adaptive_norm', 
            min_scale=0.5, 
            max_scale=1.5,
            alpha=1.0  # Full scaling to test clipping
        )
        layer.build(input_shapes)
        
        # Create inputs with very different magnitudes to force clipping
        batch_size = 2
        main_path = tf.ones((batch_size, 8, 8, 16)) * 10.0  # Large magnitude
        residual_path = tf.ones((batch_size, 8, 8, 16)) * 0.01  # Small magnitude
        
        output = layer([main_path, residual_path], training=True)
        assert output.shape == main_path.shape
        assert not tf.reduce_any(tf.math.is_nan(output))
        
        # Output should be finite due to clipping
        assert tf.reduce_all(tf.math.is_finite(output))
    
    def test_get_config(self):
        """Test layer configuration serialization"""
        layer = DynamicResidualScaling(
            strategy='magnitude_ratio',
            alpha=0.3,
            momentum=0.95,
            epsilon=1e-5,
            min_scale=0.2,
            max_scale=1.8
        )
        
        config = layer.get_config()
        
        assert config['strategy'] == 'magnitude_ratio'
        assert config['alpha'] == 0.3
        assert config['momentum'] == 0.95
        assert config['epsilon'] == 1e-5
        assert config['min_scale'] == 0.2
        assert config['max_scale'] == 1.8
    
    def test_compute_output_shape(self):
        """Test output shape computation"""
        layer = DynamicResidualScaling()
        
        input_shapes = [(None, 8, 8, 16), (None, 8, 8, 16)]
        output_shape = layer.compute_output_shape(input_shapes)
        
        assert output_shape == (None, 8, 8, 16)
        
        # Test with mismatched shapes
        with pytest.raises(ValueError, match="Input shapes must match"):
            layer.compute_output_shape([(None, 8, 8, 16), (None, 8, 8, 32)])
    
    def test_in_functional_model(self, sample_inputs):
        """Test that layer works correctly in a functional model"""
        input_shape = (8, 8, 16)
        
        # Create functional model
        main_input = Input(shape=input_shape, name='main_input')
        residual_input = Input(shape=input_shape, name='residual_input')
        
        output = DynamicResidualScaling(strategy='adaptive_norm')([main_input, residual_input])
        
        model = Model(inputs=[main_input, residual_input], outputs=output)
        
        # Test model compilation and prediction
        model.compile(optimizer='adam', loss='mse')
        
        main_path, residual_path = sample_inputs
        prediction = model.predict([main_path, residual_path], verbose=0)
        
        assert prediction.shape == main_path.shape
        assert not np.any(np.isnan(prediction))


class TestLambdaScalingFunctions:
    """Test class for lambda-based scaling functions"""
    
    @pytest.fixture
    def sample_tensors(self):
        """Create sample tensors for testing"""
        batch_size = 3
        height, width, channels = 4, 4, 8
        
        main_path = tf.random.normal((batch_size, height, width, channels), mean=0.0, stddev=1.5)
        residual_path = tf.random.normal((batch_size, height, width, channels), mean=0.0, stddev=0.3)
        
        return main_path, residual_path
    
    def test_adaptive_lambda_scaling(self, sample_tensors):
        """Test adaptive lambda scaling function"""
        scaling_func = create_adaptive_lambda_scaling(alpha=0.6)
        
        main_path, residual_path = sample_tensors
        output = scaling_func([main_path, residual_path])
        
        assert output.shape == main_path.shape
        assert not tf.reduce_any(tf.math.is_nan(output))
        assert tf.reduce_all(tf.math.is_finite(output))
    
    def test_magnitude_ratio_lambda_scaling(self, sample_tensors):
        """Test magnitude ratio lambda scaling function"""
        scaling_func = create_magnitude_ratio_lambda_scaling(alpha=0.4)
        
        main_path, residual_path = sample_tensors
        output = scaling_func([main_path, residual_path])
        
        assert output.shape == main_path.shape
        assert not tf.reduce_any(tf.math.is_nan(output))
        assert tf.reduce_all(tf.math.is_finite(output))
    
    def test_lambda_scaling_with_extreme_inputs(self):
        """Test lambda scaling with extreme input magnitudes"""
        # Create inputs with very different scales
        main_path = tf.ones((2, 4, 4, 8)) * 100.0
        residual_path = tf.ones((2, 4, 4, 8)) * 0.001
        
        # Test adaptive scaling
        adaptive_func = create_adaptive_lambda_scaling(alpha=0.8, min_scale=0.01, max_scale=10.0)
        output_adaptive = adaptive_func([main_path, residual_path])
        
        assert tf.reduce_all(tf.math.is_finite(output_adaptive))
        assert not tf.reduce_any(tf.math.is_nan(output_adaptive))
        
        # Test magnitude ratio scaling
        ratio_func = create_magnitude_ratio_lambda_scaling(alpha=0.5, min_scale=0.01, max_scale=10.0)
        output_ratio = ratio_func([main_path, residual_path])
        
        assert tf.reduce_all(tf.math.is_finite(output_ratio))
        assert not tf.reduce_any(tf.math.is_nan(output_ratio))
    
    def test_lambda_scaling_in_model(self, sample_tensors):
        """Test lambda scaling functions work in Keras models"""
        input_shape = (4, 4, 8)
        
        # Create model with adaptive lambda scaling
        main_input = Input(shape=input_shape)
        residual_input = Input(shape=input_shape)
        
        scaling_func = create_adaptive_lambda_scaling(alpha=0.5)
        output = Lambda(scaling_func)([main_input, residual_input])
        
        model = Model(inputs=[main_input, residual_input], outputs=output)
        model.compile(optimizer='adam', loss='mse')
        
        main_path, residual_path = sample_tensors
        prediction = model.predict([main_path, residual_path], verbose=0)
        
        assert prediction.shape == main_path.shape
        assert not np.any(np.isnan(prediction))


class TestBiasCorrection:
    """Test that dynamic scaling actually corrects bias"""
    
    def test_magnitude_balancing(self):
        """Test that scaling balances path magnitudes"""
        # Create paths with very different magnitudes
        batch_size = 4
        main_path = tf.ones((batch_size, 8, 8, 16)) * 5.0  # Large magnitude
        residual_path = tf.ones((batch_size, 8, 8, 16)) * 0.2  # Small magnitude
        
        # Test adaptive norm strategy
        layer = DynamicResidualScaling(strategy='adaptive_norm', alpha=1.0)
        layer.build([(None, 8, 8, 16), (None, 8, 8, 16)])
        
        output = layer([main_path, residual_path], training=True)
        
        # Check that the output is not dominated by either path
        main_contribution = tf.reduce_mean(tf.abs(main_path))
        residual_contribution = tf.reduce_mean(tf.abs(residual_path))
        output_magnitude = tf.reduce_mean(tf.abs(output))
        
        # Output should be between the two path magnitudes due to balancing
        assert output_magnitude > residual_contribution
        assert output_magnitude < main_contribution


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])