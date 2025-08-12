"""
Preprocessing module for neutrophil image data.

This module provides:
- 3D to 2D MIP projections
- Principal plane estimation utilities

Note: Some modules are planned for future implementation.
"""

from .projection import create_mip_projection, principal_plane_estimation

__all__ = [
    "create_mip_projection",
    "principal_plane_estimation",
]
