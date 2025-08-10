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
    """Read gene data from TSV/CSV file and build mappings."""
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


def write_gene_data_tsv(
    gene_data: GeneData,
    file_path: Union[str, Path],
    include_gene_transcript: bool = True,
    include_transcript_biotype: bool = True,
    include_gene_name: bool = True,
    separator: str = '\t'
) -> None:
    file_path = Path(file_path)
    has_gene_transcript = gene_data.has_gene_transcript_mapping() and include_gene_transcript
    has_transcript_biotype = gene_data.has_biotype_mapping() and include_transcript_biotype
    has_gene_name = gene_data.has_gene_name_mapping() and include_gene_name
    
    if not any([has_gene_transcript, has_transcript_biotype, has_gene_name]):
        raise ValueError("No data mappings available to export")
    
    header = ["transcript_id"]
    if has_gene_transcript:
        header.append("gene_id")
    if has_transcript_biotype:
        header.append("transcript_biotype")
    if has_gene_name:
        header.append("gene_name")
    
    transcript_ids = set()
    if has_gene_transcript:
        transcript_ids.update(gene_data.transcript_ids)
    if has_transcript_biotype:
        transcript_ids.update(gene_data.transcript_ids)
    
    if not transcript_ids:
        raise ValueError("No transcript data available to export")
    
    with open(file_path, 'w') as f:
        f.write(separator.join(header) + '\n')

        for transcript_id in sorted(transcript_ids):
            row = [transcript_id]
            
            if has_gene_transcript:
                gene_id = gene_data.get_gene(transcript_id) or ""
                row.append(gene_id)
            
            if has_transcript_biotype:
                biotype = gene_data.get_transcript_biotype(transcript_id) or ""
                row.append(biotype)
            
            if has_gene_name:
                gene_id = gene_data.get_gene(transcript_id) if has_gene_transcript else None
                gene_name = ""
                if gene_id:
                    gene_name = gene_data.get_gene_name(gene_id) or ""
                row.append(gene_name)
            
            f.write(separator.join(row) + '\n')
