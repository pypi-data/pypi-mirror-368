"""Auxiliary functions for gene and transcript objects."""

import numpy as np
from typing import Tuple, Optional, Dict, Callable, List
from .intervals import GenomicInterval, RegionType, AnnotatedIntervalSet
from .strand import Strand


def get_transcript_interval(transcript) -> GenomicInterval:
    """Get genomic interval spanning the entire transcript."""
    if len(transcript.blocks) == 0:
        raise ValueError("Transcript has no blocks")
    
    starts = transcript.blocks[:, 0]
    ends = transcript.blocks[:, 1]
    
    start = int(np.min(starts))
    end = int(np.max(ends))
    
    return GenomicInterval(
        chrom=transcript.chrom,
        start=start,
        end=end,
        strand=transcript.strand,
        id=transcript.id
    )


def get_transcript_cds_interval(transcript) -> Optional[GenomicInterval]:
    """Get genomic interval spanning the CDS region."""
    if not transcript.is_coding:
        return None

    cds = transcript.cds_blocks
    start = cds[0, 0]
    end = cds[-1, 1]
    return GenomicInterval(
        chrom=transcript.chrom,
        start=start,
        end=end,
        strand=transcript.strand,
        id=transcript.id
    )


def compute_flanks(
    transcript, 
    flank_size: int, 
    chrom_sizes: Dict[str, int]
) -> Tuple[Optional[GenomicInterval], Optional[GenomicInterval]]:
    """Get flanking regions of specified size around a transcript."""
    if len(transcript.blocks) == 0:
        raise ValueError("Transcript has no blocks")
    
    chrom_name = transcript.chrom
    if chrom_name not in chrom_sizes:
        return None, None
    
    chrom_size = chrom_sizes[chrom_name]
    
    transcript_start = transcript.blocks[0, 0]
    transcript_end = transcript.blocks[-1, 1]
    
    # Calculate left flank (chromosomally to the left)
    left_flank = None
    left_flank_start = max(0, transcript_start - flank_size)
    if left_flank_start < transcript_start:
        left_flank = GenomicInterval(
            chrom=chrom_name,
            start=left_flank_start,
            end=transcript_start,
            strand=transcript.strand,
            id=f"{transcript.id}_left_flank"
        )
    
    # Calculate right flank (chromosomally to the right)
    right_flank = None
    right_flank_end = min(chrom_size, transcript_end + flank_size)
    if transcript_end < right_flank_end:
        right_flank = GenomicInterval(
            chrom=chrom_name,
            start=transcript_end,
            end=right_flank_end,
            strand=transcript.strand,
            id=f"{transcript.id}_right_flank"
        )
    
    return left_flank, right_flank


def get_cds_blocks(transcript) -> np.ndarray:
    """Get CDS blocks from transcript using slice operations."""
    if not transcript.is_coding:
        return np.empty((0, 2), dtype=np.int32)

    from ..ops.interval_slicing import slice_intervals
    return slice_intervals(transcript.blocks, transcript.cds_start, transcript.cds_end)


def get_left_utr_blocks(transcript) -> np.ndarray:
    """Get UTR blocks to the left of CDS (chromosomally before CDS start)."""
    if not transcript.is_coding:
        return np.empty((0, 2), dtype=np.int32)

    span_start = transcript.blocks[0, 0]
    if span_start >= transcript.cds_start:
        return np.empty((0, 2), dtype=np.int32)
    
    from ..ops.interval_slicing import slice_intervals
    return slice_intervals(transcript.blocks, span_start, transcript.cds_start)


def get_right_utr_blocks(transcript) -> np.ndarray:
    """Get UTR blocks to the right of CDS (chromosomally after CDS end)."""
    if not transcript.is_coding:
        return np.empty((0, 2), dtype=np.int32)

    # Check if there's actually a right UTR region
    span_end = transcript.blocks[-1, 1]
    if transcript.cds_end >= span_end:
        return np.empty((0, 2), dtype=np.int32)
    
    from ..ops.interval_slicing import slice_intervals
    return slice_intervals(transcript.blocks, transcript.cds_end, span_end)


def get_utr5_blocks(transcript) -> np.ndarray:
    if transcript.strand == Strand.PLUS:
        return get_left_utr_blocks(transcript)
    elif transcript.strand == Strand.MINUS:
        return get_right_utr_blocks(transcript)
    else:
        # Unknown strand - default to left UTR blocks
        return get_left_utr_blocks(transcript)


def get_utr3_blocks(transcript) -> np.ndarray:
    if transcript.strand == Strand.PLUS:
        return get_right_utr_blocks(transcript)
    elif transcript.strand == Strand.MINUS:
        return get_left_utr_blocks(transcript)
    else:
        # Unknown strand - default to right UTR blocks  
        return get_right_utr_blocks(transcript)


