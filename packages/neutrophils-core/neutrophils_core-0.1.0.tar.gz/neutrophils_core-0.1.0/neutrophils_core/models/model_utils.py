"""
Model utilities for neutrophil classification models

This module contains utility functions for model operations including
saving, loading, and enhanced summary printing with colorized output.
"""

import os
import sys
import tensorflow as tf
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import subprocess
import tempfile

# Enhanced ANSI color codes for terminal output with full palette
class Colors:
    """Extended ANSI color codes for enhanced terminal visualization"""
    # Basic formatting
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    # Standard colors
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Layer type specific colors
    INPUT = BLACK
    CONV = BRIGHT_CYAN
    BN = BRIGHT_YELLOW
    ACTIVATION = BRIGHT_GREEN
    RESIDUAL = BRIGHT_MAGENTA
    MERGE = BRIGHT_RED
    BLOCK = BRIGHT_BLUE

def colorize(text, color_code, bold=False):
    """Add color and formatting to text if terminal supports it"""
    try:
        # Check if stdout is a terminal (not redirected to file)
        has_isatty = hasattr(sys.stdout, 'isatty')
        if has_isatty:
            # Try calling isatty() which might raise an exception in tests
            try:
                is_tty = sys.stdout.isatty()
                # Additional check: if we're in a test environment with mocks,
                # is_tty might be a Mock object that evaluates to True.
                # Check if it's actually a boolean True, not just truthy
                if is_tty is True:
                    style = Colors.BOLD if bold else ''
                    return f"{style}{color_code}{text}{Colors.RESET}"
                else:
                    return text
            except Exception:
                # If isatty() raises an exception, return plain text
                return text
        else:
            return text
    except Exception:
        # If any exception occurs (including AttributeError), return plain text
        return text

def print_feature_extractor_detailed_summary(feature_extractor, input_shape=None, level="detailed", style="compact"):
    """
    Print detailed summary of FeatureExtractor with colorized output and layer connections
    
    Args:
        feature_extractor: FeatureExtractor instance
        input_shape: Input shape tuple (H, W, C)
        level: Summary level ("standard", "detailed", "connections",  "ascii_art")
               - "standard": Uses default Keras summary
               - "detailed": Shows detailed layer breakdown with colors
               - "connections": Shows layer connections and data flow
               - "ascii_art": Shows ASCII art visualization
        style: Style for ASCII art visualization ("compact", "tree", "flowchart")
    """
    if input_shape is None:
        if hasattr(feature_extractor, 'input_shape_config') and feature_extractor.input_shape_config:
            input_shape = feature_extractor.input_shape_config
            # Check if the input_shape_config is valid (not a Mock)
            if hasattr(input_shape, '_mock_name'):
                print(colorize("Error: No input shape available. Please provide input_shape parameter.", Colors.FAIL))
                return
        else:
            print(colorize("Error: No input shape available. Please provide input_shape parameter.", Colors.FAIL))
            return
    
    # Ensure model is built
    try:
        dummy_input = tf.zeros((1,) + input_shape)
        _ = feature_extractor(dummy_input, training=False)
    except (TypeError, ValueError) as e:
        # Handle case where input_shape might be a Mock or invalid
        if hasattr(input_shape, '__iter__') and not isinstance(input_shape, str):
            try:
                input_shape_tuple = tuple(input_shape)
                dummy_input = tf.zeros((1,) + input_shape_tuple)
                _ = feature_extractor(dummy_input, training=False)
            except:
                print(colorize(f"Warning: Could not build model with input shape {input_shape}", Colors.WARNING))
                return
        else:
            print(colorize(f"Error: Invalid input shape {input_shape}", Colors.FAIL))
            return
    
    if level == "standard":
        # Use standard Keras summary
        feature_extractor.summary()
        return
    
    # Enhanced detailed summary
    print(colorize(f"\n{'='*80}", Colors.HEADER))
    if level == "detailed":
        print(colorize(f"FEATUREEXTRACTOR ENHANCED SUMMARY", Colors.HEADER + Colors.BOLD))
    else:
        print(colorize(f"FEATUREEXTRACTOR DETAILED SUMMARY", Colors.HEADER + Colors.BOLD))
    print(colorize(f"{'='*80}", Colors.HEADER))
    print(colorize(f"Input shape: {input_shape}", Colors.OKBLUE))
    
    if level == "connections":
        _print_connection_aware_summary(feature_extractor, input_shape)
    elif level == "ascii_art":
        _print_ascii_art_summary(feature_extractor, input_shape, style)
    else:
        _print_detailed_layer_summary(feature_extractor, input_shape)

