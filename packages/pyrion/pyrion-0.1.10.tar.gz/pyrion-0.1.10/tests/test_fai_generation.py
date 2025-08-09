"""Test FASTA index (.fai) file generation and validation.

Tests for creating, validating, and managing FASTA index files using the
high-performance C extension parser with real genomic data.
"""

import pytest
import os
from pathlib import Path
from pyrion.io.fai import create_fasta_index, load_fasta_index
from pyrion.core.fai import FaiStore, FaiEntry


@pytest.mark.io
class TestFAIGeneration:
    """Test FASTA index file generation and validation."""
    
    @pytest.fixture
    def arf5_fasta_file(self):
        """Path to ARF5 FASTA test file."""
        return Path("test_data/fasta/ARF5.fasta")
    
    @pytest.fixture
    def fai_output_path(self):
        """Path for FAI output in test_outputs directory."""
        output_dir = Path("test_outputs")
        output_dir.mkdir(exist_ok=True, parents=True)
        return output_dir / "ARF5.fasta.fai"
    
    def test_arf5_fasta_exists(self, arf5_fasta_file):
        """Test that the ARF5 FASTA file exists and is not empty."""
        assert arf5_fasta_file.exists(), f"ARF5 FASTA file not found: {arf5_fasta_file}"
        assert arf5_fasta_file.stat().st_size > 0, "ARF5 FASTA file is empty"
        
        # Check that it's a reasonable size (should be ~401KB)
        size_kb = arf5_fasta_file.stat().st_size / 1024
        assert 300 < size_kb < 500, f"ARF5 FASTA file size unexpected: {size_kb:.1f}KB"
    
    def test_generate_fai_for_arf5(self, arf5_fasta_file, fai_output_path):
        """Test generating FAI index for ARF5 FASTA file."""
        # Clean up any existing FAI file
        if fai_output_path.exists():
            fai_output_path.unlink()
        
        # Generate FAI index
        fai_store = create_fasta_index(str(arf5_fasta_file), str(fai_output_path))
        
        # Verify FAI file was created
        assert fai_output_path.exists(), f"FAI file was not created: {fai_output_path}"
        assert fai_output_path.stat().st_size > 0, "FAI file is empty"
        
        # Verify returned FaiStore object
        assert isinstance(fai_store, FaiStore)
        assert len(fai_store) > 0, "FAI store is empty"
    
    def test_validate_fai_content(self, arf5_fasta_file, fai_output_path):
        """Test validating the content of the generated FAI file."""
        # Generate FAI (reusing from previous test or creating new)
        if not fai_output_path.exists():
            fai_store = create_fasta_index(str(arf5_fasta_file), str(fai_output_path))
        else:
            fai_store = load_fasta_index(str(fai_output_path))
        
        # Validate FAI entries
        sequence_names = list(fai_store.keys())
        assert len(sequence_names) > 0, "No sequences found in FAI index"
        
        # Should have multiple sequences (ARF5 has multiple orthologs)
        assert len(sequence_names) > 10, f"Expected >10 sequences, got {len(sequence_names)}"
        
        # Test specific sequences we know should be there
        expected_sequences = ["REFERENCE"]  # First sequence in ARF5.fasta
        for seq_name in expected_sequences:
            assert seq_name in fai_store, f"Expected sequence '{seq_name}' not found in FAI"
        
        # Validate FAI entry structure
        for seq_name, fai_entry in fai_store.items():
            assert isinstance(fai_entry, FaiEntry)
            assert isinstance(fai_entry.name, str)
            assert isinstance(fai_entry.length, int)
            assert isinstance(fai_entry.offset, int)
            assert isinstance(fai_entry.line_bases, int)
            assert isinstance(fai_entry.line_bytes, int)
            
            # Sanity checks on values
            assert fai_entry.length > 0, f"Invalid length for {seq_name}: {fai_entry.length}"
            assert fai_entry.offset >= 0, f"Invalid offset for {seq_name}: {fai_entry.offset}"
            assert fai_entry.line_bases > 0, f"Invalid line_bases for {seq_name}: {fai_entry.line_bases}"
            assert fai_entry.line_bytes >= fai_entry.line_bases, \
                f"line_bytes should be >= line_bases for {seq_name}"
            
            # For ARF5, sequences should be reasonable length (not tiny, not huge)
            assert 500 < fai_entry.length < 5000, \
                f"Unexpected sequence length for {seq_name}: {fai_entry.length}"
    
    def test_fai_file_format(self, fai_output_path):
        """Test that the FAI file follows the correct format."""
        # Ensure FAI file exists
        if not fai_output_path.exists():
            arf5_fasta = Path("test_data/fasta/ARF5.fasta")
            create_fasta_index(str(arf5_fasta), str(fai_output_path))
        
        # Read raw FAI file and validate format
        with open(fai_output_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) > 0, "FAI file has no content"
        
        # Check each line follows FAI format: NAME\tLENGTH\tOFFSET\tLINE_BASES\tLINE_BYTES
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            parts = line.split('\t')
            assert len(parts) == 5, \
                f"Line {i+1} should have 5 tab-separated fields, got {len(parts)}: {line}"
            
            name, length, offset, line_bases, line_bytes = parts
            
            # Validate field types
            assert isinstance(name, str) and len(name) > 0, \
                f"Invalid sequence name on line {i+1}: '{name}'"
            
            try:
                length_int = int(length)
                offset_int = int(offset)
                line_bases_int = int(line_bases)
                line_bytes_int = int(line_bytes)
            except ValueError as e:
                pytest.fail(f"Non-integer values on line {i+1}: {e}")
            
            # Validate field values
            assert length_int > 0, f"Invalid length on line {i+1}: {length_int}"
            assert offset_int >= 0, f"Invalid offset on line {i+1}: {offset_int}"
            assert line_bases_int > 0, f"Invalid line_bases on line {i+1}: {line_bases_int}"
            assert line_bytes_int >= line_bases_int, \
                f"line_bytes < line_bases on line {i+1}: {line_bytes_int} < {line_bases_int}"
    
    def test_fai_reload_consistency(self, arf5_fasta_file, fai_output_path):
        """Test that saving and reloading FAI gives consistent results."""
        # Generate original FAI
        original_fai = create_fasta_index(str(arf5_fasta_file), str(fai_output_path))
        
        # Reload FAI from file
        reloaded_fai = load_fasta_index(str(fai_output_path))
        
        # Compare original and reloaded
        assert len(original_fai) == len(reloaded_fai), \
            "Reloaded FAI has different number of entries"
        
        assert set(original_fai.keys()) == set(reloaded_fai.keys()), \
            "Reloaded FAI has different sequence names"
        
        # Compare each entry
        for seq_name in original_fai.keys():
            orig_entry = original_fai[seq_name]
            reload_entry = reloaded_fai[seq_name]
            
            assert orig_entry.name == reload_entry.name
            assert orig_entry.length == reload_entry.length
            assert orig_entry.offset == reload_entry.offset
            assert orig_entry.line_bases == reload_entry.line_bases
            assert orig_entry.line_bytes == reload_entry.line_bytes
    
    def test_fai_performance_and_size(self, arf5_fasta_file, fai_output_path):
        """Test FAI generation performance and output size."""
        import time
        
        # Clean up existing FAI
        if fai_output_path.exists():
            fai_output_path.unlink()
        
        # Time the FAI generation
        start_time = time.time()
        fai_store = create_fasta_index(str(arf5_fasta_file), str(fai_output_path))
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        # Should be reasonably fast (under 1 second for 401KB file)
        assert generation_time < 2.0, \
            f"FAI generation took too long: {generation_time:.2f}s"
        
        # Check FAI file size is reasonable
        fai_size = fai_output_path.stat().st_size
        fasta_size = arf5_fasta_file.stat().st_size
        
        # FAI should be much smaller than FASTA (typically < 5% of FASTA size for many sequences)
        size_ratio = fai_size / fasta_size
        assert size_ratio < 0.05, \
            f"FAI file too large relative to FASTA: {size_ratio:.3f} ({fai_size} / {fasta_size})"
        
        # FAI should have reasonable absolute size (a few KB for this file)
        assert 1000 < fai_size < 50000, \
            f"FAI file size unexpected: {fai_size} bytes"
    
    def test_sequence_name_extraction(self, arf5_fasta_file, fai_output_path):
        """Test that sequence names are correctly extracted from FASTA headers."""
        # Generate FAI
        if not fai_output_path.exists():
            fai_store = create_fasta_index(str(arf5_fasta_file), str(fai_output_path))
        else:
            fai_store = load_fasta_index(str(fai_output_path))
        
        sequence_names = list(fai_store.keys())
        
        # Check that we have the expected reference sequence
        assert "REFERENCE" in sequence_names, "REFERENCE sequence not found"
        
        # Check for species-specific sequences (based on ARF5.fasta content)
        species_patterns = ["vs_", "ENST"]
        species_seqs = [name for name in sequence_names 
                       if any(pattern in name for pattern in species_patterns)]
        
        assert len(species_seqs) > 0, \
            f"No species-specific sequences found. All names: {sequence_names[:10]}"
        
        # Sequence names should not contain spaces or tabs (proper FASTA parsing)
        for name in sequence_names:
            assert '\t' not in name, f"Sequence name contains tab: '{name}'"
            assert '\n' not in name, f"Sequence name contains newline: '{name}'"


