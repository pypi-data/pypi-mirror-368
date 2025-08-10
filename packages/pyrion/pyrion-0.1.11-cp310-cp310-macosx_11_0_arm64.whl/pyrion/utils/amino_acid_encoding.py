"""Amino acid encoding utilities using prime-based multiplicative semantics."""

import numpy as np
from typing import Dict, Set

# Prime-based amino acid encoding scheme:
# - Standard amino acids: positive prime numbers
# - Masking (lowercase): multiply by -1
# - Gaps: 0 (neutral under multiplication)
# - Stop codon: 1 and -1 (neutral to masking operations)
# - All values must fit in int8 range (-128 to 127)

# Stop codon (neutral to masking)
STOP = 1                    # * = +1 (stop codon)
STOP_MASKED = -1           # * = -1 (masked stop codon)

# Standard amino acids as prime numbers (uppercase)
ALANINE = 2                # A = 2
ARGININE = 3               # R = 3
ASPARAGINE = 5             # N = 5
ASPARTIC_ACID = 7          # D = 7
CYSTEINE = 11              # C = 11
GLUTAMIC_ACID = 13         # E = 13
GLUTAMINE = 17             # Q = 17
GLYCINE = 19               # G = 19
HISTIDINE = 23             # H = 23
ISOLEUCINE = 29            # I = 29
LEUCINE = 31               # L = 31
LYSINE = 37                # K = 37
METHIONINE = 41            # M = 41
PHENYLALANINE = 43         # F = 43
PROLINE = 47               # P = 47
SERINE = 53                # S = 53
THREONINE = 59             # T = 59
TRYPTOPHAN = 61            # W = 61
TYROSINE = 67              # Y = 67
VALINE = 71                # V = 71

# Ambiguous amino acids
ASPARAGINE_OR_ASPARTIC = 73     # B = 73 (N or D)
GLUTAMINE_OR_GLUTAMIC = 79      # Z = 79 (Q or E)
LEUCINE_OR_ISOLEUCINE = 83      # J = 83 (L or I)

# Special amino acids (rare)
SELENOCYSTEINE = 89        # U = 89 (rare)
PYRROLYSINE = 97           # O = 97 (rare)

# Unknown amino acid
UNKNOWN_AMINO_ACID = 101   # X = 101

# Masked amino acids (lowercase) - multiply by -1
ALANINE_MASKED = -2               # a = -2
ARGININE_MASKED = -3              # r = -3
ASPARAGINE_MASKED = -5            # n = -5
ASPARTIC_ACID_MASKED = -7         # d = -7
CYSTEINE_MASKED = -11             # c = -11
GLUTAMIC_ACID_MASKED = -13        # e = -13
GLUTAMINE_MASKED = -17            # q = -17
GLYCINE_MASKED = -19              # g = -19
HISTIDINE_MASKED = -23            # h = -23
ISOLEUCINE_MASKED = -29           # i = -29
LEUCINE_MASKED = -31              # l = -31
LYSINE_MASKED = -37               # k = -37
METHIONINE_MASKED = -41           # mm39.chrM.2bit = -41
PHENYLALANINE_MASKED = -43        # f = -43
PROLINE_MASKED = -47              # p = -47
SERINE_MASKED = -53               # s = -53
THREONINE_MASKED = -59            # t = -59
TRYPTOPHAN_MASKED = -61           # w = -61
TYROSINE_MASKED = -67             # y = -67
VALINE_MASKED = -71               # v = -71

# Ambiguous amino acids (masked)
ASPARAGINE_OR_ASPARTIC_MASKED = -73    # b = -73
GLUTAMINE_OR_GLUTAMIC_MASKED = -79     # z = -79
LEUCINE_OR_ISOLEUCINE_MASKED = -83     # j = -83

# Special amino acids (masked)
SELENOCYSTEINE_MASKED = -89       # u = -89
PYRROLYSINE_MASKED = -97          # o = -97
UNKNOWN_AMINO_ACID_MASKED = -101  # x = -101

# Gaps
GAP = 0

# Helper functions for multiplicative semantics
def mask(code: int) -> int:
    """Apply masking by multiplying by -1."""
    if code == 0:  # Gaps remain neutral
        return 0
    return code * -1

def unmask(code: int) -> int:
    """Remove masking by taking absolute value."""
    return abs(code)

def is_masked(code: int) -> bool:
    """Check if amino acid is masked (negative and not 0)."""
    return code < 0

def is_gap(code: int) -> bool:
    """Check if code represents a gap."""
    return code == 0

def is_stop(code: int) -> bool:
    """Check if code represents a stop codon."""
    return abs(code) == 1

def is_unknown(code: int) -> bool:
    """Check if code represents an unknown amino acid."""
    return abs(code) == UNKNOWN_AMINO_ACID

# Predefined sets for efficient checking
GAPS: Set[int] = {GAP}

STOP_CODONS: Set[int] = {STOP, STOP_MASKED}

