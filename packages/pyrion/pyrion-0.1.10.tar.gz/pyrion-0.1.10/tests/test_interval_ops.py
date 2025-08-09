"""Unit tests for pyrion.ops.interval_ops module."""

import pytest
import numpy as np
from typing import List

from pyrion.ops.interval_ops import (
    merge_intervals,
    _merge_intervals_numba,
    _merge_intervals_numpy,
    intersect_intervals,
    _intersect_intervals_numba,
    subtract_intervals,
    _subtract_intervals_numba,
    intervals_union
)


class TestFixtures:
    """Test data fixtures for interval operations."""
    
    @pytest.fixture
    def overlapping_intervals(self):
        """Overlapping intervals for merge testing."""
        return np.array([
            [10, 30],
            [25, 50],
            [100, 150],
            [140, 200],
            [300, 400]
        ], dtype=np.int32)
    
    @pytest.fixture
    def non_overlapping_intervals(self):
        """Non-overlapping intervals."""
        return np.array([
            [10, 20],
            [30, 40],
            [50, 60],
            [100, 110]
        ], dtype=np.int32)
    
    @pytest.fixture
    def adjacent_intervals(self):
        """Adjacent (touching) intervals."""
        return np.array([
            [10, 20],
            [20, 30],
            [30, 40],
            [50, 60]
        ], dtype=np.int32)
    
    @pytest.fixture
    def complex_intervals(self):
        """Complex overlapping pattern for thorough testing."""
        return np.array([
            [1, 10],
            [5, 15],
            [12, 25],
            [20, 30],
            [35, 45],
            [40, 50],
            [60, 70]
        ], dtype=np.int32)
    
    @pytest.fixture
    def intersecting_sets(self):
        """Two sets of intervals for intersection testing."""
        set1 = np.array([
            [10, 50],
            [100, 150],
            [200, 300]
        ], dtype=np.int32)
        
        set2 = np.array([
            [30, 70],
            [120, 180],
            [250, 350],
            [400, 500]  # No intersection with set1
        ], dtype=np.int32)
        
        return set1, set2


