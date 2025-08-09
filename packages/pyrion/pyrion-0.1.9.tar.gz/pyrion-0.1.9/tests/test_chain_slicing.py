"""Unit tests for pyrion.ops.chain_slicing module."""

import pytest
import numpy as np
from typing import Optional

from pyrion.core.genome_alignment import GenomeAlignment
from pyrion.ops.chain_slicing import (
    slice_chain_target_space,
    slice_chain_query_space,
    remove_chain_region_target_space,
    _find_overlapping_target_block,
    _find_overlapping_query_block,
    _find_containing_target_block,
    _map_target_to_query,
    _create_empty_chain_copy
)


class TestFixtures:
    """Test data fixtures for chain slicing operations."""
    
    @pytest.fixture
    def simple_positive_chain(self):
        """Simple chain with positive query strand."""
        return GenomeAlignment(
            chain_id=1,
            score=10000,
            t_chrom="chr1",
            t_strand=1,
            t_size=5000,
            q_chrom="chr2",
            q_strand=1,  # Positive strand
            q_size=4000,
            blocks=np.array([
                [100, 200, 50, 150],    # Target 100-200 -> Query 50-150
                [300, 400, 200, 300],   # Target 300-400 -> Query 200-300
                [500, 600, 350, 450]    # Target 500-600 -> Query 350-450
            ], dtype=np.int32)
        )
    
    @pytest.fixture
    def simple_negative_chain(self):
        """Simple chain with negative query strand."""
        return GenomeAlignment(
            chain_id=2,
            score=8000,
            t_chrom="chr3",
            t_strand=1,
            t_size=3000,
            q_chrom="chr4",
            q_strand=-1,  # Negative strand
            q_size=2500,
            blocks=np.array([
                [1000, 1100, 500, 600],  # Target 1000-1100 -> Query 500-600
                [1300, 1400, 300, 400],  # Target 1300-1400 -> Query 300-400
                [1600, 1700, 100, 200]   # Target 1600-1700 -> Query 100-200
            ], dtype=np.int32)
        )
    
    @pytest.fixture
    def overlapping_blocks_chain(self):
        """Chain with closely spaced blocks for testing edge cases."""
        return GenomeAlignment(
            chain_id=3,
            score=5000,
            t_chrom="chr5",
            t_strand=1,
            t_size=2000,
            q_chrom="chr6",
            q_strand=1,
            q_size=1800,
            blocks=np.array([
                [100, 200, 100, 200],
                [250, 350, 250, 350],
                [400, 500, 400, 500]
            ], dtype=np.int32)
        )
    
    @pytest.fixture
    def single_block_chain(self):
        """Chain with single block."""
        return GenomeAlignment(
            chain_id=4,
            score=3000,
            t_chrom="chr7",
            t_strand=1,
            t_size=1000,
            q_chrom="chr8",
            q_strand=1,
            q_size=1000,
            blocks=np.array([[200, 400, 100, 300]], dtype=np.int32)
        )
    
    @pytest.fixture
    def empty_chain(self):
        """Empty chain for testing edge cases."""
        return GenomeAlignment(
            chain_id=5,
            score=0,
            t_chrom="chr9",
            t_strand=1,
            t_size=1000,
            q_chrom="chr10",
            q_strand=1,
            q_size=1000,
            blocks=np.empty((0, 4), dtype=np.int32)
        )


