"""Metrics and evaluation utilities for neutrophils-core."""

from .classification_metrics import (
    ordinal_mae, adjacent_class_accuracy, adjacent_class_recall,
    adjacent_class_precision, get_metrics
)
from .callbacks import Metric_Callback, multiclass_roc_auc_score, print_metrics_summary, CM_eval
from .loss_functions import STANDARD_LOSS_FUNCTIONS, ORDINAL_LOSS_FUNCTIONS
from .tensorboard_utils import setup_tensorboard_logging, ImageCallback
from .contrastive_losses import (
    nce_loss, nt_xent_loss, contrastive_accuracy, supervised_contrastive_loss,
    ContrastiveLosses, ContrastiveLossTracker, SimilarityMetric,
    create_nce_loss_fn, create_nt_xent_loss_fn, create_contrastive_accuracy_fn
)

__all__ = [
    'ordinal_mae',
    'adjacent_class_accuracy',
    'adjacent_class_recall',
    'adjacent_class_precision',
    'get_metrics',
    'Metric_Callback',
    'multiclass_roc_auc_score',
    'print_metrics_summary',
    'CM_eval',
    'STANDARD_LOSS_FUNCTIONS',
    'ORDINAL_LOSS_FUNCTIONS',
    'setup_tensorboard_logging',
    'ImageCallback',
    # Contrastive learning components
    'nce_loss',
    'nt_xent_loss',
    'contrastive_accuracy',
    'supervised_contrastive_loss',
    'ContrastiveLosses',
    'ContrastiveLossTracker',
    'SimilarityMetric',
    'create_nce_loss_fn',
    'create_nt_xent_loss_fn',
    'create_contrastive_accuracy_fn'
]
