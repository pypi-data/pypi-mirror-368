"""FASTA I/O operations."""

from __future__ import annotations

from typing import Dict, Union, List, Mapping
from pathlib import Path
from enum import IntEnum

from .._fastaparser import parse_fasta_fast
from ..core.nucleotide_sequences import NucleotideSequence, SequenceType
from ..core.amino_acid_sequences import AminoAcidSequence
from ..core.fai import FaiStore
from ..core.intervals import GenomicInterval
from ..core.sequences_collection import SequencesCollection


class _SequenceTypeMapping(IntEnum):
    DNA = 0
    RNA = 1
    PROTEIN = 2


class FastaAccessor:
    def __init__(self, fasta_file: Union[str, Path], fai_store: FaiStore):
        """Initialize FastaAccessor with FASTA file and index."""
        self.fasta_file = Path(fasta_file)
        if not self.fasta_file.exists():
            raise FileNotFoundError(f"FASTA file not found: {self.fasta_file}")
        
        self.fai_store = fai_store
        self._file_handle = None
    
    def __enter__(self):
        self._file_handle = open(self.fasta_file, 'rb')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
    
    def get_sequence(self, 
                    region: GenomicInterval,
                    is_rna: bool = False) -> NucleotideSequence:
        if region.chrom not in self.fai_store:
            raise KeyError(f"Sequence '{region.chrom}' not found in FASTA index")
        
        fai_entry = self.fai_store[region.chrom]
        start = region.start
        end = region.end
        
        if start is None:
            start = 0
        if end is None:
            end = fai_entry.length
        
        if start < 0 or end < start or end > fai_entry.length:
            raise ValueError(f"Invalid coordinates: start={start}, end={end}, sequence_length={fai_entry.length}")
        
        raw_sequence = self._extract_raw_sequence(fai_entry, start, end)
        return NucleotideSequence.from_string(
            raw_sequence, 
            is_rna=is_rna,
            metadata={
                'sequence_id': region.chrom,
                'source_file': str(self.fasta_file),
                'start': start,
                'end': end
            }
        )

    def get_sequence_length(self, sequence_name: str) -> int:
        if sequence_name not in self.fai_store:
            raise KeyError(f"Sequence '{sequence_name}' not found in FASTA index")
        
        return self.fai_store[sequence_name].length
    
    def get_sequence_names(self) -> List[str]:
        return list(self.fai_store.keys())
    
    def has_sequence(self, sequence_name: str) -> bool:
        return sequence_name in self.fai_store
    
    def _extract_raw_sequence(self, fai_entry, start: int, end: int) -> str:
        if not self._file_handle:
            raise RuntimeError("File not opened. Use FastaAccessor as context manager.")

        full_lines_before_start = start // fai_entry.line_bases
        remaining_before_start = start % fai_entry.line_bases
        
        start_byte = fai_entry.offset + (full_lines_before_start * fai_entry.line_bytes) + remaining_before_start
        sequence_length = end - start
        full_lines_needed = sequence_length // fai_entry.line_bases
        remaining_bases = sequence_length % fai_entry.line_bases
        estimated_bytes = (full_lines_needed * fai_entry.line_bytes) + remaining_bases
        padding = max(full_lines_needed + 2, 100)
        read_bytes = estimated_bytes + padding
        
        self._file_handle.seek(start_byte)
        raw_data = self._file_handle.read(read_bytes)
        
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode('utf-8', errors='ignore')
        
        sequence_chars = []
        bases_collected = 0
        
        for char in raw_data:
            if char.isalpha() or char in '-N':
                sequence_chars.append(char)
                bases_collected += 1
                if bases_collected >= sequence_length:
                    break
        
        return ''.join(sequence_chars)
    
    def get_multiple_sequences(self, 
                              regions: List[GenomicInterval],
                              is_rna: bool = False) -> Dict[str, NucleotideSequence]:
        results = {}
        
        for region in regions:
            sequence = self.get_sequence(
                region=region,
                is_rna=is_rna
            )
            
            if region.id:
                region_key = f"{region.id} ({region})"
            else:
                region_key = str(region)
            
            results[region_key] = sequence
        
        return results
    
    
    def __repr__(self) -> str:
        return f"FastaAccessor(file='{self.fasta_file}', sequences={len(self.fai_store)})"


def read_fasta(
    filename: Union[str, Path], 
    sequence_type: SequenceType,
    return_dict: bool = True
) -> Union[SequencesCollection, List[Union[NucleotideSequence, AminoAcidSequence]]]:
    filename = str(filename)
    type_mapping = {
        SequenceType.DNA: _SequenceTypeMapping.DNA,
        SequenceType.RNA: _SequenceTypeMapping.RNA,
        SequenceType.PROTEIN: _SequenceTypeMapping.PROTEIN
    }
    
    if sequence_type not in type_mapping:
        raise ValueError(f"Invalid sequence_type: {sequence_type}")
    
    internal_type = type_mapping[sequence_type]
    
    raw_sequences = parse_fasta_fast(filename, internal_type)
    sequences = SequencesCollection()
    sequence_list: List[Union[NucleotideSequence, AminoAcidSequence]] = []
    
    for header, encoded_array, seq_type in raw_sequences:
        seq_id = header.strip()
        
        if seq_type == _SequenceTypeMapping.PROTEIN:
            sequence_obj = AminoAcidSequence(
                data=encoded_array,
                metadata={'sequence_id': seq_id, 'source_file': filename}
            )
        else:
            is_rna = (seq_type == _SequenceTypeMapping.RNA)
            sequence_obj = NucleotideSequence(
                data=encoded_array,
                is_rna=is_rna,
                metadata={'sequence_id': seq_id, 'source_file': filename}
            )
        
        sequences.add(seq_id, sequence_obj, force=False)
        sequence_list.append(sequence_obj)
    
    return sequences if return_dict else sequence_list


def write_fasta(
    sequences: Union[Mapping[str, NucleotideSequence], List[NucleotideSequence]],
    filename: Union[str, Path],
    line_width: int = 80
) -> None:
    with open(filename, 'w') as file:
        from collections.abc import Mapping as _Mapping
        if isinstance(sequences, _Mapping):
            for seq_id, sequence in sequences.items():
                _write_sequence(file, seq_id, sequence, line_width)
        else:
            for i, sequence in enumerate(sequences):
                if sequence.metadata and 'sequence_id' in sequence.metadata:
                    seq_id = sequence.metadata['sequence_id']
                else:
                    seq_id = f"sequence_{i+1}"
                _write_sequence(file, seq_id, sequence, line_width)


def _write_sequence(file, seq_id: str, sequence: NucleotideSequence, line_width: int):
    file.write(f">{seq_id}\n")
    
    seq_str = str(sequence)
    if line_width <= 0:
        file.write(seq_str + '\n')
    else:
        for i in range(0, len(seq_str), line_width):
            file.write(seq_str[i:i+line_width] + '\n')


def read_dna_fasta(filename: Union[str, Path], **kwargs) -> SequencesCollection:
    return read_fasta(filename, SequenceType.DNA, **kwargs)


def read_rna_fasta(filename: Union[str, Path], **kwargs) -> SequencesCollection:
    return read_fasta(filename, SequenceType.RNA, **kwargs)


def read_protein_fasta(filename: Union[str, Path], **kwargs) -> SequencesCollection:
    """Read protein sequences from FASTA file."""
    return read_fasta(filename, SequenceType.PROTEIN, **kwargs)
