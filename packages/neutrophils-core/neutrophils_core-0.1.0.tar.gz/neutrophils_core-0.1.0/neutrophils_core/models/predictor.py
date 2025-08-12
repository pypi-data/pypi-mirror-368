"""
Prediction utilities for neutrophil classification models.

This module provides the Predictor class that handles the actual prediction
logic for both 2D and 3D models.
"""

import numpy as np
from typing import Union, Optional, Dict, Any, List
import tensorflow as tf


class Predictor:
    """
    Predictor class for making predictions with neutrophil classification models.

    Handles preprocessing, prediction, and postprocessing for both 2D and 3D models.
    """

    def __init__(
        self,
        model: tf.keras.Model,
        model_type: str,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the predictor.

        Args:
            model: Loaded TensorFlow/Keras model
            model_type: Model type ('2d' or '3d')
            config: Optional configuration dictionary
        """
        self.model = model
        self.model_type = model_type
        self.config = config or {}

        # Get model input/output information
        self.input_shape = model.input_shape
        self.output_shape = model.output_shape

        # Determine number of classes from output shape
        if len(self.output_shape) >= 2:
            self.num_classes = self.output_shape[-1]
        else:
            self.num_classes = 1

        # Default class names (can be overridden in config)
        self.class_names = self.config.get(
            "class_names", ["M", "MM", "BN", "SN"][: self.num_classes]
        )

    def predict(
        self,
        input_data: np.ndarray,
        return_probabilities: bool = True,
        batch_size: Optional[int] = None,
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        Make prediction on input data.

        Args:
            input_data: Input image array
            return_probabilities: If True, return class probabilities
            batch_size: Batch size for prediction

        Returns:
            Predictions (probabilities or class indices)
        """
        # Preprocess input
        processed_input = self._preprocess_input(input_data)

        # Make prediction
        if batch_size is not None:
            predictions = self.model.predict(processed_input, batch_size=batch_size)
        else:
            predictions = self.model.predict(processed_input)

        # Postprocess predictions
        return self._postprocess_predictions(predictions, return_probabilities)

    def predict_batch(
        self,
        input_batch: Union[np.ndarray, List[np.ndarray]],
        batch_size: int = 32,
        return_probabilities: bool = True,
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        Make predictions on a batch of inputs.

        Args:
            input_batch: Batch of input images
            batch_size: Batch size for processing
            return_probabilities: If True, return class probabilities

        Returns:
            Batch predictions array
        """
        # Convert list to array if needed
        if isinstance(input_batch, list):
            input_batch = np.array(input_batch)

        # Preprocess batch
        processed_batch = self._preprocess_batch(input_batch)

        # Make predictions
        predictions = self.model.predict(processed_batch, batch_size=batch_size)

        # Postprocess predictions
        return self._postprocess_predictions(predictions, return_probabilities)

    def _preprocess_input(self, input_data: np.ndarray) -> np.ndarray:
        """
        Preprocess input data for model prediction.

        Args:
            input_data: Raw input image array

        Returns:
            Preprocessed input ready for model
        """
        # Ensure proper shape (add batch dimension if missing)
        if len(input_data.shape) == len(self.input_shape) - 1:
            input_data = np.expand_dims(input_data, axis=0)

        # Normalize if needed
        if input_data.dtype != np.float32:
            input_data = input_data.astype(np.float32)

        # Apply any normalization specified in config
        normalization_method = self.config.get("normalization", "none")

        if normalization_method == "minmax":
            input_data = self._normalize_minmax(input_data)
        elif normalization_method == "standardize":
            input_data = self._normalize_standardize(input_data)
        elif normalization_method == "zero_one":
            input_data = input_data / 255.0

        return input_data

    def _preprocess_batch(self, input_batch: np.ndarray) -> np.ndarray:
        """
        Preprocess a batch of input data.

        Args:
            input_batch: Batch of input images

        Returns:
            Preprocessed batch ready for model
        """
        # Apply preprocessing to each item in batch
        processed_batch = []

        for i in range(input_batch.shape[0]):
            # Remove batch dimension for individual preprocessing
            single_input = input_batch[i]
            processed_input = self._preprocess_input(single_input)
            # Remove the batch dimension added by _preprocess_input
            processed_batch.append(processed_input[0])

        return np.array(processed_batch)

    def _postprocess_predictions(
        self, predictions: np.ndarray, return_probabilities: bool
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        Postprocess model predictions.

        Args:
            predictions: Raw model predictions
            return_probabilities: Whether to return probabilities

        Returns:
            Processed predictions
        """
        if return_probabilities:
            # Return probabilities and predicted classes
            if len(predictions.shape) > 1 and predictions.shape[-1] > 1:
                # Multi-class case
                probabilities = tf.nn.softmax(predictions).numpy()
                predicted_classes = np.argmax(probabilities, axis=-1)
            else:
                # Binary case
                probabilities = tf.nn.sigmoid(predictions).numpy()
                predicted_classes = (probabilities > 0.5).astype(int)

            return {
                "probabilities": probabilities,
                "predicted_classes": predicted_classes,
                "class_names": self.class_names,
            }
        else:
            # Return only predicted classes
            if len(predictions.shape) > 1 and predictions.shape[-1] > 1:
                return np.argmax(predictions, axis=-1)
            else:
                return (tf.nn.sigmoid(predictions).numpy() > 0.5).astype(int)

    def _normalize_minmax(self, data: np.ndarray) -> np.ndarray:
        """
        Apply min-max normalization to data.

        Args:
            data: Input data array

        Returns:
            Normalized data
        """
        data_min = np.min(data)
        data_max = np.max(data)

        if data_max > data_min:
            return (data - data_min) / (data_max - data_min)
        else:
            return data

    def _normalize_standardize(self, data: np.ndarray) -> np.ndarray:
        """
        Apply standardization (z-score normalization) to data.

        Args:
            data: Input data array

        Returns:
            Standardized data
        """
        mean = np.mean(data)
        std = np.std(data)

        if std > 0:
            return (data - mean) / std
        else:
            return data - mean

    def get_prediction_info(self) -> Dict[str, Any]:
        """
        Get information about the predictor setup.

        Returns:
            Dictionary with predictor information
        """
        return {
            "model_type": self.model_type,
            "input_shape": self.input_shape,
            "output_shape": self.output_shape,
            "num_classes": self.num_classes,
            "class_names": self.class_names,
            "config": self.config,
        }
