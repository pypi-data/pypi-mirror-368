"""Unit tests for pyrion.ops.intervals module."""

import pytest
import numpy as np
from typing import List

from pyrion.core.intervals import GenomicInterval
from pyrion.core.strand import Strand
from pyrion.core.genes import Transcript
from pyrion.core.genome_alignment import GenomeAlignment
from pyrion.ops.intervals import (
    find_intersections,
    compute_intersections_core,
    compute_overlap_size,
    intervals_to_array,
    array_to_intervals,
    chains_to_arrays,
    transcripts_to_arrays,
    projected_intervals_to_genomic_intervals
)


class TestFixtures:
    """Test data fixtures for interval operations."""
    
    @pytest.fixture
    def sample_intervals_array(self):
        """Sample interval array for testing."""
        return np.array([
            [100, 200],
            [150, 250],
            [300, 400],
            [350, 450],
            [500, 600]
        ], dtype=np.int32)
    
    @pytest.fixture
    def sample_intervals_objects(self):
        """Sample GenomicInterval objects."""
        return [
            GenomicInterval(chrom="chr1", start=100, end=200, strand=Strand.PLUS, id="int1"),
            GenomicInterval(chrom="chr1", start=300, end=400, strand=Strand.PLUS, id="int2"),
            GenomicInterval(chrom="chr1", start=500, end=600, strand=Strand.MINUS, id="int3")
        ]
    
    @pytest.fixture
    def sample_transcripts(self):
        """Sample transcripts for testing."""
        return [
            Transcript(
                blocks=np.array([[100, 200], [300, 400]], dtype=np.int64),
                strand=Strand.PLUS,
                chrom="chr1",
                id="transcript1"
            ),
            Transcript(
                blocks=np.array([[1000, 1200]], dtype=np.int64),
                strand=Strand.MINUS,
                chrom="chr2", 
                id="transcript2"
            )
        ]
    
    @pytest.fixture
    def sample_chains(self):
        """Sample genome alignments (chains) for testing."""
        return [
            GenomeAlignment(
                chain_id=1, score=1000, t_chrom="chr1", t_strand=1, t_size=1000000,
                q_chrom="chr2", q_strand=1, q_size=1000000,
                blocks=np.array([[100, 200, 1000, 1100], [300, 400, 1200, 1300]], dtype=np.int64)
            ),
            GenomeAlignment(
                chain_id=2, score=2000, t_chrom="chr3", t_strand=-1, t_size=2000000,
                q_chrom="chr4", q_strand=-1, q_size=2000000,
                blocks=np.array([[500, 700, 2000, 2200]], dtype=np.int64)
            )
        ]
    
    @pytest.fixture
    def overlapping_arrays(self):
        """Two arrays with overlapping intervals."""
        arr1 = np.array([[10, 50], [100, 150], [200, 300]], dtype=np.int32)
        arr2 = np.array([[30, 80], [120, 180], [250, 350]], dtype=np.int32)
        return arr1, arr2


class TestFindIntersections(TestFixtures):
    """Test interval intersection functionality."""
    
    def test_basic_intersections(self, overlapping_arrays):
        """Test basic intersection finding."""
        arr1, arr2 = overlapping_arrays
        intersections = find_intersections(arr1, arr2)
        
        # Should have intersections for all three intervals in arr1
        assert len(intersections) == 3
        assert 0 in intersections  # First interval
        assert 1 in intersections  # Second interval
        assert 2 in intersections  # Third interval
        
        # Check overlap values
        assert intersections[0][0][1] == 20  # [10,50] ∩ [30,80] = 20bp
        assert intersections[1][0][1] == 30  # [100,150] ∩ [120,180] = 30bp
        assert intersections[2][0][1] == 50  # [200,300] ∩ [250,350] = 50bp
    
    def test_intersections_with_ids(self, overlapping_arrays):
        """Test intersections with custom IDs."""
        arr1, arr2 = overlapping_arrays
        ids1 = ["interval_A", "interval_B", "interval_C"]
        ids2 = ["target_X", "target_Y", "target_Z"]
        
        intersections = find_intersections(arr1, arr2, ids1, ids2)
        
        assert "interval_A" in intersections
        assert "interval_B" in intersections
        assert "interval_C" in intersections
        
        # Check that target IDs are preserved
        assert intersections["interval_A"][0][0] == "target_X"
        assert intersections["interval_B"][0][0] == "target_Y"
        assert intersections["interval_C"][0][0] == "target_Z"
    
    def test_empty_arrays(self):
        """Test intersection with empty arrays."""
        arr1 = np.array([[100, 200]], dtype=np.int32)
        empty_arr = np.array([], dtype=np.int32).reshape(0, 2)
        
        # Empty second array
        result = find_intersections(arr1, empty_arr)
        assert result == {}
        
        # Empty first array
        result = find_intersections(empty_arr, arr1)
        assert result == {}
        
        # Both empty
        result = find_intersections(empty_arr, empty_arr)
        assert result == {}
    
    def test_no_intersections(self):
        """Test arrays with no overlapping intervals."""
        arr1 = np.array([[10, 20], [100, 110]], dtype=np.int32)
        arr2 = np.array([[30, 40], [200, 210]], dtype=np.int32)
        
        result = find_intersections(arr1, arr2)
        assert result == {}
    
    def test_invalid_input_shapes(self):
        """Test error handling for invalid input shapes."""
        invalid_arr = np.array([[100, 200, 300]], dtype=np.int32)  # Wrong shape
        valid_arr = np.array([[100, 200]], dtype=np.int32)
        
        with pytest.raises(ValueError, match="Arrays must have shape"):
            find_intersections(invalid_arr, valid_arr)
    
    def test_mismatched_ids(self):
        """Test error handling for mismatched ID lengths."""
        arr1 = np.array([[100, 200], [300, 400]], dtype=np.int32)
        arr2 = np.array([[150, 250]], dtype=np.int32)
        wrong_ids = ["id1"]  # Should be length 2
        
        with pytest.raises(ValueError, match="ids1 length must match"):
            find_intersections(arr1, arr2, ids1=wrong_ids)


