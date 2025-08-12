"""Argument parsing utilities for 2D CNN classifier."""

import argparse
import os
from .config_loader import load_config


def get_args():
    """Parse command line arguments for 2D CNN classification trainer."""
    parser = argparse.ArgumentParser("2D CNN classification trainer for principal plane down projected LLSM neutrophils for maturation stage")
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration TOML file",
        required=False,
        default="config/resnet_2d.user.toml",
        metavar="PATH"
    )
    parser.add_argument(
        "-db", "--debug",
        help="Debug mode",
        action="store_true"
    )
    parser.add_argument(
        "--use-legacy-loading",
        help="Use legacy image loading method (load all images into memory)",
        action="store_true"
    )

    args = parser.parse_args()
    
    # Initialize minimal required attributes
    args.optimizer = {}

    # Load config from TOML file (defaults to config/resnet_2d.user.toml)
    if os.path.exists(args.config):
        args = load_config(args.config, args)
    else:
        print(f"Config file '{args.config}' not found. Please provide a valid config file.")
        exit(1)

    # verbose output to debug mode
    if args.debug:
        print("Running in debug mode")
        # Debug configuration is already loaded from TOML file by config_loader
        # If debug_config exists and has values, they override the defaults
        if hasattr(args, 'debug_config') and 'samples_per_class' in args.debug_config:
            args.samples_per_class = args.debug_config['samples_per_class']
        if hasattr(args, 'debug_config') and 'debug_epochs' in args.debug_config:
            args.debug_epochs = args.debug_config['debug_epochs']
        
    return args


def get_args_from_config(args):
    """Load configuration from a config file path and return configured args.
    
    Args:
        args: Object with at least a 'config' attribute containing the config file path
        
    Returns:
        Configured args object with all settings loaded from the config file
    """
    # Load config from TOML file
    if hasattr(args, 'config') and args.config and os.path.exists(args.config):
        configured_args = load_config(args.config, args)
    else:
        print(f"Config file '{getattr(args, 'config', 'None')}' not found. Using defaults.")
        configured_args = args
        
        # Set minimal defaults if no config is provided
        if not hasattr(configured_args, 'data_dir'):
            configured_args.data_dir = None
        if not hasattr(configured_args, 'label_file'):
            configured_args.label_file = None
        if not hasattr(configured_args, 'epochs'):
            configured_args.epochs = 15
        if not hasattr(configured_args, 'batch_size'):
            configured_args.batch_size = 32
        if not hasattr(configured_args, 'test_size'):
            configured_args.test_size = 0.2
        if not hasattr(configured_args, 'random_state'):
            configured_args.random_state = 42
        if not hasattr(configured_args, 'samples_per_class'):
            configured_args.samples_per_class = 10
        if not hasattr(configured_args, 'debug_epochs'):
            configured_args.debug_epochs = 3
        if not hasattr(configured_args, 'augmentation'):
            configured_args.augmentation = []
        if not hasattr(configured_args, 'sampling_strategy'):
            configured_args.sampling_strategy = "none"
        if not hasattr(configured_args, 'projection_mode'):
            configured_args.projection_mode = "single"
        if not hasattr(configured_args, 'projection_shuffle'):
            configured_args.projection_shuffle = False
        if not hasattr(configured_args, 'model'):
            configured_args.model = {}
        if not hasattr(configured_args, 'optimizer'):
            configured_args.optimizer = {}
        if not hasattr(configured_args, 'normalization_method'):
            configured_args.normalization_method = "percentile"
        if not hasattr(configured_args, 'normalization_params'):
            configured_args.normalization_params = {}
    
    return configured_args