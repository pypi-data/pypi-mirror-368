"""BED format I/O support."""

from typing import Union, List
from pathlib import Path

from .. import GenomicInterval
from ..core.genes import TranscriptsCollection
from .._bed12parser import parse_bed12_file
from .._narrowbedparser import parse_narrow_bed_file


def read_bed12_file(file_path: Union[str, Path]) -> TranscriptsCollection:
    """Read BED12 file and return TranscriptsCollection."""
    file_path = Path(file_path)
    
    with file_path.open("rb") as f:
        content = f.read()
    
    transcripts = parse_bed12_file(content)
    return TranscriptsCollection(transcripts=transcripts, source_file=str(file_path))


def read_narrow_bed_file(file_path: Union[str, Path]) -> List[GenomicInterval]:
    """Read a narrow BED file with 3-9 fields and return a list of GenomicInterval objects."""
    file_path = Path(file_path)
    
    with file_path.open("rb") as f:
        content = f.read()

    width = None
    start = 0
    for i in range(len(content)):
        if content[i:i+1] == b'\n' or i == len(content) - 1:
            line_end = i if content[i:i+1] == b'\n' else i + 1
            line_bytes = content[start:line_end]
            
            if line_bytes and not line_bytes.startswith(b'#'):
                width = line_bytes.count(b'\t') + 1  # +1 because tabs separate fields
                break
            
            start = i + 1
    
    if width is None:
        raise ValueError("No valid BED lines found in file")
    
    if width < 3 or width > 9:
        raise ValueError(f"Unsupported BED width: {width} (must be 3-9)")
    
    intervals = parse_narrow_bed_file(content, width)
    return intervals