class TestSliceChainTargetSpace(TestFixtures):
    """Test slicing chains in target coordinate space."""
    
    def test_slice_target_basic_positive_strand(self, simple_positive_chain):
        """Test basic target space slicing with positive strand."""
        # Slice that intersects first two blocks
        result = slice_chain_target_space(simple_positive_chain, 150, 350)
        
        assert len(result.blocks) == 2
        
        # First block: original [100,200,50,150] sliced to [150,200]
        # Query coordinates should be proportionally adjusted
        block1 = result.blocks[0]
        assert block1[0] == 150  # t_start
        assert block1[1] == 200  # t_end
        assert block1[2] == 100  # q_start (50 + 50% of 100)
        assert block1[3] == 150  # q_end
        
        # Second block: original [300,400,200,300] sliced to [300,350]
        block2 = result.blocks[1]
        assert block2[0] == 300  # t_start
        assert block2[1] == 350  # t_end
        assert block2[2] == 200  # q_start
        assert block2[3] == 250  # q_end (200 + 50% of 100)
        
        # Chain metadata should be preserved
        assert result.chain_id == simple_positive_chain.chain_id
        assert result.t_chrom == simple_positive_chain.t_chrom
        assert result.q_chrom == simple_positive_chain.q_chrom
        assert result.q_strand == simple_positive_chain.q_strand
    
    def test_slice_target_basic_negative_strand(self, simple_negative_chain):
        """Test basic target space slicing with negative strand."""
        # Slice that intersects first block
        result = slice_chain_target_space(simple_negative_chain, 1050, 1150)
        
        assert len(result.blocks) == 1
        
        # Block coordinates should be adjusted for negative strand
        block = result.blocks[0]
        assert block[0] == 1050  # t_start
        assert block[1] == 1100  # t_end (trimmed)
        # Query coordinates should be adjusted appropriately for negative strand
        assert block[2] >= 500   # q_start
        assert block[3] <= 600   # q_end
    
    def test_slice_target_complete_blocks(self, simple_positive_chain):
        """Test slicing that includes complete blocks."""
        # Slice that completely contains the second block
        result = slice_chain_target_space(simple_positive_chain, 250, 450)
        
        assert len(result.blocks) == 1
        
        # Should be exactly the second block
        block = result.blocks[0]
        assert block[0] == 300  # t_start
        assert block[1] == 400  # t_end
        assert block[2] == 200  # q_start
        assert block[3] == 300  # q_end
    
    def test_slice_target_no_intersection(self, simple_positive_chain):
        """Test slicing with no intersection."""
        # Slice in region with no blocks
        result = slice_chain_target_space(simple_positive_chain, 700, 800)
        
        # Should return empty chain
        assert len(result.blocks) == 0
        assert result.score == 0
        assert result.t_chrom == simple_positive_chain.t_chrom
        assert result.q_chrom == simple_positive_chain.q_chrom
    
    def test_slice_target_partial_overlap(self, simple_positive_chain):
        """Test slicing with partial block overlap."""
        # Slice that partially overlaps first block
        result = slice_chain_target_space(simple_positive_chain, 80, 150)
        
        assert len(result.blocks) == 1
        
        block = result.blocks[0]
        assert block[0] == 100  # t_start (trimmed to block boundary)
        assert block[1] == 150  # t_end
        # Query should be proportionally adjusted
        assert block[2] == 50   # q_start
        assert block[3] == 100  # q_end (half of original range)
    
    def test_slice_target_empty_chain(self, empty_chain):
        """Test slicing empty chain."""
        result = slice_chain_target_space(empty_chain, 100, 200)
        
        assert len(result.blocks) == 0
        assert result.score == 0
        assert result.chain_id == empty_chain.chain_id
    
    def test_slice_target_single_block(self, single_block_chain):
        """Test slicing single block chain."""
        result = slice_chain_target_space(single_block_chain, 250, 350)
        
        assert len(result.blocks) == 1
        
        block = result.blocks[0]
        assert block[0] == 250  # t_start
        assert block[1] == 350  # t_end
        # Query coordinates proportionally adjusted
        assert block[2] == 150  # q_start (100 + 25% of 200)
        assert block[3] == 250  # q_end (100 + 75% of 200)
    
    def test_slice_target_edge_boundaries(self, simple_positive_chain):
        """Test slicing at exact block boundaries."""
        # Slice exactly at block boundaries
        result = slice_chain_target_space(simple_positive_chain, 200, 300)
        
        # Should return empty since there's no overlap at boundaries
        assert len(result.blocks) == 0


