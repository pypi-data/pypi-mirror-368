"""GenePred format I/O support."""

from typing import Union
from pathlib import Path
import numpy as np

from ..core.genes import Transcript, TranscriptsCollection
from ..core.strand import Strand


def read_genepred_file(file_path: Union[str, Path], 
                      has_header: bool = False,
                      extended: bool = False) -> TranscriptsCollection:
    """Read genePred file and return TranscriptsCollection."""
    # TODO: test properly on some real genePred file
    file_path = Path(file_path)
    
    transcripts = []
    line_num = 0
    
    with file_path.open('r') as f:
        for line in f:
            line_num += 1
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
                
            if has_header and line_num == 1:
                continue
            
            try:
                transcript = _parse_genepred_line(line, extended=extended)
                if transcript:
                    transcripts.append(transcript)
            except Exception as e:
                raise ValueError(f"Error parsing line {line_num} in {file_path}: {e}")
    
    return TranscriptsCollection(transcripts=transcripts, source_file=str(file_path))


def _parse_genepred_line(line: str, extended: bool = False) -> Transcript:
    fields = line.split('\t')
    
    # Validate field count
    expected_fields = 15 if extended else 10
    if len(fields) < expected_fields:
        raise ValueError(f"Expected {expected_fields} fields for {'extended ' if extended else ''}genePred, got {len(fields)}")
    
    # Parse standard fields
    name = fields[0]
    chrom = fields[1]
    strand_char = fields[2]
    tx_start = int(fields[3])
    tx_end = int(fields[4])
    cds_start = int(fields[5])
    cds_end = int(fields[6])
    exon_count = int(fields[7])
    exon_starts_str = fields[8].rstrip(',')
    exon_ends_str = fields[9].rstrip(',')
    
    # Parse strand
    if strand_char == '+':
        strand = Strand.PLUS
    elif strand_char == '-':
        strand = Strand.MINUS
    else:
        strand = Strand.UNKNOWN
    
    if exon_starts_str and exon_ends_str:
        exon_starts = [int(x) for x in exon_starts_str.split(',') if x]
        exon_ends = [int(x) for x in exon_ends_str.split(',') if x]
    else:
        exon_starts = []
        exon_ends = []
    
    if len(exon_starts) != exon_count or len(exon_ends) != exon_count:
        raise ValueError(f"Exon count mismatch: expected {exon_count}, got {len(exon_starts)} starts and {len(exon_ends)} ends")
    
    if len(exon_starts) != len(exon_ends):
        raise ValueError(f"Exon coordinate mismatch: {len(exon_starts)} starts vs {len(exon_ends)} ends")
    
    if exon_starts:
        blocks = np.array([(start, end) for start, end in zip(exon_starts, exon_ends)], dtype=np.int32)
        
        for i in range(len(blocks) - 1):
            if blocks[i][1] > blocks[i + 1][0]:
                raise ValueError(f"Overlapping exons in transcript {name}: {blocks[i]} and {blocks[i + 1]}")
    else:
        blocks = np.array([(tx_start, tx_end)], dtype=np.int32)

    transcript_cds_start = cds_start if cds_start < cds_end else None
    transcript_cds_end = cds_end if cds_start < cds_end else None
    
    return Transcript(
        id=name,
        chrom=chrom,
        strand=strand,
        blocks=blocks,
        cds_start=transcript_cds_start,
        cds_end=transcript_cds_end
    )


def read_refflat_file(file_path: Union[str, Path], has_header: bool = False) -> TranscriptsCollection:
    """Read refFlat file and return TranscriptsCollection.
    
    refFlat format is like genePred but with an additional first column for gene name:
    geneName name chrom strand txStart txEnd cdsStart cdsEnd exonCount exonStarts exonEnds.
    """
    file_path = Path(file_path)
    
    transcripts = []
    line_num = 0
    
    with file_path.open('r') as f:
        for line in f:
            line_num += 1
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            # Skip header if present
            if has_header and line_num == 1:
                continue
            
            try:
                fields = line.split('\t')
                if len(fields) < 11:
                    raise ValueError(f"Expected at least 11 fields for refFlat, got {len(fields)}")
                
                genepred_line = '\t'.join(fields[1:11])
                transcript = _parse_genepred_line(genepred_line, extended=False)
                
                if transcript:
                    transcripts.append(transcript)
            except Exception as e:
                raise ValueError(f"Error parsing line {line_num} in {file_path}: {e}")
    
    return TranscriptsCollection(transcripts=transcripts, source_file=str(file_path)) 