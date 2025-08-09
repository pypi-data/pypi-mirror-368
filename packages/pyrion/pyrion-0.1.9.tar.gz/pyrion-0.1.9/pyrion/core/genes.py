"""Gene and transcript representations."""

from dataclasses import dataclass
from functools import cached_property
from typing import Optional, List, Dict, Set, Tuple, Union, Callable
import numpy as np
from weakref import WeakKeyDictionary
from pathlib import Path

from .genes_auxiliary import build_annotated_regions
from .strand import Strand
from .intervals import GenomicInterval, AnnotatedIntervalSet
from . import genes_auxiliary

_region_cache = WeakKeyDictionary()


@dataclass(frozen=True)
class Transcript:
    blocks: np.ndarray  # (N, 2) array: start, end
    strand: Strand
    chrom: str
    id: str
    cds_start: Optional[int] = None
    cds_end: Optional[int] = None
    biotype: Optional[str] = None

    @property
    def is_coding(self) -> bool:
        return self.cds_start is not None and self.cds_end is not None

    def __hash__(self) -> int:
        return hash(self.id)

    @cached_property
    def transcript_span(self) -> np.ndarray:
        return np.array([self.blocks[0][0], self.blocks[-1][1]], dtype=np.int32)

    @cached_property
    def transcript_interval(self) -> GenomicInterval:
        return genes_auxiliary.get_transcript_interval(self)

    @cached_property
    def transcript_cds_interval(self) -> GenomicInterval:
        return genes_auxiliary.get_transcript_cds_interval(self)

    @cached_property
    def cds_blocks(self) -> np.ndarray:
        return genes_auxiliary.get_cds_blocks(self)

    @cached_property
    def utr5_blocks(self) -> np.ndarray:
        return genes_auxiliary.get_utr5_blocks(self)

    @cached_property
    def utr3_blocks(self) -> np.ndarray:
        return genes_auxiliary.get_utr3_blocks(self)
    
    @cached_property
    def utr_blocks(self) -> np.ndarray:
        """Get all UTR intervals (merged 5' and 3')."""
        utr5 = self.utr5_blocks
        utr3 = self.utr3_blocks
        
        if utr5.size == 0 and utr3.size == 0:
            return np.empty((0, 2), dtype=np.uint32)
        elif utr5.size == 0:
            return utr3
        elif utr3.size == 0:
            return utr5
        else:
            return np.vstack([utr5, utr3])

    def __str__(self) -> str:
        from ..ops.transcript_serialization import transcript_to_bed12_string
        return transcript_to_bed12_string(self)
    
    def __repr__(self) -> str:
        coding_info = f", coding={self.is_coding}" if self.is_coding else ", non-coding"
        cds_info = f", CDS={self.cds_start}-{self.cds_end}" if self.is_coding else ""
        
        strand_str = Strand(self.strand).to_char()
            
        return f"Transcript(id='{self.id}', {self.chrom}:{self.blocks[0,0]}-{self.blocks[-1,1]}:{strand_str}, {len(self.blocks)} exons{coding_info}{cds_info})"

    def compute_flanks(
            self,
            flank_size: int,
            chrom_sizes: Dict[str, int]
    ) -> Tuple[Optional[GenomicInterval], Optional[GenomicInterval]]:
        return genes_auxiliary.compute_flanks(self, flank_size, chrom_sizes)

    def get_annotated_regions(self, chrom_sizes: dict, flank_size: int = 5000) -> AnnotatedIntervalSet:
        cache = _region_cache.setdefault(self, {})
        key = (flank_size, id(chrom_sizes))
        if key not in cache:
            cache[key] = build_annotated_regions(self, chrom_sizes, flank_size)
        return cache[key]
    
    def contains_interval(self, interval: GenomicInterval) -> bool:
        if self.chrom != interval.chrom:
            return False
        
        block_starts = self.blocks[:, 0]
        block_ends = self.blocks[:, 1]
        
        no_overlap = (interval.end <= block_starts) | (block_ends <= interval.start)
        has_overlap = ~no_overlap
        
        return np.any(has_overlap)
    
    def splice_junctions(self):
        """Generator yielding splice junction coordinates (donor, acceptor) for transcript."""
        if len(self.blocks) <= 1:
            # Single exon transcript has no splice junctions
            return
        
        sorted_blocks = self.blocks[np.argsort(self.blocks[:, 0])]
        for i in range(len(sorted_blocks) - 1):
            current_end = sorted_blocks[i, 1]      # Donor site (end of current exon)
            next_start = sorted_blocks[i + 1, 0]   # Acceptor site (start of next exon)
            
            if self.strand == Strand.MINUS:
                yield (next_start, current_end)  # (acceptor, donor)
            else:
                yield (current_end, next_start)  # (donor, acceptor)
                
    def get_introns(self, use_numba: bool = True) -> np.ndarray:
        if len(self.blocks) <= 1:
            return np.empty((0, 2), dtype=np.int32)
        
        intron_starts = self.blocks[:-1, 1]
        intron_ends = self.blocks[1:, 0]
        valid_mask = intron_starts < intron_ends
        
        if not np.any(valid_mask):
            return np.empty((0, 2), dtype=np.int32)
            
        return np.column_stack((intron_starts[valid_mask], intron_ends[valid_mask]))


