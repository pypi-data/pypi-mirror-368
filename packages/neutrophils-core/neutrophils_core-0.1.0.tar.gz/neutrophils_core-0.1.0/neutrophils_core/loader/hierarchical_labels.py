#!/usr/bin/env python3
"""
Hierarchical neutrophil classification labels and utilities.

This module defines the neutrophil maturation hierarchy and provides utilities for
converting between flat and hierarchical label representations. The hierarchy supports
the contradiction penalty logic for training models that respect biological ordering.

Neutrophil Maturation Hierarchy:
===============================

The neutrophil classification follows a two-level hierarchical structure:

Level 0 (Standard): Binary classification between early and late stage neutrophils
- early: Early stage neutrophils (M, MM)
- late: Late stage neutrophils (BN, SN)

Level 1 (Stage): Fine-grained maturation stages
- M: Myelocyte
- MM: Metamyelocyte  
- BN: Band Neutrophil
- SN: Segmented Neutrophil

Biological Ordering:
===================
The classification respects the natural biological progression:
M → MM → BN → SN (increasing maturity)

This ordering is critical for:
- Ordinal loss functions that penalize violations of biological sequence
- Contradiction penalty logic that enforces parent-child consistency
- Model architectures with hierarchical outputs
"""

from typing import Dict, List, Any, Union, Optional, Tuple
import numpy as np


# =============================================================================
# NEUTROPHIL HIERARCHY DEFINITION
# =============================================================================

NEUTROPHIL_HIERARCHY = {
    "coarse": {
        "level": 0,
        "parent_head": None,
        "classes": {
            "early": {
                "class_id": 0,
                "description": "Early stage neutrophils",
                "children": ["M", "MM"]
            },
            "late": {
                "class_id": 1,
                "description": "Late stage neutrophils",
                "children": ["BN", "SN"]
            }
        }
    },
    
    "stage": {
        "level": 1,
        "parent_head": "coarse",
        "classes": {
            "M": {
                "class_id": 0,
                "description": "Myelocyte - earliest recognizable neutrophil precursor",
                "parent": "early",
                "parent_id": 0,
                "ordinal_position": 0
            },
            "MM": {
                "class_id": 1,
                "description": "Metamyelocyte - intermediate maturation stage",
                "parent": "early",
                "parent_id": 0,
                "ordinal_position": 1
            },
            "BN": {
                "class_id": 2,
                "description": "Band Neutrophil - nearly mature neutrophil",
                "parent": "late",
                "parent_id": 1,
                "ordinal_position": 2
            },
            "SN": {
                "class_id": 3,
                "description": "Segmented Neutrophil - fully mature neutrophil",
                "parent": "late",
                "parent_id": 1,
                "ordinal_position": 3
            }
        }
    }
}


# =============================================================================
# HIERARCHY ANALYSIS FUNCTIONS
# =============================================================================