def build_annotated_regions(transcript, chrom_sizes: dict, flank_size: int = 5000) -> AnnotatedIntervalSet:
    intervals = []
    region_types = []

    if transcript.is_coding:
        cds = transcript.cds_blocks
        intervals.append(cds)
        region_types.append(np.full(len(cds), RegionType.CDS, dtype=np.int8))

    utr5 = transcript.utr5_blocks
    if utr5.size > 0:
        intervals.append(utr5)
        region_types.append(np.full(len(utr5), RegionType.UTR5, dtype=np.int8))

    utr3 = transcript.utr3_blocks
    if utr3.size > 0:
        intervals.append(utr3)
        region_types.append(np.full(len(utr3), RegionType.UTR3, dtype=np.int8))

    flanks = compute_flanks(transcript, flank_size=flank_size, chrom_sizes=chrom_sizes)
    if flanks[0] is not None:
        intervals.append(np.array([[flanks[0].start, flanks[0].end]], dtype=np.int32))
        region_types.append(np.array([RegionType.FLANK_LEFT], dtype=np.int8))
    if flanks[1] is not None:
        intervals.append(np.array([[flanks[1].start, flanks[1].end]], dtype=np.int32))
        region_types.append(np.array([RegionType.FLANK_RIGHT], dtype=np.int8))

    span = transcript.transcript_cds_interval
    if span:
        intervals.append(np.array([[span.start, span.end]], dtype=np.int32))
        region_types.append(np.array([RegionType.GENE_SPAN], dtype=np.int8))

    all_intervals = np.vstack(intervals) if intervals else np.empty((0, 2), dtype=np.int32)
    all_labels = np.concatenate(region_types) if region_types else np.empty((0,), dtype=np.int8)

    return AnnotatedIntervalSet(intervals=all_intervals, region_types=all_labels)


def filter_transcripts_in_interval(transcripts_collection, interval: GenomicInterval, include_partial: bool = True):
    """Filter transcripts that are within or intersect with a genomic interval."""
    filtered_transcripts = []
    chrom_transcripts = [t for t in transcripts_collection.transcripts if t.chrom == interval.chrom]
    
    if not chrom_transcripts:
        from .genes import TranscriptsCollection
        return TranscriptsCollection(
            transcripts=[], 
            source_file=transcripts_collection.source_file
        )
    
    for transcript in chrom_transcripts:
        transcript_interval = transcript.transcript_interval
        
        if include_partial:
            if transcript_interval.intersects(interval):
                filtered_transcripts.append(transcript)
        else:
            if (transcript_interval.start >= interval.start and
                transcript_interval.end <= interval.end):
                filtered_transcripts.append(transcript)
    
    from .genes import TranscriptsCollection
    return TranscriptsCollection(
        transcripts=filtered_transcripts, 
        source_file=transcripts_collection.source_file
    )


def set_canonical_transcripts_for_collection(transcripts_collection, canonizer_func: Optional[Callable] = None, **kwargs) -> None:
    """Set canonical transcripts for all genes in a collection using a canonizer function."""
    if not transcripts_collection.has_gene_mapping:
        raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
    
    # Ensure genes cache is built
    if transcripts_collection._genes_cache is None:
        transcripts_collection._build_genes_cache()
    
    # Set canonical transcripts for all genes
    for gene in transcripts_collection._genes_cache.values():
        gene.apply_canonizer(canonizer_func, **kwargs)


def get_canonical_transcripts_from_collection(transcripts_collection, canonizer_func: Optional[Callable] = None, **kwargs):
    """Get a new collection containing only canonical transcripts."""
    if not transcripts_collection.has_gene_mapping:
        raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
    
    if canonizer_func is not None:
        set_canonical_transcripts_for_collection(transcripts_collection, canonizer_func, **kwargs)
    
    if transcripts_collection._genes_cache is None:
        transcripts_collection._build_genes_cache()
    
    canonical_transcripts = []
    for gene in transcripts_collection._genes_cache.values():
        canonical_transcript = gene.canonical_transcript
        if canonical_transcript is not None:
            canonical_transcripts.append(canonical_transcript)
    
    from .genes import TranscriptsCollection
    return TranscriptsCollection(
        transcripts=canonical_transcripts,
        source_file=transcripts_collection.source_file
    )


def get_canonical_transcripts_only_from_collection(transcripts_collection):
    """Get a new collection containing only already-set canonical transcripts."""
    if not transcripts_collection.has_gene_mapping:
        raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
    
    if transcripts_collection._genes_cache is None:
        transcripts_collection._build_genes_cache()
    
    canonical_transcripts = []
    for gene in transcripts_collection._genes_cache.values():
        canonical_transcript = gene.canonical_transcript
        if canonical_transcript is not None:
            canonical_transcripts.append(canonical_transcript)
    
    if not canonical_transcripts:
        print("Warning: No canonical transcripts found. Maybe you forgot to apply canonizer function using canonize_transcripts() method?")
    
    from .genes import TranscriptsCollection
    canonical_collection = TranscriptsCollection(
        transcripts=canonical_transcripts,
        source_file=transcripts_collection.source_file
    )
    
    if transcripts_collection._gene_data is not None:
        canonical_collection.bind_gene_data(transcripts_collection._gene_data)
    
    return canonical_collection


def get_genes_with_canonical_transcripts_from_collection(transcripts_collection) -> List:
    """Get all genes that have canonical transcripts set."""
    if not transcripts_collection.has_gene_mapping:
        raise ValueError("No gene data with gene-transcript mapping bound. Call bind_gene_data() first.")
    
    if transcripts_collection._genes_cache is None:
        transcripts_collection._build_genes_cache()
    
    return [gene for gene in transcripts_collection._genes_cache.values() if gene.has_canonical_transcript]
