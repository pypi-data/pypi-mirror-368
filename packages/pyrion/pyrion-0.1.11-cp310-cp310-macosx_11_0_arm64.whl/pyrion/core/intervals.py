"""Genomic interval representations."""

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Union, List, Callable, Dict, Tuple

import numpy as np

from .strand import Strand
from ..core_types import Coordinate


class RegionType(IntEnum):
    CDS = 0
    UTR5 = 1
    UTR3 = 2
    FLANK_LEFT = 3
    FLANK_RIGHT = 4
    GENE_SPAN = 5


@dataclass(frozen=True)
class AnnotatedIntervalSet:
    intervals: np.ndarray        # shape (N, 2), dtype=int32
    region_types: np.ndarray     # shape (N,), dtype=int8
    
    def __repr__(self) -> str:
        n_intervals = len(self.intervals) if len(self.intervals.shape) > 0 else 0
        unique_types = len(set(self.region_types)) if len(self.region_types) > 0 else 0
        return f"AnnotatedIntervalSet({n_intervals} intervals, {unique_types} region types)"


@dataclass(frozen=True)
class GenomicInterval:
    """Single genomic interval with strand information and optional ID."""
    chrom: str
    start: Coordinate
    end: Coordinate
    strand: Strand = Strand.UNKNOWN
    id: Optional[str] = None
    
    def __post_init__(self):
        # Convert integer strand to Strand object if needed (for C parser compatibility)
        if isinstance(self.strand, int):
            object.__setattr__(self, 'strand', Strand.from_int(self.strand))
        
        if self.start >= self.end:
            raise ValueError(f"Invalid interval: start {self.start} >= end {self.end}")
        if self.start < 0:
            raise ValueError(f"Negative start coordinate: {self.start}")
    
    def length(self) -> int:
        return self.end - self.start
    
    def intersects(self, other: 'GenomicInterval') -> bool:
        if self.chrom != other.chrom:
            return False
        return not (self.end <= other.start or other.end <= self.start)
    
    def overlap(self, other: 'GenomicInterval') -> int:
        if not self.intersects(other):
            return 0
        return min(self.end, other.end) - max(self.start, other.start)
    
    def flip_strand(self) -> 'GenomicInterval':
        return GenomicInterval(
            chrom=self.chrom,
            start=self.start, 
            end=self.end,
            strand=self.strand.flip(),
            id=self.id
        )
    
    def contains(self, pos: Coordinate) -> bool:
        return self.start <= pos < self.end
    
    def union(self, other: 'GenomicInterval') -> Optional['GenomicInterval']:
        if self.chrom != other.chrom:
            return None
        
        # For union, combine IDs if both exist, otherwise use the non-None one
        union_id = None
        if self.id and other.id:
            union_id = f"{self.id}+{other.id}"
        elif self.id:
            union_id = self.id
        elif other.id:
            union_id = other.id
            
        return GenomicInterval(
            chrom=self.chrom,
            start=min(self.start, other.start),
            end=max(self.end, other.end),
            strand=self.strand if self.strand == other.strand else Strand.UNKNOWN,
            id=union_id
        )
    
    def __str__(self) -> str:
        if self.strand == Strand.UNKNOWN:
            base_str = f"{self.chrom}:{self.start}-{self.end}"
        else:
            base_str = f"{self.chrom}:{self.start}-{self.end}:{self.strand.to_char()}"
        if self.id:
            return f"{base_str} ({self.id})"
        return base_str

    def to_bed6_string(self, score: int = 1000) -> str:
        """Convert to BED6 format string."""
        from ..ops.interval_serialization import genomic_interval_to_bed6_string
        return genomic_interval_to_bed6_string(self, score)
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        id_part = f", id='{self.id}'" if self.id else ""
        length = self.length()
        return f"GenomicInterval(chrom='{self.chrom}', start={self.start}, end={self.end}, length={length:,}, strand={self.strand.name}{id_part})"
    
    @classmethod
    def from_string(cls, interval_string: str, id: Optional[str] = None) -> 'GenomicInterval':
        """Create GenomicInterval from string representation.
        
        Supported formats:
        - "chr1:100-200" (no strand)
        - "chr1:100-200:+" (plus strand)  
        - "chr1:100-200:-" (minus strand)
        - "chr1:1,000,000-2,000,000" (commas in numbers supported)
        - "chr11:118,300,000-118,400,000:+" (full example with commas)
        """
        interval_string = interval_string.strip()
        
        # Split by colons to handle strand
        parts = interval_string.split(':')
        
        if len(parts) < 2:
            raise ValueError(f"Invalid interval format: {interval_string}. Expected 'chr:start-end' or 'chr:start-end:strand'")
        
        chrom = parts[0]
        strand = Strand.UNKNOWN

        if len(parts) == 3:
            strand_char = parts[2]
            if strand_char == '+':
                strand = Strand.PLUS
            elif strand_char == '-':
                strand = Strand.MINUS
            elif strand_char == '.':
                strand = Strand.UNKNOWN
            elif strand_char == '0':
                strand = Strand.UNKNOWN
            else:
                raise ValueError(f"Invalid strand character: {strand_char}. Expected '+', '-', or '.'")
        elif len(parts) > 3:
            raise ValueError(f"Too many colons in interval string: {interval_string}")
        
        coord_part = parts[1]
        if '-' not in coord_part:
            raise ValueError(f"Invalid coordinate format: {coord_part}. Expected 'start-end'")
        
        coord_parts = coord_part.split('-')
        if len(coord_parts) != 2:
            raise ValueError(f"Invalid coordinate format: {coord_part}. Expected 'start-end'")
        
        try:
            start = int(coord_parts[0].replace(',', ''))  # Remove commas for readability
            end = int(coord_parts[1].replace(',', ''))
        except ValueError as e:
            raise ValueError(f"Invalid coordinates in {coord_part}: {e}")
        
        return cls(chrom=chrom, start=start, end=end, strand=strand, id=id)


