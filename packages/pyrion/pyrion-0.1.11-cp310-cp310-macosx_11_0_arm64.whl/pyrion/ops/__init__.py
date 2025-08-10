"""Pyrion operations module."""

from .chains import (
    project_intervals_through_chain, 
    project_intervals_through_genome_alignment,
    project_intervals_through_genome_alignment_to_intervals,
    get_chain_target_interval,
    get_chain_query_interval,
    get_chain_t_start,
    get_chain_t_end,
    get_chain_q_start,
    get_chain_q_end,
    split_genome_alignment,
)
from .genes import merge_transcript_intervals
from .intervals import find_intersections, compute_overlap_size, intervals_to_array, array_to_intervals, chains_to_arrays, transcripts_to_arrays, projected_intervals_to_genomic_intervals
from .interval_slicing import slice_intervals, remove_intervals, invert_intervals
from .interval_ops import merge_intervals, intersect_intervals, subtract_intervals, intervals_union
from .interval_collection_ops import (
    merge_close_intervals,
    group_intervals_by_proximity, 
    split_intervals_on_gaps,
    intersect_collections,
    filter_collection,
    create_collections_from_mixed_intervals,
)
from .entity_ops import (
    get_transcript_cds_in_range,
    get_transcript_utrs_in_range,
    get_transcript_introns_in_range,
    merge_transcript_cds,
    merge_transcript_utrs,
    find_transcript_overlaps,
    subtract_transcript_regions,
    merge_genome_alignments,
    find_alignment_gaps,
    intersect_alignment_with_intervals,
)
from .transcript_slicing import slice_transcript, get_transcript_introns, remove_transcript_region
from .chain_slicing import (
    slice_chain_target_space,
    slice_chain_query_space, 
    remove_chain_region_target_space,
)
from .transcript_serialization import (
    transcript_to_bed12_string,
    transcripts_collection_to_bed12_string,
    save_transcripts_collection_to_bed12,
    transcript_to_dict,
    transcript_from_dict,
    transcripts_collection_to_dict,
    transcripts_collection_from_dict,
    save_transcripts_collection_to_json,
    load_transcripts_collection_from_json,
    transcripts_collection_summary_string,
)
from .interval_serialization import (
    genomic_interval_to_bed6_string,
    genomic_intervals_to_bed6_string,
    save_genomic_intervals_to_bed6,
)
from .sequence_serialization import (
    sequence_to_fasta_string,
)
from .data_consistency import check_data_consistency
from .chain_serialization import (
    genome_alignment_to_chain_string,
    genome_alignments_collection_to_chain_string,
    save_genome_alignments_collection_to_chain,
    genome_alignment_to_dict,
    genome_alignment_from_dict,
    genome_alignments_collection_to_dict,
    genome_alignments_collection_from_dict,
    save_genome_alignments_collection_to_json,
    load_genome_alignments_collection_from_json,
    genome_alignments_collection_summary_string,
)
from .transformations import (
    intervals_to_transcripts,
    bed_to_transcripts,
)

__all__ = [
    # Original operations
    "find_intersections",
    "compute_overlap_size", 
    "intervals_to_array",
    "array_to_intervals",
    "chains_to_arrays",
    "transcripts_to_arrays",
    "projected_intervals_to_genomic_intervals",
    "project_intervals_through_chain",
    "project_intervals_through_genome_alignment",
    "project_intervals_through_genome_alignment_to_intervals",
    "project_transcript_through_chain",
    "get_chain_target_interval",
    "get_chain_query_interval",
    "get_chain_t_start",
    "get_chain_t_end",
    "get_chain_q_start",
    "get_chain_q_end",
    "split_genome_alignment",
    "merge_transcript_intervals",
    # New low-level interval operations
    "slice_intervals",
    "remove_intervals",
    "invert_intervals",
    "merge_intervals",
    "intersect_intervals", 
    "subtract_intervals",
    "intervals_union",
    # New interval collection operations
    "merge_close_intervals",
    "group_intervals_by_proximity", 
    "split_intervals_on_gaps",
    "intersect_collections",
    "filter_collection",
    "create_collections_from_mixed_intervals",
    # New entity-specific operations
    "get_transcript_cds_in_range",
    "get_transcript_utrs_in_range",
    "get_transcript_introns_in_range",
    "merge_transcript_cds",
    "merge_transcript_utrs",
    "find_transcript_overlaps",
    "subtract_transcript_regions",
    "merge_genome_alignments",
    "find_alignment_gaps",
    "intersect_alignment_with_intervals",
    # Transcript slicing operations
    "slice_transcript",
    "get_transcript_introns",
    "remove_transcript_region",
    # Chain slicing operations
    "slice_chain_target_space",
    "slice_chain_query_space", 
    "remove_chain_region_target_space",
    "transcript_to_bed12_string",
    "transcripts_collection_to_bed12_string",
    "save_transcripts_collection_to_bed12",
    "transcript_to_dict",
    "transcript_from_dict",
    "transcripts_collection_to_dict",
    "transcripts_collection_from_dict",
    "save_transcripts_collection_to_json",
    "load_transcripts_collection_from_json",
    "transcripts_collection_summary_string",
    "genome_alignment_to_chain_string",
    "genome_alignments_collection_to_chain_string",
    "save_genome_alignments_collection_to_chain",
    "genome_alignment_to_dict",
    "genome_alignment_from_dict",
    "genome_alignments_collection_to_dict",
    "genome_alignments_collection_from_dict",
    "save_genome_alignments_collection_to_json",
    "load_genome_alignments_collection_from_json",
    "genome_alignments_collection_summary_string",
    "genomic_interval_to_bed6_string",
    "genomic_intervals_to_bed6_string", 
    "save_genomic_intervals_to_bed6",
    "sequence_to_fasta_string",
    "nucleotide_sequence_to_fasta_string",
    "amino_acid_sequence_to_fasta_string",
    "save_nucleotide_sequence_to_fasta",
    "save_amino_acid_sequence_to_fasta",
    # Data consistency checking
    "check_data_consistency",
    # Data transformations
    "intervals_to_transcripts",
    "bed_to_transcripts",
]