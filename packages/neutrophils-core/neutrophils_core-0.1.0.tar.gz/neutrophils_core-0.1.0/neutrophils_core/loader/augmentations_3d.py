"""
3D Augmentation functions for neutrophil classification.

This module provides GPU-accelerated 3D augmentation functions using CUDA kernels
for efficient processing of 3D microscopy volumes.

Functions:
    - noise: Add Gaussian noise to volumes
    - rotate: 3D rotation with trilinear interpolation
    - zoom: 3D zoom with trilinear interpolation
    - offset: Random 3D translation
    - blur: Gaussian blur filtering
    - swap_axes: Random axis swapping

Requirements:
    - numpy
    - scipy
    - numba with CUDA support
"""

import numpy as np
import random
from scipy.ndimage import zoom as scipy_zoom, rotate as scipy_rotate, gaussian_filter
from numba import cuda
import math
import gc
from typing import Optional, Tuple, List
import tensorflow as tf


def noise(img_np: np.ndarray, std_factor: float = 0.1) -> np.ndarray:
    """
    Add Gaussian noise to a 3D volume. The noise standard deviation is based on the
    1st percentile of the non-zero pixel values to increase robustness against images
    with a high number of zero-value pixels.
    
    Args:
        img_np: Input 3D numpy array.
        std_factor: Noise standard deviation as a factor of the 1st percentile of non-zero pixels.
        
    Returns:
        Noisy 3D volume.
    """
    non_zero_pixels = img_np[img_np > 0]

    if non_zero_pixels.size == 0:
        # If there are no non-zero pixels, no noise is added.
        return img_np

    percentile_val = np.percentile(non_zero_pixels, 1)
    noise_std = percentile_val * std_factor
    
    noise_array = np.random.normal(0, noise_std, img_np.shape)
    img_res = img_np + noise_array
    
    # Squeeze output back to input range to avoid overflow
    if np.issubdtype(img_np.dtype, np.integer):
        img_min = np.iinfo(img_np.dtype).min
        img_max = np.iinfo(img_np.dtype).max
        img_res = np.clip(img_res, img_min, img_max)

    return img_res

def swap_axes(img_np: np.ndarray, swap_pair: Optional[List[int]] = None) -> np.ndarray:
    """
    Randomly swap two axes of a 3D volume.
    
    Args:
        img_np: Input 3D numpy array
        swap_pair: Specific axes to swap, if None, random pair is chosen
        
    Returns:
        Volume with swapped axes
    """
    if swap_pair is None:
        swap_pairs = [[0, 1], [0, 2], [1, 2]]
        swap_pair = random.choice(swap_pairs)
    
    return np.swapaxes(img_np, swap_pair[0], swap_pair[1])


def rotate_cpu(img_np: np.ndarray, degree_max: float = 90) -> np.ndarray:
    """
    CPU-based 3D rotation (slower, use only when GPU not available).
    
    Args:
        img_np: Input 3D numpy array
        degree_max: Maximum rotation angle in degrees
        
    Returns:
        Rotated 3D volume
    """
    angle = np.random.uniform(-degree_max, degree_max)
    
    for i, axis in enumerate([(0, 1), (0, 2), (1, 2)]):
        img_np = scipy_rotate(img_np, angle, axes=axis, reshape=(i != 2), mode='nearest')
    
    return img_np


