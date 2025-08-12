"""
Custom callbacks and metrics for training neutrophil classification models.

This module provides specialized callbacks for monitoring training progress
and computing multi-class metrics during training.
"""

import tensorflow as tf
from tensorflow.keras.callbacks import Callback
import numpy as np
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    confusion_matrix,
    roc_curve,
    auc,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.preprocessing import label_binarize
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")  # for headless plotting
import os
from datetime import datetime
from tqdm import tqdm
import multiprocessing
from tensorflow.keras.utils import to_categorical


def multiclass_roc_auc_score(y_test, y_pred, classes, ax=None, average="macro"):
    """
    Calculate multiclass ROC AUC score with optional plotting.

    Args:
        y_test: Ground truth labels (one-hot encoded)
        y_pred: Predicted probabilities
        classes: Dictionary mapping class names to indices
        ax: Optional matplotlib axis for plotting
        average: Averaging method for ROC AUC calculation

    Returns:
        ROC AUC score for multiclass classification
    """
    # Compute ROC curve and ROC area for each class
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for idx, c_label in enumerate(list(classes.keys())):
        fpr[c_label], tpr[c_label], thresholds = roc_curve(
            y_test[:, idx].astype(int), y_pred[:, idx]
        )
        roc_auc[c_label] = auc(fpr[c_label], tpr[c_label])

    # Compute micro-average ROC curve and ROC area
    fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_pred.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    # First aggregate all false positive rates
    all_fpr = np.unique(
        np.concatenate([fpr[c_label] for c_label in list(classes.keys())])
    )

    # Then interpolate all ROC curves at this points
    mean_tpr = np.zeros_like(all_fpr)
    for c_label in list(classes.keys()):
        mean_tpr += np.interp(all_fpr, fpr[c_label], tpr[c_label])

    # average it and compute AUC
    mean_tpr /= len(classes)

    fpr["macro"] = all_fpr
    tpr["macro"] = mean_tpr
    roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

    if ax:
        ax.plot([0, 1], [0, 1], "k--", label="Random Guessing")

        ax.plot(
            fpr["micro"],
            tpr["micro"],
            label="micro-avg (AUC={:0.2f})".format(roc_auc["micro"]),
            color="deeppink",
            linestyle=":",
            linewidth=2,
        )

        plt.plot(
            fpr["macro"],
            tpr["macro"],
            label="macro-avg (AUC={:0.2f}))".format(roc_auc["macro"]),
            color="navy",
            linestyle=":",
            linewidth=2,
        )

        for c_label in list(classes.keys()):
            plt.plot(
                fpr[c_label],
                tpr[c_label],
                lw=2,
                label="{} (AUC={:0.2f})".format(c_label, roc_auc[c_label]),
            )

    return roc_auc_score(y_test, y_pred, average=average)