class TestComputeIntersectionsCore(TestFixtures):
    """Test the numba-optimized core intersection function."""
    
    def test_core_intersection_function(self):
        """Test the core numba intersection implementation."""
        sorted1 = np.array([[10, 50], [100, 150]], dtype=np.int32)
        sorted2 = np.array([[30, 80], [120, 180]], dtype=np.int32)
        idx1 = np.array([0, 1], dtype=np.int32)
        idx2 = np.array([0, 1], dtype=np.int32)
        
        i_arr, j_arr, ov_arr = compute_intersections_core(sorted1, sorted2, idx1, idx2)
        
        assert len(i_arr) == 2  # Two intersections
        assert len(j_arr) == 2
        assert len(ov_arr) == 2
        
        # Check overlaps
        assert ov_arr[0] == 20  # [10,50] ∩ [30,80] = 20
        assert ov_arr[1] == 30  # [100,150] ∩ [120,180] = 30
    
    def test_core_no_intersections(self):
        """Test core function with no overlapping intervals."""
        sorted1 = np.array([[10, 20]], dtype=np.int32)
        sorted2 = np.array([[30, 40]], dtype=np.int32)
        idx1 = np.array([0], dtype=np.int32)
        idx2 = np.array([0], dtype=np.int32)
        
        i_arr, j_arr, ov_arr = compute_intersections_core(sorted1, sorted2, idx1, idx2)
        
        assert len(i_arr) == 0
        assert len(j_arr) == 0
        assert len(ov_arr) == 0


class TestComputeOverlapSize(TestFixtures):
    """Test overlap size computation."""
    
    def test_overlap_calculation(self):
        """Test basic overlap size calculation."""
        # Overlapping intervals
        assert compute_overlap_size(10, 50, 30, 80) == 20  # [10,50] ∩ [30,80]
        assert compute_overlap_size(100, 200, 150, 250) == 50  # [100,200] ∩ [150,250]
        
        # Non-overlapping intervals
        assert compute_overlap_size(10, 20, 30, 40) == 0
        assert compute_overlap_size(100, 110, 50, 90) == 0
        
        # Adjacent intervals (no overlap)
        assert compute_overlap_size(10, 20, 20, 30) == 0
        
        # Contained intervals
        assert compute_overlap_size(10, 100, 30, 50) == 20  # [30,50] contained in [10,100]
        assert compute_overlap_size(30, 50, 10, 100) == 20  # Same result
    
    def test_identical_intervals(self):
        """Test overlap of identical intervals."""
        assert compute_overlap_size(100, 200, 100, 200) == 100
    
    def test_single_base_overlap(self):
        """Test minimal overlap scenarios."""
        assert compute_overlap_size(10, 21, 20, 30) == 1  # Single base overlap


