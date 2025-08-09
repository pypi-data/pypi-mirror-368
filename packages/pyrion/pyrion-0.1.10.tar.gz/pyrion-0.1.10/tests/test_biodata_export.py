"""Test biodata export functionality (TSV and BED12).

Tests for exporting GeneData to TSV format and TranscriptsCollection to BED12 format.
"""

import pytest
import tempfile
from pathlib import Path
from pyrion.io.gtf import read_gtf
from pyrion.io.gene_data import write_gene_data_tsv
from pyrion.core.gene_data import GeneData


@pytest.mark.io
class TestGeneDataTSVExport:
    """Test TSV export functionality for GeneData."""
    
    @pytest.fixture
    def sample_collection_with_genedata(self):
        """Load GTF with gene data for testing."""
        gtf_file = Path("test_data/gtf/sample_gencode.gtf")
        return read_gtf(str(gtf_file))
    
    def test_write_gene_data_tsv_basic(self, sample_collection_with_genedata):
        """Test basic TSV export functionality."""
        collection = sample_collection_with_genedata
        gene_data = collection._gene_data
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Write TSV file
            write_gene_data_tsv(gene_data, tmp_path)
            
            # Verify file was created and has content
            assert Path(tmp_path).exists()
            assert Path(tmp_path).stat().st_size > 0
            
            # Read and verify content
            with open(tmp_path, 'r') as f:
                lines = f.readlines()
            
            # Should have header + data lines
            assert len(lines) > 1, "TSV file should have header + data lines"
            
            # Check header
            header = lines[0].strip().split('\t')
            expected_columns = ['transcript_id', 'gene_id', 'transcript_biotype', 'gene_name']
            assert header == expected_columns, f"Unexpected header: {header}"
            
            # Check data lines
            for i, line in enumerate(lines[1:], 1):
                fields = line.strip().split('\t')
                assert len(fields) == 4, f"Line {i} should have 4 fields, got {len(fields)}"
                
                transcript_id, gene_id, biotype, gene_name = fields
                assert transcript_id.startswith('ENST'), f"Invalid transcript ID: {transcript_id}"
                assert gene_id.startswith('ENSG'), f"Invalid gene ID: {gene_id}"
                assert len(biotype) > 0, f"Empty biotype on line {i}"
                # gene_name can be empty (represented as empty string)
                
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_write_gene_data_tsv_selective_columns(self, sample_collection_with_genedata):
        """Test TSV export with selective column inclusion."""
        collection = sample_collection_with_genedata
        gene_data = collection._gene_data
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Write only biotype information
            write_gene_data_tsv(
                gene_data, 
                tmp_path,
                include_gene_transcript=True,
                include_transcript_biotype=True,
                include_gene_name=False
            )
            
            # Read and verify content
            with open(tmp_path, 'r') as f:
                lines = f.readlines()
            
            # Check header
            header = lines[0].strip().split('\t')
            expected_columns = ['transcript_id', 'gene_id', 'transcript_biotype']
            assert header == expected_columns, f"Unexpected header: {header}"
            
            # Check data lines have correct number of fields
            for line in lines[1:]:
                fields = line.strip().split('\t')
                assert len(fields) == 3, f"Expected 3 fields, got {len(fields)}"
                
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_write_gene_data_tsv_custom_separator(self, sample_collection_with_genedata):
        """Test TSV export with custom separator."""
        collection = sample_collection_with_genedata
        gene_data = collection._gene_data
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Write with comma separator
            write_gene_data_tsv(gene_data, tmp_path, separator=',')
            
            # Read and verify content
            with open(tmp_path, 'r') as f:
                lines = f.readlines()
            
            # Check that commas are used as separators
            header = lines[0].strip()
            assert ',' in header, "Should use comma separator"
            assert '\t' not in header, "Should not contain tabs"
            
            # Check data lines
            for line in lines[1:]:
                assert ',' in line, "Data lines should use comma separator"
                
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_write_gene_data_tsv_empty_genedata(self):
        """Test TSV export with empty GeneData."""
        gene_data = GeneData()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Should raise error for empty data (no mappings to export)
            with pytest.raises(ValueError, match="No data mappings available"):
                write_gene_data_tsv(gene_data, tmp_path)
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)


