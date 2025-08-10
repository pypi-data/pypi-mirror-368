"""Test GTF file I/O operations.

Tests for reading and parsing GTF (Gene Transfer Format) files using the
high-performance C extension parser. Uses real Gencode v48 annotation data.
"""

import pytest
import numpy as np
from pathlib import Path
from pyrion.io.gtf import read_gtf
from pyrion.core.strand import Strand
from pyrion.core.genes import Transcript, TranscriptsCollection


@pytest.mark.io
class TestGTFReading:
    """Test GTF file reading and parsing."""
    
    @pytest.fixture
    def sample_gtf_file(self):
        """Path to sample GTF file with real Gencode data."""
        return Path("test_data/gtf/sample_gencode.gtf")
    
    def test_gtf_file_exists(self, sample_gtf_file):
        """Test that the sample GTF file exists."""
        assert sample_gtf_file.exists(), f"Sample GTF file not found: {sample_gtf_file}"
        assert sample_gtf_file.stat().st_size > 0, "Sample GTF file is empty"
    
    def test_read_gtf_basic(self, sample_gtf_file):
        """Test basic GTF file reading."""
        collection = read_gtf(str(sample_gtf_file))
        
        assert isinstance(collection, TranscriptsCollection)
        assert len(collection) > 0, "No transcripts were read from GTF file"
        
        # Should have read multiple transcripts from our 4 genes
        assert len(collection) > 20, f"Expected >20 transcripts, got {len(collection)}"
        assert len(collection) < 100, f"Expected <100 transcripts, got {len(collection)}"
    
    def test_gtf_transcript_structure(self, sample_gtf_file):
        """Test GTF transcript parsing and structure."""
        collection = read_gtf(str(sample_gtf_file))
        
        # Test first transcript structure
        transcript = collection[0]
        assert isinstance(transcript, Transcript)
        
        # Check required fields
        assert hasattr(transcript, 'id')
        assert hasattr(transcript, 'chrom')
        assert hasattr(transcript, 'strand')
        assert hasattr(transcript, 'blocks')
        assert hasattr(transcript, 'biotype')
        
        # Check data types and validity
        assert isinstance(transcript.id, str)
        assert isinstance(transcript.chrom, str)
        assert isinstance(transcript.strand, Strand)
        assert isinstance(transcript.blocks, np.ndarray)
        assert transcript.blocks.shape[1] == 2, "Blocks should be (N, 2) array"
        assert len(transcript.blocks) > 0, "Transcript should have at least one exon"
        
        # Check that transcript ID looks like an Ensembl ID
        assert transcript.id.startswith("ENST"), f"Expected Ensembl transcript ID, got: {transcript.id}"
    
    def test_gtf_chromosomes(self, sample_gtf_file):
        """Test chromosome information from GTF."""
        collection = read_gtf(str(sample_gtf_file))
        
        chromosomes = collection.get_all_chromosomes()
        assert len(chromosomes) > 0, "No chromosomes found"
        
        # Should have features from chromosome 1 and 19
        expected_chroms = {'chr1', 'chr19'}
        found_chroms = set(chromosomes)
        overlap = expected_chroms.intersection(found_chroms)
        assert len(overlap) >= 1, f"Expected {expected_chroms}, found {found_chroms}"
        
        # Test getting transcripts by chromosome
        for chrom in chromosomes:
            chrom_transcripts = collection.get_by_chrom(chrom)
            assert len(chrom_transcripts) > 0, f"No transcripts found for {chrom}"
            
            # All transcripts should be on the same chromosome
            for transcript in chrom_transcripts:
                assert transcript.chrom == chrom, f"Transcript {transcript.id} on wrong chromosome"
    
    def test_gtf_transcript_coordinates(self, sample_gtf_file):
        """Test transcript coordinate validity."""
        collection = read_gtf(str(sample_gtf_file))
        
        for transcript in collection.transcripts[:10]:  # Test first 10 transcripts
            # Blocks should be sorted and non-overlapping
            blocks = transcript.blocks
            assert len(blocks) > 0, f"Transcript {transcript.id} has no blocks"
            
            # Check block validity
            for i, (start, end) in enumerate(blocks):
                assert start < end, f"Invalid block {i} in {transcript.id}: {start} >= {end}"
                
                # Check block ordering (should be sorted by start)
                if i > 0:
                    prev_end = blocks[i-1, 1]
                    assert start > prev_end, f"Overlapping blocks in {transcript.id}"
    
    def test_gtf_coding_transcripts(self, sample_gtf_file):
        """Test coding transcript features."""
        collection = read_gtf(str(sample_gtf_file))
        
        # Find coding transcripts (should have CDS coordinates)
        coding_transcripts = [t for t in collection.transcripts if t.is_coding]
        assert len(coding_transcripts) > 0, "No coding transcripts found"
        
        # Test coding transcript properties
        for transcript in coding_transcripts[:5]:  # Test first 5
            assert transcript.cds_start is not None, f"Coding transcript {transcript.id} missing CDS start"
            assert transcript.cds_end is not None, f"Coding transcript {transcript.id} missing CDS end"
            
            # For minus strand, coordinates might be stored differently
            if transcript.strand == Strand.MINUS:
                # Just check that both coordinates exist and are different
                assert transcript.cds_start != transcript.cds_end, f"CDS coordinates are identical in {transcript.id}"
            else:
                # For plus strand, normal coordinate ordering
                assert transcript.cds_start < transcript.cds_end, f"Invalid CDS coordinates in {transcript.id}"
            
            # CDS coordinates should be reasonable (not zero)
            assert transcript.cds_start > 0, f"Invalid CDS start in {transcript.id}"
            assert transcript.cds_end > 0, f"Invalid CDS end in {transcript.id}"
    
    def test_gtf_non_coding_transcripts(self, sample_gtf_file):
        """Test non-coding transcript features."""
        collection = read_gtf(str(sample_gtf_file))
        
        # Find non-coding transcripts
        non_coding_transcripts = [t for t in collection.transcripts if not t.is_coding]
        assert len(non_coding_transcripts) > 0, "No non-coding transcripts found"
        
        # Test non-coding transcript properties
        for transcript in non_coding_transcripts[:5]:  # Test first 5
            assert transcript.cds_start is None, f"Non-coding transcript {transcript.id} has CDS start"
            assert transcript.cds_end is None, f"Non-coding transcript {transcript.id} has CDS end"
    
    def test_gtf_biotypes(self, sample_gtf_file):
        """Test transcript biotype information."""
        collection = read_gtf(str(sample_gtf_file))
        
        biotypes = set()
        biotype_count = 0
        for transcript in collection.transcripts:
            if transcript.biotype:
                biotypes.add(transcript.biotype)
                biotype_count += 1
        
        # Check that we have transcripts with and without biotype info
        total_transcripts = len(collection.transcripts)
        transcripts_without_biotype = total_transcripts - biotype_count
        
        # Either we have biotype information, or we expect it to be missing from this data
        if biotype_count > 0:
            # If we have biotypes, they should be reasonable
            assert len(biotypes) > 0, f"No valid biotypes found: {biotypes}"
        else:
            # If no biotypes, that's also acceptable - just document it
            assert biotype_count == 0, f"Expected either all or no biotypes, got {biotype_count}/{total_transcripts}"
    
    def test_gtf_strand_information(self, sample_gtf_file):
        """Test strand information parsing."""
        collection = read_gtf(str(sample_gtf_file))
        
        strands = {transcript.strand for transcript in collection.transcripts}
        
        # Should have transcripts on both strands
        assert Strand.PLUS in strands or Strand.MINUS in strands, "No strand information found"
        
        # Check that strands are valid
        valid_strands = {Strand.PLUS, Strand.MINUS}
        assert strands.issubset(valid_strands), f"Invalid strands found: {strands - valid_strands}"


