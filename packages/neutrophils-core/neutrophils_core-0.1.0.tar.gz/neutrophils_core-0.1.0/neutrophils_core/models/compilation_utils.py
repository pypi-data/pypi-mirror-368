"""Model compilation utilities."""

import tensorflow as tf
from tensorflow import keras
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

from ..metrics.loss_functions import STANDARD_LOSS_FUNCTIONS, ORDINAL_LOSS_FUNCTIONS
from ..metrics.classification_metrics import get_metrics

# Import loss utility functions from trainer_2d (temporary until fully migrated)
import sys
import os
trainer_2d_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'trainer_2d')
if trainer_2d_path not in sys.path:
    sys.path.append(trainer_2d_path)

try:
    from loss_utils import get_configured_loss_function, print_loss_function_summary
except ImportError:
    print("Warning: Could not import loss_utils. Some functionality may be limited.")
    def get_configured_loss_function(loss_type, training_mode, class_weights, optimizer_params):
        return loss_type
    def print_loss_function_summary(loss_type, training_mode, class_weights, optimizer_params):
        print(f"Loss: {loss_type}, Mode: {training_mode}")


def compile_model(model,
                  optimizer_name='adam',
                  optimizer_params=None,
                  loss_type='categorical_crossentropy',
                  training_labels=None,
                  training_mode='standard',
                  class_weights_strategy="none"):
    """
    Compile the model with optimizer and loss function
    
    Args:
        model: Keras model to compile
        optimizer_name: Name of the optimizer to use
        optimizer_params: Dictionary of parameters for the optimizer
        loss_type: Type of loss function to use
        training_labels: Training labels for calculating class weights
        training_mode: Training mode ('standard' or 'ordinal')
        class_weights_strategy: Strategy for handling class weights
    
    Returns:
        Compiled model
    """
    if optimizer_params is None:
        optimizer_params = {}

    # Setup learning rate schedule
    lr_schedule = keras.optimizers.schedules.ExponentialDecay(
        initial_learning_rate=optimizer_params.get('learning_rate', 1e-4),
        decay_steps=optimizer_params.get('decay_steps', 100),
        decay_rate=optimizer_params.get('decay_rate', 0.99)
    )

    optimizer_name = optimizer_name.lower()
    if optimizer_name == 'adam':
        optimizer = keras.optimizers.Adam(
            learning_rate=lr_schedule,
            beta_1=optimizer_params.get('beta_1', 0.9),
            beta_2=optimizer_params.get('beta_2', 0.999),
            epsilon=optimizer_params.get('epsilon', 1e-7),
            amsgrad=optimizer_params.get('amsgrad', False)
        )
    elif optimizer_name == 'sgd':
        optimizer = keras.optimizers.SGD(
            learning_rate=lr_schedule,
            momentum=optimizer_params.get('momentum', 0.0),
            nesterov=optimizer_params.get('nesterov', False)
        )
    elif optimizer_name == 'rmsprop':
        optimizer = keras.optimizers.RMSprop(
            learning_rate=lr_schedule,
            rho=optimizer_params.get('rho', 0.9),
            momentum=optimizer_params.get('momentum', 0.0),
            epsilon=optimizer_params.get('epsilon', 1e-7),
            centered=optimizer_params.get('centered', False)
        )
    else:
        print(f"Warning: Unknown optimizer '{optimizer_name}'. Defaulting to Adam.")
        optimizer = keras.optimizers.Adam(learning_rate=lr_schedule)
    
    # Automatic detection and setup for ordinal mode
    is_ordinal_mode = training_mode == 'ordinal'
    
    # Setup metrics based on training mode
    if is_ordinal_mode:
        metrics = get_metrics(training_mode='ordinal')
        print(f"Ordinal mode detected. Using ordinal-specific metrics.")
    else:
        metrics = get_metrics(training_mode='standard')
        print(f"Standard mode detected. Using standard metrics.")
    
    # Calculate class weights based on strategy
    class_weights = None
    if class_weights_strategy == "auto":
        if training_labels is not None:
            class_weights = compute_class_weight(
                class_weight='balanced',
                classes=np.unique(training_labels),
                y=training_labels
            )
            print(f"Auto-calculated class weights: {class_weights}")
        else:
            print("Warning: class_weights_strategy='auto' but no training labels provided.")
            class_weights = None
    elif isinstance(class_weights_strategy, (list, tuple)):
        class_weights = np.array(class_weights_strategy)
        print(f"Using manual class weights: {class_weights}")
    elif class_weights_strategy == "none":
        class_weights = None
        print("No class weights applied")
    else:
        print(f"Warning: Unknown class_weights_strategy '{class_weights_strategy}'.")
        class_weights = None

    # Check if this is a multi-output model
    is_multi_output = hasattr(model, 'output_names') and len(model.output_names) > 1
    
    if is_multi_output:
        print("✓ Detected multi-output model - configuring hierarchical/staged losses")
        
        # Multi-output model compilation
        if 'hierarchical' in model.name:
            hierarchical_config = getattr(model, 'hierarchical_config', {})
            alpha = hierarchical_config.get('alpha', 0.3)
            beta = hierarchical_config.get('beta', 0.7)
            penalty_weight = hierarchical_config.get('penalty_weight', 0.1)
            
            print(f"Setting up hierarchical loss with alpha={alpha}, beta={beta}, penalty_weight={penalty_weight}")
            print("Note: Hierarchical contradiction penalty will be implemented as a custom metric")
            
            # For now, use the same approach as staged models
            # TODO: Add hierarchical constraint as a custom metric or callback
            stage_loss = get_configured_loss_function(
                loss_type='binary_crossentropy',
                training_mode=training_mode,
                class_weights=None,
                optimizer_params=optimizer_params
            )
            
            subclass_loss = get_configured_loss_function(
                loss_type=loss_type,
                training_mode=training_mode,
                class_weights=class_weights,
                optimizer_params=optimizer_params
            )
            
            losses = {'stage': stage_loss, 'subclass': subclass_loss}
            loss_weights = {'stage': alpha, 'subclass': beta}
            
            metrics_dict = {'stage': ['accuracy'], 'subclass': metrics}
            
            model.compile(
                optimizer=optimizer,
                loss=losses,
                loss_weights=loss_weights,
                metrics=metrics_dict
            )
            
        elif 'staged' in model.name:
            staged_config = getattr(model, 'staged_config', {})
            alpha = staged_config.get('alpha', 0.3)
            beta = staged_config.get('beta', 0.7)
            
            print(f"Setting up staged loss with alpha={alpha}, beta={beta}")
            
            stage_loss = get_configured_loss_function(
                loss_type='binary_crossentropy',
                training_mode=training_mode,
                class_weights=None,
                optimizer_params=optimizer_params
            )
            
            subclass_loss = get_configured_loss_function(
                loss_type=loss_type,
                training_mode=training_mode,
                class_weights=class_weights,
                optimizer_params=optimizer_params
            )
            
            losses = {'stage': stage_loss, 'subclass': subclass_loss}
            loss_weights = {'stage': alpha, 'subclass': beta}
            
            metrics_dict = {'stage': ['accuracy'], 'subclass': metrics}
            
            model.compile(
                optimizer=optimizer,
                loss=losses,
                loss_weights=loss_weights,
                metrics=metrics_dict
            )
        
    else:
        # Single-output model compilation
        print("✓ Detected single-output model - using standard compilation")
        
        print_loss_function_summary(loss_type, training_mode, class_weights, optimizer_params)
        
        loss = get_configured_loss_function(
            loss_type=loss_type,
            training_mode=training_mode,
            class_weights=class_weights,
            optimizer_params=optimizer_params
        )
        
        model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics
        )
    
    return model