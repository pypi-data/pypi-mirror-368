"""Entity-specific operations for Transcripts and GenomeAlignments using low-level interval operations."""

import numpy as np
from typing import List
from ..core.genes import Transcript
from ..core.genome_alignment import GenomeAlignment
from .interval_slicing import slice_intervals, invert_intervals
from .interval_ops import merge_intervals, intersect_intervals, subtract_intervals


def get_transcript_cds_in_range(transcript: Transcript, start: int, end: int, 
                               use_numba: bool = True) -> np.ndarray:
    """Get CDS blocks within a specific genomic range using slice operations."""
    if not transcript.is_coding:
        return np.empty((0, 2), dtype=np.int32)
    
    cds_blocks = transcript.cds_blocks
    return slice_intervals(cds_blocks, start, end, use_numba=use_numba)


def get_transcript_utrs_in_range(transcript: Transcript, start: int, end: int,
                                utr_type: str = "both", use_numba: bool = True) -> np.ndarray:
    """Get UTR blocks within a specific genomic range."""
    if not transcript.is_coding:
        if utr_type in ["both", "5"]:
            # Non-coding transcript - all blocks are effectively UTR
            return slice_intervals(transcript.blocks, start, end, use_numba=use_numba)
        else:
            return np.empty((0, 2), dtype=np.int32)
    
    utr_blocks = []
    
    if utr_type in ["both", "5"]:
        utr5_blocks = transcript.utr5_blocks
        if len(utr5_blocks) > 0:
            sliced_utr5 = slice_intervals(utr5_blocks, start, end, use_numba=use_numba)
            if len(sliced_utr5) > 0:
                utr_blocks.append(sliced_utr5)
    
    if utr_type in ["both", "3"]:
        utr3_blocks = transcript.utr3_blocks
        if len(utr3_blocks) > 0:
            sliced_utr3 = slice_intervals(utr3_blocks, start, end, use_numba=use_numba)
            if len(sliced_utr3) > 0:
                utr_blocks.append(sliced_utr3)
    
    if utr_blocks:
        return np.vstack(utr_blocks)
    else:
        return np.empty((0, 2), dtype=np.int32)


def get_transcript_introns_in_range(transcript: Transcript, start: int, end: int,
                                   use_numba: bool = True) -> np.ndarray:
    """Get intron blocks within a specific genomic range."""
    introns = transcript.get_introns(use_numba=use_numba)
    return slice_intervals(introns, start, end, use_numba=use_numba)


def merge_transcript_cds(transcripts: List[Transcript], use_numba: bool = True) -> np.ndarray:
    """Merge CDS blocks from multiple transcripts."""
    if not transcripts:
        return np.empty((0, 2), dtype=np.int32)
    
    # Collect all CDS blocks
    all_cds = []
    for transcript in transcripts:
        if transcript.is_coding and len(transcript.cds_blocks) > 0:
            all_cds.append(transcript.cds_blocks)
    
    if not all_cds:
        return np.empty((0, 2), dtype=np.int32)
    
    # Concatenate and merge
    combined_cds = np.vstack(all_cds)
    return merge_intervals(combined_cds, use_numba=use_numba)


def merge_transcript_utrs(transcripts: List[Transcript], utr_type: str = "both",
                         use_numba: bool = True) -> np.ndarray:
    """Merge UTR blocks from multiple transcripts."""
    if not transcripts:
        return np.empty((0, 2), dtype=np.int32)
    
    all_utrs = []
    
    for transcript in transcripts:
        if utr_type in ["both", "5"]:
            utr5_blocks = transcript.utr5_blocks
            if len(utr5_blocks) > 0:
                all_utrs.append(utr5_blocks)
        
        if utr_type in ["both", "3"]:
            utr3_blocks = transcript.utr3_blocks
            if len(utr3_blocks) > 0:
                all_utrs.append(utr3_blocks)
    
    if not all_utrs:
        return np.empty((0, 2), dtype=np.int32)
    
    combined_utrs = np.vstack(all_utrs)
    return merge_intervals(combined_utrs, use_numba=use_numba)


