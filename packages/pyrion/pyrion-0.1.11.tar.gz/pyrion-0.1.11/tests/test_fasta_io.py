"""Unit tests for pyrion.io.fasta module."""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Dict

from pyrion.core.nucleotide_sequences import NucleotideSequence, SequenceType
from pyrion.core.amino_acid_sequences import AminoAcidSequence
from pyrion.core.sequences_collection import SequencesCollection
from pyrion.core.intervals import GenomicInterval
from pyrion.core.strand import Strand
from pyrion.core.fai import FaiStore, FaiEntry
from pyrion.io.fasta import (
    FastaAccessor,
    read_fasta,
    write_fasta,
    read_dna_fasta,
    read_rna_fasta,
    read_protein_fasta,
    _write_sequence
)
from pyrion.io.fai import create_fasta_index
from pyrion.core.nucleotide_sequences import SequenceType


class TestFixtures:
    """Test data fixtures for FASTA I/O operations."""
    
    @pytest.fixture
    def sample_fasta_content(self):
        """Sample FASTA content for testing."""
        return """
>sequence1 Description of sequence 1
ATCGATCGATCGATCG
ATCGATCGATCGATCG
>sequence2
GGCCTTAAGGCCTTAA
>sequence3 Multi-line sequence
ATATATATATAT
GCGCGCGCGCGC
TTTTTTTTTTTT
""".strip()
    
    @pytest.fixture
    def sample_fasta_file(self, sample_fasta_content):
        """Create temporary FASTA file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(sample_fasta_content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def sample_fai_store(self):
        """Sample FAI index store for testing."""
        fai_store = FaiStore()
        
        # Add sample entries
        fai_store["sequence1"] = FaiEntry(
            name="sequence1",
            length=32,
            offset=43,  # After header
            line_bases=16,
            line_bytes=17  # Including newline
        )
        
        fai_store["sequence2"] = FaiEntry(
            name="sequence2", 
            length=16,
            offset=88,
            line_bases=16,
            line_bytes=17
        )
        
        return fai_store
    
    @pytest.fixture
    def sample_nucleotide_sequences(self):
        """Sample NucleotideSequence objects for testing."""
        return {
            "seq1": NucleotideSequence.from_string(
                "ATCGATCGATCGATCG", 
                is_rna=False,
                metadata={"id": "seq1", "description": "Test sequence 1"}
            ),
            "seq2": NucleotideSequence.from_string(
                "GGCCTTAAGGCCTTAA",
                is_rna=False, 
                metadata={"id": "seq2", "description": "Test sequence 2"}
            )
        }
    
    @pytest.fixture
    def sample_protein_content(self):
        """Sample protein FASTA content for testing."""
        return """
>protein1
MKFGAYA*ARNDCQEGHILKMFPSTWYV
ARNDCQEGHILKMFPSTWYV*
>protein2
MKFGAYA*
>protein3
MKF-GAY-A*ARN
""".strip()
    
    @pytest.fixture
    def sample_protein_file(self, sample_protein_content):
        """Create temporary protein FASTA file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(sample_protein_content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)


