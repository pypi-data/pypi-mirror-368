"""Additional low-level interval operations for merge, intersection, etc."""

import numpy as np
from typing import List
from numba import njit


@njit
def _merge_intervals_numba(intervals: np.ndarray) -> np.ndarray:
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    sorted_indices = np.argsort(intervals[:, 0])
    sorted_intervals = intervals[sorted_indices]
    merged = np.empty((len(intervals), 2), dtype=np.int32)
    merged_idx = 0
    current_start, current_end = sorted_intervals[0, 0], sorted_intervals[0, 1]
    
    for i in range(1, len(sorted_intervals)):
        start, end = sorted_intervals[i, 0], sorted_intervals[i, 1]
        
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            merged[merged_idx, 0] = current_start
            merged[merged_idx, 1] = current_end
            merged_idx += 1
            current_start = start
            current_end = end
    
    merged[merged_idx, 0] = current_start
    merged[merged_idx, 1] = current_end
    merged_idx += 1
    
    return merged[:merged_idx]


def merge_intervals(intervals: np.ndarray, use_numba: bool = None) -> np.ndarray:
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    intervals = np.asarray(intervals, dtype=np.int32)
    if intervals.shape[1] != 2:
        raise ValueError("intervals must have shape (N, 2)")
    
    if len(intervals) == 1:
        return intervals.copy()
    
    if use_numba is None:
        use_numba = len(intervals) > 100000
    
    if use_numba:
        return _merge_intervals_numba(intervals)
    else:
        return _merge_intervals_numpy(intervals)


def _merge_intervals_numpy(intervals: np.ndarray) -> np.ndarray:
    # Sort by start coordinate
    sorted_indices = np.argsort(intervals[:, 0])
    sorted_intervals = intervals[sorted_indices]
    starts = sorted_intervals[:, 0]
    ends = sorted_intervals[:, 1]
    cummax_ends = np.maximum.accumulate(ends)
    gaps = starts[1:] > cummax_ends[:-1]
    
    group_starts = np.concatenate(([True], gaps))
    group_start_indices = np.flatnonzero(group_starts)
    merged_starts = np.minimum.reduceat(starts, group_start_indices)
    merged_ends = np.maximum.reduceat(ends, group_start_indices)

    return np.column_stack((merged_starts, merged_ends))


@njit
def _intersect_intervals_numba(intervals1: np.ndarray, intervals2: np.ndarray) -> np.ndarray:
    intersections = np.empty((len(intervals1) * len(intervals2), 2), dtype=np.int32)
    intersection_count = 0
    
    for i in range(len(intervals1)):
        start1, end1 = intervals1[i, 0], intervals1[i, 1]
        
        for j in range(len(intervals2)):
            start2, end2 = intervals2[j, 0], intervals2[j, 1]
            
            intersect_start = max(start1, start2)
            intersect_end = min(end1, end2)
            
            if intersect_start < intersect_end:
                intersections[intersection_count, 0] = intersect_start
                intersections[intersection_count, 1] = intersect_end
                intersection_count += 1
    
    return intersections[:intersection_count]


def intersect_intervals(intervals1: np.ndarray, intervals2: np.ndarray, 
                       use_numba: bool = True) -> np.ndarray:
    if len(intervals1) == 0 or len(intervals2) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    intervals1 = np.asarray(intervals1, dtype=np.int32)
    intervals2 = np.asarray(intervals2, dtype=np.int32)
    
    if intervals1.shape[1] != 2 or intervals2.shape[1] != 2:
        raise ValueError("intervals must have shape (N, 2)")
    
    if use_numba:
        return _intersect_intervals_numba(intervals1, intervals2)
    else:
        intersections = []
        
        for interval1 in intervals1:
            start1, end1 = interval1[0], interval1[1]
            starts2 = intervals2[:, 0]
            ends2 = intervals2[:, 1]
            intersect_starts = np.maximum(start1, starts2)
            intersect_ends = np.minimum(end1, ends2)
            valid = intersect_starts < intersect_ends
            
            if np.any(valid):
                valid_intersections = np.stack([intersect_starts[valid], intersect_ends[valid]], axis=1)
                intersections.append(valid_intersections)
        
        if intersections:
            return np.vstack(intersections)
        else:
            return np.empty((0, 2), dtype=np.int32)


