from dataclasses import dataclass
from functools import cached_property
from typing import List, Optional, Dict, Union, Tuple
import numpy as np
from pathlib import Path

from pyrion.core.strand import Strand


@dataclass(frozen=True)
class GenomeAlignment:
    chain_id: int
    score: int
    t_chrom: str
    t_strand: int
    t_size: int
    q_chrom: str
    q_strand: int
    q_size: int
    blocks: np.ndarray             # Shape (N, 4) -- [[t_start, t_end, q_start, q_end], ...]
    child_id: Optional[int] = None  # For sub-chains (None for original chains)

    @cached_property
    def t_span(self) -> np.ndarray:
        return np.array([self.blocks[0][0], self.blocks[-1][1]], dtype=np.int32)

    @cached_property
    def q_span(self) -> np.ndarray:
        if self.q_strand == -1:
            # For negative strand, coordinates are reversed: first block has highest, last block has lowest
            return np.array([self.blocks[-1][2], self.blocks[0][3]], dtype=np.int32)
        else:
            # For positive strand, use first block start and last block end as before
            return np.array([self.blocks[0][2], self.blocks[-1][3]], dtype=np.int32)

    def __repr__(self) -> str:
        t_strand_str = Strand.from_int(self.t_strand).to_char()
        q_strand_str = Strand.from_int(self.q_strand).to_char()
        
        # Get target and query spans
        t_start, t_end = self.t_span
        q_start, q_end = self.q_span
        
        return (f"GenomeAlignment(id={self.chain_id}, score={self.score:,}, "
                f"T={self.t_chrom}:{t_start:,}-{t_end:,}:{t_strand_str} -> "
                f"Q={self.q_chrom}:{q_start:,}-{q_end:,}:{q_strand_str}, "
                f"{len(self.blocks)} blocks)")

    def aligned_length(self) -> int:
        if len(self.blocks) == 0:
            return 0
        return int(np.sum(self.blocks[:, 1] - self.blocks[:, 0]))

    def t_length(self) -> int:
        return int(self.t_span[1] - self.t_span[0])

    def q_length(self) -> int:
        return int(self.q_span[1] - self.q_span[0])

    def blocks_in_target(self) -> np.ndarray:
        return self.blocks[:, :2]

    def blocks_in_query(self) -> np.ndarray:
        return self.blocks[:, 2:]

    def __hash__(self):
        return hash((self.chain_id, self.t_chrom, self.t_strand, self.q_chrom, self.q_strand))


