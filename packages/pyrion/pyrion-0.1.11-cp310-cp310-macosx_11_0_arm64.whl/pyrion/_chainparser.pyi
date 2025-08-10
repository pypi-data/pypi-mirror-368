"""Type stubs for _chainparser C extension module.

This module provides fast parsing of chain format files for genome alignments.
"""

from typing import List, Optional
from pyrion.core.genome_alignment import GenomeAlignment

def parse_chain_chunk(data: bytes, min_score: Optional[int] = None) -> Optional[GenomeAlignment]:
    """Parse a single chain chunk into a GenomeAlignment object.
    
    Args:
        data: Raw bytes of a single chain block from a chain file
        min_score: Optional minimum score threshold. Chains with scores below this
                  will be filtered out and None will be returned.
        
    Returns:
        A GenomeAlignment object containing the parsed alignment data, or None
        if the chain score is below the min_score threshold.
        
    Raises:
        ValueError: If the chain data is malformed or cannot be parsed
    """
    ...

def parse_many_chain_chunks(chunks: List[bytes], min_score: Optional[int] = None) -> List[GenomeAlignment]:
    """Parse multiple chain chunks into a list of GenomeAlignment objects.
    
    Args:
        chunks: List of raw bytes, each representing a chain block from a chain file
        min_score: Optional minimum score threshold. Chains with scores below this
                  will be filtered out from the results.
        
    Returns:
        List of GenomeAlignment objects containing the parsed alignment data.
        Only chains with scores >= min_score (if specified) are included.
        
    Raises:
        ValueError: If any chain data is malformed or cannot be parsed
    """
    ... 