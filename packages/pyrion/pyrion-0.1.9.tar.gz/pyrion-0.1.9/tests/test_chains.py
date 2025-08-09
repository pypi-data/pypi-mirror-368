"""Unit tests for pyrion.ops.chains module."""

import pytest
import numpy as np
from pathlib import Path

from pyrion.core.intervals import GenomicInterval
from pyrion.core.strand import Strand
from pyrion.core.genes import Transcript
from pyrion.core.genome_alignment import GenomeAlignment
from pyrion.io.chain import read_chain_file
from pyrion.ops.chains import (
    project_intervals_through_chain,
    _project_intervals_vectorized, 
    _project_intervals_numba,
    _project_intervals_numpy,
    project_intervals_through_genome_alignment,
    project_intervals_through_genome_alignment_to_intervals,
    get_chain_target_interval,
    get_chain_query_interval,
    get_chain_t_start,
    get_chain_t_end,
    get_chain_q_start,
    get_chain_q_end,
    split_genome_alignment,
    HAS_NUMBA
)


class TestFixtures:
    """Test data fixtures."""
    
    @pytest.fixture(scope="class")
    def test_chain_file(self):
        """Path to test chain file."""
        return Path("test_data/chains/hg38.chr9.mm39.chr4.chain")
    
    @pytest.fixture(scope="class") 
    def sample_chain_file(self):
        """Path to smaller sample chain file."""
        return Path("test_data/chains/hg38.chr9.mm39.chr4.chain")
    
    @pytest.fixture(scope="class")
    def loaded_chain(self, sample_chain_file):
        """Loaded GenomeAlignment from sample data."""
        collection = read_chain_file(sample_chain_file)
        return collection.alignments[0]  # Use first alignment
    
    @pytest.fixture
    def simple_chain_blocks(self):
        """Simple synthetic chain blocks for basic testing."""
        return np.array([
            [100, 200, 1000, 1100],  # t_start, t_end, q_start, q_end
            [300, 400, 1200, 1300],
            [500, 600, 1400, 1500],
        ], dtype=np.int64)
    
    @pytest.fixture
    def simple_genome_alignment(self, simple_chain_blocks):
        """Simple GenomeAlignment for testing."""
        return GenomeAlignment(
            chain_id=1,
            score=1000,
            t_chrom="chr1",
            t_strand=1,
            t_size=1000000,
            q_chrom="chr2", 
            q_strand=1,
            q_size=1000000,
            blocks=simple_chain_blocks
        )
    
    @pytest.fixture
    def test_intervals(self):
        """Test intervals for projection."""
        return np.array([
            [150, 180],   # Overlaps first block
            [120, 220],   # Spans first block  
            [350, 380],   # Overlaps second block
            [250, 350],   # In gap between blocks
            [80, 120],    # Before all blocks
            [700, 800],   # After all blocks
        ], dtype=np.int64)
    
    @pytest.fixture
    def sample_transcripts(self):
        """Sample transcripts for split testing."""
        return [
            Transcript(
                blocks=np.array([[1000, 1200], [1300, 1500]], dtype=np.int64),
                strand=Strand.PLUS,
                chrom="chr1",
                id="transcript1"
            ),
            Transcript(
                blocks=np.array([[2000, 2300]], dtype=np.int64),
                strand=Strand.PLUS,
                chrom="chr1", 
                id="transcript2"
            )
        ]


