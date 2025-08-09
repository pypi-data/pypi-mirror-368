"""Sequence serialization operations for FASTA format."""

from pathlib import Path
from typing import List, Union, Any, Optional
from ..core.nucleotide_sequences import NucleotideSequence
from ..core.amino_acid_sequences import AminoAcidSequence
from ..core.codons import CodonSequence


def format_fasta_sequence(sequence_string: str, width: int = 80) -> str:
    """Format sequence string with specified line width."""
    if width <= 0:
        return sequence_string
    
    lines = []
    for i in range(0, len(sequence_string), width):
        lines.append(sequence_string[i:i + width])
    
    return '\n'.join(lines)


def get_sequence_header(sequence: Any, index: Optional[int] = None) -> str:
    """Extract or generate FASTA header for a sequence object."""
    if hasattr(sequence, 'metadata') and sequence.metadata:
        if isinstance(sequence.metadata, dict):
            seq_id = sequence.metadata.get('sequence_id')
            if seq_id:
                return seq_id
    
    if index is not None:
        return f"sequence_{index + 1}"
    else:
        return "sequence"


def sequence_to_fasta_string(sequence: Any, width: int = 80, header: Optional[str] = None) -> str:
    if hasattr(sequence, 'to_string'):
        sequence_string = sequence.to_string()
    elif hasattr(sequence, '__str__'):
        sequence_string = str(sequence)
    else:
        raise ValueError(f"Sequence object {type(sequence)} doesn't have to_string() or __str__() method")
    
    if header is None:
        header = get_sequence_header(sequence)
    
    if not header.startswith('>'):
        header = '>' + header
    
    formatted_sequence = format_fasta_sequence(sequence_string, width)
    return f"{header}\n{formatted_sequence}"


def sequences_to_fasta_string(sequences: List[Any], width: int = 80) -> str:
    fasta_entries = []
    
    for i, sequence in enumerate(sequences):
        fasta_entry = sequence_to_fasta_string(sequence, width=width)
        fasta_entries.append(fasta_entry)
    
    return '\n'.join(fasta_entries)


def save_sequences_to_fasta(sequences: List[Any], 
                           file_path: Union[str, Path],
                           width: int = 80) -> None:
    file_path = Path(file_path)
    
    with file_path.open('w') as f:
        for i, sequence in enumerate(sequences):
            fasta_entry = sequence_to_fasta_string(sequence, width=width)
            f.write(fasta_entry)
            
            if i < len(sequences) - 1:
                f.write('\n')
        
        if sequences:
            f.write('\n')


def nucleotide_sequence_to_fasta_string(sequence: NucleotideSequence, 
                                       width: int = 80, 
                                       header: Optional[str] = None) -> str:
    return sequence_to_fasta_string(sequence, width=width, header=header)


def amino_acid_sequence_to_fasta_string(sequence: AminoAcidSequence,
                                       width: int = 80,
                                       header: Optional[str] = None) -> str:
    return sequence_to_fasta_string(sequence, width=width, header=header)


def codon_sequence_to_fasta_string(sequence: CodonSequence,
                                  width: int = 80,
                                  header: Optional[str] = None) -> str:
    return sequence_to_fasta_string(sequence, width=width, header=header)