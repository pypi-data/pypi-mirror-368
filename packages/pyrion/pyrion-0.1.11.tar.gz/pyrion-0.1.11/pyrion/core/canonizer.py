"""Canonizer functions for selecting canonical transcripts from transcript lists."""

from typing import List, Optional
import numpy as np


def longest_isoform_canonizer(transcripts: List, **kwargs) -> Optional[str]:
    """Default canonizer that selects the transcript with the longest total exonic length."""
    if not transcripts:
        return None
    
    if len(transcripts) == 1:
        return transcripts[0].id
    
    max_length = 0
    canonical_transcript_id = None
    
    for transcript in transcripts:
        exon_lengths = transcript.blocks[:, 1] - transcript.blocks[:, 0]
        total_length = int(np.sum(exon_lengths))
        
        if total_length > max_length:
            max_length = total_length
            canonical_transcript_id = transcript.id
    
    return canonical_transcript_id


def longest_cds_canonizer(transcripts: List, **kwargs) -> Optional[str]:
    if not transcripts:
        return None
    
    coding_transcripts = [t for t in transcripts if t.is_coding]
    
    if not coding_transcripts:
        return longest_isoform_canonizer(transcripts, **kwargs)
    
    if len(coding_transcripts) == 1:
        return coding_transcripts[0].id

    max_cds_length = 0
    canonical_transcript_id = None
    
    for transcript in coding_transcripts:
        cds_blocks = transcript.cds_blocks
        if len(cds_blocks) > 0:
            cds_lengths = cds_blocks[:, 1] - cds_blocks[:, 0]
            total_cds_length = int(np.sum(cds_lengths))
            
            if total_cds_length > max_cds_length:
                max_cds_length = total_cds_length
                canonical_transcript_id = transcript.id
    
    return canonical_transcript_id


def longest_transcript_span_canonizer(transcripts: List, **kwargs) -> Optional[str]:
    if not transcripts:
        return None
    
    if len(transcripts) == 1:
        return transcripts[0].id
    
    max_span = 0
    canonical_transcript_id = None
    
    for transcript in transcripts:
        span = transcript.blocks[-1, 1] - transcript.blocks[0, 0]
        
        if span > max_span:
            max_span = span
            canonical_transcript_id = transcript.id
    
    return canonical_transcript_id


def first_transcript_canonizer(transcripts: List, **kwargs) -> Optional[str]:
    if not transcripts:
        return None
    return transcripts[0].id


def most_exons_canonizer(transcripts: List, **kwargs) -> Optional[str]:
    if not transcripts:
        return None
    
    if len(transcripts) == 1:
        return transcripts[0].id
    
    # Find transcript with most exons
    max_exons = 0
    canonical_transcript_id = None
    
    for transcript in transcripts:
        num_exons = len(transcript.blocks)
        
        if num_exons > max_exons:
            max_exons = num_exons
            canonical_transcript_id = transcript.id
    
    return canonical_transcript_id

DEFAULT_CANONIZER = longest_isoform_canonizer
