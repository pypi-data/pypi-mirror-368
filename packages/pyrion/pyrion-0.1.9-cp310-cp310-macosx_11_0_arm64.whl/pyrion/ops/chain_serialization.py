"""Genome alignment serialization operations for chain format and JSON."""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, Union
from ..core.genome_alignment import GenomeAlignment, GenomeAlignmentsCollection


def genome_alignment_to_chain_string(alignment: GenomeAlignment) -> str:
    """Convert a single GenomeAlignment to chain format string.
    
    Chain format:
    chain {score} {t_chrom} {t_size} {t_strand} {t_start} {t_end} {q_chrom} {q_size} {q_strand} {q_start} {q_end} {chain_id}
    {block_size} {dt} {dq}
    ...
    {final_block_size}
    """
    # Header values from alignment
    score = alignment.score
    t_chrom = alignment.t_chrom
    q_chrom = alignment.q_chrom
    t_strand = '+' if alignment.t_strand == 1 else '-'
    q_strand = '+' if alignment.q_strand == 1 else '-'
    chain_id = alignment.chain_id
    t_size = alignment.t_size
    q_size = alignment.q_size
    
    # Handle empty blocks gracefully
    if len(alignment.blocks) == 0:
        t_start = t_end = q_start = q_end = 0
    else:
        t_start = int(alignment.t_span[0])
        t_end = int(alignment.t_span[1])
        q_start = int(alignment.q_span[0]) 
        q_end = int(alignment.q_span[1])
    
    header = f"chain {score} {t_chrom} {t_size} {t_strand} {t_start} {t_end} {q_chrom} {q_size} {q_strand} {q_start} {q_end} {chain_id}"
    
    block_lines = []
    blocks = alignment.blocks
    
    for i in range(len(blocks)):
        t_block_start, t_block_end, q_block_start, q_block_end = blocks[i]
        
        block_size = int(t_block_end - t_block_start)
        
        if i < len(blocks) - 1:
            next_t_start, _, next_q_start, _ = blocks[i + 1]
            dt = int(next_t_start - t_block_end)  # Gap in target
            
            if alignment.q_strand == -1:
                dq = int(q_block_start - next_q_start)
            else:
                dq = int(next_q_start - q_block_end)
            
            dt = max(0, dt)
            dq = max(0, dq)
            
            block_lines.append(f"{block_size}\t{dt}\t{dq}")
        else:
            block_lines.append(str(block_size))
    
    block_lines.append("")
    return header + "\n" + "\n".join(block_lines)


def genome_alignments_collection_to_chain_string(collection: GenomeAlignmentsCollection) -> str:
    chain_strings = []
    
    for alignment in collection.alignments:
        chain_string = genome_alignment_to_chain_string(alignment)
        chain_strings.append(chain_string)
    
    return "\n".join(chain_strings)


def save_genome_alignments_collection_to_chain(collection: GenomeAlignmentsCollection, 
                                              file_path: Union[str, Path]) -> None:
    file_path = Path(file_path)
    _write_chain_file_streaming(collection, file_path)


def _write_chain_file_streaming(collection: GenomeAlignmentsCollection, file_path: Path) -> None:
    with file_path.open('w') as f:
        for i, alignment in enumerate(collection.alignments):
            chain_string = genome_alignment_to_chain_string(alignment)
            f.write(chain_string)
            if i < len(collection.alignments) - 1:
                f.write('\n')


def genome_alignment_to_dict(alignment: GenomeAlignment) -> Dict[str, Any]:
    return {
        'chain_id': alignment.chain_id,
        'score': alignment.score,
        't_chrom': alignment.t_chrom,
        't_strand': alignment.t_strand,
        't_size': alignment.t_size,
        'q_chrom': alignment.q_chrom,
        'q_strand': alignment.q_strand,
        'q_size': alignment.q_size,
        'blocks': alignment.blocks.tolist(),
        'child_id': alignment.child_id
    }


def genome_alignment_from_dict(data: Dict[str, Any]) -> GenomeAlignment:
    blocks = np.array(data['blocks'], dtype=np.int32)
    t_chrom = data['t_chrom']
    q_chrom = data['q_chrom']
    
    return GenomeAlignment(
        chain_id=data['chain_id'],
        score=data['score'],
        t_chrom=t_chrom,
        t_strand=data['t_strand'],
        t_size=data['t_size'],
        q_chrom=q_chrom,
        q_strand=data['q_strand'],
        q_size=data['q_size'],
        blocks=blocks,
        child_id=data.get('child_id')
    )


def genome_alignments_collection_to_dict(collection: GenomeAlignmentsCollection) -> Dict[str, Any]:
    return {
        'alignments': [genome_alignment_to_dict(ga) for ga in collection.alignments],
        'source_file': collection.source_file,
        'count': len(collection.alignments)
    }


def genome_alignments_collection_from_dict(data: Dict[str, Any]) -> GenomeAlignmentsCollection:
    alignments = [genome_alignment_from_dict(ga_data) for ga_data in data['alignments']]
    source_file = data.get('source_file')
    
    return GenomeAlignmentsCollection(alignments=alignments, source_file=source_file)


def save_genome_alignments_collection_to_json(collection: GenomeAlignmentsCollection, 
                                             file_path: Union[str, Path]) -> None:
    file_path = Path(file_path)
    data = genome_alignments_collection_to_dict(collection)
    
    with file_path.open('w') as f:
        json.dump(data, f, indent=2)


def load_genome_alignments_collection_from_json(file_path: Union[str, Path]) -> GenomeAlignmentsCollection:
    file_path = Path(file_path)
    
    with file_path.open('r') as f:
        data = json.load(f)
    
    return genome_alignments_collection_from_dict(data)


def genome_alignments_collection_summary_string(collection: GenomeAlignmentsCollection) -> str:
    base_summary = f"GenomeAlignmentsCollection: {len(collection.alignments):,} alignments"
    
    if collection.alignments:
        t_chroms = set()
        q_chroms = set()
        total_score = 0
        
        for alignment in collection.alignments:
            t_chroms.add(alignment.t_chrom)
            q_chroms.add(alignment.q_chrom)
            total_score += alignment.score
        
        avg_score = total_score / len(collection.alignments)
        chrom_info = f"{len(t_chroms)} target chroms, {len(q_chroms)} query chroms"
        score_info = f"avg score: {avg_score:,.0f}"
        
        base_summary += f" across {chrom_info}, {score_info}"
    
    if collection.source_file:
        base_summary += f"\nSource: {collection.source_file}"
    
    return base_summary 