"""Unit tests for pyrion.ops serialization modules."""

import pytest
import json
import tempfile
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

from pyrion.core.genome_alignment import GenomeAlignment, GenomeAlignmentsCollection
from pyrion.core.genes import Transcript, TranscriptsCollection
from pyrion.core.strand import Strand

# Chain serialization functions
from pyrion.ops.chain_serialization import (
    genome_alignment_to_chain_string,
    genome_alignments_collection_to_chain_string,
    save_genome_alignments_collection_to_chain,
    genome_alignment_to_dict,
    genome_alignment_from_dict,
    genome_alignments_collection_to_dict,
    genome_alignments_collection_from_dict,
    save_genome_alignments_collection_to_json,
    load_genome_alignments_collection_from_json,
    genome_alignments_collection_summary_string
)

# Transcript serialization functions
from pyrion.ops.transcript_serialization import (
    transcript_to_bed12_string,
    transcripts_collection_to_bed12_string,
    save_transcripts_collection_to_bed12,
    transcript_to_dict,
    transcript_from_dict,
    transcripts_collection_to_dict,
    transcripts_collection_from_dict,
    save_transcripts_collection_to_json,
    load_transcripts_collection_from_json,
    transcripts_collection_summary_string
)


class TestFixtures:
    """Test data fixtures for serialization operations."""
    
    @pytest.fixture
    def simple_genome_alignment(self):
        """Simple genome alignment for testing."""
        return GenomeAlignment(
            chain_id=12345,
            score=15000,
            t_chrom="chr1",
            t_strand=1,
            t_size=248956422,
            q_chrom="chr2",
            q_strand=1,
            q_size=242193529,
            blocks=np.array([
                [1000, 1100, 500, 600],
                [1200, 1300, 700, 800],
                [1500, 1600, 900, 1000]
            ], dtype=np.int32)
        )
    
    @pytest.fixture
    def negative_strand_alignment(self):
        """Alignment with negative query strand."""
        return GenomeAlignment(
            chain_id=67890,
            score=8000,
            t_chrom="chr3",
            t_strand=1,
            t_size=198295559,
            q_chrom="chr4",
            q_strand=-1,
            q_size=190214555,
            blocks=np.array([
                [2000, 2200, 1000, 1200],
                [2400, 2500, 800, 900]
            ], dtype=np.int32)
        )
    
    @pytest.fixture
    def genome_alignments_collection(self, simple_genome_alignment, negative_strand_alignment):
        """Collection of genome alignments."""
        return GenomeAlignmentsCollection(
            alignments=[simple_genome_alignment, negative_strand_alignment],
            source_file="test_chains.chain"
        )
    
    @pytest.fixture
    def coding_transcript(self):
        """Coding transcript for testing."""
        return Transcript(
            blocks=np.array([
                [1000, 1200],   # Exon 1
                [1500, 1700],   # Exon 2
                [2000, 2300]    # Exon 3
            ], dtype=np.int32),
            strand=Strand.PLUS,
            chrom="chr1",
            id="ENST00000123456",
            cds_start=1100,
            cds_end=2200,
            biotype="protein_coding"
        )
    
    @pytest.fixture
    def non_coding_transcript(self):
        """Non-coding transcript for testing."""
        return Transcript(
            blocks=np.array([
                [5000, 5300],
                [5600, 5800]
            ], dtype=np.int32),
            strand=Strand.MINUS,
            chrom="chr2",
            id="ENST00000789012",
            biotype="lncRNA"
        )
    
    @pytest.fixture
    def transcripts_collection(self, coding_transcript, non_coding_transcript):
        """Collection of transcripts."""
        return TranscriptsCollection(
            transcripts=[coding_transcript, non_coding_transcript],
            source_file="test_transcripts.bed12"
        )


