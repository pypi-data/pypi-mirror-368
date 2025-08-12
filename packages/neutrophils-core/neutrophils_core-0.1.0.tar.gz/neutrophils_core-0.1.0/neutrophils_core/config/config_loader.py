"""Configuration loading utilities."""

import toml
import os


def load_config(config_path, args):
    """Load configuration from TOML file and update args."""
    if not config_path:
        return args
    
    print(f"Loading configuration from {config_path}")
    try:
        config = toml.load(config_path)
        
        # Data section - load as individual attributes
        if "data" in config:
            args.data_dir = config["data"].get("data_dir")
            args.label_file = config["data"].get("label_csv")  # Note: label_csv in TOML
            args.test_size = config["data"].get("test_size", 0.2)
            args.random_state = config["data"].get("random_state", 42)
            args.augmentation = config["data"].get("augmentation", [])
            args.sampling_strategy = config["data"].get("sampling_strategy", "none")
            args.projection_mode = config["data"].get("projection_mode", "single")
            args.projection_shuffle = config["data"].get("projection_shuffle", False)
            
            # Bias prevention: normalization configuration
            args.normalization_method = config["data"].get("normalization_method", "percentile")
            args.normalization_params = config["data"].get("normalization_params", {})
            
        # Training section
        if "training" in config:
            args.epochs = config["training"].get("epochs", 15)
            args.batch_size = config["training"].get("batch_size", 32)
            
        # Output section
        if "output" in config:
            args.output_dir = config["output"].get("output_dir", "./output")
            args.save_model = config["output"].get("save_model", True)
            args.save_plots = config["output"].get("save_plots", True)
            
        # Model section - store as nested dict
        if "model" in config:
            args.model = config["model"]
            
        # Optimizer section - store as nested dict
        if "optimizer" in config:
            args.optimizer = config["optimizer"]
                
        # TensorBoard section
        if "tensorboard" in config:
            args.tensorboard = config["tensorboard"]
            
        # Debug section
        if "debug" in config:
            args.debug_config = config["debug"]
            args.samples_per_class = config["debug"].get("samples_per_class", 10)
            args.debug_epochs = config["debug"].get("debug_epochs", 3)
                
        # Ensure required attributes have defaults
        if not hasattr(args, 'output_dir') or args.output_dir is None:
            args.output_dir = "./output"
        if not hasattr(args, 'data_dir'):
            args.data_dir = None
        if not hasattr(args, 'label_file'):
            args.label_file = None
        if not hasattr(args, 'epochs'):
            args.epochs = 15
        if not hasattr(args, 'batch_size'):
            args.batch_size = 32
        if not hasattr(args, 'test_size'):
            args.test_size = 0.2
        if not hasattr(args, 'random_state'):
            args.random_state = 42
        if not hasattr(args, 'save_model'):
            args.save_model = True
        if not hasattr(args, 'save_plots'):
            args.save_plots = True
        if not hasattr(args, 'samples_per_class'):
            args.samples_per_class = 10
        if not hasattr(args, 'debug_epochs'):
            args.debug_epochs = 3
        if not hasattr(args, 'augmentation'):
            args.augmentation = []
        if not hasattr(args, 'sampling_strategy'):
            args.sampling_strategy = "none"
        if not hasattr(args, 'projection_mode'):
            args.projection_mode = "single"
        if not hasattr(args, 'projection_shuffle'):
            args.projection_shuffle = False
        if not hasattr(args, 'model'):
            args.model = {}
        if not hasattr(args, 'optimizer'):
            args.optimizer = {}
                
        return args
        
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        print("Setting minimal defaults...")
        # Set minimal defaults if config loading fails
        args.output_dir = "./output"
        args.data_dir = None
        args.label_file = None
        args.epochs = 15
        args.batch_size = 32
        args.test_size = 0.2
        args.random_state = 42
        args.save_model = True
        args.save_plots = True
        args.samples_per_class = 10
        args.debug_epochs = 3
        args.augmentation = []
        args.sampling_strategy = "none"
        args.projection_mode = "single" 
        args.projection_shuffle = False
        args.model = {}
        args.optimizer = {}
        return args


def load_default_config():
    """Load the default model configuration from the TOML file."""
    default_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                                      "config", "resnet_2d.default.toml")
    try:
        with open(default_config_path, 'r') as f:
            return toml.load(f)
    except Exception as e:
        print(f"Warning: Could not load default configuration from {default_config_path}. Error: {e}")
        return None