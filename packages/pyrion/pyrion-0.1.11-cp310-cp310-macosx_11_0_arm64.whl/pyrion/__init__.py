"""
Pyrion: A Fast and Efficient Bioinformatics Library for Genomic Data Processing
"""

# Import version from the single source of truth
from ._version import __version__, __version_info__, __author__, __github__, __license__, __copyright__

# Configuration system
from .config import (
    get_available_cores, get_max_cores, set_max_cores,
    get_min_items_for_parallel, set_min_items_for_parallel,
    disable_parallel, enable_parallel, is_multiprocessing_available,
    get_config_summary
)

# Core data structures
from .core import (
    GenomicInterval, GenomicIntervalsCollection,
    Transcript, Gene,
    NucleotideSequence,
    GenomeAlignment, GenomeAlignmentsCollection,
)

# Type system
from .core_types import Strand, ExonType, ChainBlockArray, BlockArray, Metadata

# I/O operations
from .io import (
    # BED format
    read_bed12_file, read_narrow_bed_file,
    # Chain format
    read_chain_file,
    # 2bit format  
    TwoBitAccessor,
    # Gene data
    read_gene_data,
    # FASTA format
    read_fasta, write_fasta, read_dna_fasta, read_rna_fasta, FastaAccessor,
    # FASTA indexing
    create_fasta_index, load_fasta_index, get_or_create_fasta_index
)

# Visualization is now imported on-demand:
# from pyrion.visualization import VisualizationWindow, visualize_intervals, etc.

# Operations
# from .ops import (
#
# )

__all__ = [
    # Version info
    "__version__", "__version_info__", "__author__", "__github__",
    
    # Core types
    "Strand", "ExonType", "GenomicInterval", "Metadata", "BlockArray", "ChainBlockArray",
    
    # Sequences
    "NucleotideSequence", "SequenceType",
    
    # FASTA indexing
    "FaiEntry", "FaiStore",
    
    # Genes and annotations
    "Transcript", "TranscriptsCollection", "Gene", "GeneData",
    
    # Alignment chains
    "GenomeAlignment", "GenomeAlignmentsCollection",
    
    # I/O functions
    "read_bed12_file", "read_narrow_bed_file",
    "read_chain_file",
    "read_gene_data",
    "TwoBitAccessor",
    "read_fasta", "write_fasta", "read_dna_fasta", "read_rna_fasta", "FastaAccessor",
    "create_fasta_index", "load_fasta_index", "get_or_create_fasta_index",

    # Operations
    
    # Translation
    "TranslationTable",
    
    # Configuration
    "get_available_cores", "get_max_cores", "set_max_cores",
    "get_min_items_for_parallel", "set_min_items_for_parallel", 
    "disable_parallel", "enable_parallel", "is_multiprocessing_available",
    "get_config_summary",
    
    # Utilities
    "quick_start", "get_version", "get_version_info"
]


def get_version():
    """Get pyrion version."""
    return __version__


def get_version_info():
    """Get pyrion version as tuple."""
    return __version_info__


def cite():
    """Get citation information."""
    return {
        "software": "Pyrion",
        "version": __version__,
        "description": "A fast and efficient bioinformatics library for genomic data processing",
        "author": __author__,
        "license": __license__,
        "design_principles": [
            "Memory-efficient numpy-based storage",
            "Lazy evaluation and caching", 
            "Separation of data and operations",
            "Minimal dependencies",
            "Zero-cost abstractions"
        ]
    }


# Convenience imports for common workflows
def quick_start():
    guide = f"""
    Pyrion Quick Start Guide (v{__version__})
    =======================================
    
    # Import main components
    import pyrion as pyr
    
    # Read annotations
    genes = pyr.read_bed_as_genes("genes.bed")
    genes = pyr.read_gene_pred_as_genes("genes.gp")
    
    # Work with sequences (vectorized operations!)
    seq = pyr.NucleotideSequence.from_string("ATGAAATAG")
    
    # Fast numpy-based sequence analysis
    gc = pyr.gc_content(seq)           # GC content using abs(data) == 2
    purines = pyr.purine_content(seq)  # A+G using data > 0  
    cpg = pyr.cpg_content(seq)         # CpG dinucleotides
    comp = pyr.nucleotide_composition(seq)  # Full composition
    
    protein = pyr.translate_sequence(seq)
    
    # Process intervals
    intervals = [pyr.GenomicInterval("chr1", 100, 200)]
    merged = pyr.merge_intervals(intervals)
    
    # Chain mapping
    chains = pyr.read_chain_as_alignment_chains("mapping.chain")
    mapped = pyr.map_via_chains(intervals[0], chains)
    
    # Access sequences
    genome = pyr.TwoBitAccessor("genome.2bit")
    region_seq = genome.fetch("chr1", 1000, 2000)
    
    For detailed documentation, see the individual module docstrings.
    """
    print(guide)