@cuda.jit
def rotate_3d_trilinear_kernel(image, rotated_image, theta_x, theta_y, theta_z):
    """
    CUDA kernel for 3D rotation with trilinear interpolation.
    
    Args:
        image: Input 3D array on GPU
        rotated_image: Output 3D array on GPU
        theta_x, theta_y, theta_z: Rotation angles in radians for each axis
    """
    x, y, z = cuda.grid(3)
    
    if x < image.shape[0] and y < image.shape[1] and z < image.shape[2]:
        # Center coordinates around origin
        cx, cy, cz = image.shape[0] // 2, image.shape[1] // 2, image.shape[2] // 2
        x0, y0, z0 = x - cx, y - cy, z - cz

        # Apply rotation around x-axis
        x1, y1, z1 = x0, \
                     y0 * math.cos(theta_x) - z0 * math.sin(theta_x), \
                     y0 * math.sin(theta_x) + z0 * math.cos(theta_x)

        # Apply rotation around y-axis
        x2, y2, z2 = x1 * math.cos(theta_y) + z1 * math.sin(theta_y), \
                     y1, \
                     -x1 * math.sin(theta_y) + z1 * math.cos(theta_y)

        # Apply rotation around z-axis
        x3, y3, z3 = x2 * math.cos(theta_z) - y2 * math.sin(theta_z), \
                     x2 * math.sin(theta_z) + y2 * math.cos(theta_z), \
                     z2
        
        # Translate coordinates back
        new_x, new_y, new_z = x3 + cx, y3 + cy, z3 + cz

        # Bounds checking and trilinear interpolation
        if 0 <= new_x < image.shape[0] - 1 and 0 <= new_y < image.shape[1] - 1 and 0 <= new_z < image.shape[2] - 1:
            x0 = int(math.floor(new_x))
            x1 = min(x0 + 1, image.shape[0] - 1)
            y0 = int(math.floor(new_y))
            y1 = min(y0 + 1, image.shape[1] - 1)
            z0 = int(math.floor(new_z))
            z1 = min(z0 + 1, image.shape[2] - 1)

            xd = new_x - x0
            yd = new_y - y0
            zd = new_z - z0

            # Trilinear interpolation
            c00 = image[x0, y0, z0] * (1 - xd) + image[x1, y0, z0] * xd
            c01 = image[x0, y0, z1] * (1 - xd) + image[x1, y0, z1] * xd
            c10 = image[x0, y1, z0] * (1 - xd) + image[x1, y1, z0] * xd
            c11 = image[x0, y1, z1] * (1 - xd) + image[x1, y1, z1] * xd

            c0 = c00 * (1 - yd) + c10 * yd
            c1 = c01 * (1 - yd) + c11 * yd

            c = c0 * (1 - zd) + c1 * zd

            rotated_image[x, y, z] = c


def rotate(img_np: np.ndarray, degree_max: float = 90) -> np.ndarray:
    """
    GPU-accelerated 3D rotation with trilinear interpolation.
    
    Args:
        img_np: Input 3D numpy array
        degree_max: Maximum rotation angle in degrees
        
    Returns:
        Rotated 3D volume
    """
    # Allocate memory for rotated image
    rotated_image = np.zeros_like(img_np)

    # Copy arrays to GPU
    d_image = cuda.to_device(img_np)
    d_rotated_image = cuda.to_device(rotated_image)

    # Configure CUDA grid
    threads_per_block = (8, 8, 8)
    blocks_per_grid_x = int(np.ceil(img_np.shape[0] / threads_per_block[0]))
    blocks_per_grid_y = int(np.ceil(img_np.shape[1] / threads_per_block[1]))
    blocks_per_grid_z = int(np.ceil(img_np.shape[2] / threads_per_block[2]))
    blocks_per_grid = (blocks_per_grid_x, blocks_per_grid_y, blocks_per_grid_z)

    # Generate random rotation angles
    theta_x = np.radians(np.random.randint(-degree_max, degree_max))
    theta_y = np.radians(np.random.randint(-degree_max, degree_max))
    theta_z = np.radians(np.random.randint(-degree_max, degree_max))

    # Launch CUDA kernel
    rotate_3d_trilinear_kernel[blocks_per_grid, threads_per_block](
        d_image, d_rotated_image, theta_x, theta_y, theta_z
    )

    # Copy result back to host
    result_image = d_rotated_image.copy_to_host()

    return result_image


def offset(img_np: np.ndarray, px_max: int = 3) -> np.ndarray:
    """
    Apply random 3D translation offset.
    
    Args:
        img_np: Input 3D numpy array
        px_max: Maximum offset in pixels for each axis
        
    Returns:
        Translated 3D volume
    """
    offset_x = random.choice(np.arange(-px_max, px_max + 1))
    offset_y = random.choice(np.arange(-px_max, px_max + 1))
    offset_z = random.choice(np.arange(-px_max, px_max + 1))
    
    img_np = np.roll(img_np, offset_x, axis=0)
    img_np = np.roll(img_np, offset_y, axis=1)
    img_np = np.roll(img_np, offset_z, axis=2)
    
    return img_np


def zoom_cpu(img_np: np.ndarray, zoom_factor: float = 0.05) -> np.ndarray:
    """
    CPU-based 3D zoom (slower, use only when GPU not available).
    
    Args:
        img_np: Input 3D numpy array
        zoom_factor: Maximum zoom variation factor
        
    Returns:
        Zoomed 3D volume
    """
    zoom_val = np.random.uniform(1 - zoom_factor, 1 + zoom_factor)
    return scipy_zoom(img_np, zoom_val)