@pytest.mark.io
class TestFAIErrorHandling:
    """Test FAI generation error handling."""
    
    @pytest.fixture
    def arf5_fasta_file(self):
        """Path to ARF5 FASTA test file."""
        return Path("test_data/fasta/ARF5.fasta")
    
    def test_nonexistent_fasta_file(self):
        """Test FAI generation with nonexistent FASTA file."""
        with pytest.raises(FileNotFoundError):
            create_fasta_index("nonexistent.fasta")
    
    def test_invalid_output_directory(self, arf5_fasta_file):
        """Test FAI generation with invalid output directory."""
        invalid_output = Path("/nonexistent_directory/test.fai")
        
        # This should either create the directory or fail gracefully
        with pytest.raises((FileNotFoundError, PermissionError, OSError)):
            create_fasta_index(str(arf5_fasta_file), str(invalid_output))
    
    def test_empty_fasta_file(self, tmp_path):
        """Test FAI generation with empty FASTA file."""
        empty_fasta = tmp_path / "empty.fasta"
        empty_fasta.write_text("")
        
        fai_output = tmp_path / "empty.fasta.fai"
        
        # Should handle empty file gracefully
        fai_store = create_fasta_index(str(empty_fasta), str(fai_output))
        assert len(fai_store) == 0
        assert fai_output.exists()


