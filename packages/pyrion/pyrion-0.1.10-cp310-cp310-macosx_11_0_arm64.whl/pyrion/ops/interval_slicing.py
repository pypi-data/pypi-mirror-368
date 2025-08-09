"""Low-level interval slicing and manipulation operations."""

import numpy as np
from numba import njit


@njit
def _slice_intervals_numba(intervals: np.ndarray, slice_start: int, slice_end: int) -> np.ndarray:
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    result = np.empty((len(intervals), 2), dtype=np.int32)
    result_idx = 0
    
    for i in range(len(intervals)):
        start, end = intervals[i, 0], intervals[i, 1]
        if end > slice_start and start < slice_end:
            result[result_idx, 0] = max(start, slice_start)
            result[result_idx, 1] = min(end, slice_end)
            result_idx += 1
    
    return result[:result_idx]


def slice_intervals(intervals: np.ndarray, slice_start: int, slice_end: int, 
                   use_numba: bool = None) -> np.ndarray:
    """Slice intervals to get only parts that intersect with [slice_start, slice_end).

    Example:
        blocks = [[10, 30], [100, 150], [200, 210], [400, 600]]
        slice_intervals(blocks, 40, 450) -> [[100, 150], [200, 210], [400, 450]]
    """
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
        
    if slice_start >= slice_end:
        raise ValueError(f"Invalid slice: start {slice_start} >= end {slice_end}")
    
    intervals = np.asarray(intervals, dtype=np.int32)
    if intervals.shape[1] != 2:
        raise ValueError("intervals must have shape (N, 2)")
    
    if use_numba is None:
        if len(intervals) > 50000:
            use_numba = True
        else:
            use_numba = False
    
    if use_numba:
        return _slice_intervals_numba(intervals, slice_start, slice_end)
    else:
        starts = intervals[:, 0]
        ends = intervals[:, 1]
        intersects = (ends > slice_start) & (starts < slice_end)
        
        if not intersects.any():
            return np.empty((0, 2), dtype=np.int32)

        intersect_starts = np.maximum(starts[intersects], slice_start)
        intersect_ends = np.minimum(ends[intersects], slice_end)
        
        return np.column_stack((intersect_starts, intersect_ends))


@njit
def _remove_intervals_numba(intervals: np.ndarray, remove_start: int, remove_end: int) -> np.ndarray:
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    result = np.empty((len(intervals) * 2, 2), dtype=np.int32)
    result_idx = 0
    
    for i in range(len(intervals)):
        start, end = intervals[i, 0], intervals[i, 1]
        
        if end <= remove_start or start >= remove_end:
            result[result_idx, 0] = start
            result[result_idx, 1] = end
            result_idx += 1
        elif start < remove_start and end > remove_end:
            result[result_idx, 0] = start
            result[result_idx, 1] = remove_start
            result_idx += 1
            result[result_idx, 0] = remove_end
            result[result_idx, 1] = end
            result_idx += 1
        elif start < remove_start:
            result[result_idx, 0] = start
            result[result_idx, 1] = remove_start
            result_idx += 1
        elif end > remove_end:
            result[result_idx, 0] = remove_end
            result[result_idx, 1] = end
            result_idx += 1

    return result[:result_idx]