@cuda.jit(max_registers=40)
def zoom_3d_trilinear_kernel(image, zoomed_image, zoom_factor):
    """
    CUDA kernel for 3D zoom with trilinear interpolation.
    
    Args:
        image: Input 3D array on GPU
        zoomed_image: Output 3D array on GPU
        zoom_factor: Zoom scaling factor
    """
    x, y, z = cuda.grid(3)

    if x < zoomed_image.shape[0] and y < zoomed_image.shape[1] and z < zoomed_image.shape[2]:
        # Calculate image centers
        orig_center_x = image.shape[0] / 2
        orig_center_y = image.shape[1] / 2
        orig_center_z = image.shape[2] / 2
        zoomed_center_x = zoomed_image.shape[0] / 2
        zoomed_center_y = zoomed_image.shape[1] / 2
        zoomed_center_z = zoomed_image.shape[2] / 2

        # Calculate original coordinates
        orig_x = (x - zoomed_center_x) / zoom_factor + orig_center_x
        orig_y = (y - zoomed_center_y) / zoom_factor + orig_center_y
        orig_z = (z - zoomed_center_z) / zoom_factor + orig_center_z

        # Bounds checking and trilinear interpolation
        if 0 <= orig_x < image.shape[0] - 1 and 0 <= orig_y < image.shape[1] - 1 and 0 <= orig_z < image.shape[2] - 1:
            x0 = int(math.floor(orig_x))
            x1 = min(x0 + 1, image.shape[0] - 1)
            y0 = int(math.floor(orig_y))
            y1 = min(y0 + 1, image.shape[1] - 1)
            z0 = int(math.floor(orig_z))
            z1 = min(z0 + 1, image.shape[2] - 1)

            xd = orig_x - x0
            yd = orig_y - y0
            zd = orig_z - z0

            # Trilinear interpolation
            c00 = image[x0, y0, z0] * (1 - xd) + image[x1, y0, z0] * xd
            c01 = image[x0, y0, z1] * (1 - xd) + image[x1, y0, z1] * xd
            c10 = image[x0, y1, z0] * (1 - xd) + image[x1, y1, z0] * xd
            c11 = image[x0, y1, z1] * (1 - xd) + image[x1, y1, z1] * xd

            c0 = c00 * (1 - yd) + c10 * yd
            c1 = c01 * (1 - yd) + c11 * yd

            c = c0 * (1 - zd) + c1 * zd

            zoomed_image[x, y, z] = c


def zoom(img_np: np.ndarray, zoom_factor: float = 0.05) -> np.ndarray:
    """
    GPU-accelerated 3D zoom with trilinear interpolation.
    
    Args:
        img_np: Input 3D numpy array
        zoom_factor: Maximum zoom variation factor
        
    Returns:
        Zoomed 3D volume
    """
    zoom_val = np.random.uniform(1 - zoom_factor, 1 + zoom_factor)
    
    # Allocate memory for zoomed image
    zoomed_image = np.zeros_like(img_np)

    # Copy arrays to GPU
    d_image = cuda.to_device(img_np)
    d_zoomed_image = cuda.to_device(zoomed_image)

    # Configure CUDA grid
    threads_per_block = (8, 8, 8)
    blocks_per_grid_x = int(np.ceil(img_np.shape[0] / threads_per_block[0]))
    blocks_per_grid_y = int(np.ceil(img_np.shape[1] / threads_per_block[1]))
    blocks_per_grid_z = int(np.ceil(img_np.shape[2] / threads_per_block[2]))
    blocks_per_grid = (blocks_per_grid_x, blocks_per_grid_y, blocks_per_grid_z)

    # Launch CUDA kernel
    zoom_3d_trilinear_kernel[blocks_per_grid, threads_per_block](
        d_image, d_zoomed_image, zoom_val
    )

    # Copy result back to host
    result_image = d_zoomed_image.copy_to_host()

    return result_image


def blur(img_np: np.ndarray, kernel_sz: int = 2) -> np.ndarray:
    """
    Apply random Gaussian blur to 3D volume.
    
    Args:
        img_np: Input 3D numpy array
        kernel_sz: Maximum kernel size for Gaussian filter
        
    Returns:
        Blurred 3D volume
    """
    sigma = random.choice(np.arange(0, kernel_sz))
    return gaussian_filter(img_np, sigma=sigma)