def _print_detailed_layer_summary(feature_extractor, input_shape):
    """Print detailed layer summary with colors"""
    print(colorize(f"\n{'Step':<4} {'Layer Name':<45} {'Type':<20} {'Output Shape':<20} {'Params':<12} {'Info':<15}", Colors.BOLD))
    print(colorize(f"{'-'*120}", Colors.HEADER))
    
    step = 0
    total_params = 0
    
    # Input layer
    print(f"{step:<4} {colorize('Input', Colors.OKGREEN):<54} {'Input':<20} {str(input_shape):<20} {'0':<12} {'Entry point':<15}")
    step += 1
    
    # Process each block
    conv_config = feature_extractor.config['conv_blocks']
    filters_list = conv_config['filters']
    use_residual = conv_config.get('use_residual', False)
    conv_layers_count = conv_config.get('conv_layers', 2)
    
    for block_idx, target_filters in enumerate(filters_list):
        # Block header
        print(colorize(f"\n{'='*120}", Colors.BLOCK))
        print(colorize(f"BLOCK {block_idx} (Target filters: {target_filters})", Colors.BLOCK + Colors.BOLD))
        print(colorize(f"{'='*120}", Colors.BLOCK))
        
        block_layers = feature_extractor.conv_layers[block_idx]
        
        # Main path conv layers
        for conv_idx in range(conv_layers_count):
            # Conv layer
            if block_layers['conv_layers'][conv_idx] is not None:
                layer = block_layers['conv_layers'][conv_idx]
                params = layer.count_params()
                total_params += params
                output_shape = str(getattr(layer, 'output_shape', 'Unknown'))[1:]  # Remove batch dim
                
                layer_name = colorize(layer.name, Colors.CONV)
                layer_type = colorize('Conv2D', Colors.CONV)
                print(f"{step:<4} {layer_name:<54} {layer_type:<29} {output_shape:<20} {params:<12} {'Main path':<15}")
                step += 1
            
            # BatchNorm layer
            if block_layers['bn_layers'][conv_idx] is not None:
                layer = block_layers['bn_layers'][conv_idx]
                params = layer.count_params()
                total_params += params
                output_shape = str(getattr(layer, 'output_shape', 'Same'))[1:]
                
                layer_name = colorize(layer.name, Colors.BN)
                layer_type = colorize('BatchNorm', Colors.BN)
                print(f"{step:<4} {layer_name:<54} {layer_type:<29} {output_shape:<20} {params:<12} {'Normalization':<15}")
                step += 1
            
            # Activation layer
            if block_layers['activation_layers'][conv_idx] is not None:
                act_layer = block_layers['activation_layers'][conv_idx]
                act_name = getattr(act_layer, 'name', f'activation_block_{block_idx}_conv_{conv_idx}')
                
                layer_name = colorize(act_name, Colors.ACTIVATION)
                layer_type = colorize('Activation', Colors.ACTIVATION)
                print(f"{step:<4} {layer_name:<54} {layer_type:<29} {'(same)':<20} {'0':<12} {'Non-linearity':<15}")
                step += 1
        
        # Residual path
        if use_residual:
            print(colorize(f"\n{'-'*120}", Colors.RESIDUAL))
            print(colorize(f"RESIDUAL PATH for Block {block_idx}", Colors.RESIDUAL))
            print(colorize(f"{'-'*120}", Colors.RESIDUAL))
            
            # Residual projection
            if block_layers['residual_projection'] is not None:
                layer = block_layers['residual_projection']
                params = layer.count_params()
                total_params += params
                output_shape = str(getattr(layer, 'output_shape', 'Unknown'))[1:]
                
                layer_name = colorize(layer.name, Colors.RESIDUAL)
                layer_type = colorize('Conv2D (Skip)', Colors.RESIDUAL)
                print(f"{step:<4} {layer_name:<54} {layer_type:<29} {output_shape:<20} {params:<12} {'Skip path':<15}")
                step += 1
            
            # Residual BN
            if block_layers['residual_bn'] is not None:
                layer = block_layers['residual_bn']
                params = layer.count_params()
                total_params += params
                output_shape = str(getattr(layer, 'output_shape', 'Same'))[1:]
                
                layer_name = colorize(layer.name, Colors.RESIDUAL)
                layer_type = colorize('BatchNorm (Skip)', Colors.RESIDUAL)
                print(f"{step:<4} {layer_name:<54} {layer_type:<29} {output_shape:<20} {params:<12} {'Skip norm':<15}")
                step += 1
            
            # Merge layer
            if block_layers['residual_scaling'] is not None:
                scaling_layer = block_layers['residual_scaling']
                layer_name = getattr(scaling_layer, 'name', f'merge_block_{block_idx}')
                
                layer_name_colored = colorize(layer_name, Colors.MERGE)
                layer_type = colorize('Add/Scale', Colors.MERGE)
                print(f"{step:<4} {layer_name_colored:<54} {layer_type:<29} {'(computed)':<20} {'0':<12} {'Merge paths':<15}")
                step += 1
            
            # Final activation
            if block_layers['final_activation'] is not None:
                final_act = block_layers['final_activation']
                final_name = getattr(final_act, 'name', f'final_activation_block_{block_idx}')
                
                layer_name = colorize(final_name, Colors.ACTIVATION)
                layer_type = colorize('Activation (Final)', Colors.ACTIVATION)
                print(f"{step:<4} {layer_name:<54} {layer_type:<29} {'(same)':<20} {'0':<12} {'Block output':<15}")
                step += 1
    
    # Summary
    print(colorize(f"\n{'='*120}", Colors.HEADER))
    print(colorize(f"SUMMARY", Colors.HEADER + Colors.BOLD))
    print(colorize(f"{'='*120}", Colors.HEADER))
    print(f"Total layers: {colorize(str(step), Colors.OKGREEN)}")
    print(f"Total parameters: {colorize(f'{total_params:,}', Colors.OKGREEN)}")
    print(f"Trainable parameters: {colorize(f'{total_params:,}', Colors.OKGREEN)}")
    print(f"Model architecture: {colorize(f'{len(filters_list)} blocks', Colors.OKGREEN)}")
    print(f"Residual connections: {colorize(str(use_residual), Colors.OKGREEN)}")

