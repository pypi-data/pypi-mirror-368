"""Unit tests for pyrion.ops.interval_collection_ops module."""

import pytest
import numpy as np
from typing import List, Callable

from pyrion.core.intervals import GenomicInterval, GenomicIntervalsCollection
from pyrion.core.strand import Strand
from pyrion.ops.interval_collection_ops import (
    merge_close_intervals,
    _merge_close_intervals_numba,
    group_intervals_by_proximity,
    split_intervals_on_gaps,
    _find_gap_splits_numba,
    intersect_collections,
    _intersect_intervals_with_interval_numba,
    filter_collection,
    create_collections_from_mixed_intervals
)


class TestFixtures:
    """Test data fixtures for interval collection operations."""
    
    @pytest.fixture
    def basic_collection(self):
        """Basic genomic intervals collection."""
        intervals = [
            GenomicInterval("chr1", 100, 200, Strand.PLUS, "interval1"),
            GenomicInterval("chr1", 300, 400, Strand.PLUS, "interval2"),
            GenomicInterval("chr1", 500, 600, Strand.PLUS, "interval3"),
            GenomicInterval("chr1", 800, 900, Strand.PLUS, "interval4")
        ]
        return GenomicIntervalsCollection.from_intervals(intervals)
    
    @pytest.fixture
    def overlapping_collection(self):
        """Collection with overlapping intervals."""
        intervals = [
            GenomicInterval("chr2", 50, 150, Strand.MINUS, "overlap1"),
            GenomicInterval("chr2", 100, 250, Strand.MINUS, "overlap2"),
            GenomicInterval("chr2", 200, 300, Strand.MINUS, "overlap3"),
            GenomicInterval("chr2", 450, 550, Strand.MINUS, "overlap4")
        ]
        return GenomicIntervalsCollection.from_intervals(intervals)
    
    @pytest.fixture
    def close_intervals_collection(self):
        """Collection with intervals close together."""
        intervals = [
            GenomicInterval("chr3", 100, 200, Strand.PLUS, "close1"),
            GenomicInterval("chr3", 210, 310, Strand.PLUS, "close2"),  # 10bp gap
            GenomicInterval("chr3", 315, 415, Strand.PLUS, "close3"),  # 5bp gap
            GenomicInterval("chr3", 500, 600, Strand.PLUS, "close4")   # 85bp gap
        ]
        return GenomicIntervalsCollection.from_intervals(intervals)
    
    @pytest.fixture
    def single_interval_collection(self):
        """Collection with single interval."""
        intervals = [GenomicInterval("chr4", 1000, 2000, Strand.UNKNOWN, "single")]
        return GenomicIntervalsCollection.from_intervals(intervals)
    
    @pytest.fixture
    def empty_collection(self):
        """Empty genomic intervals collection."""
        return GenomicIntervalsCollection._empty_collection()
    
    @pytest.fixture
    def mixed_intervals(self):
        """Mixed intervals from different chromosomes and strands."""
        return [
            GenomicInterval("chr1", 100, 200, Strand.PLUS, "chr1_plus1"),
            GenomicInterval("chr1", 300, 400, Strand.PLUS, "chr1_plus2"),
            GenomicInterval("chr1", 500, 600, Strand.MINUS, "chr1_minus1"),
            GenomicInterval("chr2", 100, 200, Strand.PLUS, "chr2_plus1"),
            GenomicInterval("chr2", 300, 400, Strand.MINUS, "chr2_minus1"),
            GenomicInterval("chr3", 100, 200, Strand.UNKNOWN, "chr3_unknown")
        ]