class TestChainSerialization(TestFixtures):
    """Test chain format serialization."""
    
    def test_genome_alignment_to_chain_string(self, simple_genome_alignment):
        """Test converting GenomeAlignment to chain format string."""
        chain_string = genome_alignment_to_chain_string(simple_genome_alignment)
        
        lines = chain_string.split('\n')  # Don't strip to preserve empty line
        
        # Check header line
        header = lines[0]
        assert header.startswith("chain 15000 chr1 248956422 + 1000 1600 chr2 242193529 + 500 1000 12345")
        
        # Check block lines (should have 3 blocks, so 2 with gaps + 1 final)
        assert len(lines) == 5  # header + 2 gap lines + 1 final block + empty line
        
        # First block: size=100, gap to next = (1200-1100)=100 target, (700-600)=100 query
        assert "100\t100\t100" in lines[1]
        
        # Second block: size=100, gap to next = (1500-1300)=200 target, (900-800)=100 query  
        assert "100\t200\t100" in lines[2]
        
        # Final block: size=100
        assert lines[3] == "100"
        
        # Empty line at end
        assert lines[4] == ""
    
    def test_genome_alignment_to_chain_string_negative_strand(self, negative_strand_alignment):
        """Test chain string generation for negative strand alignment."""
        chain_string = genome_alignment_to_chain_string(negative_strand_alignment)
        
        lines = chain_string.strip().split('\n')
        header = lines[0]
        
        # Should have negative strand indicator
        assert "chr4 190214555 -" in header
        
        # Should have proper coordinates for negative strand
        assert "chr3 198295559 + 2000 2500" in header
    
    def test_genome_alignments_collection_to_chain_string(self, genome_alignments_collection):
        """Test converting collection to chain format."""
        chain_string = genome_alignments_collection_to_chain_string(genome_alignments_collection)
        
        # Should contain both alignments
        assert "chain 15000" in chain_string  # First alignment
        assert "chain 8000" in chain_string   # Second alignment
        
        # Should have proper separation between chains
        lines = chain_string.strip().split('\n')
        assert len([line for line in lines if line.startswith("chain")]) == 2
    
    def test_save_and_load_chain_file(self, genome_alignments_collection):
        """Test saving and loading chain files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.chain', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Save collection to file
            save_genome_alignments_collection_to_chain(genome_alignments_collection, tmp_path)
            
            # Verify file was created and has content
            assert tmp_path.exists()
            content = tmp_path.read_text()
            assert "chain 15000" in content
            assert "chain 8000" in content
            
        finally:
            tmp_path.unlink()


class TestChainJSONSerialization(TestFixtures):
    """Test JSON serialization for genome alignments."""
    
    def test_genome_alignment_to_dict(self, simple_genome_alignment):
        """Test converting GenomeAlignment to dictionary."""
        data = genome_alignment_to_dict(simple_genome_alignment)
        
        assert data['chain_id'] == 12345
        assert data['score'] == 15000
        assert data['t_chrom'] == "chr1"
        assert data['q_chrom'] == "chr2"
        assert data['t_strand'] == 1
        assert data['q_strand'] == 1
        assert data['t_size'] == 248956422
        assert data['q_size'] == 242193529
        assert data['child_id'] is None
        
        # Check blocks conversion
        assert isinstance(data['blocks'], list)
        assert len(data['blocks']) == 3
        assert data['blocks'][0] == [1000, 1100, 500, 600]
    
    def test_genome_alignment_from_dict(self, simple_genome_alignment):
        """Test creating GenomeAlignment from dictionary."""
        data = genome_alignment_to_dict(simple_genome_alignment)
        reconstructed = genome_alignment_from_dict(data)
        
        assert reconstructed.chain_id == simple_genome_alignment.chain_id
        assert reconstructed.score == simple_genome_alignment.score
        assert reconstructed.t_chrom == simple_genome_alignment.t_chrom
        assert reconstructed.q_chrom == simple_genome_alignment.q_chrom
        assert reconstructed.t_strand == simple_genome_alignment.t_strand
        assert reconstructed.q_strand == simple_genome_alignment.q_strand
        assert np.array_equal(reconstructed.blocks, simple_genome_alignment.blocks)
    
    def test_genome_alignment_round_trip_serialization(self, simple_genome_alignment):
        """Test round-trip serialization preserves data."""
        data = genome_alignment_to_dict(simple_genome_alignment)
        reconstructed = genome_alignment_from_dict(data)
        
        # Compare all attributes
        assert reconstructed.chain_id == simple_genome_alignment.chain_id
        assert reconstructed.score == simple_genome_alignment.score
        assert reconstructed.t_size == simple_genome_alignment.t_size
        assert reconstructed.q_size == simple_genome_alignment.q_size
        assert np.array_equal(reconstructed.blocks, simple_genome_alignment.blocks)
    
    def test_genome_alignments_collection_to_dict(self, genome_alignments_collection):
        """Test converting collection to dictionary."""
        data = genome_alignments_collection_to_dict(genome_alignments_collection)
        
        assert data['count'] == 2
        assert data['source_file'] == "test_chains.chain"
        assert len(data['alignments']) == 2
        
        # Check first alignment data
        first_alignment = data['alignments'][0]
        assert first_alignment['chain_id'] == 12345
        assert first_alignment['score'] == 15000
    
    def test_genome_alignments_collection_from_dict(self, genome_alignments_collection):
        """Test creating collection from dictionary."""
        data = genome_alignments_collection_to_dict(genome_alignments_collection)
        reconstructed = genome_alignments_collection_from_dict(data)
        
        assert len(reconstructed) == len(genome_alignments_collection)
        assert reconstructed.source_file == genome_alignments_collection.source_file
        
        # Check that alignments are preserved
        for orig, recon in zip(genome_alignments_collection.alignments, reconstructed.alignments):
            assert orig.chain_id == recon.chain_id
            assert orig.score == recon.score
            assert np.array_equal(orig.blocks, recon.blocks)
    
    def test_save_and_load_json(self, genome_alignments_collection):
        """Test saving and loading JSON files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Save collection to JSON
            save_genome_alignments_collection_to_json(genome_alignments_collection, tmp_path)
            
            # Load collection from JSON
            loaded_collection = load_genome_alignments_collection_from_json(tmp_path)
            
            # Verify data integrity
            assert len(loaded_collection) == len(genome_alignments_collection)
            assert loaded_collection.source_file == genome_alignments_collection.source_file
            
            for orig, loaded in zip(genome_alignments_collection.alignments, loaded_collection.alignments):
                assert orig.chain_id == loaded.chain_id
                assert orig.score == loaded.score
                assert np.array_equal(orig.blocks, loaded.blocks)
                
        finally:
            tmp_path.unlink()
    
    def test_genome_alignments_collection_summary_string(self, genome_alignments_collection):
        """Test generating summary string for collection."""
        summary = genome_alignments_collection_summary_string(genome_alignments_collection)
        
        assert "GenomeAlignmentsCollection: 2 alignments" in summary
        assert "2 target chroms, 2 query chroms" in summary
        assert "avg score:" in summary
        assert "Source: test_chains.chain" in summary
    
    def test_summary_string_empty_collection(self):
        """Test summary string for empty collection."""
        empty_collection = GenomeAlignmentsCollection()
        summary = genome_alignments_collection_summary_string(empty_collection)
        
        assert "GenomeAlignmentsCollection: 0 alignments" in summary