class TestMergeIntervals(TestFixtures):
    """Test interval merging functionality."""
    
    def test_merge_overlapping_intervals(self, overlapping_intervals):
        """Test merging of overlapping intervals."""
        result = merge_intervals(overlapping_intervals)
        
        expected = np.array([
            [10, 50],    # Merged [10,30] and [25,50]
            [100, 200],  # Merged [100,150] and [140,200]
            [300, 400]   # No merge needed
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_merge_non_overlapping_intervals(self, non_overlapping_intervals):
        """Test merging of non-overlapping intervals."""
        result = merge_intervals(non_overlapping_intervals)
        
        # Should return sorted intervals unchanged
        expected = np.array([
            [10, 20],
            [30, 40],
            [50, 60],
            [100, 110]
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_merge_adjacent_intervals(self, adjacent_intervals):
        """Test merging of adjacent (touching) intervals."""
        result = merge_intervals(adjacent_intervals)
        
        expected = np.array([
            [10, 40],  # Merged [10,20], [20,30], [30,40]
            [50, 60]   # No merge needed
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_merge_complex_pattern(self, complex_intervals):
        """Test merging of complex overlapping pattern."""
        result = merge_intervals(complex_intervals)
        
        expected = np.array([
            [1, 30],   # Merged [1,10], [5,15], [12,25], [20,30]
            [35, 50],  # Merged [35,45], [40,50]
            [60, 70]   # No merge needed
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_merge_single_interval(self):
        """Test merging single interval."""
        single = np.array([[100, 200]], dtype=np.int32)
        result = merge_intervals(single)
        
        assert np.array_equal(result, single)
    
    def test_merge_empty_array(self):
        """Test merging empty array."""
        empty = np.array([], dtype=np.int32).reshape(0, 2)
        result = merge_intervals(empty)
        
        assert result.shape == (0, 2)
        assert result.dtype == np.int32
    
    def test_merge_unsorted_intervals(self):
        """Test merging unsorted intervals."""
        unsorted = np.array([
            [100, 150],
            [10, 30],
            [25, 50],
            [200, 300]
        ], dtype=np.int32)
        
        result = merge_intervals(unsorted)
        
        expected = np.array([
            [10, 50],     # Merged and sorted
            [100, 150],
            [200, 300]
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_merge_numba_vs_numpy(self, complex_intervals):
        """Test that numba and numpy implementations give same results."""
        result_numba = _merge_intervals_numba(complex_intervals)
        result_numpy = _merge_intervals_numpy(complex_intervals)
        
        assert np.array_equal(result_numba, result_numpy)
    
    def test_merge_algorithm_selection(self, overlapping_intervals):
        """Test automatic algorithm selection."""
        # Force numba
        result_numba = merge_intervals(overlapping_intervals, use_numba=True)
        # Force numpy
        result_numpy = merge_intervals(overlapping_intervals, use_numba=False)
        # Auto-select
        result_auto = merge_intervals(overlapping_intervals, use_numba=None)
        
        assert np.array_equal(result_numba, result_numpy)
        assert np.array_equal(result_numpy, result_auto)


class TestIntersectIntervals(TestFixtures):
    """Test interval intersection functionality."""
    
    def test_basic_intersections(self, intersecting_sets):
        """Test basic interval intersections."""
        set1, set2 = intersecting_sets
        result = intersect_intervals(set1, set2)
        
        expected = np.array([
            [30, 50],   # [10,50] ∩ [30,70]
            [120, 150], # [100,150] ∩ [120,180]
            [250, 300]  # [200,300] ∩ [250,350]
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_no_intersections(self):
        """Test intervals with no intersections."""
        set1 = np.array([[10, 20], [100, 110]], dtype=np.int32)
        set2 = np.array([[30, 40], [200, 210]], dtype=np.int32)
        
        result = intersect_intervals(set1, set2)
        
        assert result.shape == (0, 2)
        assert result.dtype == np.int32
    
    def test_complete_overlap(self):
        """Test intervals with complete overlap."""
        set1 = np.array([[10, 100]], dtype=np.int32)
        set2 = np.array([[20, 30], [40, 60]], dtype=np.int32)
        
        result = intersect_intervals(set1, set2)
        
        expected = np.array([
            [20, 30],
            [40, 60]
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_partial_overlaps(self):
        """Test various partial overlap scenarios."""
        set1 = np.array([[10, 50], [100, 200]], dtype=np.int32)
        set2 = np.array([[30, 80], [150, 250]], dtype=np.int32)
        
        result = intersect_intervals(set1, set2)
        
        expected = np.array([
            [30, 50],   # Partial overlap
            [150, 200]  # Partial overlap
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_intersect_empty_arrays(self):
        """Test intersection with empty arrays."""
        intervals = np.array([[100, 200]], dtype=np.int32)
        empty = np.array([], dtype=np.int32).reshape(0, 2)
        
        # Empty second set
        result = intersect_intervals(intervals, empty)
        assert result.shape == (0, 2)
        
        # Empty first set
        result = intersect_intervals(empty, intervals)
        assert result.shape == (0, 2)
        
        # Both empty
        result = intersect_intervals(empty, empty)
        assert result.shape == (0, 2)
    
    def test_intersect_numba_vs_numpy(self, intersecting_sets):
        """Test that numba and numpy implementations give same results."""
        set1, set2 = intersecting_sets
        
        result_numba = intersect_intervals(set1, set2, use_numba=True)
        result_numpy = intersect_intervals(set1, set2, use_numba=False)
        
        # Sort results for comparison (order might differ)
        result_numba_sorted = result_numba[np.lexsort((result_numba[:, 1], result_numba[:, 0]))]
        result_numpy_sorted = result_numpy[np.lexsort((result_numpy[:, 1], result_numpy[:, 0]))]
        
        assert np.array_equal(result_numba_sorted, result_numpy_sorted)
    
    def test_intersect_identical_sets(self):
        """Test intersection of identical interval sets."""
        intervals = np.array([[10, 20], [30, 40], [50, 60]], dtype=np.int32)
        result = intersect_intervals(intervals, intervals)
        
        # Should return the original intervals
        assert np.array_equal(result, intervals)


class TestSubtractIntervals(TestFixtures):
    """Test interval subtraction functionality."""
    
    def test_basic_subtraction(self):
        """Test basic interval subtraction."""
        base = np.array([[10, 100]], dtype=np.int32)
        subtract = np.array([[30, 70]], dtype=np.int32)
        
        result = subtract_intervals(base, subtract)
        
        expected = np.array([
            [10, 30],   # Left part
            [70, 100]   # Right part
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_subtraction_no_overlap(self):
        """Test subtraction with no overlapping intervals."""
        base = np.array([[10, 20], [100, 110]], dtype=np.int32)
        subtract = np.array([[30, 40], [200, 210]], dtype=np.int32)
        
        result = subtract_intervals(base, subtract)
        
        # Should return original intervals unchanged
        assert np.array_equal(result, base)
    
    def test_complete_subtraction(self):
        """Test complete removal of intervals."""
        base = np.array([[10, 50], [100, 150]], dtype=np.int32)
        subtract = np.array([[5, 60], [90, 160]], dtype=np.int32)  # Completely covers base
        
        result = subtract_intervals(base, subtract)
        
        # Should return empty result
        assert result.shape == (0, 2)
    
    def test_partial_subtraction(self):
        """Test partial subtraction scenarios."""
        base = np.array([
            [10, 100],
            [200, 300],
            [400, 500]
        ], dtype=np.int32)
        
        subtract = np.array([
            [30, 70],    # Splits first interval
            [250, 350],  # Partial overlap with second
            [600, 700]   # No overlap with any
        ], dtype=np.int32)
        
        result = subtract_intervals(base, subtract)
        
        expected = np.array([
            [10, 30],    # Left part of first
            [70, 100],   # Right part of first
            [200, 250],  # Left part of second
            [400, 500]   # Third unchanged
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_multiple_subtractions_single_interval(self):
        """Test multiple subtractions from a single interval."""
        base = np.array([[10, 100]], dtype=np.int32)
        subtract = np.array([
            [20, 30],
            [40, 50],
            [70, 80]
        ], dtype=np.int32)
        
        result = subtract_intervals(base, subtract)
        
        expected = np.array([
            [10, 20],
            [30, 40],
            [50, 70],
            [80, 100]
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_subtraction_edge_cases(self):
        """Test edge cases in subtraction."""
        base = np.array([[10, 50]], dtype=np.int32)
        
        # Subtract from left edge
        subtract_left = np.array([[10, 20]], dtype=np.int32)
        result = subtract_intervals(base, subtract_left)
        expected = np.array([[20, 50]], dtype=np.int32)
        assert np.array_equal(result, expected)
        
        # Subtract from right edge
        subtract_right = np.array([[40, 50]], dtype=np.int32)
        result = subtract_intervals(base, subtract_right)
        expected = np.array([[10, 40]], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_subtraction_empty_arrays(self):
        """Test subtraction with empty arrays."""
        intervals = np.array([[100, 200]], dtype=np.int32)
        empty = np.array([], dtype=np.int32).reshape(0, 2)
        
        # Empty subtract array - should return original
        result = subtract_intervals(intervals, empty)
        assert np.array_equal(result, intervals)
        
        # Empty base array - should return empty
        result = subtract_intervals(empty, intervals)
        assert result.shape == (0, 2)
    
    def test_subtraction_numba_vs_numpy(self):
        """Test that numba and numpy implementations give same results."""
        base = np.array([[10, 100], [200, 300]], dtype=np.int32)
        subtract = np.array([[30, 70], [250, 350]], dtype=np.int32)
        
        result_numba = subtract_intervals(base, subtract, use_numba=True)
        result_numpy = subtract_intervals(base, subtract, use_numba=False)
        
        # Sort results for comparison
        result_numba_sorted = result_numba[np.lexsort((result_numba[:, 1], result_numba[:, 0]))]
        result_numpy_sorted = result_numpy[np.lexsort((result_numpy[:, 1], result_numpy[:, 0]))]
        
        assert np.array_equal(result_numba_sorted, result_numpy_sorted)


class TestIntervalsUnion(TestFixtures):
    """Test interval union functionality."""
    
    def test_basic_union(self):
        """Test basic union of multiple interval sets."""
        set1 = np.array([[10, 30], [100, 150]], dtype=np.int32)
        set2 = np.array([[25, 50], [200, 250]], dtype=np.int32)
        set3 = np.array([[40, 80], [140, 180]], dtype=np.int32)
        
        result = intervals_union([set1, set2, set3])
        
        expected = np.array([
            [10, 80],    # Merged [10,30], [25,50], [40,80]
            [100, 180],  # Merged [100,150], [140,180]
            [200, 250]   # Standalone
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_union_single_set(self):
        """Test union with single interval set."""
        intervals = np.array([[10, 30], [50, 80]], dtype=np.int32)
        result = intervals_union([intervals])
        
        assert np.array_equal(result, intervals)
    
    def test_union_empty_sets(self):
        """Test union with empty sets."""
        set1 = np.array([[10, 20]], dtype=np.int32)
        empty = np.array([], dtype=np.int32).reshape(0, 2)
        
        # Mix of empty and non-empty
        result = intervals_union([empty, set1, empty])
        assert np.array_equal(result, set1)
        
        # All empty
        result = intervals_union([empty, empty])
        assert result.shape == (0, 2)
        
        # Empty list
        result = intervals_union([])
        assert result.shape == (0, 2)
    
    def test_union_overlapping_sets(self):
        """Test union of heavily overlapping sets."""
        set1 = np.array([[10, 50]], dtype=np.int32)
        set2 = np.array([[30, 70]], dtype=np.int32)
        set3 = np.array([[60, 100]], dtype=np.int32)
        
        result = intervals_union([set1, set2, set3])
        
        expected = np.array([[10, 100]], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_union_many_sets(self):
        """Test union of many small sets."""
        # Create many small non-overlapping intervals
        sets = [
            np.array([[i*10, i*10 + 5]], dtype=np.int32) 
            for i in range(10)
        ]
        
        result = intervals_union(sets)
        
        # Should have 10 separate intervals
        assert len(result) == 10
        assert result[0][0] == 0 and result[0][1] == 5
        assert result[-1][0] == 90 and result[-1][1] == 95


class TestValidationAndErrorHandling(TestFixtures):
    """Test input validation and error handling."""
    
    def test_invalid_array_shapes(self):
        """Test error handling for invalid array shapes."""
        invalid_shape = np.array([[100, 200, 300]], dtype=np.int32)  # Wrong shape
        valid_shape = np.array([[100, 200]], dtype=np.int32)
        
        with pytest.raises(ValueError, match="intervals must have shape"):
            merge_intervals(invalid_shape)
        
        with pytest.raises(ValueError, match="intervals must have shape"):
            intersect_intervals(invalid_shape, valid_shape)
        
        with pytest.raises(ValueError, match="intervals must have shape"):
            subtract_intervals(valid_shape, invalid_shape)
    
    def test_data_type_handling(self):
        """Test handling of different data types."""
        # Float input should be converted to int32
        float_intervals = np.array([[10.5, 20.7], [30.1, 40.9]], dtype=np.float64)
        
        result = merge_intervals(float_intervals)
        assert result.dtype == np.int32
        assert np.array_equal(result, np.array([[10, 20], [30, 40]], dtype=np.int32))
    
    def test_large_datasets(self):
        """Test performance with larger datasets."""
        # Create large dataset
        n = 10000
        intervals = np.random.randint(0, 1000000, size=(n, 2))
        intervals = np.sort(intervals, axis=1)  # Ensure start < end
        
        # Test that operations complete without error
        merged = merge_intervals(intervals)
        assert merged.dtype == np.int32
        assert len(merged) <= n  # Should be merged down
        
        # Test intersection of large sets
        subset1 = intervals[:n//2]
        subset2 = intervals[n//2:]
        intersected = intersect_intervals(subset1, subset2)
        assert intersected.dtype == np.int32


class TestPerformanceBenchmarks(TestFixtures):
    """Performance comparison tests."""
    
    def test_merge_performance_comparison(self):
        """Compare numba vs numpy merge performance."""
        # Create moderately large dataset
        n = 5000
        intervals = np.random.randint(0, 100000, size=(n, 2))
        intervals = np.sort(intervals, axis=1)
        
        # Both implementations should work
        result_numba = _merge_intervals_numba(intervals)
        result_numpy = _merge_intervals_numpy(intervals)
        
        # Results should be equivalent (after sorting)
        result_numba_sorted = result_numba[np.lexsort((result_numba[:, 1], result_numba[:, 0]))]
        result_numpy_sorted = result_numpy[np.lexsort((result_numpy[:, 1], result_numpy[:, 0]))]
        
        assert np.array_equal(result_numba_sorted, result_numpy_sorted)
    
    def test_intersect_performance_comparison(self):
        """Compare numba vs numpy intersect performance."""
        # Create test datasets
        n1, n2 = 1000, 800
        set1 = np.random.randint(0, 50000, size=(n1, 2))
        set1 = np.sort(set1, axis=1)
        set2 = np.random.randint(0, 50000, size=(n2, 2))
        set2 = np.sort(set2, axis=1)
        
        # Both implementations should work
        result_numba = intersect_intervals(set1, set2, use_numba=True)
        result_numpy = intersect_intervals(set1, set2, use_numba=False)
        
        # Results should be equivalent (after sorting)
        if len(result_numba) > 0 and len(result_numpy) > 0:
            result_numba_sorted = result_numba[np.lexsort((result_numba[:, 1], result_numba[:, 0]))]
            result_numpy_sorted = result_numpy[np.lexsort((result_numpy[:, 1], result_numpy[:, 0]))]
            assert np.array_equal(result_numba_sorted, result_numpy_sorted)


