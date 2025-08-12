"""
Model loading utilities for 2D and 3D neutrophil classification models.

This module provides functionality to load pre-trained models with proper
custom objects and error handling.
"""

import os
import warnings
from typing import Optional, Dict, Any
import tensorflow as tf
from tensorflow import keras


class ModelLoader:
    """
    Utility class for loading neutrophil classification models.

    Handles loading both 2D and 3D models with proper custom objects
    and error handling for different model formats.
    """

    def __init__(self):
        """Initialize the model loader."""
        self.custom_objects = self._get_custom_objects()

    def load_model(
        self,
        model_path: str,
        model_type: str = "auto",
        config: Optional[Dict[str, Any]] = None,
    ) -> tf.keras.Model:
        """
        Load a pre-trained model from file.

        Args:
            model_path: Path to the model file
            model_type: Model type ('2d', '3d', or 'auto')
            config: Optional configuration dictionary

        Returns:
            Loaded TensorFlow/Keras model

        Raises:
            FileNotFoundError: If model file doesn't exist
            ValueError: If model cannot be loaded
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        # Determine model file format
        model_format = self._detect_model_format(model_path)

        try:
            if model_format == "keras":
                model = self._load_keras_model(model_path)
            elif model_format == "savedmodel":
                model = self._load_savedmodel(model_path)
            elif model_format == "h5":
                model = self._load_h5_model(model_path)
            else:
                # Try default keras loading
                model = self._load_keras_model(model_path)

            print(f"Successfully loaded {model_type} model from {model_path}")
            return model

        except Exception as e:
            raise ValueError(f"Failed to load model from {model_path}: {str(e)}")

    def _detect_model_format(self, model_path: str) -> str:
        """
        Detect the format of the model file.

        Args:
            model_path: Path to model file

        Returns:
            Model format ('keras', 'savedmodel', 'h5')
        """
        if os.path.isdir(model_path):
            # SavedModel format (directory)
            return "savedmodel"
        elif model_path.endswith(".h5") or model_path.endswith(".hdf5"):
            # HDF5 format
            return "h5"
        else:
            # Default to Keras format
            return "keras"

    def _load_keras_model(self, model_path: str) -> tf.keras.Model:
        """
        Load a Keras model with custom objects.

        Args:
            model_path: Path to model file

        Returns:
            Loaded Keras model
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            try:
                # Try loading with custom objects first
                model = tf.keras.models.load_model(
                    model_path, custom_objects=self.custom_objects, compile=False
                )
                return model
            except Exception as e:
                print(f"Warning: Failed to load with custom objects: {e}")

                # Try to register custom objects globally and retry
                try:
                    self._register_custom_objects_globally()
                    model = tf.keras.models.load_model(model_path, compile=False)
                    return model
                except Exception as e2:
                    print(f"Warning: Failed to load after global registration: {e2}")

                    # Final fallback: try loading without custom objects
                    try:
                        model = tf.keras.models.load_model(model_path, compile=False)
                        print("Warning: Loaded model without custom objects - some functionality may be limited")
                        return model
                    except Exception as e3:
                        raise ValueError(f"Failed to load model with all methods: {e3}")

    def _load_savedmodel(self, model_path: str) -> tf.keras.Model:
        """
        Load a SavedModel format model.

        Args:
            model_path: Path to SavedModel directory

        Returns:
            Loaded model
        """
        return tf.keras.models.load_model(model_path)

    def _load_h5_model(self, model_path: str) -> tf.keras.Model:
        """
        Load an HDF5 format model.

        Args:
            model_path: Path to H5 file

        Returns:
            Loaded model
        """
        return tf.keras.models.load_model(
            model_path, custom_objects=self.custom_objects, compile=False
        )

    def _get_custom_objects(self) -> Dict[str, Any]:
        """
        Get custom objects needed for loading models.

        Returns:
            Dictionary of custom objects
        """
        custom_objects = {}

        try:
            # Import custom model classes
            from .feature_extractor import FeatureExtractor
            from .feature_extractor_3d import FeatureExtractor3D
            from .dynamic_residual_scaling import DynamicResidualScaling
            from .heads import ClassificationHead, ContrastiveHead
            from .simclr import SimCLREncoder, SimCLRModel
            
            # Add custom model classes
            custom_objects.update({
                'FeatureExtractor': FeatureExtractor,
                'FeatureExtractor3D': FeatureExtractor3D,
                'DynamicResidualScaling': DynamicResidualScaling,
                'ClassificationHead': ClassificationHead,
                'ContrastiveHead': ContrastiveHead,
                'SimCLREncoder': SimCLREncoder,
                'SimCLRModel': SimCLRModel,
            })
            
        except ImportError as e:
            print(f"Warning: Could not import custom model classes: {e}")

        try:
            # Import loss functions from metrics module
            from ..metrics.loss_functions import (
                dice_loss,
                ordinal_crossentropy,
                balanced_ordinal_crossentropy,
                ordinal_focal_loss,
                soft_ordinal_loss,
                cumulative_ordinal_loss,
                categorical_dice_loss,
                ordinal_dice_loss,
                f1_loss,
            )

            # Add loss functions
            custom_objects.update(
                {
                    "dice_loss": dice_loss,
                    "ordinal_crossentropy": ordinal_crossentropy,
                    "balanced_ordinal_crossentropy": balanced_ordinal_crossentropy,
                    "ordinal_focal_loss": ordinal_focal_loss,
                    "soft_ordinal_loss": soft_ordinal_loss,
                    "cumulative_ordinal_loss": cumulative_ordinal_loss,
                    "categorical_dice_loss": categorical_dice_loss,
                    "ordinal_dice_loss": ordinal_dice_loss,
                    "f1_loss": f1_loss,
                }
            )

        except ImportError as e:
            print(f"Warning: Could not import loss functions: {e}")

        try:
            # Import metrics from metrics module
            from ..metrics.classification_metrics import (
                ordinal_mae,
                adjacent_class_accuracy,
                adjacent_class_recall,
                adjacent_class_precision,
                adjacent_class_auc,
                kendall_tau_metric,
                balanced_accuracy_metric,
                ordinal_accuracy_tolerance,
            )

            # Add metrics
            custom_objects.update(
                {
                    "ordinal_mae": ordinal_mae,
                    "adjacent_class_accuracy": adjacent_class_accuracy,
                    "adjacent_class_recall": adjacent_class_recall,
                    "adjacent_class_precision": adjacent_class_precision,
                    "adjacent_class_auc": adjacent_class_auc,
                    "kendall_tau_metric": kendall_tau_metric,
                    "balanced_accuracy_metric": balanced_accuracy_metric,
                    "ordinal_accuracy_tolerance": ordinal_accuracy_tolerance,
                }
            )

        except ImportError as e:
            print(f"Warning: Could not import metrics: {e}")

        return custom_objects

    def _register_custom_objects_globally(self):
        """Register custom objects globally with Keras."""
        try:
            # Import and register FeatureExtractor3D
            from .feature_extractor_3d import FeatureExtractor3D
            tf.keras.utils.get_custom_objects()['FeatureExtractor3D'] = FeatureExtractor3D
            
            # Import and register DynamicResidualScaling
            from .dynamic_residual_scaling import DynamicResidualScaling
            tf.keras.utils.get_custom_objects()['DynamicResidualScaling'] = DynamicResidualScaling
            
            # Import and register FeatureExtractor
            from .feature_extractor import FeatureExtractor
            tf.keras.utils.get_custom_objects()['FeatureExtractor'] = FeatureExtractor
            
            # Import and register heads if available
            try:
                from .heads import ClassificationHead, ContrastiveHead
                tf.keras.utils.get_custom_objects()['ClassificationHead'] = ClassificationHead
                tf.keras.utils.get_custom_objects()['ContrastiveHead'] = ContrastiveHead
            except ImportError:
                pass
                
            print("✓ Custom objects registered globally with Keras")
            
        except Exception as e:
            print(f"Warning: Failed to register custom objects globally: {e}")

    def validate_model(self, model: tf.keras.Model, model_type: str) -> bool:
        """
        Validate that the loaded model is appropriate for the specified type.

        Args:
            model: Loaded model
            model_type: Expected model type ('2d' or '3d')

        Returns:
            True if validation passes
        """
        try:
            input_shape = model.input_shape

            if model_type == "2d":
                # 2D models should have 4D input (batch, height, width, channels)
                expected_dims = 4
            elif model_type == "3d":
                # 3D models should have 5D input (batch, depth, height, width, channels)
                expected_dims = 5
            else:
                # Auto or unknown type
                return True

            if len(input_shape) != expected_dims:
                print(
                    f"Warning: Model input shape {input_shape} doesn't match expected {model_type} format"
                )
                return False

            return True

        except Exception as e:
            print(f"Warning: Could not validate model: {e}")
            return True  # Assume valid if validation fails