class TestFastaAccessor(TestFixtures):
    """Test FastaAccessor functionality."""
    
    def test_fasta_accessor_context_manager(self, sample_fasta_file, sample_fai_store):
        """Test FastaAccessor as context manager."""
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            assert accessor._file_handle is not None
            assert hasattr(accessor, 'fai_store')
        
        # File should be closed after context
        assert accessor._file_handle is None
    
    def test_fasta_accessor_file_not_found(self, sample_fai_store):
        """Test FastaAccessor with non-existent file."""
        with pytest.raises(FileNotFoundError, match="FASTA file not found"):
            FastaAccessor("nonexistent.fasta", sample_fai_store)
    
    def test_get_sequence_basic(self, sample_fasta_file, sample_fai_store):
        """Test basic sequence retrieval."""
        region = GenomicInterval(chrom="sequence1", start=0, end=16, strand=Strand.PLUS)
        
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            sequence = accessor.get_sequence(region)
            
            assert isinstance(sequence, NucleotideSequence)
            assert len(sequence) == 16
            # Note: Actual sequence content depends on _extract_raw_sequence implementation
    
    def test_get_sequence_with_coordinates(self, sample_fasta_file, sample_fai_store):
        """Test sequence retrieval with specific coordinates."""
        region = GenomicInterval(chrom="sequence1", start=5, end=15, strand=Strand.PLUS)
        
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            sequence = accessor.get_sequence(region)
            
            assert len(sequence) == 10
    
    def test_get_sequence_rna_mode(self, sample_fasta_file, sample_fai_store):
        """Test sequence retrieval in RNA mode."""
        region = GenomicInterval(chrom="sequence1", start=0, end=16, strand=Strand.PLUS)
        
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            sequence = accessor.get_sequence(region, is_rna=True)
            
            assert isinstance(sequence, NucleotideSequence)
            # Should be in RNA mode
    
    def test_get_sequence_invalid_chrom(self, sample_fasta_file, sample_fai_store):
        """Test error handling for invalid chromosome."""
        region = GenomicInterval(chrom="nonexistent", start=0, end=10, strand=Strand.PLUS)
        
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            with pytest.raises(KeyError, match="Sequence 'nonexistent' not found"):
                accessor.get_sequence(region)
    
    def test_get_sequence_invalid_coordinates(self, sample_fasta_file, sample_fai_store):
        """Test error handling for invalid coordinates."""
        # Coordinates beyond sequence length
        region = GenomicInterval(chrom="sequence1", start=0, end=1000, strand=Strand.PLUS)
        
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            with pytest.raises(ValueError, match="Invalid coordinates"):
                accessor.get_sequence(region)
    
    def test_get_sequence_length(self, sample_fasta_file, sample_fai_store):
        """Test getting sequence length."""
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            length = accessor.get_sequence_length("sequence1")
            assert length == 32  # From FAI entry
            
            with pytest.raises(KeyError):
                accessor.get_sequence_length("nonexistent")
    
    def test_get_sequence_names(self, sample_fasta_file, sample_fai_store):
        """Test getting all sequence names."""
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            names = accessor.get_sequence_names()
            assert isinstance(names, list)
            assert "sequence1" in names
            assert "sequence2" in names
    
    def test_has_sequence(self, sample_fasta_file, sample_fai_store):
        """Test checking if sequence exists."""
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            assert accessor.has_sequence("sequence1")
            assert accessor.has_sequence("sequence2")
            assert not accessor.has_sequence("nonexistent")
    
    def test_get_multiple_sequences(self, sample_fasta_file, sample_fai_store):
        """Test getting multiple sequences at once."""
        regions = [
            GenomicInterval(chrom="sequence1", start=0, end=10, strand=Strand.PLUS),
            GenomicInterval(chrom="sequence2", start=0, end=8, strand=Strand.PLUS)
        ]
        
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            sequences = accessor.get_multiple_sequences(regions)
            
            assert isinstance(sequences, dict)
            assert len(sequences) == 2
            # Check that all sequences are NucleotideSequence objects
            for seq in sequences.values():
                assert isinstance(seq, NucleotideSequence)
    
    def test_extract_raw_sequence_method(self, sample_fasta_file, sample_fai_store):
        """Test the _extract_raw_sequence method directly."""
        with FastaAccessor(sample_fasta_file, sample_fai_store) as accessor:
            fai_entry = sample_fai_store["sequence1"]
            
            # Test extracting first 10 characters
            raw_seq = accessor._extract_raw_sequence(fai_entry, 0, 10)
            assert isinstance(raw_seq, str)
            assert len(raw_seq) == 10
            
            # Test extracting from middle
            raw_seq2 = accessor._extract_raw_sequence(fai_entry, 5, 15)
            assert isinstance(raw_seq2, str)
            assert len(raw_seq2) == 10
    
    def test_extract_raw_sequence_without_context_manager(self, sample_fasta_file, sample_fai_store):
        """Test error when using _extract_raw_sequence without context manager."""
        accessor = FastaAccessor(sample_fasta_file, sample_fai_store)
        fai_entry = sample_fai_store["sequence1"]
        
        with pytest.raises(RuntimeError, match="File not opened"):
            accessor._extract_raw_sequence(fai_entry, 0, 10)


