"""
Neutrophils Core Library

A unified library for neutrophil classification providing:
- 2D/3D model interfaces
- Data preprocessing and augmentations
- Configuration management
- Evaluation metrics and utilities
- Contrastive learning support
"""

__version__ = "0.1.0"
__author__ = "BPI Oxford"

# Import available components
try:
    from .models.feature_extractor import FeatureExtractor, create_feature_extractor_from_config
    from .models.feature_extractor_3d import FeatureExtractor3D, create_feature_extractor_3d_from_config
    _MODELS_AVAILABLE = True
except ImportError:
    _MODELS_AVAILABLE = False

try:
    from .loader.ImageDataGenerator2D import ImageDataGenerator2D
    from .loader.ImageDataGenerator3D import (
        ImageDataGenerator3D, 
        create_labeled_generator, 
        create_contrastive_generator
    )
    _LOADERS_AVAILABLE = True
except ImportError:
    _LOADERS_AVAILABLE = False

try:
    from .loader import augmentations_2d, augmentations_3d
    _AUGMENTATIONS_AVAILABLE = True
except ImportError:
    _AUGMENTATIONS_AVAILABLE = False

try:
    from .metrics.loss_functions import (
        # Standard losses
        categorical_crossentropy,
        ordinal_crossentropy,
        # Function registry
        LOSS_FUNCTIONS
    )
    from .metrics.classification_metrics import (
        # Ordinal metrics
        ordinal_mae,
        adjacent_class_accuracy
    )
    from .metrics.contrastive_losses import (
        # Contrastive losses
        nce_loss,
        nt_xent_loss,
        supervised_contrastive_loss,
        contrastive_accuracy,
        ContrastiveLosses,
        ContrastiveLossTracker,
        SimilarityMetric,
        create_nce_loss_fn,
        create_nt_xent_loss_fn,
        create_contrastive_accuracy_fn
    )
    _METRICS_AVAILABLE = True
except ImportError:
    _METRICS_AVAILABLE = False

try:
    from .loader.contrastive_generator import (
        ContrastiveDataGenerator3D,
        create_contrastive_generator,
        create_unlabeled_contrastive_generator
    )
    _CONTRASTIVE_LOADERS_AVAILABLE = True
except ImportError:
    _CONTRASTIVE_LOADERS_AVAILABLE = False

try:
    from .utils.embedding_visualization import (
        extract_embeddings,
        save_embeddings_data,
        create_embedding_plots,
        create_combined_embedding_plot,
        save_and_visualize_embeddings
    )
    _EMBEDDING_VIZ_AVAILABLE = True
except ImportError:
    _EMBEDDING_VIZ_AVAILABLE = False

# Build dynamic __all__ based on what's available
__all__ = ["__version__", "__author__"]

if _MODELS_AVAILABLE:
    __all__.extend([
        "FeatureExtractor",
        "create_feature_extractor_from_config", 
        "FeatureExtractor3D",
        "create_feature_extractor_3d_from_config"
    ])

if _LOADERS_AVAILABLE:
    __all__.extend([
        "ImageDataGenerator2D",
        "ImageDataGenerator3D",
        "create_labeled_generator",
        "create_contrastive_generator"
    ])

if _AUGMENTATIONS_AVAILABLE:
    __all__.extend([
        "augmentations_2d",
        "augmentations_3d"
    ])

if _METRICS_AVAILABLE:
    __all__.extend([
        # Loss functions
        "categorical_crossentropy",
        "ordinal_crossentropy",
        "nce_loss",
        "nt_xent_loss",
        "supervised_contrastive_loss",
        "LOSS_FUNCTIONS",
        # Classification metrics
        "ordinal_mae",
        "adjacent_class_accuracy",
        "contrastive_accuracy",
        # Contrastive learning utilities
        "ContrastiveLosses",
        "ContrastiveLossTracker",
        "SimilarityMetric",
        "create_nce_loss_fn",
        "create_nt_xent_loss_fn",
        "create_contrastive_accuracy_fn"
    ])

if _CONTRASTIVE_LOADERS_AVAILABLE:
    __all__.extend([
        "ContrastiveDataGenerator3D",
        "create_contrastive_generator",
        "create_unlabeled_contrastive_generator"
    ])

if _EMBEDDING_VIZ_AVAILABLE:
    __all__.extend([
        "extract_embeddings",
        "save_embeddings_data",
        "create_embedding_plots",
        "create_combined_embedding_plot",
        "save_and_visualize_embeddings"
    ])

# Convenience imports for 3D contrastive learning
def get_3d_contrastive_components():
    """
    Get all components needed for 3D contrastive learning.
    
    Returns:
        dict: Dictionary with keys:
            - feature_extractor_3d: 3D feature extractor class
            - contrastive_data_generator: Contrastive data generator class
            - augmentations_3d: 3D augmentation functions
            - contrastive_losses: Contrastive loss functions
            - embedding_visualization: Embedding visualization utilities
    """
    components = {}
    
    if _MODELS_AVAILABLE:
        components['feature_extractor_3d'] = FeatureExtractor3D
        components['create_feature_extractor_3d'] = create_feature_extractor_3d_from_config
    
    if _LOADERS_AVAILABLE:
        components['data_generator_3d'] = ImageDataGenerator3D
        components['create_labeled_generator'] = create_labeled_generator
    
    if _CONTRASTIVE_LOADERS_AVAILABLE:
        components['contrastive_data_generator'] = ContrastiveDataGenerator3D
        components['create_contrastive_generator'] = create_contrastive_generator
        components['create_unlabeled_contrastive_generator'] = create_unlabeled_contrastive_generator
    
    if _AUGMENTATIONS_AVAILABLE:
        components['augmentations_3d'] = augmentations_3d
    
    if _METRICS_AVAILABLE:
        components['contrastive_losses'] = {
            'nce_loss': nce_loss,
            'nt_xent_loss': nt_xent_loss,
            'supervised_contrastive_loss': supervised_contrastive_loss,
            'contrastive_accuracy': contrastive_accuracy,
            'create_nce_loss_fn': create_nce_loss_fn,
            'create_nt_xent_loss_fn': create_nt_xent_loss_fn,
            'create_contrastive_accuracy_fn': create_contrastive_accuracy_fn,
            'ContrastiveLosses': ContrastiveLosses,
            'ContrastiveLossTracker': ContrastiveLossTracker,
            'SimilarityMetric': SimilarityMetric
        }
    
    if _EMBEDDING_VIZ_AVAILABLE:
        components['embedding_visualization'] = {
            'extract_embeddings': extract_embeddings,
            'save_embeddings_data': save_embeddings_data,
            'create_embedding_plots': create_embedding_plots,
            'create_combined_embedding_plot': create_combined_embedding_plot,
            'save_and_visualize_embeddings': save_and_visualize_embeddings
        }
    
    return components

__all__.append("get_3d_contrastive_components")