@pytest.mark.io
class TestTranscriptsCollectionBiodataExport:
    """Test the save_biodata method on TranscriptsCollection."""
    
    @pytest.fixture
    def sample_collection_with_genedata(self):
        """Load GTF with gene data for testing."""
        gtf_file = Path("test_data/gtf/sample_gencode.gtf")
        return read_gtf(str(gtf_file))
    
    def test_save_biodata_basic(self, sample_collection_with_genedata):
        """Test basic save_biodata functionality."""
        collection = sample_collection_with_genedata
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Use save_biodata method
            collection.save_biodata(tmp_path)
            
            # Verify file was created correctly
            assert Path(tmp_path).exists()
            assert Path(tmp_path).stat().st_size > 0
            
            # Read and verify content
            with open(tmp_path, 'r') as f:
                lines = f.readlines()
            
            assert len(lines) > 1, "Should have header + data"
            
            # Check header
            header = lines[0].strip().split('\t')
            expected_columns = ['transcript_id', 'gene_id', 'transcript_biotype', 'gene_name']
            assert header == expected_columns
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_save_biodata_selective_columns(self, sample_collection_with_genedata):
        """Test save_biodata with selective column inclusion."""
        collection = sample_collection_with_genedata
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Save only gene-transcript mapping and biotypes
            collection.save_biodata(
                tmp_path,
                include_gene_transcript=True,
                include_transcript_biotype=True,
                include_gene_name=False
            )
            
            # Verify content
            with open(tmp_path, 'r') as f:
                lines = f.readlines()
            
            header = lines[0].strip().split('\t')
            expected_columns = ['transcript_id', 'gene_id', 'transcript_biotype']
            assert header == expected_columns
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_save_biodata_no_genedata_raises_error(self):
        """Test that save_biodata raises error when no GeneData is bound."""
        from pyrion.core.genes import TranscriptsCollection
        
        # Create collection without gene data
        collection = TranscriptsCollection(transcripts=[])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Should raise ValueError
            with pytest.raises(ValueError, match="No GeneData bound"):
                collection.save_biodata(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


@pytest.mark.io
class TestBED12Export:
    """Test BED12 export using existing save_to_bed12 method."""
    
    @pytest.fixture
    def sample_collection(self):
        """Load transcripts for testing."""
        gtf_file = Path("test_data/gtf/sample_gencode.gtf")
        return read_gtf(str(gtf_file))
    
    def test_save_to_bed12_basic(self, sample_collection):
        """Test that existing save_to_bed12 method works correctly."""
        collection = sample_collection
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bed', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Use existing save_to_bed12 method
            collection.save_to_bed12(tmp_path)
            
            # Verify file was created
            assert Path(tmp_path).exists()
            assert Path(tmp_path).stat().st_size > 0
            
            # Read and verify BED12 format
            with open(tmp_path, 'r') as f:
                lines = f.readlines()
            
            assert len(lines) > 0, "BED12 file should have content"
            
            # Check BED12 format (12 tab-separated fields)
            for i, line in enumerate(lines):
                fields = line.strip().split('\t')
                assert len(fields) == 12, f"Line {i+1} should have 12 BED12 fields, got {len(fields)}"
                
                # Basic format checks
                chrom, start, end, name, score, strand = fields[:6]
                assert chrom.startswith('chr'), f"Invalid chromosome: {chrom}"
                
                # Check coordinates - for minus strand genes, coordinates can be complex
                start_pos, end_pos = int(start), int(end)
                assert start_pos <= end_pos, f"Invalid coordinates: {start} > {end} (line {i+1})"
                assert start_pos >= 0, f"Negative start coordinate: {start}"
                
                assert name.startswith('ENST'), f"Invalid transcript ID: {name}"
                assert strand in ['+', '-'], f"Invalid strand: {strand}"
                
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_bed12_content_integrity(self, sample_collection):
        """Test that BED12 export preserves transcript structure correctly."""
        collection = sample_collection
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bed', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            collection.save_to_bed12(tmp_path)
            
            # Read BED12 content
            with open(tmp_path, 'r') as f:
                bed_lines = f.readlines()
            
            # Compare first few transcripts with original data
            for i, transcript in enumerate(collection.transcripts[:5]):
                bed_fields = bed_lines[i].strip().split('\t')
                
                # Check basic coordinates match
                bed_chrom = bed_fields[0]
                bed_start = int(bed_fields[1])
                bed_end = int(bed_fields[2])
                bed_name = bed_fields[3]
                bed_strand = bed_fields[5]
                
                assert bed_chrom == transcript.chrom
                assert bed_name == transcript.id
                
                expected_strand = '+' if transcript.strand.name == 'PLUS' else '-'
                assert bed_strand == expected_strand
                
                # Check that coordinates are reasonable
                transcript_start = int(transcript.transcript_span[0])
                transcript_end = int(transcript.transcript_span[1])
                
                assert bed_start == transcript_start, f"Start mismatch: {bed_start} vs {transcript_start}"
                assert bed_end == transcript_end, f"End mismatch: {bed_end} vs {transcript_end}"
                
        finally:
            Path(tmp_path).unlink(missing_ok=True)


@pytest.mark.io 
class TestBiodataExportIntegration:
    """Integration tests for biodata export workflow."""
    
    @pytest.fixture
    def sample_collection(self):
        """Load GTF with complete data."""
        gtf_file = Path("test_data/gtf/sample_gencode.gtf")
        return read_gtf(str(gtf_file))
    
    def test_complete_export_workflow(self, sample_collection):
        """Test complete biodata export workflow (both TSV and BED12)."""
        collection = sample_collection
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tsv_path = Path(tmp_dir) / "biodata.tsv"
            bed_path = Path(tmp_dir) / "transcripts.bed"
            
            # Export both formats
            collection.save_biodata(str(tsv_path))
            collection.save_to_bed12(str(bed_path))
            
            # Verify both files exist and have content
            assert tsv_path.exists() and tsv_path.stat().st_size > 0
            assert bed_path.exists() and bed_path.stat().st_size > 0
            
            # Count lines (should be similar for transcripts)
            with open(tsv_path, 'r') as f:
                tsv_lines = len(f.readlines()) - 1  # Subtract header
            
            with open(bed_path, 'r') as f:
                bed_lines = len(f.readlines())
            
            # Should have same number of transcripts
            assert tsv_lines == bed_lines, f"TSV has {tsv_lines} data lines, BED has {bed_lines} lines"
            assert tsv_lines == len(collection.transcripts), f"Expected {len(collection.transcripts)} lines, got {tsv_lines}"
    
    def test_data_consistency_across_formats(self, sample_collection):
        """Test that transcript IDs are consistent across TSV and BED12 exports."""
        collection = sample_collection
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tsv_path = Path(tmp_dir) / "biodata.tsv"
            bed_path = Path(tmp_dir) / "transcripts.bed"
            
            # Export both formats
            collection.save_biodata(str(tsv_path))
            collection.save_to_bed12(str(bed_path))
            
            # Extract transcript IDs from both files
            with open(tsv_path, 'r') as f:
                tsv_lines = f.readlines()[1:]  # Skip header
                tsv_transcript_ids = {line.split('\t')[0] for line in tsv_lines}
            
            with open(bed_path, 'r') as f:
                bed_lines = f.readlines()
                bed_transcript_ids = {line.split('\t')[3] for line in bed_lines}
            
            # Should have the same transcript IDs
            assert tsv_transcript_ids == bed_transcript_ids, "Transcript IDs should match between TSV and BED12"
            
            # Should match original collection
            original_ids = {t.id for t in collection.transcripts}
            assert tsv_transcript_ids == original_ids, "TSV transcript IDs should match original"
            assert bed_transcript_ids == original_ids, "BED12 transcript IDs should match original"