"""SequencesCollection: a clean wrapper over a mapping of sequences."""

from __future__ import annotations

from collections.abc import MutableMapping, Iterator
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Tuple, Union

from .nucleotide_sequences import NucleotideSequence, SequenceType
from .amino_acid_sequences import AminoAcidSequence


SequenceLike = Union[NucleotideSequence, AminoAcidSequence]


def _detect_sequence_type(sequence: SequenceLike) -> SequenceType:
    if isinstance(sequence, AminoAcidSequence):
        return SequenceType.PROTEIN
    if isinstance(sequence, NucleotideSequence):
        return SequenceType.RNA if sequence.is_rna else SequenceType.DNA
    raise TypeError("Unsupported sequence type")


@dataclass(frozen=True)
class _CollectionMeta:
    sequence_type: Optional[SequenceType] = None
    is_alignment: bool = False


class SequencesCollection(MutableMapping[str, SequenceLike]):
    def __init__(self, data: Optional[Mapping[str, SequenceLike]] = None):
        self._data: Dict[str, SequenceLike] = {}
        self._meta: _CollectionMeta = _CollectionMeta()
        if data:
            # Add via add() to enforce type consistency
            for key, value in data.items():
                self.add(key, value)

    # Mapping core
    def __getitem__(self, key: str) -> SequenceLike:
        return self._data[key]

    def __setitem__(self, key: str, value: SequenceLike) -> None:
        # Default behavior: do not overwrite existing keys without explicit force
        if key in self._data:
            raise KeyError(f"Key '{key}' already exists. Use add(..., force=True) to overwrite.")
        self._check_and_set_type(value)
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    # Convenience mutators
    def add(self, key: str, value: SequenceLike, *, force: bool = False) -> None:
        """Add a sequence. If key exists and force=False, raise; if force=True, overwrite."""
        self._check_and_set_type(value)
        if self._meta.is_alignment and len(self._data) > 0:
            aligned_len = len(next(iter(self._data.values())))
            if len(value) != aligned_len:
                raise ValueError(
                    f"Aligned collection requires equal lengths: expected {aligned_len}, got {len(value)}"
                )
        if not force and key in self._data:
            raise KeyError(f"Key '{key}' already exists. Set force=True to overwrite.")
        self._data[key] = value

    def delete(self, key: str) -> None:
        """Remove a sequence by key."""
        del self._data[key]

    @classmethod
    def from_dict(cls, data: Mapping[str, SequenceLike]) -> "SequencesCollection":
        return cls(data)

    @classmethod
    def from_list(cls, sequences: Iterable[SequenceLike]) -> "SequencesCollection":
        obj = cls()
        for i, seq in enumerate(sequences):
            obj.add(str(i), seq)
        return obj

    @property
    def is_alignment(self) -> bool:
        return self._meta.is_alignment

    @property
    def sequence_type(self) -> Optional[SequenceType]:
        return self._meta.sequence_type

    def ids(self) -> List[str]:
        return list(self._data.keys())

    def sequences(self) -> List[SequenceLike]:
        return list(self._data.values())

    def as_alignment(self, *, inplace: bool = False) -> "SequencesCollection":
        """Validate equal lengths and mark as alignment.

        If `inplace` is False (default), returns a new aligned collection.
        If `inplace` is True, sets the alignment flag on this instance and returns self.
        """
        lengths = {len(seq) for seq in self._data.values()}
        if len(lengths) > 1:
            raise ValueError("All sequences must have the same length to form an alignment")
        if inplace:
            self._meta = _CollectionMeta(sequence_type=self._meta.sequence_type, is_alignment=True)
            return self
        new = SequencesCollection(self._data)
        new._meta = _CollectionMeta(sequence_type=self._meta.sequence_type, is_alignment=True)  # type: ignore[attr-defined]
        return new

    def slice(self, start: int, end: int) -> "SequencesCollection":
        """Slice all sequences consistently. Requires aligned collection."""
        if not self.is_alignment:
            raise RuntimeError("slice() requires an aligned collection. Call as_alignment() first.")
        sliced = {k: v.slice(start, end) for k, v in self._data.items()}
        new = SequencesCollection(sliced)
        new._meta = _CollectionMeta(sequence_type=self._meta.sequence_type, is_alignment=True)  # type: ignore[attr-defined]
        return new

    # Internal helpers
    def _check_and_set_type(self, sequence: SequenceLike) -> None:
        seq_type = _detect_sequence_type(sequence)
        if self._meta.sequence_type is None:
            self._meta = _CollectionMeta(sequence_type=seq_type, is_alignment=self._meta.is_alignment)
            return
        if self._meta.sequence_type != seq_type:
            raise TypeError(
                f"All sequences in the collection must be of the same type. "
                f"Existing: {self._meta.sequence_type.value}, New: {seq_type.value}"
            )
        # If already aligned, enforce equal length on future additions via add()

