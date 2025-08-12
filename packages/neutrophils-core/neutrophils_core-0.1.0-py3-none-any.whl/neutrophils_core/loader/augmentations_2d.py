import numpy as np
import random
from scipy.ndimage import rotate, shift
from skimage import exposure
from skimage.transform import resize

def random_flip_2d(img_np, mode="horizontal_and_vertical"):
    """
    Apply random flip to 2D image
    
    Args:
        img_np: 2D or 3D numpy array (H, W) or (H, W, C)
        mode: "horizontal", "vertical", or "horizontal_and_vertical"
    
    Returns:
        Flipped image
    """
    if mode == "horizontal" or mode == "horizontal_and_vertical":
        if random.random() > 0.5:
            img_np = np.fliplr(img_np)
    
    if mode == "vertical" or mode == "horizontal_and_vertical":
        if random.random() > 0.5:
            img_np = np.flipud(img_np)
    
    return img_np

def random_rotation_2d(img_np, factor=0.15, background_method='zero'):
    """
    Apply random rotation to 2D image
    
    Args:
        img_np: 2D or 3D numpy array (H, W) or (H, W, C)
        factor: Maximum rotation angle as fraction of 360 degrees
        background_method: 'zero' for zero padding, 'lp' for lower 5th percentile value
    
    Returns:
        Rotated image
    """
    max_angle = factor * 360
    angle = np.random.uniform(-max_angle, max_angle)
    
    # Use scipy.ndimage.rotate for 2D rotation
    if background_method == 'zero':
        cval = 0
    elif background_method == 'lp':
        # use lower 5th percentile value as background
        cval = np.percentile(img_np, 5)
    img_np = rotate(img_np, angle, reshape=False, mode='constant', cval=cval)
    
    return img_np

def random_zoom_2d(img_np, height_factor=0.15, width_factor=0.15, background_method='zero'):
    """
    Apply random zoom to 2D image
    
    Args:
        img_np: 2D or 3D numpy array (H, W) or (H, W, C)
        height_factor: Maximum zoom factor for height
        width_factor: Maximum zoom factor for width
        background_method: 'zero' for zero padding, 'lp' for lower 5th percentile value
    
    Returns:
        Zoomed image
    """
    h, w = img_np.shape[:2]
    
    # Generate random zoom factors
    zoom_h = np.random.uniform(1 - height_factor, 1 + height_factor)
    zoom_w = np.random.uniform(1 - width_factor, 1 + width_factor)
    
    # Calculate new dimensions
    new_h = int(h * zoom_h)
    new_w = int(w * zoom_w)

    # Resize image
    resized = resize(img_np, (new_h, new_w), preserve_range=True, anti_aliasing=True)
    
    # Crop or pad to original size
    # Ensure new_h_actual and new_w_actual are taken from the actual resized image
    new_h_actual, new_w_actual = resized.shape[:2]

    if background_method == 'zero':
        cval = 0
    elif background_method == 'lp':
        cval = np.percentile(img_np, 5)

    if img_np.ndim == 3:
        result = np.ones((h, w, img_np.shape[2]), dtype=resized.dtype) * cval
    else:
        result = np.ones((h, w), dtype=resized.dtype) * cval

    # Calculate source and destination slices for height
    if new_h_actual > h:  # Crop height
        src_h_start = (new_h_actual - h) // 2
        src_h_end = src_h_start + h
        dest_h_start = 0
        dest_h_end = h
    else:  # Pad height (or exact match)
        src_h_start = 0
        src_h_end = new_h_actual
        dest_h_start = (h - new_h_actual) // 2
        dest_h_end = dest_h_start + new_h_actual
    
    # Calculate source and destination slices for width
    if new_w_actual > w:  # Crop width
        src_w_start = (new_w_actual - w) // 2
        src_w_end = src_w_start + w
        dest_w_start = 0
        dest_w_end = w
    else:  # Pad width (or exact match)
        src_w_start = 0
        src_w_end = new_w_actual
        dest_w_start = (w - new_w_actual) // 2
        dest_w_end = dest_w_start + new_w_actual

    # Apply the slices
    if img_np.ndim == 3:
        result[dest_h_start:dest_h_end, dest_w_start:dest_w_end, :] = \
            resized[src_h_start:src_h_end, src_w_start:src_w_end, :]
    else:
        result[dest_h_start:dest_h_end, dest_w_start:dest_w_end] = \
            resized[src_h_start:src_h_end, src_w_start:src_w_end]
    return result