ALL_AMINO_ACIDS: Set[int] = {
    ALANINE, ARGININE, ASPARAGINE, ASPARTIC_ACID, CYSTEINE,
    GLUTAMIC_ACID, GLUTAMINE, GLYCINE, HISTIDINE, ISOLEUCINE,
    LEUCINE, LYSINE, METHIONINE, PHENYLALANINE, PROLINE,
    SERINE, THREONINE, TRYPTOPHAN, TYROSINE, VALINE,
    ASPARAGINE_OR_ASPARTIC, GLUTAMINE_OR_GLUTAMIC, LEUCINE_OR_ISOLEUCINE,
    SELENOCYSTEINE, PYRROLYSINE, UNKNOWN_AMINO_ACID,
    ALANINE_MASKED, ARGININE_MASKED, ASPARAGINE_MASKED, ASPARTIC_ACID_MASKED,
    CYSTEINE_MASKED, GLUTAMIC_ACID_MASKED, GLUTAMINE_MASKED, GLYCINE_MASKED,
    HISTIDINE_MASKED, ISOLEUCINE_MASKED, LEUCINE_MASKED, LYSINE_MASKED,
    METHIONINE_MASKED, PHENYLALANINE_MASKED, PROLINE_MASKED, SERINE_MASKED,
    THREONINE_MASKED, TRYPTOPHAN_MASKED, TYROSINE_MASKED, VALINE_MASKED,
    ASPARAGINE_OR_ASPARTIC_MASKED, GLUTAMINE_OR_GLUTAMIC_MASKED,
    LEUCINE_OR_ISOLEUCINE_MASKED, SELENOCYSTEINE_MASKED, PYRROLYSINE_MASKED,
    UNKNOWN_AMINO_ACID_MASKED
}

# Encoding table: character -> code
AMINO_ACID_ENCODING: Dict[str, int] = {
    # Stop codon
    '*': STOP,                # +1
    
    # Standard amino acids (uppercase)
    'A': ALANINE,             # +2
    'R': ARGININE,            # +3
    'N': ASPARAGINE,          # +5
    'D': ASPARTIC_ACID,       # +7
    'C': CYSTEINE,            # +11
    'E': GLUTAMIC_ACID,       # +13
    'Q': GLUTAMINE,           # +17
    'G': GLYCINE,             # +19
    'H': HISTIDINE,           # +23
    'I': ISOLEUCINE,          # +29
    'L': LEUCINE,             # +31
    'K': LYSINE,              # +37
    'M': METHIONINE,          # +41
    'F': PHENYLALANINE,       # +43
    'P': PROLINE,             # +47
    'S': SERINE,              # +53
    'T': THREONINE,           # +59
    'W': TRYPTOPHAN,          # +61
    'Y': TYROSINE,            # +67
    'V': VALINE,              # +71
    
    # Ambiguous amino acids
    'B': ASPARAGINE_OR_ASPARTIC,    # +73
    'Z': GLUTAMINE_OR_GLUTAMIC,     # +79
    'J': LEUCINE_OR_ISOLEUCINE,     # +83
    
    # Special amino acids
    'U': SELENOCYSTEINE,      # +89
    'O': PYRROLYSINE,         # +97
    'X': UNKNOWN_AMINO_ACID,  # +101
    
    # Gaps
    '-': GAP,                 # 0
    
    # Masked amino acids (lowercase)
    'a': ALANINE_MASKED,             # -2
    'r': ARGININE_MASKED,            # -3
    'n': ASPARAGINE_MASKED,          # -5
    'd': ASPARTIC_ACID_MASKED,       # -7
    'c': CYSTEINE_MASKED,            # -11
    'e': GLUTAMIC_ACID_MASKED,       # -13
    'q': GLUTAMINE_MASKED,           # -17
    'g': GLYCINE_MASKED,             # -19
    'h': HISTIDINE_MASKED,           # -23
    'i': ISOLEUCINE_MASKED,          # -29
    'l': LEUCINE_MASKED,             # -31
    'k': LYSINE_MASKED,              # -37
    'mm39.chrM.2bit': METHIONINE_MASKED,          # -41
    'f': PHENYLALANINE_MASKED,       # -43
    'p': PROLINE_MASKED,             # -47
    's': SERINE_MASKED,              # -53
    't': THREONINE_MASKED,           # -59
    'w': TRYPTOPHAN_MASKED,          # -61
    'y': TYROSINE_MASKED,            # -67
    'v': VALINE_MASKED,              # -71
    
    # Ambiguous amino acids (masked)
    'b': ASPARAGINE_OR_ASPARTIC_MASKED,  # -73
    'z': GLUTAMINE_OR_GLUTAMIC_MASKED,   # -79
    'j': LEUCINE_OR_ISOLEUCINE_MASKED,   # -83
    
    # Special amino acids (masked)
    'u': SELENOCYSTEINE_MASKED,      # -89
    'o': PYRROLYSINE_MASKED,         # -97
    'x': UNKNOWN_AMINO_ACID_MASKED,  # -101
}

