"""Type stubs for _faiparser C extension."""

from typing import List, Tuple

def parse_fasta_to_fai(filename: str) -> List[Tuple[str, int, int, int, int]]:
    """Parse FASTA file and return FAI entries as list of tuples.
    
    Args:
        filename: Path to FASTA file to parse
        
    Returns:
        List of tuples, each containing:
        - name (str): Sequence name
        - length (int): Sequence length in bases
        - offset (int): Byte offset where sequence starts
        - line_bases (int): Number of bases per line
        - line_bytes (int): Number of bytes per line (including newline)
        
    Raises:
        IOError: If file cannot be read
        ValueError: If FASTA format is invalid
        MemoryError: If insufficient memory for parsing
    """
    ... 