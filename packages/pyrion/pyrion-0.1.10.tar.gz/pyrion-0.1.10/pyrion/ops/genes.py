"""Gene and transcript operations."""

import numpy as np
from typing import List, Protocol

from .interval_ops import merge_intervals
from .. import Transcript
from ..core.intervals import GenomicInterval
from ..core.nucleotide_sequences import NucleotideSequence
from ..core_types import Strand


class SequenceAccessor(Protocol):
    """Protocol for sequence accessors (TwoBitAccessor, FastaAccessor)."""
    def fetch(self, chrom: str, start: int, end: int, strand: Strand) -> NucleotideSequence:
        """Fetch sequence from chrom:start-end."""
        ...


def merge_transcript_intervals(
    transcripts: List[Transcript],
    cds_only: bool = False,
    use_numba: bool = True
) -> List[GenomicInterval]:
    """Merge overlapping or adjacent intervals from multiple transcripts."""
    if not transcripts:
        return []

    chrom = transcripts[0].chrom
    for transcript in transcripts:
        if transcript.chrom != chrom:
            raise ValueError(f"All transcripts must be same chromosome. Found {chrom} and {transcript.chrom}")

    all_intervals = []
    for transcript in transcripts:
        intervals = transcript.cds_blocks if cds_only else transcript.blocks
        if intervals.size > 0:
            all_intervals.append(intervals)

    if not all_intervals:
        return []

    combined = np.concatenate(all_intervals, axis=0)
    merged_array = merge_intervals(combined, use_numba=use_numba)

    return [
        GenomicInterval(
            chrom=chrom,
            start=int(start),
            end=int(end),
            strand=Strand.UNKNOWN,
            id=None
        )
        for start, end in merged_array
    ]


def _extract_sequence_from_blocks(
    accessor: SequenceAccessor,
    chrom: str,
    blocks: np.ndarray,
    transcript_strand: Strand
) -> NucleotideSequence:
    if blocks.size == 0:
        return NucleotideSequence.from_string("")
    
    seq_parts = []
    for start, end in blocks:
        seq = accessor.fetch(chrom, int(start), int(end), Strand.PLUS)
        seq_parts.append(seq.to_string())
    full_sequence = ''.join(seq_parts)
    if transcript_strand == Strand.MINUS:
        nt_seq = NucleotideSequence.from_string(full_sequence)
        return nt_seq.reverse_complement()
    else:
        return NucleotideSequence.from_string(full_sequence)


def extract_cds_sequence(transcript: Transcript, accessor: SequenceAccessor) -> NucleotideSequence:
    return _extract_sequence_from_blocks(
        accessor, transcript.chrom, transcript.cds_blocks, transcript.strand
    )


def extract_exon_sequence(transcript: Transcript, accessor: SequenceAccessor) -> NucleotideSequence:
    return _extract_sequence_from_blocks(
        accessor, transcript.chrom, transcript.blocks, transcript.strand
    )


def extract_utr5_sequence(transcript: Transcript, accessor: SequenceAccessor) -> NucleotideSequence:
    return _extract_sequence_from_blocks(
        accessor, transcript.chrom, transcript.utr5_blocks, transcript.strand
    )


def extract_utr3_sequence(transcript: Transcript, accessor: SequenceAccessor) -> NucleotideSequence:
    return _extract_sequence_from_blocks(
        accessor, transcript.chrom, transcript.utr3_blocks, transcript.strand
    )

# TODO: extract introns sequences?