@njit
def _subtract_intervals_numba(intervals1: np.ndarray, intervals2: np.ndarray) -> np.ndarray:
    if len(intervals1) == 0:
        return np.empty((0, 2), dtype=np.int32)
    if len(intervals2) == 0:
        return intervals1.copy()
    
    sorted_indices = np.argsort(intervals2[:, 0])
    sorted_intervals2 = intervals2[sorted_indices]
    
    result = np.empty((len(intervals1) * (len(intervals2) + 1), 2), dtype=np.int32)
    result_count = 0
    
    for i in range(len(intervals1)):
        start1, end1 = intervals1[i, 0], intervals1[i, 1]
        remaining_parts = np.array([[start1, end1]], dtype=np.int32)
        
        for j in range(len(sorted_intervals2)):
            start2, end2 = sorted_intervals2[j, 0], sorted_intervals2[j, 1]
            
            new_remaining = np.empty((len(remaining_parts) * 2, 2), dtype=np.int32)
            new_count = 0
            
            for k in range(len(remaining_parts)):
                part_start, part_end = remaining_parts[k, 0], remaining_parts[k, 1]
                
                if part_end <= start2 or part_start >= end2:
                    new_remaining[new_count, 0] = part_start
                    new_remaining[new_count, 1] = part_end
                    new_count += 1
                else:
                    if part_start < start2:
                        new_remaining[new_count, 0] = part_start
                        new_remaining[new_count, 1] = start2
                        new_count += 1
                    
                    if part_end > end2:
                        new_remaining[new_count, 0] = end2
                        new_remaining[new_count, 1] = part_end
                        new_count += 1
            
            remaining_parts = new_remaining[:new_count]
        
        for k in range(len(remaining_parts)):
            result[result_count, 0] = remaining_parts[k, 0]
            result[result_count, 1] = remaining_parts[k, 1]
            result_count += 1
    
    return result[:result_count]


def subtract_intervals(intervals1: np.ndarray, intervals2: np.ndarray,
                      use_numba: bool = True) -> np.ndarray:
    if len(intervals1) == 0:
        return np.empty((0, 2), dtype=np.int32)
    if len(intervals2) == 0:
        return np.asarray(intervals1, dtype=np.int32).copy()
    
    intervals1 = np.asarray(intervals1, dtype=np.int32)
    intervals2 = np.asarray(intervals2, dtype=np.int32)
    
    if intervals1.shape[1] != 2 or intervals2.shape[1] != 2:
        raise ValueError("intervals must have shape (N, 2)")
    
    if use_numba:
        return _subtract_intervals_numba(intervals1, intervals2)
    else:
        result_list = []
        
        for interval1 in intervals1:
            remaining_parts = [interval1]
            
            for interval2 in intervals2:
                new_remaining = []
                
                for part in remaining_parts:
                    part_start, part_end = part[0], part[1]
                    sub_start, sub_end = interval2[0], interval2[1]
                    
                    if part_end <= sub_start or part_start >= sub_end:
                        new_remaining.append(part)
                    else:
                        if part_start < sub_start:
                            new_remaining.append([part_start, sub_start])
                        if part_end > sub_end:
                            new_remaining.append([sub_end, part_end])
                
                remaining_parts = new_remaining
            
            result_list.extend(remaining_parts)
        
        if result_list:
            return np.array(result_list, dtype=np.int32)
        else:
            return np.empty((0, 2), dtype=np.int32)


def intervals_union(intervals_list: List[np.ndarray], use_numba: bool = True) -> np.ndarray:
    if not intervals_list:
        return np.empty((0, 2), dtype=np.int32)
    
    non_empty = [arr for arr in intervals_list if len(arr) > 0]
    if not non_empty:
        return np.empty((0, 2), dtype=np.int32)
    
    all_intervals = np.vstack(non_empty)
    return merge_intervals(all_intervals, use_numba=use_numba)