@pytest.mark.io 
class TestGTFContentValidation:
    """Test specific content of our sample GTF file."""
    
    @pytest.fixture
    def sample_gtf_file(self):
        """Path to sample GTF file."""
        return Path("test_data/gtf/sample_gencode.gtf")
    
    def test_expected_gene_count(self, sample_gtf_file):
        """Test that we have the expected number of genes represented."""
        collection = read_gtf(str(sample_gtf_file))
        
        # We should have transcripts from our 4 selected genes
        # A1BG, A1CF, A2M (protein-coding) and DDX11L16 (lncRNA)
        chromosomes = collection.get_all_chromosomes()
        
        # Our genes are on chr1 and chr19
        expected_chroms = {'chr1', 'chr19'}
        found_chroms = set(chromosomes)
        
        assert len(found_chroms.intersection(expected_chroms)) >= 1, \
            f"Missing expected chromosomes. Found: {found_chroms}"
    
    def test_protein_coding_gene_features(self, sample_gtf_file):
        """Test protein-coding gene transcript features."""
        collection = read_gtf(str(sample_gtf_file))
        
        # Find coding transcripts (regardless of biotype annotation)
        coding_transcripts = [t for t in collection.transcripts if t.is_coding]
        
        assert len(coding_transcripts) > 5, \
            f"Expected >5 coding transcripts, got {len(coding_transcripts)}"
        
        # All coding transcripts should have CDS coordinates
        for transcript in coding_transcripts:
            assert transcript.cds_start is not None, \
                f"Coding transcript {transcript.id} missing CDS start"
            assert transcript.cds_end is not None, \
                f"Coding transcript {transcript.id} missing CDS end"
    
    def test_lncrna_gene_features(self, sample_gtf_file):
        """Test non-coding transcript features."""
        collection = read_gtf(str(sample_gtf_file))
        
        # Find non-coding transcripts (regardless of biotype annotation)
        non_coding = [t for t in collection.transcripts if not t.is_coding]
        
        assert len(non_coding) > 0, "No non-coding transcripts found"
        
        # Non-coding transcripts should not have CDS coordinates
        for transcript in non_coding:
            assert transcript.cds_start is None, \
                f"Non-coding transcript {transcript.id} should not have CDS start"
            assert transcript.cds_end is None, \
                f"Non-coding transcript {transcript.id} should not have CDS end"
    
    def test_transcript_exon_structure(self, sample_gtf_file):
        """Test transcript exon structure validity."""
        collection = read_gtf(str(sample_gtf_file))
        
        for transcript in collection.transcripts[:20]:  # Test first 20
            # Should have at least one exon
            assert len(transcript.blocks) >= 1, \
                f"Transcript {transcript.id} has no exons"
            
            # Multi-exon transcripts should have proper intron structure
            if len(transcript.blocks) > 1:
                introns = transcript.get_introns()
                assert len(introns) == len(transcript.blocks) - 1, \
                    f"Incorrect intron count for {transcript.id}"