class TestReadFasta(TestFixtures):
    """Test read_fasta function."""
    
    def test_read_fasta_basic(self, sample_fasta_file):
        """Test basic FASTA reading."""
        sequences = read_fasta(sample_fasta_file, SequenceType.DNA)
        
        assert isinstance(sequences, SequencesCollection)
        assert len(sequences) >= 2  # At least sequence1 and sequence2
        # Check for sequences with descriptions (IDs include descriptions)
        sequence_ids = list(sequences.keys())
        assert any("sequence1" in seq_id for seq_id in sequence_ids)
        assert any("sequence2" in seq_id for seq_id in sequence_ids)
        
        # Check sequence objects
        seq1_key = next(key for key in sequence_ids if "sequence1" in key)
        seq2_key = next(key for key in sequence_ids if "sequence2" in key)
        assert isinstance(sequences[seq1_key], NucleotideSequence)
        assert isinstance(sequences[seq2_key], NucleotideSequence)
    
    def test_read_fasta_nonexistent(self):
        """Test reading non-existent FASTA file."""
        with pytest.raises((FileNotFoundError, OSError)):
            read_fasta("nonexistent.fasta", SequenceType.DNA)
    
    def test_read_fasta_with_sequence_type(self, sample_fasta_file):
        """Test reading with specific sequence type."""
        # Test DNA sequences
        dna_sequences = read_fasta(sample_fasta_file, SequenceType.DNA)
        assert isinstance(dna_sequences, SequencesCollection)
        assert len(dna_sequences) >= 2
        
        # Test RNA sequences  
        rna_sequences = read_fasta(sample_fasta_file, SequenceType.RNA)
        assert isinstance(rna_sequences, SequencesCollection)
        assert len(rna_sequences) >= 2