class GenomeAlignmentsCollection:
    """Container for many genome alignments."""
    def __init__(
        self,
        alignments: Optional[List[GenomeAlignment]] = None,
        source_file: Optional[str] = None
    ):
        self.alignments: List[GenomeAlignment] = alignments or []
        self.source_file: Optional[str] = source_file

        self._id_index: Optional[Dict[int, int]] = None  # chain_id → index
        self._chrom_index: Optional[Dict[str, List[int]]] = None  # target chrom → indices
        self._query_chrom_index: Optional[Dict[str, List[int]]] = None  # query chrom → indices

    def __len__(self):
        return len(self.alignments)

    def __getitem__(self, idx: int) -> GenomeAlignment:
        return self.alignments[idx]

    def get_by_chain_id(self, chain_id: int) -> Optional[GenomeAlignment]:
        if self._id_index is None:
            self._build_id_index()
        idx = self._id_index.get(chain_id)
        return self.alignments[idx] if idx is not None else None

    def get_by_target_chrom(self, chrom: str) -> List[GenomeAlignment]:
        if self._chrom_index is None:
            self._build_chrom_index()
        indices = self._chrom_index.get(chrom, [])
        return [self.alignments[i] for i in indices]

    def get_by_query_chrom(self, chrom: str) -> List[GenomeAlignment]:
        if self._query_chrom_index is None:
            self._build_query_chrom_index()
        indices = self._query_chrom_index.get(chrom, [])
        return [self.alignments[i] for i in indices]

    def get_reference_chromosomes(self) -> List[str]:
        if self._chrom_index is None:
            self._build_chrom_index()
        return list(self._chrom_index.keys())

    def get_query_chromosomes(self) -> List[str]:
        if self._query_chrom_index is None:
            self._build_query_chrom_index()
        return list(self._query_chrom_index.keys())

    def get_chain_ids_by_target_chrom(self, chrom: str) -> List[int]:
        if self._chrom_index is None:
            self._build_chrom_index()
        indices = self._chrom_index.get(chrom, [])
        return [self.alignments[i].chain_id for i in indices]

    def get_chain_ids_by_query_chrom(self, chrom: str) -> List[int]:
        if self._query_chrom_index is None:
            self._build_query_chrom_index()
        indices = self._query_chrom_index.get(chrom, [])
        return [self.alignments[i].chain_id for i in indices]

    def get_alignments_overlapping_target_interval(self, interval: 'GenomicInterval', include_partial: bool = True) -> List[GenomeAlignment]:
        target_chrom_alignments = self.get_by_target_chrom(interval.chrom)
        
        if not target_chrom_alignments:
            return []
        
        matching = []
        for alignment in target_chrom_alignments:
            # Get target span: [start, end]
            t_start, t_end = alignment.t_span
            
            if include_partial:
                if not (t_end <= interval.start or interval.end <= t_start):
                    matching.append(alignment)
            else:
                if t_start >= interval.start and t_end <= interval.end:
                    matching.append(alignment)
        
        return matching

    def get_alignments_overlapping_query_interval(self, interval: 'GenomicInterval', include_partial: bool = True) -> List[GenomeAlignment]:
        query_chrom_alignments = self.get_by_query_chrom(interval.chrom)
        
        if not query_chrom_alignments:
            return []
        
        # Check overlap on query coordinates
        matching = []
        for alignment in query_chrom_alignments:
            # Get query span: [start, end]  
            q_start, q_end = alignment.q_span
            
            if include_partial:
                # Include if alignment intersects (overlaps) the target interval - even 1nt
                if not (q_end <= interval.start or interval.end <= q_start):
                    matching.append(alignment)
            else:
                # Include only if alignment is fully contained within the target interval
                if q_start >= interval.start and q_end <= interval.end:
                    matching.append(alignment)
        
        return matching

    # Convenience methods with shorter names
    def get_alignments_in_interval(self, interval: 'GenomicInterval', include_partial: bool = True) -> List[GenomeAlignment]:
        return self.get_alignments_overlapping_target_interval(interval, include_partial)
    
    def get_alignments_fully_contained(self, interval: 'GenomicInterval') -> List[GenomeAlignment]:
        return self.get_alignments_overlapping_target_interval(interval, include_partial=False)

    def _build_id_index(self):
        self._id_index = {ga.chain_id: i for i, ga in enumerate(self.alignments)}

    def _build_chrom_index(self):
        from collections import defaultdict
        chrom_index = defaultdict(list)
        for i, ga in enumerate(self.alignments):
            chrom_index[ga.t_chrom].append(i)
        self._chrom_index = dict(chrom_index)

    def _build_query_chrom_index(self):
        from collections import defaultdict
        query_chrom_index = defaultdict(list)
        for i, ga in enumerate(self.alignments):
            query_chrom_index[ga.q_chrom].append(i)
        self._query_chrom_index = dict(query_chrom_index)

    def sort_by_score(self, max_elems: Optional[int] = None) -> List[Tuple[int, int]]:
        from .genome_alignment_auxiliary import sort_alignments_by_score
        return sort_alignments_by_score(self, max_elems)

    def summary(self) -> str:
        return f"{len(self.alignments):,} genome alignments from {self.source_file or 'unknown source'}"

    def __str__(self) -> str:
        """String representation with summary."""
        from ..ops.chain_serialization import genome_alignments_collection_summary_string
        return genome_alignments_collection_summary_string(self)

    def __repr__(self) -> str:
        return f"<GenomeAlignmentsCollection: {self.summary()}>"

    def save_to_chain(self, file_path: Union[str, Path]) -> None:
        from ..ops.chain_serialization import save_genome_alignments_collection_to_chain
        save_genome_alignments_collection_to_chain(self, file_path)

    def save_to_json(self, file_path: Union[str, Path]) -> None:
        from ..ops.chain_serialization import save_genome_alignments_collection_to_json
        save_genome_alignments_collection_to_json(self, file_path)

    @classmethod
    def from_json(cls, file_path: Union[str, Path]) -> 'GenomeAlignmentsCollection':
        from ..ops.chain_serialization import load_genome_alignments_collection_from_json
        return load_genome_alignments_collection_from_json(file_path)