# Decoding table: code -> character
AMINO_ACID_DECODING: Dict[int, str] = {
    # Stop codon
    STOP: '*',                # 1 -> *
    STOP_MASKED: '*',         # -1 -> *
    
    # Standard amino acids
    ALANINE: 'A',             # 2 -> A
    ARGININE: 'R',            # 3 -> R
    ASPARAGINE: 'N',          # 5 -> N
    ASPARTIC_ACID: 'D',       # 7 -> D
    CYSTEINE: 'C',            # 11 -> C
    GLUTAMIC_ACID: 'E',       # 13 -> E
    GLUTAMINE: 'Q',           # 17 -> Q
    GLYCINE: 'G',             # 19 -> G
    HISTIDINE: 'H',           # 23 -> H
    ISOLEUCINE: 'I',          # 29 -> I
    LEUCINE: 'L',             # 31 -> L
    LYSINE: 'K',              # 37 -> K
    METHIONINE: 'M',          # 41 -> M
    PHENYLALANINE: 'F',       # 43 -> F
    PROLINE: 'P',             # 47 -> P
    SERINE: 'S',              # 53 -> S
    THREONINE: 'T',           # 59 -> T
    TRYPTOPHAN: 'W',          # 61 -> W
    TYROSINE: 'Y',            # 67 -> Y
    VALINE: 'V',              # 71 -> V
    
    # Ambiguous amino acids
    ASPARAGINE_OR_ASPARTIC: 'B',    # 73 -> B
    GLUTAMINE_OR_GLUTAMIC: 'Z',     # 79 -> Z
    LEUCINE_OR_ISOLEUCINE: 'J',     # 83 -> J
    
    # Special amino acids
    SELENOCYSTEINE: 'U',      # 89 -> U
    PYRROLYSINE: 'O',         # 97 -> O
    UNKNOWN_AMINO_ACID: 'X',  # 101 -> X
    
    # Gaps
    GAP: '-',                 # 0 -> -
    
    # Masked amino acids (lowercase)
    ALANINE_MASKED: 'a',             # -2 -> a
    ARGININE_MASKED: 'r',            # -3 -> r
    ASPARAGINE_MASKED: 'n',          # -5 -> n
    ASPARTIC_ACID_MASKED: 'd',       # -7 -> d
    CYSTEINE_MASKED: 'c',            # -11 -> c
    GLUTAMIC_ACID_MASKED: 'e',       # -13 -> e
    GLUTAMINE_MASKED: 'q',           # -17 -> q
    GLYCINE_MASKED: 'g',             # -19 -> g
    HISTIDINE_MASKED: 'h',           # -23 -> h
    ISOLEUCINE_MASKED: 'i',          # -29 -> i
    LEUCINE_MASKED: 'l',             # -31 -> l
    LYSINE_MASKED: 'k',              # -37 -> k
    METHIONINE_MASKED: 'mm39.chrM.2bit',          # -41 -> mm39.chrM.2bit
    PHENYLALANINE_MASKED: 'f',       # -43 -> f
    PROLINE_MASKED: 'p',             # -47 -> p
    SERINE_MASKED: 's',              # -53 -> s
    THREONINE_MASKED: 't',           # -59 -> t
    TRYPTOPHAN_MASKED: 'w',          # -61 -> w
    TYROSINE_MASKED: 'y',            # -67 -> y
    VALINE_MASKED: 'v',              # -71 -> v
    
    # Ambiguous amino acids (masked)
    ASPARAGINE_OR_ASPARTIC_MASKED: 'b',  # -73 -> b
    GLUTAMINE_OR_GLUTAMIC_MASKED: 'z',   # -79 -> z
    LEUCINE_OR_ISOLEUCINE_MASKED: 'j',   # -83 -> j
    
    # Special amino acids (masked)
    SELENOCYSTEINE_MASKED: 'u',      # -89 -> u
    PYRROLYSINE_MASKED: 'o',         # -97 -> o
    UNKNOWN_AMINO_ACID_MASKED: 'x',  # -101 -> x
}


def encode_amino_acids(sequence: str) -> np.ndarray:
    """Encode amino acid sequence to int8 array using prime-based multiplicative semantics."""
    encoded = []
    for aa in sequence:
        code = AMINO_ACID_ENCODING.get(aa)
        if code is None:
            code = UNKNOWN_AMINO_ACID
        encoded.append(code)
    return np.array(encoded, dtype=np.int8)


def decode_amino_acids(encoded: np.ndarray) -> str:
    """Decode int8 array to amino acid sequence using prime-based multiplicative semantics."""
    decoded = ''.join(AMINO_ACID_DECODING.get(int(code), 'X') for code in encoded)
    return decoded


def apply_masking_aa(encoded: np.ndarray) -> np.ndarray:
    """Apply masking using multiplicative semantics (multiply by -1, gaps stay 0)."""
    result = encoded.copy()
    non_gap_mask = encoded != 0
    result[non_gap_mask] *= -1
    return result


def remove_masking_aa(encoded: np.ndarray) -> np.ndarray:
    """Remove masking using multiplicative semantics (take absolute value)."""
    result = encoded.copy()
    masked_mask = encoded < 0
    result[masked_mask] = np.abs(result[masked_mask])
    return result


def get_masking_status_aa(encoded: np.ndarray) -> np.ndarray:
    """Get boolean array indicating which positions are masked."""
    return encoded < 0 