def print_metrics_summary(y_true, y_pred_proba, classes_dict):
    """
    Print comprehensive metrics summary for classification results.

    Args:
        y_true: Ground truth labels (class indices)
        y_pred_proba: Predicted probabilities
        classes_dict: Dictionary mapping class names to indices
    """
    # Ensure arrays have the same length
    min_len = min(len(y_true), len(y_pred_proba))
    y_true = y_true[:min_len]
    y_pred_proba = y_pred_proba[:min_len]
    
    # Binarize the labels for AUC computation if it's a multi-class problem
    classes = sorted(list(set(y_true)))
    y_pred = np.argmax(y_pred_proba, axis=1)
    y_true_binarized = label_binarize(y_true, classes=classes)
    y_pred_binarized = label_binarize(y_pred, classes=classes)

    # Calculate overall metrics
    acc = accuracy_score(y_true, y_pred)

    precision_micro = precision_score(y_true, y_pred, average="micro")
    recall_micro = recall_score(y_true, y_pred, average="micro")
    f1_micro = f1_score(y_true, y_pred, average="micro")

    precision_macro = precision_score(y_true, y_pred, average="macro")
    recall_macro = recall_score(y_true, y_pred, average="macro")
    f1_macro = f1_score(y_true, y_pred, average="macro")

    if len(classes) > 2:  # multi-class case
        # Use the original y_true and y_pred_proba directly with multi_class='ovr'
        # This avoids the shape mismatch issue with label_binarize
        try:
            auc_micro = roc_auc_score(
                y_true, y_pred_proba, average="micro", multi_class="ovr"
            )
            auc_macro = roc_auc_score(
                y_true, y_pred_proba, average="macro", multi_class="ovr"
            )
        except ValueError as e:
            # Fallback to a simpler calculation if there are issues
            print(f"Warning: ROC AUC calculation failed: {e}")
            auc_micro = 0.5
            auc_macro = 0.5
    else:  # binary case
        auc_micro = roc_auc_score(y_true, y_pred_proba)
        auc_macro = (
            auc_micro  # In binary classification, micro and macro AUC are the same
        )

    # Calculate metrics for each class
    class_metrics = []
    for cls_k, cls_v in classes_dict.items():
        # Check if this class exists in the actual data
        if cls_v in classes:
            # Find the index in the binarized array
            class_idx = classes.index(cls_v)
            y_true_cls = (y_true_binarized[:, class_idx]).astype(int)
            y_pred_cls = (y_pred_binarized[:, class_idx]).astype(int)
        else:
            # Class not present in data, create dummy arrays
            y_true_cls = np.zeros(len(y_true), dtype=int)
            y_pred_cls = np.zeros(len(y_true), dtype=int)

        precision_cls = precision_score(y_true_cls, y_pred_cls, zero_division=0)
        recall_cls = recall_score(y_true_cls, y_pred_cls, zero_division=0)
        f1_cls = f1_score(y_true_cls, y_pred_cls, zero_division=0)
        auc_cls = (
            roc_auc_score(y_true_cls, y_pred_cls)
            if len(set(y_true_cls)) > 1
            else float("nan")
        )

        class_metrics.append([cls_k, precision_cls, recall_cls, f1_cls, auc_cls])

    # Create DataFrame for tabular printout
    df_metrics = pd.DataFrame(
        class_metrics, columns=["Class", "Precision", "Recall", "F1 Score", "AUC"]
    )

    # Add overall metrics to the DataFrame
    overall_metrics = pd.DataFrame(
        [
            ["Overall (Micro)", precision_micro, recall_micro, f1_micro, auc_micro],
            ["Overall (Macro)", precision_macro, recall_macro, f1_macro, auc_macro],
        ],
        columns=["Class", "Precision", "Recall", "F1 Score", "AUC"],
    )

    df_metrics = pd.concat([df_metrics, overall_metrics], ignore_index=True)

    # Print the DataFrame
    print(df_metrics.to_string(index=False))
    print("Accuracy: {:.3f}".format(acc))


