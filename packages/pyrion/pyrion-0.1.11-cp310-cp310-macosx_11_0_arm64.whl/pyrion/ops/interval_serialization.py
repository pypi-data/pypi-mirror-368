"""Genomic interval serialization operations for BED6 format."""

from pathlib import Path
from typing import List, Union
from ..core.intervals import GenomicInterval
from ..core.strand import Strand


def genomic_interval_to_bed6_string(interval: GenomicInterval, score: int = 1000) -> str:
    """Convert a single GenomicInterval to BED6 format string."""
    chrom = interval.chrom
    start = interval.start
    end = interval.end
    name = interval.id if interval.id is not None else "interval"
    
    # Convert strand to BED format character
    if interval.strand == Strand.PLUS:
        strand_char = "+"
    elif interval.strand == Strand.MINUS:
        strand_char = "-"
    else:
        strand_char = "."
    
    return f"{chrom}\t{start}\t{end}\t{name}\t{score}\t{strand_char}"


def save_genomic_intervals_to_bed6(intervals: List[GenomicInterval], 
                                  file_path: Union[str, Path],
                                  score: int = 1000) -> None:
    file_path = Path(file_path)
    
    with file_path.open('w') as f:
        for i, interval in enumerate(intervals):
            bed6_line = genomic_interval_to_bed6_string(interval, score=score)
            f.write(bed6_line)
            if i < len(intervals) - 1:
                f.write('\n')
        if intervals:
            f.write('\n')


def genomic_intervals_to_bed6_string(intervals: List[GenomicInterval], 
                                    score: int = 1000) -> str:
    lines = []
    for interval in intervals:
        bed6_line = genomic_interval_to_bed6_string(interval, score=score)
        lines.append(bed6_line)
    
    return '\n'.join(lines)
