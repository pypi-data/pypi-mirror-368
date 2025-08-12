#!/usr/bin/env python3
"""
Dynamic Residual Scaling Layers for Bias Correction

This module implements sophisticated residual scaling strategies that dynamically
balance the residual and main paths based on their activation magnitudes,
ensuring they contribute in similar ranges to prevent bias.

Based on bias analysis findings that show standard residual connections (scaling=1.0)
introduce severe class imbalance and overconfident predictions.
"""

import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import Layer, Lambda
from tensorflow.keras import backend as K


@tf.keras.utils.register_keras_serializable()
class DynamicResidualScaling(Layer):
    """
    Dynamic residual scaling layer that balances residual and main paths
    based on their activation magnitudes to prevent bias.
    
    This layer addresses the bias issues identified in residual networks where
    the Add() operation can lead to:
    - Severe class imbalance (some classes get 100% accuracy, others 0%)
    - Overconfident predictions (artificially low entropy)
    - 96% gradient suppression leading to optimization issues
    
    Strategies available:
    - 'adaptive_norm': Balance paths by normalizing their L2 norms
    - 'learned_balance': Let the network learn optimal weights for each path
    - 'magnitude_ratio': Scale based on the ratio of path magnitudes
    - 'spectral_norm': Balance based on spectral norms of the paths
    """
    
    def __init__(self, 
                 strategy='adaptive_norm', 
                 alpha=0.5, 
                 momentum=0.99, 
                 epsilon=1e-6,
                 min_scale=0.1,
                 max_scale=2.0,
                 **kwargs):
        """
        Initialize dynamic residual scaling layer.
        
        Args:
            strategy (str): Scaling strategy to use
                - 'adaptive_norm': Balance paths by normalizing their L2 norms
                - 'learned_balance': Learn optimal weights for each path
                - 'magnitude_ratio': Scale based on ratio of path magnitudes
                - 'spectral_norm': Balance based on spectral norms
            alpha (float): Balance parameter (0.5 = equal weighting)
            momentum (float): Momentum for running statistics
            epsilon (float): Small constant for numerical stability
            min_scale (float): Minimum allowed scaling factor
            max_scale (float): Maximum allowed scaling factor
        """
        super(DynamicResidualScaling, self).__init__(**kwargs)
        
        # Validate strategy
        valid_strategies = ['adaptive_norm', 'learned_balance', 'magnitude_ratio', 'spectral_norm']
        if strategy not in valid_strategies:
            raise ValueError(f"Strategy must be one of {valid_strategies}, got {strategy}")
        
        self.strategy = strategy
        self.alpha = float(alpha)
        self.momentum = float(momentum)
        self.epsilon = float(epsilon)
        self.min_scale = float(min_scale)
        self.max_scale = float(max_scale)
        
        # Validate parameters
        if not 0.0 <= self.alpha <= 1.0:
            raise ValueError(f"alpha must be between 0.0 and 1.0, got {alpha}")
        if not 0.0 <= self.momentum <= 1.0:
            raise ValueError(f"momentum must be between 0.0 and 1.0, got {momentum}")
        if self.min_scale >= self.max_scale:
            raise ValueError(f"min_scale ({min_scale}) must be less than max_scale ({max_scale})")
        
    def build(self, input_shape):
        """Build the layer"""
        if not isinstance(input_shape, list) or len(input_shape) != 2:
            raise ValueError("DynamicResidualScaling expects exactly 2 inputs: [main_path, residual_path]")
        
        # Validate input shapes match
        main_shape, residual_shape = input_shape
        if main_shape != residual_shape:
            raise ValueError(f"Input shapes must match: main_path {main_shape} != residual_path {residual_shape}")
        
        # For learned balance strategy
        if self.strategy == 'learned_balance':
            self.main_weight = self.add_weight(
                name='main_weight',
                shape=(),
                initializer='ones',
                trainable=True,
                dtype=self.dtype
            )
            self.residual_weight = self.add_weight(
                name='residual_weight',
                shape=(),
                initializer='ones',
                trainable=True,
                dtype=self.dtype
            )
        
        # For running statistics (adaptive_norm and magnitude_ratio)
        if self.strategy in ['adaptive_norm', 'magnitude_ratio']:
            self.running_main_norm = self.add_weight(
                name='running_main_norm',
                shape=(),
                initializer='ones',
                trainable=False,
                dtype=self.dtype
            )
            self.running_residual_norm = self.add_weight(
                name='running_residual_norm',
                shape=(),
                initializer='ones',
                trainable=False,
                dtype=self.dtype
            )
            
        super(DynamicResidualScaling, self).build(input_shape)
    
    def call(self, inputs, training=None):
        """Apply dynamic scaling"""
        if len(inputs) != 2:
            raise ValueError("DynamicResidualScaling expects exactly 2 inputs: [main_path, residual_path]")
        
        main_path, residual_path = inputs
        
        # Ensure inputs are the same shape
        if main_path.shape != residual_path.shape:
            raise ValueError(f"Input shapes must match during call: {main_path.shape} != {residual_path.shape}")
        
        if self.strategy == 'adaptive_norm':
            return self._adaptive_norm_scaling(main_path, residual_path, training)
        elif self.strategy == 'learned_balance':
            return self._learned_balance_scaling(main_path, residual_path)
        elif self.strategy == 'magnitude_ratio':
            return self._magnitude_ratio_scaling(main_path, residual_path, training)
        elif self.strategy == 'spectral_norm':
            return self._spectral_norm_scaling(main_path, residual_path)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
    
    def _adaptive_norm_scaling(self, main_path, residual_path, training):
        """
        Adaptive normalization scaling: Scale inputs so their L2 norms are balanced
        
        This strategy calculates the L2 norm of each path and scales them to have
        similar magnitudes, preventing one path from dominating the other.
        """
        # Calculate current norms
        main_norm = tf.sqrt(tf.reduce_mean(tf.square(main_path)) + self.epsilon)
        residual_norm = tf.sqrt(tf.reduce_mean(tf.square(residual_path)) + self.epsilon)
        
        if training:
            # Update running statistics during training
            self.running_main_norm.assign(
                self.momentum * self.running_main_norm + (1 - self.momentum) * main_norm
            )
            self.running_residual_norm.assign(
                self.momentum * self.running_residual_norm + (1 - self.momentum) * residual_norm
            )
            
            # Use current norms for training
            current_main_norm = main_norm
            current_residual_norm = residual_norm
        else:
            # Use running statistics for inference consistency
            current_main_norm = self.running_main_norm
            current_residual_norm = self.running_residual_norm
        
        # Calculate target norm (average of both paths)
        target_norm = (current_main_norm + current_residual_norm) / 2.0
        
        # Calculate scaling factors to achieve target norm
        main_scale = target_norm / (current_main_norm + self.epsilon)
        residual_scale = target_norm / (current_residual_norm + self.epsilon)
        
        # Apply alpha weighting (allows partial scaling)
        main_scale = (1 - self.alpha) + self.alpha * main_scale
        residual_scale = (1 - self.alpha) + self.alpha * residual_scale
        
        # Clip scaling factors to prevent instability
        main_scale = tf.clip_by_value(main_scale, self.min_scale, self.max_scale)
        residual_scale = tf.clip_by_value(residual_scale, self.min_scale, self.max_scale)
        
        # Apply scaling and combine
        scaled_main = main_path * main_scale
        scaled_residual = residual_path * residual_scale
        
        return scaled_main + scaled_residual
    
    def _learned_balance_scaling(self, main_path, residual_path):
        """
        Learned balance scaling: Let the network learn optimal weights for each path
        
        This strategy uses trainable weights that the network learns during training
        to find the optimal balance between main and residual paths.
        """
        # Ensure inputs are float32 to prevent type mismatches
        main_path = tf.cast(main_path, tf.float32)
        residual_path = tf.cast(residual_path, tf.float32)
        epsilon_f32 = tf.cast(self.epsilon, tf.float32)
        
        # Apply softmax normalization to ensure weights sum to reasonable values
        main_weight_f32 = tf.cast(self.main_weight, tf.float32)
        residual_weight_f32 = tf.cast(self.residual_weight, tf.float32)
        
        total_weight = tf.abs(main_weight_f32) + tf.abs(residual_weight_f32) + epsilon_f32
        
        main_weight_norm = tf.abs(main_weight_f32) / total_weight
        residual_weight_norm = tf.abs(residual_weight_f32) / total_weight
        
        # Apply learned weights
        weighted_main = main_path * main_weight_norm
        weighted_residual = residual_path * residual_weight_norm
        
        result = weighted_main + weighted_residual
        return tf.cast(result, tf.float32)
    
    def _magnitude_ratio_scaling(self, main_path, residual_path, training):
        """
        Magnitude ratio scaling: Scale based on the ratio of path magnitudes
        
        This strategy compares the average magnitude of each path and scales
        the smaller one up or the larger one down to achieve balance.
        """
        # Ensure inputs are float32 to prevent type mismatches
        main_path = tf.cast(main_path, tf.float32)
        residual_path = tf.cast(residual_path, tf.float32)
        
        # Calculate magnitudes (L1 norm averaged over all dimensions except batch)
        main_mag = tf.reduce_mean(tf.abs(main_path))
        residual_mag = tf.reduce_mean(tf.abs(residual_path))
        
        # Ensure magnitudes are float32
        main_mag = tf.cast(main_mag, tf.float32)
        residual_mag = tf.cast(residual_mag, tf.float32)
        
        if training:
            # Update running statistics
            self.running_main_norm.assign(
                self.momentum * self.running_main_norm + (1 - self.momentum) * main_mag
            )
            self.running_residual_norm.assign(
                self.momentum * self.running_residual_norm + (1 - self.momentum) * residual_mag
            )
            
            current_main_mag = main_mag
            current_residual_mag = residual_mag
        else:
            current_main_mag = self.running_main_norm
            current_residual_mag = self.running_residual_norm
        
        # Ensure all values are float32
        current_main_mag = tf.cast(current_main_mag, tf.float32)
        current_residual_mag = tf.cast(current_residual_mag, tf.float32)
        epsilon_f32 = tf.cast(self.epsilon, tf.float32)
        alpha_f32 = tf.cast(self.alpha, tf.float32)
        min_scale_f32 = tf.cast(self.min_scale, tf.float32)
        max_scale_f32 = tf.cast(self.max_scale, tf.float32)
        
        # Calculate ratio and determine scaling strategy
        ratio = current_residual_mag / (current_main_mag + epsilon_f32)
        ratio = tf.cast(ratio, tf.float32)
        
        # Use tf.cond for conditional logic to ensure consistent types
        def scale_down_residual():
            residual_scale = tf.clip_by_value(
                tf.cast(1.0, tf.float32) / ratio, min_scale_f32, max_scale_f32
            )
            main_scale = tf.cast(1.0, tf.float32)
            return main_scale, residual_scale
        
        def scale_up_residual():
            residual_scale = tf.clip_by_value(
                tf.cast(1.0, tf.float32) + alpha_f32 * (tf.cast(1.0, tf.float32) - ratio),
                min_scale_f32, max_scale_f32
            )
            main_scale = tf.cast(1.0, tf.float32)
            return main_scale, residual_scale
        
        main_scale, residual_scale = tf.cond(
            ratio > tf.cast(1.0, tf.float32),
            scale_down_residual,
            scale_up_residual
        )
        
        # Ensure final result is float32
        result = main_path * main_scale + residual_path * residual_scale
        return tf.cast(result, tf.float32)
    
    def _spectral_norm_scaling(self, main_path, residual_path):
        """
        Spectral normalization scaling: Scale based on spectral norms of the paths
        
        This strategy uses the spectral norm (largest singular value) to balance
        the paths, providing a mathematically principled approach.
        """
        # Ensure inputs are float32 to prevent type mismatches
        main_path = tf.cast(main_path, tf.float32)
        residual_path = tf.cast(residual_path, tf.float32)
        epsilon_f32 = tf.cast(self.epsilon, tf.float32)
        min_scale_f32 = tf.cast(self.min_scale, tf.float32)
        max_scale_f32 = tf.cast(self.max_scale, tf.float32)
        
        # Get batch size and spatial dimensions
        batch_size = tf.shape(main_path)[0]
        
        # Flatten tensors for spectral norm calculation (preserve batch dimension)
        main_flat = tf.reshape(main_path, (batch_size, -1))
        residual_flat = tf.reshape(residual_path, (batch_size, -1))
        
        # Calculate spectral norms (approximated by L2 norm along feature dimension)
        main_spectral = tf.norm(main_flat, ord=2, axis=1, keepdims=True)
        residual_spectral = tf.norm(residual_flat, ord=2, axis=1, keepdims=True)
        
        # Ensure spectral norms are float32
        main_spectral = tf.cast(main_spectral, tf.float32)
        residual_spectral = tf.cast(residual_spectral, tf.float32)
        
        # Calculate target spectral norm (average)
        mean_spectral = (main_spectral + residual_spectral) / tf.cast(2.0, tf.float32)
        
        # Calculate scaling factors
        main_scale = mean_spectral / (main_spectral + epsilon_f32)
        residual_scale = mean_spectral / (residual_spectral + epsilon_f32)
        
        # Reshape scaling factors to match input shape (broadcast-compatible)
        target_shape = [batch_size] + [1] * (len(main_path.shape) - 1)
        main_scale = tf.reshape(main_scale, target_shape)
        residual_scale = tf.reshape(residual_scale, target_shape)
        
        # Clip scaling factors
        main_scale = tf.clip_by_value(main_scale, min_scale_f32, max_scale_f32)
        residual_scale = tf.clip_by_value(residual_scale, min_scale_f32, max_scale_f32)
        
        result = main_path * main_scale + residual_path * residual_scale
        return tf.cast(result, tf.float32)
    
    def get_config(self):
        """Get layer configuration for serialization"""
        config = super(DynamicResidualScaling, self).get_config()
        config.update({
            'strategy': self.strategy,
            'alpha': self.alpha,
            'momentum': self.momentum,
            'epsilon': self.epsilon,
            'min_scale': self.min_scale,
            'max_scale': self.max_scale
        })
        return config
    
    def compute_output_shape(self, input_shape):
        """Compute the output shape of the layer"""
        if not isinstance(input_shape, list) or len(input_shape) != 2:
            raise ValueError("DynamicResidualScaling expects exactly 2 inputs")
        
        main_shape, residual_shape = input_shape
        if main_shape != residual_shape:
            raise ValueError(f"Input shapes must match: {main_shape} != {residual_shape}")
        
        return main_shape