@dataclass(frozen=True)
class GenomicIntervalsCollection:
    chrom: str
    strand: Strand
    array: np.ndarray  # shape (N, 2), dtype=int32, sorted by start
    ids: np.ndarray    # shape (N,), dtype=object or None
    
    def __post_init__(self):
        if len(self.array) == 0:
            return
            
        if self.array.shape[1] != 2:
            raise ValueError("Array must have shape (N, 2)")
        
        if self.ids is not None and len(self.ids) != len(self.array):
            raise ValueError("IDs array length must match intervals array length")

        starts = self.array[:, 0]
        if not np.all(starts[:-1] <= starts[1:]):
            raise ValueError("Intervals must be sorted by start position")
    
    @classmethod
    def from_intervals(cls, intervals: List[GenomicInterval]) -> 'GenomicIntervalsCollection':
        """Create collection from list of GenomicInterval objects."""
        if not intervals:
            return cls._empty_collection()
        
        # Check chromosome consistency
        chroms = {iv.chrom for iv in intervals}
        if len(chroms) > 1:
            raise ValueError("All intervals must be on the same chromosome")
        
        # Check strand consistency  
        strands = {iv.strand for iv in intervals}
        if len(strands) > 1:
            raise ValueError("All intervals must have the same strand")
        
        chrom = intervals[0].chrom
        strand = intervals[0].strand
        
        # Sort by start position
        sorted_intervals = sorted(intervals, key=lambda x: x.start)
        
        # Build arrays
        array = cls._build_array(sorted_intervals)
        ids = np.array([iv.id for iv in sorted_intervals], dtype=object)
        
        return cls(chrom=chrom, strand=strand, array=array, ids=ids)
    
    @classmethod
    def from_array(cls, array: np.ndarray, chrom: str, 
                   strand: Optional[Strand] = None, ids: Optional[List[str]] = None) -> 'GenomicIntervalsCollection':
        """Create collection from numpy array."""
        if strand is None:
            strand = Strand.UNKNOWN
            
        array = np.asarray(array, dtype=np.int32)
        if array.shape[1] != 2:
            raise ValueError("Array must have shape (N, 2)")

        sort_indices = np.argsort(array[:, 0])
        sorted_array = array[sort_indices]
        
        sorted_ids = None
        if ids is not None:
            sorted_ids = np.array(ids, dtype=object)[sort_indices]
        
        return cls(chrom=chrom, strand=strand, array=sorted_array, ids=sorted_ids)
    
    @classmethod
    def from_strings(cls, interval_strings, ids: Optional[List[str]] = None) -> Dict[Tuple[str, Strand], 'GenomicIntervalsCollection']:
        from .intervals_auxiliary import create_intervals_collections_from_strings
        return create_intervals_collections_from_strings(interval_strings, ids)
    
    @classmethod
    def _empty_collection(cls) -> 'GenomicIntervalsCollection':
        return cls(
            chrom="",
            strand=Strand.UNKNOWN,
            array=np.empty((0, 2), dtype=np.int32),
            ids=None
        )
    
    @staticmethod
    def _build_array(intervals: List[GenomicInterval]) -> np.ndarray:
        return np.array([[iv.start, iv.end] for iv in intervals], dtype=np.int32)
    
    def __len__(self) -> int:
        return len(self.array)
    
    def is_empty(self) -> bool:
        return len(self.array) == 0
    
    def __repr__(self) -> str:
        if self.is_empty():
            return f"GenomicIntervalsCollection(empty, chrom='{self.chrom}', strand={self.strand.name})"
        
        has_ids = self.ids is not None
        id_info = " with IDs" if has_ids else ""
        return f"GenomicIntervalsCollection({len(self.array)} intervals{id_info}, chrom='{self.chrom}', strand={self.strand.name})"
    
    def to_intervals_list(self) -> List[GenomicInterval]:
        if self.is_empty():
            return []
        
        intervals = []
        for i, (start, end) in enumerate(self.array):
            interval_id = self.ids[i] if self.ids is not None else None
            intervals.append(GenomicInterval(
                chrom=self.chrom,
                start=int(start),
                end=int(end),
                strand=self.strand,
                id=interval_id
            ))
        return intervals
    
    def merge_close(self, max_gap: int = 0) -> 'GenomicIntervalsCollection':
        from ..ops.interval_collection_ops import merge_close_intervals
        return merge_close_intervals(self, max_gap)
    
    def group_by_proximity(self, max_gap: int) -> List['GenomicIntervalsCollection']:
        from ..ops.interval_collection_ops import group_intervals_by_proximity
        return group_intervals_by_proximity(self, max_gap)
    
    def split_on_gaps(self, min_gap: int) -> List['GenomicIntervalsCollection']:
        from ..ops.interval_collection_ops import split_intervals_on_gaps
        return split_intervals_on_gaps(self, min_gap)
    
    def intersect(self, other: Union['GenomicIntervalsCollection', GenomicInterval]) -> 'GenomicIntervalsCollection':
        from ..ops.interval_collection_ops import intersect_collections
        return intersect_collections(self, other)
    
    def filter_by(self, predicate: Callable[[GenomicInterval], bool]) -> 'GenomicIntervalsCollection':
        from ..ops.interval_collection_ops import filter_collection
        return filter_collection(self, predicate)
    
    def to_bed6_string(self, score: int = 1000) -> str:
        from ..ops.interval_serialization import genomic_intervals_to_bed6_string
        return genomic_intervals_to_bed6_string(self.to_intervals_list(), score)
    
    def __str__(self) -> str:
        if self.is_empty():
            return f"GenomicIntervalsCollection(empty)"
        return f"GenomicIntervalsCollection({self.chrom}:{len(self)} intervals)"