def get_head_info(hierarchy: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Analyze the hierarchy and return metadata for each classification head.
    
    Args:
        hierarchy: Nested dictionary defining the hierarchical structure
        
    Returns:
        Dictionary mapping head names to their metadata:
        - num_classes: Number of classes for this head
        - level: Hierarchical level (0=top, 1=mid, 2=bottom, etc.)
        - parent_head: Name of parent head (None for root level)
        - class_names: List of class names for this head
        - class_descriptions: Dictionary mapping class names to descriptions
        - ordinal_mapping: Dictionary mapping class names to ordinal positions (if applicable)
        
    Example:
        >>> head_info = get_head_info(NEUTROPHIL_HIERARCHY)
        >>> head_info['stage']['num_classes']
        4
        >>> head_info['stage']['class_names']
        ['M', 'MM', 'BN', 'SN']
    """
    head_info = {}
    
    for head_name, head_data in hierarchy.items():
        classes = head_data["classes"]
        class_names = list(classes.keys())
        
        # Extract class descriptions
        class_descriptions = {
            name: data.get("description", f"Class {name}")
            for name, data in classes.items()
        }
        
        # Extract ordinal mapping if available
        ordinal_mapping = {}
        for name, data in classes.items():
            if "ordinal_position" in data:
                ordinal_mapping[name] = data["ordinal_position"]
        
        head_info[head_name] = {
            "num_classes": len(classes),
            "level": head_data["level"],
            "parent_head": head_data.get("parent_head"),
            "class_names": class_names,
            "class_descriptions": class_descriptions,
            "ordinal_mapping": ordinal_mapping if ordinal_mapping else None
        }
    
    return head_info


def get_parent_child_mapping(hierarchy: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Extract parent-child relationships from the hierarchy.
    
    Args:
        hierarchy: Nested dictionary defining the hierarchical structure
        
    Returns:
        Dictionary containing parent-child mappings:
        - child_to_parent: Maps (child_head, child_class) -> (parent_head, parent_class)
        - parent_to_children: Maps (parent_head, parent_class) -> [(child_head, child_class), ...]
        
    Example:
        >>> mapping = get_parent_child_mapping(NEUTROPHIL_HIERARCHY)
        >>> mapping['child_to_parent'][('stage', 'M')]
        ('coarse', 'early')
    """
    child_to_parent = {}
    parent_to_children = {}
    
    for head_name, head_data in hierarchy.items():
        parent_head = head_data.get("parent_head")
        if parent_head is None:
            continue
            
        for class_name, class_data in head_data["classes"].items():
            parent_class = class_data.get("parent")
            if parent_class:
                # Map child to parent
                child_to_parent[(head_name, class_name)] = (parent_head, parent_class)
                
                # Map parent to children
                parent_key = (parent_head, parent_class)
                if parent_key not in parent_to_children:
                    parent_to_children[parent_key] = []
                parent_to_children[parent_key].append((head_name, class_name))
    
    return {
        "child_to_parent": child_to_parent,
        "parent_to_children": parent_to_children
    }


# =============================================================================
# LABEL CONVERSION FUNCTIONS
# =============================================================================

def convert_flat_label_to_hierarchical(
    flat_label: Union[str, int],
    hierarchy_info: Dict[str, Dict[str, Any]],
    source_head: str = "stage"
) -> Dict[str, int]:
    """
    Convert a single flat class label to hierarchical labels for all heads.
    
    Args:
        flat_label: Class label (string name or integer ID) from the source head
        hierarchy_info: Output from get_head_info() containing head metadata
        source_head: Name of the head containing the input label (default: "subclass")
        
    Returns:
        Dictionary mapping head names to class indices for hierarchical output
        
    Example:
        >>> hierarchy_info = get_head_info(NEUTROPHIL_HIERARCHY)
        >>> convert_flat_label_to_hierarchical("M", hierarchy_info)
        {'coarse': 0, 'stage': 0}
        
        >>> convert_flat_label_to_hierarchical("SN", hierarchy_info)
        {'coarse': 1, 'stage': 3}
    """
    if source_head not in hierarchy_info:
        raise ValueError(f"Unknown source head: {source_head}")
    
    # Convert label to string if it's an integer index
    if isinstance(flat_label, int):
        class_names = hierarchy_info[source_head]["class_names"]
        if flat_label >= len(class_names):
            raise ValueError(f"Label index {flat_label} out of range for head {source_head}")
        flat_label = class_names[flat_label]
    
    # Validate label exists in source head
    if flat_label not in hierarchy_info[source_head]["class_names"]:
        raise ValueError(f"Unknown class '{flat_label}' in head '{source_head}'")
    
    # Get the class data for the input label
    source_classes = NEUTROPHIL_HIERARCHY[source_head]["classes"]
    if flat_label not in source_classes:
        raise ValueError(f"Class '{flat_label}' not found in hierarchy definition")
    
    class_data = source_classes[flat_label]
    
    # Initialize result with the source head
    result = {source_head: class_data["class_id"]}
    
    # Traverse up the hierarchy to find parent labels
    current_head = source_head
    current_class = flat_label
    
    while True:
        current_head_data = NEUTROPHIL_HIERARCHY[current_head]
        parent_head = current_head_data.get("parent_head")
        
        if parent_head is None:
            break
            
        # Find parent class
        current_class_data = current_head_data["classes"][current_class]
        parent_class = current_class_data.get("parent")
        
        if parent_class is None:
            break
            
        # Get parent class ID
        parent_class_data = NEUTROPHIL_HIERARCHY[parent_head]["classes"][parent_class]
        result[parent_head] = parent_class_data["class_id"]
        
        # Move up the hierarchy
        current_head = parent_head
        current_class = parent_class
    
    # No child traversal needed for 2-level hierarchy
    
    return result


def convert_hierarchical_to_flat_label(
    hierarchical_labels: Dict[str, int],
    target_head: str = "stage"
) -> Union[str, int]:
    """
    Convert hierarchical labels to a single flat label for the target head.
    
    Args:
        hierarchical_labels: Dictionary mapping head names to class indices
        target_head: Name of the head to extract the label from
        
    Returns:
        Class index for the target head
        
    Example:
        >>> labels = {'coarse': 0, 'stage': 0}
        >>> convert_hierarchical_to_flat_label(labels, 'stage')
        0
    """
    if target_head not in hierarchical_labels:
        raise ValueError(f"Target head '{target_head}' not found in hierarchical labels")
    
    return hierarchical_labels[target_head]


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_hierarchy_consistency(hierarchy: Dict[str, Any]) -> List[str]:
    """
    Validate that the hierarchy structure is consistent and well-formed.
    
    Args:
        hierarchy: Nested dictionary defining the hierarchical structure
        
    Returns:
        List of validation error messages (empty if valid)
        
    Example:
        >>> errors = validate_hierarchy_consistency(NEUTROPHIL_HIERARCHY)
        >>> len(errors) == 0  # Should be True for valid hierarchy
        True
    """
    errors = []
    
    # Check that all heads have required fields
    for head_name, head_data in hierarchy.items():
        if "level" not in head_data:
            errors.append(f"Head '{head_name}' missing 'level' field")
        
        if "classes" not in head_data:
            errors.append(f"Head '{head_name}' missing 'classes' field")
            continue
        
        # Check class structure
        classes = head_data["classes"]
        for class_name, class_data in classes.items():
            if "class_id" not in class_data:
                errors.append(f"Class '{class_name}' in head '{head_name}' missing 'class_id'")
    
    # Check parent-child consistency
    parent_child_mapping = get_parent_child_mapping(hierarchy)
    
    for (child_head, child_class), (parent_head, parent_class) in parent_child_mapping["child_to_parent"].items():
        # Verify parent exists
        if parent_head not in hierarchy:
            errors.append(f"Parent head '{parent_head}' referenced by '{child_head}:{child_class}' does not exist")
            continue
            
        if parent_class not in hierarchy[parent_head]["classes"]:
            errors.append(f"Parent class '{parent_class}' in head '{parent_head}' does not exist")
    
    # Check class_id uniqueness within each head
    for head_name, head_data in hierarchy.items():
        class_ids = [class_data["class_id"] for class_data in head_data["classes"].values()]
        if len(class_ids) != len(set(class_ids)):
            errors.append(f"Duplicate class_id values found in head '{head_name}'")
    
    # Check ordinal positions if present
    for head_name, head_data in hierarchy.items():
        ordinal_positions = []
        for class_name, class_data in head_data["classes"].items():
            if "ordinal_position" in class_data:
                ordinal_positions.append(class_data["ordinal_position"])
        
        if ordinal_positions:
            if len(ordinal_positions) != len(set(ordinal_positions)):
                errors.append(f"Duplicate ordinal_position values found in head '{head_name}'")
            
            # Check if ordinal positions form a continuous sequence
            ordinal_positions.sort()
            expected = list(range(len(ordinal_positions)))
            if ordinal_positions != expected and ordinal_positions != list(range(min(ordinal_positions), max(ordinal_positions) + 1)):
                errors.append(f"Ordinal positions in head '{head_name}' are not continuous")
    
    return errors


def validate_hierarchical_labels(
    hierarchical_labels: Dict[str, int],
    hierarchy_info: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Validate that hierarchical labels are consistent across hierarchy levels.
    
    Args:
        hierarchical_labels: Dictionary mapping head names to class indices
        hierarchy_info: Output from get_head_info() containing head metadata
        
    Returns:
        List of validation error messages (empty if valid)
        
    Example:
        >>> hierarchy_info = get_head_info(NEUTROPHIL_HIERARCHY)
        >>> labels = {'coarse': 0, 'stage': 0}
        >>> errors = validate_hierarchical_labels(labels, hierarchy_info)
        >>> len(errors) == 0  # Should be True for consistent labels
        True
    """
    errors = []
    
    # Check that all required heads are present
    for head_name in hierarchy_info:
        if head_name not in hierarchical_labels:
            errors.append(f"Missing label for head '{head_name}'")
    
    # Check that class indices are valid
    for head_name, class_idx in hierarchical_labels.items():
        if head_name not in hierarchy_info:
            errors.append(f"Unknown head '{head_name}' in hierarchical labels")
            continue
            
        num_classes = hierarchy_info[head_name]["num_classes"]
        if not (0 <= class_idx < num_classes):
            errors.append(f"Invalid class index {class_idx} for head '{head_name}' (valid range: 0-{num_classes-1})")
    
    # Check parent-child consistency
    parent_child_mapping = get_parent_child_mapping(NEUTROPHIL_HIERARCHY)
    
    for head_name, class_idx in hierarchical_labels.items():
        if head_name not in hierarchy_info:
            continue
            
        class_names = hierarchy_info[head_name]["class_names"]
        if class_idx >= len(class_names):
            continue
            
        class_name = class_names[class_idx]
        
        # Check if this class has a parent
        child_key = (head_name, class_name)
        if child_key in parent_child_mapping["child_to_parent"]:
            parent_head, parent_class = parent_child_mapping["child_to_parent"][child_key]
            
            if parent_head in hierarchical_labels:
                parent_class_idx = hierarchical_labels[parent_head]
                parent_class_names = hierarchy_info[parent_head]["class_names"]
                
                if parent_class_idx < len(parent_class_names):
                    actual_parent_class = parent_class_names[parent_class_idx]
                    
                    if actual_parent_class != parent_class:
                        errors.append(
                            f"Inconsistent parent-child relationship: "
                            f"'{head_name}:{class_name}' expects parent '{parent_head}:{parent_class}' "
                            f"but got '{parent_head}:{actual_parent_class}'"
                        )
    
    return errors


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_class_name_to_id_mapping(hierarchy: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    """
    Create mapping from class names to class IDs for each head.
    
    Args:
        hierarchy: Nested dictionary defining the hierarchical structure
        
    Returns:
        Dictionary mapping head names to {class_name: class_id} dictionaries
    """
    mapping = {}
    for head_name, head_data in hierarchy.items():
        mapping[head_name] = {
            class_name: class_data["class_id"]
            for class_name, class_data in head_data["classes"].items()
        }
    return mapping


def get_ordinal_distance_matrix(hierarchy_info: Dict[str, Dict[str, Any]], head_name: str) -> Optional[np.ndarray]:
    """
    Create ordinal distance matrix for a head with ordinal positions.
    
    Args:
        hierarchy_info: Output from get_head_info() containing head metadata
        head_name: Name of the head to create distance matrix for
        
    Returns:
        NumPy array of shape (num_classes, num_classes) with ordinal distances,
        or None if the head doesn't have ordinal positions
        
    Example:
        >>> hierarchy_info = get_head_info(NEUTROPHIL_HIERARCHY)
        >>> matrix = get_ordinal_distance_matrix(hierarchy_info, 'stage')
        >>> matrix[0, 3]  # Distance from M to SN
        3.0
    """
    if head_name not in hierarchy_info:
        raise ValueError(f"Unknown head: {head_name}")
    
    head_info = hierarchy_info[head_name]
    ordinal_mapping = head_info.get("ordinal_mapping")
    
    if ordinal_mapping is None:
        return None
    
    num_classes = head_info["num_classes"]
    class_names = head_info["class_names"]
    
    # Create distance matrix
    distance_matrix = np.zeros((num_classes, num_classes))
    
    for i, class_i in enumerate(class_names):
        for j, class_j in enumerate(class_names):
            ordinal_i = ordinal_mapping[class_i]
            ordinal_j = ordinal_mapping[class_j]
            distance_matrix[i, j] = abs(ordinal_i - ordinal_j)
    
    return distance_matrix


def print_hierarchy_summary(hierarchy: Dict[str, Any]) -> None:
    """
    Print a human-readable summary of the hierarchy structure.
    
    Args:
        hierarchy: Nested dictionary defining the hierarchical structure
    """
    print("Neutrophil Classification Hierarchy")
    print("=" * 50)
    
    hierarchy_info = get_head_info(hierarchy)
    
    # Sort heads by level
    sorted_heads = sorted(hierarchy_info.items(), key=lambda x: x[1]["level"])
    
    for head_name, head_info in sorted_heads:
        level = head_info["level"]
        num_classes = head_info["num_classes"]
        parent_head = head_info["parent_head"]
        
        print(f"\nLevel {level}: {head_name.upper()}")
        print(f"  Classes: {num_classes}")
        print(f"  Parent: {parent_head or 'None'}")
        
        # Print class details
        head_data = hierarchy[head_name]
        for class_name, class_data in head_data["classes"].items():
            class_id = class_data["class_id"]
            description = class_data.get("description", "")
            parent = class_data.get("parent", "")
            ordinal = class_data.get("ordinal_position", "")
            
            details = []
            if parent:
                details.append(f"parent: {parent}")
            if isinstance(ordinal, int):
                details.append(f"ordinal: {ordinal}")
            
            detail_str = f" ({', '.join(details)})" if details else ""
            print(f"    {class_id}: {class_name}{detail_str}")
            if description:
                print(f"       {description}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Hierarchy definition
    "NEUTROPHIL_HIERARCHY",
    
    # Analysis functions
    "get_head_info",
    "get_parent_child_mapping",
    
    # Label conversion functions
    "convert_flat_label_to_hierarchical",
    "convert_hierarchical_to_flat_label",
    
    # Validation functions
    "validate_hierarchy_consistency",
    "validate_hierarchical_labels",
    
    # Utility functions
    "get_class_name_to_id_mapping",
    "get_ordinal_distance_matrix",
    "print_hierarchy_summary",
]


# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

# Validate hierarchy on import
if __name__ != "__main__":
    validation_errors = validate_hierarchy_consistency(NEUTROPHIL_HIERARCHY)
    if validation_errors:
        raise ValueError(f"Invalid hierarchy definition: {validation_errors}")


# =============================================================================
# MAIN FUNCTION FOR TESTING
# =============================================================================

def main():
    """Main function for testing and demonstration."""
    print("Testing Neutrophil Hierarchical Labels Module")
    print("=" * 60)
    
    # Print hierarchy summary
    print_hierarchy_summary(NEUTROPHIL_HIERARCHY)
    
    # Test hierarchy validation
    print(f"\nHierarchy Validation:")
    errors = validate_hierarchy_consistency(NEUTROPHIL_HIERARCHY)
    if errors:
        print("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Hierarchy is valid and consistent")
    
    # Test head info extraction
    print(f"\nHead Information:")
    hierarchy_info = get_head_info(NEUTROPHIL_HIERARCHY)
    for head_name, info in hierarchy_info.items():
        print(f"  {head_name}: {info['num_classes']} classes at level {info['level']}")
    
    # Test label conversion
    print(f"\nLabel Conversion Examples:")
    test_labels = ["M", "MM", "BN", "SN"]
    
    for label in test_labels:
        hierarchical = convert_flat_label_to_hierarchical(label, hierarchy_info)
        print(f"  {label:8} -> {hierarchical}")
    
    # Test hierarchical label validation
    print(f"\nHierarchical Label Validation:")
    test_hierarchical = {'coarse': 0, 'stage': 0}
    errors = validate_hierarchical_labels(test_hierarchical, hierarchy_info)
    if errors:
        print("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Hierarchical labels are valid and consistent")
    
    # Test ordinal distance matrix
    print(f"\nOrdinal Distance Matrix (Stage head):")
    distance_matrix = get_ordinal_distance_matrix(hierarchy_info, 'stage')
    if distance_matrix is not None:
        print(f"  Shape: {distance_matrix.shape}")
        print(f"  M->SN distance: {distance_matrix[0, 3]}")
        print(f"  MM->BN distance: {distance_matrix[1, 2]}")
    
    print(f"\nModule testing completed successfully!")


if __name__ == "__main__":
    main()