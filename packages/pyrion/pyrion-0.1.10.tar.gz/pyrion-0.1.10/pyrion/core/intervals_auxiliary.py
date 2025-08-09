"""Auxiliary functions for interval objects."""

from typing import Dict, List, Tuple, Optional
from .intervals import GenomicInterval, GenomicIntervalsCollection
from .strand import Strand


def create_intervals_collections_from_strings(interval_strings, ids: Optional[List[str]] = None) -> Dict[Tuple[str, Strand], GenomicIntervalsCollection]:
    """Create collections from iterable of string representations, grouped by chromosome and strand."""
    string_list = list(interval_strings)
    
    if not string_list:
        return {}
    
    intervals = []
    for i, interval_string in enumerate(string_list):
        # Use provided ID or generate one
        interval_id = None
        if ids is not None:
            if len(ids) != len(string_list):
                raise ValueError(f"IDs list length ({len(ids)}) must match intervals length ({len(string_list)})")
            interval_id = ids[i]
        
        interval = GenomicInterval.from_string(interval_string, id=interval_id)
        intervals.append(interval)
    
    groups = {}
    for interval in intervals:
        key = (interval.chrom, interval.strand)
        if key not in groups:
            groups[key] = []
        groups[key].append(interval)

    collections = {}
    for (chrom, strand), group_intervals in groups.items():
        collections[(chrom, strand)] = GenomicIntervalsCollection.from_intervals(group_intervals)
    
    return collections 