class TestMergeCloseIntervals(TestFixtures):
    """Test merging of close intervals."""
    
    def test_merge_close_no_gap(self, close_intervals_collection):
        """Test merging with no gap tolerance."""
        result = merge_close_intervals(close_intervals_collection, max_gap=0)
        
        # Should not merge any intervals since they don't actually overlap
        assert len(result) == 4
        assert result.chrom == "chr3"
        assert result.strand == Strand.PLUS
    
    def test_merge_close_small_gap(self, close_intervals_collection):
        """Test merging with small gap tolerance."""
        result = merge_close_intervals(close_intervals_collection, max_gap=10)
        
        # Should merge first three intervals (10bp and 5bp gaps both <= 10bp)
        assert len(result) == 2
        expected_starts = [100, 500]
        expected_ends = [415, 600]
        
        for i, (start, end) in enumerate(result.array):
            assert start == expected_starts[i]
            assert end == expected_ends[i]
    
    def test_merge_close_large_gap(self, close_intervals_collection):
        """Test merging with large gap tolerance."""
        result = merge_close_intervals(close_intervals_collection, max_gap=100)
        
        # Should merge all intervals into one
        assert len(result) == 1
        assert result.array[0][0] == 100
        assert result.array[0][1] == 600
    
    def test_merge_close_empty_collection(self, empty_collection):
        """Test merging empty collection."""
        result = merge_close_intervals(empty_collection, max_gap=50)
        
        assert result.is_empty()
        assert len(result) == 0
    
    def test_merge_close_single_interval(self, single_interval_collection):
        """Test merging collection with single interval."""
        result = merge_close_intervals(single_interval_collection, max_gap=100)
        
        assert len(result) == 1
        assert result.array[0][0] == 1000
        assert result.array[0][1] == 2000
    
    def test_merge_close_overlapping_intervals(self, overlapping_collection):
        """Test merging overlapping intervals."""
        result = merge_close_intervals(overlapping_collection, max_gap=0)
        
        # Overlapping intervals should be merged
        assert len(result) <= len(overlapping_collection)
        assert result.chrom == "chr2"
        assert result.strand == Strand.MINUS


class TestGroupIntervalsByProximity(TestFixtures):
    """Test grouping intervals by proximity."""
    
    def test_group_by_proximity_small_gap(self, close_intervals_collection):
        """Test grouping with small gap threshold."""
        groups = group_intervals_by_proximity(close_intervals_collection, max_gap=15)
        
        # Should create 2 groups: [interval1, interval2, interval3] and [interval4]
        assert len(groups) == 2
        assert len(groups[0]) == 3  # First three intervals
        assert len(groups[1]) == 1  # Last interval
        
        # Check that all groups have consistent metadata
        for group in groups:
            assert group.chrom == "chr3"
            assert group.strand == Strand.PLUS
    
    def test_group_by_proximity_large_gap(self, close_intervals_collection):
        """Test grouping with large gap threshold."""
        groups = group_intervals_by_proximity(close_intervals_collection, max_gap=200)
        
        # Should create 1 group containing all intervals
        assert len(groups) == 1
        assert len(groups[0]) == 4
    
    def test_group_by_proximity_no_gap(self, basic_collection):
        """Test grouping with no gap tolerance."""
        groups = group_intervals_by_proximity(basic_collection, max_gap=0)
        
        # Should create 4 separate groups (no overlaps or adjacency)
        assert len(groups) == 4
        for group in groups:
            assert len(group) == 1
    
    def test_group_by_proximity_empty_collection(self, empty_collection):
        """Test grouping empty collection."""
        groups = group_intervals_by_proximity(empty_collection, max_gap=100)
        
        assert len(groups) == 0
    
    def test_group_by_proximity_preserves_ids(self, close_intervals_collection):
        """Test that grouping preserves interval IDs."""
        groups = group_intervals_by_proximity(close_intervals_collection, max_gap=15)
        
        # Check that IDs are preserved
        assert groups[0].ids is not None
        assert len(groups[0].ids) == 3
        assert groups[1].ids is not None
        assert len(groups[1].ids) == 1


class TestSplitIntervalsOnGaps(TestFixtures):
    """Test splitting intervals on gaps."""
    
    def test_split_on_gaps_alias(self, close_intervals_collection):
        """Test that split_intervals_on_gaps is an alias for group_intervals_by_proximity."""
        groups1 = group_intervals_by_proximity(close_intervals_collection, max_gap=15)
        groups2 = split_intervals_on_gaps(close_intervals_collection, min_gap=15)
        
        assert len(groups1) == len(groups2)
        for g1, g2 in zip(groups1, groups2):
            assert len(g1) == len(g2)
            assert np.array_equal(g1.array, g2.array)