class TestArrayConversions(TestFixtures):
    """Test array conversion functions."""
    
    def test_intervals_to_array(self, sample_intervals_objects):
        """Test conversion from GenomicInterval objects to array."""
        array = intervals_to_array(sample_intervals_objects)
        
        expected = np.array([
            [100, 200],
            [300, 400], 
            [500, 600]
        ], dtype=np.int32)
        
        assert np.array_equal(array, expected)
    
    def test_intervals_to_array_empty(self):
        """Test conversion of empty interval list."""
        array = intervals_to_array([])
        assert array.shape == (0, 2)
        assert array.dtype == np.int32
    
    def test_array_to_intervals(self, sample_intervals_array):
        """Test conversion from array to GenomicInterval objects."""
        intervals = array_to_intervals(sample_intervals_array, "chr5")
        
        assert len(intervals) == 5
        assert all(iv.chrom == "chr5" for iv in intervals)
        assert all(iv.strand == Strand.UNKNOWN for iv in intervals)
        
        # Check coordinates
        assert intervals[0].start == 100 and intervals[0].end == 200
        assert intervals[2].start == 300 and intervals[2].end == 400
    
    def test_array_to_intervals_empty(self):
        """Test conversion of empty array."""
        empty_array = np.array([], dtype=np.int32).reshape(0, 2)
        intervals = array_to_intervals(empty_array, "chr1")
        assert intervals == []


class TestChainArrayConversion(TestFixtures):
    """Test chain-specific array conversion functions."""
    
    def test_chains_to_arrays_target(self, sample_chains):
        """Test conversion of chains to target coordinate arrays."""
        spans, ids = chains_to_arrays(sample_chains, for_q=False)
        
        assert spans.shape == (2, 2)
        assert len(ids) == 2
        
        # Check target spans
        assert spans[0][0] == 100 and spans[0][1] == 400  # Chain 1 target span
        assert spans[1][0] == 500 and spans[1][1] == 700  # Chain 2 target span
        
        # Check chain IDs
        assert ids[0] == 1
        assert ids[1] == 2
    
    def test_chains_to_arrays_query(self, sample_chains):
        """Test conversion of chains to query coordinate arrays."""
        spans, ids = chains_to_arrays(sample_chains, for_q=True)
        
        assert spans.shape == (2, 2)
        
        # Check query spans (note: handles strand automatically)
        assert spans[0][0] == 1000 and spans[0][1] == 1300  # Chain 1 query span
        # Chain 2 is negative strand, so coordinates should be handled differently
        assert len(spans[1]) == 2
    
    def test_chains_to_arrays_empty(self):
        """Test conversion of empty chain list."""
        spans, ids = chains_to_arrays([])
        
        assert spans.shape == (0, 2)
        assert len(ids) == 0
        assert spans.dtype == np.int32
        assert ids.dtype == np.int32


class TestTranscriptArrayConversion(TestFixtures):
    """Test transcript-specific array conversion functions."""
    
    def test_transcripts_to_arrays(self, sample_transcripts):
        """Test conversion of transcripts to arrays."""
        spans, ids = transcripts_to_arrays(sample_transcripts)
        
        assert spans.shape == (2, 2)
        assert len(ids) == 2
        
        # Check transcript spans
        assert spans[0][0] == 100 and spans[0][1] == 400  # Transcript 1 span
        assert spans[1][0] == 1000 and spans[1][1] == 1200  # Transcript 2 span
        
        # Check IDs
        assert ids[0] == "transcript1"
        assert ids[1] == "transcript2"
    
    def test_transcripts_to_arrays_empty(self):
        """Test conversion of empty transcript list."""
        spans, ids = transcripts_to_arrays([])
        
        assert spans.shape == (0, 2)
        assert len(ids) == 0
        assert spans.dtype == np.int32
        assert ids.dtype == object