# Utility functions for creating lambda-based scaling (simpler alternative)

def create_adaptive_lambda_scaling(alpha=0.5, epsilon=1e-6, min_scale=0.1, max_scale=2.0):
    """
    Create a lambda function for adaptive scaling without custom layers
    
    This is a simpler alternative that doesn't require custom layer implementation
    but provides basic adaptive scaling functionality.
    
    Args:
        alpha (float): Balance parameter
        epsilon (float): Numerical stability constant
        min_scale (float): Minimum scaling factor
        max_scale (float): Maximum scaling factor
    
    Returns:
        Lambda layer function for scaling
    """
    def scale_func(inputs):
        main_path, residual_path = inputs
        
        # Ensure inputs are float32 to prevent type mismatches
        main_path = tf.cast(main_path, tf.float32)
        residual_path = tf.cast(residual_path, tf.float32)
        epsilon_f32 = tf.cast(epsilon, tf.float32)
        alpha_f32 = tf.cast(alpha, tf.float32)
        min_scale_f32 = tf.cast(min_scale, tf.float32)
        max_scale_f32 = tf.cast(max_scale, tf.float32)
        
        # Calculate norms
        main_norm = tf.sqrt(tf.reduce_mean(tf.square(main_path)) + epsilon_f32)
        residual_norm = tf.sqrt(tf.reduce_mean(tf.square(residual_path)) + epsilon_f32)
        
        # Ensure norms are float32
        main_norm = tf.cast(main_norm, tf.float32)
        residual_norm = tf.cast(residual_norm, tf.float32)
        
        # Target balanced norm
        target_norm = (main_norm + residual_norm) / tf.cast(2.0, tf.float32)
        
        # Calculate scaling factors
        main_scale = target_norm / (main_norm + epsilon_f32)
        residual_scale = target_norm / (residual_norm + epsilon_f32)
        
        # Apply alpha weighting and clipping
        main_scale = tf.clip_by_value(
            (tf.cast(1.0, tf.float32) - alpha_f32) + alpha_f32 * main_scale,
            min_scale_f32, max_scale_f32
        )
        residual_scale = tf.clip_by_value(
            (tf.cast(1.0, tf.float32) - alpha_f32) + alpha_f32 * residual_scale,
            min_scale_f32, max_scale_f32
        )
        
        result = main_path * main_scale + residual_path * residual_scale
        return tf.cast(result, tf.float32)
    
    return scale_func