class TestTranscriptBED12Serialization(TestFixtures):
    """Test BED12 format serialization for transcripts."""
    
    def test_transcript_to_bed12_string_coding(self, coding_transcript):
        """Test converting coding transcript to BED12 format."""
        bed12_string = transcript_to_bed12_string(coding_transcript)
        
        fields = bed12_string.split('\t')
        assert len(fields) == 12
        
        # Check basic fields
        assert fields[0] == "chr1"  # chrom
        assert fields[1] == "1000"  # chromStart
        assert fields[2] == "2300"  # chromEnd
        assert fields[3] == "ENST00000123456"  # name
        assert fields[4] == "1000"  # score
        assert fields[5] == "+"  # strand
        assert fields[6] == "1100"  # thickStart (CDS start)
        assert fields[7] == "2200"  # thickEnd (CDS end)
        assert fields[8] == "0"  # itemRgb
        assert fields[9] == "3"  # blockCount
        
        # Check block information
        block_sizes = fields[10].rstrip(',').split(',')
        assert block_sizes == ["200", "200", "300"]  # block sizes
        
        block_starts = fields[11].rstrip(',').split(',')
        assert block_starts == ["0", "500", "1000"]  # relative starts
    
    def test_transcript_to_bed12_string_non_coding(self, non_coding_transcript):
        """Test converting non-coding transcript to BED12 format."""
        bed12_string = transcript_to_bed12_string(non_coding_transcript)
        
        fields = bed12_string.split('\t')
        
        assert fields[0] == "chr2"  # chrom
        assert fields[1] == "5000"  # chromStart
        assert fields[2] == "5800"  # chromEnd
        assert fields[3] == "ENST00000789012"  # name
        assert fields[5] == "-"  # strand
        assert fields[6] == "5000"  # thickStart (same as chromStart for non-coding)
        assert fields[7] == "5000"  # thickEnd (same as chromStart for non-coding)
        assert fields[9] == "2"  # blockCount
    
    def test_transcripts_collection_to_bed12_string(self, transcripts_collection):
        """Test converting transcript collection to BED12 format."""
        bed12_string = transcripts_collection_to_bed12_string(transcripts_collection)
        
        lines = bed12_string.split('\n')
        assert len(lines) == 2
        
        # Check that both transcripts are included
        assert "ENST00000123456" in lines[0]
        assert "ENST00000789012" in lines[1]
        
        # Check chromosome information
        assert lines[0].startswith("chr1")
        assert lines[1].startswith("chr2")
    
    def test_save_transcripts_collection_to_bed12(self, transcripts_collection):
        """Test saving transcript collection to BED12 file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bed', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            save_transcripts_collection_to_bed12(transcripts_collection, tmp_path)
            
            # Verify file was created and has content
            assert tmp_path.exists()
            content = tmp_path.read_text()
            assert "ENST00000123456" in content
            assert "ENST00000789012" in content
            
            # Verify format
            lines = content.strip().split('\n')
            assert len(lines) == 2
            for line in lines:
                fields = line.split('\t')
                assert len(fields) == 12  # Valid BED12 format
                
        finally:
            tmp_path.unlink()


class TestTranscriptJSONSerialization(TestFixtures):
    """Test JSON serialization for transcripts."""
    
    def test_transcript_to_dict_coding(self, coding_transcript):
        """Test converting coding transcript to dictionary."""
        data = transcript_to_dict(coding_transcript)
        
        assert data['id'] == "ENST00000123456"
        assert data['chrom'] == "chr1"
        assert data['strand'] == Strand.PLUS.value
        assert data['cds_start'] == 1100
        assert data['cds_end'] == 2200
        assert data['biotype'] == "protein_coding"
        
        # Check blocks
        assert isinstance(data['blocks'], list)
        assert len(data['blocks']) == 3
        assert data['blocks'][0] == [1000, 1200]
    
    def test_transcript_to_dict_non_coding(self, non_coding_transcript):
        """Test converting non-coding transcript to dictionary."""
        data = transcript_to_dict(non_coding_transcript)
        
        assert data['id'] == "ENST00000789012"
        assert data['chrom'] == "chr2"
        assert data['strand'] == Strand.MINUS.value
        assert data['cds_start'] is None
        assert data['cds_end'] is None
        assert data['biotype'] == "lncRNA"
    
    def test_transcript_from_dict(self, coding_transcript):
        """Test creating transcript from dictionary."""
        data = transcript_to_dict(coding_transcript)
        reconstructed = transcript_from_dict(data)
        
        assert reconstructed.id == coding_transcript.id
        assert reconstructed.chrom == coding_transcript.chrom
        assert reconstructed.strand == coding_transcript.strand
        assert reconstructed.cds_start == coding_transcript.cds_start
        assert reconstructed.cds_end == coding_transcript.cds_end
        assert reconstructed.biotype == coding_transcript.biotype
        assert np.array_equal(reconstructed.blocks, coding_transcript.blocks)
    
    def test_transcript_round_trip_serialization(self, coding_transcript):
        """Test round-trip serialization preserves data."""
        data = transcript_to_dict(coding_transcript)
        reconstructed = transcript_from_dict(data)
        
        # Test that CDS blocks are computed correctly
        assert np.array_equal(reconstructed.cds_blocks, coding_transcript.cds_blocks)
        assert reconstructed.is_coding == coding_transcript.is_coding
    
    def test_transcripts_collection_to_dict(self, transcripts_collection):
        """Test converting transcript collection to dictionary."""
        data = transcripts_collection_to_dict(transcripts_collection)
        
        assert data['count'] == 2
        assert data['source_file'] == "test_transcripts.bed12"
        assert len(data['transcripts']) == 2
        
        # Check transcript data
        first_transcript = data['transcripts'][0]
        assert first_transcript['id'] == "ENST00000123456"
    
    def test_transcripts_collection_from_dict(self, transcripts_collection):
        """Test creating transcript collection from dictionary."""
        data = transcripts_collection_to_dict(transcripts_collection)
        reconstructed = transcripts_collection_from_dict(data)
        
        assert len(reconstructed) == len(transcripts_collection)
        assert reconstructed.source_file == transcripts_collection.source_file
        
        # Check that transcripts are preserved
        for orig, recon in zip(transcripts_collection.transcripts, reconstructed.transcripts):
            assert orig.id == recon.id
            assert orig.chrom == recon.chrom
            assert orig.strand == recon.strand
            assert np.array_equal(orig.blocks, recon.blocks)
    
    def test_save_and_load_transcript_json(self, transcripts_collection):
        """Test saving and loading transcript JSON files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Save collection to JSON
            save_transcripts_collection_to_json(transcripts_collection, tmp_path)
            
            # Load collection from JSON
            loaded_collection = load_transcripts_collection_from_json(tmp_path)
            
            # Verify data integrity
            assert len(loaded_collection) == len(transcripts_collection)
            assert loaded_collection.source_file == transcripts_collection.source_file
            
            for orig, loaded in zip(transcripts_collection.transcripts, loaded_collection.transcripts):
                assert orig.id == loaded.id
                assert orig.chrom == loaded.chrom
                assert np.array_equal(orig.blocks, loaded.blocks)
                
        finally:
            tmp_path.unlink()
    
    def test_transcripts_collection_summary_string(self, transcripts_collection):
        """Test generating summary string for transcript collection."""
        summary = transcripts_collection_summary_string(transcripts_collection)
        
        assert "TranscriptsCollection: 2 transcripts" in summary
        assert "2 chromosomes" in summary
        assert "1 coding (50.0%)" in summary
        assert "Source: test_transcripts.bed12" in summary
    
    def test_summary_string_empty_transcript_collection(self):
        """Test summary string for empty transcript collection."""
        empty_collection = TranscriptsCollection()
        summary = transcripts_collection_summary_string(empty_collection)
        
        assert "TranscriptsCollection: 0 transcripts" in summary