# Convenience function for applying multiple augmentations
def apply_augmentations(img_np: np.ndarray, 
                       augmentation_order: List[str],
                       augmentation_params: dict) -> np.ndarray:
    """
    Apply a sequence of augmentations to a 3D volume.
    
    Args:
        img_np: Input 3D numpy array
        augmentation_order: List of augmentation function names to apply
        augmentation_params: Dictionary of parameters for each augmentation
        
    Returns:
        Augmented 3D volume
    """
    augmentation_functions = {
        'noise': noise,
        'rotate': rotate,
        'zoom': zoom,
        'offset': offset,
        'blur': blur,
        'swap_axes': swap_axes
    }
    
    result = img_np.copy()
    
    for aug_name in augmentation_order:
        if aug_name in augmentation_functions:
            params = augmentation_params.get(aug_name, {})
            result = augmentation_functions[aug_name](result, **params)

    return result

# --- TensorFlow-based GPU Augmentations ---

@tf.function
def _trilinear_interpolate_tf(image: tf.Tensor, coords: tf.Tensor) -> tf.Tensor:
    """Trilinear interpolation for 3D image sampling using TensorFlow."""
    batch_size = tf.shape(image)[0]
    height, width, depth = tf.shape(image)[1], tf.shape(image)[2], tf.shape(image)[3]
    
    y_coords, x_coords, z_coords = coords[..., 0], coords[..., 1], coords[..., 2]
    
    y0 = tf.cast(tf.floor(y_coords), tf.int32)
    x0 = tf.cast(tf.floor(x_coords), tf.int32)
    z0 = tf.cast(tf.floor(z_coords), tf.int32)
    
    y1, x1, z1 = y0 + 1, x0 + 1, z0 + 1
    
    y0 = tf.clip_by_value(y0, 0, height - 1)
    y1 = tf.clip_by_value(y1, 0, height - 1)
    x0 = tf.clip_by_value(x0, 0, width - 1)
    x1 = tf.clip_by_value(x1, 0, width - 1)
    z0 = tf.clip_by_value(z0, 0, depth - 1)
    z1 = tf.clip_by_value(z1, 0, depth - 1)
    
    y_frac = y_coords - tf.cast(y0, tf.float32)
    x_frac = x_coords - tf.cast(x0, tf.float32)
    z_frac = z_coords - tf.cast(z0, tf.float32)
    
    def gather_corner(y_idx, x_idx, z_idx):
        batch_indices = tf.range(batch_size)[:, None, None, None]
        batch_indices = tf.tile(batch_indices, [1, tf.shape(y_idx)[1], tf.shape(y_idx)[2], tf.shape(y_idx)[3]])
        indices = tf.stack([batch_indices, y_idx, x_idx, z_idx], axis=-1)
        return tf.gather_nd(image, indices)

    c000 = gather_corner(y0, x0, z0)
    c001 = gather_corner(y0, x0, z1)
    c010 = gather_corner(y0, x1, z0)
    c011 = gather_corner(y0, x1, z1)
    c100 = gather_corner(y1, x0, z0)
    c101 = gather_corner(y1, x0, z1)
    c110 = gather_corner(y1, x1, z0)
    c111 = gather_corner(y1, x1, z1)

    c00 = c000 * (1 - x_frac) + c010 * x_frac
    c01 = c001 * (1 - x_frac) + c011 * x_frac
    c10 = c100 * (1 - x_frac) + c110 * x_frac
    c11 = c101 * (1 - x_frac) + c111 * x_frac
    
    c0 = c00 * (1 - z_frac) + c01 * z_frac
    c1 = c10 * (1 - z_frac) + c11 * z_frac
    
    return c0 * (1 - y_frac) + c1 * y_frac

