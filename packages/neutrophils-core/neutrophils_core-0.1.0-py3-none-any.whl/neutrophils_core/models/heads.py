#!/usr/bin/env python3
"""
Generic Classification Head Component for Neutrophil Maturation Classification

This module implements configurable classification heads that work with the FeatureExtractor
to provide hierarchical classification outputs for neutrophil maturation stages.

The ClassificationHead supports:
- Hierarchical classification (coarse early/late and fine-grained stage classification)
- Configurable fully connected layer architectures
- Different output activations (softmax, sigmoid, linear)
- Dropout regularization and batch normalization
- TOML configuration support
- Integration with the existing neutrophil hierarchy

Architecture Overview:
---------------------
Feature Tensor -> GlobalAveragePooling2D -> FC Layers -> Output

Each Classification Head contains:
- GlobalAveragePooling2D layer for spatial reduction
- Configurable sequence of Dense layers with optional dropout
- Optional batch normalization between layers
- Final output layer with configurable activation
"""

import tensorflow as tf
from tensorflow.keras.layers import (
    GlobalAveragePooling2D, Dense, Dropout, BatchNormalization, Layer
)
from tensorflow.keras.saving import register_keras_serializable
from typing import Dict, List, Any, Optional, Union
from ..loader.hierarchical_labels import NEUTROPHIL_HIERARCHY, get_head_info


