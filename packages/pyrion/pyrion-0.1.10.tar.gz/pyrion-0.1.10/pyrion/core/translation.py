"""Translation tables for genetic code."""

from dataclasses import dataclass
from typing import Dict, Tuple

from ..utils.encoding import ADENINE, GUANINE, THYMINE, CYTOSINE
from ..utils.amino_acid_encoding import (
    ALANINE, ARGININE, ASPARAGINE, ASPARTIC_ACID, CYSTEINE,
    GLUTAMIC_ACID, GLUTAMINE, GLYCINE, HISTIDINE, ISOLEUCINE,
    LEUCINE, LYSINE, METHIONINE, PHENYLALANINE, PROLINE,
    SERINE, THREONINE, TRYPTOPHAN, TYROSINE, VALINE,
    STOP, UNKNOWN_AMINO_ACID
)


@dataclass
class TranslationTable:
    table_id: int
    name: str
    codon_table: Dict[tuple, int]  # (nt1, nt2, nt3) -> amino acid code
    start_codons: set[tuple]
    stop_codons: set[tuple]
    
    @classmethod
    def standard(cls) -> 'TranslationTable':
        """Standard genetic code (NCBI table 1)."""
        codon_table = {
            # TTT, TTC -> F (Phenylalanine)
            (THYMINE, THYMINE, THYMINE): PHENYLALANINE,
            (THYMINE, THYMINE, CYTOSINE): PHENYLALANINE,
            # TTA, TTG -> L (Leucine)
            (THYMINE, THYMINE, ADENINE): LEUCINE,
            (THYMINE, THYMINE, GUANINE): LEUCINE,
            # TCT, TCC, TCA, TCG -> S (Serine)
            (THYMINE, CYTOSINE, THYMINE): SERINE,
            (THYMINE, CYTOSINE, CYTOSINE): SERINE,
            (THYMINE, CYTOSINE, ADENINE): SERINE,
            (THYMINE, CYTOSINE, GUANINE): SERINE,
            # TAT, TAC -> Y (Tyrosine)
            (THYMINE, ADENINE, THYMINE): TYROSINE,
            (THYMINE, ADENINE, CYTOSINE): TYROSINE,
            # TAA, TAG -> * (Stop)
            (THYMINE, ADENINE, ADENINE): STOP,
            (THYMINE, ADENINE, GUANINE): STOP,
            # TGT, TGC -> C (Cysteine)
            (THYMINE, GUANINE, THYMINE): CYSTEINE,
            (THYMINE, GUANINE, CYTOSINE): CYSTEINE,
            # TGA -> * (Stop)
            (THYMINE, GUANINE, ADENINE): STOP,
            # TGG -> W (Tryptophan)
            (THYMINE, GUANINE, GUANINE): TRYPTOPHAN,
            
            # CTT, CTC, CTA, CTG -> L (Leucine)
            (CYTOSINE, THYMINE, THYMINE): LEUCINE,
            (CYTOSINE, THYMINE, CYTOSINE): LEUCINE,
            (CYTOSINE, THYMINE, ADENINE): LEUCINE,
            (CYTOSINE, THYMINE, GUANINE): LEUCINE,
            # CCT, CCC, CCA, CCG -> P (Proline)
            (CYTOSINE, CYTOSINE, THYMINE): PROLINE,
            (CYTOSINE, CYTOSINE, CYTOSINE): PROLINE,
            (CYTOSINE, CYTOSINE, ADENINE): PROLINE,
            (CYTOSINE, CYTOSINE, GUANINE): PROLINE,
            # CAT, CAC -> H (Histidine)
            (CYTOSINE, ADENINE, THYMINE): HISTIDINE,
            (CYTOSINE, ADENINE, CYTOSINE): HISTIDINE,
            # CAA, CAG -> Q (Glutamine)
            (CYTOSINE, ADENINE, ADENINE): GLUTAMINE,
            (CYTOSINE, ADENINE, GUANINE): GLUTAMINE,
            # CGT, CGC, CGA, CGG -> R (Arginine)
            (CYTOSINE, GUANINE, THYMINE): ARGININE,
            (CYTOSINE, GUANINE, CYTOSINE): ARGININE,
            (CYTOSINE, GUANINE, ADENINE): ARGININE,
            (CYTOSINE, GUANINE, GUANINE): ARGININE,
            
            # ATT, ATC, ATA -> I (Isoleucine)
            (ADENINE, THYMINE, THYMINE): ISOLEUCINE,
            (ADENINE, THYMINE, CYTOSINE): ISOLEUCINE,
            (ADENINE, THYMINE, ADENINE): ISOLEUCINE,
            # ATG -> M (Methionine)
            (ADENINE, THYMINE, GUANINE): METHIONINE,
            # ACT, ACC, ACA, ACG -> T (Threonine)
            (ADENINE, CYTOSINE, THYMINE): THREONINE,
            (ADENINE, CYTOSINE, CYTOSINE): THREONINE,
            (ADENINE, CYTOSINE, ADENINE): THREONINE,
            (ADENINE, CYTOSINE, GUANINE): THREONINE,
            # AAT, AAC -> N (Asparagine)
            (ADENINE, ADENINE, THYMINE): ASPARAGINE,
            (ADENINE, ADENINE, CYTOSINE): ASPARAGINE,
            # AAA, AAG -> K (Lysine)
            (ADENINE, ADENINE, ADENINE): LYSINE,
            (ADENINE, ADENINE, GUANINE): LYSINE,
            # AGT, AGC -> S (Serine)
            (ADENINE, GUANINE, THYMINE): SERINE,
            (ADENINE, GUANINE, CYTOSINE): SERINE,
            # AGA, AGG -> R (Arginine)
            (ADENINE, GUANINE, ADENINE): ARGININE,
            (ADENINE, GUANINE, GUANINE): ARGININE,
            
            # GTT, GTC, GTA, GTG -> V (Valine)
            (GUANINE, THYMINE, THYMINE): VALINE,
            (GUANINE, THYMINE, CYTOSINE): VALINE,
            (GUANINE, THYMINE, ADENINE): VALINE,
            (GUANINE, THYMINE, GUANINE): VALINE,
            # GCT, GCC, GCA, GCG -> A (Alanine)
            (GUANINE, CYTOSINE, THYMINE): ALANINE,
            (GUANINE, CYTOSINE, CYTOSINE): ALANINE,
            (GUANINE, CYTOSINE, ADENINE): ALANINE,
            (GUANINE, CYTOSINE, GUANINE): ALANINE,
            # GAT, GAC -> D (Aspartic acid)
            (GUANINE, ADENINE, THYMINE): ASPARTIC_ACID,
            (GUANINE, ADENINE, CYTOSINE): ASPARTIC_ACID,
            # GAA, GAG -> E (Glutamic acid)
            (GUANINE, ADENINE, ADENINE): GLUTAMIC_ACID,
            (GUANINE, ADENINE, GUANINE): GLUTAMIC_ACID,
            # GGT, GGC, GGA, GGG -> G (Glycine)
            (GUANINE, GUANINE, THYMINE): GLYCINE,
            (GUANINE, GUANINE, CYTOSINE): GLYCINE,
            (GUANINE, GUANINE, ADENINE): GLYCINE,
            (GUANINE, GUANINE, GUANINE): GLYCINE,
        }
        
        start_codons = {(ADENINE, THYMINE, GUANINE)}  # ATG
        stop_codons = {
            (THYMINE, ADENINE, ADENINE),  # TAA
            (THYMINE, ADENINE, GUANINE),  # TAG
            (THYMINE, GUANINE, ADENINE)   # TGA
        }
        
        return cls(
            table_id=1,
            name="Standard",
            codon_table=codon_table,
            start_codons=start_codons,
            stop_codons=stop_codons
        )
        
    @classmethod 
    def mitochondrial(cls) -> 'TranslationTable':
        """Mitochondrial genetic code (NCBI table 2)."""
        standard = cls.standard()
        codon_table = standard.codon_table.copy()
        
        # Mitochondrial differences:
        # UGA codes for Trp instead of Stop
        codon_table[(THYMINE, GUANINE, ADENINE)] = TRYPTOPHAN
        # AGA, AGG are Stop instead of Arg
        codon_table[(ADENINE, GUANINE, ADENINE)] = STOP
        codon_table[(ADENINE, GUANINE, GUANINE)] = STOP
        # AUA codes for Met instead of Ile
        codon_table[(ADENINE, THYMINE, ADENINE)] = METHIONINE
        
        start_codons = {
            (ADENINE, THYMINE, GUANINE),  # ATG
            (ADENINE, THYMINE, ADENINE),  # ATA
            (ADENINE, THYMINE, THYMINE),  # ATT
            (ADENINE, THYMINE, CYTOSINE)  # ATC
        }
        
        stop_codons = {
            (THYMINE, ADENINE, ADENINE),  # TAA
            (THYMINE, ADENINE, GUANINE),  # TAG
            (ADENINE, GUANINE, ADENINE),  # AGA
            (ADENINE, GUANINE, GUANINE)   # AGG
        }
        
        return cls(
            table_id=2, 
            name="Mitochondrial",
            codon_table=codon_table,
            start_codons=start_codons,
            stop_codons=stop_codons
        )
    
    def translate_codon(self, codon_codes: Tuple[int, int, int]) -> int:
        return self.codon_table.get(codon_codes, UNKNOWN_AMINO_ACID)
        
    def is_start_codon(self, codon_codes: Tuple[int, int, int]) -> bool:
        return codon_codes in self.start_codons
        
    def is_stop_codon(self, codon_codes: Tuple[int, int, int]) -> bool:
        return codon_codes in self.stop_codons
    
    def __repr__(self) -> str:
        return f"TranslationTable(id={self.table_id}, name='{self.name}', {len(self.codon_table)} codons, {len(self.stop_codons)} stops)"