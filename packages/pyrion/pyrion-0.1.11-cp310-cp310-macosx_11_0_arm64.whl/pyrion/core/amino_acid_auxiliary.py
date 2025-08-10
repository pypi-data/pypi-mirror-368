"""Auxiliary functions for amino acid sequence objects."""

import numpy as np
from typing import Dict
from ..utils.amino_acid_encoding import AMINO_ACID_DECODING, remove_masking_aa


def count_amino_acids_in_sequence(sequence) -> Dict[str, int]:
    """Count occurrences of each amino acid type (ignoring masking)."""
    unmasked_data = remove_masking_aa(sequence.data)
    unique_codes, counts = np.unique(unmasked_data, return_counts=True)
    
    result = {}
    for code, count in zip(unique_codes, counts):
        aa = AMINO_ACID_DECODING.get(int(code), 'X')
        result[aa] = int(count)
        
    return result


def calculate_molecular_weight(sequence) -> float:
    """Calculate approximate molecular weight in Daltons."""
    weights = {
        'A': 71.04, 'R': 156.10, 'N': 114.04, 'D': 115.03, 'C': 103.01,
        'E': 129.04, 'Q': 128.06, 'G': 57.02, 'H': 137.06, 'I': 113.08,
        'L': 113.08, 'K': 128.09, 'M': 131.04, 'F': 147.07, 'P': 97.05,
        'S': 87.03, 'T': 101.05, 'W': 186.08, 'Y': 163.06, 'V': 99.07,
        'B': 114.53, 'Z': 128.55, 'J': 113.08, 'U': 150.95, 'O': 255.15,
        'X': 110.0  # Average amino acid weight
    }
    
    counts = count_amino_acids_in_sequence(sequence)
    total_weight = sum(weights.get(aa, 110.0) * count for aa, count in counts.items() if aa != '-' and aa != '*')
    
    # Subtract water molecules for peptide bonds (n-1 peptide bonds for n amino acids)
    non_gap_non_stop = sum(count for aa, count in counts.items() if aa not in ['-', '*'])
    if non_gap_non_stop > 1:
        total_weight -= (non_gap_non_stop - 1) * 18.015  # Water molecular weight
        
    return max(0.0, total_weight)


def get_amino_acid_composition(sequence) -> Dict[str, float]:
    counts = count_amino_acids_in_sequence(sequence)
    total = sum(counts.values())
    
    if total == 0:
        return {}
        
    return {aa: (count / total) * 100 for aa, count in counts.items()}
