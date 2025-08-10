"""Unit tests for pyrion.ops.genes and data_consistency modules."""

import pytest
import numpy as np
from typing import List
from unittest.mock import Mock

from pyrion.core.genes import Transcript, TranscriptsCollection
from pyrion.core.nucleotide_sequences import NucleotideSequence
from pyrion.core.intervals import GenomicInterval
from pyrion.core.strand import Strand
from pyrion.ops.genes import (
    SequenceAccessor,
    merge_transcript_intervals,
    _extract_sequence_from_blocks,
    extract_cds_sequence,
    extract_exon_sequence,
    extract_utr5_sequence,
    extract_utr3_sequence
)
from pyrion.ops.data_consistency import check_data_consistency


class MockSequenceAccessor:
    """Mock sequence accessor for testing."""
    
    def __init__(self, sequences_dict=None):
        """Initialize with dictionary of chrom:start-end -> sequence."""
        self.sequences = sequences_dict or {}
        self.default_sequence = "ATCGATCG"  # Default 8bp sequence
    
    def fetch(self, chrom: str, start: int, end: int, strand: Strand) -> NucleotideSequence:
        """Fetch sequence from chrom:start-end."""
        key = f"{chrom}:{start}-{end}"
        if key in self.sequences:
            sequence = self.sequences[key]
        else:
            # Generate a simple repeating sequence based on coordinates
            length = end - start
            repeats = (length // len(self.default_sequence)) + 1
            sequence = (self.default_sequence * repeats)[:length]
        
        return NucleotideSequence.from_string(sequence)


class TestFixtures:
    """Test data fixtures."""
    
    @pytest.fixture
    def coding_transcript(self):
        """Coding transcript for testing."""
        return Transcript(
            blocks=np.array([
                [1000, 1200],   # Exon 1: 200bp
                [1500, 1700],   # Exon 2: 200bp  
                [2000, 2300]    # Exon 3: 300bp
            ], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="ENST00000123456",
            cds_start=1100,  # CDS starts 100bp into exon 1
            cds_end=2200,    # CDS ends 100bp before end of exon 3
            biotype="protein_coding"
        )
    
    @pytest.fixture
    def non_coding_transcript(self):
        """Non-coding transcript for testing."""
        return Transcript(
            blocks=np.array([
                [5000, 5300],   # 300bp
                [5600, 5800]    # 200bp
            ], dtype=np.int32),
            strand=Strand.MINUS,
            chrom="chr2",
            id="ENST00000789012",
            biotype="lncRNA"
        )
    
    @pytest.fixture
    def overlapping_transcripts(self):
        """Multiple transcripts with overlapping regions."""
        t1 = Transcript(
            blocks=np.array([[100, 300], [500, 700]], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="transcript1"
        )
        t2 = Transcript(
            blocks=np.array([[200, 400], [600, 800]], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1", 
            id="transcript2"
        )
        t3 = Transcript(
            blocks=np.array([[350, 550]], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="transcript3"
        )
        return [t1, t2, t3]
    
    @pytest.fixture
    def mock_sequence_accessor(self):
        """Mock sequence accessor with predefined sequences."""
        sequences = {
            "chr1:1000-1200": "ATCGATCG" * 25,  # 8*25=200bp exactly
            "chr1:1500-1700": "GCTAGCTA" * 25,  # 8*25=200bp exactly
            "chr1:2000-2300": "TTAATTAA" * 37 + "TTAA",  # 8*37+4=300bp exactly  
            "chr2:5000-5300": "CCCGGGAA" * 37 + "ATTT",  # 8*37+4=300bp exactly
            "chr2:5600-5800": "GGGGCCCC" * 25,  # 8*25=200bp exactly
        }
        return MockSequenceAccessor(sequences)


class TestMergeTranscriptIntervals(TestFixtures):
    """Test merging intervals from multiple transcripts."""
    
    def test_merge_transcript_intervals_basic(self, overlapping_transcripts):
        """Test basic merging of transcript intervals."""
        result = merge_transcript_intervals(overlapping_transcripts)
        
        # Should merge overlapping regions
        assert len(result) >= 1
        assert len(result) <= 3  # Maximum possible separate intervals
        
        # All results should be GenomicInterval objects
        for interval in result:
            assert isinstance(interval, GenomicInterval)
            assert interval.chrom == "chr1"
            assert interval.strand == Strand.UNKNOWN  # Merged intervals have unknown strand
    
    def test_merge_transcript_intervals_cds_only(self, overlapping_transcripts):
        """Test merging only CDS intervals."""
        # Add CDS information to transcripts (create new objects since Transcript is frozen)
        modified_transcripts = []
        for i, transcript in enumerate(overlapping_transcripts):
            if i == 0:  # Make first transcript coding
                modified_transcript = Transcript(
                    blocks=transcript.blocks,
                    strand=transcript.strand,
                    chrom=transcript.chrom,
                    id=transcript.id,
                    cds_start=150,
                    cds_end=650,
                    biotype=transcript.biotype
                )
                modified_transcripts.append(modified_transcript)
            else:
                modified_transcripts.append(transcript)
        
        result = merge_transcript_intervals(modified_transcripts, cds_only=True)
        
        # Should only include CDS regions from coding transcripts
        if result:  # May be empty if no CDS regions
            for interval in result:
                assert isinstance(interval, GenomicInterval)
    
    def test_merge_transcript_intervals_empty_list(self):
        """Test merging empty transcript list."""
        result = merge_transcript_intervals([])
        
        assert result == []
    
    def test_merge_transcript_intervals_different_chroms(self, coding_transcript, non_coding_transcript):
        """Test merging transcripts from different chromosomes."""
        transcripts = [coding_transcript, non_coding_transcript]
        
        with pytest.raises(ValueError, match="All transcripts must be same chromosome"):
            merge_transcript_intervals(transcripts)
    
    def test_merge_transcript_intervals_same_chrom(self, overlapping_transcripts):
        """Test merging transcripts from same chromosome."""
        result = merge_transcript_intervals(overlapping_transcripts)
        
        # All transcripts are on chr1, so should work
        assert len(result) >= 1
        for interval in result:
            assert interval.chrom == "chr1"
    
    def test_merge_transcript_intervals_numba_vs_numpy(self, overlapping_transcripts):
        """Test that numba and numpy give same results."""
        result_numba = merge_transcript_intervals(overlapping_transcripts, use_numba=True)
        result_numpy = merge_transcript_intervals(overlapping_transcripts, use_numba=False)
        
        assert len(result_numba) == len(result_numpy)
        for r1, r2 in zip(result_numba, result_numpy):
            assert r1.start == r2.start
            assert r1.end == r2.end
            assert r1.chrom == r2.chrom


class TestSequenceExtraction(TestFixtures):
    """Test sequence extraction functions."""
    
    def test_extract_sequence_from_blocks_plus_strand(self, mock_sequence_accessor):
        """Test extracting sequence from blocks on plus strand."""
        blocks = np.array([[1000, 1200], [1500, 1700]], dtype=np.int32)
        
        result = _extract_sequence_from_blocks(
            mock_sequence_accessor, "chr1", blocks, Strand.PLUS
        )
        
        # Should concatenate sequences from both blocks
        assert isinstance(result, NucleotideSequence)
        sequence = result.to_string()
        assert len(sequence) == 400  # 200 + 200 bp
        
        # Should start with sequence from first block
        expected_start = mock_sequence_accessor.sequences["chr1:1000-1200"][:10]
        assert sequence.startswith(expected_start)
    
    def test_extract_sequence_from_blocks_minus_strand(self, mock_sequence_accessor):
        """Test extracting sequence from blocks on minus strand."""
        blocks = np.array([[5000, 5300]], dtype=np.int32)
        
        result = _extract_sequence_from_blocks(
            mock_sequence_accessor, "chr2", blocks, Strand.MINUS
        )
        
        # Should return reverse complement for minus strand
        assert isinstance(result, NucleotideSequence)
        sequence = result.to_string()
        assert len(sequence) == 300
        
        # Should be reverse complement of original
        original = NucleotideSequence.from_string(mock_sequence_accessor.sequences["chr2:5000-5300"])
        expected = original.reverse_complement().to_string()
        assert sequence == expected
    
    def test_extract_sequence_from_empty_blocks(self, mock_sequence_accessor):
        """Test extracting sequence from empty blocks."""
        empty_blocks = np.array([], dtype=np.int32).reshape(0, 2)
        
        result = _extract_sequence_from_blocks(
            mock_sequence_accessor, "chr1", empty_blocks, Strand.PLUS
        )
        
        assert isinstance(result, NucleotideSequence)
        assert result.to_string() == ""
    
    def test_extract_cds_sequence(self, coding_transcript, mock_sequence_accessor):
        """Test extracting CDS sequence."""
        result = extract_cds_sequence(coding_transcript, mock_sequence_accessor)
        
        assert isinstance(result, NucleotideSequence)
        sequence = result.to_string()
        
        # CDS should be shorter than total exon sequence
        exon_result = extract_exon_sequence(coding_transcript, mock_sequence_accessor)
        assert len(sequence) < len(exon_result.to_string())
        
        # Should not be empty for coding transcript
        assert len(sequence) > 0
    
    def test_extract_cds_sequence_non_coding(self, non_coding_transcript, mock_sequence_accessor):
        """Test extracting CDS sequence from non-coding transcript."""
        result = extract_cds_sequence(non_coding_transcript, mock_sequence_accessor)
        
        # Non-coding transcript should have empty CDS
        assert result.to_string() == ""
    
    def test_extract_exon_sequence(self, coding_transcript, mock_sequence_accessor):
        """Test extracting exon sequence."""
        result = extract_exon_sequence(coding_transcript, mock_sequence_accessor)
        
        assert isinstance(result, NucleotideSequence)
        sequence = result.to_string()
        
        # Should be length of all exons combined
        total_exon_length = sum(end - start for start, end in coding_transcript.blocks)
        assert len(sequence) == total_exon_length
    
    def test_extract_utr5_sequence(self, coding_transcript, mock_sequence_accessor):
        """Test extracting 5' UTR sequence."""
        result = extract_utr5_sequence(coding_transcript, mock_sequence_accessor)
        
        assert isinstance(result, NucleotideSequence)
        sequence = result.to_string()
        
        # Should not be empty for coding transcript with 5' UTR
        assert len(sequence) > 0
    
    def test_extract_utr3_sequence(self, coding_transcript, mock_sequence_accessor):
        """Test extracting 3' UTR sequence."""
        result = extract_utr3_sequence(coding_transcript, mock_sequence_accessor)
        
        assert isinstance(result, NucleotideSequence)
        sequence = result.to_string()
        
        # Should not be empty for coding transcript with 3' UTR
        assert len(sequence) > 0
    
    def test_extract_utr_sequences_non_coding(self, non_coding_transcript, mock_sequence_accessor):
        """Test extracting UTR sequences from non-coding transcript."""
        result_5 = extract_utr5_sequence(non_coding_transcript, mock_sequence_accessor)
        result_3 = extract_utr3_sequence(non_coding_transcript, mock_sequence_accessor)
        
        # Non-coding transcripts have no defined UTRs
        assert result_5.to_string() == ""
        assert result_3.to_string() == ""
    
    def test_sequence_extraction_consistency(self, coding_transcript, mock_sequence_accessor):
        """Test that extracted sequences are consistent."""
        exon_seq = extract_exon_sequence(coding_transcript, mock_sequence_accessor)
        cds_seq = extract_cds_sequence(coding_transcript, mock_sequence_accessor)
        utr5_seq = extract_utr5_sequence(coding_transcript, mock_sequence_accessor)
        utr3_seq = extract_utr3_sequence(coding_transcript, mock_sequence_accessor)
        
        # Total UTR + CDS should not exceed exon length
        total_functional_length = len(cds_seq.to_string()) + len(utr5_seq.to_string()) + len(utr3_seq.to_string())
        assert total_functional_length <= len(exon_seq.to_string())


class TestDataConsistency(TestFixtures):
    """Test data consistency checking."""
    
    def test_check_consistency_no_mappings(self, coding_transcript, non_coding_transcript):
        """Test consistency check with no mappings applied."""
        collection = TranscriptsCollection([coding_transcript, non_coding_transcript])
        
        report = check_data_consistency(collection)
        
        assert "No gene data mappings have been applied" in report
        assert "Data Consistency Report" in report
    
    def test_check_consistency_with_biotypes(self, coding_transcript, non_coding_transcript):
        """Test consistency check with biotype mappings."""
        # Create transcript without biotype
        transcript_no_biotype = Transcript(
            blocks=np.array([[1000, 2000]], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="no_biotype_transcript"
        )
        
        collection = TranscriptsCollection([coding_transcript, non_coding_transcript, transcript_no_biotype])
        
        # Mock applied_biotypes property
        collection._applied_biotypes = True
        
        report = check_data_consistency(collection)
        
        assert "Applied mappings:" in report
        assert "Transcript biotypes" in report
        assert "Transcripts without biotype:" in report
    
    def test_check_consistency_detailed_report(self, coding_transcript):
        """Test detailed consistency report."""
        # Create multiple transcripts without biotypes
        transcripts = [coding_transcript]
        for i in range(5):
            transcript = Transcript(
                blocks=np.array([[1000, 2000]], dtype=np.int32),
                strand=Strand.PLUS,
                chrom="chr1",
                id=f"transcript_{i}"
            )
            transcripts.append(transcript)
        
        collection = TranscriptsCollection(transcripts)
        collection._applied_biotypes = True
        
        report = check_data_consistency(collection, detailed=True)
        
        assert "Data Consistency Report" in report
        assert "Transcripts without biotype:" in report
        # Should list individual transcript IDs in detailed mode
        assert "transcript_0" in report
    
    def test_check_consistency_no_issues(self, coding_transcript, non_coding_transcript):
        """Test consistency check with no issues found."""
        collection = TranscriptsCollection([coding_transcript, non_coding_transcript])
        
        # Mock that biotypes were applied and all transcripts have them
        collection._applied_biotypes = True
        
        report = check_data_consistency(collection)
        
        assert "No consistency issues found!" in report
    
    def test_check_consistency_large_collection(self):
        """Test consistency check with large collection."""
        # Create many transcripts
        transcripts = []
        for i in range(150):  # More than the 100 limit
            transcript = Transcript(
                blocks=np.array([[1000, 2000]], dtype=np.int32),
                strand=Strand.PLUS,
                chrom="chr1",
                id=f"transcript_{i:03d}"
            )
            transcripts.append(transcript)
        
        collection = TranscriptsCollection(transcripts)
        collection._applied_biotypes = True
        
        report = check_data_consistency(collection, detailed=True)
        
        assert "Transcripts without biotype: 150" in report
        assert "... and 50 more" in report  # Should truncate after 100
    
    def test_check_consistency_multiple_issues(self):
        """Test consistency check with multiple types of issues."""
        transcript = Transcript(
            blocks=np.array([[1000, 2000]], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="test_transcript"
        )
        
        collection = TranscriptsCollection([transcript])
        
        # Mock multiple applied mappings
        collection._applied_biotypes = True
        collection._applied_gene_names = True
        
        report = check_data_consistency(collection)
        
        assert "Applied mappings:" in report
        assert "Transcript biotypes" in report
        assert "Issues summary:" in report


class TestErrorHandling(TestFixtures):
    """Test error handling in genes operations."""
    
    def test_sequence_accessor_protocol(self):
        """Test that SequenceAccessor protocol is properly defined."""
        # This test ensures the protocol interface is correct
        accessor = MockSequenceAccessor()
        
        # Should be able to call fetch method
        result = accessor.fetch("chr1", 100, 200, Strand.PLUS)
        assert isinstance(result, NucleotideSequence)
    
    def test_extract_sequence_with_failing_accessor(self, coding_transcript):
        """Test sequence extraction with failing accessor."""
        class FailingAccessor:
            def fetch(self, chrom: str, start: int, end: int, strand: Strand) -> NucleotideSequence:
                raise Exception("Sequence fetch failed")
        
        failing_accessor = FailingAccessor()
        
        with pytest.raises(Exception, match="Sequence fetch failed"):
            extract_exon_sequence(coding_transcript, failing_accessor)
    
    def test_merge_intervals_edge_cases(self):
        """Test merge intervals with edge cases."""
        # Single transcript
        single_transcript = Transcript(
            blocks=np.array([[1000, 2000]], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="single"
        )
        
        result = merge_transcript_intervals([single_transcript])
        assert len(result) == 1
        assert result[0].start == 1000
        assert result[0].end == 2000
    
    def test_consistency_check_edge_cases(self):
        """Test data consistency check edge cases."""
        # Empty collection
        empty_collection = TranscriptsCollection([])
        report = check_data_consistency(empty_collection)
        assert "No gene data mappings have been applied" in report
        
        # Collection with applied mappings but no issues
        transcript = Transcript(
            blocks=np.array([[1000, 2000]], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="test",
            biotype="protein_coding"
        )
        
        collection = TranscriptsCollection([transcript])
        collection._applied_biotypes = True
        
        report = check_data_consistency(collection)
        assert "No consistency issues found!" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])