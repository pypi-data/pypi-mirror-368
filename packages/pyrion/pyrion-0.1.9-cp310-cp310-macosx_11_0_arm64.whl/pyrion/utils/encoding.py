"""Encoding utilities for nucleotides using multiplicative semantics."""

import numpy as np
from typing import Dict, Set

# Unmasked nucleotides (uppercase)
ADENINE = 1             # A = +1 (purine)
GUANINE = 2             # G = +2 (purine)  
THYMINE = -1            # T = -1 (pyrimidine)
URACIL = -1             # U = -1 (RNA pyrimidine, same as T)
CYTOSINE = -2           # C = -2 (pyrimidine)
UNKNOWN = 3             # N = +3 (self-complementary)
UNKNOWN_COMP = -3       # N = -3 (complement form)

# Masked nucleotides (lowercase) - multiply by 5
ADENINE_MASKED = 5      # a = +5 (1 × 5)
GUANINE_MASKED = 10     # g = +10 (2 × 5)
THYMINE_MASKED = -5     # t = -5 (-1 × 5)
URACIL_MASKED = -5      # u = -5 (-1 × 5, same as t)
CYTOSINE_MASKED = -10   # c = -10 (-2 × 5)
UNKNOWN_MASKED = 15     # n = +15 (3 × 5)
UNKNOWN_MASKED_COMP = -15  # n = -15 (-3 × 5)

# Gaps (neutral under multiplication)
GAP = 0

# Frameshifts (self-complementary, masking doesn't affect semantics)
FRAMESHIFT_1 = 13
FRAMESHIFT_1_COMP = -13
FRAMESHIFT_1_MASKED = 65
FRAMESHIFT_1_MASKED_COMP = -65

def complement(code: int) -> int:
    """Get complement by multiplying by -1."""
    return -code

def mask(code: int) -> int:
    """Apply masking by multiplying by 5."""
    if code == 0:  # Gaps remain neutral
        return 0
    return code * 5

def unmask(code: int) -> int:
    """Remove masking by dividing by 5."""
    if code == 0:  # Gaps remain neutral
        return 0
    if abs(code) % 5 == 0:
        return code // 5
    return code

def is_masked(code: int) -> bool:
    """Check if nucleotide is masked using multiplicative test."""
    return abs(code) % 5 == 0 and code != 0

def is_gap(code: int) -> bool:
    """Check if code represents a gap."""
    return code == 0

def is_frameshift(code: int) -> bool:
    """Check if code represents a frameshift."""
    return abs(code) in {13, 65}

GAPS: Set[int] = {GAP}

FRAMESHIFTS: Set[int] = {
    FRAMESHIFT_1, FRAMESHIFT_1_COMP, 
    FRAMESHIFT_1_MASKED, FRAMESHIFT_1_MASKED_COMP
}

ALL_NUCLEOTIDES: Set[int] = {
    ADENINE, GUANINE, THYMINE, CYTOSINE, UNKNOWN, UNKNOWN_COMP,
    ADENINE_MASKED, GUANINE_MASKED, THYMINE_MASKED, CYTOSINE_MASKED,
    UNKNOWN_MASKED, UNKNOWN_MASKED_COMP
}

# Encoding table: character -> code
NUCLEOTIDE_ENCODING: Dict[str, int] = {
    # Unmasked (uppercase)
    'A': ADENINE,           # +1
    'G': GUANINE,           # +2
    'T': THYMINE,           # -1
    'U': URACIL,            # -1 (RNA)
    'C': CYTOSINE,          # -2
    'N': UNKNOWN,           # +3
    '-': GAP,               # 0
    
    # Masked (lowercase)
    'a': ADENINE_MASKED,    # +5
    'g': GUANINE_MASKED,    # +10
    't': THYMINE_MASKED,    # -5
    'u': URACIL_MASKED,     # -5 (RNA)
    'c': CYTOSINE_MASKED,   # -10
    'n': UNKNOWN_MASKED,    # +15
    
    # Frameshifts
    '!': FRAMESHIFT_1,      # +13
}

