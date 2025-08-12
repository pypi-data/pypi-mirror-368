#!/usr/bin/env python3
"""
Hierarchical Model Component for Neutrophil Maturation Classification

This module implements a unified hierarchical model that combines the FeatureExtractor
with multiple ClassificationHeads to provide hierarchical classification outputs for
neutrophil maturation stages.

The HierarchicalModel serves as the main coordination point between feature extraction
and multiple classification heads, supporting:
- Flexible head configuration from TOML config
- Model compilation with multiple outputs and appropriate loss functions
- Both single-output (backward compatibility) and multi-output modes
- Training, evaluation, and inference with multiple outputs
- Configurable loss weights for different output heads

Architecture Overview:
---------------------
Input -> FeatureExtractor -> Multiple ClassificationHeads -> Multiple Outputs

The model supports hierarchical classification where:
- Coarse head: Early/Late classification (2 classes)
- Stage head: Fine-grained stage classification (4 classes: M, MM, BN, SN)
- Additional heads can be easily added through configuration
"""

import tensorflow as tf
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam, SGD, RMSprop
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np

from .feature_extractor import FeatureExtractor, create_feature_extractor_from_config
from .heads import ClassificationHead, create_heads_from_toml_config, create_heads_from_hierarchy_info
from ..metrics.loss_functions import get_loss_function, LOSS_FUNCTIONS
from ..loader.hierarchical_labels import NEUTROPHIL_HIERARCHY, get_head_info


