"""FASTA index (FAI) functionality for efficient random access to large FASTA files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Union
from pathlib import Path


@dataclass
class FaiEntry:
    """FASTA index entry for a single sequence."""
    
    name: str
    length: int
    offset: int
    line_bases: int
    line_bytes: int
    
    def __str__(self) -> str:
        """Format as FAI file line."""
        return f"{self.name}\t{self.length}\t{self.offset}\t{self.line_bases}\t{self.line_bytes}"
    
    def __repr__(self) -> str:
        return f"FaiEntry(name='{self.name}', length={self.length:,}, offset={self.offset}, line_bases={self.line_bases}, line_bytes={self.line_bytes})"
    
    @classmethod
    def from_fai_line(cls, line: str) -> 'FaiEntry':
        parts = line.strip().split('\t')
        if len(parts) != 5:
            raise ValueError(f"Invalid FAI line format: {line}")
        
        name, length, offset, line_bases, line_bytes = parts
        return cls(
            name=name,
            length=int(length),
            offset=int(offset),
            line_bases=int(line_bases),
            line_bytes=int(line_bytes)
        )
    
    def get_sequence_end_offset(self) -> int:
        full_lines = self.length // self.line_bases
        remaining_bases = self.length % self.line_bases
        full_lines_bytes = full_lines * self.line_bytes
        remaining_bytes = remaining_bases + (1 if remaining_bases > 0 else 0)  # +1 for newline if partial line
        
        return self.offset + full_lines_bytes + remaining_bytes


class FaiStore(dict[str, FaiEntry]):
    """Container for FASTA index entries with dict interface."""
    def __init__(self, entries: Optional[Dict[str, FaiEntry]] = None):
        super().__init__(entries or {})
    
    def save_to_file(self, filename: Union[str, Path]) -> None:
        filename = Path(filename)
        
        with open(filename, 'w') as f:
            for entry in self.values():
                f.write(f"{entry}\n")
    
    @classmethod
    def load_from_file(cls, filename: Union[str, Path]) -> 'FaiStore':
        filename = Path(filename)
        
        if not filename.exists():
            raise FileNotFoundError(f"FAI file not found: {filename}")
        
        entries = {}
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = FaiEntry.from_fai_line(line)
                    entries[entry.name] = entry
                except ValueError as e:
                    raise ValueError(f"Error parsing FAI file {filename} at line {line_num}: {e}")
        
        return cls(entries)
    
    def get_total_bases(self) -> int:
        return sum(entry.length for entry in self.values())
    
    def __repr__(self) -> str:
        return f"FaiStore({len(self)} sequences, {self.get_total_bases():,} total bases)"