def find_transcript_overlaps(transcript1: Transcript, transcript2: Transcript,
                           region_type: str = "exon", use_numba: bool = True) -> np.ndarray:
    """Find overlaps between specific regions of two transcripts."""
    blocks1 = _get_transcript_blocks_by_type(transcript1, region_type, use_numba)
    blocks2 = _get_transcript_blocks_by_type(transcript2, region_type, use_numba)
    
    if len(blocks1) == 0 or len(blocks2) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    return intersect_intervals(blocks1, blocks2, use_numba=use_numba)


def subtract_transcript_regions(transcript: Transcript, subtract_regions: np.ndarray,
                              region_type: str = "exon", use_numba: bool = True) -> np.ndarray:
    """Subtract regions from specific parts of a transcript."""
    blocks = _get_transcript_blocks_by_type(transcript, region_type, use_numba)
    
    if len(blocks) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    return subtract_intervals(blocks, subtract_regions, use_numba=use_numba)


def _get_transcript_blocks_by_type(transcript: Transcript, region_type: str,
                                  use_numba: bool = True) -> np.ndarray:
    if region_type == "exon":
        return transcript.blocks
    elif region_type == "cds":
        return transcript.cds_blocks
    elif region_type == "utr5":
        return transcript.utr5_blocks
    elif region_type == "utr3":
        return transcript.utr3_blocks
    elif region_type == "intron":
        return transcript.get_introns(use_numba=use_numba)
    else:
        raise ValueError(f"Unknown region_type: {region_type}")


def merge_genome_alignments(alignments: List[GenomeAlignment], 
                           space: str = "target", use_numba: bool = True) -> np.ndarray:
    """Merge blocks from multiple genome alignments."""
    if not alignments:
        return np.empty((0, 2), dtype=np.int32)
    all_blocks = []
    for alignment in alignments:
        if len(alignment.blocks) == 0:
            continue
            
        if space == "target":
            blocks = alignment.blocks[:, :2]  # t_start, t_end
        elif space == "query":
            blocks = alignment.blocks[:, 2:4]  # q_start, q_end
        else:
            raise ValueError("space must be 'target' or 'query'")
        
        all_blocks.append(blocks)
    
    if not all_blocks:
        return np.empty((0, 2), dtype=np.int32)
    
    combined_blocks = np.vstack(all_blocks)
    return merge_intervals(combined_blocks, use_numba=use_numba)


def find_alignment_gaps(alignment: GenomeAlignment, space: str = "target",
                       use_numba: bool = True) -> np.ndarray:
    """Find gaps in a genome alignment.
    
    Args:
        alignment: GenomeAlignment object
        space: "target" or "query" - which coordinate space to find gaps in
        use_numba: Whether to use numba-optimized operations
        
    Returns:
        Array of gap intervals
    """
    if len(alignment.blocks) <= 1:
        return np.empty((0, 2), dtype=np.int32)
    
    if space == "target":
        blocks = alignment.blocks[:, :2]  # t_start, t_end
        span = alignment.t_span
    elif space == "query":
        blocks = alignment.blocks[:, 2:4]  # q_start, q_end
        span = alignment.q_span
    else:
        raise ValueError("space must be 'target' or 'query'")
    
    return invert_intervals(blocks, span[0], span[1], use_numba=use_numba)


def intersect_alignment_with_intervals(alignment: GenomeAlignment, intervals: np.ndarray,
                                     space: str = "target", use_numba: bool = True) -> np.ndarray:
    """Find intersections between alignment blocks and given intervals.
    
    Args:
        alignment: GenomeAlignment object
        intervals: Array of intervals to intersect with, shape (N, 2)
        space: "target" or "query" - which coordinate space to use
        use_numba: Whether to use numba-optimized operations
        
    Returns:
        Array of intersection intervals
    """
    if len(alignment.blocks) == 0 or len(intervals) == 0:
        return np.empty((0, 2), dtype=np.int32)
    
    if space == "target":
        blocks = alignment.blocks[:, :2]  # t_start, t_end
    elif space == "query":
        blocks = alignment.blocks[:, 2:4]  # q_start, q_end
    else:
        raise ValueError("space must be 'target' or 'query'")
    
    return intersect_intervals(blocks, intervals, use_numba=use_numba) 