class TestProjectedIntervalsConversion(TestFixtures):
    """Test conversion of projected interval arrays to GenomicInterval objects."""
    
    def test_projected_intervals_conversion(self):
        """Test conversion of projected arrays to GenomicInterval objects."""
        # Simulate output from projection function
        projected_arrays = [
            np.array([[1000, 1100], [1200, 1300]], dtype=np.int64),  # Multiple results
            np.array([[2000, 2100]], dtype=np.int64),                # Single result
            np.array([[0, 0]], dtype=np.int64),                      # Invalid (unmappable)
            np.array([], dtype=np.int64).reshape(0, 2)               # Empty
        ]
        
        result = projected_intervals_to_genomic_intervals(
            projected_arrays, "chr4", Strand.PLUS, ids=["input1", "input2", "input3", "input4"]
        )
        
        assert len(result) == 4
        
        # First input - multiple results
        assert len(result[0]) == 2
        assert result[0][0].chrom == "chr4"
        assert result[0][0].start == 1000 and result[0][0].end == 1100
        assert result[0][0].strand == Strand.PLUS
        assert result[0][0].id == "input1_0"  # Multi-result ID
        assert result[0][1].id == "input1_1"
        
        # Second input - single result
        assert len(result[1]) == 1
        assert result[1][0].id == "input2"  # Single result ID
        
        # Third input - invalid (0,0) filtered out
        assert len(result[2]) == 0
        
        # Fourth input - empty
        assert len(result[3]) == 0
    
    def test_projected_intervals_no_ids(self):
        """Test conversion without providing IDs."""
        projected_arrays = [
            np.array([[1000, 1100]], dtype=np.int64),
            np.array([[2000, 2100]], dtype=np.int64)
        ]
        
        result = projected_intervals_to_genomic_intervals(
            projected_arrays, "chr5", Strand.MINUS
        )
        
        assert len(result) == 2
        assert result[0][0].id is None
        assert result[1][0].id is None
        assert all(iv[0].strand == Strand.MINUS for iv in result)
    
    def test_projected_intervals_edge_cases(self):
        """Test edge cases in projected interval conversion."""
        # All invalid results
        projected_arrays = [
            np.array([[0, 0]], dtype=np.int64),
            np.array([[0, 0], [0, 0]], dtype=np.int64)
        ]
        
        result = projected_intervals_to_genomic_intervals(
            projected_arrays, "chr1", Strand.UNKNOWN
        )
        
        assert len(result) == 2
        assert len(result[0]) == 0  # All filtered out
        assert len(result[1]) == 0  # All filtered out


class TestRealDataIntegration(TestFixtures):
    """Integration tests with more realistic data."""
    
    def test_large_dataset_intersections(self):
        """Test intersections with larger datasets."""
        # Create larger test dataset
        n1, n2 = 1000, 800
        arr1 = np.random.randint(0, 100000, size=(n1, 2))
        arr1 = np.sort(arr1, axis=1)  # Ensure start < end
        
        arr2 = np.random.randint(0, 100000, size=(n2, 2))
        arr2 = np.sort(arr2, axis=1)
        
        # Test that function runs without error
        intersections = find_intersections(arr1, arr2)
        
        # Basic sanity checks
        assert isinstance(intersections, dict)
        assert all(isinstance(k, (int, np.integer)) for k in intersections.keys())
    
    def test_conversion_round_trip(self, sample_intervals_objects):
        """Test round-trip conversion: objects -> array -> objects."""
        # Forward conversion
        array = intervals_to_array(sample_intervals_objects)
        
        # Backward conversion
        converted_back = array_to_intervals(array, "chr1")
        
        # Check that coordinates match (ignoring IDs/strands which aren't preserved)
        for orig, converted in zip(sample_intervals_objects, converted_back):
            assert orig.start == converted.start
            assert orig.end == converted.end
            assert orig.chrom == converted.chrom


class TestPerformanceAndEdgeCases(TestFixtures):
    """Test performance characteristics and edge cases."""
    
    def test_single_interval_arrays(self):
        """Test functions with single-interval arrays."""
        single_interval = np.array([[100, 200]], dtype=np.int32)
        
        # Test intersections
        intersections = find_intersections(single_interval, single_interval)
        assert 0 in intersections
        assert intersections[0][0][1] == 100  # Full overlap
        
        # Test conversions
        intervals = array_to_intervals(single_interval, "chr1")
        assert len(intervals) == 1
        
        back_to_array = intervals_to_array(intervals)
        assert np.array_equal(back_to_array, single_interval)
    
    def test_zero_length_intervals(self):
        """Test handling of zero-length intervals."""
        # Note: GenomicInterval validation should prevent these, but test robustness
        zero_length = np.array([[100, 100]], dtype=np.int32)
        normal = np.array([[50, 150]], dtype=np.int32)
        
        # Should not crash, though behavior may vary
        result = find_intersections(zero_length, normal)
        assert isinstance(result, dict)
    
    def test_very_large_coordinates(self):
        """Test with very large genomic coordinates."""
        large_coords = np.array([
            [1000000000, 1000001000],  # 1Gb region
            [2000000000, 2000002000]   # 2Gb region
        ], dtype=np.int32)
        
        # Test basic operations
        overlap = compute_overlap_size(1000000500, 1000001500, 1000000000, 1000001000)
        assert overlap == 500
        
        intervals = array_to_intervals(large_coords, "chr1")
        assert len(intervals) == 2
        assert intervals[0].start == 1000000000