class Gene:
    """Gene containing multiple transcripts with computed genomic bounds."""
    def __init__(self, gene_id: str, transcripts: List[Transcript], gene_name: Optional[str] = None):
        self.gene_id = gene_id
        self.gene_name = gene_name
        self._transcripts = list(transcripts)
        self._canonical_transcript_id: Optional[str] = None
        
        if not self._transcripts:
            raise ValueError(f"Gene {gene_id} must have at least one transcript")
        
        # Validate all transcripts are on same chromosome and strand
        first_transcript = self._transcripts[0]
        self._chrom = first_transcript.chrom
        self._strand = first_transcript.strand
        
        for transcript in self._transcripts[1:]:
            if transcript.chrom != self._chrom:
                raise ValueError(f"All transcripts must be on same chromosome. Found {transcript.chrom} and {self._chrom}")
            if transcript.strand != self._strand:
                raise ValueError(f"All transcripts must have same strand. Found {transcript.strand} and {self._strand}")
    
    @property
    def transcripts(self) -> List[Transcript]:
        return self._transcripts.copy()
    
    @property
    def transcript_ids(self) -> Set[str]:
        return {t.id for t in self._transcripts}
    
    @property
    def chrom(self) -> str:
        return self._chrom

    @property
    def strand(self) -> Strand:
        return self._strand
    
    @cached_property
    def start(self) -> int:
        return int(min(t.transcript_span[0] for t in self._transcripts)) if self._transcripts else 0
    
    @cached_property
    def end(self) -> int:
        return int(max(t.transcript_span[1] for t in self._transcripts)) if self._transcripts else 0

    @cached_property
    def bounds(self) -> GenomicInterval:
        return GenomicInterval(self.chrom, self.start, self.end, self.strand)

    @property
    def length(self) -> int:
        return self.end - self.start
    
    def get_transcript(self, transcript_id: str) -> Optional[Transcript]:
        for transcript in self._transcripts:
            if transcript.id == transcript_id:
                return transcript
        return None
    
    def has_transcript(self, transcript_id: str) -> bool:
        return transcript_id in self.transcript_ids
    
    @property
    def is_coding(self) -> bool:
        """Check if gene has any coding transcripts."""
        return any(t.is_coding for t in self._transcripts)
    
    def apply_canonizer(self, canonizer_func: Optional[Callable] = None, **kwargs) -> None:
        """Set the canonical transcript using a canonizer function.
        
        Args:
            canonizer_func: Function that takes transcripts list and returns canonical transcript ID.
                          If None, uses the default longest_isoform_canonizer.
            **kwargs: Additional arguments passed to the canonizer function.
        """
        if canonizer_func is None:
            from .canonizer import DEFAULT_CANONIZER
            canonizer_func = DEFAULT_CANONIZER
        
        canonical_id = canonizer_func(self._transcripts, **kwargs)
        
        if canonical_id is not None and canonical_id not in self.transcript_ids:
            raise ValueError(f"Canonical transcript ID '{canonical_id}' not found in gene {self.gene_id}")
        
        self._canonical_transcript_id = canonical_id


    def set_canonical_transcript(self, transcript_id: str) -> None:
        if transcript_id not in self.transcript_ids:
            raise ValueError(f"Transcript ID '{transcript_id}' not found in gene {self.gene_id}")
        
        self._canonical_transcript_id = transcript_id
    
    @property
    def canonical_transcript_id(self) -> Optional[str]:
        return self._canonical_transcript_id
    
    @property
    def canonical_transcript(self) -> Optional[Transcript]:
        if self._canonical_transcript_id is None:
            return None
        return self.get_transcript(self._canonical_transcript_id)
    
    @property
    def has_canonical_transcript(self) -> bool:
        return self._canonical_transcript_id is not None
    
    def clear_canonical_transcript(self) -> None:
        self._canonical_transcript_id = None
    
    def __len__(self) -> int:
        return len(self._transcripts)
    
    def __repr__(self) -> str:
        name_info = f", name={self.gene_name}" if self.gene_name else ""
        canonical_info = f", canonical={self._canonical_transcript_id}" if self.has_canonical_transcript else ""
        return f"Gene(id={self.gene_id}{name_info}, {self.chrom}:{self.start}-{self.end}:{self._strand}, {len(self._transcripts)} transcripts{canonical_info})"


