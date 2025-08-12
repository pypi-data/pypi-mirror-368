# Neutrophils Core

[![CI Pipeline](https://github.com/bpi-oxford/neutrophils-core/actions/workflows/test-and-deploy.yml/badge.svg)](https://github.com/bpi-oxford/neutrophils-core/actions/workflows/test-and-deploy.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A shared library for neutrophil classification providing unified interfaces for both 2D and 3D model inference, data preprocessing, and common utilities.

## Overview

This package serves as the core shared library between:
- The main neutrophils training repository
- The neutrophils classifier frontend app

## Features

- **Unified Model Interface**: Support for both 2D and 3D neutrophil classification models
- **Data Preprocessing**: Image augmentations, 3D→2D MIP projections, and normalization
- **Configuration Management**: Unified configuration loading and validation
- **Metrics & Loss Functions**: Comprehensive evaluation metrics and loss functions
- **Utilities**: Image I/O, tracking, and visualization tools

## Installation

### As a Git Submodule

```bash
# Add as submodule to your project
git submodule add https://github.com/bpi-oxford/neutrophils-core.git

# Initialize and update
git submodule update --init --recursive
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/bpi-oxford/neutrophils-core.git
cd neutrophils-core

# Install in development mode
pip install -e .
```

## Quick Start

### Unified Model Interface

```python
from neutrophils_core.models import Classifier

# Auto-detect model type (2D/3D)
classifier = Classifier(model_path='path/to/model')
prediction = classifier.predict(input_data)

# Explicit 3D model with 2D MIP option
classifier = Classifier(model_type='3d', model_path='path/to/3d/model')
prediction = classifier.predict(image_3d, return_2d_mip=True)
```

### Data Preprocessing

```python
from neutrophils_core.preprocessing import load_image, create_mip_projection
from neutrophils_core.preprocessing.augmentations_2d import random_flip_2d

# Load and preprocess image
image = load_image('path/to/image.tiff')
mip_2d = create_mip_projection(image)
augmented = random_flip_2d(mip_2d)
```

### Configuration Management

```python
from neutrophils_core.config import ConfigManager

config = ConfigManager.load_config('path/to/config.toml')
model_config = config.get_model_config()
```

## Architecture

```
neutrophils_core/
├── models/              # Unified model interface and loading
├── preprocessing/       # Data preprocessing and augmentations
├── config/             # Configuration management
├── metrics/            # Evaluation metrics and loss functions
└── utils/              # Common utilities
```

## Development

### Status Badges

The badges above show:
- **CI Pipeline**: Status of automated testing
- **Python 3.8+**: Supported Python versions
- **License**: MIT License

### Running Tests

```bash
pytest tests/
```

### Adding New Features

1. Follow the existing module structure
2. Add comprehensive tests
3. Update documentation
4. Ensure backward compatibility

## License

This project is licensed under the MIT License.