class TestProjectIntervalsThroughChain(TestFixtures):
    """Test interval projection functions."""
    
    def test_empty_intervals(self, simple_chain_blocks):
        """Test with empty intervals array."""
        empty_intervals = np.array([], dtype=np.int64).reshape(0, 2)
        result = project_intervals_through_chain(empty_intervals, simple_chain_blocks)
        assert result == []
    
    def test_empty_chain_blocks(self):
        """Test with empty chain blocks."""
        intervals = np.array([[100, 200]], dtype=np.int64)
        empty_blocks = np.array([], dtype=np.int64).reshape(0, 4)
        result = project_intervals_through_chain(intervals, empty_blocks)
        assert len(result) == 1
        assert np.array_equal(result[0], np.array([[0, 0]], dtype=np.int64))
    
    def test_basic_projection(self, simple_chain_blocks, test_intervals):
        """Test basic interval projection."""
        results = project_intervals_through_chain(test_intervals, simple_chain_blocks)
        assert len(results) == len(test_intervals)
        
        # First interval [150, 180] should project to [1050, 1080]
        assert np.array_equal(results[0], np.array([[1050, 1080]], dtype=np.int64))
        
        # Second interval [120, 220] should project to [1020, 1120]
        assert np.array_equal(results[1], np.array([[1020, 1120]], dtype=np.int64))
    
    def test_vectorized_dispatcher(self, simple_chain_blocks, test_intervals):
        """Test vectorized implementation dispatcher."""
        result_vectorized = _project_intervals_vectorized(test_intervals, simple_chain_blocks)
        result_numpy = _project_intervals_numpy(test_intervals, simple_chain_blocks)
        
        # Results should be identical
        assert len(result_vectorized) == len(result_numpy)
        for vec_res, np_res in zip(result_vectorized, result_numpy):
            assert np.array_equal(vec_res, np_res)
    
    @pytest.mark.skipif(not HAS_NUMBA, reason="Numba not available")
    def test_numba_implementation(self, simple_chain_blocks, test_intervals):
        """Test numba implementation if available."""
        result_numba = _project_intervals_numba(test_intervals, simple_chain_blocks)
        result_numpy = _project_intervals_numpy(test_intervals, simple_chain_blocks)
        
        # Results should be identical
        assert len(result_numba) == len(result_numpy)
        for numba_res, np_res in zip(result_numba, result_numpy):
            assert np.array_equal(numba_res, np_res)
    
    def test_clamping_to_chain_bounds(self, simple_chain_blocks):
        """Test that results are clamped to chain boundaries."""
        # Interval that would project outside chain bounds
        intervals = np.array([[50, 650]], dtype=np.int64)
        results = project_intervals_through_chain(intervals, simple_chain_blocks)
        
        # Should be clamped to chain bounds [1000, 1500]
        result = results[0][0]
        assert result[0] >= 1000  # Min q_start
        assert result[1] <= 1500  # Max q_end


class TestProjectThroughGenomeAlignment(TestFixtures):
    """Test GenomeAlignment projection functions."""
    
    def test_project_through_genome_alignment(self, simple_genome_alignment, test_intervals):
        """Test projection through GenomeAlignment object."""
        results = project_intervals_through_genome_alignment(test_intervals, simple_genome_alignment)
        assert len(results) == len(test_intervals)
        assert all(isinstance(r, np.ndarray) for r in results)
    
    def test_project_to_intervals_objects(self, simple_genome_alignment):
        """Test projection to GenomicInterval objects."""
        intervals = np.array([[150, 180], [350, 380]], dtype=np.int64)
        results = project_intervals_through_genome_alignment_to_intervals(
            intervals, simple_genome_alignment
        )
        
        assert len(results) == 2
        assert all(isinstance(r, GenomicInterval) for r in results)
        assert all(r.chrom == "chr2" for r in results)  # Target chromosome
        assert all(r.strand == Strand.PLUS for r in results)
    
    def test_project_to_intervals_custom_chrom_strand(self, simple_genome_alignment):
        """Test projection with custom chromosome and strand."""
        intervals = np.array([[150, 180]], dtype=np.int64)
        results = project_intervals_through_genome_alignment_to_intervals(
            intervals, simple_genome_alignment, 
            target_chrom="custom_chr", target_strand=Strand.MINUS
        )
        
        assert len(results) == 1
        assert results[0].chrom == "custom_chr"
        assert results[0].strand == Strand.MINUS
    
    def test_filter_invalid_projections(self, simple_genome_alignment):
        """Test that invalid projections (0,0) are filtered out."""
        # Intervals outside chain coverage
        intervals = np.array([[50, 80], [150, 180]], dtype=np.int64)
        results = project_intervals_through_genome_alignment_to_intervals(
            intervals, simple_genome_alignment
        )
        
        # Should only get valid projections
        assert len(results) == 1  # Only second interval projects validly
        assert results[0].start == 1050
        assert results[0].end == 1080


