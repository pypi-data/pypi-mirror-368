"""Interval operations for pyrion."""

from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from numba import njit

from ..core.intervals import GenomicInterval
from ..core.strand import Strand


def find_intersections(arr1: np.ndarray, arr2: np.ndarray, ids1: Optional[List] = None, ids2: Optional[List] = None) -> Dict[Any, List]:
    """Find intersections between two arrays of intervals."""
    if arr1.size == 0 or arr2.size == 0:
        return {}

    if arr1.shape[1] != 2 or arr2.shape[1] != 2:
        raise ValueError("Arrays must have shape (N, 2)")
    
    # Validate IDs if provided
    if ids1 is not None and len(ids1) != len(arr1):
        raise ValueError("ids1 length must match arr1 length")
    if ids2 is not None and len(ids2) != len(arr2):
        raise ValueError("ids2 length must match arr2 length")

    sort_mask1 = np.argsort(arr1[:, 0])
    sort_mask2 = np.argsort(arr2[:, 0])
    sorted1 = arr1[sort_mask1]
    sorted2 = arr2[sort_mask2]
    idx1 = np.arange(len(arr1))[sort_mask1]
    idx2 = np.arange(len(arr2))[sort_mask2]

    i_arr, j_arr, ov_arr = compute_intersections_core(sorted1, sorted2, idx1, idx2)

    result = defaultdict(list)
    for i, j, ov in zip(i_arr, j_arr, ov_arr):
        key = ids1[i] if ids1 is not None else i
        value_id = ids2[j] if ids2 is not None else j
        result[key].append((value_id, ov))

    return result


@njit
def compute_intersections_core(sorted1, sorted2, sorted_idx1, sorted_idx2):
    result_i = []
    result_j = []
    result_ov = []

    j = 0
    n1, n2 = len(sorted1), len(sorted2)

    for i in range(n1):
        start1, end1 = sorted1[i]
        orig_i = sorted_idx1[i]

        while j < n2 and sorted2[j, 1] <= start1:
            j += 1

        k = j
        while k < n2 and sorted2[k, 0] < end1:
            start2, end2 = sorted2[k]
            orig_j = sorted_idx2[k]

            ov = min(end1, end2) - max(start1, start2)
            if ov > 0:
                result_i.append(orig_i)
                result_j.append(orig_j)
                result_ov.append(ov)

            k += 1

    return np.array(result_i), np.array(result_j), np.array(result_ov)


def compute_overlap_size(start1: int, end1: int, start2: int, end2: int) -> int:
    return max(0, min(end1, end2) - max(start1, start2))


def intervals_to_array(intervals: List) -> np.ndarray:
    """Convert list of GenomicInterval objects to 2D numpy array of [start, end] pairs."""
    if not intervals:
        return np.empty((0, 2), dtype=np.int32)
    
    starts = [interval.start for interval in intervals]
    ends = [interval.end for interval in intervals]
    
    return np.column_stack([starts, ends])


def array_to_intervals(array: np.ndarray, chrom: str) -> List:
    """Convert 2D numpy array of [start, end] pairs to list of GenomicInterval objects."""
    from ..core.intervals import GenomicInterval
    from ..core_types import Strand
    
    if array.size == 0:
        return []
    
    intervals = []
    for start, end in array:
        interval = GenomicInterval(
            chrom=chrom,
            start=int(start),
            end=int(end),
            strand=Strand.UNKNOWN,
            id=None
        )
        intervals.append(interval)
    
    return intervals


def chains_to_arrays(chains: List, for_q: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    if not chains:
        return np.empty((0, 2), dtype=np.int32), np.empty(0, dtype=np.int32)
    
    if for_q:
        spans = np.array([c.q_span for c in chains], dtype=np.int32)
    else:
        spans = np.array([c.t_span for c in chains], dtype=np.int32)
    
    ids = np.array([c.chain_id for c in chains], dtype=np.int32)
    
    return spans, ids


def transcripts_to_arrays(transcripts: List) -> Tuple[np.ndarray, np.ndarray]:
    if not transcripts:
        return np.empty((0, 2), dtype=np.int32), np.empty(0, dtype=object)
    
    spans = np.array([t.transcript_span for t in transcripts], dtype=np.int32)
    ids = np.array([t.id for t in transcripts])
    
    return spans, ids 


def projected_intervals_to_genomic_intervals(
    projected_arrays: List[np.ndarray],
    target_chrom: str,
    target_strand: Strand = Strand.UNKNOWN,
    ids: Optional[List[str]] = None
) -> List[List[GenomicInterval]]:
    """Convert projected interval arrays to GenomicInterval objects.
    
    Convenience function to convert the output of project_intervals_through_genome_alignment
    into GenomicInterval objects.
    """
    result = []
    
    for i, array in enumerate(projected_arrays):
        interval_list = []
        
        if len(array) == 0:
            result.append(interval_list)
            continue
            
        for j, (start, end) in enumerate(array):
            if start == 0 and end == 0:
                continue
                
            interval_id = None
            if ids is not None and i < len(ids):
                interval_id = f"{ids[i]}_{j}" if len(array) > 1 else ids[i]
                
            interval = GenomicInterval(
                chrom=target_chrom,
                start=int(start),
                end=int(end),
                strand=target_strand,
                id=interval_id
            )
            interval_list.append(interval)
            
        result.append(interval_list)
    
    return result
