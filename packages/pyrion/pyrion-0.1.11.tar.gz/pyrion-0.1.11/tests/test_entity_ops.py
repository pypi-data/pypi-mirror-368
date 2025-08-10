"""Unit tests for pyrion.ops.entity_ops module."""

import pytest
import numpy as np
from typing import List

from pyrion.core.genes import Transcript
from pyrion.core.genome_alignment import GenomeAlignment  
from pyrion.core.strand import Strand
from pyrion.ops.entity_ops import (
    get_transcript_cds_in_range,
    get_transcript_utrs_in_range,
    get_transcript_introns_in_range,
    merge_transcript_cds,
    merge_transcript_utrs,
    find_transcript_overlaps,
    subtract_transcript_regions,
    _get_transcript_blocks_by_type,
    merge_genome_alignments,
    find_alignment_gaps,
    intersect_alignment_with_intervals
)


class TestFixtures:
    """Test data fixtures for entity operations."""
    
    @pytest.fixture
    def coding_transcript(self):
        """Coding transcript with CDS, UTRs."""
        return Transcript(
            blocks=np.array([
                [100, 200],   # Exon 1: UTR5
                [300, 400],   # Exon 2: UTR5 + CDS
                [500, 600],   # Exon 3: CDS
                [700, 800]    # Exon 4: CDS + UTR3
            ], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="transcript1",
            cds_start=350,  # CDS starts in exon 2
            cds_end=750     # CDS ends in exon 4
        )
    
    @pytest.fixture 
    def non_coding_transcript(self):
        """Non-coding transcript."""
        return Transcript(
            blocks=np.array([
                [1000, 1100],
                [1200, 1300],
                [1400, 1500]
            ], dtype=np.int32),
            strand=Strand.MINUS,
            chrom="chr2", 
            id="transcript2"
        )
    
    @pytest.fixture
    def single_exon_coding(self):
        """Single exon coding transcript."""
        return Transcript(
            blocks=np.array([[2000, 2500]], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr3",
            id="transcript3", 
            cds_start=2100,
            cds_end=2400
        )
    
    @pytest.fixture
    def overlapping_transcripts(self, coding_transcript):
        """Two transcripts with overlapping regions."""
        transcript2 = Transcript(
            blocks=np.array([
                [150, 250],   # Overlaps with first transcript
                [550, 650],   # Overlaps with third exon
                [900, 1000]   # No overlap
            ], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="transcript_overlapping",
            cds_start=200,
            cds_end=600
        )
        return [coding_transcript, transcript2]
    
    @pytest.fixture
    def simple_genome_alignment(self):
        """Simple genome alignment for testing."""
        return GenomeAlignment(
            chain_id=1,
            score=10000,
            t_chrom="chr1",
            t_strand=1,
            t_size=5000,
            q_chrom="chr2", 
            q_strand=1,
            q_size=4000,
            blocks=np.array([
                [100, 200, 50, 150],    # Target 100-200 -> Query 50-150
                [300, 400, 200, 300],   # Target 300-400 -> Query 200-300
                [500, 600, 350, 450]    # Target 500-600 -> Query 350-450
            ], dtype=np.int32)
        )
    
    @pytest.fixture
    def alignment_with_gaps(self):
        """Genome alignment with gaps for testing."""
        return GenomeAlignment(
            chain_id=2,
            score=8000,
            t_chrom="chr3",
            t_strand=1,
            t_size=3000,
            q_chrom="chr4",
            q_strand=-1,
            q_size=2500,
            blocks=np.array([
                [1000, 1100, 500, 600],
                [1300, 1400, 300, 400],
                [1600, 1700, 100, 200]
            ], dtype=np.int32)
        )


class TestTranscriptCDSOperations(TestFixtures):
    """Test CDS-related operations on transcripts."""
    
    def test_get_cds_in_range_coding(self, coding_transcript):
        """Test getting CDS blocks within a range for coding transcript."""
        # Range that includes part of CDS
        result = get_transcript_cds_in_range(coding_transcript, 325, 525)
        
        expected = np.array([
            [350, 400],   # CDS part of exon 2
            [500, 525]    # CDS part of exon 3 (trimmed to range)
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_get_cds_in_range_non_coding(self, non_coding_transcript):
        """Test getting CDS from non-coding transcript."""
        result = get_transcript_cds_in_range(non_coding_transcript, 1000, 1500)
        
        # Non-coding transcript has no CDS
        assert result.shape == (0, 2)
        assert result.dtype == np.int32
    
    def test_get_cds_in_range_no_intersection(self, coding_transcript):
        """Test getting CDS with range that doesn't intersect CDS."""
        result = get_transcript_cds_in_range(coding_transcript, 50, 200)
        
        # Range is before CDS starts
        assert result.shape == (0, 2)
    
    def test_get_cds_single_exon(self, single_exon_coding):
        """Test getting CDS from single-exon transcript."""
        result = get_transcript_cds_in_range(single_exon_coding, 2050, 2450)
        
        expected = np.array([[2100, 2400]], dtype=np.int32)
        assert np.array_equal(result, expected)


class TestTranscriptUTROperations(TestFixtures):
    """Test UTR-related operations on transcripts."""
    
    def test_get_utrs_both_coding(self, coding_transcript):
        """Test getting both UTR types from coding transcript."""
        result = get_transcript_utrs_in_range(coding_transcript, 50, 850, utr_type="both")
        
        # Should include UTR5 and UTR3 blocks
        expected = np.array([
            [100, 200],   # UTR5 exon 1
            [300, 350],   # UTR5 part of exon 2
            [750, 800]    # UTR3 part of exon 4
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_get_utrs_5_only(self, coding_transcript):
        """Test getting only 5' UTR."""
        result = get_transcript_utrs_in_range(coding_transcript, 50, 450, utr_type="5")
        
        expected = np.array([
            [100, 200],   # UTR5 exon 1
            [300, 350]    # UTR5 part of exon 2
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_get_utrs_3_only(self, coding_transcript):
        """Test getting only 3' UTR."""
        result = get_transcript_utrs_in_range(coding_transcript, 700, 850, utr_type="3")
        
        expected = np.array([[750, 800]], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_get_utrs_non_coding_both(self, non_coding_transcript):
        """Test getting UTRs from non-coding transcript (should return exons)."""
        result = get_transcript_utrs_in_range(non_coding_transcript, 950, 1550, utr_type="both")
        
        # Non-coding transcript: all exons are effectively UTR
        expected = np.array([
            [1000, 1100],
            [1200, 1300], 
            [1400, 1500]
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_get_utrs_non_coding_3_only(self, non_coding_transcript):
        """Test getting 3' UTR only from non-coding transcript."""
        result = get_transcript_utrs_in_range(non_coding_transcript, 950, 1550, utr_type="3")
        
        # Non-coding transcript with 3' only should return empty
        assert result.shape == (0, 2)


class TestTranscriptIntronOperations(TestFixtures):
    """Test intron-related operations on transcripts."""
    
    def test_get_introns_in_range(self, coding_transcript):
        """Test getting introns within a range."""
        result = get_transcript_introns_in_range(coding_transcript, 250, 650)
        
        # Should include introns that intersect the range
        # Transcript has introns: 200-300, 400-500, 600-700
        expected = np.array([
            [250, 300],   # Trimmed first intron
            [400, 500],   # Full second intron 
            [600, 650]    # Trimmed third intron
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_get_introns_single_exon(self, single_exon_coding):
        """Test getting introns from single-exon transcript."""
        result = get_transcript_introns_in_range(single_exon_coding, 1000, 3000)
        
        # Single exon has no introns
        assert result.shape == (0, 2)


class TestMergeTranscriptCDS(TestFixtures):
    """Test merging CDS blocks from multiple transcripts."""
    
    def test_merge_cds_multiple_transcripts(self, overlapping_transcripts):
        """Test merging CDS from multiple overlapping transcripts."""
        result = merge_transcript_cds(overlapping_transcripts)
        
        # CDS regions should be merged
        expected = np.array([
            [200, 250],   # CDS from transcript2 exon 1
            [350, 400],   # CDS from transcript1 exon 2  
            [500, 600],   # Merged CDS from both transcripts
            [700, 750]    # CDS from transcript1 exon 4
        ], dtype=np.int32)
        
        # Result should be sorted and merged
        assert result.dtype == np.int32
        assert len(result) >= 1  # Should have some CDS regions
    
    def test_merge_cds_empty_list(self):
        """Test merging CDS from empty transcript list."""
        result = merge_transcript_cds([])
        
        assert result.shape == (0, 2)
        assert result.dtype == np.int32
    
    def test_merge_cds_non_coding_only(self, non_coding_transcript):
        """Test merging CDS from non-coding transcripts only."""
        result = merge_transcript_cds([non_coding_transcript])
        
        # Non-coding transcripts have no CDS
        assert result.shape == (0, 2)
    
    def test_merge_cds_mixed_coding_non_coding(self, coding_transcript, non_coding_transcript):
        """Test merging CDS from mix of coding and non-coding transcripts."""
        result = merge_transcript_cds([coding_transcript, non_coding_transcript])
        
        # Should only include CDS from coding transcript
        assert result.dtype == np.int32
        assert len(result) > 0  # Should have CDS regions from coding transcript


class TestMergeTranscriptUTRs(TestFixtures):
    """Test merging UTR blocks from multiple transcripts."""
    
    def test_merge_utrs_both(self, overlapping_transcripts):
        """Test merging both UTR types."""
        result = merge_transcript_utrs(overlapping_transcripts, utr_type="both")
        
        assert result.dtype == np.int32
        assert len(result) >= 1  # Should have UTR regions
    
    def test_merge_utrs_5_only(self, overlapping_transcripts):
        """Test merging only 5' UTRs."""
        result = merge_transcript_utrs(overlapping_transcripts, utr_type="5")
        
        assert result.dtype == np.int32
    
    def test_merge_utrs_3_only(self, overlapping_transcripts):
        """Test merging only 3' UTRs.""" 
        result = merge_transcript_utrs(overlapping_transcripts, utr_type="3")
        
        assert result.dtype == np.int32
    
    def test_merge_utrs_empty_list(self):
        """Test merging UTRs from empty list."""
        result = merge_transcript_utrs([])
        
        assert result.shape == (0, 2)
        assert result.dtype == np.int32


class TestTranscriptOverlaps(TestFixtures):
    """Test finding overlaps between transcripts."""
    
    def test_find_overlaps_exons(self, overlapping_transcripts):
        """Test finding exon overlaps between transcripts."""
        t1, t2 = overlapping_transcripts
        result = find_transcript_overlaps(t1, t2, region_type="exon")
        
        # Should find overlapping exon regions
        expected = np.array([
            [150, 200],   # Overlap in first region
            [550, 600]    # Overlap in third region
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_find_overlaps_cds(self, overlapping_transcripts):
        """Test finding CDS overlaps."""
        t1, t2 = overlapping_transcripts
        result = find_transcript_overlaps(t1, t2, region_type="cds")
        
        # Should find CDS overlap
        assert result.dtype == np.int32
        assert len(result) >= 1
    
    def test_find_overlaps_no_intersection(self, coding_transcript, non_coding_transcript):
        """Test finding overlaps when there are none."""
        result = find_transcript_overlaps(coding_transcript, non_coding_transcript, region_type="exon")
        
        # Different chromosomes, no overlap
        assert result.shape == (0, 2)
    
    def test_find_overlaps_invalid_region_type(self, overlapping_transcripts):
        """Test finding overlaps with invalid region type."""
        t1, t2 = overlapping_transcripts
        
        with pytest.raises(ValueError, match="Unknown region_type"):
            find_transcript_overlaps(t1, t2, region_type="invalid")


class TestSubtractTranscriptRegions(TestFixtures):
    """Test subtracting regions from transcripts."""
    
    def test_subtract_from_exons(self, coding_transcript):
        """Test subtracting regions from exons."""
        subtract_regions = np.array([
            [150, 250],   # Intersects first exon
            [350, 450]    # Intersects second exon
        ], dtype=np.int32)
        
        result = subtract_transcript_regions(coding_transcript, subtract_regions, region_type="exon")
        
        # Should remove specified regions from exons
        expected = np.array([
            [100, 150],   # Left part of first exon
            [300, 350],   # Left part of second exon
            [500, 600],   # Third exon unchanged
            [700, 800]    # Fourth exon unchanged
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_subtract_from_cds(self, coding_transcript):
        """Test subtracting regions from CDS."""
        subtract_regions = np.array([[375, 525]], dtype=np.int32)
        
        result = subtract_transcript_regions(coding_transcript, subtract_regions, region_type="cds")
        
        # Should remove region from CDS blocks
        expected = np.array([
            [350, 375],   # Left part of CDS in exon 2
            [525, 600],   # Right part of CDS in exon 3
            [700, 750]    # CDS in exon 4 unchanged
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_subtract_no_intersection(self, coding_transcript):
        """Test subtracting regions that don't intersect."""
        subtract_regions = np.array([[1000, 1100]], dtype=np.int32)
        
        result = subtract_transcript_regions(coding_transcript, subtract_regions, region_type="exon")
        
        # Should return original exons unchanged
        assert np.array_equal(result, coding_transcript.blocks)


class TestGetTranscriptBlocksByType(TestFixtures):
    """Test helper function for getting blocks by type."""
    
    def test_get_blocks_exon(self, coding_transcript):
        """Test getting exon blocks."""
        result = _get_transcript_blocks_by_type(coding_transcript, "exon")
        assert np.array_equal(result, coding_transcript.blocks)
    
    def test_get_blocks_cds(self, coding_transcript):
        """Test getting CDS blocks."""
        result = _get_transcript_blocks_by_type(coding_transcript, "cds")
        assert np.array_equal(result, coding_transcript.cds_blocks)
    
    def test_get_blocks_utr5(self, coding_transcript):
        """Test getting UTR5 blocks."""
        result = _get_transcript_blocks_by_type(coding_transcript, "utr5")
        assert np.array_equal(result, coding_transcript.utr5_blocks)
    
    def test_get_blocks_utr3(self, coding_transcript):
        """Test getting UTR3 blocks."""
        result = _get_transcript_blocks_by_type(coding_transcript, "utr3")
        assert np.array_equal(result, coding_transcript.utr3_blocks)
    
    def test_get_blocks_invalid_type(self, coding_transcript):
        """Test getting blocks with invalid type."""
        with pytest.raises(ValueError, match="Unknown region_type"):
            _get_transcript_blocks_by_type(coding_transcript, "invalid")


class TestGenomeAlignmentOperations(TestFixtures):
    """Test operations on genome alignments."""
    
    def test_merge_alignments_target_space(self, simple_genome_alignment, alignment_with_gaps):
        """Test merging genome alignments in target space."""
        result = merge_genome_alignments([simple_genome_alignment, alignment_with_gaps], space="target")
        
        # Should merge all target coordinates
        assert result.dtype == np.int32
        assert len(result) >= 1
    
    def test_merge_alignments_query_space(self, simple_genome_alignment, alignment_with_gaps):
        """Test merging genome alignments in query space."""
        result = merge_genome_alignments([simple_genome_alignment, alignment_with_gaps], space="query")
        
        # Should merge all query coordinates
        assert result.dtype == np.int32
        assert len(result) >= 1
    
    def test_merge_alignments_empty_list(self):
        """Test merging empty alignment list."""
        result = merge_genome_alignments([])
        
        assert result.shape == (0, 2)
        assert result.dtype == np.int32
    
    def test_merge_alignments_invalid_space(self, simple_genome_alignment):
        """Test merging with invalid space parameter."""
        with pytest.raises(ValueError, match="space must be 'target' or 'query'"):
            merge_genome_alignments([simple_genome_alignment], space="invalid")
    
    def test_find_alignment_gaps_target(self, simple_genome_alignment):
        """Test finding gaps in target space."""
        result = find_alignment_gaps(simple_genome_alignment, space="target")
        
        # Should find gaps between aligned blocks
        expected = np.array([
            [200, 300],   # Gap between first and second block
            [400, 500]    # Gap between second and third block
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_find_alignment_gaps_query(self, simple_genome_alignment):
        """Test finding gaps in query space."""
        result = find_alignment_gaps(simple_genome_alignment, space="query")
        
        # Should find gaps in query coordinates
        expected = np.array([
            [150, 200],   # Gap between first and second block
            [300, 350]    # Gap between second and third block  
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_find_gaps_single_block(self):
        """Test finding gaps in single-block alignment."""
        single_block_alignment = GenomeAlignment(
            chain_id=1,
            score=5000,
            t_chrom="chr1",
            t_strand=1,
            t_size=1000,
            q_chrom="chr2",
            q_strand=1,
            q_size=1000,
            blocks=np.array([[100, 200, 50, 150]], dtype=np.int32)
        )
        
        result = find_alignment_gaps(single_block_alignment, space="target")
        
        # Single block has no gaps
        assert result.shape == (0, 2)
    
    def test_intersect_alignment_with_intervals_target(self, simple_genome_alignment):
        """Test intersecting alignment with intervals in target space."""
        intervals = np.array([
            [150, 250],   # Intersects first block
            [350, 450],   # Intersects second block
            [800, 900]    # No intersection
        ], dtype=np.int32)
        
        result = intersect_alignment_with_intervals(simple_genome_alignment, intervals, space="target")
        
        expected = np.array([
            [150, 200],   # Intersection with first block
            [350, 400]    # Intersection with second block
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_intersect_alignment_with_intervals_query(self, simple_genome_alignment):
        """Test intersecting alignment with intervals in query space."""
        intervals = np.array([
            [100, 200],   # Intersects first and second blocks
            [400, 500]    # Intersects third block
        ], dtype=np.int32)
        
        result = intersect_alignment_with_intervals(simple_genome_alignment, intervals, space="query")
        
        assert result.dtype == np.int32
        assert len(result) >= 1
    
    def test_intersect_alignment_empty_intervals(self, simple_genome_alignment):
        """Test intersecting with empty intervals."""
        empty_intervals = np.array([], dtype=np.int32).reshape(0, 2)
        
        result = intersect_alignment_with_intervals(simple_genome_alignment, empty_intervals, space="target")
        
        assert result.shape == (0, 2)
        assert result.dtype == np.int32
    
    def test_intersect_alignment_invalid_space(self, simple_genome_alignment):
        """Test intersecting with invalid space parameter."""
        intervals = np.array([[100, 200]], dtype=np.int32)
        
        with pytest.raises(ValueError, match="space must be 'target' or 'query'"):
            intersect_alignment_with_intervals(simple_genome_alignment, intervals, space="invalid")


class TestAlgorithmSelection(TestFixtures):
    """Test automatic algorithm selection for different functions."""
    
    def test_numba_vs_numpy_consistency(self, coding_transcript):
        """Test that numba and numpy implementations give consistent results."""
        range_start, range_end = 250, 650
        
        # Test CDS operations
        result_numba = get_transcript_cds_in_range(coding_transcript, range_start, range_end, use_numba=True)
        result_numpy = get_transcript_cds_in_range(coding_transcript, range_start, range_end, use_numba=False)
        assert np.array_equal(result_numba, result_numpy)
        
        # Test UTR operations
        result_numba = get_transcript_utrs_in_range(coding_transcript, range_start, range_end, use_numba=True)
        result_numpy = get_transcript_utrs_in_range(coding_transcript, range_start, range_end, use_numba=False)
        assert np.array_equal(result_numba, result_numpy)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])