def _print_connection_aware_summary(feature_extractor, input_shape):
    """Print connection-aware summary showing layer relationships"""
    print(colorize("Connection-aware debugging not available. Using standard detailed summary.", Colors.WARNING))
    _print_detailed_layer_summary(feature_extractor, input_shape)

def get_activation_function(activation_config):
    """Get activation function from configuration"""
    if isinstance(activation_config, str):
        return activation_config
    elif isinstance(activation_config, dict):
        name = activation_config.get('name', 'relu')
        if name == 'leaky_relu':
            from tensorflow.keras.layers import LeakyReLU
            # Use negative_slope parameter for newer TensorFlow versions
            alpha_value = activation_config.get('alpha', 0.1)
            return LeakyReLU(negative_slope=alpha_value)
        return name
    return 'relu'

def get_weight_initializer(initializer_name):
    """Get weight initializer from name"""
    if initializer_name is None:
        return 'he_normal'
    
    initializer_map = {
        'he_normal': tf.keras.initializers.HeNormal(seed=42),
        'he_uniform': tf.keras.initializers.HeUniform(seed=42),
        'xavier_normal': tf.keras.initializers.GlorotNormal(seed=42),
        'glorot_normal': tf.keras.initializers.GlorotNormal(seed=42)
    }
    
    return initializer_map.get(initializer_name.lower(), 'he_normal')

def save_model(model, output_dir, timestamp):
    """Save trained model to output directory"""
    model_dir = os.path.join(output_dir, "model")
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, f"neutrophil_model_{timestamp}.h5")
    model.save(model_path)
    print(f"Model saved to {model_path}")
    return model_path

def print_feature_extractor_summary(model):
    """Legacy function for backward compatibility"""
    print("FeatureExtractor Summary:")
    model.summary()