@pytest.mark.io
class TestFAICleanup:
    """Test FAI file cleanup and management."""
    
    @pytest.fixture
    def arf5_fasta_file(self):
        """Path to ARF5 FASTA test file."""
        return Path("test_data/fasta/ARF5.fasta")
    
    @pytest.fixture
    def cleanup_fai_files(self):
        """Fixture to clean up FAI files after tests."""
        files_to_cleanup = []
        
        def register_file(filepath):
            files_to_cleanup.append(Path(filepath))
        
        yield register_file
        
        # Cleanup after test
        for filepath in files_to_cleanup:
            if filepath.exists():
                filepath.unlink()
    
    def test_fai_overwrite_behavior(self, arf5_fasta_file, cleanup_fai_files):
        """Test that FAI files are properly overwritten."""
        output_dir = Path("test_outputs")
        output_dir.mkdir(exist_ok=True, parents=True)
        fai_path = output_dir / "ARF5_overwrite_test.fasta.fai"
        cleanup_fai_files(fai_path)
        
        # Create initial FAI
        original_fai = create_fasta_index(str(arf5_fasta_file), str(fai_path))
        assert fai_path.exists()
        original_size = fai_path.stat().st_size
        original_mtime = fai_path.stat().st_mtime
        
        # Wait a moment to ensure different modification time
        import time
        time.sleep(0.1)
        
        # Create FAI again (should overwrite)
        new_fai = create_fasta_index(str(arf5_fasta_file), str(fai_path))
        
        # File should still exist with same content but potentially different mtime
        assert fai_path.exists()
        new_size = fai_path.stat().st_size
        
        # Size should be the same (same FASTA file)
        assert new_size == original_size, \
            f"FAI file size changed after overwrite: {original_size} -> {new_size}"
        
        # Content should be identical
        assert len(original_fai) == len(new_fai)
        assert set(original_fai.keys()) == set(new_fai.keys())
    
    def test_concurrent_fai_access(self, arf5_fasta_file):
        """Test accessing FAI file while it exists."""
        output_dir = Path("test_outputs")
        output_dir.mkdir(exist_ok=True, parents=True)
        fai_path = output_dir / "ARF5_concurrent.fasta.fai"
        
        try:
            # Create FAI
            fai_store = create_fasta_index(str(arf5_fasta_file), str(fai_path))
            
            # Should be able to read it immediately
            loaded_fai = load_fasta_index(str(fai_path))
            
            assert len(fai_store) == len(loaded_fai)
            assert set(fai_store.keys()) == set(loaded_fai.keys())
            
        finally:
            # Clean up
            if fai_path.exists():
                fai_path.unlink()
    
    def test_fai_deletion_and_regeneration(self, arf5_fasta_file):
        """Test deleting and regenerating FAI file."""
        output_dir = Path("test_outputs")
        output_dir.mkdir(exist_ok=True, parents=True)
        fai_path = output_dir / "ARF5_delete_regen.fasta.fai"
        
        try:
            # Create initial FAI
            original_fai = create_fasta_index(str(arf5_fasta_file), str(fai_path))
            assert fai_path.exists()
            
            # Delete FAI file
            fai_path.unlink()
            assert not fai_path.exists()
            
            # Regenerate FAI
            new_fai = create_fasta_index(str(arf5_fasta_file), str(fai_path))
            assert fai_path.exists()
            
            # Should have identical content
            assert len(original_fai) == len(new_fai)
            assert set(original_fai.keys()) == set(new_fai.keys())
            
            for seq_name in original_fai.keys():
                orig_entry = original_fai[seq_name]
                new_entry = new_fai[seq_name]
                assert orig_entry.length == new_entry.length
                assert orig_entry.offset == new_entry.offset
                
        finally:
            # Clean up
            if fai_path.exists():
                fai_path.unlink()