class TestIntersectCollections(TestFixtures):
    """Test intersection operations."""
    
    def test_intersect_with_genomic_interval(self, basic_collection):
        """Test intersecting collection with single GenomicInterval."""
        target_interval = GenomicInterval("chr1", 150, 350, Strand.PLUS)
        
        result = intersect_collections(basic_collection, target_interval)
        
        # Should intersect with first two intervals
        expected = np.array([
            [150, 200],   # Intersection with first interval
            [300, 350]    # Intersection with second interval
        ], dtype=np.int32)
        
        assert np.array_equal(result.array, expected)
        assert result.chrom == "chr1"
        assert result.strand == Strand.PLUS
    
    def test_intersect_with_different_chromosome(self, basic_collection):
        """Test intersecting with interval on different chromosome."""
        target_interval = GenomicInterval("chr2", 150, 350, Strand.PLUS)
        
        result = intersect_collections(basic_collection, target_interval)
        
        # No intersection - different chromosome
        assert result.is_empty()
    
    def test_intersect_with_collection(self, basic_collection):
        """Test intersecting two collections."""
        other_intervals = [
            GenomicInterval("chr1", 150, 250, Strand.PLUS),
            GenomicInterval("chr1", 350, 450, Strand.PLUS),
            GenomicInterval("chr1", 550, 650, Strand.PLUS)
        ]
        other_collection = GenomicIntervalsCollection.from_intervals(other_intervals)
        
        result = intersect_collections(basic_collection, other_collection)
        
        # Should find intersections
        assert len(result) >= 1
        assert result.chrom == "chr1"
    
    def test_intersect_empty_collections(self, empty_collection, basic_collection):
        """Test intersecting with empty collections."""
        result = intersect_collections(empty_collection, basic_collection)
        assert result.is_empty()
        
        result = intersect_collections(basic_collection, empty_collection)
        assert result.is_empty()
    
    def test_intersect_no_overlap(self, basic_collection):
        """Test intersecting collections with no overlap."""
        other_intervals = [
            GenomicInterval("chr1", 1000, 1100, Strand.PLUS),
            GenomicInterval("chr1", 1200, 1300, Strand.PLUS)
        ]
        other_collection = GenomicIntervalsCollection.from_intervals(other_intervals)
        
        result = intersect_collections(basic_collection, other_collection)
        
        assert result.is_empty()
    
    def test_intersect_invalid_type(self, basic_collection):
        """Test intersecting with invalid object type."""
        with pytest.raises(ValueError, match="Other must be GenomicInterval or GenomicIntervalsCollection"):
            intersect_collections(basic_collection, "invalid")


