"""Auxiliary functions for sequences objects."""

import numpy as np
from typing import Optional
from ..utils.encoding import apply_masking, remove_masking


def mask_nucleotide_sequence_slice(sequence, start: Optional[int] = None, end: Optional[int] = None):
    if start is None:
        start = 0
    if end is None:
        end = len(sequence.data)
        
    if start < 0:
        start = max(0, len(sequence.data) + start)
    if end < 0:
        end = len(sequence.data) + end
    start = max(0, min(start, len(sequence.data)))
    end = max(start, min(end, len(sequence.data)))
    
    result_data = sequence.data.copy()
    slice_to_mask = result_data[start:end]
    masked_slice = apply_masking(slice_to_mask)
    result_data[start:end] = masked_slice
    
    from .nucleotide_sequences import NucleotideSequence
    return NucleotideSequence(
        data=result_data,
        is_rna=sequence.is_rna,
        metadata=sequence.metadata
    )


def unmask_nucleotide_sequence_slice(sequence, start: Optional[int] = None, end: Optional[int] = None):
    if start is None:
        start = 0
    if end is None:
        end = len(sequence.data)
        
    if start < 0:
        start = max(0, len(sequence.data) + start)
    if end < 0:
        end = len(sequence.data) + end
    start = max(0, min(start, len(sequence.data)))
    end = max(start, min(end, len(sequence.data)))
    
    result_data = sequence.data.copy()
    slice_to_unmask = result_data[start:end]
    unmasked_slice = remove_masking(slice_to_unmask)
    result_data[start:end] = unmasked_slice
    
    from .nucleotide_sequences import NucleotideSequence
    return NucleotideSequence(
        data=result_data,
        is_rna=sequence.is_rna,
        metadata=sequence.metadata
    )


def merge_nucleotide_sequences(sequence1, sequence2):
    if sequence1.is_rna != sequence2.is_rna:
        raise ValueError("Cannot merge DNA and RNA sequences")
    
    merged_data = np.concatenate([sequence1.data, sequence2.data])
    merged_metadata = None
    if sequence1.metadata is not None or sequence2.metadata is not None:
        merged_metadata = sequence1.metadata  # Keep first sequence's metadata for now
    
    from .nucleotide_sequences import NucleotideSequence
    return NucleotideSequence(
        data=merged_data,
        is_rna=sequence1.is_rna,
        metadata=merged_metadata
    )
