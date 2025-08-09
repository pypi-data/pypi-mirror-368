"""Chain alignment operations for projecting genomic intervals."""

from typing import List, Optional, Tuple, Dict
import numpy as np

from pyrion import GenomicInterval

try:
    import numba
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

from .. import GenomeAlignment, Transcript
from ..core.intervals import GenomicInterval
from ..core.strand import Strand


def project_intervals_through_chain(
    intervals: np.ndarray,
    chain_blocks: np.ndarray
) -> List[np.ndarray]:
    if len(intervals) == 0:
        return []
    if len(chain_blocks) == 0:
        return [np.array([[0, 0]], dtype=np.int64) for _ in range(len(intervals))]
    return _project_intervals_vectorized(intervals, chain_blocks)


def _project_intervals_vectorized(intervals: np.ndarray, chain_blocks: np.ndarray) -> List[np.ndarray]:
    if HAS_NUMBA:
        return _project_intervals_numba(intervals, chain_blocks)
    else:
        return _project_intervals_numpy(intervals, chain_blocks)


@numba.njit if HAS_NUMBA else lambda f: f
def _project_intervals_numba(intervals: np.ndarray, chain_blocks: np.ndarray) -> List[np.ndarray]:
    results = []
    
    # Extract block boundaries for efficient searching
    t_starts = chain_blocks[:, 0]
    t_ends = chain_blocks[:, 1]
    q_starts = chain_blocks[:, 2] 
    q_ends = chain_blocks[:, 3]
    
    chain_q_start = q_starts.min()
    chain_q_end = q_ends.max()
    
    for i in range(len(intervals)):
        interval_start, interval_end = intervals[i, 0], intervals[i, 1]
        first_possible_idx = np.searchsorted(t_ends, interval_start, side='right')
        last_possible_idx = np.searchsorted(t_starts, interval_end, side='right') - 1
        
        first_overlap_idx = -1
        last_overlap_idx = -1
        
        for block_idx in range(max(0, first_possible_idx), min(len(chain_blocks), last_possible_idx + 1)):
            t_start, t_end = t_starts[block_idx], t_ends[block_idx]
            
            if t_end > interval_start and t_start < interval_end:
                if first_overlap_idx == -1:
                    first_overlap_idx = block_idx
                last_overlap_idx = block_idx
        
        if first_overlap_idx != -1:
            first_t_start, first_q_start = t_starts[first_overlap_idx], q_starts[first_overlap_idx]
            last_t_start, last_q_start = t_starts[last_overlap_idx], q_starts[last_overlap_idx]

            projected_start = first_q_start + (interval_start - first_t_start)
            projected_end = last_q_start + (interval_end - last_t_start)

            projected_start = max(chain_q_start, min(chain_q_end, projected_start))
            projected_end = max(chain_q_start, min(chain_q_end, projected_end))

            if projected_start > projected_end:
                projected_start, projected_end = projected_end, projected_start
            
            results.append(np.array([[projected_start, projected_end]], dtype=np.int64))
        else:
            if first_possible_idx > 0 and first_possible_idx < len(chain_blocks):
                # In gap between blocks
                prev_q_end = q_ends[first_possible_idx - 1]
                next_q_start = q_starts[first_possible_idx]
                results.append(np.array([[prev_q_end, next_q_start]], dtype=np.int64))
            else:
                results.append(np.array([[0, 0]], dtype=np.int64))
    
    return results