def create_magnitude_ratio_lambda_scaling(alpha=0.5, epsilon=1e-6, min_scale=0.1, max_scale=2.0):
    """
    Create a lambda function for magnitude ratio scaling
    
    Args:
        alpha (float): Balance parameter
        epsilon (float): Numerical stability constant
        min_scale (float): Minimum scaling factor  
        max_scale (float): Maximum scaling factor
    
    Returns:
        Lambda layer function for scaling
    """
    def scale_func(inputs):
        main_path, residual_path = inputs
        
        # Ensure inputs are float32 to prevent type mismatches
        main_path = tf.cast(main_path, tf.float32)
        residual_path = tf.cast(residual_path, tf.float32)
        epsilon_f32 = tf.cast(epsilon, tf.float32)
        alpha_f32 = tf.cast(alpha, tf.float32)
        min_scale_f32 = tf.cast(min_scale, tf.float32)
        max_scale_f32 = tf.cast(max_scale, tf.float32)
        
        # Calculate magnitudes
        main_mag = tf.reduce_mean(tf.abs(main_path))
        residual_mag = tf.reduce_mean(tf.abs(residual_path))
        
        # Ensure magnitudes are float32
        main_mag = tf.cast(main_mag, tf.float32)
        residual_mag = tf.cast(residual_mag, tf.float32)
        
        # Calculate ratio and scaling
        ratio = residual_mag / (main_mag + epsilon_f32)
        ratio = tf.cast(ratio, tf.float32)
        
        # Use tf.cond for conditional logic to ensure consistent types
        def scale_down_residual():
            residual_scale = tf.clip_by_value(
                tf.cast(1.0, tf.float32) / ratio, min_scale_f32, max_scale_f32
            )
            main_scale = tf.cast(1.0, tf.float32)
            return main_scale, residual_scale
        
        def scale_up_residual():
            residual_scale = tf.clip_by_value(
                tf.cast(1.0, tf.float32) + alpha_f32 * (tf.cast(1.0, tf.float32) - ratio),
                min_scale_f32, max_scale_f32
            )
            main_scale = tf.cast(1.0, tf.float32)
            return main_scale, residual_scale
        
        main_scale, residual_scale = tf.cond(
            ratio > tf.cast(1.0, tf.float32),
            scale_down_residual,
            scale_up_residual
        )
        
        result = main_path * main_scale + residual_path * residual_scale
        return tf.cast(result, tf.float32)
    
    return scale_func
