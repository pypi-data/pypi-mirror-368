"""Chain format I/O support.

This reader streams large chain files and parses them in batches to avoid
exceeding the C-extension limit on number of chunks per call and to reduce
peak memory usage. The public API remains unchanged.
"""

import gzip
from typing import Union, Optional, Iterator, List, Tuple
from pathlib import Path

from ..core.genome_alignment import GenomeAlignmentsCollection
from .._chainparser import parse_many_chain_chunks, parse_chain_chunk


def read_chain_file(file_path: Union[str, Path],
                    min_score: Optional[int] = None) -> GenomeAlignmentsCollection:
    """Read a .chain or .chain.gz file and return parsed alignments.

    Internally parses in batches (<= 1_000_000 chunks per call) to satisfy the
    C-extension limit and to keep memory bounded for very large files.
    """
    file_path = Path(file_path)
    alignments: List = []
    # Choose an internal batch size safely under the 1M limit.
    MAX_CHUNKS_PER_CALL = 500_000

    alignments.extend(
        _parse_chunks_in_batches(
            _iter_chain_chunks(file_path, min_score=min_score),
            max_chunks_per_call=MAX_CHUNKS_PER_CALL,
            min_score=min_score,
        )
    )

    return GenomeAlignmentsCollection(alignments=alignments, source_file=str(file_path))


def _iter_chain_chunks(file_path: Path, min_score: Optional[int] = None) -> Iterator[bytes]:
    """Yield raw chain chunks (bytes) one-by-one from (gzipped) chain file.

    If min_score is provided, pre-filter chunks by parsing the header line's
    score to avoid buffering unnecessary data.
    """
    is_gzipped = file_path.suffix.lower() == '.gz'

    # Fast path for small gz files: read whole content then split. Speeds up
    # gzip performance for test fixtures while large files still stream.
    if is_gzipped:
        try:
            if file_path.stat().st_size <= 16 * 1024 * 1024:  # 16 MB compressed
                content = _read_gzip(file_path)
                yield from _iter_chunks_from_bytes(content, min_score=min_score)
                return
        except Exception:
            # If anything fails, fall back to streaming mode below
            pass

    opener = gzip.open if is_gzipped else open

    with opener(file_path, 'rb') as f:  # type: ignore[arg-type]
        yield from _iter_chunks_from_stream(f, min_score=min_score)



def _read_gzip(path: Path) -> bytes:
    with gzip.open(path, 'rb') as gf:
        return gf.read()


def _iter_chunks_from_bytes(content: bytes, min_score: Optional[int]) -> Iterator[bytes]:
    parts = content.split(b"chain ")
    for part in parts[1:]:
        chunk = (b"chain " + part).strip()
        if not chunk:
            continue
        if min_score is not None:
            header = chunk.split(b"\n", 1)[0]
            keep = _header_meets_min_score(header, min_score)
            if not keep:
                continue
        yield chunk


def _iter_chunks_from_stream(bytestream, min_score: Optional[int]) -> Iterator[bytes]:
    current: List[bytes] = []
    header_score_ok = True  # default true until header parsed

    for line in bytestream:
        if line.startswith(b"chain "):
            # Emit previous chunk if any and allowed by score
            if current and header_score_ok:
                yield b"".join(current).strip()
            # Start new chunk
            current = [line]
            header_score_ok = True
            if min_score is not None:
                header_score_ok = _header_meets_min_score(line, min_score)
        else:
            # Accumulate lines into current chunk
            if current:  # only after we've seen a header
                current.append(line)

    # EOF: emit last chunk if any and allowed
    if current and header_score_ok:
        yield b"".join(current).strip()


def _header_meets_min_score(header_line: bytes, min_score: int) -> bool:
    """Return True if header score >= min_score, False if below or parse fails."""
    try:
        tokens = header_line.split()
        if len(tokens) > 1:
            return int(tokens[1]) >= min_score
    except Exception:
        # If header parsing fails, keep the chunk to let the parser decide
        return True
    return True


def _parse_chunks_in_batches(
    chunk_iter: Iterator[bytes],
    max_chunks_per_call: int,
    min_score: Optional[int],
) -> List:
    # Limit by both chunk count and cumulative block count
    MAX_BLOCKS_PER_CALL = 900_000  # headroom below native 1M limit

    batch: List[bytes] = []
    batch_blocks: int = 0
    results: List = []

    def _flush_batch():
        nonlocal batch_blocks
        if not batch:
            return
        if min_score is not None:
            results.extend(parse_many_chain_chunks(batch, min_score))
        else:
            results.extend(parse_many_chain_chunks(batch))
        batch.clear()
        batch_blocks = 0

    for chunk in chunk_iter:
        blocks = _estimate_block_count(chunk)

        # If a single chunk would exceed the block limit in a batch, parse it alone
        if blocks > MAX_BLOCKS_PER_CALL:
            # Flush current batch first
            _flush_batch()
            # Parse single-chain path
            ga = parse_chain_chunk(chunk, min_score) if min_score is not None else parse_chain_chunk(chunk)
            if ga is not None:
                results.append(ga)
            continue

        # If adding this chunk would exceed either limit, flush
        if (
            len(batch) >= max_chunks_per_call
            or batch_blocks + blocks > MAX_BLOCKS_PER_CALL
        ):
            _flush_batch()

        # Add to batch
        batch.append(chunk)
        batch_blocks += blocks

    _flush_batch()
    return results


def _estimate_block_count(chunk: bytes) -> int:
    """Estimate number of alignment blocks in a chain chunk.

    Counts numeric lines after the header; robust to trailing whitespace.
    """
    count = 0
    first = True
    for line in chunk.splitlines():
        if first:
            first = False
            continue  # skip header
        line = line.strip()
        if not line:
            continue
        # Block lines start with a digit (size)
        c0 = line[:1]
        if c0 >= b"0" and c0 <= b"9":
            count += 1
    return count
