"""Transcript slicing operations."""

import numpy as np
from ..core.genes import Transcript
from .interval_slicing import slice_intervals, remove_intervals, invert_intervals


def slice_transcript(transcript: Transcript, start: int, end: int, use_numba: bool = True) -> Transcript:
    """Slice transcript to get only blocks that intersect with [start, end)."""
    sliced_blocks = slice_intervals(transcript.blocks, start, end, use_numba=use_numba)
    
    # Adjust CDS coordinates if present
    new_cds_start = None
    new_cds_end = None
    if transcript.is_coding:
        # Only keep CDS coordinates if they intersect with the slice
        if transcript.cds_end > start and transcript.cds_start < end:
            new_cds_start = max(transcript.cds_start, start)
            new_cds_end = min(transcript.cds_end, end)
    
    return Transcript(
        blocks=sliced_blocks,
        strand=transcript.strand,
        chrom=transcript.chrom,
        id=f"{transcript.id}_slice_{start}_{end}",
        cds_start=new_cds_start,
        cds_end=new_cds_end
    )


def get_transcript_introns(transcript: Transcript, use_numba: bool = True) -> np.ndarray:
    """Get intron blocks (gaps between exons) within transcript span."""
    if len(transcript.blocks) <= 1:
        return np.empty((0, 2), dtype=np.int32)
    
    span_start = transcript.blocks[0, 0]
    span_end = transcript.blocks[-1, 1]
    return invert_intervals(transcript.blocks, span_start, span_end, use_numba=use_numba)


def remove_transcript_region(transcript: Transcript, start: int, end: int, 
                           use_numba: bool = True) -> Transcript:
    """Remove a region from transcript, potentially splitting blocks.

    Args:
        transcript: Transcript object
        start: Start position to remove (inclusive)
        end: End position to remove (exclusive)
        use_numba: Whether to use numba-optimized operations

    Returns:
        New Transcript with region removed
    """
    new_blocks = remove_intervals(transcript.blocks, start, end, use_numba=use_numba)
    
    new_cds_start = transcript.cds_start
    new_cds_end = transcript.cds_end
    if transcript.is_coding:
        if transcript.cds_start >= end:
            new_cds_start = transcript.cds_start - (end - start)
            new_cds_end = transcript.cds_end - (end - start)
        elif transcript.cds_end <= start:
            pass
        else:
            new_cds_start = None
            new_cds_end = None
    
    return Transcript(
        blocks=new_blocks,
        strand=transcript.strand,
        chrom=transcript.chrom,
        id=f"{transcript.id}_removed_{start}_{end}",
        cds_start=new_cds_start,
        cds_end=new_cds_end
    )
