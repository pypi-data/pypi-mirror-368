"""Type stubs for _narrowbedparser C extension module.

This module provides fast parsing of narrow BED format files (3-9 columns) for genomic intervals.
"""

from typing import List, Optional
from pyrion.core.intervals import GenomicInterval

def parse_narrow_bed_line(line: bytes, width: int) -> Optional[GenomicInterval]:
    """Parse a single narrow BED line into a GenomicInterval object.
    
    Args:
        line: Raw bytes of a single line from a narrow BED file
        width: Expected number of fields (3-9)
        
    Returns:
        A GenomicInterval object containing the parsed interval data, or None for empty/comment lines
        
    Raises:
        ValueError: If the BED line is malformed or doesn't have the expected number of fields
    """
    ...

def parse_narrow_bed_file(content: bytes, width: int) -> List[GenomicInterval]:
    """Parse narrow BED file content into a list of GenomicInterval objects.
    
    Args:
        content: Raw bytes of the entire narrow BED file content
        width: Expected number of fields (3-9)
        
    Returns:
        List of GenomicInterval objects containing the parsed interval data
        
    Raises:
        ValueError: If any BED line is malformed or doesn't have the expected number of fields
    """
    ... 