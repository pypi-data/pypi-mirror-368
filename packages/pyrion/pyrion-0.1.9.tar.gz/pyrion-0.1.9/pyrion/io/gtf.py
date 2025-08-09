"""High-performance GTF format I/O support using C extension."""

import gzip
import re
from typing import Union, List, Iterator, Optional, TextIO
from pathlib import Path

from ..core.genes import TranscriptsCollection
from ..core.gene_data import GeneData
from .._gtfparser import parse_gtf_chunk


class GTFChunkReader:
    def __init__(self, file_path: Union[str, Path], chunk_size_mb: int = 512):
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size_mb * 1024 * 1024  # Convert MB to bytes
        self.is_gzipped = self.file_path.suffix.lower() == '.gz'
        
    def _open_file(self) -> TextIO:
        if self.is_gzipped:
            return gzip.open(self.file_path, 'rt', encoding='utf-8')
        else:
            return open(self.file_path, 'r', encoding='utf-8')
    
    def read_gene_chunks(self) -> Iterator[List[str]]:
        with self._open_file() as f:
            current_gene_id = None
            buffer = []
            
            while True:
                chunk_text = f.read(self.chunk_size)
                if not chunk_text:
                    # End of file - yield remaining buffer
                    if buffer:
                        yield buffer
                    break
                
                lines = chunk_text.split('\n')
                if chunk_text.endswith('\n'):
                    complete_lines = lines
                    incomplete_line = ''
                else:
                    complete_lines = lines[:-1]
                    incomplete_line = lines[-1]
                
                for line in complete_lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    gene_id = self._extract_gene_id_fast(line)
                    if not gene_id:
                        continue
                    
                    if current_gene_id is None:
                        current_gene_id = gene_id
                    
                    if gene_id == current_gene_id:
                        # Same gene - add to buffer
                        buffer.append(line)
                    else:
                        # New gene - yield current buffer and start new one
                        if buffer:
                            yield buffer
                        buffer = [line]
                        current_gene_id = gene_id
                
                # Handle incomplete line for next iteration
                if incomplete_line:
                    # Read until we get the complete line
                    rest_of_line = f.readline()
                    complete_line = incomplete_line + rest_of_line
                    
                    line = complete_line.strip()
                    if line and not line.startswith('#'):
                        gene_id = self._extract_gene_id_fast(line)
                        if gene_id:
                            if gene_id == current_gene_id:
                                buffer.append(line)
                            else:
                                if buffer:
                                    yield buffer
                                buffer = [line]
                                current_gene_id = gene_id
    
    @staticmethod
    def _extract_gene_id_fast(line: str) -> Optional[str]:
        tab_count = 0
        attr_start = 0
        
        for i, char in enumerate(line):
            if char == '\t':
                tab_count += 1
                if tab_count == 8:  # After 8th tab is the attributes column
                    attr_start = i + 1
                    break
        
        if tab_count < 8:
            return None
        
        # Look for gene_id pattern in attributes
        attrs = line[attr_start:]
        match = re.search(r'gene_id\s+"([^"]+)"', attrs)
        return match.group(1) if match else None


def read_gtf(file_path: Union[str, Path], 
             chunk_size_mb: int = 512) -> TranscriptsCollection:
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"GTF file not found: {file_path}")
    
    reader = GTFChunkReader(file_path, chunk_size_mb)
    all_transcripts = []
    all_gene_mapping = {}
    processed_genes = 0
    
    for chunk_lines in reader.read_gene_chunks():
        transcripts, gene_mapping = parse_gtf_chunk(chunk_lines)
        
        all_transcripts.extend(transcripts)
        all_gene_mapping.update(gene_mapping)
        processed_genes += 1

    collection = TranscriptsCollection(transcripts=all_transcripts, source_file=str(file_path))
    gene_data = GeneData(source_file=str(file_path))
    for transcript_id, gene_id in all_gene_mapping.items():
        gene_data.add_gene_transcript_mapping(gene_id, transcript_id)
    
    collection.bind_gene_data(gene_data)
    
    return collection 