# Enhanced summary function with all options
def print_enhanced_summary(feature_extractor, input_shape=None, **kwargs):
    """
    Enhanced summary function with full visualization options
    
    Args:
        feature_extractor: FeatureExtractor instance
        input_shape: Input shape tuple
        **kwargs: Additional options including:
            - level: "standard", "detailed", "connections", "graph", "ascii_art"
            - style: "compact", "detailed", "flowchart", "tree" (for ascii_art level)
            - export_dot: bool, whether to export DOT file
            - interactive: bool, whether to open interactive viewer
    """
    level = kwargs.get('level', 'detailed')
    style = kwargs.get('style', 'compact')
    export_dot = kwargs.get('export_dot', False)
    interactive = kwargs.get('interactive', False)
    
    # Print the summary
    print_feature_extractor_detailed_summary(feature_extractor, input_shape, level, style)
    
    # Additional options
    if export_dot:
        export_model_graph_to_dot(feature_extractor, input_shape)
    
    if interactive:
        open_interactive_model_viewer(feature_extractor, input_shape)
    
    # Show available options
    print(colorize(f"\n{'Available Summary Options:'}", Colors.HEADER, bold=True))
    print(f"• Levels: {colorize('standard, detailed, connections, graph, ascii_art', Colors.OKCYAN)}")
    print(f"• ASCII Styles: {colorize('compact, detailed, flowchart, tree', Colors.BRIGHT_YELLOW)}")
    print(f"• Export options: {colorize('export_dot=True, interactive=True', Colors.BRIGHT_MAGENTA)}")
    example_text = 'print_enhanced_summary(model, input_shape, level="ascii_art", style="flowchart")'
    print(f"• Example: {colorize(example_text, Colors.BRIGHT_CYAN)}")

# Export functionality for advanced users
def export_model_graph_to_dot(feature_extractor, input_shape, filename=None):
    """Export model graph to Graphviz DOT format for external visualization"""
    print(colorize("Graph export functionality not available.", Colors.WARNING))
    return None

def open_interactive_model_viewer(feature_extractor, input_shape):
    """Open interactive model viewer if available"""
    print(colorize("Interactive viewer not available.", Colors.WARNING))
def _print_ascii_art_summary(feature_extractor, input_shape, style="compact"):
    """Print ASCII art visualization with only the requested style"""
    print(colorize(f"\n{'='*120}", Colors.BRIGHT_BLUE, bold=True))
    print(colorize(f"ASCII ART VISUALIZATION - {style.upper()} STYLE", Colors.BRIGHT_BLUE, bold=True))
    print(colorize(f"{'='*120}", Colors.BRIGHT_BLUE, bold=True))
    
    _print_builtin_ascii_summary(feature_extractor, input_shape, style)

def _print_builtin_ascii_summary(feature_extractor, input_shape, style="compact"):
    """Fallback ASCII visualization using built-in functionality"""
    print(colorize(f"\n{'='*80}", Colors.BRIGHT_BLUE, bold=True))
    print(colorize("BUILT-IN ASCII VISUALIZATION", Colors.BRIGHT_BLUE, bold=True))
    print(colorize(f"{'='*80}", Colors.BRIGHT_BLUE, bold=True))
    
    conv_config = feature_extractor.config['conv_blocks']
    filters_list = conv_config['filters']
    use_residual = conv_config.get('use_residual', False)
    
    if style == "compact":
        _print_compact_ascii(feature_extractor, input_shape, filters_list, use_residual)
    elif style == "tree":
        _print_tree_ascii(feature_extractor, input_shape, filters_list, use_residual)
    elif style == "flowchart":
        _print_flowchart_ascii(feature_extractor, input_shape, filters_list, use_residual)
    else:
        print(f"Style '{style}' using compact fallback")
        _print_compact_ascii(feature_extractor, input_shape, filters_list, use_residual)

def _print_compact_ascii(feature_extractor, input_shape, filters_list, use_residual):
    """Print compact ASCII representation"""
    print(f"\n{colorize('INPUT', Colors.INPUT, bold=True)} {colorize(str(input_shape), Colors.INPUT)}")
    print(f"  {colorize('│', Colors.DIM)}")
    print(f"  {colorize('▼', Colors.DIM)}")
    
    for block_idx, filters in enumerate(filters_list):
        print(f"\n{colorize(f'BLOCK {block_idx}', Colors.BLOCK, bold=True)} ({colorize(f'{filters} filters', Colors.BLOCK)})")
        
        if use_residual:
            print(f"  {colorize('┌─', Colors.DIM)}{colorize('MAIN PATH', Colors.CONV)} → {colorize('CONV+BN+ACT', Colors.CONV)}")
            print(f"  {colorize('├─', Colors.DIM)}{colorize('CONV+BN+ACT', Colors.CONV)}")
            print(f"  {colorize('╟─', Colors.RESIDUAL, bold=True)}{colorize('SKIP PATH:', Colors.RESIDUAL)} → {colorize('CONV+BN', Colors.RESIDUAL)}")
            print(f"  {colorize('╚═', Colors.DIM)}{colorize('MERGE', Colors.MERGE, bold=True)} → {colorize('ADD+ACT', Colors.MERGE)}")
        else:
            print(f"  {colorize('├─', Colors.DIM)}{colorize('CONV+BN+ACT', Colors.CONV)}")
            print(f"  {colorize('└─', Colors.DIM)}{colorize('CONV+BN+ACT', Colors.CONV)}")
        
        print(f"  {colorize('│', Colors.DIM)}")
        print(f"  {colorize('▼', Colors.DIM)}")

