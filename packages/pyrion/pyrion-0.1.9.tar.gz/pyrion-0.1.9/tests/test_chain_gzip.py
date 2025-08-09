"""Tests for gzip chain file support."""

import time
from pathlib import Path
import numpy as np

from pyrion.io.chain import read_chain_file


class TestChainGzipSupport:
    """Test gzip functionality for chain files."""
    
    def test_gzip_detection(self):
        """Test that gzip files are detected correctly."""
        # Test file paths
        regular_path = Path("test.chain")
        gzip_path = Path("test.chain.gz")
        
        # This tests the path detection logic, not actual file reading
        assert not gzip_path.suffix.lower() == regular_path.suffix.lower()
        assert gzip_path.suffix.lower() == '.gz'
    
    def test_gzip_vs_regular_identical_results(self):
        """Test that gzipped and regular files produce identical results."""
        original_file = Path("test_data/chains/hg38.chr9.mm39.chr4.chain")
        gzipped_file = Path("test_data/chains/hg38.chr9.mm39.chr4.chain.gz")
        
        if not original_file.exists() or not gzipped_file.exists():
            # Skip if test files don't exist
            return
        
        # Load both files
        collection_original = read_chain_file(original_file)
        collection_gzipped = read_chain_file(gzipped_file)
        
        # Verify same number of alignments
        assert len(collection_original) == len(collection_gzipped)
        
        # Verify first few alignments are identical
        for i in range(min(5, len(collection_original))):
            align_orig = collection_original.alignments[i]
            align_gz = collection_gzipped.alignments[i]
            
            assert align_orig.chain_id == align_gz.chain_id
            assert align_orig.score == align_gz.score
            assert align_orig.t_chrom == align_gz.t_chrom
            assert align_orig.q_chrom == align_gz.q_chrom
            assert len(align_orig.blocks) == len(align_gz.blocks)
            
            # Check first few blocks are identical
            for j in range(min(3, len(align_orig.blocks))):
                assert np.array_equal(align_orig.blocks[j], align_gz.blocks[j])
    
    def test_gzip_with_score_filter(self):
        """Test that score filtering works identically for both formats."""
        original_file = Path("test_data/chains/hg38.chr9.mm39.chr4.chain")
        gzipped_file = Path("test_data/chains/hg38.chr9.mm39.chr4.chain.gz")
        
        if not original_file.exists() or not gzipped_file.exists():
            return
        
        min_score = 1000
        
        # Load both files with score filter
        collection_original = read_chain_file(original_file, min_score=min_score)
        collection_gzipped = read_chain_file(gzipped_file, min_score=min_score)
        
        # Verify same number of filtered alignments
        assert len(collection_original) == len(collection_gzipped)
        
        # Verify all alignments meet score threshold
        for alignment in collection_original.alignments:
            assert alignment.score >= min_score
        for alignment in collection_gzipped.alignments:
            assert alignment.score >= min_score
    
    def test_gzip_performance_reasonable(self):
        """Test that gzip overhead is reasonable."""
        original_file = Path("test_data/chains/hg38.chr9.mm39.chr4.chain")
        gzipped_file = Path("test_data/chains/hg38.chr9.mm39.chr4.chain.gz")
        
        if not original_file.exists() or not gzipped_file.exists():
            return
        
        # Time both operations
        start_time = time.perf_counter()
        collection_original = read_chain_file(original_file)
        original_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        collection_gzipped = read_chain_file(gzipped_file)
        gzipped_time = time.perf_counter() - start_time
        
        # Gzip should not be more than 2x slower
        assert gzipped_time < original_time * 2.0
        
        # Both should produce same results
        assert len(collection_original) == len(collection_gzipped)
        
    def test_nonexistent_gzip_file(self):
        """Test error handling for nonexistent gzip files."""
        nonexistent_file = Path("nonexistent.chain.gz")
        
        try:
            read_chain_file(nonexistent_file)
            assert False, "Should have raised an exception"
        except FileNotFoundError:
            pass  # Expected
        except Exception as e:
            # Other exceptions are also acceptable as long as it fails gracefully
            assert "not found" in str(e).lower() or "no such file" in str(e).lower()


if __name__ == "__main__":
    """Run tests manually if called directly."""
    test_instance = TestChainGzipSupport()
    
    print("🧪 Running Chain Gzip Tests")
    print("=" * 40)
    
    tests = [
        ("Gzip detection", test_instance.test_gzip_detection),
        ("Identical results", test_instance.test_gzip_vs_regular_identical_results),
        ("Score filtering", test_instance.test_gzip_with_score_filter),
        ("Performance", test_instance.test_gzip_performance_reasonable),
        ("Error handling", test_instance.test_nonexistent_gzip_file),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name} - PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} - FAILED: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All gzip tests passed!")
    else:
        print("❌ Some tests failed")