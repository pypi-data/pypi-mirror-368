"""Amino acid sequence representations and storage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import numpy as np

from ..core_types import Metadata
from ..utils.amino_acid_encoding import (
    encode_amino_acids, decode_amino_acids,
    is_masked, apply_masking_aa, remove_masking_aa, GAPS, is_gap, is_stop
)


@dataclass(frozen=True)
class AminoAcidSequence:    
    data: np.ndarray  # int8 array with amino acid codes (preserves masking)
    metadata: Optional[Metadata] = None

    @classmethod
    def from_string(cls, sequence: str, metadata: Optional[Metadata] = None) -> 'AminoAcidSequence':
        data = encode_amino_acids(sequence)
        return cls(data=data, metadata=metadata)
    
    def to_string(self) -> str:
        return decode_amino_acids(self.data)
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        seq_preview = self.to_string()
        if len(seq_preview) > 30:
            seq_preview = seq_preview[:27] + "..."
        
        metadata_info = f", metadata={bool(self.metadata)}" if self.metadata else ""
        return f"AminoAcidSequence('{seq_preview}', len={len(self)}{metadata_info})"
    
    def remove_gaps(self) -> 'AminoAcidSequence':
        mask = ~np.array([is_gap(x) for x in self.data])
        return AminoAcidSequence(
            data=self.data[mask],
            metadata=self.metadata
        )

    def slice(self, start: int, end: int) -> 'AminoAcidSequence':
        return AminoAcidSequence(
            data=self.data[start:end],
            metadata=self.metadata
        )
    
    def reverse(self) -> 'AminoAcidSequence':
        return AminoAcidSequence(
            data=self.data[::-1],
            metadata=self.metadata
        )
    
    def apply_masking(self) -> 'AminoAcidSequence':
        return AminoAcidSequence(
            data=apply_masking_aa(self.data),
            metadata=self.metadata
        )

    def to_fasta_string(self, width: int = 80, header: Optional[str] = None) -> str:
        from ..ops.sequence_serialization import amino_acid_sequence_to_fasta_string
        return amino_acid_sequence_to_fasta_string(self, width=width, header=header)
    
    def remove_masking(self) -> 'AminoAcidSequence':
        return AminoAcidSequence(
            data=remove_masking_aa(self.data),
            metadata=self.metadata
        )
    
    def get_masked_positions(self) -> np.ndarray:
        """Get boolean array indicating which positions are masked."""
        return np.array([is_masked(x) for x in self.data])
    
    def get_gap_positions(self) -> np.ndarray:
        """Get boolean array indicating which positions are gaps."""
        return np.array([is_gap(x) for x in self.data])
    
    def get_stop_positions(self) -> np.ndarray:
        """Get boolean array indicating which positions are stop codons."""
        return np.array([is_stop(x) for x in self.data])
    
    def count_amino_acids(self) -> dict:
        """Count occurrences of each amino acid type (ignoring masking) using vectorized operations."""
        from .amino_acid_auxiliary import count_amino_acids_in_sequence
        return count_amino_acids_in_sequence(self)
    
    def get_amino_acid_content(self) -> dict:
        """Get amino acid composition as percentages."""
        from .amino_acid_auxiliary import get_amino_acid_composition
        return get_amino_acid_composition(self)

    def find_stop_codons(self) -> np.ndarray:
        """Find positions of stop codons in the sequence."""
        return np.where(self.get_stop_positions())[0]
    
    def molecular_weight(self) -> float:
        """Calculate approximate molecular weight in Daltons."""
        from .amino_acid_auxiliary import calculate_molecular_weight
        return calculate_molecular_weight(self)