class HierarchicalModel(tf.keras.Model):
    """
    Unified Hierarchical Model for Neutrophil Maturation Classification
    
    This model combines a shared FeatureExtractor with multiple ClassificationHeads
    to provide hierarchical classification outputs. It supports flexible configuration
    from TOML files and provides methods for training, evaluation, and inference.
    
    The model can operate in two modes:
    1. Multi-output mode: Produces outputs for all configured heads
    2. Single-output mode: Backward compatibility mode producing a single output
    
    Key Features:
    - Shared feature extraction with multiple specialized heads
    - Configurable loss functions and weights for each head
    - TOML configuration support for easy experimentation
    - Backward compatibility with existing single-output models
    - Support for both training and inference workflows
    """
    
    def __init__(
        self,
        feature_extractor: Optional[FeatureExtractor] = None,
        heads: Optional[Dict[str, ClassificationHead]] = None,
        input_shape: Optional[Tuple[int, int, int]] = None,
        config: Optional[Dict[str, Any]] = None,
        name: str = 'hierarchical_model',
        **kwargs
    ):
        """
        Initialize the HierarchicalModel
        
        Args:
            feature_extractor (FeatureExtractor, optional): Pre-configured feature extractor.
                                                          If None, will be created from config
            heads (dict, optional): Dictionary mapping head names to ClassificationHead instances.
                                   If None, will be created from config
            input_shape (tuple, optional): Input shape (height, width, channels)
            config (dict, optional): Configuration dictionary containing model parameters
            name (str): Name of the model
            **kwargs: Additional keyword arguments for tf.keras.Model
        """
        super(HierarchicalModel, self).__init__(name=name, **kwargs)
        
        # Store configuration
        self.config = config or {}
        self.input_shape_config = input_shape
        
        # Validate and set defaults
        self._validate_and_set_defaults()
        
        # Create or use provided components
        self.feature_extractor = feature_extractor or self._create_feature_extractor()
        self.heads = heads or self._create_heads()
        
        # Configuration parameters
        self.multi_output_mode = len(self.heads) > 1
        self.head_names = list(self.heads.keys())
        
        # Model compilation parameters (will be set during compile)
        self.loss_functions = {}
        self.loss_weights = {}
        self.metrics_dict = {}
        
        print(f"✓ HierarchicalModel '{self.name}' initialized:")
        print(f"  - Multi-output mode: {self.multi_output_mode}")
        print(f"  - Heads: {self.head_names}")
        print(f"  - Input shape: {self.input_shape_config}")
    
    def _validate_and_set_defaults(self):
        """Validate configuration and set defaults"""
        # Set default input shape if not provided
        if self.input_shape_config is None:
            self.input_shape_config = (96, 96, 3)  # Default from existing configs
        
        # Ensure hierarchical configuration exists
        if 'hierarchical' not in self.config:
            self.config['hierarchical'] = {}
        
        # Set default compilation parameters
        hierarchical_config = self.config['hierarchical']
        
        if 'loss_functions' not in hierarchical_config:
            hierarchical_config['loss_functions'] = {
                'coarse': 'categorical_crossentropy',
                'stage': 'categorical_crossentropy'
            }
        
        if 'loss_weights' not in hierarchical_config:
            hierarchical_config['loss_weights'] = {
                'coarse': 1.0,
                'stage': 1.0
            }
        
        if 'metrics' not in hierarchical_config:
            hierarchical_config['metrics'] = ['accuracy', 'precision', 'recall']
    
    def _create_feature_extractor(self) -> FeatureExtractor:
        """Create feature extractor from configuration"""
        if 'feature_extractor' in self.config:
            feature_config = self.config['feature_extractor']
        else:
            # Use model config for backward compatibility
            feature_config = self.config
        
        return create_feature_extractor_from_config(
            feature_config,
            input_shape=self.input_shape_config
        )
    
    def _create_heads(self) -> Dict[str, ClassificationHead]:
        """Create classification heads from configuration"""
        hierarchical_config = self.config.get('hierarchical', {})
        
        if 'heads' in hierarchical_config:
            # Create heads from TOML configuration
            full_config = {'model': {'hierarchical': hierarchical_config}}
            return create_heads_from_toml_config(full_config)
        else:
            # Create default heads from hierarchy info
            return create_heads_from_hierarchy_info()
    
    def call(self, inputs, training=None):
        """
        Forward pass through the hierarchical model
        
        Args:
            inputs: Input tensor of shape (batch_size, height, width, channels)
            training: Boolean indicating training mode
        
        Returns:
            If multi-output mode: Dictionary mapping head names to output tensors
            If single-output mode: Single output tensor (for backward compatibility)
        """
        # Extract features using the shared feature extractor
        features = self.feature_extractor(inputs, training=training)
        
        # Apply classification heads
        outputs = {}
        for head_name, head in self.heads.items():
            outputs[head_name] = head(features, training=training)
        
        if self.multi_output_mode:
            return outputs
        else:
            # Backward compatibility: return single output
            # Use the first head or a specified primary head
            primary_head = self.head_names[0]
            return outputs[primary_head]
    
    def build_functional_model(self, input_shape: Optional[Tuple[int, int, int]] = None) -> Model:
        """
        Build a functional Keras model from the hierarchical model
        
        Args:
            input_shape: Input shape (height, width, channels).
                        If None, uses self.input_shape_config
        
        Returns:
            tf.keras.Model: Functional model with appropriate inputs and outputs
        """
        if input_shape is None:
            input_shape = self.input_shape_config
        
        # Create input layer
        inputs = Input(shape=input_shape, name='hierarchical_model_input')
        
        # Apply the hierarchical model
        outputs = self(inputs)
        
        # Create functional model
        if self.multi_output_mode:
            # Multi-output model
            model = Model(
                inputs=inputs,
                outputs=[outputs[head_name] for head_name in self.head_names],
                name=f"{self.name}_functional"
            )
        else:
            # Single-output model for backward compatibility
            model = Model(
                inputs=inputs,
                outputs=outputs,
                name=f"{self.name}_functional"
            )
        
        return model
    
    def compile_model(
        self,
        optimizer: Union[str, tf.keras.optimizers.Optimizer] = 'adam',
        loss_functions: Optional[Dict[str, Union[str, tf.keras.losses.Loss]]] = None,
        loss_weights: Optional[Dict[str, float]] = None,
        metrics: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Compile the hierarchical model with appropriate loss functions and metrics
        
        Args:
            optimizer: Optimizer to use (string name or optimizer instance)
            loss_functions: Dictionary mapping head names to loss functions.
                          If None, uses config defaults
            loss_weights: Dictionary mapping head names to loss weights.
                         If None, uses config defaults
            metrics: List of metrics to track. If None, uses config defaults
            **kwargs: Additional arguments for model compilation
        """
        # Get configuration
        hierarchical_config = self.config.get('hierarchical', {})
        
        # Set loss functions
        if loss_functions is None:
            loss_functions = hierarchical_config.get('loss_functions', {})
        
        # Set loss weights
        if loss_weights is None:
            loss_weights = hierarchical_config.get('loss_weights', {})
        
        # Set metrics
        if metrics is None:
            metrics = hierarchical_config.get('metrics', ['accuracy'])
        
        # Store compilation parameters
        self.loss_functions = loss_functions
        self.loss_weights = loss_weights
        self.metrics_dict = {head_name: metrics for head_name in self.head_names}
        
        # Build functional model for compilation
        functional_model = self.build_functional_model()
        
        if self.multi_output_mode:
            # Multi-output compilation
            compiled_losses = {}
            compiled_loss_weights = {}
            compiled_metrics = {}
            
            for head_name in self.head_names:
                # Get loss function
                loss_name = loss_functions.get(head_name, 'categorical_crossentropy')
                if isinstance(loss_name, str) and loss_name in LOSS_FUNCTIONS:
                    compiled_losses[head_name] = get_loss_function(loss_name)
                else:
                    compiled_losses[head_name] = loss_name
                
                # Get loss weight
                compiled_loss_weights[head_name] = loss_weights.get(head_name, 1.0)
                
                # Set metrics for this head
                compiled_metrics[head_name] = metrics
            
            functional_model.compile(
                optimizer=optimizer,
                loss=compiled_losses,
                loss_weights=compiled_loss_weights,
                metrics=compiled_metrics,
                **kwargs
            )
        else:
            # Single-output compilation for backward compatibility
            primary_head = self.head_names[0]
            loss_name = loss_functions.get(primary_head, 'categorical_crossentropy')
            
            if isinstance(loss_name, str) and loss_name in LOSS_FUNCTIONS:
                compiled_loss = get_loss_function(loss_name)
            else:
                compiled_loss = loss_name
            
            functional_model.compile(
                optimizer=optimizer,
                loss=compiled_loss,
                metrics=metrics,
                **kwargs
            )
        
        # Store the compiled functional model
        self.compiled_model = functional_model
        
        print(f"✓ HierarchicalModel compiled:")
        print(f"  - Multi-output mode: {self.multi_output_mode}")
        if self.multi_output_mode:
            print(f"  - Loss functions: {self.loss_functions}")
            print(f"  - Loss weights: {self.loss_weights}")
        print(f"  - Optimizer: {optimizer}")
        print(f"  - Metrics: {metrics}")
        
        return functional_model
    
    def fit(
        self,
        x=None,
        y=None,
        batch_size=None,
        epochs=1,
        verbose='auto',
        callbacks=None,
        validation_split=0.0,
        validation_data=None,
        shuffle=True,
        class_weight=None,
        sample_weight=None,
        initial_epoch=0,
        steps_per_epoch=None,
        validation_steps=None,
        validation_batch_size=None,
        validation_freq=1,
        max_queue_size=10,
        workers=1,
        use_multiprocessing=False
    ):
        """
        Train the hierarchical model
        
        This method handles both single-output and multi-output training,
        automatically adapting the labels format as needed.
        
        Args:
            x: Input data
            y: Target data. Can be:
               - Single array for single-output mode
               - Dictionary mapping head names to target arrays for multi-output mode
               - List of target arrays (ordered by head_names) for multi-output mode
            **kwargs: Additional arguments for model.fit()
        
        Returns:
            History object containing training metrics
        """
        if not hasattr(self, 'compiled_model'):
            raise ValueError("Model must be compiled before training. Call compile_model() first.")
        
        # Prepare target data for multi-output training
        if self.multi_output_mode and not isinstance(y, dict):
            if isinstance(y, (list, tuple)):
                # Convert list to dictionary
                if len(y) != len(self.head_names):
                    raise ValueError(f"Expected {len(self.head_names)} target arrays, got {len(y)}")
                y = {head_name: y[i] for i, head_name in enumerate(self.head_names)}
            else:
                # Single array - need to duplicate for all heads
                print("Warning: Single target array provided for multi-output model. Duplicating for all heads.")
                y = {head_name: y for head_name in self.head_names}
        
        return self.compiled_model.fit(
            x=x,
            y=y,
            batch_size=batch_size,
            epochs=epochs,
            verbose=verbose,
            callbacks=callbacks,
            validation_split=validation_split,
            validation_data=validation_data,
            shuffle=shuffle,
            class_weight=class_weight,
            sample_weight=sample_weight,
            initial_epoch=initial_epoch,
            steps_per_epoch=steps_per_epoch,
            validation_steps=validation_steps,
            validation_batch_size=validation_batch_size,
            validation_freq=validation_freq,
            max_queue_size=max_queue_size,
            workers=workers,
            use_multiprocessing=use_multiprocessing
        )
    
    def evaluate(
        self,
        x=None,
        y=None,
        batch_size=None,
        verbose='auto',
        sample_weight=None,
        steps=None,
        callbacks=None,
        max_queue_size=10,
        workers=1,
        use_multiprocessing=False,
        return_dict=False
    ):
        """
        Evaluate the hierarchical model
        
        Args:
            x: Input data
            y: Target data (same format as fit method)
            **kwargs: Additional arguments for model.evaluate()
        
        Returns:
            Evaluation metrics
        """
        if not hasattr(self, 'compiled_model'):
            raise ValueError("Model must be compiled before evaluation. Call compile_model() first.")
        
        # Prepare target data for multi-output evaluation
        if self.multi_output_mode and not isinstance(y, dict):
            if isinstance(y, (list, tuple)):
                if len(y) != len(self.head_names):
                    raise ValueError(f"Expected {len(self.head_names)} target arrays, got {len(y)}")
                y = {head_name: y[i] for i, head_name in enumerate(self.head_names)}
            else:
                y = {head_name: y for head_name in self.head_names}
        
        return self.compiled_model.evaluate(
            x=x,
            y=y,
            batch_size=batch_size,
            verbose=verbose,
            sample_weight=sample_weight,
            steps=steps,
            callbacks=callbacks,
            max_queue_size=max_queue_size,
            workers=workers,
            use_multiprocessing=use_multiprocessing,
            return_dict=return_dict
        )
    
    def predict(
        self,
        x,
        batch_size=None,
        verbose='auto',
        steps=None,
        callbacks=None,
        max_queue_size=10,
        workers=1,
        use_multiprocessing=False
    ):
        """
        Generate predictions from the hierarchical model
        
        Args:
            x: Input data
            **kwargs: Additional arguments for model.predict()
        
        Returns:
            If multi-output mode: Dictionary mapping head names to prediction arrays
            If single-output mode: Single prediction array
        """
        if hasattr(self, 'compiled_model'):
            predictions = self.compiled_model.predict(
                x=x,
                batch_size=batch_size,
                verbose=verbose,
                steps=steps,
                callbacks=callbacks,
                max_queue_size=max_queue_size,
                workers=workers,
                use_multiprocessing=use_multiprocessing
            )
        else:
            # Use the model directly if not compiled
            predictions = self(x, training=False)
        
        if self.multi_output_mode:
            if isinstance(predictions, (list, tuple)):
                # Convert list predictions to dictionary
                return {head_name: predictions[i] for i, head_name in enumerate(self.head_names)}
            elif isinstance(predictions, dict):
                return predictions
            else:
                # Single output returned - wrap in dict
                return {self.head_names[0]: predictions}
        else:
            if isinstance(predictions, (list, tuple)):
                return predictions[0]
            elif isinstance(predictions, dict):
                return predictions[self.head_names[0]]
            else:
                return predictions
    
    def get_feature_shape(self, input_shape: Optional[Tuple[int, int, int]] = None) -> Tuple[int, ...]:
        """
        Get the shape of features produced by the feature extractor
        
        Args:
            input_shape: Input shape (height, width, channels).
                        If None, uses self.input_shape_config
        
        Returns:
            Feature shape tuple
        """
        if input_shape is None:
            input_shape = self.input_shape_config
        
        return self.feature_extractor.get_feature_shape(input_shape)
    
    def summary(self, input_shape: Optional[Tuple[int, int, int]] = None):
        """
        Print a summary of the hierarchical model
        
        Args:
            input_shape: Input shape for building the model summary
        """
        if input_shape is None:
            input_shape = self.input_shape_config
        
        print(f"\nHierarchicalModel Summary: {self.name}")
        print("=" * 60)
        print(f"Input shape: {input_shape}")
        print(f"Multi-output mode: {self.multi_output_mode}")
        print(f"Number of heads: {len(self.heads)}")
        
        # Feature extractor summary
        print("\nFeature Extractor:")
        print("-" * 40)
        feature_shape = self.get_feature_shape(input_shape)
        print(f"Output shape: {feature_shape}")
        
        # Heads summary
        print("\nClassification Heads:")
        print("-" * 40)
        for head_name, head in self.heads.items():
            print(f"{head_name}: {head.num_classes} classes")
        
        # Build and show functional model summary if possible
        try:
            functional_model = self.build_functional_model(input_shape)
            print("\nFunctional Model Summary:")
            print("-" * 40)
            functional_model.summary()
        except Exception as e:
            print(f"\nCould not build functional model summary: {e}")
    
    def get_config(self):
        """Get configuration for serialization"""
        config = super(HierarchicalModel, self).get_config()
        config.update({
            'config': self.config,
            'input_shape_config': self.input_shape_config,
            'multi_output_mode': self.multi_output_mode,
            'head_names': self.head_names
        })
        return config
    
    @classmethod
    def from_config(cls, config):
        """Create HierarchicalModel from configuration"""
        # Extract model-specific config
        model_config = config.pop('config', {})
        input_shape = config.pop('input_shape_config', None)
        
        return cls(
            config=model_config,
            input_shape=input_shape,
            **config
        )


def create_hierarchical_model_from_config(
    config: Dict[str, Any],
    input_shape: Optional[Tuple[int, int, int]] = None
) -> HierarchicalModel:
    """
    Factory function to create a HierarchicalModel from TOML configuration
    
    This function provides a convenient way to create a complete hierarchical model
    from TOML configuration files used in the existing codebase.
    
    Args:
        config (dict): Configuration dictionary with 'model' section containing:
            - Feature extractor configuration (conv_blocks, etc.)
            - Hierarchical heads configuration
            - Loss functions and weights
        input_shape (tuple, optional): Input shape (height, width, channels)
    
    Returns:
        HierarchicalModel: Configured hierarchical model instance
    
    Example:
        >>> import toml
        >>> config = toml.load('config/hierarchical_resnet_2d.toml')
        >>> model = create_hierarchical_model_from_config(
        ...     config, input_shape=(96, 96, 3)
        ... )
        >>> model.compile_model(optimizer='adam')
        >>> model.summary()
    """
    # Extract model configuration
    model_config = config.get('model', {})
    
    # Create the hierarchical model
    hierarchical_model = HierarchicalModel(
        config=model_config,
        input_shape=input_shape
    )
    
    print(f"✓ Created HierarchicalModel from TOML configuration")
    print(f"  - Input shape: {input_shape}")
    print(f"  - Heads: {hierarchical_model.head_names}")
    
    return hierarchical_model


def create_compiled_hierarchical_model(
    config: Dict[str, Any],
    input_shape: Optional[Tuple[int, int, int]] = None,
    optimizer_config: Optional[Dict[str, Any]] = None
) -> HierarchicalModel:
    """
    Create and compile a hierarchical model from configuration
    
    This is a convenience function that creates and compiles the model in one step,
    using optimizer configuration from the config file.
    
    Args:
        config (dict): Full configuration dictionary including model and optimizer sections
        input_shape (tuple, optional): Input shape (height, width, channels)
        optimizer_config (dict, optional): Optimizer configuration. If None, uses config['optimizer']
    
    Returns:
        HierarchicalModel: Compiled hierarchical model ready for training
    
    Example:
        >>> import toml
        >>> config = toml.load('config/hierarchical_resnet_2d.toml')
        >>> model = create_compiled_hierarchical_model(
        ...     config, input_shape=(96, 96, 3)
        ... )
        >>> # Model is ready for training
        >>> history = model.fit(x_train, y_train, epochs=10)
    """
    # Create the model
    model = create_hierarchical_model_from_config(config, input_shape)
    
    # Get optimizer configuration
    if optimizer_config is None:
        optimizer_config = config.get('optimizer', {})
    
    # Create optimizer
    optimizer_name = optimizer_config.get('optimizer_name', 'adam').lower()
    learning_rate = optimizer_config.get('learning_rate', 1e-4)
    
    if optimizer_name == 'adam':
        adam_config = optimizer_config.get('adam', {})
        optimizer = Adam(
            learning_rate=learning_rate,
            beta_1=adam_config.get('beta_1', 0.9),
            beta_2=adam_config.get('beta_2', 0.999),
            epsilon=adam_config.get('epsilon', 1e-7),
            amsgrad=adam_config.get('amsgrad', False)
        )
    elif optimizer_name == 'sgd':
        sgd_config = optimizer_config.get('sgd', {})
        optimizer = SGD(
            learning_rate=learning_rate,
            momentum=sgd_config.get('momentum', 0.9),
            nesterov=sgd_config.get('nesterov', False)
        )
    elif optimizer_name == 'rmsprop':
        rmsprop_config = optimizer_config.get('rmsprop', {})
        optimizer = RMSprop(
            learning_rate=learning_rate,
            rho=rmsprop_config.get('rho', 0.9),
            momentum=rmsprop_config.get('momentum', 0.0),
            epsilon=rmsprop_config.get('epsilon', 1e-7),
            centered=rmsprop_config.get('centered', False)
        )
    else:
        raise ValueError(f"Unknown optimizer: {optimizer_name}")
    
    # Get metrics from optimizer config or use defaults
    metrics = optimizer_config.get('metrics', ['accuracy'])
    
    # Compile the model
    model.compile_model(optimizer=optimizer, metrics=metrics)
    
    print(f"✓ Created and compiled HierarchicalModel")
    print(f"  - Optimizer: {optimizer_name} (lr={learning_rate})")
    print(f"  - Metrics: {metrics}")
    
    return model


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "HierarchicalModel",
    "create_hierarchical_model_from_config",
    "create_compiled_hierarchical_model"
]