"""Type stubs for _gtfparser C extension."""

from typing import List, Dict, Tuple, Any

def parse_gtf_chunk(lines: List[str]) -> Tuple[List[Any], Dict[str, str]]:
    """
    Parse GTF chunk into transcripts and gene mapping.
    
    Args:
        lines: List of GTF lines for a single gene
        
    Returns:
        Tuple of (transcript_objects, gene_mapping_dict)
    """
    ... 