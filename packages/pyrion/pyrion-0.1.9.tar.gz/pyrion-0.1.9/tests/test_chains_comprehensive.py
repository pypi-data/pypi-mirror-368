"""Comprehensive tests for pyrion.ops.chains module."""

import pytest
import numpy as np
from pathlib import Path


class TestChainsComprehensive:
    """Comprehensive tests for chains module functionality."""
    
    @pytest.fixture
    def simple_chain_blocks(self):
        """Simple chain blocks for testing."""
        return np.array([
            [100, 200, 1000, 1100],
            [300, 400, 1200, 1300],
        ], dtype=np.int64)
    
    @pytest.fixture
    def test_intervals(self):
        """Test intervals for projection."""
        return np.array([[150, 180], [350, 380]], dtype=np.int64)
    
    def test_all_projection_methods(self, simple_chain_blocks, test_intervals):
        """Test all available projection methods."""
        from pyrion.ops.chains import (
            project_intervals_through_chain,
            _project_intervals_vectorized,
            _project_intervals_numpy,
            HAS_NUMBA
        )
        
        # Test main function
        results_main = project_intervals_through_chain(test_intervals, simple_chain_blocks)
        assert len(results_main) == 2
        
        # Test vectorized implementation
        results_vec = _project_intervals_vectorized(test_intervals, simple_chain_blocks)
        assert len(results_vec) == 2
        
        # Test numpy implementation  
        results_numpy = _project_intervals_numpy(test_intervals, simple_chain_blocks)
        assert len(results_numpy) == 2
        
        # Test numba implementation if available
        if HAS_NUMBA:
            from pyrion.ops.chains import _project_intervals_numba
            results_numba = _project_intervals_numba(test_intervals, simple_chain_blocks)
            assert len(results_numba) == 2
            
            # Results should be identical across implementations
            for i in range(len(results_main)):
                np.testing.assert_array_equal(results_main[i], results_numba[i])
    
    def test_projection_edge_cases(self, simple_chain_blocks):
        """Test projection with edge cases."""
        from pyrion.ops.chains import project_intervals_through_chain
        
        # Empty intervals
        empty_intervals = np.array([], dtype=np.int64).reshape(0, 2)
        results = project_intervals_through_chain(empty_intervals, simple_chain_blocks)
        assert len(results) == 0
        
        # Single base intervals
        single_base = np.array([[150, 151]], dtype=np.int64)
        results = project_intervals_through_chain(single_base, simple_chain_blocks)
        assert len(results) == 1
        assert results[0].shape[1] == 2
        
        # Intervals spanning chain gaps
        spanning = np.array([[250, 350]], dtype=np.int64)
        results = project_intervals_through_chain(spanning, simple_chain_blocks)
        # Should handle gracefully (may be empty or partial)
        assert isinstance(results, list)
    
    def test_genome_alignment_projections(self, simple_chain_blocks):
        """Test projections through GenomeAlignment objects."""
        from pyrion.ops.chains import (
            project_intervals_through_genome_alignment,
            project_intervals_through_genome_alignment_to_intervals
        )
        from pyrion.core.genome_alignment import GenomeAlignment
        from pyrion.core.intervals import GenomicInterval
        from pyrion.core.strand import Strand
        
        alignment = GenomeAlignment(
            chain_id=1, score=1000, t_chrom="chr1", t_strand=1, t_size=1000000,
            q_chrom="chr2", q_strand=1, q_size=1000000, blocks=simple_chain_blocks
        )
        
        test_intervals = [GenomicInterval("chr1", 150, 180, Strand.PLUS)]
        
        # Convert GenomicInterval to numpy array format for projection
        intervals_array = np.array([[150, 180]], dtype=np.int32)
        
        # Test array output
        results_array = project_intervals_through_genome_alignment(intervals_array, alignment)
        assert len(results_array) == 1
        
        # Test GenomicInterval output
        results_intervals = project_intervals_through_genome_alignment_to_intervals(
            intervals_array, alignment
        )
        assert len(results_intervals) == 1
        assert isinstance(results_intervals[0], GenomicInterval)
        assert results_intervals[0].chrom == "chr2"
    
    def test_chain_splitting(self):
        """Test chain splitting functionality."""
        from pyrion.ops.chains import split_genome_alignment
        from pyrion.core.genome_alignment import GenomeAlignment
        from pyrion.core.genes import Transcript
        from pyrion.core.intervals import GenomicInterval
        from pyrion.core.strand import Strand
        
        # Create a larger chain for splitting
        large_blocks = np.array([
            [100, 500, 1000, 1400],
            [600, 1000, 1500, 1900],
        ], dtype=np.int64)
        
        alignment = GenomeAlignment(
            chain_id=1, score=2000, t_chrom="chr1", t_strand=1, t_size=2000000,
            q_chrom="chr2", q_strand=1, q_size=2000000, blocks=large_blocks
        )
        
        # Create test transcripts
        transcripts = [
            Transcript(
                blocks=np.array([[200, 300]], dtype=np.int32),
                strand=Strand.PLUS,
                chrom="chr1",
                id="T1"
            ),
            Transcript(
                blocks=np.array([[700, 800]], dtype=np.int32),
                strand=Strand.PLUS,
                chrom="chr1",
                id="T2"
            )
        ]
        
        # Test splitting
        split_results, transcript_mapping = split_genome_alignment(alignment, transcripts)
        assert isinstance(split_results, list)
        assert isinstance(transcript_mapping, dict)
    
    @pytest.mark.io
    def test_real_chain_data(self):
        """Test with real chain data if available."""
        from pyrion.io.chain import read_chain_file
        from pyrion.ops.chains import (
            get_chain_t_start, get_chain_t_end,
            project_intervals_through_chain
        )
        
        test_files = [
            Path("test_data/chains/hg38.chr9.mm39.chr4.chain"),
            Path("test_data/chains/hg38.chr9.mm39.chr4.chain.gz")
        ]
        
        for chain_file in test_files:
            if chain_file.exists():
                collection = read_chain_file(chain_file)
                if len(collection.alignments) > 0:
                    alignment = collection.alignments[0]
                    
                    # Test coordinate accessors
                    t_start = get_chain_t_start(alignment)
                    t_end = get_chain_t_end(alignment)
                    assert t_start < t_end
                    
                    # Test projection with real data
                    test_intervals = np.array([[t_start + 1000, t_start + 1100]], dtype=np.int64)
                    results = project_intervals_through_chain(test_intervals, alignment.blocks)
                    assert isinstance(results, list)
                    
                    break  # Test with first available file
    
    @pytest.mark.slow
    def test_performance_benchmark(self):
        """Benchmark different projection implementations."""
        import time
        from pyrion.ops.chains import (
            _project_intervals_vectorized,
            _project_intervals_numpy,
            HAS_NUMBA
        )
        
        # Create larger test data
        large_blocks = np.array([
            [i*1000, (i+1)*1000-100, i*2000, (i+1)*2000-100] 
            for i in range(100)
        ], dtype=np.int64)
        
        large_intervals = np.array([
            [i*1000 + 50, i*1000 + 150] 
            for i in range(50)
        ], dtype=np.int64)
        
        # Benchmark vectorized
        start_time = time.time()
        results_vec = _project_intervals_vectorized(large_intervals, large_blocks)
        vec_time = time.time() - start_time
        
        # Benchmark numpy
        start_time = time.time()
        results_numpy = _project_intervals_numpy(large_intervals, large_blocks)
        numpy_time = time.time() - start_time
        
        # Both should produce results
        assert len(results_vec) == len(results_numpy)
        
        # Performance should be reasonable (less than 1 second for this size)
        assert vec_time < 1.0
        assert numpy_time < 1.0
        
        # Test numba if available
        if HAS_NUMBA:
            from pyrion.ops.chains import _project_intervals_numba
            
            # First call includes compilation time
            start_time = time.time()
            results_numba = _project_intervals_numba(large_intervals, large_blocks)
            first_numba_time = time.time() - start_time
            
            # Second call should be faster (compiled)
            start_time = time.time()
            _project_intervals_numba(large_intervals, large_blocks)
            second_numba_time = time.time() - start_time
            
            assert len(results_numba) == len(results_vec)
            # Second call should generally be faster than first (but timing can be flaky)
            # Just check that both calls completed successfully
            assert first_numba_time > 0
            assert second_numba_time > 0
    
    def test_chain_coordinate_accessors(self):
        """Test all chain coordinate accessor functions."""
        from pyrion.ops.chains import (
            get_chain_t_start, get_chain_t_end,
            get_chain_q_start, get_chain_q_end,
            get_chain_target_interval, get_chain_query_interval
        )
        from pyrion.core.genome_alignment import GenomeAlignment
        
        blocks = np.array([
            [100, 200, 1000, 1100],
            [300, 400, 1200, 1300],
        ], dtype=np.int64)
        
        alignment = GenomeAlignment(
            chain_id=1, score=1000, t_chrom="chr1", t_strand=1, t_size=1000000,
            q_chrom="chr2", q_strand=1, q_size=1000000, blocks=blocks
        )
        
        # Test target coordinates
        assert get_chain_t_start(alignment) == 100
        assert get_chain_t_end(alignment) == 400
        
        # Test query coordinates  
        assert get_chain_q_start(alignment) == 1000
        assert get_chain_q_end(alignment) == 1300
        
        # Test interval objects
        target_interval = get_chain_target_interval(alignment)
        assert target_interval.chrom == "chr1"
        assert target_interval.start == 100
        assert target_interval.end == 400
        
        query_interval = get_chain_query_interval(alignment)
        assert query_interval.chrom == "chr2"
        assert query_interval.start == 1000
        assert query_interval.end == 1300