class TranscriptsCollection:
    """Container for many transcripts."""

    def __init__(
        self,
        transcripts: Optional[List[Transcript]] = None,
        source_file: Optional[str] = None
    ):
        self.transcripts: List[Transcript] = transcripts or []
        self.source_file: Optional[str] = source_file

        self._id_index: Optional[Dict[str, int]] = None  # transcript_id → index
        self._chrom_index: Optional[Dict[str, List[int]]] = None  # chrom → indices
        self._gene_data: Optional['GeneData'] = None
        self._genes_cache: Optional[Dict[str, Gene]] = None
        self._applied_biotypes: bool = False
        self._applied_gene_names: bool = False

    def __len__(self):
        return len(self.transcripts)

    def __getitem__(self, idx: int) -> Transcript:
        return self.transcripts[idx]

    def get_by_id(self, transcript_id: str) -> Optional[Transcript]:
        if self._id_index is None:
            self._build_id_index()
        idx = self._id_index.get(transcript_id)
        return self.transcripts[idx] if idx is not None else None

    def get_by_chrom(self, chrom: str) -> List[Transcript]:
        if self._chrom_index is None:
            self._build_chrom_index()
        indices = self._chrom_index.get(chrom, [])
        return [self.transcripts[i] for i in indices]

    def get_all_chromosomes(self) -> List[str]:
        if self._chrom_index is None:
            self._build_chrom_index()
        return list(self._chrom_index.keys())

    def get_transcript_ids_by_chrom(self, chrom: str) -> List[str]:
        if self._chrom_index is None:
            self._build_chrom_index()
        indices = self._chrom_index.get(chrom, [])
        return [self.transcripts[i].id for i in indices]
    
    def get_transcripts_in_interval(self, interval: GenomicInterval, include_partial: bool = True) -> 'TranscriptsCollection':
        from .genes_auxiliary import filter_transcripts_in_interval
        return filter_transcripts_in_interval(self, interval, include_partial)

    def _build_id_index(self):
        self._id_index = {t.id: i for i, t in enumerate(self.transcripts)}

    def _build_chrom_index(self):
        from collections import defaultdict
        chrom_index = defaultdict(list)
        for i, t in enumerate(self.transcripts):
            chrom_index[t.chrom].append(i)
        self._chrom_index = dict(chrom_index)

    def bind_gene_data(self, gene_data: 'GeneData') -> None:
        self._gene_data = gene_data
        self._genes_cache = None  # Clear cache when binding new data
        self._applied_biotypes = False
        self._applied_gene_names = False
        
        # Apply transcript biotypes if available
        if gene_data.has_biotype_mapping():
            self._apply_transcript_biotypes()
        
        # Apply gene names if we have gene-transcript mapping and gene names
        if gene_data.has_gene_transcript_mapping() and gene_data.has_gene_name_mapping():
            self._applied_gene_names = True  # Will be applied when building genes cache

    def _apply_transcript_biotypes(self) -> None:
        if self._gene_data is None or not self._gene_data.has_biotype_mapping():
            return
        
        updated_transcripts = []
        for transcript in self.transcripts:
            biotype = self._gene_data.get_transcript_biotype(transcript.id)
            if biotype is not None and transcript.biotype is None:
                updated_transcript = Transcript(
                    blocks=transcript.blocks,
                    strand=transcript.strand,
                    chrom=transcript.chrom,
                    id=transcript.id,
                    cds_start=transcript.cds_start,
                    cds_end=transcript.cds_end,
                    biotype=biotype
                )
                updated_transcripts.append(updated_transcript)
            else:
                updated_transcripts.append(transcript)
        
        self.transcripts = updated_transcripts
        self._applied_biotypes = True
        self._id_index = None
        self._chrom_index = None

    def _build_genes_cache(self):
        if not self.has_gene_mapping:
            raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
        
        if self._id_index is None:
            self._build_id_index()
        
        genes_dict = {}
        
        for gene_id in self._gene_data.gene_ids:
            # Get transcripts for this gene that exist in our collection
            transcript_ids = self._gene_data.get_transcripts(gene_id)
            gene_transcripts = []
            
            for transcript_id in transcript_ids:
                transcript = self.get_by_id(transcript_id)
                if transcript is not None:
                    gene_transcripts.append(transcript)
            
            if gene_transcripts:
                gene_name = None
                if self._applied_gene_names and self._gene_data.has_gene_name_mapping():
                    gene_name = self._gene_data.get_gene_name(gene_id)
                
                genes_dict[gene_id] = Gene(gene_id, gene_transcripts, gene_name=gene_name)
        
        self._genes_cache = genes_dict

    def get_gene_by_id(self, gene_id: str) -> Optional[Gene]:
        if not self.has_gene_mapping:
            raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
        
        if self._genes_cache is None:
            self._build_genes_cache()
        
        return self._genes_cache.get(gene_id)

    def get_gene_by_transcript_id(self, transcript_id: str) -> Optional[Gene]:
        if not self.has_gene_mapping:
            raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
        
        gene_id = self._gene_data.get_gene(transcript_id)
        if gene_id is None:
            return None
        
        return self.get_gene_by_id(gene_id)

    def get_by_gene_name(self, gene_name: str) -> List[Gene]:
        """Get Gene objects by gene name. Multiple genes can have the same name."""
        if not self.has_gene_mapping:
            raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
        
        if not self._gene_data.has_gene_name_mapping():
            raise ValueError("No gene name mapping available. Gene names were not provided in the gene data.")
        
        gene_ids = self._gene_data.get_genes_by_name(gene_name)
        
        genes = []
        for gene_id in gene_ids:
            gene = self.get_gene_by_id(gene_id)
            if gene is not None:
                genes.append(gene)
        
        return genes

    @property
    def genes(self) -> List[Gene]:
        if not self.has_gene_mapping:
            raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
        
        if self._genes_cache is None:
            self._build_genes_cache()
        
        return list(self._genes_cache.values())

    @property
    def gene_ids(self) -> Set[str]:
        if not self.has_gene_mapping:
            raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
        
        if self._genes_cache is None:
            self._build_genes_cache()
        
        return set(self._genes_cache.keys())

    @property
    def has_gene_mapping(self) -> bool:
        return self._gene_data is not None and self._gene_data.has_gene_transcript_mapping()
    
    @property
    def available_data_mappings(self) -> List[str]:
        if self._gene_data is None:
            return []
        
        mappings = []
        if self._gene_data.has_gene_transcript_mapping():
            mappings.append("gene-transcript")
        if self._gene_data.has_biotype_mapping():
            mappings.append("transcript-biotype")
        if self._gene_data.has_gene_name_mapping():
            mappings.append("gene-name")
        return mappings
    
    @property 
    def applied_biotypes(self) -> bool:
        return self._applied_biotypes
    
    @property
    def applied_gene_names(self) -> bool:
        return self._applied_gene_names

    def canonize_transcripts(self, canonizer_func: Optional[Callable] = None, **kwargs) -> None:
        from .genes_auxiliary import set_canonical_transcripts_for_collection
        set_canonical_transcripts_for_collection(self, canonizer_func, **kwargs)

    def get_canonical_transcripts(self) -> 'TranscriptsCollection':
        from .genes_auxiliary import get_canonical_transcripts_only_from_collection
        return get_canonical_transcripts_only_from_collection(self)

    def apply_gene_canonical_mapping(self, gene_to_canonical: Dict[str, str]) -> None:
        """gene_to_canonical: Dictionary mapping gene IDs to canonical transcript IDs"""
        if not self.has_gene_mapping:
            raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
        
        # Ensure genes cache is built
        if self._genes_cache is None:
            self._build_genes_cache()
        
        # Apply mapping to each gene
        for gene_id, canonical_transcript_id in gene_to_canonical.items():
            gene = self._genes_cache.get(gene_id)
            if gene is not None:
                gene.set_canonical_transcript(canonical_transcript_id)

    def get_genes_without_canonical_transcript(self) -> List[Gene]:
        if not self.has_gene_mapping:
            raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
        
        if self._genes_cache is None:
            self._build_genes_cache()
        
        return [gene for gene in self._genes_cache.values() if not gene.has_canonical_transcript]

    def summary(self) -> str:
        base_summary = f"{len(self.transcripts):,} transcripts"
        if self._gene_data is not None and self._gene_data.has_gene_transcript_mapping():
            if self._genes_cache is None:
                self._build_genes_cache()
            gene_count = len(self._genes_cache)
            base_summary += f", {gene_count:,} genes"
        
        source_str = f" from {self.source_file}" if self.source_file else ""
        return base_summary + source_str

    def __str__(self) -> str:
        from ..ops.transcript_serialization import transcripts_collection_summary_string
        return transcripts_collection_summary_string(self)
    
    def __repr__(self) -> str:
        return f"<TranscriptsCollection: {self.summary()}>"

    def to_bed12_string(self) -> str:
        from ..ops.transcript_serialization import transcripts_collection_to_bed12_string
        return transcripts_collection_to_bed12_string(self)

    def save_to_bed12(self, file_path: Union[str, Path]) -> None:
        from ..ops.transcript_serialization import save_transcripts_collection_to_bed12
        save_transcripts_collection_to_bed12(self, file_path)

    def save_to_json(self, file_path: Union[str, Path]) -> None:
        from ..ops.transcript_serialization import save_transcripts_collection_to_json
        save_transcripts_collection_to_json(self, file_path)

    @classmethod
    def from_json(cls, file_path: Union[str, Path]) -> 'TranscriptsCollection':
        from ..ops.transcript_serialization import load_transcripts_collection_from_json
        return load_transcripts_collection_from_json(file_path)