def _project_intervals_numpy(intervals: np.ndarray, chain_blocks: np.ndarray) -> List[np.ndarray]:
    """NumPy fallback implementation when numba is not available."""
    results = []
    
    t_starts = chain_blocks[:, 0]
    t_ends = chain_blocks[:, 1]
    q_starts = chain_blocks[:, 2] 
    q_ends = chain_blocks[:, 3]
    
    chain_q_start = q_starts.min()
    chain_q_end = q_ends.max()
    
    for interval_start, interval_end in intervals:
        first_possible_idx = np.searchsorted(t_ends, interval_start, side='right')
        last_possible_idx = np.searchsorted(t_starts, interval_end, side='right') - 1
        
        first_overlap_idx = None
        last_overlap_idx = None
        
        for block_idx in range(max(0, first_possible_idx), min(len(chain_blocks), last_possible_idx + 1)):
            t_start, t_end = chain_blocks[block_idx, 0], chain_blocks[block_idx, 1]
            
            if t_end > interval_start and t_start < interval_end:
                if first_overlap_idx is None:
                    first_overlap_idx = block_idx
                last_overlap_idx = block_idx
        
        if first_overlap_idx is not None:
            first_t_start, first_q_start = chain_blocks[first_overlap_idx, 0], chain_blocks[first_overlap_idx, 2]
            last_t_start, last_q_start = chain_blocks[last_overlap_idx, 0], chain_blocks[last_overlap_idx, 2]
            projected_start = first_q_start + (interval_start - first_t_start)
            projected_end = last_q_start + (interval_end - last_t_start)
            
            projected_start = max(chain_q_start, min(chain_q_end, projected_start))
            projected_end = max(chain_q_start, min(chain_q_end, projected_end))
            
            if projected_start > projected_end:
                projected_start, projected_end = projected_end, projected_start
            
            results.append(np.array([[projected_start, projected_end]], dtype=np.int64))
        else:
            if first_possible_idx > 0 and first_possible_idx < len(chain_blocks):
                prev_q_end = q_ends[first_possible_idx - 1]
                next_q_start = q_starts[first_possible_idx]
                results.append(np.array([[prev_q_end, next_q_start]], dtype=np.int64))
            else:
                results.append(np.array([[0, 0]], dtype=np.int64))
    
    return results


def project_intervals_through_genome_alignment(
    intervals: np.ndarray,
    genome_alignment
) -> List[np.ndarray]:
    """Convenience function to project intervals through a GenomeAlignment object."""
    return project_intervals_through_chain(
        intervals=intervals,
        chain_blocks=genome_alignment.blocks
    )


def project_intervals_through_genome_alignment_to_intervals(
    intervals: np.ndarray,
    genome_alignment,
    target_chrom: Optional[str] = None,
    target_strand: Optional[Strand] = None
) -> List[GenomicInterval]:
    """Project intervals through genome alignment and convert to GenomicInterval objects.
    
    Args:
        intervals: Array of intervals to project, shape (N, 2)
        genome_alignment: GenomeAlignment object to project through
        target_chrom: Target chromosome name (auto-detected if None)
        target_strand: Target strand (auto-detected if None)

    """
    if target_chrom is None:
        target_chrom = genome_alignment.q_chrom
    if target_strand is None:
        target_strand = Strand.from_int(genome_alignment.q_strand)
    
    projected_arrays = project_intervals_through_genome_alignment(intervals, genome_alignment)
    
    return [
        GenomicInterval(target_chrom, int(array[0][0]), int(array[0][1]), target_strand)
        for array in projected_arrays 
        if len(array) > 0 and not (array[0][0] == 0 and array[0][1] == 0)
    ]


def project_transcript_through_chain(transcript: Transcript, chain: GenomeAlignment, only_cds=False) -> GenomicInterval | None:
    if only_cds:
        arr = np.array([[transcript.cds_start, transcript.cds_end]])
    else:
        arr = np.array([transcript.transcript_span])
    projection = project_intervals_through_genome_alignment(arr, chain)
    if len(projection) == 0:
        return None
    else:
        return GenomicInterval(
            chrom=chain.q_chrom,
            start=int(projection[0][0][0]),
            end=int(projection[0][0][1]),
            strand=Strand.from_int(chain.t_strand),
            id=f"chain_{chain.chain_id}_transcript_{transcript.id}"
        )

def get_chain_target_interval(genome_alignment) -> GenomicInterval:
    if genome_alignment is None:
        raise ValueError("get_chain_target_interval: for some reason, provided genome_alignment object is None")

    if len(genome_alignment.blocks) == 0:
        raise ValueError("Chain has no blocks")
    
    start = int(genome_alignment.blocks[0, 0])
    end = int(genome_alignment.blocks[-1, 1])
    
    strand = Strand.from_int(genome_alignment.t_strand)
    chrom = genome_alignment.t_chrom
    if isinstance(chrom, bytes):
        chrom = chrom.decode('utf-8')
    
    return GenomicInterval(
        chrom=chrom,
        start=start,
        end=end,
        strand=strand,
        id=f"chain_{genome_alignment.chain_id}_target"
    )


def get_chain_query_interval(genome_alignment) -> GenomicInterval:
    if len(genome_alignment.blocks) == 0:
        raise ValueError("Chain has no blocks")
    
    start = int(genome_alignment.blocks[0, 2])
    end = int(genome_alignment.blocks[-1, 3])
    
    strand = Strand.from_int(genome_alignment.q_strand)
    return GenomicInterval(
        chrom=genome_alignment.q_chrom,
        start=start,
        end=end,
        strand=strand,
        id=f"chain_{genome_alignment.chain_id}_query"
    )


