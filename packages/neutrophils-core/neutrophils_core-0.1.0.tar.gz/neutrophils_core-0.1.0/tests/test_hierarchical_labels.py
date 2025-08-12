#!/usr/bin/env python3
"""
Test suite for hierarchical neutrophil classification labels and utilities.

This module contains comprehensive tests for the hierarchical_labels module,
covering hierarchy validation, label conversion, and utility functions using pytest.
"""

import pytest
import numpy as np
from neutrophils_core.loader.hierarchical_labels import (
    NEUTROPHIL_HIERARCHY,
    get_head_info,
    get_parent_child_mapping,
    convert_flat_label_to_hierarchical,
    convert_hierarchical_to_flat_label,
    validate_hierarchy_consistency,
    validate_hierarchical_labels,
    get_class_name_to_id_mapping,
    get_ordinal_distance_matrix,
    print_hierarchy_summary
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def hierarchy():
    """Fixture providing the neutrophil hierarchy."""
    return NEUTROPHIL_HIERARCHY


@pytest.fixture
def hierarchy_info():
    """Fixture providing hierarchy information."""
    return get_head_info(NEUTROPHIL_HIERARCHY)


@pytest.fixture
def parent_child_mapping():
    """Fixture providing parent-child mappings."""
    return get_parent_child_mapping(NEUTROPHIL_HIERARCHY)


# =============================================================================
# TEST NEUTROPHIL HIERARCHY STRUCTURE
# =============================================================================

class TestNeutrophilHierarchy:
    """Test cases for neutrophil hierarchy definition and basic structure."""
    
    def test_hierarchy_structure(self, hierarchy):
        """Test basic hierarchy structure."""
        # Check that all expected heads exist
        expected_heads = ['coarse', 'stage']
        assert set(hierarchy.keys()) == set(expected_heads)
        
        # Check hierarchy levels
        assert hierarchy['coarse']['level'] == 0
        assert hierarchy['stage']['level'] == 1
        
        # Check parent relationships
        assert hierarchy['coarse']['parent_head'] is None
        assert hierarchy['stage']['parent_head'] == 'coarse'
    
    def test_class_counts(self, hierarchy):
        """Test expected number of classes in each head."""
        assert len(hierarchy['coarse']['classes']) == 2
        assert len(hierarchy['stage']['classes']) == 4
    
    def test_class_names(self, hierarchy):
        """Test specific class names."""
        # Coarse level classes
        coarse_classes = set(hierarchy['coarse']['classes'].keys())
        assert coarse_classes == {'early', 'late'}
        
        # Stage level classes
        stage_classes = set(hierarchy['stage']['classes'].keys())
        assert stage_classes == {'M', 'MM', 'BN', 'SN'}
    
    def test_ordinal_positions(self, hierarchy):
        """Test ordinal position assignments."""
        # Stage level should have ordinal positions
        stage_classes = hierarchy['stage']['classes']
        expected_ordinals = {'M': 0, 'MM': 1, 'BN': 2, 'SN': 3}
        for class_name, expected_ordinal in expected_ordinals.items():
            assert stage_classes[class_name]['ordinal_position'] == expected_ordinal
        
        # All stage classes should have ordinal positions
        assert all('ordinal_position' in class_data
                  for class_data in stage_classes.values())


# =============================================================================
# TEST HEAD INFO EXTRACTION
# =============================================================================

class TestHeadInfo:
    """Test cases for get_head_info function."""
    
    def test_head_info_structure(self, hierarchy_info):
        """Test structure of head info output."""
        for head_name, head_info in hierarchy_info.items():
            # Check required fields
            required_fields = ['num_classes', 'level', 'parent_head', 'class_names', 'class_descriptions']
            for field in required_fields:
                assert field in head_info
            
            # Check field types
            assert isinstance(head_info['num_classes'], int)
            assert isinstance(head_info['level'], int)
            assert isinstance(head_info['class_names'], list)
            assert isinstance(head_info['class_descriptions'], dict)
            
            # Check parent_head is None or string
            assert head_info['parent_head'] is None or isinstance(head_info['parent_head'], str)
    
    def test_head_info_values(self, hierarchy_info):
        """Test specific values in head info."""
        # Coarse head
        coarse_info = hierarchy_info['coarse']
        assert coarse_info['num_classes'] == 2
        assert coarse_info['level'] == 0
        assert coarse_info['parent_head'] is None
        assert set(coarse_info['class_names']) == {'early', 'late'}
        
        # Stage head
        stage_info = hierarchy_info['stage']
        assert stage_info['num_classes'] == 4
        assert stage_info['level'] == 1
        assert stage_info['parent_head'] == 'coarse'
        assert set(stage_info['class_names']) == {'M', 'MM', 'BN', 'SN'}


# =============================================================================
# TEST LABEL CONVERSION
# =============================================================================

class TestLabelConversion:
    """Test cases for label conversion functions."""
    
    @pytest.mark.parametrize("flat_label,expected_hierarchical", [
        ('M', {'coarse': 0, 'stage': 0}),
        ('MM', {'coarse': 0, 'stage': 1}),
        ('BN', {'coarse': 1, 'stage': 2}),
        ('SN', {'coarse': 1, 'stage': 3}),
    ])
    def test_flat_to_hierarchical_conversion(self, flat_label, expected_hierarchical, hierarchy_info):
        """Test conversion from flat labels to hierarchical labels."""
        result = convert_flat_label_to_hierarchical(flat_label, hierarchy_info)
        assert result == expected_hierarchical
    
    @pytest.mark.parametrize("integer_label,expected_hierarchical", [
        (0, {'coarse': 0, 'stage': 0}),
        (3, {'coarse': 1, 'stage': 3}),
    ])
    def test_integer_label_conversion(self, integer_label, expected_hierarchical, hierarchy_info):
        """Test conversion with integer labels."""
        result = convert_flat_label_to_hierarchical(integer_label, hierarchy_info, 'stage')
        assert result == expected_hierarchical
    
    @pytest.mark.parametrize("hierarchical_labels,target_head,expected", [
        ({'coarse': 1, 'stage': 3}, 'coarse', 1),
        ({'coarse': 1, 'stage': 3}, 'stage', 3),
    ])
    def test_hierarchical_to_flat_conversion(self, hierarchical_labels, target_head, expected):
        """Test conversion from hierarchical to flat labels."""
        result = convert_hierarchical_to_flat_label(hierarchical_labels, target_head)
        assert result == expected
    
    def test_conversion_errors(self, hierarchy_info):
        """Test edge cases and error conditions."""
        # Test with invalid class name
        with pytest.raises(ValueError, match="Unknown class"):
            convert_flat_label_to_hierarchical('invalid_class', hierarchy_info)
        
        # Test with invalid head name
        with pytest.raises(ValueError, match="Unknown source head"):
            convert_flat_label_to_hierarchical('M', hierarchy_info, 'invalid_head')
        
        # Test with out-of-range integer
        with pytest.raises(ValueError, match="out of range"):
            convert_flat_label_to_hierarchical(999, hierarchy_info, 'stage')
        
        # Test hierarchical to flat with missing head
        hierarchical_labels = {'coarse': 0}
        with pytest.raises(ValueError, match="not found"):
            convert_hierarchical_to_flat_label(hierarchical_labels, 'stage')


# =============================================================================
# TEST VALIDATION FUNCTIONS
# =============================================================================

class TestValidation:
    """Test cases for validation functions."""
    
    def test_hierarchy_consistency_validation_valid(self, hierarchy):
        """Test hierarchy consistency validation with valid hierarchy."""
        errors = validate_hierarchy_consistency(hierarchy)
        assert len(errors) == 0
    
    def test_hierarchy_consistency_validation_invalid(self):
        """Test hierarchy consistency validation with invalid hierarchy."""
        invalid_hierarchy = {
            'head1': {
                'level': 0,
                'classes': {
                    'class1': {'class_id': 0},
                    'class2': {'class_id': 0}  # Duplicate class_id
                }
            }
        }
        errors = validate_hierarchy_consistency(invalid_hierarchy)
        assert len(errors) > 0
        assert any('Duplicate class_id' in error for error in errors)
    
    def test_hierarchical_labels_validation_valid(self, hierarchy_info):
        """Test hierarchical labels validation with valid labels."""
        valid_labels = {'coarse': 0, 'stage': 0}
        errors = validate_hierarchical_labels(valid_labels, hierarchy_info)
        assert len(errors) == 0
    
    def test_hierarchical_labels_validation_invalid_indices(self, hierarchy_info):
        """Test hierarchical labels validation with invalid class indices."""
        invalid_labels = {'coarse': 0, 'stage': 999}
        errors = validate_hierarchical_labels(invalid_labels, hierarchy_info)
        assert len(errors) > 0
        assert any('Invalid class index' in error for error in errors)
    
    def test_hierarchical_labels_validation_missing_heads(self, hierarchy_info):
        """Test hierarchical labels validation with missing heads."""
        incomplete_labels = {'coarse': 0}
        errors = validate_hierarchical_labels(incomplete_labels, hierarchy_info)
        assert len(errors) > 0
        assert any('Missing label for head' in error for error in errors)
    
    def test_hierarchical_labels_validation_inconsistent_relationships(self, hierarchy_info):
        """Test hierarchical labels validation with inconsistent parent-child relationships."""
        # BN stage (late) but early coarse - inconsistent
        inconsistent_labels = {'coarse': 0, 'stage': 2}
        errors = validate_hierarchical_labels(inconsistent_labels, hierarchy_info)
        assert len(errors) > 0
        assert any('Inconsistent parent-child relationship' in error for error in errors)


# =============================================================================
# TEST UTILITY FUNCTIONS
# =============================================================================

class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_parent_child_mapping(self, parent_child_mapping):
        """Test parent-child mapping extraction."""
        # Check structure
        assert 'child_to_parent' in parent_child_mapping
        assert 'parent_to_children' in parent_child_mapping
        
        # Test specific mappings
        child_to_parent = parent_child_mapping['child_to_parent']
        assert child_to_parent[('stage', 'M')] == ('coarse', 'early')
        assert child_to_parent[('stage', 'SN')] == ('coarse', 'late')
        
        # Test parent to children
        parent_to_children = parent_child_mapping['parent_to_children']
        assert ('coarse', 'early') in parent_to_children
        early_children = parent_to_children[('coarse', 'early')]
        assert set(early_children) == {('stage', 'M'), ('stage', 'MM')}
    
    def test_class_name_to_id_mapping(self, hierarchy):
        """Test class name to ID mapping."""
        mapping = get_class_name_to_id_mapping(hierarchy)
        
        # Check structure
        for head_name in ['coarse', 'stage']:
            assert head_name in mapping
            assert isinstance(mapping[head_name], dict)
        
        # Test specific mappings
        assert mapping['stage']['M'] == 0
        assert mapping['stage']['SN'] == 3
        assert mapping['coarse']['early'] == 0
        assert mapping['coarse']['late'] == 1
    
    def test_ordinal_distance_matrix_with_ordinals(self, hierarchy_info):
        """Test ordinal distance matrix generation with head that has ordinal positions."""
        distance_matrix = get_ordinal_distance_matrix(hierarchy_info, 'stage')
        assert distance_matrix is not None
        assert distance_matrix.shape == (4, 4)
        
        # Test specific distances
        assert distance_matrix[0, 0] == 0  # M to M
        assert distance_matrix[0, 3] == 3  # M to SN
        assert distance_matrix[1, 2] == 1  # MM to BN
        
        # Test symmetry
        np.testing.assert_array_equal(distance_matrix, distance_matrix.T)
    
    def test_ordinal_distance_matrix_without_ordinals(self, hierarchy_info):
        """Test ordinal distance matrix generation with head that lacks ordinal positions."""
        distance_matrix = get_ordinal_distance_matrix(hierarchy_info, 'coarse')
        assert distance_matrix is None
    
    def test_ordinal_distance_matrix_invalid_head(self, hierarchy_info):
        """Test ordinal distance matrix generation with invalid head."""
        with pytest.raises(ValueError, match="Unknown head"):
            get_ordinal_distance_matrix(hierarchy_info, 'invalid_head')
    
    def test_print_hierarchy_summary(self, hierarchy, capsys):
        """Test hierarchy summary printing."""
        print_hierarchy_summary(hierarchy)
        captured = capsys.readouterr()
        
        # Check that output contains expected content
        assert "Neutrophil Classification Hierarchy" in captured.out
        assert "Level 0: COARSE" in captured.out
        assert "Level 1: STAGE" in captured.out


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for combined functionality."""
    
    @pytest.mark.parametrize("original_label", [
        'M', 'MM', 'BN', 'SN'
    ])
    def test_full_conversion_cycle(self, original_label, hierarchy_info, hierarchy):
        """Test full cycle: flat -> hierarchical -> flat."""
        # Convert to hierarchical
        hierarchical = convert_flat_label_to_hierarchical(
            original_label, hierarchy_info, 'stage'
        )
        
        # Convert back to flat
        recovered_label_id = convert_hierarchical_to_flat_label(
            hierarchical, 'stage'
        )
        
        # Verify we get back the same class ID
        expected_id = hierarchy['stage']['classes'][original_label]['class_id']
        assert recovered_label_id == expected_id
    
    def test_biological_ordering_consistency(self, hierarchy):
        """Test that the hierarchy respects biological ordering."""
        # Test that ordinal positions increase with maturity
        stage_classes = hierarchy['stage']['classes']
        maturity_order = ['M', 'MM', 'BN', 'SN']
        
        for i in range(len(maturity_order) - 1):
            current_ordinal = stage_classes[maturity_order[i]]['ordinal_position']
            next_ordinal = stage_classes[maturity_order[i + 1]]['ordinal_position']
            assert current_ordinal < next_ordinal
        
        # Test parent-child relationships align with maturity
        immature_stages = ['M', 'MM']
        mature_stages = ['BN', 'SN']
        
        for stage in immature_stages:
            assert stage_classes[stage]['parent'] == 'early'
        
        for stage in mature_stages:
            assert stage_classes[stage]['parent'] == 'late'
    
    def test_contradiction_penalty_support(self, hierarchy_info, parent_child_mapping):
        """Test that hierarchy supports contradiction penalty logic."""
        # Test that distance matrix can be generated for ordinal heads
        distance_matrix = get_ordinal_distance_matrix(hierarchy_info, 'stage')
        assert distance_matrix is not None
        
        # Test that parent-child mappings are available
        assert len(parent_child_mapping['child_to_parent']) > 0
        assert len(parent_child_mapping['parent_to_children']) > 0
        
        # Test that hierarchical labels can be validated for consistency
        test_labels = {'coarse': 0, 'stage': 0}
        errors = validate_hierarchical_labels(test_labels, hierarchy_info)
        assert len(errors) == 0


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestPerformance:
    """Performance tests for hierarchical label operations."""
    
    def test_label_conversion_performance(self, hierarchy_info):
        """Test performance of label conversion."""
        def convert_labels():
            labels = ['M', 'MM', 'BN', 'SN']
            results = []
            for label in labels:
                hierarchical = convert_flat_label_to_hierarchical(label, hierarchy_info)
                results.append(hierarchical)
            return results
        
        # Run the function to test basic performance
        results = convert_labels()
        assert len(results) == 4
        
        # Verify all conversions are correct
        expected_results = [
            {'coarse': 0, 'stage': 0},  # M
            {'coarse': 0, 'stage': 1},  # MM
            {'coarse': 1, 'stage': 2},  # BN
            {'coarse': 1, 'stage': 3},  # SN
        ]
        assert results == expected_results
    
    def test_validation_performance(self, hierarchy_info):
        """Test performance of hierarchy validation."""
        def validate_labels():
            test_cases = [
                {'coarse': 0, 'stage': 0},
                {'coarse': 0, 'stage': 1},
                {'coarse': 1, 'stage': 2},
                {'coarse': 1, 'stage': 3},
            ]
            results = []
            for labels in test_cases:
                errors = validate_hierarchical_labels(labels, hierarchy_info)
                results.append(len(errors))
            return results
        
        # Run the function to test basic performance
        results = validate_labels()
        assert all(error_count == 0 for error_count in results)


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_hierarchy(self):
        """Test behavior with empty hierarchy."""
        empty_hierarchy = {}
        head_info = get_head_info(empty_hierarchy)
        assert head_info == {}
        
        errors = validate_hierarchy_consistency(empty_hierarchy)
        assert len(errors) == 0  # Empty hierarchy is technically valid
    
    def test_single_class_hierarchy(self):
        """Test behavior with single-class hierarchy."""
        single_class_hierarchy = {
            'single_head': {
                'level': 0,
                'parent_head': None,
                'classes': {
                    'single_class': {'class_id': 0, 'description': 'Only class'}
                }
            }
        }
        
        head_info = get_head_info(single_class_hierarchy)
        assert head_info['single_head']['num_classes'] == 1
        assert head_info['single_head']['class_names'] == ['single_class']
        
        errors = validate_hierarchy_consistency(single_class_hierarchy)
        assert len(errors) == 0
    
    def test_boundary_label_values(self, hierarchy_info):
        """Test label conversion with boundary values."""
        # Test with first and last class indices
        first_result = convert_flat_label_to_hierarchical(0, hierarchy_info, 'stage')
        assert 'stage' in first_result
        assert first_result['stage'] == 0
        
        last_result = convert_flat_label_to_hierarchical(3, hierarchy_info, 'stage')
        assert 'stage' in last_result
        assert last_result['stage'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])