@register_keras_serializable()
class ClassificationHead(tf.keras.layers.Layer):
    """
    Generic Classification Head for Hierarchical Neutrophil Classification
    
    This layer takes feature tensors from the FeatureExtractor and produces
    classification outputs for a specific hierarchical level (e.g., coarse or stage).
    
    The head applies global average pooling followed by configurable fully connected
    layers and produces final classification probabilities.
    
    Architecture:
    Feature Tensor -> GlobalAveragePooling2D -> FC Layers -> Output
    
    Supports:
    - Different numbers of classes (2 for coarse, 4 for stage)
    - Configurable FC layer architectures
    - Optional dropout and batch normalization
    - Different output activations
    - TOML configuration integration
    """
    
    def __init__(
        self,
        num_classes: int,
        name: str = "classification_head",
        fc_config: Optional[Dict[str, Any]] = None,
        output_activation: str = "softmax",
        use_global_pooling: bool = True,
        **kwargs
    ):
        """
        Initialize the Classification Head
        
        Args:
            num_classes (int): Number of output classes for this head
            name (str): Name of the head (used for layer naming)
            fc_config (dict, optional): Configuration for fully connected layers:
                - units (list): List of units for each FC layer (e.g., [128, 64])
                - activation (str/dict): Activation function for FC layers
                - dropout (float): Dropout rate (0.0 = no dropout)
                - use_batch_norm (bool): Whether to use batch normalization
                - kernel_initializer (str): Weight initialization method
                - bias_initializer (str): Bias initialization method
            output_activation (str): Activation for final output layer
            use_global_pooling (bool): Whether to apply GlobalAveragePooling2D
            **kwargs: Additional keyword arguments for tf.keras.layers.Layer
        """
        super(ClassificationHead, self).__init__(name=name, **kwargs)
        
        self.num_classes = num_classes
        self.output_activation = output_activation
        self.use_global_pooling = use_global_pooling
        
        # Set default FC configuration
        self.fc_config = fc_config or {
            "units": [128],
            "activation": "relu", 
            "dropout": 0.3,
            "use_batch_norm": False,
            "kernel_initializer": "he_normal",
            "bias_initializer": "zeros"
        }
        
        # Validate configuration
        self._validate_config()
        
        # Build layers
        self._build_layers()
    
    def _validate_config(self):
        """Validate the configuration parameters"""
        if self.num_classes <= 0:
            raise ValueError(f"num_classes must be positive, got {self.num_classes}")
        
        if not isinstance(self.fc_config["units"], list):
            raise ValueError("fc_config['units'] must be a list of integers")
        
        if any(units <= 0 for units in self.fc_config["units"]):
            raise ValueError("All FC layer units must be positive")
        
        dropout = self.fc_config.get("dropout", 0.0)
        if not (0.0 <= dropout < 1.0):
            raise ValueError(f"Dropout rate must be in [0.0, 1.0), got {dropout}")
    
    def _get_activation_function(self, activation):
        """Convert activation configuration to a callable function"""
        if isinstance(activation, str):
            return activation
        elif isinstance(activation, dict):
            if 'name' not in activation:
                print(f"Warning: Activation dictionary missing 'name' key. Using 'relu' as default.")
                return 'relu'
            
            name = activation['name'].lower()
            
            if name == 'leaky_relu':
                alpha = activation.get('alpha', 0.3)
                return tf.keras.layers.LeakyReLU(alpha=alpha)
            elif name == 'prelu':
                return tf.keras.layers.PReLU()
            elif name == 'elu':
                alpha = activation.get('alpha', 1.0)
                return tf.keras.layers.ELU(alpha=alpha)
            else:
                try:
                    return tf.keras.activations.get(name)
                except ValueError:
                    print(f"Warning: Unknown activation function '{name}'. Using 'relu' as default.")
                    return 'relu'
        else:
            if callable(activation):
                return activation
            print(f"Warning: Unsupported activation type {type(activation)}. Using 'relu' as default.")
            return 'relu'
    
    def _get_weight_initializer(self, initializer_name):
        """Get weight initializer based on name"""
        if initializer_name is None:
            return 'he_normal'
        
        initializer_name = initializer_name.lower()
        
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
    
    def _build_layers(self):
        """Build the classification head layers"""
        # This list will hold the sequence of layers for the main body of the head.
        # Keras automatically tracks layers held in lists that are attributes of a Layer.
        self.fc_sequence = []
        
        # Global Average Pooling layer (optional)
        if self.use_global_pooling:
            # Assigning the layer as a direct attribute also ensures it's tracked.
            self.global_pool = GlobalAveragePooling2D(name=f"{self.name}_global_pool")
        else:
            self.global_pool = None

        # Get configuration parameters
        fc_units = self.fc_config["units"]
        fc_activation = self.fc_config.get("activation", "relu")
        dropout_rate = self.fc_config.get("dropout", 0.0)
        use_batch_norm = self.fc_config.get("use_batch_norm", False)
        kernel_init = self._get_weight_initializer(self.fc_config.get("kernel_initializer", "he_normal"))
        bias_init = self.fc_config.get("bias_initializer", "zeros")
        
        # Build fully connected layers
        for i, units in enumerate(fc_units):
            # Dense layer
            self.fc_sequence.append(Dense(
                units,
                activation=None,  # Activation applied separately for clarity and BN placement
                kernel_initializer=kernel_init,
                bias_initializer=bias_init,
                name=f"{self.name}_fc_{i}"
            ))
            
            # Optional batch normalization
            if use_batch_norm:
                self.fc_sequence.append(BatchNormalization(
                    momentum=0.99,
                    epsilon=1e-3,
                    name=f"{self.name}_bn_{i}"
                ))
            
            # Activation
            # self._get_activation_function can return a Layer instance (e.g., PReLU) or a string
            activation_layer = self._get_activation_function(fc_activation)
            self.fc_sequence.append(activation_layer)
            
            # Optional dropout
            if dropout_rate > 0.0:
                self.fc_sequence.append(Dropout(
                    dropout_rate,
                    name=f"{self.name}_dropout_{i}"
                ))
        
        # Final output layer
        self.output_layer = Dense(
            self.num_classes,
            activation=self.output_activation,
            kernel_initializer=kernel_init,
            bias_initializer=bias_init,
            name=f"{self.name}_output"
        )
        
        print(f"✓ ClassificationHead '{self.name}' built:")
        print(f"  - Classes: {self.num_classes}")
        print(f"  - FC layers: {self.fc_config['units']}")
        print(f"  - Dropout: {self.fc_config.get('dropout', 0.0)}")
        print(f"  - Output activation: {self.output_activation}")
        print(f"  - Use global pooling: {self.use_global_pooling}")

    def call(self, inputs, training=None):
        """
        Forward pass through the classification head
        
        Args:
            inputs: Feature tensor from FeatureExtractor of shape
                   (batch_size, height, width, channels) or
                   (batch_size, features) if already pooled
            training: Boolean indicating training mode
        
        Returns:
            Output tensor of shape (batch_size, num_classes)
        """
        x = inputs
        
        if self.global_pool:
            x = self.global_pool(x)
            
        # Apply the sequence of FC layers
        for layer in self.fc_sequence:
            # Pass `training` argument to layers that support it
            if isinstance(layer, (BatchNormalization, Dropout)):
                x = layer(x, training=training)
            # Handle callable layers (e.g., PReLU, LeakyReLU instances)
            elif callable(layer):
                x = layer(x)
            # Handle string activations
            else:
                x = tf.keras.activations.get(layer)(x)
        
        # Apply the final output layer
        x = self.output_layer(x)
        
        return x
    
    def get_config(self):
        """Get configuration for serialization"""
        config = super(ClassificationHead, self).get_config()
        config.update({
            'num_classes': self.num_classes,
            'fc_config': self.fc_config,
            'output_activation': self.output_activation,
            'use_global_pooling': self.use_global_pooling
        })
        return config
    
    @classmethod
    def from_config(cls, config):
        """Create ClassificationHead from configuration"""
        return cls(**config)