class TestChainAccessors(TestFixtures):
    """Test chain coordinate accessor functions."""
    
    def test_get_chain_target_interval(self, simple_genome_alignment):
        """Test target interval extraction."""
        target = get_chain_target_interval(simple_genome_alignment)
        
        assert isinstance(target, GenomicInterval)
        assert target.chrom == "chr1"
        assert target.start == 100  # First block start
        assert target.end == 600    # Last block end 
        assert target.strand == Strand.PLUS
        assert "chain_1_target" in target.id
    
    def test_get_chain_query_interval(self, simple_genome_alignment):
        """Test query interval extraction."""
        query = get_chain_query_interval(simple_genome_alignment)
        
        assert isinstance(query, GenomicInterval)
        assert query.chrom == "chr2"
        assert query.start == 1000  # First block q_start
        assert query.end == 1500    # Last block q_end
        assert query.strand == Strand.PLUS
        assert "chain_1_query" in query.id
    
    def test_chain_coordinate_accessors(self, simple_genome_alignment):
        """Test individual coordinate accessors."""
        assert get_chain_t_start(simple_genome_alignment) == 100
        assert get_chain_t_end(simple_genome_alignment) == 600
        assert get_chain_q_start(simple_genome_alignment) == 1000
        assert get_chain_q_end(simple_genome_alignment) == 1500
    
    def test_empty_chain_raises_error(self):
        """Test that empty chains raise ValueError."""
        empty_chain = GenomeAlignment(
            chain_id=1, score=0, t_chrom="chr1", t_strand=1, t_size=1000,
            q_chrom="chr2", q_strand=1, q_size=1000,
            blocks=np.array([], dtype=np.int64).reshape(0, 4)
        )
        
        with pytest.raises(ValueError, match="Chain has no blocks"):
            get_chain_target_interval(empty_chain)
        
        with pytest.raises(ValueError, match="Chain has no blocks"):
            get_chain_query_interval(empty_chain)
            
        with pytest.raises(ValueError, match="Chain has no blocks"):
            get_chain_t_start(empty_chain)
    
    def test_none_genome_alignment_raises_error(self):
        """Test that None GenomeAlignment raises specific error."""
        with pytest.raises(ValueError, match="provided genome_alignment object is None"):
            get_chain_target_interval(None)


class TestSplitGenomeAlignment(TestFixtures):
    """Test chain splitting functionality."""
    
    def test_short_chain_no_split(self, simple_genome_alignment, sample_transcripts):
        """Test that short chains are not split."""
        # Chain length is 500, less than 1.5 * window_size (1M)
        subchains, mapping = split_genome_alignment(
            simple_genome_alignment, sample_transcripts, window_size=1_000_000
        )
        
        assert len(subchains) == 1
        assert subchains[0].child_id == 0
        assert len(mapping[0]) == 2  # Both transcripts mapped
    
    def test_split_with_transcripts(self, sample_transcripts):
        """Test splitting with transcript-guided boundaries."""
        # Create a longer chain that needs splitting
        large_blocks = np.array([
            [100, 200, 1000, 1100],
            [500_000, 500_100, 1_500_000, 1_500_100],
            [1_500_000, 1_500_100, 2_500_000, 2_500_100],
            [2_000_000, 2_000_100, 3_000_000, 3_000_100],
        ], dtype=np.int64)
        
        large_chain = GenomeAlignment(
            chain_id=2, score=2000, t_chrom="chr1", t_strand=1, t_size=10_000_000,
            q_chrom="chr2", q_strand=1, q_size=10_000_000, blocks=large_blocks
        )
        
        subchains, mapping = split_genome_alignment(
            large_chain, sample_transcripts, window_size=800_000
        )
        
        assert len(subchains) >= 1
        assert all(sc.child_id is not None for sc in subchains)
        assert all(sc.chain_id == 2 for sc in subchains)  # Same chain_id
    
    def test_split_empty_transcripts(self):
        """Test splitting with no transcripts."""
        large_blocks = np.array([
            [100, 200, 1000, 1100],
            [1_000_000, 1_000_100, 2_000_000, 2_000_100],
            [2_000_000, 2_000_100, 3_000_000, 3_000_100],
        ], dtype=np.int64)
        
        large_chain = GenomeAlignment(
            chain_id=3, score=3000, t_chrom="chr1", t_strand=1, t_size=10_000_000,
            q_chrom="chr2", q_strand=1, q_size=10_000_000, blocks=large_blocks
        )
        
        subchains, mapping = split_genome_alignment(
            large_chain, [], window_size=500_000
        )
        
        assert len(subchains) >= 2  # Should split based on window size only
        assert all(len(mapping[i]) == 0 for i in mapping)  # No transcripts