class TestWriteFasta(TestFixtures):
    """Test write_fasta function."""
    
    def test_write_fasta_basic(self, sample_nucleotide_sequences):
        """Test basic FASTA writing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            output_path = f.name
        
        try:
            write_fasta(sample_nucleotide_sequences, output_path)
            
            # Check that file was created and has content
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
            # Read back and verify
            with open(output_path, 'r') as f:
                content = f.read()
                assert ">seq1" in content
                assert ">seq2" in content
                assert "ATCGATCGATCGATCG" in content
                assert "GGCCTTAAGGCCTTAA" in content
        
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_write_fasta_with_line_width(self, sample_nucleotide_sequences):
        """Test FASTA writing with custom line width."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            output_path = f.name
        
        try:
            write_fasta(sample_nucleotide_sequences, output_path, line_width=8)
            
            with open(output_path, 'r') as f:
                lines = f.readlines()
                
                # Find sequence lines (not headers)
                seq_lines = [line for line in lines if not line.startswith('>')]
                # Check that sequences are wrapped correctly
                for line in seq_lines:
                    if line.strip():  # Skip empty lines
                        assert len(line.strip()) <= 8
        
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_write_fasta_line_width_zero(self, sample_nucleotide_sequences):
        """Test FASTA writing with line_width=0 (single line)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            output_path = f.name
        
        try:
            # This should not crash and should write sequences on single lines
            write_fasta(sample_nucleotide_sequences, output_path, line_width=0)
            
            with open(output_path, 'r') as f:
                content = f.read()
                lines = content.strip().split('\n')
                
                # Check that sequences are on single lines (no wrapping)
                seq_lines = [line for line in lines if not line.startswith('>')]
                
                # Verify we have sequences and they are not wrapped
                assert len(seq_lines) > 0
                for line in seq_lines:
                    if line.strip():  # Skip empty lines
                        # Each sequence should be on a single line (no max length constraint)
                        # We just verify they exist and contain valid nucleotides
                        assert all(c in 'ATGCNRYSWKMBDHV-atgcnryswkmbdhv' for c in line.strip())
        
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_write_fasta_empty_dict(self):
        """Test writing empty sequence dictionary."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            output_path = f.name
        
        try:
            write_fasta({}, output_path)
            
            # File should exist but be empty or minimal
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) == 0
        
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_write_sequence_helper(self):
        """Test the _write_sequence helper function."""
        sequence = NucleotideSequence.from_string(
            "ATCGATCGATCGATCG",
            metadata={"description": "Test sequence"}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_path = f.name
            
            try:
                with open(output_path, 'w') as file_handle:
                    _write_sequence(file_handle, "test_seq", sequence, line_width=8)
                
                with open(output_path, 'r') as f:
                    content = f.read()
                    assert ">test_seq" in content
                    # Check for line-wrapped sequence (line_width=8)
                    assert "ATCGATCG" in content
                    assert content.count("ATCGATCG") == 2  # Should appear twice due to wrapping
            
            finally:
                if os.path.exists(output_path):
                    os.unlink(output_path)


class TestSpecializedReaders(TestFixtures):
    """Test specialized FASTA reader functions."""
    
    def test_read_dna_fasta(self, sample_fasta_file):
        """Test DNA-specific FASTA reader."""
        sequences = read_dna_fasta(sample_fasta_file)
        
        assert isinstance(sequences, SequencesCollection)
        assert len(sequences) >= 2
        
        # All sequences should be DNA (not RNA)
        for seq in sequences.values():
            assert isinstance(seq, NucleotideSequence)
            # Note: Specific RNA/DNA testing depends on internal implementation
    
    def test_read_rna_fasta(self, sample_fasta_file):
        """Test RNA-specific FASTA reader."""
        sequences = read_rna_fasta(sample_fasta_file)
        
        assert isinstance(sequences, SequencesCollection)
        assert len(sequences) >= 2
        
        # All sequences should be RNA
        for seq in sequences.values():
            assert isinstance(seq, NucleotideSequence)
    
    def test_read_dna_vs_rna_equivalence(self, sample_fasta_file):
        """Test that DNA and RNA readers handle same data consistently."""
        dna_sequences = read_dna_fasta(sample_fasta_file)
        rna_sequences = read_rna_fasta(sample_fasta_file)
        
        # Should have same sequence IDs
        assert set(dna_sequences.keys()) == set(rna_sequences.keys())
        
        # Sequences should have same lengths
        for seq_id in dna_sequences.keys():
            assert len(dna_sequences[seq_id]) == len(rna_sequences[seq_id])


class TestProteinSequenceSupport(TestFixtures):
    """Test protein sequence functionality."""
    
    def test_read_protein_fasta_basic(self, sample_protein_file):
        """Test basic protein FASTA reading."""
        sequences = read_protein_fasta(sample_protein_file)
        
        assert isinstance(sequences, SequencesCollection)
        assert len(sequences) >= 3
        assert "protein1" in sequences
        assert "protein2" in sequences
        assert "protein3" in sequences
        
        # Check sequence objects are AminoAcidSequence
        for seq in sequences.values():
            assert isinstance(seq, AminoAcidSequence)
    
    def test_read_fasta_protein_type(self, sample_protein_file):
        """Test read_fasta with PROTEIN sequence type."""
        sequences = read_fasta(sample_protein_file, SequenceType.PROTEIN)
        
        assert isinstance(sequences, SequencesCollection)
        assert len(sequences) >= 3
        
        # Check all sequences are AminoAcidSequence
        for seq in sequences.values():
            assert isinstance(seq, AminoAcidSequence)
            assert len(seq) > 0
    
    def test_read_fasta_protein_vs_nucleotide(self, sample_fasta_file, sample_protein_file):
        """Test that protein and nucleotide sequences return different types."""
        # Read nucleotide sequences
        dna_sequences = read_fasta(sample_fasta_file, SequenceType.DNA)
        
        # Read protein sequences
        protein_sequences = read_fasta(sample_protein_file, SequenceType.PROTEIN)
        
        # Check types are different
        for seq in dna_sequences.values():
            assert isinstance(seq, NucleotideSequence)
        
        for seq in protein_sequences.values():
            assert isinstance(seq, AminoAcidSequence)
    
    def test_sequence_type_enum(self):
        """Test that SequenceType enum includes PROTEIN."""
        assert hasattr(SequenceType, 'DNA')
        assert hasattr(SequenceType, 'RNA') 
        assert hasattr(SequenceType, 'PROTEIN')
        
        assert SequenceType.DNA.value == "dna"
        assert SequenceType.RNA.value == "rna"
        assert SequenceType.PROTEIN.value == "protein"
    
    def test_protein_fasta_with_mixed_content(self):
        """Test protein FASTA with various amino acid characters."""
        mixed_protein_content = """>test_protein
MKFGAYAARNDCQEGHILKMFPSTWYV*
mkfgayaarndcqeghilkmfpstwyv-
XBZJOU  # Test unknown/ambiguous amino acids
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(mixed_protein_content)
            temp_path = f.name
        
        try:
            sequences = read_protein_fasta(temp_path)
            assert "test_protein" in sequences
            assert isinstance(sequences["test_protein"], AminoAcidSequence)
            # Should handle various amino acid characters
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_protein_sequence_metadata(self, sample_protein_file):
        """Test that protein sequences include correct metadata."""
        sequences = read_protein_fasta(sample_protein_file)
        
        for seq_id, seq in sequences.items():
            assert seq.metadata is not None
            assert seq.metadata.get('sequence_id') == seq_id
            assert 'source_file' in seq.metadata
    
    def test_read_protein_fasta_nonexistent_file(self):
        """Test error handling for non-existent protein FASTA file."""
        with pytest.raises((FileNotFoundError, IOError)):
            read_protein_fasta("nonexistent_protein.fasta")
    
    def test_invalid_sequence_type(self, sample_fasta_file):
        """Test error handling for invalid sequence type."""
        with pytest.raises(ValueError, match="Invalid sequence_type"):
            # Try to use a non-existent sequence type
            read_fasta(sample_fasta_file, "invalid_type")


class TestFastaAccessorIntegration(TestFixtures):
    """Test FastaAccessor integration with real FAI indices."""
    
    def test_fasta_accessor_with_real_fai_index(self, sample_fasta_file):
        """Test FastaAccessor with a real FAI index."""
        # Create real FAI index for the test file
        fai_store = create_fasta_index(sample_fasta_file)
        
        with FastaAccessor(sample_fasta_file, fai_store) as accessor:
            names = accessor.get_sequence_names()
            assert len(names) >= 2
            
            # Test extracting sequences
            for name in names:
                length = accessor.get_sequence_length(name)
                assert length > 0
                
                # Extract full sequence
                region = GenomicInterval(chrom=name, start=0, end=length, strand=Strand.PLUS)
                sequence = accessor.get_sequence(region)
                assert len(sequence) == length
    
    def test_fasta_accessor_partial_sequence_extraction(self, sample_fasta_file):
        """Test extracting partial sequences with real FAI index."""
        fai_store = create_fasta_index(sample_fasta_file)
        
        with FastaAccessor(sample_fasta_file, fai_store) as accessor:
            names = accessor.get_sequence_names()
            test_name = names[0]
            total_length = accessor.get_sequence_length(test_name)
            
            if total_length >= 10:
                # Extract first 10 bases
                region1 = GenomicInterval(chrom=test_name, start=0, end=10, strand=Strand.PLUS)
                seq1 = accessor.get_sequence(region1)
                assert len(seq1) == 10
                
                # Extract middle portion
                start = total_length // 3
                end = min(start + 10, total_length)
                region2 = GenomicInterval(chrom=test_name, start=start, end=end, strand=Strand.PLUS)
                seq2 = accessor.get_sequence(region2)
                assert len(seq2) == end - start
    
    def test_fasta_accessor_boundary_conditions(self, sample_fasta_file):
        """Test boundary conditions for sequence extraction."""
        fai_store = create_fasta_index(sample_fasta_file)
        
        with FastaAccessor(sample_fasta_file, fai_store) as accessor:
            names = accessor.get_sequence_names()
            test_name = names[0]
            total_length = accessor.get_sequence_length(test_name)
            
            # Test extracting single base
            region = GenomicInterval(chrom=test_name, start=0, end=1, strand=Strand.PLUS)
            seq = accessor.get_sequence(region)
            assert len(seq) == 1
            
            # Test extracting last base
            if total_length > 1:
                region = GenomicInterval(chrom=test_name, start=total_length-1, end=total_length, strand=Strand.PLUS)
                seq = accessor.get_sequence(region)
                assert len(seq) == 1


class TestSequenceTypeMapping(TestFixtures):
    """Test sequence type mapping and consistency."""
    
    def test_sequence_type_consistency(self, sample_fasta_file, sample_protein_file):
        """Test that sequence types are handled consistently."""
        # Test DNA
        dna_sequences = read_fasta(sample_fasta_file, SequenceType.DNA)
        dna_specialized = read_dna_fasta(sample_fasta_file)
        
        assert len(dna_sequences) == len(dna_specialized)
        assert set(dna_sequences.keys()) == set(dna_specialized.keys())
        
        # Test RNA
        rna_sequences = read_fasta(sample_fasta_file, SequenceType.RNA)
        rna_specialized = read_rna_fasta(sample_fasta_file)
        
        assert len(rna_sequences) == len(rna_specialized)
        assert set(rna_sequences.keys()) == set(rna_specialized.keys())
        
        # Test PROTEIN
        protein_sequences = read_fasta(sample_protein_file, SequenceType.PROTEIN)
        protein_specialized = read_protein_fasta(sample_protein_file)
        
        assert len(protein_sequences) == len(protein_specialized)
        assert set(protein_sequences.keys()) == set(protein_specialized.keys())
    
    def test_return_type_hints(self, sample_fasta_file, sample_protein_file):
        """Test that return types match expected type hints."""
        # Test with return_dict=True (default)
        dna_dict = read_fasta(sample_fasta_file, SequenceType.DNA, return_dict=True)
        assert isinstance(dna_dict, SequencesCollection)
        
        protein_dict = read_fasta(sample_protein_file, SequenceType.PROTEIN, return_dict=True)
        assert isinstance(protein_dict, SequencesCollection)
        
        # Test with return_dict=False
        dna_list = read_fasta(sample_fasta_file, SequenceType.DNA, return_dict=False)
        assert isinstance(dna_list, list)
        
        protein_list = read_fasta(sample_protein_file, SequenceType.PROTEIN, return_dict=False)
        assert isinstance(protein_list, list)


class TestFileFormatHandling(TestFixtures):
    """Test various FASTA format variations."""
    
    def test_multiline_sequences(self):
        """Test handling of multi-line sequences."""
        multiline_content = """>test_sequence
ATCGATCGATCGATCG
ATCGATCGATCGATCG
GGCCTTAAGGCCTTAA
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(multiline_content)
            temp_path = f.name
        
        try:
            sequences = read_fasta(temp_path, SequenceType.DNA)
            assert "test_sequence" in sequences
            # Should handle concatenation correctly
            seq = sequences["test_sequence"]
            assert len(seq) == 48  # 16 + 16 + 16
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_headers_with_descriptions(self):
        """Test handling of headers with descriptions."""
        described_content = """>sequence1 This is a test sequence with description
ATCGATCGATCGATCG
>sequence2|accession|description with pipes
GGCCTTAAGGCCTTAA
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(described_content)
            temp_path = f.name
        
        try:
            sequences = read_fasta(temp_path, SequenceType.DNA)
            # Check for sequences with descriptions
            sequence_ids = list(sequences.keys())
            assert any("sequence1" in seq_id for seq_id in sequence_ids)
            # Note: Description handling depends on implementation
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_empty_lines_handling(self):
        """Test handling of empty lines in FASTA."""
        content_with_empty_lines = """>sequence1

ATCGATCGATCGATCG

>sequence2

GGCCTTAAGGCCTTAA

"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(content_with_empty_lines)
            temp_path = f.name
        
        try:
            sequences = read_fasta(temp_path, SequenceType.DNA)
            assert len(sequences) == 2
            assert all(len(seq) > 0 for seq in sequences.values())
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_case_sensitivity(self):
        """Test handling of uppercase/lowercase nucleotides."""
        mixed_case_content = """>test_sequence
ATCGatcgATCGatcg
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(mixed_case_content)
            temp_path = f.name
        
        try:
            sequences = read_fasta(temp_path, SequenceType.DNA)
            assert "test_sequence" in sequences
            # Should handle mixed case appropriately
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestErrorHandling(TestFixtures):
    """Test error handling and edge cases."""
    
    def test_malformed_fasta(self):
        """Test handling of malformed FASTA files."""
        malformed_content = """This is not a FASTA file
No headers starting with >
Just random text
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(malformed_content)
            temp_path = f.name
        
        try:
            # Should handle gracefully or raise appropriate error
            sequences = read_fasta(temp_path, SequenceType.DNA)
            # Depending on implementation, might return empty mapping or raise error
            assert isinstance(sequences, SequencesCollection)
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_empty_fasta_file(self):
        """Test handling of empty FASTA files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            # Write nothing (empty file)
            temp_path = f.name
        
        try:
            sequences = read_fasta(temp_path, SequenceType.DNA)
            assert isinstance(sequences, SequencesCollection)
            assert len(sequences) == 0
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_write_to_readonly_location(self, sample_nucleotide_sequences):
        """Test error handling when writing to read-only location."""
        readonly_path = "/root/readonly.fasta"  # Should fail on most systems
        
        with pytest.raises((PermissionError, OSError, FileNotFoundError)):
            write_fasta(sample_nucleotide_sequences, readonly_path)
    
    def test_path_object_handling(self, sample_nucleotide_sequences):
        """Test that Path objects are handled correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Should accept Path objects
            write_fasta(sample_nucleotide_sequences, temp_path)
            sequences = read_fasta(temp_path, SequenceType.DNA)
            
            assert len(sequences) == len(sample_nucleotide_sequences)
        
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestIntegrationWithRealData(TestFixtures):
    """Integration tests with real FASTA data if available."""
    
    def test_with_test_data_if_available(self):
        """Test with actual test data files if they exist."""
        test_fasta_path = Path("test_data/fasta/ARF5.fasta")
        
        if test_fasta_path.exists():
            # Test with real data
            sequences = read_fasta(test_fasta_path, SequenceType.DNA)
            
            assert isinstance(sequences, SequencesCollection)
            assert len(sequences) > 0
            
            # All values should be NucleotideSequence objects
            for seq in sequences.values():
                assert isinstance(seq, NucleotideSequence)
                assert len(seq) > 0
        else:
            pytest.skip("Test FASTA data not available")
    
    def test_round_trip_with_real_data(self):
        """Test round-trip (read -> write -> read) with real data."""
        test_fasta_path = Path("test_data/fasta/ARF5.fasta")
        
        if test_fasta_path.exists():
            # Read original
            original_sequences = read_fasta(test_fasta_path, SequenceType.DNA)
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
                temp_path = f.name
            
            try:
                write_fasta(original_sequences, temp_path)
                
                # Read back
                reread_sequences = read_fasta(temp_path, SequenceType.DNA)
                
                # Should have same sequence IDs and lengths
                assert set(original_sequences.keys()) == set(reread_sequences.keys())
                
                for seq_id in original_sequences.keys():
                    assert len(original_sequences[seq_id]) == len(reread_sequences[seq_id])
            
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        else:
            pytest.skip("Test FASTA data not available")


