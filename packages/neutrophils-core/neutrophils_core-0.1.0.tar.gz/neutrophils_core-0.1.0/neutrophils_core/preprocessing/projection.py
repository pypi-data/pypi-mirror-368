"""
3D to 2D projection utilities for neutrophil images.

This module provides functionality to convert 3D neutrophil images to 2D
using Maximum Intensity Projection (MIP) and principal plane estimation.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional, List, Union
import SimpleITK as sitk
import matplotlib.pyplot as plt


def principal_plane_estimation(
    image: np.ndarray,
    label: np.ndarray,
    input_spacing: List[float] = [0.149, 0.149, 0.149],
    output_spacing: List[float] = [0.149, 0.149, 0.149],
    output_images_size: Optional[List[int]] = None,
) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    Estimate principal plane and reorient 3D image.

    This function estimates the principal plane of the largest object in the image
    and reorients the image to align with this plane.

    Args:
        image: 3D image array
        label: 3D label array for segmentation
        input_spacing: Voxel spacing of input image
        output_spacing: Desired voxel spacing of output
        output_images_size: Desired output size (if None, uses input size)

    Returns:
        Tuple of (reoriented_image, reoriented_label, stats_dataframe)
    """
    # Convert numpy arrays to SimpleITK images
    image_sitk = sitk.GetImageFromArray(image)
    label_sitk = sitk.GetImageFromArray(label)
    image_sitk.SetSpacing(input_spacing)
    label_sitk.SetSpacing(input_spacing)

    # Calculate shape statistics
    shape_stats = sitk.LabelShapeStatisticsImageFilter()
    shape_stats.ComputeOrientedBoundingBoxOn()
    shape_stats.Execute(label_sitk)

    # Calculate intensity statistics
    intensity_stats = sitk.LabelIntensityStatisticsImageFilter()
    intensity_stats.Execute(label_sitk, image_sitk)

    # Collect statistics for all labels
    stats_list = [
        (
            shape_stats.GetPhysicalSize(i),
            shape_stats.GetElongation(i),
            shape_stats.GetFlatness(i),
            shape_stats.GetOrientedBoundingBoxSize(i)[0],
            shape_stats.GetOrientedBoundingBoxSize(i)[2],
            intensity_stats.GetMean(i),
            intensity_stats.GetStandardDeviation(i),
            intensity_stats.GetSkewness(i),
        )
        for i in shape_stats.GetLabels()
    ]

    # Create statistics DataFrame
    cols = [
        "Volume (um^3)",
        "Elongation",
        "Flatness",
        "Oriented Bounding Box Minimum Size(um)",
        "Oriented Bounding Box Maximum Size(um)",
        "Intensity Mean",
        "Intensity Standard Deviation",
        "Intensity Skewness",
    ]
    stats = pd.DataFrame(data=stats_list, index=shape_stats.GetLabels(), columns=cols)

    # Find largest volume region
    region_labels = shape_stats.GetLabels()
    region_volumes = [shape_stats.GetPhysicalSize(label) for label in region_labels]
    region_labels_volume_sorted = [
        label for _, label in sorted(zip(region_volumes, region_labels))
    ]

    # Setup resampler
    resampler = sitk.ResampleImageFilter()
    aligned_image_spacing = output_spacing

    if output_images_size is None:
        aligned_image_size = image_sitk.GetSize()
    else:
        aligned_image_size = output_images_size

    # Use the largest volume segment to compute the principal plane
    direction_mat = shape_stats.GetOrientedBoundingBoxDirection(
        region_labels_volume_sorted[0]
    )
    aligned_image_direction = [
        direction_mat[0],
        direction_mat[3],
        direction_mat[6],
        direction_mat[1],
        direction_mat[4],
        direction_mat[7],
        direction_mat[2],
        direction_mat[5],
        direction_mat[8],
    ]  # Transpose to get inverse transform

    resampler.SetOutputDirection(aligned_image_direction)

    # Calculate transformation matrices
    dir_matrix = np.eye(4)
    dir_matrix[:3, :3] = np.reshape(aligned_image_direction, (3, 3))

    # Translation matrices
    translate_0 = np.eye(4)
    translate_vec = [
        image_sitk.GetSize()[i] * image_sitk.GetSpacing()[i] * -0.5 for i in range(3)
    ]
    translate_0[:3, 3] = translate_vec

    translate_1 = np.eye(4)
    translate_vec = [
        image_sitk.GetSize()[i] * image_sitk.GetSpacing()[i] * 0.5 for i in range(3)
    ]
    translate_1[:3, 3] = translate_vec

    # Combined transformation
    combined_transform = np.dot(translate_1, np.dot(dir_matrix, translate_0))

    # Calculate output origin
    output_origin = [
        image_sitk.GetSize()[0] * image_sitk.GetSpacing()[0] / 2
        - aligned_image_size[0] * aligned_image_spacing[0] / 2,
        image_sitk.GetSize()[1] * image_sitk.GetSpacing()[1] / 2
        - aligned_image_size[1] * aligned_image_spacing[1] / 2,
        image_sitk.GetSize()[2] * image_sitk.GetSpacing()[2] / 2
        - aligned_image_size[2] * aligned_image_spacing[2] / 2,
        1,
    ]
    output_origin = np.dot(combined_transform, output_origin)

    # Configure resampler
    resampler.SetOutputOrigin(output_origin[0:3])
    resampler.SetOutputSpacing(aligned_image_spacing)
    resampler.SetSize(aligned_image_size)

    # Resample image and label
    resampler.SetInterpolator(sitk.sitkLinear)
    image_oriented_sitk = resampler.Execute(image_sitk)

    resampler.SetInterpolator(sitk.sitkNearestNeighbor)
    label_oriented_sitk = resampler.Execute(label_sitk)

    # Convert back to numpy arrays
    image_oriented = sitk.GetArrayFromImage(image_oriented_sitk)
    label_oriented = sitk.GetArrayFromImage(label_oriented_sitk)

    return image_oriented, label_oriented, stats


