"""Shared types, enums, and protocols for pyrion."""

from enum import Enum
from typing import Dict, Any
import numpy as np

# Import Strand from its actual location for backwards compatibility
from .core.strand import Strand

class ExonType(Enum):
    """Enumeration for exon types in genomic annotations."""
    ALL = "all"
    CDS = "cds" 
    UTR5 = "utr5"
    UTR3 = "utr3"

# Type aliases
Coordinate = int
BlockArray = np.ndarray  # Shape (N, 2) for [start, end] pairs
ChainBlockArray = np.ndarray  # Shape (N, 6) for chain blocks
Metadata = Dict[str, Any]
ChromSizes = Dict[str, int]  # Mapping from chromosome name to size in bp