def create_heads_from_hierarchy_info(
    hierarchy_info: Optional[Dict[str, Dict[str, Any]]] = None,
    head_configs: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, ClassificationHead]:
    """
    Create classification heads automatically from neutrophil hierarchy information
    
    This helper function creates the appropriate classification heads based on the
    neutrophil hierarchy, with configurable FC architectures for each head.
    
    Args:
        hierarchy_info (dict, optional): Output from get_head_info(). If None,
                                       uses default neutrophil hierarchy
        head_configs (dict, optional): Configuration for each head:
            {
                "coarse": {
                    "fc_config": {...},
                    "output_activation": "softmax"
                },
                "stage": {
                    "fc_config": {...},
                    "output_activation": "softmax"
                }
            }
    
    Returns:
        Dictionary mapping head names to ClassificationHead instances
    
    Example:
        >>> heads = create_heads_from_hierarchy_info()
        >>> coarse_head = heads["coarse"]  # 2 classes
        >>> stage_head = heads["stage"]    # 4 classes
        
        >>> # With custom configuration
        >>> configs = {
        ...     "coarse": {
        ...         "fc_config": {"units": [128], "dropout": 0.3},
        ...         "output_activation": "softmax"
        ...     },
        ...     "stage": {
        ...         "fc_config": {"units": [256, 128], "dropout": 0.3},
        ...         "output_activation": "softmax"
        ...     }
        ... }
        >>> heads = create_heads_from_hierarchy_info(head_configs=configs)
    """
    # Use default neutrophil hierarchy if not provided
    if hierarchy_info is None:
        hierarchy_info = get_head_info(NEUTROPHIL_HIERARCHY)
    
    # Default head configurations
    default_head_configs = {
        "coarse": {
            "fc_config": {
                "units": [128],
                "activation": "relu",
                "dropout": 0.3,
                "use_batch_norm": False,
                "kernel_initializer": "he_normal",
                "bias_initializer": "zeros"
            },
            "output_activation": "softmax"
        },
        "stage": {
            "fc_config": {
                "units": [256, 128],
                "activation": "relu", 
                "dropout": 0.3,
                "use_batch_norm": False,
                "kernel_initializer": "he_normal",
                "bias_initializer": "zeros"
            },
            "output_activation": "softmax"
        }
    }
    
    # Merge user configs with defaults
    if head_configs is None:
        head_configs = default_head_configs
    else:
        for head_name in default_head_configs:
            if head_name not in head_configs:
                head_configs[head_name] = default_head_configs[head_name]
            else:
                # Merge fc_config if provided
                if "fc_config" not in head_configs[head_name]:
                    head_configs[head_name]["fc_config"] = default_head_configs[head_name]["fc_config"]
                else:
                    # Merge individual fc_config parameters
                    default_fc = default_head_configs[head_name]["fc_config"]
                    user_fc = head_configs[head_name]["fc_config"]
                    for key, value in default_fc.items():
                        if key not in user_fc:
                            user_fc[key] = value
                
                # Set default output activation if not provided
                if "output_activation" not in head_configs[head_name]:
                    head_configs[head_name]["output_activation"] = default_head_configs[head_name]["output_activation"]
    
    # Create heads
    heads = {}
    for head_name, head_info in hierarchy_info.items():
        num_classes = head_info["num_classes"]
        config = head_configs.get(head_name, default_head_configs.get(head_name, {}))
        
        head = ClassificationHead(
            num_classes=num_classes,
            name=head_name,
            fc_config=config.get("fc_config", {}),
            output_activation=config.get("output_activation", "softmax")
        )
        heads[head_name] = head
    
    print(f"✓ Created {len(heads)} classification heads from hierarchy:")
    for head_name, head in heads.items():
        head_info = hierarchy_info[head_name]
        print(f"  - {head_name}: {head_info['num_classes']} classes at level {head_info['level']}")
    
    return heads


