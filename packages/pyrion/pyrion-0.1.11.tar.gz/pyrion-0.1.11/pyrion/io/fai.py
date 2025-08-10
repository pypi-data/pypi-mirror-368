"""FASTA indexing functionality using fast C extension."""

from __future__ import annotations

from typing import Union, Optional
from pathlib import Path

from ..core.fai import FaiEntry, FaiStore
from .._faiparser import parse_fasta_to_fai

def create_fasta_index(fasta_file: Union[str, Path], fai_file: Optional[Union[str, Path]] = None) -> FaiStore:
    fasta_file = Path(fasta_file)
    
    if not fasta_file.exists():
        raise FileNotFoundError(f"FASTA file not found: {fasta_file}")
    
    fai_tuples = parse_fasta_to_fai(str(fasta_file))
    fai_store = FaiStore()
    
    for name, length, offset, line_bases, line_bytes in fai_tuples:
        entry = FaiEntry(
            name=name,
            length=length,
            offset=offset,
            line_bases=line_bases,
            line_bytes=line_bytes
        )
        fai_store[entry.name] = entry

    if fai_file is not None:
        fai_store.save_to_file(fai_file)
    else:
        default_fai_file = fasta_file.with_suffix(fasta_file.suffix + '.fai')
        fai_store.save_to_file(default_fai_file)
    
    return fai_store


def load_fasta_index(fai_file: Union[str, Path]) -> FaiStore:
    return FaiStore.load_from_file(fai_file)


def get_or_create_fasta_index(fasta_file: Union[str, Path], force_recreate: bool = False) -> FaiStore:
    fasta_file = Path(fasta_file)
    fai_file = fasta_file.with_suffix(fasta_file.suffix + '.fai')
    
    if force_recreate or not fai_file.exists() or fai_file.stat().st_mtime < fasta_file.stat().st_mtime:
        return create_fasta_index(fasta_file, fai_file)
    else:
        return load_fasta_index(fai_file)