class TestSliceChainQuerySpace(TestFixtures):
    """Test slicing chains in query coordinate space."""
    
    def test_slice_query_basic_positive_strand(self, simple_positive_chain):
        """Test basic query space slicing with positive strand."""
        # Slice that intersects first two blocks in query space
        result = slice_chain_query_space(simple_positive_chain, 100, 250)
        
        assert len(result.blocks) == 2
        
        # First block query [50,150] sliced to [100,150]
        block1 = result.blocks[0]
        assert block1[2] == 100  # q_start
        assert block1[3] == 150  # q_end
        # Target coordinates should be proportionally adjusted
        assert block1[0] == 150  # t_start (100 + 50% of 100)
        assert block1[1] == 200  # t_end
        
        # Second block query [200,300] sliced to [200,250]
        block2 = result.blocks[1]
        assert block2[2] == 200  # q_start
        assert block2[3] == 250  # q_end
        assert block2[0] == 300  # t_start
        assert block2[1] == 350  # t_end (300 + 50% of 100)
    
    def test_slice_query_negative_strand(self, simple_negative_chain):
        """Test query space slicing with negative strand."""
        # Slice in query space
        result = slice_chain_query_space(simple_negative_chain, 150, 350)
        
        # Should handle negative strand coordinate mapping
        assert len(result.blocks) >= 1
        
        # Verify target coordinates are adjusted correctly for negative strand
        for block in result.blocks:
            assert block[0] < block[1]  # Valid target coordinates
            assert block[2] < block[3]  # Valid query coordinates
    
    def test_slice_query_no_intersection(self, simple_positive_chain):
        """Test query slicing with no intersection."""
        # Slice in region with no query coordinates
        result = slice_chain_query_space(simple_positive_chain, 600, 700)
        
        assert len(result.blocks) == 0
        assert result.score == 0
    
    def test_slice_query_complete_block(self, simple_positive_chain):
        """Test query slicing that includes complete block."""
        # Slice that completely contains second block's query coordinates
        result = slice_chain_query_space(simple_positive_chain, 150, 350)
        
        # Should include the second block completely
        assert len(result.blocks) >= 1
        
        # Check that one block has the complete query range
        block_found = False
        for block in result.blocks:
            if block[2] == 200 and block[3] == 300:
                assert block[0] == 300  # t_start
                assert block[1] == 400  # t_end
                block_found = True
        assert block_found
    
    def test_slice_query_empty_chain(self, empty_chain):
        """Test query slicing empty chain."""
        result = slice_chain_query_space(empty_chain, 100, 200)
        
        assert len(result.blocks) == 0
        assert result.score == 0


class TestRemoveChainRegionTargetSpace(TestFixtures):
    """Test removing regions from chains in target space."""
    
    def test_remove_region_middle_of_block(self, single_block_chain):
        """Test removing region from middle of a block."""
        # Remove region from middle of the single block [200,400]
        result = remove_chain_region_target_space(single_block_chain, 250, 350)
        
        assert len(result.blocks) == 2
        
        # Should split into two blocks
        block1, block2 = result.blocks
        
        # First part: [200,250]
        assert block1[0] == 200
        assert block1[1] == 250
        
        # Second part: [350,400]  
        assert block2[0] == 350
        assert block2[1] == 400
        
        # Query coordinates should be mapped appropriately
        assert block1[2] < block1[3]  # Valid query range
        assert block2[2] < block2[3]  # Valid query range
    
    def test_remove_region_entire_block(self, simple_positive_chain):
        """Test removing region that covers entire block."""
        # Remove region that completely covers the second block
        result = remove_chain_region_target_space(simple_positive_chain, 250, 450)
        
        # Should have 2 blocks left (first and third)
        assert len(result.blocks) == 2
        
        # Verify remaining blocks are first and third
        assert result.blocks[0][0] == 100  # First block t_start
        assert result.blocks[0][1] == 200  # First block t_end
        assert result.blocks[1][0] == 500  # Third block t_start
        assert result.blocks[1][1] == 600  # Third block t_end
    
    def test_remove_region_no_intersection(self, simple_positive_chain):
        """Test removing region that doesn't intersect any blocks."""
        # Remove region in gap between blocks
        result = remove_chain_region_target_space(simple_positive_chain, 220, 280)
        
        # Should return unchanged chain
        assert len(result.blocks) == len(simple_positive_chain.blocks)
        assert np.array_equal(result.blocks, simple_positive_chain.blocks)
    
    def test_remove_region_partial_overlap(self, simple_positive_chain):
        """Test removing region with partial block overlap."""
        # Remove region that partially overlaps first block
        result = remove_chain_region_target_space(simple_positive_chain, 150, 250)
        
        # First block should be trimmed, others unchanged
        assert len(result.blocks) == 3
        
        # First block trimmed from left
        block1 = result.blocks[0]
        assert block1[0] == 100  # t_start unchanged
        assert block1[1] == 150  # t_end trimmed
        
        # Other blocks should be unchanged
        assert result.blocks[1][0] == 300  # Second block t_start
        assert result.blocks[2][0] == 500  # Third block t_start
    
    def test_remove_region_empty_chain(self, empty_chain):
        """Test removing region from empty chain."""
        result = remove_chain_region_target_space(empty_chain, 100, 200)
        
        assert len(result.blocks) == 0
        assert result.score == 0
    
    def test_remove_region_entire_chain(self, simple_positive_chain):
        """Test removing region that covers entire chain."""
        # Remove region that covers all blocks
        result = remove_chain_region_target_space(simple_positive_chain, 50, 650)
        
        assert len(result.blocks) == 0
        assert result.score == 0


