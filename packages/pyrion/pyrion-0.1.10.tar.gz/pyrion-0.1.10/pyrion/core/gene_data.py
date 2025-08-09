"""Gene data storage with multiple mappings."""

from typing import Dict, Set, Optional
from collections import defaultdict


class GeneData:
    """Gene data container with optional mappings for gene-transcript relationships, biotypes, and names."""
    
    def __init__(self, source_file: Optional[str] = None):
        self.source_file: Optional[str] = source_file
        
        self._gene_to_transcripts: Dict[str, Set[str]] = defaultdict(set)
        self._transcript_to_gene: Dict[str, str] = {}
        
        self._transcript_to_biotype: Dict[str, str] = {}
        self._gene_to_name: Dict[str, str] = {}
        self._name_to_gene: Dict[str, Set[str]] = defaultdict(set)  # One name can map to multiple genes
    
    def add_gene_transcript_mapping(self, gene_id: str, transcript_id: str) -> None:
        # Validate transcript not already mapped to different gene
        if transcript_id in self._transcript_to_gene:
            existing_gene = self._transcript_to_gene[transcript_id]
            if existing_gene != gene_id:
                raise ValueError(
                    f"Transcript {transcript_id} already mapped to {existing_gene}, "
                    f"cannot map to {gene_id}"
                )

        self._gene_to_transcripts[gene_id].add(transcript_id)
        self._transcript_to_gene[transcript_id] = gene_id
    
    def get_transcripts(self, gene_id: str) -> Set[str]:
        return self._gene_to_transcripts.get(gene_id, set()).copy()
    
    def get_gene(self, transcript_id: str) -> Optional[str]:
        return self._transcript_to_gene.get(transcript_id)

    def add_transcript_biotype(self, transcript_id: str, biotype: str) -> None:
        self._transcript_to_biotype[transcript_id] = biotype
    
    def get_transcript_biotype(self, transcript_id: str) -> Optional[str]:
        return self._transcript_to_biotype.get(transcript_id)
    
    # Gene name mapping methods
    def add_gene_name(self, gene_id: str, gene_name: str) -> None:
        self._gene_to_name[gene_id] = gene_name
        self._name_to_gene[gene_name].add(gene_id)
    
    def get_gene_name(self, gene_id: str) -> Optional[str]:
        return self._gene_to_name.get(gene_id)
    
    def get_genes_by_name(self, gene_name: str) -> Set[str]:
        return self._name_to_gene.get(gene_name, set()).copy()

    def has_gene(self, gene_id: str) -> bool:
        return gene_id in self._gene_to_transcripts
    
    def has_transcript(self, transcript_id: str) -> bool:
        return transcript_id in self._transcript_to_gene
    
    def has_gene_transcript_mapping(self) -> bool:
        return bool(self._gene_to_transcripts)
    
    def has_biotype_mapping(self) -> bool:
        return bool(self._transcript_to_biotype)
    
    def has_gene_name_mapping(self) -> bool:
        return bool(self._gene_to_name)

    @property
    def gene_ids(self) -> Set[str]:
        genes = set(self._gene_to_transcripts.keys())
        genes.update(self._gene_to_name.keys())
        return genes
    
    @property
    def transcript_ids(self) -> Set[str]:
        transcripts = set(self._transcript_to_gene.keys())
        transcripts.update(self._transcript_to_biotype.keys())
        return transcripts
    
    def get_gene_transcript_count(self) -> int:
        return len(self._transcript_to_gene)
    
    def get_biotype_count(self) -> int:
        return len(self._transcript_to_biotype)
    
    def get_gene_name_count(self) -> int:
        return len(self._gene_to_name)
    
    def summary(self) -> str:
        mappings = []
        if self.has_gene_transcript_mapping():
            mappings.append(f"gene-transcript: {self.get_gene_transcript_count()} pairs")
        if self.has_biotype_mapping():
            mappings.append(f"transcript-biotype: {self.get_biotype_count()} pairs")
        if self.has_gene_name_mapping():
            mappings.append(f"gene-name: {self.get_gene_name_count()} pairs")
        
        if not mappings:
            return "GeneData: No mappings available"
        
        source_info = f" from {self.source_file}" if self.source_file else ""
        return f"GeneData: {', '.join(mappings)}{source_info}"
    
    def __repr__(self) -> str:
        return self.summary()