@tf.function
def _rotate_3d_around_center_tf(image: tf.Tensor, theta_x: tf.Tensor, theta_y: tf.Tensor, theta_z: tf.Tensor) -> tf.Tensor:
    """Apply 3D rotation around image center using trilinear interpolation."""
    shape = tf.shape(image)
    height, width, depth = shape[0], shape[1], shape[2]
    
    y_coords, x_coords, z_coords = tf.range(height, dtype=tf.float32), tf.range(width, dtype=tf.float32), tf.range(depth, dtype=tf.float32)
    y_grid, x_grid, z_grid = tf.meshgrid(y_coords, x_coords, z_coords, indexing='ij')
    
    center_y, center_x, center_z = tf.cast(height, tf.float32) / 2.0, tf.cast(width, tf.float32) / 2.0, tf.cast(depth, tf.float32) / 2.0
    y_centered, x_centered, z_centered = y_grid - center_y, x_grid - center_x, z_grid - center_z
    
    cos_x, sin_x = tf.cos(theta_x), tf.sin(theta_x)
    y1 = y_centered * cos_x - z_centered * sin_x
    z1 = y_centered * sin_x + z_centered * cos_x
    
    cos_y, sin_y = tf.cos(theta_y), tf.sin(theta_y)
    x2 = x_centered * cos_y + z1 * sin_y
    z2 = -x_centered * sin_y + z1 * cos_y
    
    cos_z, sin_z = tf.cos(theta_z), tf.sin(theta_z)
    x3 = x2 * cos_z - y1 * sin_z
    y3 = x2 * sin_z + y1 * cos_z
    
    new_y, new_x, new_z = y3 + center_y, x3 + center_x, z2 + center_z
    
    coords = tf.stack([new_y, new_x, new_z], axis=-1)
    
    image_batch = tf.expand_dims(image, 0)
    coords_batch = tf.expand_dims(coords, 0)
    
    rotated = _trilinear_interpolate_tf(image_batch, coords_batch)
    
    return tf.squeeze(rotated, 0)

@tf.function
def noise_tf(image: tf.Tensor, std_dev: float, intensity_range: Tuple[float, float]) -> tf.Tensor:
    """Adds Gaussian noise to a 3D image tensor."""
    scaled_std_dev = std_dev * (intensity_range[1] - intensity_range[0])
    noise = tf.random.normal(tf.shape(image), stddev=scaled_std_dev)
    return image + noise

@tf.function
def brightness_tf(image: tf.Tensor, max_delta: float, intensity_range: Tuple[float, float]) -> tf.Tensor:
    """Adjusts brightness of a 3D image tensor."""
    scaled_delta = max_delta * (intensity_range[1] - intensity_range[0])
    delta = tf.random.uniform([], -scaled_delta, scaled_delta)
    return image + delta

@tf.function
def contrast_tf(image: tf.Tensor, contrast_range: Tuple[float, float]) -> tf.Tensor:
    """Adjusts contrast of a 3D image tensor."""
    factor = tf.random.uniform([], contrast_range[0], contrast_range[1])
    return image * factor

@tf.function
def rotate_tf(image: tf.Tensor, max_angle_deg: float) -> tf.Tensor:
    """Applies 3D rotation to an image tensor."""
    if tf.random.uniform([]) < 0.5:
        pi = tf.constant(np.pi, dtype=tf.float32)
        max_angle_rad = max_angle_deg * (pi / 180.0)
        
        theta_x = tf.random.uniform([], -max_angle_rad, max_angle_rad)
        theta_y = tf.random.uniform([], -max_angle_rad, max_angle_rad)
        theta_z = tf.random.uniform([], -max_angle_rad, max_angle_rad)
        
        return _rotate_3d_around_center_tf(image, theta_x, theta_y, theta_z)
    return image

def apply_gpu_augmentations(image: tf.Tensor, 
                            augmentation_order: List[str],
                            augmentation_params: dict,
                            intensity_out_range: Tuple[float, float]) -> tf.Tensor:
    """
    Apply a sequence of GPU-accelerated augmentations to a 3D image tensor.
    """
    img = tf.squeeze(image, axis=-1)

    augmentation_functions = {
        'noise': lambda img, p: noise_tf(img, std_dev=p.get('std_factor', 0.1), intensity_range=intensity_out_range),
        'brightness': lambda img, p: brightness_tf(img, max_delta=p.get('brightness_range', 0.1), intensity_range=intensity_out_range),
        'contrast': lambda img, p: contrast_tf(img, contrast_range=p.get('contrast_range', (0.9, 1.1))),
        'rotate': lambda img, p: rotate_tf(img, max_angle_deg=p.get('degree_max', 15.0)),
    }
    
    for aug_name in augmentation_order:
        if aug_name in augmentation_functions:
            params = augmentation_params.get(aug_name, {})
            img = augmentation_functions[aug_name](img, params)
            
    img = tf.clip_by_value(img, intensity_out_range[0], intensity_out_range[1])
    return tf.expand_dims(img, axis=-1)