def remove_intervals(intervals: np.ndarray, remove_start: int, remove_end: int,
                    use_numba: bool = None) -> np.ndarray:
    """Remove a region from intervals, potentially splitting them.
        
    Example:
        blocks = [[10, 100], [150, 300]]
        remove_intervals(blocks, 50, 200) -> [[10, 50], [200, 300]]
    """
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
        
    if remove_start >= remove_end:
        raise ValueError(f"Invalid remove region: start {remove_start} >= end {remove_end}")
    
    intervals = np.asarray(intervals, dtype=np.int32)
    if intervals.shape[1] != 2:
        raise ValueError("intervals must have shape (N, 2)")
    
    # Auto-select algorithm
    if use_numba is None:
        use_numba = len(intervals) > 20000  # Different approaches for different dataset sizes
    
    if use_numba:
        return _remove_intervals_numba(intervals, remove_start, remove_end)
    else:
        starts = intervals[:, 0]
        ends = intervals[:, 1]
        
        no_intersect = (ends <= remove_start) | (starts >= remove_end)
        need_process = ~no_intersect
        
        result_list = []
        
        if np.any(no_intersect):
            result_list.append(intervals[no_intersect])
        
        if np.any(need_process):
            proc_starts = starts[need_process]
            proc_ends = ends[need_process]
            
            left_mask = proc_starts < remove_start
            if np.any(left_mask):
                left_starts = proc_starts[left_mask]
                left_ends = np.minimum(proc_ends[left_mask], remove_start)
                valid_left = left_starts < left_ends
                if np.any(valid_left):
                    result_list.append(np.stack([left_starts[valid_left], left_ends[valid_left]], axis=1))
            
            right_mask = proc_ends > remove_end
            if np.any(right_mask):
                right_starts = np.maximum(proc_starts[right_mask], remove_end)
                right_ends = proc_ends[right_mask]
                valid_right = right_starts < right_ends
                if np.any(valid_right):
                    result_list.append(np.stack([right_starts[valid_right], right_ends[valid_right]], axis=1))
        
        if result_list:
            return np.vstack(result_list)
        else:
            return np.empty((0, 2), dtype=np.int32)


@njit
def _invert_intervals_numba(intervals: np.ndarray, span_start: int, span_end: int) -> np.ndarray:
    if len(intervals) == 0:
        return np.array([[span_start, span_end]], dtype=np.int32)
    
    sorted_indices = np.argsort(intervals[:, 0])
    sorted_intervals = intervals[sorted_indices]
    gaps = np.empty((len(intervals) + 1, 2), dtype=np.int32)
    gap_count = 0
    
    if sorted_intervals[0, 0] > span_start:
        gaps[gap_count, 0] = span_start
        gaps[gap_count, 1] = sorted_intervals[0, 0]
        gap_count += 1
    
    for i in range(len(sorted_intervals) - 1):
        current_end = sorted_intervals[i, 1]
        next_start = sorted_intervals[i + 1, 0]
        if current_end < next_start:
            gaps[gap_count, 0] = current_end
            gaps[gap_count, 1] = next_start
            gap_count += 1
    
    if sorted_intervals[-1, 1] < span_end:
        gaps[gap_count, 0] = sorted_intervals[-1, 1]
        gaps[gap_count, 1] = span_end
        gap_count += 1
    
    return gaps[:gap_count]


def invert_intervals(intervals: np.ndarray, span_start: int, span_end: int,
                    use_numba: bool = None) -> np.ndarray:
    """Get the inverse (gaps) of intervals within a given span.
        
    Example:
        exons = [[100, 150], [200, 210], [400, 600]]
        invert_intervals(exons, 50, 700) -> [[50, 100], [150, 200], [210, 400], [600, 700]]
    """
    if len(intervals) == 0:
        return np.array([[span_start, span_end]], dtype=np.int32)
        
    if span_start >= span_end:
        raise ValueError(f"Invalid span: start {span_start} >= end {span_end}")
    
    intervals = np.asarray(intervals, dtype=np.int32)
    if intervals.shape[1] != 2:
        raise ValueError("intervals must have shape (N, 2)")
    
    if use_numba is None:
        use_numba = len(intervals) > 10000  # Different approaches for different dataset sizes
    
    if use_numba:
        return _invert_intervals_numba(intervals, span_start, span_end)
    else:
        # Sort intervals by start position
        sorted_indices = np.argsort(intervals[:, 0])
        sorted_intervals = intervals[sorted_indices]
        
        gaps = []
        
        if sorted_intervals[0, 0] > span_start:
            gaps.append([span_start, sorted_intervals[0, 0]])
        
        for i in range(len(sorted_intervals) - 1):
            current_end = sorted_intervals[i, 1]
            next_start = sorted_intervals[i + 1, 0]
            if current_end < next_start:
                gaps.append([current_end, next_start])
        
        if sorted_intervals[-1, 1] < span_end:
            gaps.append([sorted_intervals[-1, 1], span_end])
        
        return np.array(gaps, dtype=np.int32) if gaps else np.empty((0, 2), dtype=np.int32)
