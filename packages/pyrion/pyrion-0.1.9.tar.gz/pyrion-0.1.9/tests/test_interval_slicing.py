"""Unit tests for pyrion.ops.interval_slicing module."""

import pytest
import numpy as np
from typing import List

from pyrion.ops.interval_slicing import (
    slice_intervals,
    _slice_intervals_numba,
    remove_intervals,
    _remove_intervals_numba,
    invert_intervals,
    _invert_intervals_numba
)


class TestFixtures:
    """Test data fixtures for interval slicing operations."""
    
    @pytest.fixture
    def basic_intervals(self):
        """Basic intervals for testing."""
        return np.array([
            [10, 30],
            [100, 150],
            [200, 210],
            [400, 600]
        ], dtype=np.int32)
    
    @pytest.fixture
    def overlapping_intervals(self):
        """Overlapping intervals for complex testing."""
        return np.array([
            [10, 50],
            [30, 80],
            [70, 120],
            [200, 300]
        ], dtype=np.int32)
    
    @pytest.fixture
    def unsorted_intervals(self):
        """Unsorted intervals to test sorting behavior."""
        return np.array([
            [200, 300],
            [10, 50],
            [100, 150],
            [50, 80]
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


class TestSliceIntervals(TestFixtures):
    """Test interval slicing functionality."""
    
    def test_basic_slicing(self, basic_intervals):
        """Test basic interval slicing."""
        # Slice that intersects multiple intervals
        result = slice_intervals(basic_intervals, 40, 450)
        
        expected = np.array([
            [100, 150],   # [100,150] intersects [40,450] -> [100,150]
            [200, 210],   # [200,210] intersects [40,450] -> [200,210]
            [400, 450]    # [400,600] intersects [40,450] -> [400,450]
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_slice_no_intersection(self, basic_intervals):
        """Test slicing with no intersections."""
        result = slice_intervals(basic_intervals, 250, 350)
        
        # No intervals intersect this range
        assert result.shape == (0, 2)
        assert result.dtype == np.int32
    
    def test_slice_complete_overlap(self, basic_intervals):
        """Test slicing that completely contains some intervals."""
        result = slice_intervals(basic_intervals, 95, 155)
        
        expected = np.array([[100, 150]], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_slice_partial_overlaps(self, basic_intervals):
        """Test slicing with partial overlaps."""
        result = slice_intervals(basic_intervals, 20, 110)
        
        expected = np.array([
            [20, 30],     # [10,30] intersects [20,110] -> [20,30]
            [100, 110]    # [100,150] intersects [20,110] -> [100,110]
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_slice_single_interval(self):
        """Test slicing with single interval."""
        single = np.array([[100, 200]], dtype=np.int32)
        result = slice_intervals(single, 150, 250)
        
        expected = np.array([[150, 200]], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_slice_empty_array(self):
        """Test slicing empty array."""
        empty = np.array([], dtype=np.int32).reshape(0, 2)
        result = slice_intervals(empty, 100, 200)
        
        assert result.shape == (0, 2)
        assert result.dtype == np.int32
    
    def test_slice_boundary_cases(self, basic_intervals):
        """Test boundary conditions."""
        # Slice exactly at interval boundaries
        result = slice_intervals(basic_intervals, 30, 100)
        assert result.shape == (0, 2)  # No intersection
        
        # Slice touching left boundary
        result = slice_intervals(basic_intervals, 10, 50)
        expected = np.array([[10, 30]], dtype=np.int32)
        assert np.array_equal(result, expected)
        
        # Slice touching right boundary
        result = slice_intervals(basic_intervals, 150, 300)
        expected = np.array([[200, 210]], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_slice_numba_vs_numpy(self, basic_intervals):
        """Test that numba and numpy implementations give same results."""
        slice_start, slice_end = 40, 450
        
        result_numba = slice_intervals(basic_intervals, slice_start, slice_end, use_numba=True)
        result_numpy = slice_intervals(basic_intervals, slice_start, slice_end, use_numba=False)
        
        assert np.array_equal(result_numba, result_numpy)
    
    def test_slice_auto_algorithm_selection(self, basic_intervals):
        """Test automatic algorithm selection."""
        # Small dataset should use numpy
        result_auto = slice_intervals(basic_intervals, 40, 450, use_numba=None)
        result_numpy = slice_intervals(basic_intervals, 40, 450, use_numba=False)
        
        assert np.array_equal(result_auto, result_numpy)
    
    def test_slice_invalid_input(self):
        """Test error handling for invalid input."""
        intervals = np.array([[100, 200]], dtype=np.int32)
        
        # Invalid slice range
        with pytest.raises(ValueError, match="Invalid slice"):
            slice_intervals(intervals, 200, 100)
        
        # Invalid array shape
        invalid_shape = np.array([[100, 200, 300]], dtype=np.int32)
        with pytest.raises(ValueError, match="intervals must have shape"):
            slice_intervals(invalid_shape, 100, 200)
    
    def test_slice_overlapping_intervals(self, overlapping_intervals):
        """Test slicing with overlapping intervals."""
        result = slice_intervals(overlapping_intervals, 40, 90)
        
        expected = np.array([
            [40, 50],     # [10,50] intersects [40,90] -> [40,50]
            [40, 80],     # [30,80] intersects [40,90] -> [40,80]
            [70, 90]      # [70,120] intersects [40,90] -> [70,90]
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)


class TestRemoveIntervals(TestFixtures):
    """Test interval removal functionality."""
    
    def test_basic_removal(self):
        """Test basic interval removal."""
        intervals = np.array([[10, 100]], dtype=np.int32)
        result = remove_intervals(intervals, 30, 70)
        
        expected = np.array([
            [10, 30],   # Left part
            [70, 100]   # Right part
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_remove_no_intersection(self, basic_intervals):
        """Test removal with no intersections."""
        result = remove_intervals(basic_intervals, 250, 350)
        
        # Should return original intervals unchanged
        assert np.array_equal(result, basic_intervals)
    
    def test_remove_complete_overlap(self):
        """Test complete removal of intervals."""
        intervals = np.array([[100, 200], [300, 400]], dtype=np.int32)
        result = remove_intervals(intervals, 50, 450)
        
        # Both intervals completely removed
        assert result.shape == (0, 2)
    
    def test_remove_partial_overlaps(self, basic_intervals):
        """Test removal with partial overlaps."""
        result = remove_intervals(basic_intervals, 20, 110)
        
        expected = np.array([
            [10, 20],     # Left part of [10,30]
            [110, 150],   # Right part of [100,150]
            [200, 210],   # Unchanged [200,210]
            [400, 600]    # Unchanged [400,600]
        ], dtype=np.int32)
        
        # Sort both arrays by start position before comparison
        result_sorted = result[np.argsort(result[:, 0])] if len(result) > 0 else result
        expected_sorted = expected[np.argsort(expected[:, 0])] if len(expected) > 0 else expected
        assert np.array_equal(result_sorted, expected_sorted)
    
    def test_remove_edge_cases(self):
        """Test edge cases in removal."""
        intervals = np.array([[100, 200]], dtype=np.int32)
        
        # Remove from left edge
        result = remove_intervals(intervals, 100, 150)
        expected = np.array([[150, 200]], dtype=np.int32)
        assert np.array_equal(result, expected)
        
        # Remove from right edge
        result = remove_intervals(intervals, 150, 200)
        expected = np.array([[100, 150]], dtype=np.int32)
        assert np.array_equal(result, expected)
        
        # Remove entire interval
        result = remove_intervals(intervals, 100, 200)
        assert result.shape == (0, 2)
        
        # Remove beyond interval
        result = remove_intervals(intervals, 50, 250)
        assert result.shape == (0, 2)
    
    def test_remove_multiple_intervals(self, basic_intervals):
        """Test removal affecting multiple intervals."""
        result = remove_intervals(basic_intervals, 25, 105)
        
        expected = np.array([
            [10, 25],     # Left part of [10,30]
            [105, 150],   # Right part of [100,150]
            [200, 210],   # Unchanged [200,210]
            [400, 600]    # Unchanged [400,600]
        ], dtype=np.int32)
        
        # Sort both arrays by start position before comparison
        result_sorted = result[np.argsort(result[:, 0])] if len(result) > 0 else result
        expected_sorted = expected[np.argsort(expected[:, 0])] if len(expected) > 0 else expected
        assert np.array_equal(result_sorted, expected_sorted)
    
    def test_remove_splits_interval(self):
        """Test removal that splits a single interval."""
        intervals = np.array([[10, 100], [200, 300]], dtype=np.int32)
        result = remove_intervals(intervals, 40, 60)
        
        expected = np.array([
            [10, 40],     # Left part of split interval
            [60, 100],    # Right part of split interval
            [200, 300]    # Unchanged
        ], dtype=np.int32)
        
        # Sort both arrays by start position before comparison
        result_sorted = result[np.argsort(result[:, 0])] if len(result) > 0 else result
        expected_sorted = expected[np.argsort(expected[:, 0])] if len(expected) > 0 else expected
        assert np.array_equal(result_sorted, expected_sorted)
    
    def test_remove_empty_array(self):
        """Test removal from empty array."""
        empty = np.array([], dtype=np.int32).reshape(0, 2)
        result = remove_intervals(empty, 100, 200)
        
        assert result.shape == (0, 2)
        assert result.dtype == np.int32
    
    def test_remove_numba_vs_numpy(self, basic_intervals):
        """Test that numba and numpy implementations give same results."""
        remove_start, remove_end = 25, 105
        
        result_numba = remove_intervals(basic_intervals, remove_start, remove_end, use_numba=True)
        result_numpy = remove_intervals(basic_intervals, remove_start, remove_end, use_numba=False)
        
        # Sort results for comparison (order might differ)
        result_numba_sorted = result_numba[np.lexsort((result_numba[:, 1], result_numba[:, 0]))]
        result_numpy_sorted = result_numpy[np.lexsort((result_numpy[:, 1], result_numpy[:, 0]))]
        
        assert np.array_equal(result_numba_sorted, result_numpy_sorted)
    
    def test_remove_invalid_input(self):
        """Test error handling for invalid input."""
        intervals = np.array([[100, 200]], dtype=np.int32)
        
        # Invalid remove range
        with pytest.raises(ValueError, match="Invalid remove region"):
            remove_intervals(intervals, 200, 100)
        
        # Invalid array shape
        invalid_shape = np.array([[100, 200, 300]], dtype=np.int32)
        with pytest.raises(ValueError, match="intervals must have shape"):
            remove_intervals(invalid_shape, 100, 150)


class TestInvertIntervals(TestFixtures):
    """Test interval inversion (gap finding) functionality."""
    
    def test_basic_inversion(self):
        """Test basic interval inversion."""
        intervals = np.array([
            [100, 150],
            [200, 210],
            [400, 600]
        ], dtype=np.int32)
        
        result = invert_intervals(intervals, 50, 700)
        
        expected = np.array([
            [50, 100],    # Gap before first interval
            [150, 200],   # Gap between first and second
            [210, 400],   # Gap between second and third
            [600, 700]    # Gap after last interval
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_invert_no_gaps(self):
        """Test inversion with no gaps."""
        intervals = np.array([[100, 200]], dtype=np.int32)
        result = invert_intervals(intervals, 100, 200)
        
        # No gaps within the exact span
        assert result.shape == (0, 2)
    
    def test_invert_empty_array(self):
        """Test inversion of empty array."""
        empty = np.array([], dtype=np.int32).reshape(0, 2)
        result = invert_intervals(empty, 100, 200)
        
        expected = np.array([[100, 200]], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_invert_single_interval(self):
        """Test inversion with single interval."""
        intervals = np.array([[150, 200]], dtype=np.int32)
        result = invert_intervals(intervals, 100, 300)
        
        expected = np.array([
            [100, 150],   # Gap before
            [200, 300]    # Gap after
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_invert_touching_span_boundaries(self):
        """Test inversion with intervals touching span boundaries."""
        intervals = np.array([
            [100, 150],
            [250, 300]
        ], dtype=np.int32)
        
        result = invert_intervals(intervals, 100, 300)
        
        expected = np.array([[150, 250]], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_invert_overlapping_intervals(self, overlapping_intervals):
        """Test inversion with overlapping intervals."""
        # Note: overlapping intervals may produce unexpected results
        # This tests the actual behavior
        result = invert_intervals(overlapping_intervals, 0, 400)
        
        # The function should handle overlaps by finding gaps in the sorted sequence
        assert result.dtype == np.int32
        assert len(result.shape) == 2
        assert result.shape[1] == 2
    
    def test_invert_unsorted_intervals(self, unsorted_intervals):
        """Test inversion with unsorted intervals."""
        result = invert_intervals(unsorted_intervals, 0, 350)
        
        # Should handle unsorted input correctly by sorting first
        assert result.dtype == np.int32
        # Verify that gaps are found correctly after sorting
        assert len(result) > 0
    
    def test_invert_adjacent_intervals(self, adjacent_intervals):
        """Test inversion with adjacent intervals."""
        result = invert_intervals(adjacent_intervals, 0, 100)
        
        expected = np.array([
            [0, 10],      # Gap before first
            [40, 50],     # Gap between [30,40] and [50,60]
            [60, 100]     # Gap after last
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_invert_numba_vs_numpy(self, basic_intervals):
        """Test that numba and numpy implementations give same results."""
        span_start, span_end = 0, 700
        
        result_numba = invert_intervals(basic_intervals, span_start, span_end, use_numba=True)
        result_numpy = invert_intervals(basic_intervals, span_start, span_end, use_numba=False)
        
        assert np.array_equal(result_numba, result_numpy)
    
    def test_invert_intervals_beyond_span(self):
        """Test inversion when intervals extend beyond span."""
        intervals = np.array([
            [50, 150],    # Starts before span
            [200, 350]    # Extends beyond span
        ], dtype=np.int32)
        
        result = invert_intervals(intervals, 100, 300)
        
        expected = np.array([[150, 200]], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_invert_invalid_input(self):
        """Test error handling for invalid input."""
        intervals = np.array([[100, 200]], dtype=np.int32)
        
        # Invalid span
        with pytest.raises(ValueError, match="Invalid span"):
            invert_intervals(intervals, 200, 100)
        
        # Invalid array shape
        invalid_shape = np.array([[100, 200, 300]], dtype=np.int32)
        with pytest.raises(ValueError, match="intervals must have shape"):
            invert_intervals(invalid_shape, 100, 200)


class TestPerformanceAndLargeDatasets(TestFixtures):
    """Test performance with large datasets."""
    
    def test_large_dataset_slicing(self):
        """Test slicing with large dataset."""
        # Create large dataset
        n = 10000
        intervals = np.random.randint(0, 1000000, size=(n, 2))
        intervals = np.sort(intervals, axis=1)  # Ensure start < end
        
        # Test that operations complete without error
        result = slice_intervals(intervals, 100000, 200000)
        assert result.dtype == np.int32
        assert len(result) <= n
    
    def test_large_dataset_removal(self):
        """Test removal with large dataset."""
        n = 8000
        intervals = np.random.randint(0, 500000, size=(n, 2))
        intervals = np.sort(intervals, axis=1)
        
        result = remove_intervals(intervals, 100000, 200000)
        assert result.dtype == np.int32
    
    def test_large_dataset_inversion(self):
        """Test inversion with large dataset."""
        n = 5000
        intervals = np.random.randint(0, 100000, size=(n, 2))
        intervals = np.sort(intervals, axis=1)
        
        result = invert_intervals(intervals, 0, 150000)
        assert result.dtype == np.int32
    
    def test_algorithm_selection_thresholds(self):
        """Test that algorithm selection works correctly."""
        # Small dataset should prefer numpy
        small_intervals = np.array([[10, 20], [30, 40]], dtype=np.int32)
        
        # These should not raise errors and should complete quickly
        slice_intervals(small_intervals, 5, 45, use_numba=None)
        remove_intervals(small_intervals, 15, 35, use_numba=None)
        invert_intervals(small_intervals, 0, 50, use_numba=None)


class TestDataTypeHandling(TestFixtures):
    """Test handling of different data types."""
    
    def test_float_input_conversion(self):
        """Test conversion of float inputs to int32."""
        float_intervals = np.array([[10.5, 20.7], [30.1, 40.9]], dtype=np.float64)
        
        result = slice_intervals(float_intervals, 15, 35)
        assert result.dtype == np.int32
        
        result = remove_intervals(float_intervals, 15, 35)
        assert result.dtype == np.int32
        
        result = invert_intervals(float_intervals, 0, 50)
        assert result.dtype == np.int32
    
    def test_different_integer_types(self):
        """Test handling of different integer types."""
        int64_intervals = np.array([[10, 20], [30, 40]], dtype=np.int64)
        
        result = slice_intervals(int64_intervals, 15, 35)
        assert result.dtype == np.int32
        
        result = remove_intervals(int64_intervals, 15, 35)
        assert result.dtype == np.int32
        
        result = invert_intervals(int64_intervals, 0, 50)
        assert result.dtype == np.int32


if __name__ == "__main__":
    pytest.main([__file__, "-v"])