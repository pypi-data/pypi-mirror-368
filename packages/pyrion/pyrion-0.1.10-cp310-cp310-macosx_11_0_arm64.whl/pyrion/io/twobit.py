"""2bit file format support."""

from typing import Optional, List
from pathlib import Path

from ..core_types import Strand, ChromSizes
from ..core.intervals import GenomicInterval
from ..core.nucleotide_sequences import NucleotideSequence


class TwoBitAccessor:
    """Access sequences from 2bit files using py2bit."""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._chrom_sizes_cache: Optional[ChromSizes] = None
        
        try:
            import py2bit
            self._backend = py2bit.open(self.file_path)
        except ImportError as e:
            raise ImportError("py2bit is required for 2bit file support. Install with: pip install py2bit") from e
        except Exception as e:
            raise ValueError(f"Failed to open 2bit file {self.file_path}: {e}") from e
    
    def __repr__(self) -> str:
        try:
            chrom_sizes = self.chrom_sizes()
            num_chroms = len(chrom_sizes)
            total_length = sum(chrom_sizes.values())
            path_str = Path(self.file_path).name if len(self.file_path) > 50 else self.file_path
            
            if total_length >= 1_000_000_000:
                length_str = f"{total_length / 1_000_000_000:.1f}Gb"
            elif total_length >= 1_000_000:
                length_str = f"{total_length / 1_000_000:.1f}Mb" 
            elif total_length >= 1_000:
                length_str = f"{total_length / 1_000:.1f}kb"
            else:
                length_str = f"{total_length}bp"

            chrom_names = sorted(chrom_sizes.keys())
            if len(chrom_names) <= 3:
                chrom_preview = ", ".join(chrom_names)
            else:
                chrom_preview = ", ".join(chrom_names[:3]) + "..."
                
            return f"TwoBitAccessor('{path_str}', {num_chroms} chromosomes [{chrom_preview}], {length_str})"
        except Exception:
            return f"TwoBitAccessor('{self.file_path}')"
    
    def fetch(self, chrom: str, start: int, end: int, strand: Strand = Strand.PLUS) -> NucleotideSequence:
        available_chroms = self.chrom_names()
        if chrom not in available_chroms:
            raise ValueError(f"Chromosome '{chrom}' not found in {self.file_path}. "
                             f"Available: {sorted(available_chroms)}")

        if not self.validate_interval(chrom, start, end):
            chrom_size = self.chrom_sizes()[chrom]
            raise ValueError(f"Invalid coordinates {chrom}:{start}-{end}. "
                             f"Chromosome size: {chrom_size}")
        
        try:
            seq_str = self._backend.sequence(chrom, start, end)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {chrom}:{start}-{end} from {self.file_path}: {e}") from e
        
        sequence = NucleotideSequence.from_string(
            seq_str,
            metadata={
                'chrom': chrom,
                'start': start,
                'end': end,
                'source': self.file_path
            }
        )
        
        if strand == Strand.MINUS:
            sequence = sequence.reverse_complement()
        
        return sequence
    
    def fetch_interval(self, interval: GenomicInterval) -> NucleotideSequence:
        return self.fetch(interval.chrom, interval.start, interval.end, interval.strand)
    
    def chrom_names(self) -> List[str]:
        return self._backend.chroms()
    
    def chrom_sizes(self) -> ChromSizes:
        if self._chrom_sizes_cache is None:
            self._chrom_sizes_cache = dict(self._backend.chroms())
        return self._chrom_sizes_cache
    
    def validate_interval(self, chrom: str, start: int, end: int) -> bool:
        sizes = self.chrom_sizes()
        if chrom not in sizes:
            return False
        
        chrom_size = sizes[chrom]
        return 0 <= start < end <= chrom_size
    
    def close(self):
        if hasattr(self._backend, 'close'):
            self._backend.close()
    
    def list_chromosomes(self) -> None:
        chrom_sizes = self.chrom_sizes()
        print(f"\nAvailable chromosomes in {Path(self.file_path).name}:")
        print("-" * 50)
        
        for chrom in sorted(chrom_sizes.keys()):
            size = chrom_sizes[chrom]
            if size >= 1_000_000:
                size_str = f"{size / 1_000_000:.1f}M"
            elif size >= 1_000:
                size_str = f"{size / 1_000:.1f}K"  
            else:
                size_str = f"{size}"
            print(f"{chrom:>15}: {size_str:>8} bp")
        
        print(f"\nTotal: {len(chrom_sizes)} chromosomes")
