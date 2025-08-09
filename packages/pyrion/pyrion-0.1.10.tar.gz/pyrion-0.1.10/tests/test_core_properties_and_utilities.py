"""Test core properties, utilities, and algorithmic edge cases.

This module focuses on testing:
- Core transcript and gene properties that are fundamental to genomics analysis
- Utility functions for constants, amino acid analysis, and data type handling  
- Algorithm threshold behaviors and performance-critical code paths
- Edge cases and error handling in core data structures
"""

import pytest
import numpy as np
from pyrion.core.strand import Strand
from pyrion.core.genes import Transcript
from pyrion.core.amino_acid_sequences import AminoAcidSequence
from pyrion.core_types import ExonType
from pyrion.ops.interval_ops import merge_intervals, intersect_intervals
from pyrion.ops.interval_collection_ops import merge_close_intervals
from pyrion.core.intervals import GenomicInterval


class TestGenomicsConstants:
    """Test genomics constants and enumerations."""
    
    def test_exon_prefixes(self):
        """Test EXON_PREFIXES constants."""
        from pyrion.constants import EXON_PREFIXES
        
        assert EXON_PREFIXES[ExonType.ALL] == "exon"
        assert EXON_PREFIXES[ExonType.CDS] == "cds_exon"
        assert EXON_PREFIXES[ExonType.UTR5] == "utr5_exon"
        assert EXON_PREFIXES[ExonType.UTR3] == "utr3_exon"
        assert len(EXON_PREFIXES) == 4
    
    def test_exon_numbering_constants(self):
        """Test exon numbering constants."""
        from pyrion.constants import EXON_NUMBER_START, EXON_ID_SEPARATOR
        
        assert EXON_NUMBER_START == 1
        assert EXON_ID_SEPARATOR == ":"


class TestAminoAcidAnalysis:
    """Test amino acid sequence analysis functions."""
    
    def test_count_amino_acids_in_sequence(self):
        """Test amino acid counting function."""
        from pyrion.core.amino_acid_auxiliary import count_amino_acids_in_sequence
        
        # Create a simple amino acid sequence
        aa_seq = AminoAcidSequence.from_string("ACDEFGHIKLMNPQRSTVWY")
        
        counts = count_amino_acids_in_sequence(aa_seq)
        
        # Should have 20 different amino acids, each with count 1
        assert isinstance(counts, dict)
        assert len(counts) == 20
        assert all(count == 1 for count in counts.values())
        assert "A" in counts
        assert "C" in counts
        assert "Y" in counts
    
    def test_count_amino_acids_with_duplicates(self):
        """Test amino acid counting with repeated amino acids."""
        from pyrion.core.amino_acid_auxiliary import count_amino_acids_in_sequence
        
        aa_seq = AminoAcidSequence.from_string("AAACCCGGG")
        counts = count_amino_acids_in_sequence(aa_seq)
        
        assert counts["A"] == 3
        assert counts["C"] == 3
        assert counts["G"] == 3
        assert len(counts) == 3