class TestErrorHandling(TestFixtures):
    """Test error handling in serialization."""
    
    def test_invalid_json_file(self):
        """Test handling of invalid JSON files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_file.write("invalid json content")
            tmp_path = Path(tmp_file.name)
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_genome_alignments_collection_from_json(tmp_path)
        finally:
            tmp_path.unlink()
    
    def test_missing_file(self):
        """Test handling of missing files."""
        non_existent_path = Path("non_existent_file.json")
        
        with pytest.raises(FileNotFoundError):
            load_genome_alignments_collection_from_json(non_existent_path)
    
    def test_empty_blocks_alignment(self):
        """Test serialization of alignment with empty blocks."""
        empty_alignment = GenomeAlignment(
            chain_id=1,
            score=0,
            t_chrom="chr1",
            t_strand=1,
            t_size=1000,
            q_chrom="chr2",
            q_strand=1,
            q_size=1000,
            blocks=np.empty((0, 4), dtype=np.int32)
        )
        
        # Should handle empty blocks gracefully
        chain_string = genome_alignment_to_chain_string(empty_alignment)
        assert "chain 0" in chain_string
        
        # JSON serialization should also work
        data = genome_alignment_to_dict(empty_alignment)
        reconstructed = genome_alignment_from_dict(data)
        assert len(reconstructed.blocks) == 0


class TestDataIntegrity(TestFixtures):
    """Test data integrity across different serialization formats."""
    
    def test_chain_format_coordinates(self, simple_genome_alignment):
        """Test that chain format preserves coordinate information."""
        chain_string = genome_alignment_to_chain_string(simple_genome_alignment)
        
        # Extract header information
        header_line = chain_string.split('\n')[0]
        parts = header_line.split()
        
        # Verify coordinate information
        assert parts[2] == "chr1"  # t_chrom
        assert parts[7] == "chr2"  # q_chrom
        assert int(parts[5]) == 1000  # t_start
        assert int(parts[6]) == 1600  # t_end
        assert int(parts[10]) == 500  # q_start
        assert int(parts[11]) == 1000  # q_end
    
    def test_bed12_format_coordinates(self, coding_transcript):
        """Test that BED12 format preserves coordinate information."""
        bed12_string = transcript_to_bed12_string(coding_transcript)
        fields = bed12_string.split('\t')
        
        # Verify coordinate information
        assert int(fields[1]) == 1000  # chromStart
        assert int(fields[2]) == 2300  # chromEnd
        assert int(fields[6]) == 1100  # thickStart (CDS start)
        assert int(fields[7]) == 2200  # thickEnd (CDS end)
        
        # Verify block structure
        block_count = int(fields[9])
        assert block_count == 3
        
        block_sizes = [int(x) for x in fields[10].rstrip(',').split(',')]
        assert sum(block_sizes) == 700  # Total exon length
    
    def test_cross_format_consistency(self, simple_genome_alignment):
        """Test consistency between chain and JSON formats."""
        # Convert to both formats
        chain_string = genome_alignment_to_chain_string(simple_genome_alignment)
        json_data = genome_alignment_to_dict(simple_genome_alignment)
        
        # Reconstruct from JSON
        reconstructed = genome_alignment_from_dict(json_data)
        
        # Generate chain string from reconstructed alignment
        reconstructed_chain_string = genome_alignment_to_chain_string(reconstructed)
        
        # Should be identical
        assert chain_string == reconstructed_chain_string


if __name__ == "__main__":
    pytest.main([__file__, "-v"])