class TestHelperFunctions(TestFixtures):
    """Test helper functions."""
    
    def test_find_overlapping_target_block(self, simple_positive_chain):
        """Test finding overlapping target block."""
        blocks = simple_positive_chain.blocks
        
        # Test overlaps
        assert _find_overlapping_target_block(blocks, 150, 180) == 0  # First block
        assert _find_overlapping_target_block(blocks, 350, 380) == 1  # Second block
        assert _find_overlapping_target_block(blocks, 550, 580) == 2  # Third block
        
        # Test no overlap
        assert _find_overlapping_target_block(blocks, 250, 280) is None  # Gap
        assert _find_overlapping_target_block(blocks, 700, 800) is None  # After all
    
    def test_find_overlapping_query_block(self, simple_positive_chain):
        """Test finding overlapping query block."""
        blocks = simple_positive_chain.blocks
        
        # Test overlaps
        assert _find_overlapping_query_block(blocks, 100, 120) == 0  # First block
        assert _find_overlapping_query_block(blocks, 250, 280) == 1  # Second block
        assert _find_overlapping_query_block(blocks, 400, 430) == 2  # Third block
        
        # Test no overlap
        assert _find_overlapping_query_block(blocks, 160, 190) is None  # Gap
        assert _find_overlapping_query_block(blocks, 500, 600) is None  # After all
    
    def test_find_containing_target_block(self, simple_positive_chain):
        """Test finding containing target block."""
        blocks = simple_positive_chain.blocks
        
        # Test containment
        assert _find_containing_target_block(blocks, 120, 180) == 0  # Within first
        assert _find_containing_target_block(blocks, 320, 380) == 1  # Within second
        
        # Test no containment
        assert _find_containing_target_block(blocks, 150, 250) is None  # Spans blocks
        assert _find_containing_target_block(blocks, 50, 250) is None   # Too large
    
    def test_map_target_to_query_positive_strand(self):
        """Test mapping target coordinates to query for positive strand."""
        block = np.array([100, 200, 50, 150], dtype=np.int32)
        
        # Map middle 50% of target block
        q_start, q_end = _map_target_to_query(block, 125, 175, q_strand=1)
        
        assert q_start == 75   # 50 + 25% of 100
        assert q_end == 125    # 50 + 75% of 100
    
    def test_map_target_to_query_negative_strand(self):
        """Test mapping target coordinates to query for negative strand."""
        block = np.array([100, 200, 50, 150], dtype=np.int32)
        
        # Map middle 50% of target block on negative strand
        q_start, q_end = _map_target_to_query(block, 125, 175, q_strand=-1)
        
        # Coordinates are flipped for negative strand
        assert q_start > q_end  # Start > end for negative strand
        assert q_end >= 50 and q_start <= 150  # Within original range
        assert q_start == 125 and q_end == 75  # Expected values
    
    def test_map_target_to_query_zero_length(self):
        """Test mapping with zero-length target block."""
        block = np.array([100, 100, 50, 150], dtype=np.int32)
        
        q_start, q_end = _map_target_to_query(block, 100, 100, q_strand=1)
        
        assert q_start == 50  # Should return original start
        assert q_end == 50    # No length
    
    def test_create_empty_chain_copy(self, simple_positive_chain):
        """Test creating empty chain copy."""
        empty = _create_empty_chain_copy(simple_positive_chain)
        
        assert len(empty.blocks) == 0
        assert empty.score == 0
        assert empty.chain_id == simple_positive_chain.chain_id
        assert empty.t_chrom == simple_positive_chain.t_chrom
        assert empty.q_chrom == simple_positive_chain.q_chrom
        assert empty.t_strand == simple_positive_chain.t_strand
        assert empty.q_strand == simple_positive_chain.q_strand
        assert empty.t_size == simple_positive_chain.t_size
        assert empty.q_size == simple_positive_chain.q_size