class TestTranscriptCoreProperties:
    """Test fundamental Transcript properties for genomic analysis."""
    
    @pytest.fixture
    def sample_transcript(self):
        """Create a sample transcript for testing."""
        return Transcript(
            blocks=np.array([[1000, 1200], [1500, 1700]], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="TEST001",
            cds_start=1050,
            cds_end=1650,
            biotype="protein_coding"
        )
    
    def test_transcript_span(self, sample_transcript):
        """Test transcript_span property."""
        span = sample_transcript.transcript_span
        
        assert isinstance(span, np.ndarray)
        assert span.shape == (2,)
        assert span[0] == 1000  # Start of first block
        assert span[1] == 1700  # End of last block
    
    def test_transcript_interval(self, sample_transcript):
        """Test transcript_interval property."""
        interval = sample_transcript.transcript_interval
        
        assert isinstance(interval, GenomicInterval)
        assert interval.chrom == "chr1"
        assert interval.start == 1000
        assert interval.end == 1700
        assert interval.strand == Strand.PLUS
        assert interval.id == "TEST001"
    
    def test_transcript_cds_interval(self, sample_transcript):
        """Test transcript_cds_interval property."""
        cds_interval = sample_transcript.transcript_cds_interval
        
        assert isinstance(cds_interval, GenomicInterval)
        assert cds_interval.chrom == "chr1"
        assert cds_interval.start == 1050
        assert cds_interval.end == 1650
        assert cds_interval.strand == Strand.PLUS
    
    def test_non_coding_transcript_cds_interval(self):
        """Test CDS interval for non-coding transcript."""
        non_coding = Transcript(
            blocks=np.array([[1000, 1200]], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="NC001"
        )
        
        cds_interval = non_coding.transcript_cds_interval
        assert cds_interval is None


class TestPerformanceCriticalPaths:
    """Test performance-critical algorithm paths and large dataset handling."""
    
    def test_merge_intervals_numba_threshold(self):
        """Test merge_intervals with large dataset to trigger numba."""
        # Create dataset larger than numba threshold (usually ~20k)
        large_intervals = np.random.randint(0, 100000, (25000, 2))
        large_intervals = np.sort(large_intervals, axis=1)  # Ensure start < end
        large_intervals = large_intervals[np.argsort(large_intervals[:, 0])]  # Sort by start
        
        # This should trigger the numba implementation
        result = merge_intervals(large_intervals, use_numba=True)
        
        assert isinstance(result, np.ndarray)
        assert result.shape[1] == 2
        assert len(result) <= len(large_intervals)  # Merged result should be smaller or equal
    
    def test_intersect_intervals_numba_threshold(self):
        """Test intersect_intervals with large dataset to trigger numba."""
        # Create two large datasets
        intervals1 = np.random.randint(0, 50000, (15000, 2))
        intervals1 = np.sort(intervals1, axis=1)
        intervals2 = np.random.randint(25000, 75000, (15000, 2))
        intervals2 = np.sort(intervals2, axis=1)
        
        # This should trigger the numba implementation
        result = intersect_intervals(intervals1, intervals2, use_numba=True)
        
        assert isinstance(result, np.ndarray)
        assert result.shape[1] == 2
    
    def test_merge_close_intervals_numba_path(self):
        """Test merge_close_intervals with conditions that trigger numba helpers."""
        from pyrion.core.intervals import GenomicIntervalsCollection
        
        # Create large collection with small gaps that will merge
        intervals = []
        for i in range(1000):
            start = i * 60  # 60bp spacing
            end = start + 50  # 50bp intervals, so 10bp gaps
            intervals.append(GenomicInterval("chr1", start, end, Strand.PLUS, f"interval_{i}"))
        
        collection = GenomicIntervalsCollection.from_intervals(intervals)
        
        # This should exercise the numba helper functions and merge intervals (10bp gaps < 15bp threshold)
        result = merge_close_intervals(collection, max_gap=15)
        
        assert isinstance(result, GenomicIntervalsCollection)
        assert len(result) < len(collection)  # Should merge some intervals


class TestGenomicsUtilities:
    """Test core genomics utility functions and data type operations."""
    
    def test_strand_utilities(self):
        """Test strand utility functions."""
        # Test from_int method
        plus_strand = Strand.from_int(1)
        minus_strand = Strand.from_int(-1)
        
        assert plus_strand == Strand.PLUS
        assert minus_strand == Strand.MINUS
        
        # Test to_char method
        assert Strand.PLUS.to_char() == "+"
        assert Strand.MINUS.to_char() == "-"
    
    def test_encoding_edge_cases(self):
        """Test encoding utility edge cases."""
        from pyrion.utils.encoding import encode_nucleotides
        
        # Test with mixed case
        result = encode_nucleotides("AtCg")
        assert isinstance(result, np.ndarray)
        assert len(result) == 4
        
        # Test with gaps
        result_with_gaps = encode_nucleotides("AT-GC")
        assert len(result_with_gaps) == 5


class TestGenomicsDataTypes:
    """Test genomics-specific data types and enumerations."""
    
    def test_core_types_enum_usage(self):
        """Test ExonType enum in realistic scenarios."""
        from pyrion.core_types import ExonType
        
        # Test all enum values are accessible
        assert ExonType.ALL is not None
        assert ExonType.CDS is not None
        assert ExonType.UTR5 is not None
        assert ExonType.UTR3 is not None
        
        # Test enum can be used in collections
        exon_types = [ExonType.ALL, ExonType.CDS]
        assert len(exon_types) == 2
        assert ExonType.ALL in exon_types


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling in core genomics operations."""
    
    def test_empty_transcript_blocks_error(self):
        """Test transcript with empty blocks."""
        with pytest.raises(IndexError):
            # This should fail when trying to access blocks[0] in transcript_span
            empty_transcript = Transcript(
                blocks=np.empty((0, 2), dtype=np.int32),
                strand=Strand.PLUS,
                chrom="chr1",
                id="EMPTY001"
            )
            _ = empty_transcript.transcript_span
    
    def test_invalid_interval_operations(self):
        """Test interval operations with invalid inputs."""
        # Test with malformed intervals
        invalid_intervals = np.array([[100, 50]], dtype=np.int32)  # end < start
        
        # Should still work but produce empty result
        result = merge_intervals(invalid_intervals)
        assert isinstance(result, np.ndarray)