def create_heads_from_toml_config(config: Dict[str, Any]) -> Dict[str, ClassificationHead]:
    """
    Create classification heads from TOML configuration
    
    This function creates heads based on a TOML configuration structure that
    follows the hierarchical model configuration format.
    
    Args:
        config (dict): Configuration dictionary with hierarchical head definitions:
            {
                "model": {
                    "hierarchical": {
                        "heads": {
                            "coarse": {
                                "num_classes": 2,
                                "fc_units": [128],
                                "fc_activation": "relu",
                                "dropout": 0.3,
                                "output_activation": "softmax"
                            },
                            "stage": {
                                "num_classes": 4,
                                "fc_units": [256, 128],
                                "fc_activation": "relu",
                                "dropout": 0.3,
                                "output_activation": "softmax"
                            }
                        }
                    }
                }
            }
    
    Returns:
        Dictionary mapping head names to ClassificationHead instances
    
    Example:
        >>> import toml
        >>> config = toml.load('hierarchical_config.toml')
        >>> heads = create_heads_from_toml_config(config)
    """
    # Extract hierarchical head configurations
    try:
        heads_config = config["model"]["hierarchical"]["heads"]
    except KeyError as e:
        raise ValueError(f"Invalid configuration structure: missing key {e}")
    
    heads = {}
    for head_name, head_config in heads_config.items():
        # Extract parameters from TOML format
        num_classes = head_config.get("num_classes")
        if num_classes is None:
            raise ValueError(f"Missing 'num_classes' for head '{head_name}'")
        
        # Build fc_config from TOML parameters
        fc_config = {
            "units": head_config.get("fc_units", [128]),
            "activation": head_config.get("fc_activation", "relu"),
            "dropout": head_config.get("dropout", 0.3),
            "use_batch_norm": head_config.get("use_batch_norm", False),
            "kernel_initializer": head_config.get("kernel_initializer", "he_normal"),
            "bias_initializer": head_config.get("bias_initializer", "zeros")
        }
        
        output_activation = head_config.get("output_activation", "softmax")
        
        # Create head
        head = ClassificationHead(
            num_classes=num_classes,
            name=head_name,
            fc_config=fc_config,
            output_activation=output_activation
        )
        heads[head_name] = head
    
    print(f"✓ Created {len(heads)} classification heads from TOML config:")
    for head_name, head in heads.items():
        print(f"  - {head_name}: {head.num_classes} classes")
    
    return heads


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ClassificationHead",
    "create_heads_from_hierarchy_info", 
    "create_heads_from_toml_config"
]