# Decoding table: code -> character (DNA)
NUCLEOTIDE_DECODING: Dict[int, str] = {
    # Unmasked
    ADENINE: 'A',           # 1 -> A
    GUANINE: 'G',           # 2 -> G
    THYMINE: 'T',           # -1 -> T
    CYTOSINE: 'C',          # -2 -> C
    UNKNOWN: 'N',           # 3 -> N
    UNKNOWN_COMP: 'N',      # -3 -> N
    GAP: '-',               # 0 -> -
    
    # Masked
    ADENINE_MASKED: 'a',    # 5 -> a
    GUANINE_MASKED: 'g',    # 10 -> g
    THYMINE_MASKED: 't',    # -5 -> t
    CYTOSINE_MASKED: 'c',   # -10 -> c
    UNKNOWN_MASKED: 'n',    # 15 -> n
    UNKNOWN_MASKED_COMP: 'n',  # -15 -> n
    
    # Frameshifts
    FRAMESHIFT_1: '!',      # 13 -> !
    FRAMESHIFT_1_COMP: '!', # -13 -> !
    FRAMESHIFT_1_MASKED: '!',     # 65 -> !
    FRAMESHIFT_1_MASKED_COMP: '!', # -65 -> !
}

# RNA decoding table: code -> character (RNA, T->U)
RNA_NUCLEOTIDE_DECODING: Dict[int, str] = {
    # Unmasked RNA
    ADENINE: 'A',           # 1 -> A
    GUANINE: 'G',           # 2 -> G
    URACIL: 'U',            # -1 -> U (instead of T)
    CYTOSINE: 'C',          # -2 -> C
    UNKNOWN: 'N',           # 3 -> N
    UNKNOWN_COMP: 'N',      # -3 -> N
    GAP: '-',               # 0 -> -
    
    # Masked RNA
    ADENINE_MASKED: 'a',    # 5 -> a
    GUANINE_MASKED: 'g',    # 10 -> g
    URACIL_MASKED: 'u',     # -5 -> u (instead of t)
    CYTOSINE_MASKED: 'c',   # -10 -> c
    UNKNOWN_MASKED: 'n',    # 15 -> n
    UNKNOWN_MASKED_COMP: 'n',  # -15 -> n
    
    # Frameshifts (same as DNA)
    FRAMESHIFT_1: '!',
    FRAMESHIFT_1_COMP: '!',
    FRAMESHIFT_1_MASKED: '!',
    FRAMESHIFT_1_MASKED_COMP: '!',
}


def encode_nucleotides(sequence: str) -> np.ndarray:
    """Encode nucleotide sequence to int8 array using multiplicative semantics."""
    encoded = np.array([NUCLEOTIDE_ENCODING.get(nt, UNKNOWN) for nt in sequence], dtype=np.int8)
    return encoded


def decode_nucleotides(encoded: np.ndarray, is_rna: bool = False) -> str:
    """Decode int8 array to nucleotide sequence using multiplicative semantics."""
    decoding_table = RNA_NUCLEOTIDE_DECODING if is_rna else NUCLEOTIDE_DECODING
    decoded = ''.join(decoding_table.get(int(code), 'N') for code in encoded)
    return decoded


def apply_complement(encoded: np.ndarray) -> np.ndarray:
    """Apply complement using multiplicative semantics (multiply by -1)."""
    return encoded * -1


def apply_masking(encoded: np.ndarray) -> np.ndarray:
    """Apply masking using multiplicative semantics (multiply by 5, gaps stay 0)."""
    result = encoded.copy()
    non_gap_mask = encoded != 0
    result[non_gap_mask] *= 5
    return result


def remove_masking(encoded: np.ndarray) -> np.ndarray:
    """Remove masking using multiplicative semantics."""
    result = encoded.copy()
    # Only unmask if actually masked (divisible by 5 and not 0)
    masked_mask = (np.abs(encoded) % 5 == 0) & (encoded != 0)
    result[masked_mask] //= 5
    return result


def get_masking_status(encoded: np.ndarray) -> np.ndarray:
    """Get boolean array indicating which positions are masked."""
    return (np.abs(encoded) % 5 == 0) & (encoded != 0)
