"""Gene data I/O support."""

from typing import Union, Optional, List, Dict
from pathlib import Path

from ..core.gene_data import GeneData


def resolve_index(column_idx: Union[int, str], header: List[str]) -> int | None:
    if column_idx is None:
        return None

    if isinstance(column_idx, int):
        return column_idx - 1

    if isinstance(column_idx, str):
        try:
            return header.index(column_idx)
        except ValueError:
            raise ValueError(f"Column '{column_idx}' not found in header")


def read_gene_data(
    file_path: Union[str, Path],
    gene_column: Optional[Union[int, str]] = None,
    transcript_id_column: Optional[Union[int, str]] = None,
    gene_name_column: Optional[Union[int, str]] = None,
    transcript_type_column: Optional[Union[int, str]] = None,
    separator: str = '\t',
    has_header: bool = True,
) -> GeneData:
    """Read gene data from TSV/CSV file and build mappings.
    
    Args:
        file_path: Path to the data file
        gene_column: Gene ID column index (1-based) or name. Optional.
        transcript_id_column: Transcript ID column index (1-based) or name. Optional.
        gene_name_column: Gene name column index (1-based) or name. Optional.
        transcript_type_column: Transcript type/biotype column index (1-based) or name. Optional.
        separator: Column separator. Default: '\t' (tab)
        has_header: Whether file has header row. If False, only numeric column indices work.

    Returns:
        GeneData object with available mappings built from the data

    Examples:
        # Build all mappings from biomart TSV with header
        gene_data = read_gene_data(
            "transcripts.tsv",
            gene_column="Gene stable ID",
            transcript_id_column="Transcript stable ID", 
            gene_name_column="Gene name",
            transcript_type_column="Transcript type",
            has_header=True
        )
        
        # Build from file without header using column indices (1-based)
        gene_data = read_gene_data(
            "file.tsv",
            gene_column=1,
            transcript_id_column=2,
            gene_name_column=5,
            transcript_type_column=6,
            has_header=False
        )
        
        # Build only transcript-biotype mapping
        gene_data = read_gene_data(
            "file.tsv",
            transcript_id_column="transcript_id",
            transcript_type_column="biotype"
        )
    """
    file_path = Path(file_path)

    gene_data = GeneData(source_file=str(file_path))
    with open(file_path, 'r') as f:
        lines = f.readlines()

    if has_header:
        header = lines[0].strip().split(separator)
        data_lines = lines[1:]
    else:
        header = None
        data_lines = lines

    transcript_column_idx = resolve_index(transcript_id_column, header)
    gene_column_idx = resolve_index(gene_column, header)
    gene_name_column_idx = resolve_index(gene_name_column, header)
    transcript_type_column_idx = resolve_index(transcript_type_column, header)

    fill_gene_to_transcripts = gene_column_idx is not None and transcript_column_idx is not None
    fill_gene_to_name = gene_name_column_idx is not None and gene_column_idx is not None
    fill_transcript_to_biotype = transcript_type_column_idx is not None and transcript_column_idx is not None

    for line in data_lines:
        line = line.strip().split(separator)
        transcript_id = line[transcript_column_idx]
        gene_id = line[gene_column_idx] if gene_column_idx is not None else None
        gene_name = line[gene_name_column_idx] if gene_name_column_idx is not None else None
        transcript_type = line[transcript_type_column_idx] if transcript_type_column_idx is not None else None

        if fill_gene_to_transcripts:
            gene_data.add_gene_transcript_mapping(gene_id, transcript_id)
        if fill_gene_to_name:
            gene_data.add_gene_name(gene_id, gene_name)
        if fill_transcript_to_biotype:
            gene_data.add_transcript_biotype(transcript_id, transcript_type)

    return gene_data
