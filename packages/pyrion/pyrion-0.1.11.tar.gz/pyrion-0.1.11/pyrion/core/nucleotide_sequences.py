"""Sequence representations and storage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from enum import Enum
import numpy as np

from ..core_types import Metadata
from ..utils.encoding import (
    encode_nucleotides, decode_nucleotides, apply_complement,
    is_masked, apply_masking, remove_masking, GAPS, is_gap
)


class SequenceType(Enum):
    """Sequence type detection."""
    DNA = "dna"
    RNA = "rna"
    PROTEIN = "protein" 


@dataclass(frozen=True)
class NucleotideSequence:
    data: np.ndarray  # int8 array with nucleotide codes (preserves masking)
    is_rna: bool = False
    metadata: Optional[Metadata] = None

    @classmethod
    def from_string(cls, sequence: str, is_rna: bool = False, metadata: Optional[Metadata] = None) -> 'NucleotideSequence':
        data = encode_nucleotides(sequence)
        return cls(data=data, is_rna=is_rna, metadata=metadata)
    
    def to_string(self) -> str:
        return decode_nucleotides(self.data, is_rna=self.is_rna)
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        seq_preview = self.to_string()
        if len(seq_preview) > 50:
            seq_preview = seq_preview[:47] + "..."
        
        seq_type = "RNA" if self.is_rna else "DNA"
        metadata_info = f", metadata={bool(self.metadata)}" if self.metadata else ""
        return f"NucleotideSequence('{seq_preview}', len={len(self)}, type={seq_type}{metadata_info})"
    
    def remove_gaps(self) -> 'NucleotideSequence':
        mask = ~np.array([is_gap(x) for x in self.data])
        return NucleotideSequence(
            data=self.data[mask],
            is_rna=self.is_rna,
            metadata=self.metadata
        )

    def slice(self, start: int, end: int) -> 'NucleotideSequence':
        return NucleotideSequence(
            data=self.data[start:end],
            is_rna=self.is_rna,
            metadata=self.metadata
        )
    
    def reverse(self) -> 'NucleotideSequence':
        return NucleotideSequence(
            data=self.data[::-1],
            is_rna=self.is_rna,
            metadata=self.metadata
        )
    
    def complement(self) -> 'NucleotideSequence':
        return NucleotideSequence(
            data=apply_complement(self.data),
            is_rna=self.is_rna,
            metadata=self.metadata
        )
    

    def toggle_type(self) -> 'NucleotideSequence':
        """Toggle between DNA and RNA (T <-> U)."""
        return NucleotideSequence(
            data=self.data.copy(),
            is_rna=not self.is_rna,
            metadata=self.metadata
        )
    
    def to_codons(self):
        from .codons import CodonSequence
        return CodonSequence(self)

    def to_amino_acids(self, translation_table=None):
        from .codons import CodonSequence
        return CodonSequence(self).translate(translation_table)

    def to_fasta_string(self, width: int = 80, header: Optional[str] = None) -> str:
        from ..ops.sequence_serialization import nucleotide_sequence_to_fasta_string
        return nucleotide_sequence_to_fasta_string(self, width=width, header=header)

    def reverse_complement(self) -> 'NucleotideSequence':
        rc_data = apply_complement(self.data[::-1])  # Reverse then complement
        return NucleotideSequence(
            data=rc_data,
            is_rna=self.is_rna,
            metadata=self.metadata
        )
    
    def merge(self, other: 'NucleotideSequence') -> 'NucleotideSequence':
        from .sequences_auxiliary import merge_nucleotide_sequences
        return merge_nucleotide_sequences(self, other)
    
    def mask(self, start: Optional[int] = None, end: Optional[int] = None) -> 'NucleotideSequence':
        from .sequences_auxiliary import mask_nucleotide_sequence_slice
        return mask_nucleotide_sequence_slice(self, start, end)
    
    def unmask(self, start: Optional[int] = None, end: Optional[int] = None) -> 'NucleotideSequence':
        from .sequences_auxiliary import unmask_nucleotide_sequence_slice
        return unmask_nucleotide_sequence_slice(self, start, end)
    
    def is_position_masked(self, position: int) -> bool:
        if position < 0 or position >= len(self.data):
            raise IndexError(f"Position {position} out of range")
        return is_masked(self.data[position])
    
    def get_masked_positions(self) -> np.ndarray:
        return np.where([is_masked(nt) for nt in self.data])[0]
    
    def get_unmasked_positions(self) -> np.ndarray:
        return np.where([not is_masked(nt) for nt in self.data])[0]
    
    @property
    def masked_fraction(self) -> float:
        if len(self.data) == 0:
            return 0.0
        masked_count = sum(is_masked(nt) for nt in self.data)
        return masked_count / len(self.data)
    
    def nucleotide_composition(self, consider_masking: bool = False) -> dict[str, int]:
        from .sequences_auxiliary import get_nucleotide_composition
        return get_nucleotide_composition(self, consider_masking)
