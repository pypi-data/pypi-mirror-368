"""Codon and codon sequence representations for genomic analysis."""

import numpy as np
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass

from ..utils.encoding import (
    NUCLEOTIDE_DECODING, RNA_NUCLEOTIDE_DECODING,
    FRAMESHIFT_1, is_gap, is_frameshift
)
from .nucleotide_sequences import NucleotideSequence

INVALID_CHARACTER = 0


@dataclass
class Codon:
    """Codon representation holding 1-3 non-gap symbols (incomplete codons allowed)."""
    
    symbols: np.ndarray  # Variable length int8 array containing 1-3 non-gap symbols
    is_rna: bool = False
    
    def __post_init__(self):
        """Validate codon structure."""
        non_gap_count = np.sum(~np.array([is_gap(x) for x in self.symbols]))
        if non_gap_count < 1 or non_gap_count > 3:
            raise ValueError(f"Codon must have 1-3 non-gap symbols, got {non_gap_count}")
    
    def is_complete(self) -> bool:
        """Check if codon has exactly 3 non-gap symbols."""
        non_gap_count = np.sum(~np.array([is_gap(x) for x in self.symbols]))
        return non_gap_count == 3
    
    def to_string(self) -> str:
        def _symbol_to_char(val: int) -> str:
            # Use the appropriate decoding table
            decoding_table = RNA_NUCLEOTIDE_DECODING if self.is_rna else NUCLEOTIDE_DECODING
            
            if val in decoding_table:
                return decoding_table[val]
            else:
                return '?'
        
        return ''.join(_symbol_to_char(int(x)) for x in self.symbols)
    
    def translate(self, translation_table=None) -> str:
        from ..utils.amino_acid_encoding import decode_amino_acids, UNKNOWN_AMINO_ACID
        from ..utils.encoding import is_gap, is_frameshift
        import numpy as np
        
        if translation_table is None:
            from .translation import TranslationTable
            translation_table = TranslationTable.standard()
        
        # Filter out gaps and check for frameshifts
        non_gap_symbols = []
        has_frameshift = False
        
        for symbol in self.symbols:
            if is_frameshift(symbol):
                has_frameshift = True
            elif not is_gap(symbol):
                non_gap_symbols.append(symbol)
        
        # If frameshift present, return X
        if has_frameshift:
            return decode_amino_acids(np.array([UNKNOWN_AMINO_ACID], dtype=np.int8))[0]
        
        # If incomplete codon (less than 3 non-gap symbols), return X
        if len(non_gap_symbols) < 3:
            return decode_amino_acids(np.array([UNKNOWN_AMINO_ACID], dtype=np.int8))[0]

        codon_codes = tuple(int(x) for x in non_gap_symbols[:3])
        aa_code = translation_table.translate_codon(codon_codes)
        
        return decode_amino_acids(np.array([aa_code], dtype=np.int8))[0]
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        complete_status = "complete" if self.is_complete() else "incomplete"
        return f"Codon('{self.to_string()}', is_rna={self.is_rna}, {complete_status})"


