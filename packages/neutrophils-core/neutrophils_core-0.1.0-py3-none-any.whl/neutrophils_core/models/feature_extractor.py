#!/usr/bin/env python3
"""
Feature Extractor Component for Neutrophil Maturation Classification

This module implements a configurable CNN feature extractor that extracts the
convolutional backbone from the existing ResNet-based classifier. It serves as
the foundation for hierarchical models by providing shared feature representations.

The FeatureExtractor extracts the convolutional layers (before GlobalAveragePooling)
from the build_model function in trainer_2d/cnn_classifier_2d.py and makes them
reusable with configurable architectures.
"""

import tensorflow as tf
from tensorflow.keras.layers import (
    Input, Conv2D, BatchNormalization, Add, ReLU, LeakyReLU, PReLU,
    Lambda, GlobalAveragePooling2D
)
from tensorflow.keras.models import Model
from tensorflow.keras.activations import get as get_activation

# Import DynamicResidualScaling from the same models package
from .dynamic_residual_scaling import DynamicResidualScaling, create_adaptive_lambda_scaling


@tf.keras.utils.register_keras_serializable()
class FeatureExtractor(tf.keras.Model):
    """
    Configurable CNN Feature Extractor for Neutrophil Classification
    
    This class extracts the convolutional backbone from the existing ResNet-based
    architecture, providing shared feature representations for hierarchical models.
    
    The feature extractor supports:
    - Configurable backbone architectures (different depths, filter sizes)
    - Dynamic residual scaling strategies for bias correction
    - Multiple activation functions and initialization strategies
    - Backward compatibility with existing TOML configurations
    - Enhanced summary with detailed layer information and colorized output
    
    Architecture Overview:
    ----------------------
    Input -> Conv Blocks (with optional residual connections) -> Feature Tensor
    
    Each Conv Block contains:
    - Multiple Conv2D layers (configurable count)
    - Optional BatchNormalization
    - Optional residual connections with projection
    - Configurable activation functions
    - Dynamic residual scaling (if enabled)
    
    The output is the feature tensor BEFORE GlobalAveragePooling, allowing
    hierarchical heads to apply their own pooling strategies.
    """
    
    def __init__(self, config=None, input_shape=None, name='feature_extractor', **kwargs):
        """
        Initialize the FeatureExtractor
        
        Args:
            config (dict): Configuration dictionary containing:
                - conv_blocks: Configuration for convolutional blocks
                - input_shape: Shape of input tensor (optional, can be inferred)
            input_shape (tuple): Input shape (H, W, C), overrides config if provided
            name (str): Name of the model
            **kwargs: Additional keyword arguments for tf.keras.Model
        """
        super(FeatureExtractor, self).__init__(name=name, **kwargs)
        
        # Store configuration
        self.config = config or {}
        self.input_shape_config = input_shape
        
        # Validate and set default configuration
        self._validate_and_set_defaults()
        
        # Build the feature extraction layers
        self._build_feature_layers()
    
    def _validate_and_set_defaults(self):
        """Validate configuration and set defaults based on existing architecture"""
        
        # Default configuration matching the existing ResNet architecture
        default_config = {
            'conv_blocks': {
                'filters': [32, 64, 128],
                'kernel_size': [3, 3],
                'activation': {'name': 'leaky_relu', 'alpha': 0.1},
                'padding': 'same',
                'use_batch_norm': True,
                'use_residual': True,
                'conv_layers': 2,
                'residual_kernel_size': [[1, 1], [1, 1]],
                'kernel_initializer': 'he_normal',
                'bias_initializer': 'zeros',
                'residual_scaling': {
                    'strategy': 'fixed_scaling',
                    'params': {
                        'alpha': 0.5,
                        'scale': 0.2,
                        'momentum': 0.99,
                        'epsilon': 1e-6,
                        'min_scale': 0.1,
                        'max_scale': 2.0
                    }
                }
            }
        }
        
        # Merge user config with defaults
        if 'conv_blocks' not in self.config:
            self.config['conv_blocks'] = default_config['conv_blocks']
        else:
            # Merge conv_blocks configuration
            for key, value in default_config['conv_blocks'].items():
                if key not in self.config['conv_blocks']:
                    self.config['conv_blocks'][key] = value
        
        # Validate required parameters
        conv_config = self.config['conv_blocks']
        required_params = ['filters', 'kernel_size', 'activation']
        for param in required_params:
            if param not in conv_config:
                raise ValueError(f"Missing required parameter '{param}' in conv_blocks configuration")
        
        # Ensure filters is a list
        if not isinstance(conv_config['filters'], list):
            raise ValueError("'filters' must be a list of integers")
        
        # Validate residual_kernel_size length if provided
        if 'residual_kernel_size' in conv_config:
            expected_length = len(conv_config['filters']) - 1
            if len(conv_config['residual_kernel_size']) != expected_length:
                print(f"Warning: residual_kernel_size length ({len(conv_config['residual_kernel_size'])}) "
                      f"doesn't match expected length ({expected_length}). Using default [1,1] for missing entries.")
    
    def _get_weight_initializer(self, initializer_name):
        """Get weight initializer based on name with stability improvements"""
        if initializer_name is None:
            return 'he_normal'  # Default stable choice for ReLU networks
        
        initializer_name = initializer_name.lower()
        
        # Map common initializer names to TensorFlow initializers
        initializer_map = {
            'he_normal': tf.keras.initializers.HeNormal(seed=42),
            'he_uniform': tf.keras.initializers.HeUniform(seed=42),
            'xavier_normal': tf.keras.initializers.GlorotNormal(seed=42),
            'glorot_normal': tf.keras.initializers.GlorotNormal(seed=42),
            'xavier_uniform': tf.keras.initializers.GlorotUniform(seed=42),
            'glorot_uniform': tf.keras.initializers.GlorotUniform(seed=42),
            'lecun_normal': tf.keras.initializers.LecunNormal(seed=42),
            'lecun_uniform': tf.keras.initializers.LecunUniform(seed=42),
            'random_normal': tf.keras.initializers.RandomNormal(stddev=0.02, seed=42),
            'random_uniform': tf.keras.initializers.RandomUniform(minval=-0.05, maxval=0.05, seed=42),
            'truncated_normal': tf.keras.initializers.TruncatedNormal(stddev=0.02, seed=42),
            'zeros': 'zeros',
            'ones': 'ones'
        }
        
        if initializer_name in initializer_map:
            return initializer_map[initializer_name]
        else:
            print(f"Warning: Unknown initializer '{initializer_name}', using 'he_normal'")
            return tf.keras.initializers.HeNormal(seed=42)
    
    def _get_activation_function(self, activation):
        """Convert activation function specification to a callable function or string"""
        if isinstance(activation, str):
            return activation
        elif isinstance(activation, dict):
            if 'name' not in activation:
                print(f"Warning: Activation dictionary missing 'name' key. Using 'relu' as default.")
                return 'relu'
            
            name = activation['name'].lower()
            
            if name == 'leaky_relu':
                alpha = activation.get('alpha', 0.3)
                return LeakyReLU(alpha=alpha)
            elif name == 'prelu':
                return PReLU()
            elif name == 'elu':
                alpha = activation.get('alpha', 1.0)
                return tf.keras.layers.ELU(alpha=alpha)
            elif name == 'selu':
                return 'selu'
            elif name == 'swish' or name == 'silu':
                return tf.keras.activations.swish
            elif name == 'gelu':
                return tf.keras.activations.gelu
            elif name == 'relu6':
                return tf.keras.layers.ReLU(max_value=6)
            else:
                try:
                    return get_activation(name)
                except ValueError:
                    print(f"Warning: Unknown activation function '{name}'. Using 'relu' as default.")
                    return 'relu'
        else:
            if callable(activation):
                return activation
            print(f"Warning: Unsupported activation type {type(activation)}. Using 'relu' as default.")
            return 'relu'
    
    def _build_feature_layers(self):
        """Build the convolutional feature extraction layers"""
        
        conv_config = self.config['conv_blocks']
        
        # Get configuration parameters
        filters_list = conv_config['filters']
        kernel_size_base = tuple(conv_config.get('kernel_size', [3, 3]))
        activation_config = conv_config.get('activation', 'relu')
        padding_base = conv_config.get('padding', 'same')
        use_batch_norm_base = conv_config.get('use_batch_norm', False)
        use_residual_base = conv_config.get('use_residual', False)
        conv_layers_count = conv_config.get('conv_layers', 2)
        residual_kernel_sizes_list = conv_config.get('residual_kernel_size', [])
        
        # Get weight initializers
        conv_kernel_init_name = conv_config.get('kernel_initializer', 'he_normal')
        conv_bias_init_name = conv_config.get('bias_initializer', 'zeros')
        conv_initializer = self._get_weight_initializer(conv_kernel_init_name)
        conv_bias_initializer = conv_bias_init_name
        
        # Get residual scaling configuration
        residual_scaling_config = conv_config.get('residual_scaling', {})
        self.residual_scaling_strategy = residual_scaling_config.get('strategy', 'standard')
        self.residual_scaling_params = residual_scaling_config.get('params', {})
        
        # Store layers for building the model
        self.conv_layers = []
        self.bn_layers = []
        self.activation_layers = []
        self.residual_projection_layers = []
        self.residual_bn_layers = []
        self.residual_scaling_layers = []
        
        # Build layers for each block
        for i, current_filters in enumerate(filters_list):
            block_layers = {}
            
            # Standard ResNet downsampling: first block keeps spatial size, subsequent blocks downsample by 2
            downsample_stride = (2, 2) if i > 0 else (1, 1)
            
            # Build conv layers for this block
            block_conv_layers = []
            block_bn_layers = []
            block_activation_layers = []
            
            for i_conv in range(conv_layers_count):
                # First conv in each block uses downsampling stride, others use (1,1)
                conv_strides = downsample_stride if i_conv == 0 else (1, 1)
                
                conv_layer = Conv2D(
                    current_filters,
                    kernel_size_base,
                    strides=conv_strides,
                    activation=None,  # Activation applied separately
                    padding=padding_base,
                    kernel_initializer=conv_initializer,
                    bias_initializer=conv_bias_initializer,
                    use_bias=not use_batch_norm_base,  # No bias when using BatchNorm
                    name=f'main_block_{i}_conv_{i_conv}'
                )
                block_conv_layers.append(conv_layer)
                
                if use_batch_norm_base:
                    bn_layer = BatchNormalization(
                        momentum=0.99,
                        epsilon=1e-3,
                        center=True,
                        scale=True,
                        beta_initializer='zeros',
                        gamma_initializer='ones',
                        name=f'bn_main_block_{i}_conv_{i_conv}'
                    )
                    block_bn_layers.append(bn_layer)
                else:
                    block_bn_layers.append(None)
                
                # Apply activation for all but the last conv layer in the main path
                if i_conv < conv_layers_count - 1:
                    activation_fn = self._get_activation_function(activation_config)
                    # Set name for layer-based activations
                    if hasattr(activation_fn, '__call__') and hasattr(activation_fn, 'name'):
                        if hasattr(activation_fn, '__class__') and hasattr(activation_fn.__class__, '__name__'):
                            layer_type = activation_fn.__class__.__name__.lower()
                            activation_fn.name = f'{layer_type}_main_block_{i}_conv_{i_conv}'
                    block_activation_layers.append(activation_fn)
                else:
                    block_activation_layers.append(None)
            
            block_layers['conv_layers'] = block_conv_layers
            block_layers['bn_layers'] = block_bn_layers
            block_layers['activation_layers'] = block_activation_layers
            
            # Build residual projection if needed
            if use_residual_base:
                res_kernel_idx = i
                res_kernel_size = tuple(residual_kernel_sizes_list[res_kernel_idx] if res_kernel_idx < len(residual_kernel_sizes_list) else [1, 1])
                
                residual_projection = Conv2D(
                    current_filters,
                    res_kernel_size,
                    strides=downsample_stride,
                    padding='same',
                    activation=None,
                    kernel_initializer=conv_initializer,
                    bias_initializer=conv_bias_initializer,
                    use_bias=not use_batch_norm_base,
                    name=f'conv_skip_projection_block_{i}'
                )
                block_layers['residual_projection'] = residual_projection
                
                if use_batch_norm_base:
                    residual_bn = BatchNormalization(
                        momentum=0.99,
                        epsilon=1e-3,
                        center=True,
                        scale=True,
                        beta_initializer='zeros',
                        gamma_initializer='ones',
                        name=f'bn_skip_projection_block_{i}'
                    )
                    block_layers['residual_bn'] = residual_bn
                else:
                    block_layers['residual_bn'] = None
                
                # Create residual scaling layer
                if self.residual_scaling_strategy == 'standard':
                    block_layers['residual_scaling'] = None
                elif self.residual_scaling_strategy == 'fixed_scaling':
                    scale = self.residual_scaling_params.get('scale', 0.5)
                    block_layers['residual_scaling'] = Lambda(
                        lambda inputs: inputs[0] + inputs[1] * scale,
                        name=f'lambda_fixed_scale_block_{i}'
                    )
                elif self.residual_scaling_strategy == 'dynamic_adaptive':
                    alpha = self.residual_scaling_params.get('alpha', 0.5)
                    block_layers['residual_scaling'] = DynamicResidualScaling(
                        strategy='adaptive_norm',
                        alpha=alpha,
                        name=f'dyn_scale_adaptive_block_{i}'
                    )
                elif self.residual_scaling_strategy == 'dynamic_learned':
                    alpha = self.residual_scaling_params.get('alpha', 0.5)
                    block_layers['residual_scaling'] = DynamicResidualScaling(
                        strategy='learned_balance',
                        alpha=alpha,
                        name=f'dyn_scale_learned_block_{i}'
                    )
                elif self.residual_scaling_strategy == 'lambda_adaptive':
                    alpha = self.residual_scaling_params.get('alpha', 0.5)
                    scaling_func = create_adaptive_lambda_scaling(alpha=alpha)
                    block_layers['residual_scaling'] = Lambda(
                        scaling_func,
                        name=f'lambda_adaptive_scale_block_{i}'
                    )
                else:
                    raise ValueError(f"Unknown residual scaling strategy: {self.residual_scaling_strategy}")
            else:
                block_layers['residual_projection'] = None
                block_layers['residual_bn'] = None
                block_layers['residual_scaling'] = None
            
            # Final block activation
            final_activation_fn = self._get_activation_function(activation_config)
            if hasattr(final_activation_fn, '__call__') and hasattr(final_activation_fn, 'name'):
                if hasattr(final_activation_fn, '__class__') and hasattr(final_activation_fn.__class__, '__name__'):
                    layer_type = final_activation_fn.__class__.__name__.lower()
                    final_activation_fn.name = f'{layer_type}_final_block_{i}'
            block_layers['final_activation'] = final_activation_fn
            
            # Store block configuration
            self.conv_layers.append(block_layers)
        
        print(f"✓ FeatureExtractor built with {len(filters_list)} convolutional blocks")
        print(f"  - Filters: {filters_list}")
        print(f"  - Residual connections: {use_residual_base}")
        print(f"  - Batch normalization: {use_batch_norm_base}")
        print(f"  - Residual scaling strategy: {self.residual_scaling_strategy}")
        if self.residual_scaling_params and self.residual_scaling_strategy != 'standard':
            print(f"  - Residual scaling params: {self.residual_scaling_params}")
    
    def build(self, input_shape):
        """
        Build all layers with the given input shape
        
        This method builds all the layers in the feature extractor with the specified
        input shape, ensuring that layer output shapes are properly computed and
        available for model summary functions.
        
        Args:
            input_shape: Input shape tuple (batch_size, height, width, channels)
                        or (height, width, channels)
        """
        # Handle input shape format - add batch dimension if not present
        if len(input_shape) == 3:
            # Input shape without batch dimension, add None for batch
            shape_with_batch = (None,) + input_shape
        else:
            # Input shape already includes batch dimension
            shape_with_batch = input_shape
        
        conv_config = self.config['conv_blocks']
        filters_list = conv_config['filters']
        use_residual_base = conv_config.get('use_residual', False)
        conv_layers_count = conv_config.get('conv_layers', 2)
        
        # Track current shape through the network (with batch dimension)
        current_shape = shape_with_batch
        
        # Build each convolutional block
        for i, current_filters in enumerate(filters_list):
            block_layers = self.conv_layers[i]
            
            # Standard ResNet downsampling: first block keeps spatial size, subsequent blocks downsample by 2
            downsample_stride = (2, 2) if i > 0 else (1, 1)
            
            # Store the input shape for this block (for residual connections)
            block_input_shape = current_shape
            
            # Build conv layers for this block
            for i_conv in range(conv_layers_count):
                conv_strides = downsample_stride if i_conv == 0 else (1, 1)
                
                # Build conv layer
                conv_layer = block_layers['conv_layers'][i_conv]
                conv_layer.build(current_shape)
                current_shape = conv_layer.compute_output_shape(current_shape)
                
                # Build batch normalization layer if present
                if block_layers['bn_layers'][i_conv] is not None:
                    bn_layer = block_layers['bn_layers'][i_conv]
                    bn_layer.build(current_shape)
                    current_shape = bn_layer.compute_output_shape(current_shape)
            
            # Build residual projection layers if needed
            if use_residual_base:
                # Build residual projection layer
                if block_layers['residual_projection'] is not None:
                    proj_layer = block_layers['residual_projection']
                    proj_layer.build(block_input_shape)
                    proj_output_shape = proj_layer.compute_output_shape(block_input_shape)
                    
                    # Build residual batch normalization if present
                    if block_layers['residual_bn'] is not None:
                        residual_bn = block_layers['residual_bn']
                        residual_bn.build(proj_output_shape)
        
        # Mark as built
        self.built = True
    
    def _get_block_input_shape(self, block_idx, initial_shape):
        """
        Calculate the input shape for a specific block based on previous blocks
        
        Args:
            block_idx: Index of the current block
            initial_shape: Initial input shape (height, width, channels)
            
        Returns:
            Input shape for the specified block
        """
        conv_config = self.config['conv_blocks']
        filters_list = conv_config['filters']
        
        current_shape = initial_shape
        
        # Apply transformations from previous blocks
        for i in range(block_idx):
            # Apply downsampling if not the first block
            if i > 0:
                current_shape = (current_shape[0] // 2, current_shape[1] // 2, filters_list[i])
            else:
                current_shape = (current_shape[0], current_shape[1], filters_list[i])
        
        return current_shape
    
    def call(self, inputs, training=None):
        """
        Forward pass through the feature extractor
        
        Args:
            inputs: Input tensor of shape (batch_size, height, width, channels)
            training: Boolean indicating training mode
        
        Returns:
            Feature tensor before global average pooling of shape 
            (batch_size, feature_height, feature_width, feature_channels)
        """
        x = inputs
        
        conv_config = self.config['conv_blocks']
        filters_list = conv_config['filters']
        use_residual_base = conv_config.get('use_residual', False)
        conv_layers_count = conv_config.get('conv_layers', 2)
        
        # Process each convolutional block
        for i, current_filters in enumerate(filters_list):
            with tf.name_scope(f'feature_block_{i}'):
                block_layers = self.conv_layers[i]
                block_input_tensor = x  # Input to the current block for potential skip connection
                current_path_tensor = x  # Tensor being transformed within the main path
                
                # Apply conv layers in the main path
                for i_conv in range(conv_layers_count):
                    with tf.name_scope(f'conv_{i_conv}'):
                        # Apply convolution
                        current_path_tensor = block_layers['conv_layers'][i_conv](current_path_tensor)
                        
                        # Apply batch normalization if enabled
                        if block_layers['bn_layers'][i_conv] is not None:
                            current_path_tensor = block_layers['bn_layers'][i_conv](current_path_tensor, training=training)
                        
                        # Apply activation for all but the last conv layer
                        if block_layers['activation_layers'][i_conv] is not None:
                            current_path_tensor = block_layers['activation_layers'][i_conv](current_path_tensor)
                
                # Handle residual connections
                if use_residual_base:
                    projected_skip_tensor = block_input_tensor
                    needs_projection = False
                    
                    # Determine stride used in this block
                    downsample_stride = (2, 2) if i > 0 else (1, 1)
                    
                    # Need projection if stride changes or channels change
                    if downsample_stride != (1, 1) or block_input_tensor.shape[-1] != current_filters:
                        needs_projection = True
                    
                    if needs_projection:
                        projected_skip_tensor = block_layers['residual_projection'](block_input_tensor)
                        if block_layers['residual_bn'] is not None:
                            projected_skip_tensor = block_layers['residual_bn'](projected_skip_tensor, training=training)
                    
                    # Apply residual scaling strategy
                    if self.residual_scaling_strategy == 'standard':
                        x = Add(name=f'add_standard_block_{i}')([current_path_tensor, projected_skip_tensor])
                    elif block_layers['residual_scaling'] is not None:
                        x = block_layers['residual_scaling']([current_path_tensor, projected_skip_tensor])
                    else:
                        # Fallback to standard add
                        x = Add(name=f'add_fallback_block_{i}')([current_path_tensor, projected_skip_tensor])
                    
                    # Apply final block activation AFTER Add or scaling
                    x = block_layers['final_activation'](x)
                else:
                    # Not a residual block, apply final activation to main path
                    x = block_layers['final_activation'](current_path_tensor)
        
        return x
    
    def summary(self, input_shape=None, level="standard", style="compact", line_length=None, positions=None, **kwargs):
        """
        Enhanced summary method with detailed layer information and colorized output
        
        Args:
            input_shape: Input shape tuple (H, W, C). If None, uses stored input_shape_config
            level: Summary level - "standard", "detailed", "connections", "graph", or "ascii_art"
                  - "standard": Uses default Keras summary
                  - "detailed": Shows detailed layer breakdown with colors
                  - "connections": Shows layer connections and data flow
                  - "ascii_art": Shows ASCII art visualization
            style: Style for ASCII art visualization ("compact", "tree", "flowchart")
            line_length: Line length for formatting (passed to standard summary)
            positions: Column positions for formatting (passed to standard summary)
            **kwargs: Additional arguments for standard summary
        """
        # Handle different summary levels
        if level == "standard":
            # Use standard Keras summary for standard level
            super().summary(line_length=line_length, positions=positions, **kwargs)
        else:
            # Import model_utils functions for enhanced summary
            try:
                if level in ["detailed", "connections", "graph", "ascii_art"]:
                    from .model_utils import print_feature_extractor_detailed_summary
                    print_feature_extractor_detailed_summary(self, input_shape, level, style)
                else:
                    # Unknown level, fallback to standard
                    print(f"Unknown summary level '{level}', using standard summary")
                    super().summary(line_length=line_length, positions=positions, **kwargs)
            except ImportError:
                # Fallback to standard summary if model_utils not available
                print("Enhanced summary not available, using standard summary")
                super().summary(line_length=line_length, positions=positions, **kwargs)
    
    def get_config(self):
        """Get configuration for serialization"""
        config = super(FeatureExtractor, self).get_config()
        config.update({
            'config': self.config,
            'input_shape_config': self.input_shape_config
        })
        return config
    
    @classmethod
    def from_config(cls, config):
        """Create FeatureExtractor from configuration"""
        return cls(**config)
    
    def get_feature_shape(self, input_shape):
        """
        Calculate the output feature shape given an input shape
        
        Args:
            input_shape: Input shape tuple (height, width, channels)
        
        Returns:
            Output feature shape tuple (feature_height, feature_width, feature_channels)
        """
        # Build a temporary model to calculate output shape
        temp_input = Input(shape=input_shape)
        temp_output = self(temp_input)
        return temp_output.shape[1:]  # Remove batch dimension
    
    def build_layers_with_shape(self, input_shape):
        """
        Build all layers with a specific input shape to ensure output_shape is available.
        This is useful for summary functions that need to access layer output shapes.
        
        Args:
            input_shape: Input shape tuple (height, width, channels)
        """
        if not hasattr(self, '_layers_built') or not self._layers_built:
            # Create a dummy input to build all layers
            dummy_input = tf.zeros((1,) + input_shape)
            _ = self(dummy_input, training=False)
            self._layers_built = True
    
    def get_layer_output_shapes(self, input_shape):
        """
        Get output shapes for all layers in the feature extractor.
        
        Args:
            input_shape: Input shape tuple (height, width, channels)
            
        Returns:
            dict: Dictionary mapping layer names to their output shapes
        """
        # Ensure layers are built
        self.build_layers_with_shape(input_shape)
        
        layer_shapes = {}
        
        for block_idx, block_layers in enumerate(self.conv_layers):
            # Conv layers
            if 'conv_layers' in block_layers:
                for conv_idx, conv_layer in enumerate(block_layers['conv_layers']):
                    if conv_layer is not None:
                        try:
                            layer_shapes[conv_layer.name] = conv_layer.output_shape
                        except (AttributeError, ValueError):
                            layer_shapes[conv_layer.name] = "Not built"
            
            # Batch normalization layers
            if 'bn_layers' in block_layers:
                for bn_idx, bn_layer in enumerate(block_layers['bn_layers']):
                    if bn_layer is not None:
                        try:
                            layer_shapes[bn_layer.name] = bn_layer.output_shape
                        except (AttributeError, ValueError):
                            layer_shapes[bn_layer.name] = "Not built"
            
            # Activation layers
            if 'activation_layers' in block_layers:
                for act_idx, act_layer in enumerate(block_layers['activation_layers']):
                    if act_layer is not None and hasattr(act_layer, 'name'):
                        try:
                            layer_shapes[act_layer.name] = getattr(act_layer, 'output_shape', "Same as input")
                        except (AttributeError, ValueError):
                            layer_shapes[act_layer.name] = "Same as input"
            
            # Residual projection layers
            if 'residual_projection' in block_layers and block_layers['residual_projection'] is not None:
                proj_layer = block_layers['residual_projection']
                try:
                    layer_shapes[proj_layer.name] = proj_layer.output_shape
                except (AttributeError, ValueError):
                    layer_shapes[proj_layer.name] = "Not built"
            
            # Residual BN layers
            if 'residual_bn' in block_layers and block_layers['residual_bn'] is not None:
                bn_layer = block_layers['residual_bn']
                try:
                    layer_shapes[bn_layer.name] = bn_layer.output_shape
                except (AttributeError, ValueError):
                    layer_shapes[bn_layer.name] = "Not built"
            
            # Residual scaling layers
            if 'residual_scaling' in block_layers and block_layers['residual_scaling'] is not None:
                scaling_layer = block_layers['residual_scaling']
                layer_name = getattr(scaling_layer, 'name', f"residual_scaling_block_{block_idx}")
                try:
                    layer_shapes[layer_name] = getattr(scaling_layer, 'output_shape', "Same as input")
                except (AttributeError, ValueError):
                    layer_shapes[layer_name] = "Same as input"
            
            # Final activation
            if 'final_activation' in block_layers and block_layers['final_activation'] is not None:
                final_act = block_layers['final_activation']
                if hasattr(final_act, 'name'):
                    try:
                        layer_shapes[final_act.name] = getattr(final_act, 'output_shape', "Same as input")
                    except (AttributeError, ValueError):
                        layer_shapes[final_act.name] = "Same as input"
        
        return layer_shapes
    
    def build_model(self, input_shape):
        """
        Build a functional Keras model from the feature extractor
        
        Args:
            input_shape: Input shape tuple (height, width, channels)
        
        Returns:
            tf.keras.Model: Functional model
        """
        inputs = Input(shape=input_shape, name='feature_extractor_input')
        features = self(inputs)
        
        model = Model(inputs=inputs, outputs=features, name=self.name + '_model')
        return model


def create_feature_extractor_from_config(config, input_shape=None):
    """
    Factory function to create a FeatureExtractor from configuration
    
    This function provides a convenient way to create a FeatureExtractor
    from TOML configuration files used in the existing codebase.
    
    Args:
        config (dict): Configuration dictionary with 'model' section
        input_shape (tuple): Input shape (height, width, channels)
    
    Returns:
        FeatureExtractor: Configured feature extractor instance
    
    Example:
        >>> import toml
        >>> config = toml.load('config/resnet_2d.user.toml')
        >>> feature_extractor = create_feature_extractor_from_config(
        ...     config, input_shape=(96, 96, 3)
        ... )
        >>> features = feature_extractor(inputs)
    """
    model_config = config.get('model', {}) if 'model' in config else config
    
    feature_extractor = FeatureExtractor(
        config=model_config,
        input_shape=input_shape
    )
    
    return feature_extractor