class TestRealDataIntegration(TestFixtures):
    """Integration tests with real chain data."""
    
    @pytest.mark.io
    def test_with_real_chain_data(self, loaded_chain):
        """Test functions with real chain data."""
        assert loaded_chain.chain_id is not None
        assert len(loaded_chain.blocks) > 0
        
        # Test accessors
        t_start = get_chain_t_start(loaded_chain)
        t_end = get_chain_t_end(loaded_chain) 
        q_start = get_chain_q_start(loaded_chain)
        q_end = get_chain_q_end(loaded_chain)
        
        assert t_start >= 0
        assert t_end > t_start
        assert q_start >= 0
        assert q_end > q_start
        
        # Test interval creation
        target_interval = get_chain_target_interval(loaded_chain)
        query_interval = get_chain_query_interval(loaded_chain)
        
        assert target_interval.start == t_start
        assert target_interval.end == t_end
        assert query_interval.start == q_start
        assert query_interval.end == q_end
    
    @pytest.mark.io
    def test_projection_with_real_data(self, loaded_chain):
        """Test interval projection with real chain data."""
        # Create test intervals within chain bounds
        t_start = get_chain_t_start(loaded_chain)
        t_end = get_chain_t_end(loaded_chain)
        
        # Small intervals within chain
        test_intervals = np.array([
            [t_start + 1000, t_start + 1100],
            [t_start + 5000, t_start + 5200],
        ], dtype=np.int64)
        
        results = project_intervals_through_chain(test_intervals, loaded_chain.blocks)
        
        assert len(results) == 2
        assert all(len(r) > 0 for r in results)
        assert all(r.shape[1] == 2 for r in results)  # Each result has start,end


class TestEdgeCases(TestFixtures):
    """Test edge cases and error conditions."""
    
    def test_single_base_intervals(self, simple_chain_blocks):
        """Test projection of single-base intervals."""
        intervals = np.array([[150, 151], [350, 351]], dtype=np.int64)
        results = project_intervals_through_chain(intervals, simple_chain_blocks)
        
        assert len(results) == 2
        assert all(r[0][1] > r[0][0] for r in results)  # End > start
    
    def test_intervals_in_gaps(self, simple_chain_blocks):
        """Test intervals that fall in gaps between blocks."""
        gap_intervals = np.array([[250, 280]], dtype=np.int64)  # Between blocks 1 and 2
        results = project_intervals_through_chain(gap_intervals, simple_chain_blocks)
        
        assert len(results) == 1
        # Should get gap coordinates
        result = results[0][0]
        assert result[0] == 1100  # End of previous block
        assert result[1] == 1200  # Start of next block
    
    def test_strand_handling(self):
        """Test different strand configurations."""
        # Negative strand chain
        neg_blocks = np.array([[100, 200, 1000, 1100]], dtype=np.int64)
        neg_chain = GenomeAlignment(
            chain_id=4, score=1000, t_chrom="chr1", t_strand=-1, t_size=1000000,
            q_chrom="chr2", q_strand=-1, q_size=1000000, blocks=neg_blocks
        )
        
        target = get_chain_target_interval(neg_chain)
        query = get_chain_query_interval(neg_chain)
        
        assert target.strand == Strand.MINUS
        assert query.strand == Strand.MINUS
    
    def test_large_intervals(self, simple_chain_blocks):
        """Test projection of very large intervals."""
        large_intervals = np.array([[0, 1000000]], dtype=np.int64)
        results = project_intervals_through_chain(large_intervals, simple_chain_blocks)
        
        assert len(results) == 1
        # Should be clamped to chain bounds
        result = results[0][0]
        assert result[0] >= 1000  # Min bound
        assert result[1] <= 1500  # Max bound


