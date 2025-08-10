"""Data transformation utilities for converting between different genomic data types."""

from typing import List, Optional
import numpy as np

from ..core.intervals import GenomicInterval
from ..core.genes import Transcript, TranscriptsCollection


def intervals_to_transcripts(
    intervals: List[GenomicInterval], 
    source_file: Optional[str] = None
) -> TranscriptsCollection:
    """Convert a list of GenomicInterval objects to a TranscriptsCollection.

    May be helpful if bed-6 formatted data is needed as is was bed-12.
    """
    transcripts = []
    
    for i, interval in enumerate(intervals):
        # Use interval ID if available, otherwise generate one
        transcript_id = interval.id if interval.id is not None else f"interval_{i+1}"
        blocks = np.array([[interval.start, interval.end]], dtype=np.int32)
        
        transcript = Transcript(
            id=transcript_id,
            chrom=interval.chrom,
            strand=interval.strand,
            blocks=blocks,
            cds_start=interval.start,
            cds_end=interval.end
        )
        
        transcripts.append(transcript)
    
    return TranscriptsCollection(transcripts=transcripts, source_file=source_file)


def bed_to_transcripts(bed_file_path: str) -> TranscriptsCollection:
    from ..io import read_narrow_bed_file
    
    intervals = read_narrow_bed_file(bed_file_path)
    return intervals_to_transcripts(intervals, source_file=bed_file_path)
