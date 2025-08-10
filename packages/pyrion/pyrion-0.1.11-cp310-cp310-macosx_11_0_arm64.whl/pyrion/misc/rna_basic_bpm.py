"""RNA basic binding potential matrix computation."""

import numpy as np
from typing import Optional
from ..core.nucleotide_sequences import NucleotideSequence
from ..utils.encoding import (
    ADENINE, GUANINE, THYMINE, URACIL, CYTOSINE, UNKNOWN,
    ADENINE_MASKED, GUANINE_MASKED, THYMINE_MASKED, URACIL_MASKED, 
    CYTOSINE_MASKED, UNKNOWN_MASKED,
    unmask, is_gap, is_masked
)



"""RNA basic binding potential matrix computation."""

import numpy as np
from typing import Optional
from ..core.nucleotide_sequences import NucleotideSequence
from ..utils.encoding import (
    ADENINE, GUANINE, THYMINE, URACIL, CYTOSINE, UNKNOWN,
    ADENINE_MASKED, GUANINE_MASKED, THYMINE_MASKED, URACIL_MASKED, 
    CYTOSINE_MASKED, UNKNOWN_MASKED,
    unmask, is_gap, is_masked
)


def _get_base_pair_score(nt1_code: int, nt2_code: int, is_rna: bool = True) -> float:
    """Get base pairing score between two nucleotides."""
    # Unmask if needed
    if is_masked(nt1_code):
        nt1_code = unmask(nt1_code)
    if is_masked(nt2_code):
        nt2_code = unmask(nt2_code)
    
    # Skip gaps and unknowns
    if is_gap(nt1_code) or is_gap(nt2_code):
        return 0.0
    if abs(nt1_code) == UNKNOWN:
        return 0.0
    
    # Canonical Watson-Crick pairs
    canonical_pairs = {
        (ADENINE, -URACIL),     # A-U (RNA)
        (GUANINE, -CYTOSINE),   # G-C
        (-URACIL, ADENINE),     # U-A (RNA)
        (-CYTOSINE, GUANINE),   # C-G
    }
    
    # Wobble pairs (G-U/T)
    wobble_pairs = {
        (GUANINE, -URACIL),     # G-U
        (-THYMINE, GUANINE),    # T-G
    }
    
    pair = (nt1_code, nt2_code)
    
    if pair in canonical_pairs:
        return 1.0
    elif pair in wobble_pairs:
        return 0.5
    else:
        return 0.0


def _can_form_stem(seq_data: np.ndarray, i: int, j: int, min_stem_size: int, is_rna: bool) -> float:
    """Check if positions i and j can form a stem of minimum size."""
    if j - i + 1 < min_stem_size:
        return 0.0
    
    scores = []
    
    # Check consecutive base pairs
    for k in range(min_stem_size):
        if i + k >= len(seq_data) or j - k < 0 or i + k >= j - k:
            return 0.0
        
        score = _get_base_pair_score(seq_data[i + k], seq_data[j - k], is_rna)
        if score == 0.0:  # No pairing possible
            return 0.0
        scores.append(score)
    
    return np.mean(scores)


def compute_rna_binding_potential_matrix(
    sequence: NucleotideSequence,
    min_loop_size: int = 5,
    min_stem_size: int = 4
) -> np.ndarray:
    """Compute RNA base pairing potential matrix."""
    seq_len = len(sequence)
    matrix = np.zeros((seq_len, seq_len), dtype=np.float32)
    
    # Iterate through all position pairs
    for i in range(seq_len):
        for j in range(i + min_loop_size + min_stem_size, seq_len):
            # Check if these positions can form a valid stem
            stem_score = _can_form_stem(sequence.data, i, j, min_stem_size, sequence.is_rna)
            if stem_score > 0:
                # Fill matrix symmetrically for the entire stem region
                for k in range(min_stem_size):
                    if i + k < seq_len and j - k >= 0:
                        pair_score = _get_base_pair_score(
                            sequence.data[i + k], 
                            sequence.data[j - k], 
                            sequence.is_rna
                        )
                        matrix[i + k, j - k] = pair_score
                        matrix[j - k, i + k] = pair_score  # Symmetric
    
    return matrix

"""
def _get_base_pair_score(nt1_code: int, nt2_code: int, is_rna: bool = True) -> float:
    # Unmask if needed
    if is_masked(nt1_code):
        nt1_code = unmask(nt1_code)
    if is_masked(nt2_code):
        nt2_code = unmask(nt2_code)
    
    # Skip gaps and unknowns
    if is_gap(nt1_code) or is_gap(nt2_code):
        return 0.0
    if abs(nt1_code) == UNKNOWN:
        return 0.0
    
    # Watson-Crick pairs: complements are just *-1 in pyrion encoding
    if nt1_code == -nt2_code:
        # G-C: 3 hydrogen bonds, A-U/T: 2 hydrogen bonds
        if abs(nt1_code) == GUANINE:  # G-C pair
            return 3.0
        elif abs(nt1_code) == ADENINE:  # A-U/T pair  
            return 2.0
    
    # Wobble pairs: G-U/T in either direction (1 hydrogen bond)
    # G=2, U/T=-1
    wobble_pairs = {
        (GUANINE, URACIL), (URACIL, GUANINE),     # (2,-1), (-1,2)
        (GUANINE, THYMINE), (THYMINE, GUANINE),   # (2,-1), (-1,2) - same as U
    }
    
    pair = (nt1_code, nt2_code)
    if pair in wobble_pairs:
        return 1.0
    
    return 0.0


def _can_form_stem(seq_data: np.ndarray, i: int, j: int, min_stem_size: int, is_rna: bool, min_stem_strength: float = 1.75) -> float:
    if j - i + 1 < min_stem_size:
        return 0.0
    
    scores = []
    
    # Check consecutive base pairs
    for k in range(min_stem_size):
        if i + k >= len(seq_data) or j - k < 0 or i + k >= j - k:
            return 0.0
        
        score = _get_base_pair_score(seq_data[i + k], seq_data[j - k], is_rna)
        if score == 0.0:  # No pairing possible
            return 0.0
        scores.append(score)
    
    avg_strength = np.mean(scores)
    
    # Check if stem meets minimum strength requirement
    if avg_strength < min_stem_strength:
        return 0.0
        
    return avg_strength


def compute_rna_binding_potential_matrix(
    sequence: NucleotideSequence,
    min_loop_size: int = 5,
    min_stem_size: int = 4,
    min_stem_strength: float = 1.75
) -> np.ndarray:

    seq_len = len(sequence)
    matrix = np.zeros((seq_len, seq_len), dtype=np.float32)
    
    # Iterate through all position pairs
    for i in range(seq_len):
        for j in range(i + min_loop_size + min_stem_size, seq_len):
            # Check if these positions can form a valid stem
            stem_score = _can_form_stem(sequence.data, i, j, min_stem_size, sequence.is_rna, min_stem_strength)
            if stem_score > 0:
                # Fill matrix symmetrically for the entire stem region
                for k in range(min_stem_size):
                    if i + k < seq_len and j - k >= 0:
                        pair_score = _get_base_pair_score(
                            sequence.data[i + k], 
                            sequence.data[j - k], 
                            sequence.is_rna
                        )
                        matrix[i + k, j - k] = pair_score
                        matrix[j - k, i + k] = pair_score  # Symmetric
    
    return matrix
"""