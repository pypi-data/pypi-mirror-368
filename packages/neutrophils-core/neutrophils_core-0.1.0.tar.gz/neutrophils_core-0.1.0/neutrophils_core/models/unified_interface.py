"""
Unified interface for 2D and 3D neutrophil classification models.

This module provides the main Classifier class for inference with both 2D and 3D models,
featuring automatic type detection and unified prediction interface.
"""

import os
import numpy as np
from typing import Union, Optional, Dict, Any, Tuple, List
import tensorflow as tf

from .model_loader import ModelLoader
from .predictor import Predictor
from ..preprocessing.projection import create_mip_projection

# from ..config.config_manager import ConfigManager  # Temporarily disabled until config_manager is implemented


class Classifier:
    """
    Unified classifier for both 2D and 3D neutrophil classification inference.

    This class provides a single interface for loading and using both 2D and 3D
    neutrophil classification models for inference, with automatic model type
    detection and support for 3D→2D MIP projections.

    Note: This interface is designed for inference only. Training should be done
    using the training pipelines in the main repository.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        model_type: Optional[str] = None,
        config_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the classifier for inference.

        Args:
            model_path: Path to the trained model file
            model_type: Explicit model type ('2d', '3d', or 'auto' for auto-detection)
            config_path: Path to configuration file
            config: Configuration dictionary (alternative to config_path)
        """
        self.model_path = model_path
        self.model_type = model_type or "auto"
        self.model: Optional[tf.keras.Model] = None
        self.config = None
        self.predictor: Optional[Predictor] = None

        # Load configuration
        if config is not None:
            self.config = config
        elif config_path is not None:
            # Temporarily disabled until ConfigManager is implemented
            # self.config = ConfigManager.load_config(config_path)
            import warnings

            warnings.warn(
                "ConfigManager not yet implemented. Config loading from file is disabled."
            )
            self.config = None

        # Initialize model loader
        self.model_loader = ModelLoader()

        # Load model if path provided
        if model_path is not None:
            self.load_model(model_path, model_type)

    def load_model(self, model_path: str, model_type: Optional[str] = None) -> None:
        """
        Load a pre-trained model from the specified path.

        Args:
            model_path: Path to the model file
            model_type: Explicit model type or 'auto' for detection
        """
        self.model_path = model_path

        if model_type is not None:
            self.model_type = model_type

        # Auto-detect model type if needed
        if self.model_type == "auto":
            self.model_type = self._detect_model_type(model_path)

        # Load the model
        self.model = self.model_loader.load_model(
            model_path, self.model_type, self.config
        )

        # Initialize predictor
        self.predictor = Predictor(self.model, self.model_type, self.config)

    def predict(
        self,
        input_data: Union[np.ndarray, str],
        return_2d_mip: bool = False,
        return_probabilities: bool = True,
        batch_size: Optional[int] = None,
    ) -> Union[
        np.ndarray,
        Dict[str, np.ndarray],
        Tuple[
            Union[np.ndarray, Dict[str, np.ndarray]],
            Union[np.ndarray, List[np.ndarray]],
        ],
    ]:
        """
        Predict neutrophil classification for input data.

        Args:
            input_data: Input image array or path to image file
            return_2d_mip: If True and input is 3D, also return 2D MIP projection
            return_probabilities: If True, return class probabilities
            batch_size: Batch size for prediction (if applicable)

        Returns:
            Predictions array, optionally with 2D MIP projection
        """
        if self.model is None or self.predictor is None:
            raise ValueError("No model loaded. Call load_model() first.")

        # Load image if path provided
        if isinstance(input_data, str):
            input_data = self._load_image(input_data)

        # Handle 3D→2D conversion if needed
        processed_input: np.ndarray = input_data
        mip_projection: Optional[Union[np.ndarray, List[np.ndarray]]] = None

        if self.model_type == "2d" and len(input_data.shape) == 3:
            # Convert 3D to 2D MIP for 2D models
            mip_result = create_mip_projection(input_data)
            # Ensure we get an ndarray for model input
            if isinstance(mip_result, list):
                processed_input = mip_result[0]  # Use first projection if list
            else:
                processed_input = mip_result
            if return_2d_mip:
                mip_projection = mip_result
        elif self.model_type == "3d" and return_2d_mip and len(input_data.shape) == 3:
            # Create MIP projection for visualization
            mip_projection = create_mip_projection(input_data)

        # Make prediction
        predictions = self.predictor.predict(
            processed_input,
            return_probabilities=return_probabilities,
            batch_size=batch_size,
        )

        # Return results
        if return_2d_mip and mip_projection is not None:
            return predictions, mip_projection
        else:
            return predictions

    def predict_batch(
        self,
        input_batch: Union[np.ndarray, list],
        batch_size: int = 32,
        return_probabilities: bool = True,
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """
        Predict classifications for a batch of inputs.

        Args:
            input_batch: Batch of input images
            batch_size: Batch size for processing
            return_probabilities: If True, return class probabilities

        Returns:
            Batch predictions array
        """
        if self.model is None or self.predictor is None:
            raise ValueError("No model loaded. Call load_model() first.")

        return self.predictor.predict_batch(
            input_batch,
            batch_size=batch_size,
            return_probabilities=return_probabilities,
        )

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.

        Returns:
            Dictionary containing model information
        """
        if self.model is None:
            return {"status": "No model loaded"}

        info = {
            "model_path": self.model_path,
            "model_type": self.model_type,
            "input_shape": self.model.input_shape,
            "output_shape": self.model.output_shape,
            "num_parameters": self.model.count_params(),
        }

        if self.config is not None:
            info["config"] = self.config

        return info

    def _detect_model_type(self, model_path: str) -> str:
        """
        Auto-detect model type from model file or path.

        Args:
            model_path: Path to model file

        Returns:
            Detected model type ('2d' or '3d')
        """
        # Check filename for hints
        filename = os.path.basename(model_path).lower()

        if "2d" in filename or "mip" in filename:
            return "2d"
        elif "3d" in filename:
            return "3d"

        # Try to load model and check input shape
        try:
            temp_model = tf.keras.models.load_model(model_path)
            input_shape = temp_model.input_shape

            # Determine based on input dimensions
            # Assuming: 2D models have 4D input (batch, height, width, channels)
            # 3D models have 5D input (batch, depth, height, width, channels)
            if len(input_shape) == 4:
                return "2d"
            elif len(input_shape) == 5:
                return "3d"
            else:
                # Default to 2d if uncertain
                return "2d"

        except Exception:
            # Default to 2d if detection fails
            return "2d"

    def _load_image(self, image_path: str) -> np.ndarray:
        """
        Load image from file path.

        Args:
            image_path: Path to image file

        Returns:
            Loaded image array
        """
        from ..preprocessing.image_utils import load_image

        return load_image(image_path)