def _print_tree_ascii(feature_extractor, input_shape, filters_list, use_residual):
    """Print tree-style ASCII representation"""
    print(f"\n{colorize('INPUT', Colors.INPUT, bold=True)} {colorize(str(input_shape), Colors.INPUT)}")
    
    for block_idx, filters in enumerate(filters_list):
        is_last_block = block_idx == len(filters_list) - 1
        block_prefix = "└──" if is_last_block else "├──"
        continuation = "    " if is_last_block else "│   "
        
        print(f"{colorize(block_prefix, Colors.DIM)} {colorize(f'BLOCK_{block_idx}', Colors.BLOCK, bold=True)} ({colorize(f'{filters}f', Colors.BLOCK)})")
        
        if use_residual:
            print(f"{continuation}{colorize('├──', Colors.DIM)} {colorize('MAIN_PATH', Colors.CONV)}")
            print(f"{continuation}{colorize('│  ', Colors.DIM)} {colorize('├──', Colors.DIM)} {colorize('Conv2D', Colors.CONV)}")
            print(f"{continuation}{colorize('│  ', Colors.DIM)} {colorize('├──', Colors.DIM)} {colorize('BatchNorm', Colors.BN)}")
            print(f"{continuation}{colorize('│  ', Colors.DIM)} {colorize('└──', Colors.DIM)} {colorize('Activation', Colors.ACTIVATION)}")
            print(f"{continuation}{colorize('├──', Colors.DIM)} {colorize('SKIP_PATH', Colors.RESIDUAL)}")
            print(f"{continuation}{colorize('│  ', Colors.DIM)} {colorize('├──', Colors.DIM)} {colorize('Conv2D', Colors.RESIDUAL)}")
            print(f"{continuation}{colorize('│  ', Colors.DIM)} {colorize('└──', Colors.DIM)} {colorize('BatchNorm', Colors.RESIDUAL)}")
            print(f"{continuation}{colorize('└──', Colors.DIM)} {colorize('MERGE', Colors.MERGE, bold=True)}")
        else:
            print(f"{continuation}{colorize('├──', Colors.DIM)} {colorize('Conv2D', Colors.CONV)}")
            print(f"{continuation}{colorize('├──', Colors.DIM)} {colorize('BatchNorm', Colors.BN)}")
            print(f"{continuation}{colorize('├──', Colors.DIM)} {colorize('Activation', Colors.ACTIVATION)}")
            print(f"{continuation}{colorize('├──', Colors.DIM)} {colorize('Conv2D', Colors.CONV)}")
            print(f"{continuation}{colorize('├──', Colors.DIM)} {colorize('BatchNorm', Colors.BN)}")
            print(f"{continuation}{colorize('└──', Colors.DIM)} {colorize('Activation', Colors.ACTIVATION)}")