class CodonSequence:
    """Codon sequence wrapper around NucleotideSequence with codon-wise operations."""
    def __init__(self, nucleotide_sequence):
        """Initialize from a NucleotideSequence object."""
        self.nucleotide_sequence = nucleotide_sequence
        self._data = nucleotide_sequence.data.copy()  # Work with a copy
        self.is_rna = getattr(nucleotide_sequence, 'is_rna', False)
    
    @property
    def data(self) -> np.ndarray:
        """Access to underlying data array."""
        return self._data
    
    def _get_valid_nucleotide_positions(self) -> np.ndarray:
        """Get positions of valid nucleotides (non-gap, non-frameshift, non-invalid)."""
        valid_mask = np.array([
            not is_gap(x) and not is_frameshift(x) for x in self._data
        ])
        return np.where(valid_mask)[0]
    
    def insert_frameshift(self, position: int) -> None:
        """Insert frameshift after the Nth valid nucleotide (atgcnATGCN) (0-based)."""
        valid_positions = self._get_valid_nucleotide_positions()
        
        if position < 0 or position >= len(valid_positions):
            raise ValueError(f"Position {position} out of range [0, {len(valid_positions)-1}] for valid nucleotides")
        
        # Insert frameshift right after the valid nucleotide
        insert_pos = valid_positions[position] + 1
        frameshift_val = np.array([FRAMESHIFT_1], dtype=np.int8)
        self._data = np.insert(self._data, insert_pos, frameshift_val)
        self._apply_frameshift_cancellation()
    
    def remove_frameshift(self, position: int) -> None:
        """Remove frameshift after the Nth valid nucleotide (atgcnATGCN)."""
        valid_positions = self._get_valid_nucleotide_positions()
        
        if position < 0 or position >= len(valid_positions):
            raise ValueError(f"Position {position} out of range for valid nucleotides")
        
        # Look for frameshift after this valid nucleotide
        search_pos = valid_positions[position] + 1
        
        # Find the first frameshift after this position
        while (search_pos < len(self._data) and 
               not is_frameshift(self._data[search_pos])):
            if not is_gap(self._data[search_pos]):
                # Hit another valid nucleotide, no frameshift to remove
                raise ValueError(f"No frameshift found after nucleotide at position {position}")
            search_pos += 1
        
        if search_pos >= len(self._data):
            raise ValueError(f"No frameshift found after nucleotide at position {position}")
        
        # Remove the frameshift
        self._data = np.delete(self._data, search_pos)
        self._apply_frameshift_cancellation()
    
    def _apply_frameshift_cancellation(self) -> None:
        """Remove consecutive groups of 3 frameshifts."""
        # TODO: check, seems suboptimal
        frameshift_positions = np.where(np.array([is_frameshift(x) for x in self._data]))[0]
        
        if len(frameshift_positions) == 0:
            return
        
        groups = []
        current_group = [frameshift_positions[0]]
        
        for i in range(1, len(frameshift_positions)):
            if frameshift_positions[i] == frameshift_positions[i-1] + 1:
                current_group.append(frameshift_positions[i])
            else:
                groups.append(current_group)
                current_group = [frameshift_positions[i]]
        groups.append(current_group)
        
        
        positions_to_remove = []
        for group in groups:
            if len(group) >= 3:
                # Remove groups of 3
                num_to_remove = (len(group) // 3) * 3
                positions_to_remove.extend(group[:num_to_remove])
        
        for pos in sorted(positions_to_remove, reverse=True):
            self._data = np.delete(self._data, pos)
    
    def get_frameshift_positions(self) -> List[Tuple[int, int]]:
        # TODO: check, seems suboptimal
        valid_positions = self._get_valid_nucleotide_positions()
        frameshift_info = []
        
        for i, pos in enumerate(valid_positions):
            count = 0
            search_pos = pos + 1
            
            while (search_pos < len(self._data) and 
                   (is_frameshift(self._data[search_pos]) or 
                    is_gap(self._data[search_pos]))):
                if is_frameshift(self._data[search_pos]):
                    count += 1
                search_pos += 1
            
            if count > 0:
                frameshift_info.append((i, count))
        
        return frameshift_info
    
    def remove_gaps(self) -> None:
        gap_mask = ~np.array([is_gap(x) for x in self._data])
        self._data = self._data[gap_mask]
    
    def get_codons(self, preserve_gaps: bool = False) -> List[Codon]:
        if preserve_gaps:
            symbols = self._data[self._data != INVALID_CHARACTER]
        else:
            valid_mask = ~np.array([is_gap(x) for x in self._data])
            invalid_mask = self._data != INVALID_CHARACTER
            symbols = self._data[valid_mask & invalid_mask]
        
        if len(symbols) == 0:
            return []
        
        if preserve_gaps:
            non_gap_mask = ~np.array([is_gap(x) for x in symbols])
        else:
            non_gap_mask = np.ones(len(symbols), dtype=bool)  # All are non-gap already
        
        non_gap_indices = np.where(non_gap_mask)[0]
        
        if len(non_gap_indices) == 0:
            return []
        
        codons = []
        i = 0

        # TODO: seems quite suboptimal
        while i < len(non_gap_indices):
            remaining = len(non_gap_indices) - i
            codon_size = min(3, remaining)  # Take up to 3 symbols
            start_idx = non_gap_indices[i]
            end_idx = non_gap_indices[i + codon_size - 1] + 1
            
            codon_symbols = symbols[start_idx:end_idx]
            
            non_gap_count = np.sum(~np.array([is_gap(x) for x in codon_symbols]))
            if non_gap_count >= 1:
                codons.append(Codon(codon_symbols, self.is_rna))
            
            i += 3
        
        return codons
    
    def translate(self, translation_table=None):
        from .amino_acid_sequences import AminoAcidSequence
        from .translation import TranslationTable
        from ..utils.amino_acid_encoding import UNKNOWN_AMINO_ACID, encode_amino_acids

        if translation_table is None:
            translation_table = TranslationTable.standard()
        
        codons = self.get_codons(preserve_gaps=True)
        
        if not codons:
            return None
        
        aa_chars = []
        for codon in codons:
            aa_char = codon.translate(translation_table)
            aa_chars.append(aa_char)
        
        aa_string = ''.join(aa_chars)
        aa_data = encode_amino_acids(aa_string)
        
        return AminoAcidSequence(data=aa_data)
    
    def __len__(self) -> int:
        """Number of codons (including incomplete trailing codon if present)."""
        return len(self.get_codons(preserve_gaps=True))

    def __getitem__(self, index: Union[int, slice]) -> Union[Codon, 'CodonSequence']:
        codons = self.get_codons(preserve_gaps=True)
        if isinstance(index, int):
            return codons[index]
        # Slice -> build a new CodonSequence from selected codons
        selected = codons[index]
        if not selected:
            # Empty slice returns empty CodonSequence
            empty_nt = NucleotideSequence(data=np.array([], dtype=np.int8), is_rna=self.is_rna)
            return CodonSequence(empty_nt)
        concatenated = np.concatenate([c.symbols for c in selected]).astype(np.int8, copy=False)
        new_nt = NucleotideSequence(data=concatenated, is_rna=self.is_rna)
        return CodonSequence(new_nt)
    
    def __str__(self) -> str:
        def _symbol_to_char(val: int) -> str:
            # Use the appropriate decoding table
            decoding_table = RNA_NUCLEOTIDE_DECODING if self.is_rna else NUCLEOTIDE_DECODING
            
            if val in decoding_table:
                return decoding_table[val]
            else:
                return '?'
        
        return ''.join(_symbol_to_char(int(x)) for x in self._data)

    def to_fasta_string(self, width: int = 80, header: Optional[str] = None) -> str:
        from ..ops.sequence_serialization import codon_sequence_to_fasta_string
        return codon_sequence_to_fasta_string(self, width=width, header=header)
    
    def __repr__(self) -> str:
        seq_preview = self.nucleotide_sequence.to_string()
        if len(seq_preview) > 30:
            seq_preview = seq_preview[:27] + "..."
        
        seq_type = "RNA" if self.is_rna else "DNA"
        return f"CodonSequence('{seq_preview}', codons={len(self)}, type={seq_type})"