def random_contrast_2d(img_np, factor=0.15):
    """
    Apply random contrast adjustment to 2D image (OVERFLOW-SAFE VERSION)
    
    Args:
        img_np: 2D or 3D numpy array (H, W) or (H, W, C)
        factor: Maximum contrast adjustment factor
    
    Returns:
        Contrast-adjusted image as float32
    """
    # Convert to float32 and ensure [0,1] range
    img_float = img_np.astype(np.float32)
    if img_float.max() > 1.0:
        img_float = img_float / img_float.max()
    
    # Generate random contrast factor
    contrast_factor = np.random.uniform(1 - factor, 1 + factor)
    
    # Use fixed midpoint for consistent behavior in [0,1] range
    mean_val = 0.5
    
    # Apply contrast adjustment
    img_contrast = (img_float - mean_val) * contrast_factor + mean_val
    
    # Clip to valid range [0,1] to prevent overflow
    return np.clip(img_contrast, 0.0, 1.0).astype(np.float32)

def random_brightness_2d(img_np, factor=0.15):
    """
    Apply random brightness adjustment to 2D image (OVERFLOW-SAFE VERSION)
    
    Args:
        img_np: 2D or 3D numpy array (H, W) or (H, W, C)
        factor: Maximum brightness adjustment factor
    
    Returns:
        Brightness-adjusted image as float32
    """
    # Convert to float32
    img_float = img_np.astype(np.float32)
    
    # Determine the original data range for proper normalization
    original_min = img_float.min()
    original_max = img_float.max()
    
    # Handle edge cases
    if original_max == original_min:
        # Uniform image - return as is (no brightness change meaningful)
        if original_max <= 1.0:
            return img_float
        else:
            return np.full_like(img_float, 0.5, dtype=np.float32)
    
    # Apply min-max normalization to [0,1] range for stable brightness adjustment
    img_normalized = (img_float - original_min) / (original_max - original_min)
    
    # Generate random brightness factor
    brightness_factor = np.random.uniform(-factor, factor)
    
    # Apply brightness adjustment
    img_bright = img_normalized + brightness_factor
    
    # normalize the brightness-adjusted image back to [0,1] range
    img_bright_clipped = (img_bright- np.min(img_bright))/(np.max(img_bright) - np.min(img_bright))
    
    return img_bright_clipped.astype(np.float32)

def random_translation_2d(img_np, height_factor=0.1, width_factor=0.1, background_method = "zero"):
    """
    Apply random translation to 2D image
    
    Args:
        img_np: 2D or 3D numpy array (H, W) or (H, W, C)
        height_factor: Maximum translation factor for height (as fraction of image height)
        width_factor: Maximum translation factor for width (as fraction of image width)
        background_method: 'zero' for zero padding, 'lp' for lower 5th percentile value

    Returns:
        Translated image
    """
    h, w = img_np.shape[:2]
    
    # Generate random translation values as pixels
    max_shift_h = int(h * height_factor)
    max_shift_w = int(w * width_factor)
    
    shift_h = np.random.randint(-max_shift_h, max_shift_h + 1)
    shift_w = np.random.randint(-max_shift_w, max_shift_w + 1)
    
    if background_method == 'zero':
        cval = 0
    elif background_method == 'lp':
        # use lower 5th percentile value as background
        cval = np.percentile(img_np, 5)

    # Apply translation using scipy.ndimage.shift
    if img_np.ndim == 3:
        # For 3D arrays (H, W, C), shift only the first two dimensions
        shifted = shift(img_np, [shift_h, shift_w, 0], mode='constant', cval=cval)
    else:
        # For 2D arrays (H, W)
        shifted = shift(img_np, [shift_h, shift_w], mode='constant', cval=cval)
    
    return shifted