def create_mip_projection(
    image: np.ndarray,
    projection_axes: Optional[List[int]] = None,
    concatenate: bool = True,
) -> Union[np.ndarray, List[np.ndarray]]:
    """
    Create Maximum Intensity Projection (MIP) from 3D image.

    Args:
        image: 3D image array (depth, height, width) or (depth, height, width, channels)
        projection_axes: Axes along which to project (default: [0, 1, 2])
        concatenate: If True, concatenate projections horizontally

    Returns:
        2D MIP projection(s)
    """
    if len(image.shape) < 3:
        raise ValueError("Input image must be at least 3D")

    if projection_axes is None:
        projection_axes = [0, 1, 2]

    # Create projections along specified axes
    projections = []

    for axis in projection_axes:
        if axis < len(image.shape):
            projection = np.max(image, axis=axis)
            projections.append(projection)

    if not projections:
        raise ValueError("No valid projection axes found")

    if concatenate and len(projections) > 1:
        # Concatenate projections horizontally
        return np.concatenate(projections, axis=1)
    elif len(projections) == 1:
        return projections[0]
    else:
        return projections


def max_mip_with_segmentation(
    image: np.ndarray,
    threshold_factor: float = 0.5,
    output_size: List[int] = [96, 96, 96],
) -> Tuple[Union[np.ndarray, List[np.ndarray]], np.ndarray]:
    """
    Create MIP projection with automatic segmentation.

    Args:
        image: 3D input image
        threshold_factor: Factor for automatic thresholding (0.0-1.0)
        output_size: Desired output size for principal plane estimation

    Returns:
        Tuple of (mip_projection, oriented_image)
    """
    # Perform automatic segmentation
    threshold = np.max(image) * threshold_factor
    label = np.zeros_like(image)
    label[image > threshold] = 1

    # Apply principal plane estimation
    image_oriented, _, _ = principal_plane_estimation(
        image, label, output_images_size=output_size
    )

    # Create MIP projection
    mip_projection = create_mip_projection(image_oriented)

    return mip_projection, image_oriented


def save_mip_projection(
    mip_projection: np.ndarray, output_path: str, colormap: str = "inferno"
) -> None:
    """
    Save MIP projection as image file.

    Args:
        mip_projection: 2D MIP projection array
        output_path: Path to save image
        colormap: Matplotlib colormap name
    """
    import os

    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save image
    plt.imsave(output_path, mip_projection, cmap=colormap)


def batch_mip_projection(
    image_paths: List[str],
    output_dir: str,
    threshold_factor: float = 0.5,
    output_size: List[int] = [96, 96, 96],
) -> None:
    """
    Process multiple images to create MIP projections.

    Args:
        image_paths: List of input image file paths
        output_dir: Output directory for MIP projections
        threshold_factor: Threshold factor for segmentation
        output_size: Output size for principal plane estimation
    """
    import os
    import tifffile
    from tqdm import tqdm

    os.makedirs(output_dir, exist_ok=True)

    for image_path in tqdm(image_paths, desc="Creating MIP projections"):
        try:
            # Load image
            image = tifffile.imread(image_path)

            # Create MIP projection
            mip_projection, _ = max_mip_with_segmentation(
                image, threshold_factor, output_size
            )

            # Generate output path
            filename = os.path.basename(image_path)
            name_without_ext = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, f"{name_without_ext}.png")

            # Save MIP projection - ensure we have an ndarray
            if isinstance(mip_projection, list):
                save_mip_projection(mip_projection[0], output_path)
            else:
                save_mip_projection(mip_projection, output_path)

        except Exception as e:
            print(f"Error processing {image_path}: {e}")
