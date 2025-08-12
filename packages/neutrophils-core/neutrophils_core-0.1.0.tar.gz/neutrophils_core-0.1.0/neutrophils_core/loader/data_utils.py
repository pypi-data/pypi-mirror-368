"""Data loading and preprocessing utilities."""

import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tqdm import tqdm
import matplotlib.pyplot as plt
from skimage.exposure import rescale_intensity
from typing import Optional, Dict, List, Tuple, Union
from . import augmentations_3d
from .optimized_image_data_generator_3d import OptimizedImageDataGenerator3D


def crop_center(image: np.ndarray, crop_size: List[int] = [69, 69, 69]) -> np.ndarray:
    """
    Crop image to center with specified size.
    
    Args:
        image: Input 3D numpy array
        crop_size: Target crop size [width, height, depth]
        
    Returns:
        Center-cropped image
    """
    width, height, depth = image.shape
    start_x = max((width - crop_size[0]) // 2, 0)
    start_y = max((height - crop_size[1]) // 2, 0)
    start_z = max((depth - crop_size[2]) // 2, 0)
    
    return image[
        start_x:start_x + crop_size[0],
        start_y:start_y + crop_size[1],
        start_z:start_z + crop_size[2]
    ]


def pad_image(image: np.ndarray, padded_size: List[int] = [69, 69, 69]) -> np.ndarray:
    """
    Pad image to specified size with zeros.
    
    Args:
        image: Input 3D numpy array
        padded_size: Target padded size [width, height, depth]
        
    Returns:
        Zero-padded image
    """
    pad_0 = [0, 0, 0]
    pad_1 = [0, 0, 0]
    
    for i in range(3):
        if image.shape[i] < padded_size[i]:
            pad_0[i] = (padded_size[i] - image.shape[i]) // 2
            pad_1[i] = padded_size[i] - image.shape[i] - pad_0[i]

    padded_image = np.pad(
        image,
        ((pad_0[0], pad_1[0]), (pad_0[1], pad_1[1]), (pad_0[2], pad_1[2])),
        mode='constant',
        constant_values=0
    )
    
    return padded_image

def process_image_3d(
    img_np: np.ndarray,
    image_size: int,
    mip: bool,
    train: bool = False,
    augmentation_config: Optional[Dict] = None,
    intensity_input_percentiles: Tuple[float, float] = (1, 99),
    intensity_out_range: Tuple[float, float] = (0, 1)
) -> np.ndarray:
    """
    Process a 3D image with augmentation, normalization, and resizing.
    """
    # Apply augmentations if in training mode
    if train and augmentation_config:
        img_np = augmentations_3d.apply_augmentations(
            img_np,
            augmentation_config["order"],
            augmentation_config
        )
    
    # Intensity normalization
    p_low, p_high = np.percentile(img_np, intensity_input_percentiles)
    if p_high > p_low:
        img_np = rescale_intensity(
            img_np,
            in_range=(p_low, p_high),
            out_range=intensity_out_range
        )
    elif img_np.max() > 0:
        img_np = img_np / img_np.max()
    
    # Resize to target dimensions
    img_np = pad_image(img_np, padded_size=[image_size, image_size, image_size])
    img_np = crop_center(img_np, crop_size=[image_size, image_size, image_size])

    # Generate MIP if requested
    if mip:
        img_mip_0 = img_np.max(axis=0)
        img_mip_1 = img_np.max(axis=1)
        img_mip_2 = img_np.max(axis=2)
        return np.stack([img_mip_0, img_mip_1, img_mip_2], axis=-1)
    
    return np.expand_dims(img_np, axis=-1)

def load_data(data_dir, label_file, classes, debug=False, samples_per_class=10):
    """
    Load image paths and labels from the label file
    
    Args:
        data_dir: Directory containing the image files
        label_file: CSV file with image labels
        classes: Dictionary mapping class names to class IDs
        debug: If True, load only a subset of images
        samples_per_class: Number of samples to load per class in debug mode
    """
    print("Loading data from:", data_dir)
    print("Using label file:", label_file)
    
    image_paths = []
    labels = []
    label_id = []

    label_df = pd.read_csv(label_file)
    
    # In debug mode, limit the number of images to load
    if debug:
        print(f"Debug mode: Loading {samples_per_class} samples per class")
        for class_name in classes.keys():
            class_rows = label_df[label_df["stage"] == class_name].head(samples_per_class)
            for _, row in class_rows.iterrows():
                if pd.isna(row["filepath"]) or not str(row["filepath"]).strip():
                    continue

                image_path = os.path.join(data_dir, "{}.png".format(str(row["filepath"]).split(".")[0]))

                if not os.path.exists(image_path):
                    continue

                image_paths.append(image_path)
                labels.append(row["stage"])
                label_id.append(classes[row["stage"]])
    else:
        # Normal mode: Load all images
        for _, row in label_df.iterrows():
            if pd.isna(row["filepath"]) or not str(row["filepath"]).strip():
                continue

            image_path = os.path.join(data_dir, "{}.png".format(str(row["filepath"]).split(".")[0]))

            if not os.path.exists(image_path):
                continue

            if row["stage"] in classes:
                image_paths.append(image_path)
                labels.append(row["stage"])
                label_id.append(classes[row["stage"]])

    label_df = pd.DataFrame.from_dict({"path": image_paths, "label": labels, "label_id": label_id})
    print(f"Loaded {len(label_df)} images")
    return label_df

def split_data(label_df, test_size=0.2, random_state=42):
    """Split data into training and testing sets."""
    label_df_train, label_df_test = train_test_split(label_df, test_size=test_size, random_state=random_state)
    return label_df_train, label_df_test

def load_images_legacy(label_df_train, label_df_test, projection_mode='single'):
    """(Legacy) Load images into memory in static way"""
    images_train = []
    images_test = []

    for path in tqdm(label_df_train["path"], desc="Loading training", total=len(label_df_train)):
        if projection_mode == 'multi':
            img = plt.imread(path)
            projection_width = 96
            proj1 = img[:, :projection_width, 0] / 255.0
            proj2 = img[:, projection_width:2*projection_width, 0] / 255.0
            proj3 = img[:, -projection_width:, 0] / 255.0
            multi_channel_img = np.stack([proj1, proj2, proj3], axis=-1)
            images_train.append(multi_channel_img)
        else:
            images_train.append(plt.imread(path)[:, -96:, 0] / 255.0)

    for path in tqdm(label_df_test["path"], desc="Loading testing", total=len(label_df_test)):
        if projection_mode == 'multi':
            img = plt.imread(path)
            projection_width = 96
            proj1 = img[:, :projection_width, 0] / 255.0
            proj2 = img[:, projection_width:2*projection_width, 0] / 255.0
            proj3 = img[:, -projection_width:, 0] / 255.0
            multi_channel_img = np.stack([proj1, proj2, proj3], axis=-1)
            images_test.append(multi_channel_img)
        else:
            images_test.append(plt.imread(path)[:, -96:, 0] / 255.0)
            
    return images_train, images_test

def convert_labels_for_ordinal(labels_encoded, loss_type):
    """Convert labels to appropriate format for ordinal loss functions"""
    ordinal_losses = ['ordinal_crossentropy', 'balanced_ordinal_crossentropy', 'soft_ordinal_loss', 
                     'cumulative_ordinal_loss', 'balanced_cumulative_ordinal_loss']
    
    if loss_type in ordinal_losses:
        if len(labels_encoded.shape) > 1 and labels_encoded.shape[1] > 1:
            converted_labels = np.argmax(labels_encoded, axis=1)
            print(f"Converting one-hot encoded labels to class indices for ordinal loss '{loss_type}'")
            return converted_labels
        else:
            return labels_encoded
    else:
        if len(labels_encoded.shape) == 1 or labels_encoded.shape[1] == 1:
            num_classes = len(np.unique(labels_encoded))
            converted_labels = to_categorical(labels_encoded, num_classes=num_classes)
            print(f"Converting class indices to one-hot encoded labels for standard loss '{loss_type}'")
            return converted_labels
        else:
            return labels_encoded
        
def create_dataset_from_directory(data_dir, config, labels=None, return_paths=False):
    """
    Creates a tf.data.Dataset from a directory of images.

    Args:
        data_dir (str): Path to the directory containing images.
        config (dict): Configuration dictionary.
        labels (pd.DataFrame, optional): DataFrame with labels. Defaults to None.
        return_paths (bool, optional): Whether to return file paths. Defaults to False.

    Returns:
        tf.data.Dataset: The created dataset.
    """
    # Create a dummy DataFrame if labels are not provided
    if labels is None:
        image_files = []
        for root, _, files in os.walk(data_dir):
            for f in files:
                if f.endswith(('.tif', '.tiff')):
                    image_files.append(os.path.relpath(os.path.join(root, f), data_dir))
        labels = pd.DataFrame({'filepath': image_files})

    generator = OptimizedImageDataGenerator3D(
        df=labels,
        data_dir=data_dir,
        batch_size=config.get('train_params', {}).get('batch_size', 32),
        image_size=config.get('data', {}).get('image_size', 69),
        mip=config.get('data', {}).get('use_mip', False),
        shuffle=False,  # No shuffling for inference
        to_fit=False,
        get_paths=return_paths,
        train=False,  # No augmentations for inference
        use_tf_data_optimization=True,
        intensity_input_percentiles=(1, 99),
        intensity_out_range=(0, 255)
    )
    
    dataset = generator.get_tf_dataset()
    
    if return_paths:
        return dataset, labels['filepath'].tolist()
    
    return dataset