def CM_eval(
    model,
    classes,
    data_gen,
    df,
    epoch,
    title="",
    plot=None,
    normalize=True,
    batch_size=32,
    drop_batch_remainder=True,
):
    """
    Evaluate model performance using confusion matrix and comprehensive metrics.

    Args:
        model: Trained model to evaluate
        classes: Dictionary mapping class names to indices
        data_gen: Data generator for evaluation
        df: DataFrame containing labels
        epoch: Current epoch number
        title: Title for the evaluation
        plot: Directory path for saving plots (optional)
        normalize: Whether to normalize confusion matrix
        batch_size: Batch size for evaluation
        drop_batch_remainder: Whether to drop incomplete batches
    """
    tqdm.write("Evaluating {}".format(title))

    # Generate data
    t1 = datetime.now()
    if drop_batch_remainder:
        n = (len(df) // batch_size) * batch_size
    else:
        n = len(df)

    if int(tf.keras.__version__.split(".")[0]) == 3:
        Y_pred_proba = model.predict(data_gen)[:n]
    else:
        Y_pred_proba = model.predict(
            data_gen, workers=multiprocessing.cpu_count(), use_multiprocessing=True
        )[:n]
    t2 = datetime.now()
    # time difference in seconds
    delta = t2 - t1
    tqdm.write(
        "Evaluation takes {:.2} seconds, TF Eager mode: {}".format(
            delta.total_seconds(), tf.executing_eagerly()
        )
    )

    y_pred = np.argmax(Y_pred_proba, axis=1)

    y_ = df["stage"].apply(lambda x: classes[x]).values[:n]
    y_categorical = to_categorical(
        y_, num_classes=classes[max(classes, key=classes.get)] + 1
    )

    labels = classes.keys()
    print("Confusion matrix:")
    cm = confusion_matrix(y_, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)

    tqdm.write(title)
    print(disp.confusion_matrix)

    # Ensure both arrays have the same length
    min_len = min(len(y_), len(Y_pred_proba))
    y_trimmed = y_[:min_len]
    Y_pred_proba_trimmed = Y_pred_proba[:min_len]
    print_metrics_summary(y_trimmed, Y_pred_proba_trimmed, classes)

    # force running on cpu for memory sake
    with tf.device("/cpu:0"):
        if plot is not None:
            fig, axs = plt.subplots(1, 2, figsize=(10, 5))
            axs[0].set_title(title)
            disp.plot(cmap=plt.cm.Blues, ax=axs[0])
            axs[1].set_xlabel("False Positive Rate")
            axs[1].set_ylabel("True Positive Rate")
            tqdm.write(
                "ROC AUC score: {:.4f}".format(
                    multiclass_roc_auc_score(
                        y_test=y_categorical,
                        y_pred=Y_pred_proba,
                        classes=classes,
                        ax=axs[1],
                        average="macro",
                    )
                )
            )
            axs[1].set_xlim((0, 1))
            axs[1].set_ylim((0, 1.05))
            axs[1].legend(fontsize=8)

            # Create directories with proper path handling
            # Sanitize title for filesystem compatibility
            safe_title = title.replace(" ", "_").replace("/", "_")
            svg_dir = os.path.join(plot, "plots", safe_title, "SVG")
            png_dir = os.path.join(plot, "plots", safe_title, "PNG")
            
            # Ensure directories exist
            try:
                os.makedirs(svg_dir, exist_ok=True)
                os.makedirs(png_dir, exist_ok=True)
                dirs_created = True
            except OSError as e:
                tqdm.write(f"Warning: Could not create directories: {e}")
                dirs_created = False

            tqdm.write("Saving confusion matrix plots...")
            
            # Only try to save files if directories were created successfully
            if dirs_created:
                # Save SVG
                svg_path = os.path.join(svg_dir, "confusion_matrix_epoch-{}.svg".format(str(epoch).zfill(3)))
                try:
                    plt.savefig(svg_path)
                except Exception as e:
                    tqdm.write(f"Warning: Could not save SVG: {e}")
                
                # Save PNG
                png_path = os.path.join(png_dir, "confusion_matrix_epoch-{}.png".format(str(epoch).zfill(3)))
                try:
                    plt.savefig(png_path, dpi=600)
                except Exception as e:
                    tqdm.write(f"Warning: Could not save PNG: {e}")
            else:
                tqdm.write("Skipping file save due to directory creation failure")
            plt.close(fig)
        else:
            tqdm.write(
                "ROC AUC score: {:.4f}".format(
                    multiclass_roc_auc_score(y_categorical, Y_pred_proba, classes)
                )
            )


class Metric_Callback(Callback):
    """
    Custom callback for computing and logging additional metrics during training.

    This callback computes metrics that are not easily computed as standard
    Keras metrics, such as multiclass ROC AUC and ordinal-specific metrics.
    """

    def __init__(self, validation_data=None, metric_names=None):
        """
        Initialize the callback.

        Args:
            validation_data: Tuple of (X_val, y_val) for validation metrics
            metric_names: List of metric names to compute
        """
        super().__init__()
        self.validation_data = validation_data
        self.metric_names = metric_names or ["roc_auc"]

    def on_epoch_end(self, epoch, logs=None):
        """
        Called at the end of each epoch to compute additional metrics.

        Args:
            epoch: Current epoch number
            logs: Dictionary of logs from the epoch
        """
        if logs is None:
            logs = {}

        if self.validation_data is not None:
            X_val, y_val = self.validation_data
            y_pred = self.model.predict(X_val, verbose=0)

            # Compute ROC AUC if requested
            if "roc_auc" in self.metric_names:
                try:
                    # Create a dummy classes dict for ROC AUC calculation
                    num_classes = y_pred.shape[-1]
                    classes_dict = {f'class_{i}': i for i in range(num_classes)}
                    roc_auc = multiclass_roc_auc_score(y_val, y_pred, classes_dict)
                    logs["val_roc_auc"] = roc_auc
                    print(f" - val_roc_auc: {roc_auc:.4f}")
                except Exception as e:
                    print(f" - val_roc_auc: calculation failed ({e})")

            # Compute ordinal MAE if requested
            if "ordinal_mae" in self.metric_names:
                try:
                    # Convert one-hot to class indices if needed
                    if y_val.ndim > 1 and y_val.shape[-1] > 1:
                        y_true_indices = np.argmax(y_val, axis=-1)
                    else:
                        y_true_indices = y_val.flatten()

                    # Calculate expected class from predictions
                    num_classes = y_pred.shape[-1]
                    class_indices = np.arange(num_classes)
                    y_pred_expected = np.sum(y_pred * class_indices, axis=-1)

                    # Calculate MAE
                    ordinal_mae = np.mean(np.abs(y_true_indices - y_pred_expected))
                    logs["val_ordinal_mae"] = ordinal_mae
                    print(f" - val_ordinal_mae: {ordinal_mae:.4f}")
                except Exception as e:
                    print(f" - val_ordinal_mae: calculation failed ({e})")

    def on_train_begin(self, logs=None):
        """Called at the beginning of training."""
        print(f"Starting training with custom metrics: {self.metric_names}")

    def on_train_end(self, logs=None):
        """Called at the end of training."""
        print("Training completed with custom metrics callback")


import time
import gc
from tqdm import tqdm


@tf.keras.utils.register_keras_serializable()
class NanStopping(tf.keras.callbacks.Callback):
    """Callback to stop training if loss or accuracy is NaN."""
    def on_batch_end(self, batch, logs=None):
        logs = logs or {}
        loss = logs.get('contrastive_loss')
        accuracy = logs.get('contrastive_accuracy')

        if loss is not None and (np.isnan(loss) or np.isinf(loss)):
            print(f"\nStopping training at batch {batch}: contrastive_loss is {loss}.")
            self.model.stop_training = True
        
        if accuracy is not None and (np.isnan(accuracy) or np.isinf(accuracy)):
            print(f"\nStopping training at batch {batch}: contrastive_accuracy is {accuracy}.")
            self.model.stop_training = True

    def get_config(self):
        return {}


class SimCLRWarmupCallback(Callback):
    """
    A specialized callback for SimCLR training that warms up the data pipeline
    and provides progress feedback during the shuffle buffer initialization.
    """

    def __init__(self, warmup_steps=None, enable_warmup=True):
        """
        Initialize the warmup callback.

        Args:
            warmup_steps: Number of steps to use for warmup (defaults to 128)
            enable_warmup: Whether to enable the warmup process
        """
        super().__init__()
        self.warmup_steps = warmup_steps or 128  # Match typical shuffle buffer size
        self.enable_warmup = enable_warmup

    def on_train_begin(self, logs=None):
        """
        Called at the beginning of training to warm up the dataset.
        """
        if not self.enable_warmup:
            return

        print("\n" + "="*60)
        print("🚀 WARMING UP DATA PIPELINE")
        print("="*60)
        print("This process fills the shuffle buffer and prepares the data pipeline.")
        print("Progress will be shown below:\n")

        # Get the training dataset from the model
        if hasattr(self.model, 'train_dataset'):
            dataset = self.model.train_dataset
        elif hasattr(self, '_dataset'):
            dataset = self._dataset
        else:
            print("⚠️  Could not find dataset for warmup. Skipping...")
            return

        # Create iterator and warm up
        try:
            warmup_iterator = iter(dataset)
            warmup_progress = tqdm(
                total=self.warmup_steps,
                desc="Filling shuffle buffer",
                unit="batch",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {rate_fmt}"
            )

            start_time = time.time()
            
            for i in range(self.warmup_steps):
                try:
                    _ = next(warmup_iterator)
                    warmup_progress.update(1)
                except (StopIteration, tf.errors.OutOfRangeError):
                    # Dataset exhausted, break early
                    break

            warmup_progress.close()
            elapsed_time = time.time() - start_time
            
            # Explicitly clean up the iterator and collect garbage
            del warmup_iterator
            gc.collect()

            print(f"\n✅ Warmup completed in {elapsed_time:.2f} seconds")
            print("🎯 Starting actual training...\n")

        except Exception as e:
            print(f"⚠️  Warmup failed: {e}")
            print("Proceeding with training anyway...\n")

    def set_dataset(self, dataset):
        """
        Set the dataset for warmup (to be called before fit).
        
        Args:
            dataset: The tf.data.Dataset to warm up
        """
        self._dataset = dataset
