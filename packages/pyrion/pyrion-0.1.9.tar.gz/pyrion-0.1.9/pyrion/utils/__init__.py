"""Utility modules for pyrion."""

from .encoding import (
    ADENINE, GUANINE, THYMINE, URACIL, CYTOSINE, UNKNOWN, UNKNOWN_COMP,
    ADENINE_MASKED, GUANINE_MASKED, THYMINE_MASKED, URACIL_MASKED, 
    CYTOSINE_MASKED, UNKNOWN_MASKED, UNKNOWN_MASKED_COMP,
    GAP, FRAMESHIFT_1, FRAMESHIFT_1_COMP, FRAMESHIFT_1_MASKED, FRAMESHIFT_1_MASKED_COMP,
    
    # Helper functions
    complement, mask, unmask, is_masked, is_gap, is_frameshift,
    
    # Sets
    GAPS, FRAMESHIFTS, ALL_NUCLEOTIDES,
    
    # Encoding/decoding functions
    encode_nucleotides, decode_nucleotides,
    apply_complement, apply_masking, remove_masking, get_masking_status,
    
    # Tables
    NUCLEOTIDE_ENCODING, NUCLEOTIDE_DECODING, RNA_NUCLEOTIDE_DECODING
)

__all__ = [
    # Constants
    "ADENINE", "GUANINE", "THYMINE", "URACIL", "CYTOSINE", "UNKNOWN", "UNKNOWN_COMP",
    "ADENINE_MASKED", "GUANINE_MASKED", "THYMINE_MASKED", "URACIL_MASKED", 
    "CYTOSINE_MASKED", "UNKNOWN_MASKED", "UNKNOWN_MASKED_COMP",
    "GAP", "FRAMESHIFT_1", "FRAMESHIFT_1_COMP", "FRAMESHIFT_1_MASKED", "FRAMESHIFT_1_MASKED_COMP",
    
    # Helper functions
    "complement", "mask", "unmask", "is_masked", "is_gap", "is_frameshift",
    
    # Sets
    "GAPS", "FRAMESHIFTS", "ALL_NUCLEOTIDES",
    
    # Functions
    "encode_nucleotides", "decode_nucleotides", 
    "apply_complement", "apply_masking", "remove_masking", "get_masking_status",
    
    # Tables
    "NUCLEOTIDE_ENCODING", "NUCLEOTIDE_DECODING", "RNA_NUCLEOTIDE_DECODING"
] 