class TestAlgorithmSelection(TestFixtures):
    """Test algorithm selection and consistency."""
    
    def test_numba_vs_numpy_consistency_target_slice(self, simple_positive_chain):
        """Test that numba and numpy give consistent results for target slicing."""
        start, end = 150, 450
        
        result_numba = slice_chain_target_space(simple_positive_chain, start, end, use_numba=True)
        result_numpy = slice_chain_target_space(simple_positive_chain, start, end, use_numba=False)
        
        assert len(result_numba.blocks) == len(result_numpy.blocks)
        assert np.array_equal(result_numba.blocks, result_numpy.blocks)
    
    def test_numba_vs_numpy_consistency_query_slice(self, simple_positive_chain):
        """Test that numba and numpy give consistent results for query slicing."""
        start, end = 100, 400
        
        result_numba = slice_chain_query_space(simple_positive_chain, start, end, use_numba=True)
        result_numpy = slice_chain_query_space(simple_positive_chain, start, end, use_numba=False)
        
        assert len(result_numba.blocks) == len(result_numpy.blocks)
        assert np.array_equal(result_numba.blocks, result_numpy.blocks)
    
    def test_numba_vs_numpy_consistency_remove(self, simple_positive_chain):
        """Test that numba and numpy give consistent results for region removal."""
        start, end = 150, 450
        
        result_numba = remove_chain_region_target_space(simple_positive_chain, start, end, use_numba=True)
        result_numpy = remove_chain_region_target_space(simple_positive_chain, start, end, use_numba=False)
        
        assert len(result_numba.blocks) == len(result_numpy.blocks)
        # Sort results for comparison since order might differ
        if len(result_numba.blocks) > 0:
            numba_sorted = result_numba.blocks[np.argsort(result_numba.blocks[:, 0])]
            numpy_sorted = result_numpy.blocks[np.argsort(result_numpy.blocks[:, 0])]
            assert np.array_equal(numba_sorted, numpy_sorted)


class TestEdgeCases(TestFixtures):
    """Test edge cases and error conditions."""
    
    def test_slice_invalid_coordinates(self, simple_positive_chain):
        """Test slicing with invalid coordinates."""
        # Start >= end should raise ValueError
        with pytest.raises(ValueError, match="Invalid slice"):
            slice_chain_target_space(simple_positive_chain, 300, 300)
        
        with pytest.raises(ValueError, match="Invalid slice"):
            slice_chain_target_space(simple_positive_chain, 400, 300)
    
    def test_very_small_slices(self, simple_positive_chain):
        """Test very small slice regions."""
        # Slice very small region
        result = slice_chain_target_space(simple_positive_chain, 150, 151)
        
        if len(result.blocks) > 0:
            # If slice is found, coordinates should be valid
            for block in result.blocks:
                assert block[0] < block[1]  # Valid target range
                assert block[2] < block[3]  # Valid query range
    
    def test_large_coordinates(self):
        """Test with very large coordinates."""
        large_chain = GenomeAlignment(
            chain_id=99,
            score=10000,
            t_chrom="chr1",
            t_strand=1,
            t_size=1000000000,
            q_chrom="chr2",
            q_strand=1,
            q_size=1000000000,
            blocks=np.array([[1000000, 2000000, 500000, 1500000]], dtype=np.int32)
        )
        
        result = slice_chain_target_space(large_chain, 1500000, 1800000)
        assert len(result.blocks) == 1
        
        block = result.blocks[0]
        assert block[0] == 1500000
        assert block[1] == 1800000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])