def _print_flowchart_ascii(feature_extractor, input_shape, filters_list, use_residual):
    """Print flowchart-style ASCII representation with center alignment using double stroke lines"""
    # Get terminal width for centering (default to 80 if not available)
    try:
        import shutil
        terminal_width = shutil.get_terminal_size().columns
        print(f"Terminal width detected: {terminal_width}")
    except:
        terminal_width = 80
        print(f"Could not detect terminal width, using default: {terminal_width}")
    
    # Calculate center position for blocks
    if use_residual:
        block_width = 50  # Wider block to contain both main and skip paths
    else:
        block_width = 30  # Narrower block for simple path
    center_pos = (terminal_width - block_width) // 2
    center_padding = " " * max(0, center_pos)
    
    # Connector positions relative to center
    connector_pos = center_pos + block_width // 2  # Position for vertical connectors
    connector_padding = " " * max(0, connector_pos)
    
    # INPUT block (centered) - using double stroke lines
    # Try to retrieve batch size from the feature extractor model
    batch_size = "?"  # Default fallback
    
    try:
        # Try to get batch size from the model's input specification
        if hasattr(feature_extractor, 'built') and feature_extractor.built:
            # If model is built, try to get input spec
            if hasattr(feature_extractor, 'input_spec') and feature_extractor.input_spec:
                if hasattr(feature_extractor.input_spec, 'shape') and feature_extractor.input_spec.shape:
                    batch_dim = feature_extractor.input_spec.shape[0]
                    batch_size = str(batch_dim) if batch_dim is not None else "None"
        
        # Alternative: try to build a functional model and get its input shape
        if batch_size == "?":
            try:
                temp_model = feature_extractor.build_model(input_shape)
                if temp_model.input_shape and len(temp_model.input_shape) > 0:
                    batch_dim = temp_model.input_shape[0]
                    batch_size = str(batch_dim) if batch_dim is not None else "None"
            except:
                pass  # Keep default "?"
                
    except Exception:
        # If any error occurs, keep the default "?"
        pass
    
    # Format input shape to show batch size and layer dimensions like typical CNN networks
    layer_shape = " x ".join(map(str, input_shape))  # Convert (H, W, C) to "HxWxC"
    input_display = f"({batch_size} x {layer_shape})"
    input_content = f"    INPUT {input_display}   "
    
    # Calculate dynamic border width based on content
    content_width = len(input_content)
    border_width = max(content_width, 13)  # Minimum width of 13 for aesthetics
    
    # Calculate center padding specifically for the INPUT block
    input_center_pos = (terminal_width - border_width - 2) // 2  # -2 for the border characters
    input_center_padding = " " * max(0, input_center_pos)
    
    print(f"\n{input_center_padding}{colorize('╔' + '═' * border_width + '╗', Colors.INPUT, bold=True)}")
    print(f"{input_center_padding}{colorize(f'║{input_content.center(border_width)}║', Colors.INPUT, bold=True)}")
    print(f"{input_center_padding}{colorize('╚' + '═' * border_width + '╝', Colors.INPUT, bold=True)}")
    print(f"{connector_padding}{colorize('║', Colors.DIM)}")
    print(f"{connector_padding}{colorize('▼', Colors.DIM)}")
    
    for block_idx, filters in enumerate(filters_list):
        if use_residual:
            # Large block containing both main and skip paths - using double stroke lines
            print(f"\n{center_padding}{colorize('╔' + '═' * (block_width-2) + '╗', Colors.BLOCK, bold=True)}")
            print(f"{center_padding}{colorize(f'║                BLOCK {block_idx}               ║', Colors.BLOCK, bold=True)}")
            print(f"{center_padding}{colorize('╠' + '═' * (block_width-2) + '╣', Colors.BLOCK, bold=True)}")
            print(f"{center_padding}{colorize('║                      ║                      ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║    ║═══ MAIN ═══║         ║═══ SKIP ═══║   ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║    ║            ║         ║            ║   ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║    ║ CONV+BN+ACT║         ║  CONV+BN   ║   ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║    ║            ║         ║            ║   ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║    ║════════════║         ║════════════║   ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║              ║                     ║       ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║              ║════════ADD+ACT══════║       ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║                      ║                      ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('╚' + '═' * (block_width-2) + '╝', Colors.BLOCK, bold=True)}")
        else:
            # Smaller block for simple path - using double stroke lines
            print(f"\n{center_padding}{colorize('╔' + '═' * (block_width-2) + '╗', Colors.BLOCK, bold=True)}")
            print(f"{center_padding}{colorize(f'║        BLOCK {block_idx} ({filters}f)        ║', Colors.BLOCK, bold=True)}")
            print(f"{center_padding}{colorize('╠' + '═' * (block_width-2) + '╣', Colors.BLOCK, bold=True)}")
            print(f"{center_padding}{colorize('║             ║              ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║      CONV+BN+ACT       ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║             ║              ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║      CONV+BN+ACT       ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('║             ║              ║', Colors.BLOCK)}")
            print(f"{center_padding}{colorize('╚' + '═' * (block_width-2) + '╝', Colors.BLOCK, bold=True)}")
        
        print(f"{connector_padding}{colorize('║', Colors.DIM)}")
        print(f"{connector_padding}{colorize('▼', Colors.DIM)}")