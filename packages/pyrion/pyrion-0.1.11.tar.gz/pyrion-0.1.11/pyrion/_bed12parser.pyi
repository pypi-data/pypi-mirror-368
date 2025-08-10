"""Type stubs for _bed12parser C extension module.

This module provides fast parsing of BED12 format files for gene/transcript annotations.
"""

from typing import List, Optional
from pyrion.core.genes import Transcript

def parse_bed12_line(line: bytes) -> Optional[Transcript]:
    """Parse a single BED12 line into a Transcript object.
    
    Args:
        line: Raw bytes of a single line from a BED12 file
        
    Returns:
        A Transcript object containing the parsed transcript data, or None for empty/comment lines
        
    Raises:
        ValueError: If the BED12 line is malformed or doesn't have 12 fields
    """
    ...

def parse_bed12_file(content: bytes) -> List[Transcript]:
    """Parse BED12 file content into a list of Transcript objects.
    
    Args:
        content: Raw bytes of the entire BED12 file content
        
    Returns:
        List of Transcript objects containing the parsed transcript data
        
    Raises:
        ValueError: If any BED12 line is malformed or doesn't have 12 fields
    """
    ... 