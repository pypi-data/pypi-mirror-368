"""Data loading utilities for neutrophils-core."""

from .ImageDataGenerator2D import ImageDataGenerator2D
from .hierarchical_labels import NEUTROPHIL_HIERARCHY, get_head_info, convert_flat_label_to_hierarchical
from .data_utils import load_data, split_data, load_images_legacy, convert_labels_for_ordinal
from .contrastive_generator import (
    ContrastiveDataGenerator3D, create_contrastive_generator, create_unlabeled_contrastive_generator
)
from .optimized_image_data_generator_3d import (
    OptimizedImageDataGenerator3D,
    create_optimized_labeled_generator,
    create_optimized_contrastive_generator
)

__all__ = [
    'ImageDataGenerator2D',
    'NEUTROPHIL_HIERARCHY',
    'get_head_info',
    'convert_flat_label_to_hierarchical',
    'load_data',
    'split_data',
    'load_images_legacy',
    'convert_labels_for_ordinal',
    'augmentations_3d',
    # Contrastive learning components
    'ContrastiveDataGenerator3D',
    'create_contrastive_generator',
    'create_unlabeled_contrastive_generator',
    # Optimized data generators
    'OptimizedImageDataGenerator3D',
    'create_optimized_labeled_generator',
    'create_optimized_contrastive_generator'
]