class TestFilterCollection(TestFixtures):
    """Test filtering collections."""
    
    def test_filter_by_length(self, basic_collection):
        """Test filtering by interval length."""
        # Filter intervals longer than 90bp
        predicate = lambda iv: iv.length() > 90
        result = filter_collection(basic_collection, predicate)
        
        # All intervals are 100bp long, so all should pass
        assert len(result) == len(basic_collection)
        assert result.chrom == basic_collection.chrom
        assert result.strand == basic_collection.strand
    
    def test_filter_by_position(self, basic_collection):
        """Test filtering by genomic position."""
        # Filter intervals that start before position 400
        predicate = lambda iv: iv.start < 400
        result = filter_collection(basic_collection, predicate)
        
        # Should include first two intervals
        assert len(result) == 2
        assert result.array[0][0] == 100
        assert result.array[1][0] == 300
    
    def test_filter_by_id(self, basic_collection):
        """Test filtering by interval ID."""
        # Filter intervals containing "2" in their ID
        predicate = lambda iv: iv.id is not None and "2" in iv.id
        result = filter_collection(basic_collection, predicate)
        
        # Should include only interval2
        assert len(result) == 1
        assert result.to_intervals_list()[0].id == "interval2"
    
    def test_filter_all_excluded(self, basic_collection):
        """Test filtering that excludes all intervals."""
        # Filter intervals longer than 1000bp (none exist)
        predicate = lambda iv: iv.length() > 1000
        result = filter_collection(basic_collection, predicate)
        
        assert result.is_empty()
    
    def test_filter_empty_collection(self, empty_collection):
        """Test filtering empty collection."""
        predicate = lambda iv: True
        result = filter_collection(empty_collection, predicate)
        
        assert result.is_empty()
    
    def test_filter_preserves_order(self, basic_collection):
        """Test that filtering preserves interval order."""
        # Filter every other interval
        predicate = lambda iv: iv.id in ["interval1", "interval3"]
        result = filter_collection(basic_collection, predicate)
        
        assert len(result) == 2
        intervals = result.to_intervals_list()
        assert intervals[0].id == "interval1"
        assert intervals[1].id == "interval3"
        # Check that positions are still in order
        assert intervals[0].start < intervals[1].start


class TestCreateCollectionsFromMixedIntervals(TestFixtures):
    """Test creating collections from mixed intervals."""
    
    def test_create_collections_consider_strand_false(self, mixed_intervals):
        """Test creating collections without considering strand."""
        collections = create_collections_from_mixed_intervals(mixed_intervals, consider_strand=False)
        
        # Should create separate collections for each chromosome+strand combination
        # chr1: plus and minus strands separate
        # chr2: plus and minus strands separate  
        # chr3: unknown strand
        assert len(collections) == 5
        
        # Check that each collection has consistent chromosome and strand
        for collection in collections:
            intervals = collection.to_intervals_list()
            chroms = {iv.chrom for iv in intervals}
            strands = {iv.strand for iv in intervals}
            assert len(chroms) == 1  # Single chromosome per collection
            assert len(strands) == 1  # Single strand per collection
    
    def test_create_collections_consider_strand_true(self, mixed_intervals):
        """Test creating collections considering strand."""
        collections = create_collections_from_mixed_intervals(mixed_intervals, consider_strand=True)
        
        # Should create separate collections for each chromosome+strand combination
        assert len(collections) == 5
        
        # Verify collections
        chr_strand_combinations = set()
        for collection in collections:
            intervals = collection.to_intervals_list()
            chrom = intervals[0].chrom
            strand = intervals[0].strand
            chr_strand_combinations.add((chrom, strand))
            
            # All intervals in collection should have same chrom/strand
            for iv in intervals:
                assert iv.chrom == chrom
                assert iv.strand == strand
        
        expected_combinations = {
            ("chr1", Strand.PLUS),
            ("chr1", Strand.MINUS),
            ("chr2", Strand.PLUS),
            ("chr2", Strand.MINUS),
            ("chr3", Strand.UNKNOWN)
        }
        assert chr_strand_combinations == expected_combinations
    
    def test_create_collections_empty_list(self):
        """Test creating collections from empty interval list."""
        collections = create_collections_from_mixed_intervals([])
        
        assert len(collections) == 0
    
    def test_create_collections_single_group(self):
        """Test creating collections when all intervals belong to same group."""
        intervals = [
            GenomicInterval("chr1", 100, 200, Strand.PLUS, "int1"),
            GenomicInterval("chr1", 300, 400, Strand.PLUS, "int2"),
            GenomicInterval("chr1", 500, 600, Strand.PLUS, "int3")
        ]
        
        collections = create_collections_from_mixed_intervals(intervals, consider_strand=True)
        
        assert len(collections) == 1
        assert len(collections[0]) == 3
        assert collections[0].chrom == "chr1"
        assert collections[0].strand == Strand.PLUS


