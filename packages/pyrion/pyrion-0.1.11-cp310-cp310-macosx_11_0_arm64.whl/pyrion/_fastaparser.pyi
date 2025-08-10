"""Type stubs for fast FASTA parser C extension."""

from typing import List, Tuple
import numpy as np

def parse_fasta_fast(filename: str, sequence_type: int) -> List[Tuple[str, np.ndarray, int]]:
    """
    Fast FASTA file parser.
    
    Parameters
    ----------
    filename : str
        Path to FASTA file
    sequence_type : int
        Sequence type: 0=DNA, 1=RNA, 2=PROTEIN
        
    Returns
    -------
    list of tuple
        List of (header, encoded_array, sequence_type) tuples
        - header: str, sequence identifier without '>'
        - encoded_array: numpy array of encoded sequence
        - sequence_type: int, same as input parameter
    """
    ... 