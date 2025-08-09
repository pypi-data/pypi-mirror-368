"""Transcript serialization operations for BED12 and JSON formats."""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, Union
from ..core.genes import Transcript, TranscriptsCollection
from ..core.strand import Strand


def transcript_to_bed12_string(transcript: Transcript) -> str:
    chrom_name = transcript.chrom
    chrom_start = int(transcript.blocks[0, 0])
    chrom_end = int(transcript.blocks[-1, 1])
    name = transcript.id
    score = 1000  # Default score
    strand = '+' if transcript.strand == Strand.PLUS else '-' if transcript.strand == Strand.MINUS else '.'
    
    thick_start = transcript.cds_start if transcript.cds_start is not None else chrom_start
    thick_end = transcript.cds_end if transcript.cds_end is not None else chrom_start
    
    item_rgb = "0"  # Default color
    block_count = len(transcript.blocks)
    
    block_sizes = []
    block_starts = []
    
    for i, (start, end) in enumerate(transcript.blocks):
        block_sizes.append(str(int(end - start)))
        block_starts.append(str(int(start - chrom_start)))
    
    block_sizes_str = ','.join(block_sizes) + ','
    block_starts_str = ','.join(block_starts) + ','
    
    return '\t'.join([
        chrom_name,
        str(chrom_start),
        str(chrom_end), 
        name,
        str(score),
        strand,
        str(thick_start),
        str(thick_end),
        item_rgb,
        str(block_count),
        block_sizes_str,
        block_starts_str
    ])


def transcripts_collection_to_bed12_string(collection: TranscriptsCollection) -> str:
    lines = []
    for transcript in collection.transcripts:
        lines.append(transcript_to_bed12_string(transcript))
    return '\n'.join(lines)


def save_transcripts_collection_to_bed12(collection: TranscriptsCollection, file_path: Union[str, Path]) -> None:
    file_path = Path(file_path)
    bed12_content = transcripts_collection_to_bed12_string(collection)
    
    with file_path.open('w') as f:
        f.write(bed12_content)
        if not bed12_content.endswith('\n'):
            f.write('\n')


def transcript_to_dict(transcript: Transcript) -> Dict[str, Any]:
    return {
        'id': transcript.id,
        'chrom': transcript.chrom,
        'strand': int(transcript.strand),
        'blocks': transcript.blocks.tolist(),
        'cds_start': transcript.cds_start,
        'cds_end': transcript.cds_end,
        'is_coding': transcript.is_coding,
        'biotype': transcript.biotype
    }


def transcript_from_dict(data: Dict[str, Any]) -> Transcript:
    blocks = np.array(data['blocks'], dtype=np.int32)
    strand = Strand(data['strand']) if isinstance(data['strand'], int) else data['strand']
    chrom = data['chrom']
    
    return Transcript(
        blocks=blocks,
        strand=strand,
        chrom=chrom,
        id=data['id'],
        cds_start=data.get('cds_start'),
        cds_end=data.get('cds_end'),
        biotype=data.get('biotype')
    )


def transcripts_collection_to_dict(collection: TranscriptsCollection) -> Dict[str, Any]:
    return {
        'transcripts': [transcript_to_dict(t) for t in collection.transcripts],
        'source_file': collection.source_file,
        'count': len(collection.transcripts)
    }


def transcripts_collection_from_dict(data: Dict[str, Any]) -> TranscriptsCollection:
    transcripts = [transcript_from_dict(t_data) for t_data in data['transcripts']]
    source_file = data.get('source_file')
    
    return TranscriptsCollection(transcripts=transcripts, source_file=source_file)


def save_transcripts_collection_to_json(collection: TranscriptsCollection, file_path: Union[str, Path]) -> None:
    file_path = Path(file_path)
    data = transcripts_collection_to_dict(collection)
    
    with file_path.open('w') as f:
        json.dump(data, f, indent=2)


def load_transcripts_collection_from_json(file_path: Union[str, Path]) -> TranscriptsCollection:
    file_path = Path(file_path)
    
    with file_path.open('r') as f:
        data = json.load(f)
    
    return transcripts_collection_from_dict(data)


def transcripts_collection_summary_string(collection: TranscriptsCollection) -> str:
    base_summary = f"TranscriptsCollection: {len(collection.transcripts):,} transcripts"
    
    if collection.transcripts:
        chrom_counts = {}
        coding_count = 0
        
        for transcript in collection.transcripts:
            chrom = transcript.chrom
            chrom_counts[chrom] = chrom_counts.get(chrom, 0) + 1
            if transcript.is_coding:
                coding_count += 1
        
        chrom_info = f"{len(chrom_counts)} chromosomes"
        coding_info = f"{coding_count:,} coding ({coding_count/len(collection.transcripts)*100:.1f}%)"
        
        base_summary += f" across {chrom_info}, {coding_info}"
    
    if collection.source_file:
        base_summary += f"\nSource: {collection.source_file}"
    
    return base_summary
