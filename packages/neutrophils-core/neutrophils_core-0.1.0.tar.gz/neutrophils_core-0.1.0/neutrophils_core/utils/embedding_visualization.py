"""
Embedding Visualization Utilities for Contrastive Learning

This module provides utilities for extracting and visualizing embeddings from trained models,
specifically designed for contrastive learning applications including:
- Embedding extraction from trained models
- Dimensionality reduction (PCA, t-SNE)
- MIP image visualization with embedding positions
- Class-colored visualization for labeled data
- Adaptive visualization based on dataset size
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import json
from tqdm import tqdm


def extract_balanced_samples_by_class(generator, model, samples_per_class: int = 10) -> Tuple[np.ndarray, np.ndarray, List[str], np.ndarray]:
    """
    Extract balanced samples from each class for debug visualization.
    
    Args:
        generator: Labeled data generator with df attribute
        model: Trained encoder model
        samples_per_class: Number of samples to extract per class
        
    Returns:
        embeddings: numpy array of embeddings
        labels: numpy array of labels
        filenames: list of filenames
        images: numpy array of images
    """
    if not hasattr(generator, 'df'):
        raise ValueError("Generator must have 'df' attribute for balanced sampling")
    
    df = generator.df
    target_classes = [0, 1, 2, 3]  # M, MM, BN, SN
    class_names = {0: "M", 1: "MM", 2: "BN", 3: "SN"}
    
    # Debug: Print DataFrame columns and sample to understand structure
    print(f"DataFrame columns: {list(df.columns)}")
    print(f"DataFrame shape: {df.shape}")
    if len(df) > 0:
        print("Sample rows:")
        print(df.head())
    
    # Try to identify the correct label column name
    label_column = None
    possible_label_columns = ['label', 'class', 'target', 'y', 'labels', 'class_label', 'stage']
    
    for col in possible_label_columns:
        if col in df.columns:
            label_column = col
            print(f"Found label column: {label_column}")
            break
    
    if label_column is None:
        print("Error: Could not find label column in DataFrame")
        print("Available columns:", list(df.columns))
        # Fallback to original batch-based approach
        print("Falling back to batch-based sampling...")
        return extract_embeddings_fallback(generator, model, debug=True)
    
    all_embeddings = []
    all_labels = []
    all_filenames = []
    all_images = []
    
    print("Performing balanced sampling by class...")
    
    # Check unique values in label column
    unique_labels = df[label_column].unique()
    print(f"Unique labels found: {sorted(unique_labels)}")
    
    # Create mapping from string labels to integer indices
    string_to_int_mapping = {"M": 0, "MM": 1, "BN": 2, "SN": 3}
    int_to_string_mapping = {0: "M", 1: "MM", 2: "BN", 3: "SN"}
    
    for class_idx in target_classes:
        # Get samples for this class - handle both string and integer labels
        class_string = int_to_string_mapping[class_idx]
        class_mask = (df[label_column] == class_idx) | (df[label_column] == class_string)
        class_df = df[class_mask]
        
        if len(class_df) == 0:
            print(f"Warning: No samples found for class {class_names[class_idx]} ({class_idx})")
            continue
            
        # Sample up to samples_per_class from this class
        n_samples = min(samples_per_class, len(class_df))
        sampled_df = class_df.sample(n=n_samples, random_state=42)
        
        print(f"Sampling {n_samples} samples from class {class_names[class_idx]} ({class_idx})")
        
        # Create a temporary generator for this class
        class_embeddings = []
        class_labels = []
        class_filenames = []
        class_images = []
        
        for idx, row in sampled_df.iterrows():
            try:
                # Try different possible image path column names
                image_path = None
                possible_path_columns = ['image_path', 'path', 'file_path', 'filename', 'filepath']
                
                for path_col in possible_path_columns:
                    if path_col in row and row[path_col] is not None:
                        image_path = row[path_col]
                        break
                
                if image_path is None:
                    print(f"Warning: Could not find image path in row {idx}")
                    continue
                
                # Construct full path by combining with generator's data directory
                if hasattr(generator, 'data_dir'):
                    full_image_path = Path(generator.data_dir) / image_path
                elif hasattr(generator, 'directory'):
                    full_image_path = Path(generator.directory) / image_path
                else:
                    # Fallback to relative path
                    full_image_path = Path(image_path)
                
                # Use generator's preprocessing if available
                if hasattr(generator, 'load_and_preprocess_image'):
                    image = generator.load_and_preprocess_image(str(full_image_path))
                else:
                    # Fallback: basic image loading using tifffile (better for TIFF images)
                    try:
                        import tifffile
                        from skimage import transform
                        from skimage.util import img_as_float32
                        
                        # Load TIFF image using tifffile
                        image = tifffile.imread(str(full_image_path))
                        
                        # Handle different image dimensions for 3D data
                        if len(image.shape) == 3:
                            # For 3D volumes, keep as is (this is what we expect for 3D models)
                            pass
                        elif len(image.shape) == 2:
                            # For 2D images, add channel dimension if needed
                            if hasattr(generator, 'use_mip') and not generator.use_mip:
                                # For 3D models expecting 3D input, we need to handle this differently
                                # This shouldn't happen with proper 3D TIFF files
                                print(f"Warning: 2D image found but 3D expected: {full_image_path}")
                                continue
                            else:
                                # For 2D/MIP processing, convert to RGB
                                image = np.stack([image] * 3, axis=-1)
                        
                        # Resize to expected input size if needed
                        if hasattr(generator, 'target_size'):
                            target_size = generator.target_size
                        elif hasattr(generator, 'image_size'):
                            # For 3D data, target_size should be (image_size, image_size, image_size)
                            img_size = generator.image_size
                            if len(image.shape) == 3 and image.shape[0] == image.shape[1] == image.shape[2]:
                                target_size = (img_size, img_size, img_size)
                            else:
                                target_size = (img_size, img_size)
                        else:
                            target_size = (69, 69, 69)  # Default 3D size
                        
                        # Resize image if necessary
                        if image.shape != target_size:
                            if len(target_size) == 3 and len(image.shape) == 3:
                                # 3D resize
                                image = transform.resize(image, target_size,
                                                       anti_aliasing=True,
                                                       preserve_range=True)
                            elif len(target_size) == 2 and len(image.shape) == 3:
                                # 2D resize for MIP data
                                image = transform.resize(image, target_size + (image.shape[2],),
                                                       anti_aliasing=True,
                                                       preserve_range=True)
                        
                        # Convert to float32 and normalize to [0, 1]
                        image = img_as_float32(image)
                        
                        # Add channel dimension for 3D data if needed
                        if len(image.shape) == 3 and len(target_size) == 3:
                            image = np.expand_dims(image, axis=-1)  # Add channel dimension
                        
                    except ImportError:
                        print("Error: tifffile not available. Please install with: pip install tifffile")
                        # Fallback to scikit-image
                        try:
                            from skimage import io, transform
                            from skimage.util import img_as_float32
                            
                            image = io.imread(str(full_image_path))
                            image = img_as_float32(image)
                            if len(image.shape) == 3 and image.shape[0] == image.shape[1] == image.shape[2]:
                                image = np.expand_dims(image, axis=-1)
                        except Exception as e:
                            print(f"Warning: Could not load image {full_image_path} with fallback method: {e}")
                            continue
                    except Exception as e:
                        print(f"Warning: Could not load image {full_image_path} with tifffile: {e}")
                        continue
                
                # Add batch dimension
                image_batch = np.expand_dims(image, axis=0)
                
                # Extract embedding
                embedding = model(image_batch, training=False)
                embedding_np = embedding.numpy()
                
                class_embeddings.append(embedding_np[0])  # Remove batch dimension
                class_labels.append(class_idx)  # Use integer class index
                class_filenames.append(str(image_path))  # Store original relative path
                class_images.append(image)
                
            except Exception as e:
                print(f"Error processing image {full_image_path}: {e}")
                continue
        
        if class_embeddings:
            all_embeddings.extend(class_embeddings)
            all_labels.extend(class_labels)
            all_filenames.extend(class_filenames)
            all_images.extend(class_images)
    
    if all_embeddings:
        embeddings = np.array(all_embeddings)
        labels = np.array(all_labels)
        images = np.array(all_images)
        
        # Print final class distribution
        unique_classes, class_counts = np.unique(labels, return_counts=True)
        print("Final balanced class distribution:")
        for class_idx, count in zip(unique_classes, class_counts):
            class_name = class_names.get(class_idx, f"Class_{class_idx}")
            print(f"  {class_name} (class {class_idx}): {count} samples")
        
        return embeddings, labels, all_filenames, images
    else:
        return np.array([]), np.array([]), [], np.array([])


def extract_embeddings_fallback(generator, model, debug: bool = True) -> Tuple[np.ndarray, np.ndarray, List[str], np.ndarray]:
    """
    Fallback function for extracting embeddings when balanced sampling fails.
    """
    embeddings_list = []
    labels_list = []
    filenames_list = []
    images_list = []
    
    print("Using fallback batch-based extraction...")
    
    # Process more batches to increase chance of finding all classes
    max_batches = 20 if debug else 3
    
    for batch_idx in tqdm(range(max_batches), desc="Extracting embeddings (fallback)"):
        try:
            # Get batch from labeled generator
            batch = generator.get_contrastive_batch()
            X = batch['X1']  # Use first augmentation
            batch_labels = batch.get('labels', None)
            
            # Use the augmented images as fallback since original method may not exist
            batch_images = X
            
            # Get filenames if available
            if hasattr(generator, 'get_batch_filenames'):
                batch_filenames = generator.get_batch_filenames()
            else:
                batch_filenames = [f"labeled_sample_{batch_idx}_{i}" for i in range(len(X))]
            
            # Extract embeddings
            embeddings = model(X, training=False)
            embeddings_np = embeddings.numpy()
            
            embeddings_list.append(embeddings_np)
            if batch_labels is not None:
                labels_list.append(batch_labels)
            filenames_list.extend(batch_filenames)
            images_list.append(batch_images)
            
        except Exception as e:
            print(f"Error processing batch {batch_idx}: {e}")
            continue
    
    # Concatenate all embeddings and images
    if embeddings_list:
        embeddings = np.concatenate(embeddings_list, axis=0)
        labels = np.concatenate(labels_list, axis=0) if labels_list else None
        images = np.concatenate(images_list, axis=0) if images_list else np.array([])
    else:
        embeddings = np.array([])
        labels = None
        images = np.array([])
    
    return embeddings, labels, filenames_list, images


def extract_embeddings(model,
                      generator,
                      data_type: str = "labeled",
                      max_samples: Optional[int] = None,
                      debug: bool = False) -> Tuple[np.ndarray, Optional[np.ndarray], List[str], np.ndarray]:
    """
    Extract embeddings from the trained model for a given data generator.
    
    Args:
        model: Trained encoder model
        generator: Data generator (labeled or unlabeled)
        data_type: "labeled" or "unlabeled"
        max_samples: Maximum number of samples to extract (None for all)
        debug: Whether to run in debug mode with balanced class sampling
        
    Returns:
        embeddings: numpy array of embeddings
        labels: numpy array of labels (None for unlabeled data)
        filenames: list of filenames
        images: numpy array of original images (for visualization)
    """
    # Use balanced sampling for labeled data in debug mode
    if debug and data_type == "labeled" and hasattr(generator, 'df'):
        print("Debug mode: Using balanced sampling by class...")
        return extract_balanced_samples_by_class(generator, model, samples_per_class=15)
    
    # Original implementation for non-debug mode or unlabeled data
    embeddings_list = []
    labels_list = []
    filenames_list = []
    images_list = []
    
    # Determine number of batches to process
    if hasattr(generator, 'df'):
        total_samples = len(generator.df)
        batch_size = generator.batch_size
    else:
        total_samples = 1000  # Fallback estimate
        batch_size = 32  # Default batch size
    
    num_batches = min(
        (total_samples + batch_size - 1) // batch_size,
        (max_samples + batch_size - 1) // batch_size if max_samples else float('inf')
    )
    
    # Limit batches in debug mode for unlabeled data
    if debug:
        num_batches = min(num_batches, 3)
        print(f"Processing {num_batches} batches for {data_type} data (debug mode)...")
    else:
        print(f"Processing {num_batches} batches for {data_type} data...")
    
    samples_processed = 0
    for batch_idx in tqdm(range(int(num_batches)), desc=f"Extracting {data_type} embeddings"):
        try:
            if data_type == "labeled":
                # Get batch from labeled generator
                batch = generator.get_contrastive_batch()
                X = batch['X1']  # Use first augmentation
                batch_labels = batch.get('labels', None)
                
                # Use the augmented images as fallback since original method may not exist
                batch_images = X
                
                # Get filenames if available
                if hasattr(generator, 'get_batch_filenames'):
                    batch_filenames = generator.get_batch_filenames()
                else:
                    batch_filenames = [f"labeled_sample_{samples_processed + i}" for i in range(len(X))]
                
            else:  # unlabeled
                # Get batch from unlabeled generator
                X, _ = generator.generate_positive_pairs(batch_size=batch_size)
                batch_labels = None
                
                # For unlabeled data, use the input images as original images
                batch_images = X
                
                # Get filenames if available
                if hasattr(generator, 'get_batch_filenames'):
                    batch_filenames = generator.get_batch_filenames()
                else:
                    batch_filenames = [f"unlabeled_sample_{samples_processed + i}" for i in range(len(X))]
            
            # Extract embeddings
            embeddings = model(X, training=False)
            embeddings_np = embeddings.numpy()
            
            embeddings_list.append(embeddings_np)
            if batch_labels is not None:
                labels_list.append(batch_labels)
            filenames_list.extend(batch_filenames)
            images_list.append(batch_images)
            
            samples_processed += len(X)
            
            # Stop if we've reached max_samples
            if max_samples and samples_processed >= max_samples:
                break
                
        except Exception as e:
            print(f"Error processing batch {batch_idx}: {e}")
            if debug:
                import traceback
                traceback.print_exc()
            continue
    
    # Concatenate all embeddings and images
    if embeddings_list:
        embeddings = np.concatenate(embeddings_list, axis=0)
        labels = np.concatenate(labels_list, axis=0) if labels_list else None
        images = np.concatenate(images_list, axis=0) if images_list else np.array([])
    else:
        embeddings = np.array([])
        labels = None
        images = np.array([])
    
    # Print class distribution for labeled data
    if data_type == "labeled" and labels is not None:
        unique_classes, class_counts = np.unique(labels, return_counts=True)
        print(f"Class distribution in extracted embeddings:")
        class_names_debug = {0: "M", 1: "MM", 2: "BN", 3: "SN"}
        for class_idx, count in zip(unique_classes, class_counts):
            class_name = class_names_debug.get(class_idx, f"Class_{class_idx}")
            print(f"  {class_name} (class {class_idx}): {count} samples")
    
    print(f"Extracted {len(embeddings)} {data_type} embeddings")
    return embeddings, labels, filenames_list, images


def save_embeddings_data(labeled_embeddings: np.ndarray,
                        labeled_labels: Optional[np.ndarray],
                        labeled_filenames: List[str],
                        unlabeled_embeddings: np.ndarray,
                        unlabeled_filenames: List[str],
                        output_dir: Path) -> None:
    """
    Save embedding data to files.
    
    Args:
        labeled_embeddings: Labeled embeddings array
        labeled_labels: Labeled labels array (can be None)
        labeled_filenames: List of labeled filenames
        unlabeled_embeddings: Unlabeled embeddings array
        unlabeled_filenames: List of unlabeled filenames
        output_dir: Output directory path
    """
    # Create embeddings directory
    embeddings_dir = output_dir / "embeddings"
    embeddings_dir.mkdir(exist_ok=True)
    
    # Determine embedding dimension safely
    embedding_dim = None
    if len(labeled_embeddings) > 0 and len(labeled_embeddings.shape) > 1:
        embedding_dim = labeled_embeddings.shape[1]
    elif len(unlabeled_embeddings) > 0 and len(unlabeled_embeddings.shape) > 1:
        embedding_dim = unlabeled_embeddings.shape[1]
    else:
        embedding_dim = 0
        print("Warning: Could not determine embedding dimension - no valid embeddings found")
    
    # Save raw embeddings
    embeddings_data = {
        'labeled_embeddings': labeled_embeddings.tolist() if len(labeled_embeddings) > 0 else [],
        'labeled_labels': labeled_labels.tolist() if labeled_labels is not None else None,
        'labeled_filenames': labeled_filenames,
        'unlabeled_embeddings': unlabeled_embeddings.tolist() if len(unlabeled_embeddings) > 0 else [],
        'unlabeled_filenames': unlabeled_filenames,
        'embedding_dim': embedding_dim,
        'num_labeled_samples': len(labeled_embeddings),
        'num_unlabeled_samples': len(unlabeled_embeddings)
    }
    
    # Save embeddings as JSON
    embeddings_file = embeddings_dir / "embeddings_data.json"
    with open(embeddings_file, 'w') as f:
        json.dump(embeddings_data, f, indent=2)
    print(f"Raw embeddings saved to: {embeddings_file}")
    
    # Save embeddings as numpy arrays for easier loading
    try:
        np.savez(
            embeddings_dir / "embeddings_arrays.npz",
            labeled_embeddings=labeled_embeddings if len(labeled_embeddings) > 0 else np.array([]),
            labeled_labels=labeled_labels if labeled_labels is not None else np.array([]),
            unlabeled_embeddings=unlabeled_embeddings if len(unlabeled_embeddings) > 0 else np.array([])
        )
        print(f"Numpy embeddings saved to: {embeddings_dir / 'embeddings_arrays.npz'}")
    except Exception as e:
        print(f"Warning: Could not save numpy arrays: {e}")


def create_embedding_plots(labeled_embeddings: np.ndarray,
                          labeled_labels: Optional[np.ndarray],
                          unlabeled_embeddings: np.ndarray,
                          class_names: Dict[int, str],
                          output_dir: Path) -> None:
    """
    Create visualization plots for embeddings using PCA and t-SNE.
    
    Args:
        labeled_embeddings: Labeled embeddings array
        labeled_labels: Labeled labels array (can be None)
        unlabeled_embeddings: Unlabeled embeddings array
        class_names: Dictionary mapping class indices to names
        output_dir: Output directory path
    """
    try:
        # Import required libraries
        from sklearn.manifold import TSNE
        from sklearn.decomposition import PCA
        import seaborn as sns
        try:
            import umap
            umap_available = True
        except ImportError:
            print("Warning: UMAP not available. Install with: pip install umap-learn")
            umap_available = False
    except ImportError as e:
        print(f"Error: Required libraries not available for embedding visualization: {e}")
        print("Please install: pip install scikit-learn seaborn")
        return
    
    # Set up plotting style
    plt.style.use('default')
    try:
        sns.set_palette("husl")
    except:
        # Use matplotlib default colors if seaborn setup fails
        pass
    
    # Create separate plots for labeled and unlabeled data
    # Adjust subplot layout based on UMAP availability
    if umap_available:
        fig, axes = plt.subplots(3, 2, figsize=(16, 18))
    else:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('SimCLR Embedding Visualizations', fontsize=16, fontweight='bold')
    
    # 1. PCA visualization for labeled data
    if len(labeled_embeddings) > 0:
        print("Computing PCA for labeled data...")
        pca_labeled = PCA(n_components=2, random_state=42)
        labeled_pca = pca_labeled.fit_transform(labeled_embeddings)
        
        ax = axes[0, 0]
        if labeled_labels is not None:
            for class_idx, class_name in class_names.items():
                mask = labeled_labels == class_idx
                if np.any(mask):
                    ax.scatter(labeled_pca[mask, 0], labeled_pca[mask, 1],
                             label=f'Class {class_name}', alpha=0.7, s=50)
            ax.legend()
        else:
            ax.scatter(labeled_pca[:, 0], labeled_pca[:, 1], alpha=0.7, s=50)
        
        ax.set_title(f'PCA - Labeled Data (n={len(labeled_embeddings)})')
        ax.set_xlabel(f'PC1 ({pca_labeled.explained_variance_ratio_[0]:.2%} variance)')
        ax.set_ylabel(f'PC2 ({pca_labeled.explained_variance_ratio_[1]:.2%} variance)')
        ax.grid(True, alpha=0.3)
    
    # 2. PCA visualization for unlabeled data
    if len(unlabeled_embeddings) > 0:
        print("Computing PCA for unlabeled data...")
        pca_unlabeled = PCA(n_components=2, random_state=42)
        unlabeled_pca = pca_unlabeled.fit_transform(unlabeled_embeddings)
        
        ax = axes[0, 1]
        ax.scatter(unlabeled_pca[:, 0], unlabeled_pca[:, 1],
                  alpha=0.7, s=50, color='gray', label='Unlabeled')
        ax.set_title(f'PCA - Unlabeled Data (n={len(unlabeled_embeddings)})')
        ax.set_xlabel(f'PC1 ({pca_unlabeled.explained_variance_ratio_[0]:.2%} variance)')
        ax.set_ylabel(f'PC2 ({pca_unlabeled.explained_variance_ratio_[1]:.2%} variance)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # 3. t-SNE visualization for labeled data
    if len(labeled_embeddings) > 1:
        print("Computing t-SNE for labeled data...")
        # Use PCA preprocessing for t-SNE if embeddings are high-dimensional
        if labeled_embeddings.shape[1] > 50:
            # Ensure n_components doesn't exceed min(n_samples, n_features)
            max_components = min(labeled_embeddings.shape[0], labeled_embeddings.shape[1])
            n_components = min(50, max_components)
            pca_prep = PCA(n_components=n_components, random_state=42)
            labeled_prep = pca_prep.fit_transform(labeled_embeddings)
        else:
            labeled_prep = labeled_embeddings
        
        tsne_labeled = TSNE(n_components=2, random_state=42, perplexity=min(30, len(labeled_embeddings)-1))
        labeled_tsne = tsne_labeled.fit_transform(labeled_prep)
        
        ax = axes[1, 0]
        if labeled_labels is not None:
            for class_idx, class_name in class_names.items():
                mask = labeled_labels == class_idx
                if np.any(mask):
                    ax.scatter(labeled_tsne[mask, 0], labeled_tsne[mask, 1],
                             label=f'Class {class_name}', alpha=0.7, s=50)
            ax.legend()
        else:
            ax.scatter(labeled_tsne[:, 0], labeled_tsne[:, 1], alpha=0.7, s=50)
        
        ax.set_title(f't-SNE - Labeled Data (n={len(labeled_embeddings)})')
        ax.set_xlabel('t-SNE 1')
        ax.set_ylabel('t-SNE 2')
        ax.grid(True, alpha=0.3)
    
    # 4. t-SNE visualization for unlabeled data
    if len(unlabeled_embeddings) > 1:
        print("Computing t-SNE for unlabeled data...")
        # Use PCA preprocessing for t-SNE if embeddings are high-dimensional
        if unlabeled_embeddings.shape[1] > 50:
            # Ensure n_components doesn't exceed min(n_samples, n_features)
            max_components = min(unlabeled_embeddings.shape[0], unlabeled_embeddings.shape[1])
            n_components = min(50, max_components)
            pca_prep = PCA(n_components=n_components, random_state=42)
            unlabeled_prep = pca_prep.fit_transform(unlabeled_embeddings)
        else:
            unlabeled_prep = unlabeled_embeddings
        
        tsne_unlabeled = TSNE(n_components=2, random_state=42, perplexity=min(30, len(unlabeled_embeddings)-1))
        unlabeled_tsne = tsne_unlabeled.fit_transform(unlabeled_prep)
        
        ax = axes[1, 1]
        ax.scatter(unlabeled_tsne[:, 0], unlabeled_tsne[:, 1],
                  alpha=0.7, s=50, color='gray', label='Unlabeled')
        ax.set_title(f't-SNE - Unlabeled Data (n={len(unlabeled_embeddings)})')
        ax.set_xlabel('t-SNE 1')
        ax.set_ylabel('t-SNE 2')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # 5. UMAP visualization for labeled data
    if umap_available and len(labeled_embeddings) > 1:
        print("Computing UMAP for labeled data...")
        # Use PCA preprocessing for UMAP if embeddings are high-dimensional
        if labeled_embeddings.shape[1] > 50:
            max_components = min(labeled_embeddings.shape[0], labeled_embeddings.shape[1])
            n_components = min(50, max_components)
            pca_prep = PCA(n_components=n_components, random_state=42)
            labeled_prep = pca_prep.fit_transform(labeled_embeddings)
        else:
            labeled_prep = labeled_embeddings
        
        # Adjust n_neighbors based on dataset size
        n_neighbors = min(15, max(2, len(labeled_embeddings) // 10))
        umap_labeled = umap.UMAP(n_components=2, random_state=42, n_neighbors=n_neighbors)
        labeled_umap = umap_labeled.fit_transform(labeled_prep)
        
        ax = axes[2, 0]
        if labeled_labels is not None:
            for class_idx, class_name in class_names.items():
                mask = labeled_labels == class_idx
                if np.any(mask):
                    ax.scatter(labeled_umap[mask, 0], labeled_umap[mask, 1],
                             label=f'Class {class_name}', alpha=0.7, s=50)
            ax.legend()
        else:
            ax.scatter(labeled_umap[:, 0], labeled_umap[:, 1], alpha=0.7, s=50)
        
        ax.set_title(f'UMAP - Labeled Data (n={len(labeled_embeddings)})')
        ax.set_xlabel('UMAP 1')
        ax.set_ylabel('UMAP 2')
        ax.grid(True, alpha=0.3)
    
    # 6. UMAP visualization for unlabeled data
    if umap_available and len(unlabeled_embeddings) > 1:
        print("Computing UMAP for unlabeled data...")
        # Use PCA preprocessing for UMAP if embeddings are high-dimensional
        if unlabeled_embeddings.shape[1] > 50:
            max_components = min(unlabeled_embeddings.shape[0], unlabeled_embeddings.shape[1])
            n_components = min(50, max_components)
            pca_prep = PCA(n_components=n_components, random_state=42)
            unlabeled_prep = pca_prep.fit_transform(unlabeled_embeddings)
        else:
            unlabeled_prep = unlabeled_embeddings
        
        # Adjust n_neighbors based on dataset size
        n_neighbors = min(15, max(2, len(unlabeled_embeddings) // 10))
        umap_unlabeled = umap.UMAP(n_components=2, random_state=42, n_neighbors=n_neighbors)
        unlabeled_umap = umap_unlabeled.fit_transform(unlabeled_prep)
        
        ax = axes[2, 1]
        ax.scatter(unlabeled_umap[:, 0], unlabeled_umap[:, 1],
                  alpha=0.7, s=50, color='gray', label='Unlabeled')
        ax.set_title(f'UMAP - Unlabeled Data (n={len(unlabeled_embeddings)})')
        ax.set_xlabel('UMAP 1')
        ax.set_ylabel('UMAP 2')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    plot_path = output_dir / "embedding_visualizations.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Embedding visualizations saved to: {plot_path}")


def create_combined_embedding_plot(labeled_embeddings: np.ndarray,
                                  labeled_labels: Optional[np.ndarray],
                                  unlabeled_embeddings: np.ndarray,
                                  class_names: Dict[int, str],
                                  output_dir: Path) -> None:
    """
    Create a combined plot showing both labeled and unlabeled embeddings together.
    
    Args:
        labeled_embeddings: Labeled embeddings array
        labeled_labels: Labeled labels array (can be None)
        unlabeled_embeddings: Unlabeled embeddings array
        class_names: Dictionary mapping class indices to names
        output_dir: Output directory path
    """
    if len(labeled_embeddings) == 0 or len(unlabeled_embeddings) == 0:
        return
    
    try:
        # Import required libraries
        from sklearn.manifold import TSNE
        from sklearn.decomposition import PCA
        try:
            import umap
            umap_available = True
        except ImportError:
            print("Warning: UMAP not available for combined visualization. Install with: pip install umap-learn")
            umap_available = False
    except ImportError as e:
        print(f"Error: Required libraries not available for combined embedding visualization: {e}")
        print("Please install: pip install scikit-learn")
        return
    
    print("Creating combined embedding visualization...")
    
    # Combine embeddings for joint dimensionality reduction
    all_embeddings = np.vstack([labeled_embeddings, unlabeled_embeddings])
    
    # Create labels for plotting (labeled vs unlabeled)
    n_labeled = len(labeled_embeddings)
    n_unlabeled = len(unlabeled_embeddings)
    
    # Adjust subplot layout based on UMAP availability
    if umap_available:
        fig, axes = plt.subplots(1, 3, figsize=(24, 6))
    else:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Combined Labeled and Unlabeled Embeddings', fontsize=16, fontweight='bold')
    
    # PCA on combined data
    print("Computing PCA on combined data...")
    pca_combined = PCA(n_components=2, random_state=42)
    combined_pca = pca_combined.fit_transform(all_embeddings)
    
    labeled_pca = combined_pca[:n_labeled]
    unlabeled_pca = combined_pca[n_labeled:]
    
    ax = axes[0]
    # Plot labeled data with class colors
    if labeled_labels is not None:
        for class_idx, class_name in class_names.items():
            mask = labeled_labels == class_idx
            if np.any(mask):
                ax.scatter(labeled_pca[mask, 0], labeled_pca[mask, 1],
                         label=f'Labeled - {class_name}', alpha=0.8, s=60)
    else:
        ax.scatter(labeled_pca[:, 0], labeled_pca[:, 1],
                  label='Labeled', alpha=0.8, s=60)
    
    # Plot unlabeled data
    ax.scatter(unlabeled_pca[:, 0], unlabeled_pca[:, 1],
              label='Unlabeled', alpha=0.6, s=40, color='gray', marker='x')
    
    ax.set_title('PCA - Combined Data')
    ax.set_xlabel(f'PC1 ({pca_combined.explained_variance_ratio_[0]:.2%} variance)')
    ax.set_ylabel(f'PC2 ({pca_combined.explained_variance_ratio_[1]:.2%} variance)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # t-SNE on combined data
    if len(all_embeddings) > 1:
        print("Computing t-SNE on combined data...")
        # Use PCA preprocessing for t-SNE if embeddings are high-dimensional
        if all_embeddings.shape[1] > 50:
            # Ensure n_components doesn't exceed min(n_samples, n_features)
            max_components = min(all_embeddings.shape[0], all_embeddings.shape[1])
            n_components = min(50, max_components)
            pca_prep = PCA(n_components=n_components, random_state=42)
            combined_prep = pca_prep.fit_transform(all_embeddings)
        else:
            combined_prep = all_embeddings
        
        tsne_combined = TSNE(n_components=2, random_state=42,
                           perplexity=min(30, len(all_embeddings)-1))
        combined_tsne = tsne_combined.fit_transform(combined_prep)
        
        labeled_tsne = combined_tsne[:n_labeled]
        unlabeled_tsne = combined_tsne[n_labeled:]
        
        ax = axes[1]
        # Plot labeled data with class colors
        if labeled_labels is not None:
            for class_idx, class_name in class_names.items():
                mask = labeled_labels == class_idx
                if np.any(mask):
                    ax.scatter(labeled_tsne[mask, 0], labeled_tsne[mask, 1],
                             label=f'Labeled - {class_name}', alpha=0.8, s=60)
        else:
            ax.scatter(labeled_tsne[:, 0], labeled_tsne[:, 1],
                      label='Labeled', alpha=0.8, s=60)
        
        # Plot unlabeled data
        ax.scatter(unlabeled_tsne[:, 0], unlabeled_tsne[:, 1],
                  label='Unlabeled', alpha=0.6, s=40, color='gray', marker='x')
        
        ax.set_title('t-SNE - Combined Data')
        ax.set_xlabel('t-SNE 1')
        ax.set_ylabel('t-SNE 2')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # UMAP on combined data
    if umap_available and len(all_embeddings) > 1:
        print("Computing UMAP on combined data...")
        # Use PCA preprocessing for UMAP if embeddings are high-dimensional
        if all_embeddings.shape[1] > 50:
            max_components = min(all_embeddings.shape[0], all_embeddings.shape[1])
            n_components = min(50, max_components)
            pca_prep = PCA(n_components=n_components, random_state=42)
            combined_prep = pca_prep.fit_transform(all_embeddings)
        else:
            combined_prep = all_embeddings
        
        # Adjust n_neighbors based on dataset size
        n_neighbors = min(15, max(2, len(all_embeddings) // 10))
        umap_combined = umap.UMAP(n_components=2, random_state=42, n_neighbors=n_neighbors)
        combined_umap = umap_combined.fit_transform(combined_prep)
        
        labeled_umap = combined_umap[:n_labeled]
        unlabeled_umap = combined_umap[n_labeled:]
        
        ax = axes[2]
        # Plot labeled data with class colors
        if labeled_labels is not None:
            for class_idx, class_name in class_names.items():
                mask = labeled_labels == class_idx
                if np.any(mask):
                    ax.scatter(labeled_umap[mask, 0], labeled_umap[mask, 1],
                             label=f'Labeled - {class_name}', alpha=0.8, s=60)
        else:
            ax.scatter(labeled_umap[:, 0], labeled_umap[:, 1],
                      label='Labeled', alpha=0.8, s=60)
        
        # Plot unlabeled data
        ax.scatter(unlabeled_umap[:, 0], unlabeled_umap[:, 1],
                  label='Unlabeled', alpha=0.6, s=40, color='gray', marker='x')
        
        ax.set_title('UMAP - Combined Data')
        ax.set_xlabel('UMAP 1')
        ax.set_ylabel('UMAP 2')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the combined plot
    combined_plot_path = output_dir / "combined_embedding_visualization.png"
    plt.savefig(combined_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Combined embedding visualization saved to: {combined_plot_path}")


def get_class_description(class_name: str) -> str:
    """Get description for neutrophil maturation stages."""
    descriptions = {
        'M': 'Myelocyte',
        'MM': 'Metamyelocyte',
        'BN': 'Band Neutrophil',
        'SN': 'Segmented Neutrophil'
    }
    return descriptions.get(class_name, 'Unknown')


def save_and_visualize_embeddings(model,
                                 labeled_generator,
                                 unlabeled_generator,
                                 output_dir: Path,
                                 debug: bool = False) -> None:
    """
    Extract and save embedded feature space for both labeled and unlabeled data.
    Create separate visualization plots for labeled and unlabeled data.
    
    Args:
        model: Trained encoder model
        labeled_generator: Labeled data generator
        unlabeled_generator: Unlabeled data generator
        output_dir: Output directory for saving results
        debug: Whether to run in debug mode
    """
    print("\n" + "="*60)
    print("EXTRACTING AND VISUALIZING EMBEDDINGS")
    print("="*60)
    
    try:
        # Define class names for neutrophil maturation stages
        class_names = {0: "M", 1: "MM", 2: "BN", 3: "SN"}
        
        # Extract embeddings for labeled data
        print("Extracting embeddings for labeled data...")
        labeled_embeddings, labeled_labels, labeled_filenames, labeled_images = extract_embeddings(
            model, labeled_generator, data_type="labeled", debug=debug
        )
        
        # Extract embeddings for unlabeled data
        print("Extracting embeddings for unlabeled data...")
        unlabeled_embeddings, _, unlabeled_filenames, unlabeled_images = extract_embeddings(
            model, unlabeled_generator, data_type="unlabeled", debug=debug
        )
        
        # Save raw embeddings
        save_embeddings_data(
            labeled_embeddings, labeled_labels, labeled_filenames,
            unlabeled_embeddings, unlabeled_filenames, output_dir
        )
        
        # Create visualizations
        print("Creating embedding visualizations...")
        create_embedding_plots(
            labeled_embeddings, labeled_labels, unlabeled_embeddings,
            class_names, output_dir
        )
        
        # Create combined visualization
        create_combined_embedding_plot(
            labeled_embeddings, labeled_labels, unlabeled_embeddings,
            class_names, output_dir
        )
        
        print("✓ Embedding extraction and visualization completed successfully!")
        
    except ImportError as e:
        print(f"Warning: Could not import required libraries for embedding visualization: {e}")
        print("Please install: pip install scikit-learn seaborn")
        print("For UMAP support, also install: pip install umap-learn")
    except Exception as e:
        print(f"Error during embedding extraction: {e}")
        if debug:
            import traceback
            traceback.print_exc()