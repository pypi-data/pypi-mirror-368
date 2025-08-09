"""I/O modules for various genomic file formats."""

# I/O functions
from .bed import read_bed12_file, read_narrow_bed_file
from .chain import read_chain_file
from .fasta import (
    read_fasta, write_fasta, read_dna_fasta, read_rna_fasta, read_protein_fasta, FastaAccessor
)
from .fai import (
    create_fasta_index, load_fasta_index, get_or_create_fasta_index
)
from .gene_data import read_gene_data
from .genepred import read_genepred_file, read_refflat_file
from .gtf import read_gtf
from .twobit import TwoBitAccessor

__all__ = [
    # BED format
    "read_bed12_file", "read_narrow_bed_file",
    # Chain format
    "read_chain_file",
    # GenePred format
    "read_genepred_file", "read_refflat_file",
    # GTF format
    "read_gtf",
    # 2bit format
    "TwoBitAccessor",
    # Gene data
    "read_gene_data",
    # FASTA format
    "read_fasta", "write_fasta", "read_dna_fasta", "read_rna_fasta", "read_protein_fasta", "FastaAccessor",
    # FASTA indexing
    "create_fasta_index", "load_fasta_index", "get_or_create_fasta_index",
]