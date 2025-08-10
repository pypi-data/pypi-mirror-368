"""Chain slicing operations with proper Q strand handling."""

import numpy as np
from typing import Optional
from ..core.genome_alignment import GenomeAlignment
from .interval_slicing import slice_intervals


def slice_chain_target_space(chain: GenomeAlignment, start: int, end: int, 
                             use_numba: bool = True) -> GenomeAlignment:
    if len(chain.blocks) == 0:
        return _create_empty_chain_copy(chain)
    
    t_coords = chain.blocks[:, :2]  # columns 0,1 are t_start, t_end
    sliced_t_coords = slice_intervals(t_coords, start, end, use_numba=use_numba)
    
    if len(sliced_t_coords) == 0:
        return _create_empty_chain_copy(chain)

    new_blocks = []
    for sliced_t_start, sliced_t_end in sliced_t_coords:
        orig_block_idx = _find_overlapping_target_block(chain.blocks, sliced_t_start, sliced_t_end)
        if orig_block_idx is None:
            continue
            
        orig_block = chain.blocks[orig_block_idx]
        orig_t_start, orig_t_end, orig_q_start, orig_q_end = orig_block
        
        t_length = orig_t_end - orig_t_start
        q_length = orig_q_end - orig_q_start
        
        if t_length == 0:
            continue
            
        left_trim_t = sliced_t_start - orig_t_start
        right_trim_t = orig_t_end - sliced_t_end
        left_trim_q = int((left_trim_t / t_length) * q_length)
        right_trim_q = int((right_trim_t / t_length) * q_length)
        
        if chain.q_strand == -1:
            new_q_start = orig_q_start + left_trim_q
            new_q_end = orig_q_end - right_trim_q
        else:
            new_q_start = orig_q_start + left_trim_q
            new_q_end = orig_q_end - right_trim_q
        
        if new_q_start >= new_q_end:
            continue
            
        new_blocks.append([sliced_t_start, sliced_t_end, new_q_start, new_q_end])
    
    if not new_blocks:
        return _create_empty_chain_copy(chain)
        
    return GenomeAlignment(
        chain_id=chain.chain_id,
        score=chain.score,
        t_chrom=chain.t_chrom,
        t_strand=chain.t_strand,
        q_chrom=chain.q_chrom,
        q_strand=chain.q_strand,
        blocks=np.array(new_blocks, dtype=np.int32),
        child_id=chain.child_id,
        q_size=chain.q_size,
        t_size=chain.t_size
    )


def slice_chain_query_space(chain: GenomeAlignment, start: int, end: int,
                          use_numba: bool = True) -> GenomeAlignment:
    if len(chain.blocks) == 0:
        return _create_empty_chain_copy(chain)
    
    q_coords = chain.blocks[:, 2:4]
    sliced_q_coords = slice_intervals(q_coords, start, end, use_numba=use_numba)
    
    if len(sliced_q_coords) == 0:
        return _create_empty_chain_copy(chain)
    
    new_blocks = []
    for sliced_q_start, sliced_q_end in sliced_q_coords:
        orig_block_idx = _find_overlapping_query_block(chain.blocks, sliced_q_start, sliced_q_end)
        if orig_block_idx is None:
            continue
            
        orig_block = chain.blocks[orig_block_idx]
        orig_t_start, orig_t_end, orig_q_start, orig_q_end = orig_block
        
        q_length = orig_q_end - orig_q_start
        t_length = orig_t_end - orig_t_start
        
        if q_length == 0:
            continue
            
        left_trim_q = sliced_q_start - orig_q_start
        right_trim_q = orig_q_end - sliced_q_end
        left_trim_t = int((left_trim_q / q_length) * t_length)
        right_trim_t = int((right_trim_q / q_length) * t_length)
        
        if chain.q_strand == -1:
            new_t_start = orig_t_start + right_trim_t
            new_t_end = orig_t_end - left_trim_t
        else:
            new_t_start = orig_t_start + left_trim_t
            new_t_end = orig_t_end - right_trim_t
        
        if new_t_start >= new_t_end:
            continue
            
        new_blocks.append([new_t_start, new_t_end, sliced_q_start, sliced_q_end])
    
    if not new_blocks:
        return _create_empty_chain_copy(chain)
        
    return GenomeAlignment(
        chain_id=chain.chain_id,
        score=chain.score,
        t_chrom=chain.t_chrom,
        t_strand=chain.t_strand,
        q_chrom=chain.q_chrom,
        q_strand=chain.q_strand,
        blocks=np.array(new_blocks, dtype=np.int32),
        child_id=chain.child_id,
        t_size=chain.t_size,
        q_size=chain.q_size
    )


