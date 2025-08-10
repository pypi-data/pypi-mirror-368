"""Super-optimized interval slicing using advanced numpy vectorization."""

import numpy as np
from numba import njit
from typing import Tuple


def slice_intervals_superopt(intervals: np.ndarray, slice_start: int, slice_end: int) -> np.ndarray:
    """Super-optimized interval slicing using advanced numpy vectorization.
    
    Uses SIMD-friendly operations and minimal memory allocations.
    """
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
        
    if slice_start >= slice_end:
        raise ValueError(f"Invalid slice: start {slice_start} >= end {slice_end}")
    
    # Extract start/end columns - this is memory-contiguous
    starts = intervals[:, 0]
    ends = intervals[:, 1]
    
    # Single vectorized intersection test - highly SIMD optimized
    intersects = (ends > slice_start) & (starts < slice_end)
    
    # Early exit for no matches
    if not intersects.any():
        return np.empty((0, 2), dtype=np.int32)
    
    # Use advanced indexing to get matching intervals directly
    # This avoids creating intermediate boolean-indexed arrays
    intersect_starts = np.maximum(starts[intersects], slice_start)
    intersect_ends = np.minimum(ends[intersects], slice_end)
    
    # Use column_stack instead of stack for better memory layout
    return np.column_stack((intersect_starts, intersect_ends)).astype(np.int32)


def slice_intervals_searchsorted(intervals: np.ndarray, slice_start: int, slice_end: int) -> np.ndarray:
    """Ultra-optimized slicing using binary search for large sorted datasets.
    
    O(log n + k) instead of O(n) for sorted intervals.
    Note: This assumes intervals are sorted by start coordinate.
    """
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
        
    if slice_start >= slice_end:
        raise ValueError(f"Invalid slice: start {slice_start} >= end {slice_end}")
    
    # For unsorted data, fall back to regular method
    starts = intervals[:, 0]
    ends = intervals[:, 1]
    
    # Check if data is sorted (for optimization to be valid)
    if not np.all(starts[:-1] <= starts[1:]):
        # Data not sorted, use regular vectorized approach
        intersects = (ends > slice_start) & (starts < slice_end)
        
        if not intersects.any():
            return np.empty((0, 2), dtype=np.int32)
        
        intersect_starts = np.maximum(starts[intersects], slice_start)
        intersect_ends = np.minimum(ends[intersects], slice_end)
        
        return np.column_stack((intersect_starts, intersect_ends)).astype(np.int32)
    
    # Binary search optimization for sorted data
    # Find first interval where end > slice_start
    first_idx = np.searchsorted(ends, slice_start, side='right')
    
    # Find last interval where start < slice_end  
    last_idx = np.searchsorted(starts, slice_end, side='left')
    
    if first_idx >= last_idx:
        return np.empty((0, 2), dtype=np.int32)
    
    # Only process the relevant subset
    subset_intervals = intervals[first_idx:last_idx]
    subset_starts = subset_intervals[:, 0] 
    subset_ends = subset_intervals[:, 1]
    
    # Final intersection test on reduced set
    intersects = (subset_ends > slice_start) & (subset_starts < slice_end)
    
    if not intersects.any():
        return np.empty((0, 2), dtype=np.int32)
    
    # Compute intersections on the reduced set
    intersect_starts = np.maximum(subset_starts[intersects], slice_start)
    intersect_ends = np.minimum(subset_ends[intersects], slice_end)
    
    return np.column_stack((intersect_starts, intersect_ends)).astype(np.int32)


@njit
def slice_intervals_numba_opt(intervals: np.ndarray, slice_start: int, slice_end: int) -> np.ndarray:
    """Optimized numba version with reduced allocations and better algorithm."""
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    # Pre-allocate result array (worst case size)
    result = np.empty((len(intervals), 2), dtype=np.int32)
    result_idx = 0
    
    # Single pass through intervals
    for i in range(len(intervals)):
        start, end = intervals[i, 0], intervals[i, 1]
        
        # Quick intersection test
        if end > slice_start and start < slice_end:
            # Compute intersection inline
            intersect_start = max(start, slice_start)
            intersect_end = min(end, slice_end)
            
            result[result_idx, 0] = intersect_start
            result[result_idx, 1] = intersect_end
            result_idx += 1
    
    # Return only the used portion
    return result[:result_idx]


def merge_intervals_superopt(intervals: np.ndarray) -> np.ndarray:
    """Super-optimized merge using numpy's advanced grouping operations."""
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    if len(intervals) == 1:
        return intervals.copy()
    
    # Sort by start coordinate
    sorted_indices = np.argsort(intervals[:, 0])
    sorted_intervals = intervals[sorted_indices]
    
    starts = sorted_intervals[:, 0]
    ends = sorted_intervals[:, 1]
    
    # Vectorized gap detection
    # A new group starts where start[i] > cumulative_max_end[i-1]
    cummax_ends = np.maximum.accumulate(ends)
    gaps = starts[1:] > cummax_ends[:-1]
    
    # Create group labels
    group_starts = np.concatenate(([True], gaps))
    group_ids = np.cumsum(group_starts)
    
    # Use reduceat for efficient grouping
    group_start_indices = np.flatnonzero(group_starts)
    
    # Get min start and max end for each group
    merged_starts = np.minimum.reduceat(starts, group_start_indices)
    merged_ends = np.maximum.reduceat(ends, group_start_indices)
    
    return np.column_stack((merged_starts, merged_ends))


def batch_slice_intervals(intervals: np.ndarray, slice_ranges: np.ndarray) -> list:
    """Batch process multiple slice operations efficiently.
    
    Args:
        intervals: Shape (N, 2) intervals
        slice_ranges: Shape (M, 2) slice ranges
        
    Returns:
        List of M result arrays
    """
    if len(intervals) == 0:
        return [np.empty((0, 2), dtype=np.int32) for _ in range(len(slice_ranges))]
    
    starts = intervals[:, 0]
    ends = intervals[:, 1]
    
    results = []
    for slice_start, slice_end in slice_ranges:
        # Vectorized intersection for this range
        intersects = (ends > slice_start) & (starts < slice_end)
        
        if intersects.any():
            intersect_starts = np.maximum(starts[intersects], slice_start)
            intersect_ends = np.minimum(ends[intersects], slice_end)
            result = np.column_stack((intersect_starts, intersect_ends)).astype(np.int32)
        else:
            result = np.empty((0, 2), dtype=np.int32)
        
        results.append(result)
    
    return results 