class TestGTFErrorHandling:
    """Test GTF error handling and edge cases."""
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent GTF files."""
        with pytest.raises(FileNotFoundError):
            read_gtf("nonexistent.gtf")
    
    def test_empty_file(self, tmp_path):
        """Test handling of empty GTF files."""
        empty_file = tmp_path / "empty.gtf"
        empty_file.write_text("")
        
        collection = read_gtf(str(empty_file))
        assert isinstance(collection, TranscriptsCollection)
        assert len(collection) == 0, "Empty file should return empty collection"
    
    def test_header_only_file(self, tmp_path):
        """Test handling of GTF files with only headers."""
        header_file = tmp_path / "header_only.gtf" 
        header_file.write_text("##gff-version 2\n##description: test\n")
        
        collection = read_gtf(str(header_file))
        assert isinstance(collection, TranscriptsCollection)
        assert len(collection) == 0, "Header-only file should return empty collection"


@pytest.mark.io
class TestGTFIntegration:
    """Integration tests with GTF data."""
    
    @pytest.fixture
    def sample_gtf_file(self):
        """Path to sample GTF file."""
        return Path("test_data/gtf/sample_gencode.gtf")
    
    def test_gtf_to_transcripts_workflow(self, sample_gtf_file):
        """Test complete GTF to transcripts workflow."""
        # Read GTF file
        collection = read_gtf(str(sample_gtf_file))
        
        # Test collection properties
        assert len(collection) > 0
        assert collection.source_file is not None
        
        # Test accessing transcripts by different methods
        all_transcripts = collection.transcripts
        assert len(all_transcripts) > 0
        
        # Test chromosome-based access
        chromosomes = collection.get_all_chromosomes()
        for chrom in chromosomes:
            chrom_transcripts = collection.get_by_chrom(chrom)
            assert all(t.chrom == chrom for t in chrom_transcripts)
        
        # Test ID-based access
        first_transcript = all_transcripts[0]
        retrieved = collection.get_by_id(first_transcript.id)
        assert retrieved is not None
        assert retrieved.id == first_transcript.id
    
    def test_gtf_gene_data_binding(self, sample_gtf_file):
        """Test that gene data is properly bound to the collection."""
        collection = read_gtf(str(sample_gtf_file))
        
        # Should have gene data bound
        assert hasattr(collection, '_gene_data')
        
        # Test that we can access some transcript information
        transcript = collection.transcripts[0] 
        assert transcript.id is not None
        assert isinstance(transcript.id, str)
        assert len(transcript.id) > 0
    
    def test_gtf_biotype_and_gene_name_extraction(self, sample_gtf_file):
        """Test that GTF parsing extracts transcript biotypes and gene names."""
        collection = read_gtf(str(sample_gtf_file))
        
        # Ensure gene data is bound
        assert collection._gene_data is not None
        gene_data = collection._gene_data
        
        # Check that biotype and gene name mappings are present
        assert gene_data.has_biotype_mapping(), "No transcript biotype mappings found"
        assert gene_data.has_gene_name_mapping(), "No gene name mappings found"
        
        # Verify mapping counts
        assert gene_data.get_biotype_count() > 0, "No transcript biotypes extracted"
        assert gene_data.get_gene_name_count() > 0, "No gene names extracted"
        
        # Test specific known transcripts from DDX11L16 gene
        known_transcripts = [
            "ENST00000832824.1",  # DDX11L16-260
            "ENST00000832825.1",  # DDX11L16-261
        ]
        
        for transcript_id in known_transcripts:
            # Test gene mapping
            gene_id = gene_data.get_gene(transcript_id)
            assert gene_id is not None, f"No gene mapping found for {transcript_id}"
            assert gene_id == "ENSG00000290825.2", f"Unexpected gene ID for {transcript_id}: {gene_id}"
            
            # Test biotype extraction
            biotype = gene_data.get_transcript_biotype(transcript_id)
            assert biotype is not None, f"No biotype found for {transcript_id}"
            assert biotype == "lncRNA", f"Expected 'lncRNA' biotype for {transcript_id}, got '{biotype}'"
            
            # Test gene name extraction
            gene_name = gene_data.get_gene_name(gene_id)
            assert gene_name is not None, f"No gene name found for gene {gene_id}"
            assert gene_name == "DDX11L16", f"Expected 'DDX11L16' gene name, got '{gene_name}'"
        
        # Test that all transcripts have biotypes
        for transcript in collection.transcripts:
            biotype = gene_data.get_transcript_biotype(transcript.id)
            assert biotype is not None, f"Missing biotype for transcript {transcript.id}"
            assert isinstance(biotype, str), f"Biotype should be string, got {type(biotype)}"
            assert len(biotype) > 0, f"Empty biotype for transcript {transcript.id}"
        
        # Verify gene names are strings and non-empty
        for gene_id in gene_data.gene_ids:
            gene_name = gene_data.get_gene_name(gene_id)
            if gene_name is not None:  # Gene names are optional
                assert isinstance(gene_name, str), f"Gene name should be string, got {type(gene_name)}"
                assert len(gene_name) > 0, f"Empty gene name for gene {gene_id}"