def remove_chain_region_target_space(chain: GenomeAlignment, start: int, end: int,
                                    use_numba: bool = True) -> GenomeAlignment:
    from .interval_slicing import remove_intervals
    
    if len(chain.blocks) == 0:
        return _create_empty_chain_copy(chain)
    
    t_coords = chain.blocks[:, :2]
    new_t_coords = remove_intervals(t_coords, start, end, use_numba=use_numba)
    
    if len(new_t_coords) == 0:
        return _create_empty_chain_copy(chain)
    
    new_blocks = []
    for new_t_start, new_t_end in new_t_coords:
        orig_block_idx = _find_containing_target_block(chain.blocks, new_t_start, new_t_end)
        if orig_block_idx is not None:
            orig_block = chain.blocks[orig_block_idx]
            
            q_start, q_end = _map_target_to_query(
                orig_block, new_t_start, new_t_end, chain.q_strand
            )
            
            if q_start < q_end:
                new_blocks.append([new_t_start, new_t_end, q_start, q_end])
    
    if not new_blocks:
        return _create_empty_chain_copy(chain)
        
    return GenomeAlignment(
        chain_id=chain.chain_id,
        score=chain.score,
        t_chrom=chain.t_chrom,
        t_strand=chain.t_strand,
        q_chrom=chain.q_chrom,
        q_strand=chain.q_strand,
        blocks=np.array(new_blocks, dtype=np.int32),
        child_id=chain.child_id,
        t_size=chain.t_size,
        q_size=chain.q_size
    )


def _find_overlapping_target_block(blocks: np.ndarray, t_start: int, t_end: int) -> Optional[int]:
    for i, block in enumerate(blocks):
        block_t_start, block_t_end = block[0], block[1]
        if block_t_end > t_start and block_t_start < t_end:
            return i
    return None


def _find_overlapping_query_block(blocks: np.ndarray, q_start: int, q_end: int) -> Optional[int]:
    for i, block in enumerate(blocks):
        block_q_start, block_q_end = block[2], block[3]
        # Check for overlap
        if block_q_end > q_start and block_q_start < q_end:
            return i
    return None


def _find_containing_target_block(blocks: np.ndarray, t_start: int, t_end: int) -> Optional[int]:
    for i, block in enumerate(blocks):
        block_t_start, block_t_end = block[0], block[1]
        if block_t_start <= t_start and t_end <= block_t_end:
            return i
    return None


def _map_target_to_query(orig_block: np.ndarray, new_t_start: int, new_t_end: int, 
                        q_strand: int) -> tuple[int, int]:
    orig_t_start, orig_t_end, orig_q_start, orig_q_end = orig_block
    
    t_length = orig_t_end - orig_t_start
    q_length = orig_q_end - orig_q_start
    
    if t_length == 0:
        return orig_q_start, orig_q_start
    
    start_frac = (new_t_start - orig_t_start) / t_length
    end_frac = (new_t_end - orig_t_start) / t_length
    
    if q_strand == -1:
        new_q_end = orig_q_start + int(start_frac * q_length)
        new_q_start = orig_q_start + int(end_frac * q_length)
    else:
        new_q_start = orig_q_start + int(start_frac * q_length)
        new_q_end = orig_q_start + int(end_frac * q_length)
    
    return new_q_start, new_q_end


def _create_empty_chain_copy(chain: GenomeAlignment) -> GenomeAlignment:
    return GenomeAlignment(
        chain_id=chain.chain_id,
        score=0,
        t_chrom=chain.t_chrom,
        t_strand=chain.t_strand,
        q_chrom=chain.q_chrom,
        q_strand=chain.q_strand,
        blocks=np.empty((0, 4), dtype=np.int32),
        child_id=chain.child_id,
        t_size=chain.t_size,
        q_size=chain.q_size
    ) 