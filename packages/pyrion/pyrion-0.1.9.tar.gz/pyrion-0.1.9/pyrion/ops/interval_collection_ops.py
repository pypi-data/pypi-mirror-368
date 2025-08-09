"""Bulk operations for GenomicIntervalsCollection using vectorized numpy operations."""

import numpy as np
from typing import List, Union, Callable
from numba import njit

from ..core.intervals import GenomicInterval, GenomicIntervalsCollection


@njit
def _merge_close_intervals_numba(intervals: np.ndarray, max_gap: int) -> np.ndarray:
    if len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    merged = np.empty((len(intervals), 2), dtype=np.int32)
    merged_idx = 0
    current_start, current_end = intervals[0, 0], intervals[0, 1]
    
    for i in range(1, len(intervals)):
        start, end = intervals[i, 0], intervals[i, 1]
        
        if start <= current_end + max_gap:
            # Close enough to merge
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


@njit
def _find_gap_splits_numba(intervals: np.ndarray, min_gap: int) -> np.ndarray:
    if len(intervals) <= 1:
        return np.array([len(intervals)], dtype=np.int32)
    
    split_points = np.empty(len(intervals), dtype=np.int32)
    split_count = 0
    
    for i in range(len(intervals) - 1):
        current_end = intervals[i, 1]
        next_start = intervals[i + 1, 0]
        
        if next_start - current_end >= min_gap:
            split_points[split_count] = i + 1
            split_count += 1
    
    # Always include the end
    split_points[split_count] = len(intervals)
    split_count += 1
    
    return split_points[:split_count]


@njit
def _intersect_intervals_with_interval_numba(intervals: np.ndarray, 
                                           target_start: int, target_end: int) -> np.ndarray:
    intersections = np.empty((len(intervals), 2), dtype=np.int32)
    intersection_count = 0
    
    for i in range(len(intervals)):
        start, end = intervals[i, 0], intervals[i, 1]
        
        if end > target_start and start < target_end:
            intersect_start = max(start, target_start)
            intersect_end = min(end, target_end)
            
            intersections[intersection_count, 0] = intersect_start
            intersections[intersection_count, 1] = intersect_end
            intersection_count += 1
    
    return intersections[:intersection_count]


def merge_close_intervals(collection: GenomicIntervalsCollection, max_gap: int = 0) -> GenomicIntervalsCollection:
    if collection.is_empty():
        return collection
    
    merged_array = _merge_close_intervals_numba(collection.array, max_gap)
    
    return GenomicIntervalsCollection(
        chrom=collection.chrom,
        strand=collection.strand,
        array=merged_array,
        ids=None
    )


def group_intervals_by_proximity(collection: GenomicIntervalsCollection, 
                                max_gap: int) -> List[GenomicIntervalsCollection]:
    if collection.is_empty():
        return []
    
    split_points = _find_gap_splits_numba(collection.array, max_gap)
    
    groups = []
    start_idx = 0
    
    for end_idx in split_points:
        if end_idx > start_idx:
            group_array = collection.array[start_idx:end_idx]
            group_ids = collection.ids[start_idx:end_idx] if collection.ids is not None else None
            
            groups.append(GenomicIntervalsCollection(
                chrom=collection.chrom,
                strand=collection.strand,
                array=group_array,
                ids=group_ids
            ))
            
        start_idx = end_idx
    
    return groups


def split_intervals_on_gaps(collection: GenomicIntervalsCollection, 
                           min_gap: int) -> List[GenomicIntervalsCollection]:
    return group_intervals_by_proximity(collection, min_gap)


def intersect_collections(collection: GenomicIntervalsCollection, 
                         other: Union[GenomicIntervalsCollection, GenomicInterval]) -> GenomicIntervalsCollection:
    if collection.is_empty():
        return collection
    
    if isinstance(other, GenomicInterval):
        if collection.chrom != other.chrom:
            return GenomicIntervalsCollection._empty_collection()
        
        intersections = _intersect_intervals_with_interval_numba(
            collection.array, other.start, other.end
        )
        
        if len(intersections) > 0:
            sort_indices = np.argsort(intersections[:, 0])
            intersections = intersections[sort_indices]
        
        return GenomicIntervalsCollection(
            chrom=collection.chrom,
            strand=collection.strand,
            array=intersections,
            ids=None
        )
    
    elif isinstance(other, GenomicIntervalsCollection):
        if collection.chrom != other.chrom or other.is_empty():
            return GenomicIntervalsCollection._empty_collection()
        
        from .interval_ops import intersect_intervals
        intersections = intersect_intervals(collection.array, other.array)
        
        if len(intersections) > 0:
            sort_indices = np.argsort(intersections[:, 0])
            intersections = intersections[sort_indices]
        
        return GenomicIntervalsCollection(
            chrom=collection.chrom,
            strand=collection.strand,
            array=intersections,
            ids=None
        )
    
    else:
        raise ValueError("Other must be GenomicInterval or GenomicIntervalsCollection")


def filter_collection(collection: GenomicIntervalsCollection, 
                     predicate: Callable[[GenomicInterval], bool]) -> GenomicIntervalsCollection:
    if collection.is_empty():
        return collection
    
    intervals = collection.to_intervals_list()
    filtered_intervals = [iv for iv in intervals if predicate(iv)]
    
    if not filtered_intervals:
        return GenomicIntervalsCollection._empty_collection()
    
    return GenomicIntervalsCollection.from_intervals(filtered_intervals)


def create_collections_from_mixed_intervals(intervals: List[GenomicInterval], 
                                          consider_strand: bool = False) -> List[GenomicIntervalsCollection]:
    if not intervals:
        return []
    groups = {}
    
    for interval in intervals:
        if consider_strand:
            key = (interval.chrom, interval.strand)
        else:
            key = interval.chrom
        
        if key not in groups:
            groups[key] = []
        groups[key].append(interval)
    
    collections = []
    for group_intervals in groups.values():
        if consider_strand:
            collections.append(GenomicIntervalsCollection.from_intervals(group_intervals))
        else:
            strand_groups = {}
            for interval in group_intervals:
                strand = interval.strand
                if strand not in strand_groups:
                    strand_groups[strand] = []
                strand_groups[strand].append(interval)
            
            for strand_intervals in strand_groups.values():
                collections.append(GenomicIntervalsCollection.from_intervals(strand_intervals))
    
    return collections