def get_chain_t_start(genome_alignment) -> int:
    if len(genome_alignment.blocks) == 0:
        raise ValueError("Chain has no blocks")
    
    return int(genome_alignment.blocks[0, 0])


def get_chain_t_end(genome_alignment) -> int:
    if len(genome_alignment.blocks) == 0:
        raise ValueError("Chain has no blocks")
    
    return int(genome_alignment.blocks[-1, 1])


def get_chain_q_start(genome_alignment) -> int:
    if len(genome_alignment.blocks) == 0:
        raise ValueError("Chain has no blocks")
    
    return int(genome_alignment.blocks[0, 2])


def get_chain_q_end(genome_alignment) -> int:
    if len(genome_alignment.blocks) == 0:
        raise ValueError("Chain has no blocks")
    
    return int(genome_alignment.blocks[-1, 3])


def split_genome_alignment(
    chain: GenomeAlignment,
    intersected_transcripts: List[Transcript],
    window_size: int = 1_000_000,
    intergenic_margin: int = 10_000,
) -> Tuple[List[GenomeAlignment], Dict[int, List[str]]]:

    t_start, t_end = chain.blocks[:, 0].min(), chain.blocks[:, 1].max()
    chain_length = t_end - t_start

    if chain_length < window_size * 1.5:
        return [GenomeAlignment(**{**chain.__dict__, "child_id": 0})], {0: [t.id for t in intersected_transcripts]}

    transcript_spans = np.array([
        [tr.blocks[0, 0], tr.blocks[-1, 1]]
        for tr in intersected_transcripts if tr.blocks.size > 0
    ], dtype=int)

    if transcript_spans.size == 0:
        cut_points = list(range(t_start + window_size, t_end, window_size))
    else:
        transcript_spans = transcript_spans[np.argsort(transcript_spans[:, 0])]
        gaps = []
        for i in range(len(transcript_spans) - 1):
            gap_start, gap_end = transcript_spans[i, 1], transcript_spans[i + 1, 0]
            if gap_end - gap_start >= intergenic_margin:
                gaps.append((gap_start + gap_end) // 2)

        cut_points = []
        current = t_start
        while current + window_size < t_end:
            target = current + window_size
            nearby = [g for g in gaps if abs(g - target) < window_size // 2]
            if nearby:
                best = min(nearby, key=lambda g: abs(g - target))
                cut_points.append(best)
                current = best
            else:
                cut_points.append(target)
                current = target

    boundaries = [t_start] + cut_points + [t_end]
    subchains = []
    transcript_mapping = {}

    for i, (start, end) in enumerate(zip(boundaries[:-1], boundaries[1:])):
        block_mask = (chain.blocks[:, 1] > start) & (chain.blocks[:, 0] < end)
        block_idxs = np.where(block_mask)[0]
        if len(block_idxs) == 0:
            continue

        new_blocks = chain.blocks[block_idxs].copy()
        new_blocks[:, 0] = np.clip(new_blocks[:, 0], start, end)
        new_blocks[:, 1] = np.clip(new_blocks[:, 1], start, end)

        for j, orig_idx in enumerate(block_idxs):
            t0, t1, q0, q1 = chain.blocks[orig_idx]
            t_start_new, t_end_new = new_blocks[j, 0], new_blocks[j, 1]
            if t1 > t0:
                ratio_start = (t_start_new - t0) / (t1 - t0)
                ratio_end = (t_end_new - t0) / (t1 - t0)
                q_len = q1 - q0
                new_blocks[j, 2] = q0 + int(ratio_start * q_len)
                new_blocks[j, 3] = q0 + int(ratio_end * q_len)

        subchains.append(GenomeAlignment(
            chain_id=chain.chain_id,
            score=-1,
            t_chrom=chain.t_chrom,
            t_strand=chain.t_strand,
            q_chrom=chain.q_chrom,
            q_strand=chain.q_strand,
            blocks=new_blocks,
            child_id=i,
            t_size=chain.t_size,
            q_size=chain.q_size,
        ))

        overlapping_transcripts = [
            tr.id for tr in intersected_transcripts
            if tr.blocks.size > 0 and not (tr.blocks[-1, 1] <= start or tr.blocks[0, 0] >= end)
        ]
        transcript_mapping[i] = overlapping_transcripts

    return subchains, transcript_mapping