class TestNumbaHelperFunctions(TestFixtures):
    """Test numba helper functions."""
    
    def test_merge_close_intervals_numba(self):
        """Test numba merge function directly."""
        intervals = np.array([
            [100, 200],
            [210, 310],  # 10bp gap
            [320, 420],  # 10bp gap
            [500, 600]   # 80bp gap
        ], dtype=np.int32)
        
        result = _merge_close_intervals_numba(intervals, max_gap=15)
        
        expected = np.array([
            [100, 420],  # First three merged
            [500, 600]   # Last one separate
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_merge_close_intervals_numba_empty(self):
        """Test numba merge function with empty array."""
        empty = np.array([], dtype=np.int32).reshape(0, 2)
        result = _merge_close_intervals_numba(empty, max_gap=10)
        
        assert result.shape == (0, 2)
        assert result.dtype == np.int32
    
    def test_find_gap_splits_numba(self):
        """Test numba gap splits function."""
        intervals = np.array([
            [100, 200],
            [210, 310],  # 10bp gap
            [320, 420],  # 10bp gap
            [500, 600]   # 80bp gap
        ], dtype=np.int32)
        
        result = _find_gap_splits_numba(intervals, min_gap=50)
        
        # Should split after index 2 (before the 80bp gap)
        expected = np.array([3, 4], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_find_gap_splits_numba_single_interval(self):
        """Test gap splits with single interval."""
        single = np.array([[100, 200]], dtype=np.int32)
        result = _find_gap_splits_numba(single, min_gap=50)
        
        expected = np.array([1], dtype=np.int32)
        assert np.array_equal(result, expected)
    
    def test_intersect_intervals_with_interval_numba(self):
        """Test numba intersection function."""
        intervals = np.array([
            [100, 200],
            [300, 400],
            [500, 600]
        ], dtype=np.int32)
        
        result = _intersect_intervals_with_interval_numba(intervals, 150, 350)
        
        expected = np.array([
            [150, 200],  # Intersection with first interval
            [300, 350]   # Intersection with second interval
        ], dtype=np.int32)
        
        assert np.array_equal(result, expected)
    
    def test_intersect_intervals_with_interval_numba_no_overlap(self):
        """Test numba intersection with no overlaps."""
        intervals = np.array([
            [100, 200],
            [300, 400]
        ], dtype=np.int32)
        
        result = _intersect_intervals_with_interval_numba(intervals, 250, 280)
        
        assert result.shape == (0, 2)
        assert result.dtype == np.int32


class TestDataTypeHandling(TestFixtures):
    """Test handling of different data types and edge cases."""
    
    def test_large_datasets(self):
        """Test operations with large datasets."""
        # Create large collection
        n = 1000
        array = np.random.randint(0, 100000, size=(n, 2))
        array = np.sort(array, axis=1)  # Ensure start < end
        array = array[np.argsort(array[:, 0])]  # Sort by start
        
        collection = GenomicIntervalsCollection.from_array(array, "chr1", Strand.PLUS)
        
        # Test operations complete without error
        merged = merge_close_intervals(collection, max_gap=100)
        assert merged.array.dtype == collection.array.dtype
        
        groups = group_intervals_by_proximity(collection, max_gap=1000)
        assert len(groups) >= 1
    
    def test_edge_case_coordinates(self):
        """Test edge cases with coordinates."""
        # Very large coordinates
        intervals = [
            GenomicInterval("chr1", 1000000000, 1000000100, Strand.PLUS),
            GenomicInterval("chr1", 1000000200, 1000000300, Strand.PLUS)
        ]
        collection = GenomicIntervalsCollection.from_intervals(intervals)
        
        result = merge_close_intervals(collection, max_gap=150)
        assert len(result) == 1  # Should merge
        
        # Very small coordinates
        intervals = [
            GenomicInterval("chr1", 0, 1, Strand.PLUS),
            GenomicInterval("chr1", 5, 10, Strand.PLUS)
        ]
        collection = GenomicIntervalsCollection.from_intervals(intervals)
        
        result = merge_close_intervals(collection, max_gap=10)
        assert len(result) == 1  # Should merge


if __name__ == "__main__":
    pytest.main([__file__, "-v"])