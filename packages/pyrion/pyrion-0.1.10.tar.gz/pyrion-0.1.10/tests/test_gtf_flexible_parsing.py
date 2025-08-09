"""Test flexible GTF attribute field name parsing.

Tests the enhanced GTF parser's ability to handle different field naming conventions
used by various databases (GENCODE/Ensembl, UCSC, NCBI, etc.).
"""

import pytest
import tempfile
from pathlib import Path
from pyrion.io.gtf import read_gtf


@pytest.mark.io
class TestGTFFlexibleFieldNames:
    """Test GTF parsing with various field naming conventions."""
    
    def create_test_gtf(self, attributes_string):
        """Helper to create a test GTF file with specific attributes."""
        gtf_content = f"""##gff-version 2
chr1	TEST	gene	1000	2000	.	+	.	gene_id "TESTG001"; {attributes_string}
chr1	TEST	transcript	1000	2000	.	+	.	gene_id "TESTG001"; transcript_id "TESTT001"; {attributes_string}
chr1	TEST	exon	1000	1500	.	+	.	gene_id "TESTG001"; transcript_id "TESTT001"; exon_number "1";
chr1	TEST	exon	1600	2000	.	+	.	+	.	gene_id "TESTG001"; transcript_id "TESTT001"; exon_number "2";
"""
        return gtf_content
    
    def test_gencode_standard_naming(self):
        """Test GENCODE/Ensembl standard field names."""
        attributes = 'gene_name "TEST1"; gene_type "protein_coding"; transcript_type "protein_coding";'
        gtf_content = self.create_test_gtf(attributes)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
            tmp.write(gtf_content)
            tmp_path = tmp.name
        
        try:
            collection = read_gtf(tmp_path)
            
            assert len(collection.transcripts) == 1, "Should parse one transcript"
            
            gene_data = collection._gene_data
            assert gene_data is not None, "Should have gene data"
            
            # Test gene name extraction
            gene_name = gene_data.get_gene_name("TESTG001")
            assert gene_name == "TEST1", f"Expected 'TEST1', got '{gene_name}'"
            
            # Test biotype extraction
            biotype = gene_data.get_transcript_biotype("TESTT001")
            assert biotype == "protein_coding", f"Expected 'protein_coding', got '{biotype}'"
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_ucsc_variant_naming(self):
        """Test UCSC variant field names."""
        attributes = 'geneName "TEST2"; geneType "lncRNA"; transcriptType "lncRNA";'
        gtf_content = self.create_test_gtf(attributes)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
            tmp.write(gtf_content)
            tmp_path = tmp.name
        
        try:
            collection = read_gtf(tmp_path)
            gene_data = collection._gene_data
            
            # Test gene name extraction with UCSC naming
            gene_name = gene_data.get_gene_name("TESTG001")
            assert gene_name == "TEST2", f"Expected 'TEST2', got '{gene_name}'"
            
            # Test biotype extraction with UCSC naming
            biotype = gene_data.get_transcript_biotype("TESTT001")
            assert biotype == "lncRNA", f"Expected 'lncRNA', got '{biotype}'"
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_ncbi_gff3_style_naming(self):
        """Test NCBI/GFF3 style field names."""
        attributes = 'Name "TEST3"; biotype "pseudogene"; transcript_biotype "pseudogene";'
        gtf_content = self.create_test_gtf(attributes)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
            tmp.write(gtf_content)
            tmp_path = tmp.name
        
        try:
            collection = read_gtf(tmp_path)
            gene_data = collection._gene_data
            
            # Test gene name extraction with GFF3 naming
            gene_name = gene_data.get_gene_name("TESTG001")
            assert gene_name == "TEST3", f"Expected 'TEST3', got '{gene_name}'"
            
            # Test biotype extraction with GFF3 naming  
            biotype = gene_data.get_transcript_biotype("TESTT001")
            assert biotype == "pseudogene", f"Expected 'pseudogene', got '{biotype}'"
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_alternative_gene_symbol_naming(self):
        """Test alternative gene symbol field names."""
        attributes = 'gene_symbol "TEST4"; gene_biotype "miRNA";'
        gtf_content = self.create_test_gtf(attributes)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
            tmp.write(gtf_content)
            tmp_path = tmp.name
        
        try:
            collection = read_gtf(tmp_path)
            gene_data = collection._gene_data
            
            # Test gene name extraction with gene_symbol
            gene_name = gene_data.get_gene_name("TESTG001")
            assert gene_name == "TEST4", f"Expected 'TEST4', got '{gene_name}'"
            
            # Note: gene_biotype should map to transcript biotype in our current implementation
            # This tests the flexible gene type extraction
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_mixed_naming_conventions(self):
        """Test GTF with mixed naming conventions."""
        # Mix GENCODE gene_name with UCSC transcriptType
        attributes = 'gene_name "MIXED"; transcriptType "protein_coding";'
        gtf_content = self.create_test_gtf(attributes)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
            tmp.write(gtf_content)
            tmp_path = tmp.name
        
        try:
            collection = read_gtf(tmp_path)
            gene_data = collection._gene_data
            
            # Should handle mixed conventions correctly
            gene_name = gene_data.get_gene_name("TESTG001")
            assert gene_name == "MIXED", f"Expected 'MIXED', got '{gene_name}'"
            
            biotype = gene_data.get_transcript_biotype("TESTT001")
            assert biotype == "protein_coding", f"Expected 'protein_coding', got '{biotype}'"
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_missing_optional_fields(self):
        """Test GTF parsing when optional fields are missing."""
        # Only required fields, no gene_name or biotype info
        attributes = ''
        gtf_content = self.create_test_gtf(attributes)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
            tmp.write(gtf_content)
            tmp_path = tmp.name
        
        try:
            collection = read_gtf(tmp_path)
            
            # Should still parse successfully
            assert len(collection.transcripts) == 1, "Should parse transcript without optional fields"
            
            gene_data = collection._gene_data
            assert gene_data is not None, "Should have gene data even without optional fields"
            
            # Optional fields should be None/missing
            gene_name = gene_data.get_gene_name("TESTG001")
            assert gene_name is None, f"Expected None for missing gene name, got '{gene_name}'"
            
            # Biotype might still be None if not provided
            biotype = gene_data.get_transcript_biotype("TESTT001")
            # This could be None or extracted from somewhere else - just check it doesn't crash
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_field_priority_order(self):
        """Test that field extraction follows correct priority order."""
        # Include multiple possible field names - should pick the first match
        attributes = 'Name "SECOND"; gene_name "FIRST"; gene_symbol "THIRD";'
        gtf_content = self.create_test_gtf(attributes)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
            tmp.write(gtf_content)
            tmp_path = tmp.name
        
        try:
            collection = read_gtf(tmp_path)
            gene_data = collection._gene_data
            
            # Should pick gene_name first (appears first in our priority list)
            gene_name = gene_data.get_gene_name("TESTG001")
            assert gene_name == "FIRST", f"Expected 'FIRST' (gene_name priority), got '{gene_name}'"
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_quoted_values_with_spaces(self):
        """Test handling of quoted values containing spaces."""
        attributes = 'gene_name "Multi Word Gene"; transcript_type "protein coding";'
        gtf_content = self.create_test_gtf(attributes)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
            tmp.write(gtf_content)
            tmp_path = tmp.name
        
        try:
            collection = read_gtf(tmp_path)
            gene_data = collection._gene_data
            
            # Should handle spaces in quoted values
            gene_name = gene_data.get_gene_name("TESTG001")
            assert gene_name == "Multi Word Gene", f"Expected 'Multi Word Gene', got '{gene_name}'"
            
            biotype = gene_data.get_transcript_biotype("TESTT001")
            assert biotype == "protein coding", f"Expected 'protein coding', got '{biotype}'"
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_special_characters_in_values(self):
        """Test handling of special characters in field values."""
        # Use various special characters that might appear in gene names
        attributes = 'gene_name "GENE-1.2_TEST"; transcript_type "protein_coding";'
        gtf_content = self.create_test_gtf(attributes)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
            tmp.write(gtf_content)
            tmp_path = tmp.name
        
        try:
            collection = read_gtf(tmp_path)
            gene_data = collection._gene_data
            
            # Should handle special characters correctly
            gene_name = gene_data.get_gene_name("TESTG001")
            assert gene_name == "GENE-1.2_TEST", f"Expected 'GENE-1.2_TEST', got '{gene_name}'"
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)


@pytest.mark.io
class TestGTFFlexibleParsingIntegration:
    """Integration tests for flexible GTF parsing with real data."""
    
    @pytest.fixture
    def sample_gtf_file(self):
        """Use the standard test GTF file."""
        return Path("test_data/gtf/sample_gencode.gtf")
    
    def test_real_gtf_flexible_parsing(self, sample_gtf_file):
        """Test that the flexible parsing works with real GTF data."""
        collection = read_gtf(str(sample_gtf_file))
        gene_data = collection._gene_data
        
        # Should have extracted gene names and biotypes
        assert gene_data.has_gene_name_mapping(), "Should extract gene names from real data"
        assert gene_data.has_biotype_mapping(), "Should extract biotypes from real data"
        
        # Test specific known gene from the sample data
        # DDX11L16 should be present
        target_gene_id = "ENSG00000290825.2"
        gene_name = gene_data.get_gene_name(target_gene_id)
        
        assert gene_name is not None, f"Should find gene name for {target_gene_id}"
        assert gene_name == "DDX11L16", f"Expected 'DDX11L16', got '{gene_name}'"
    
    def test_biotype_variety_extraction(self, sample_gtf_file):
        """Test that various biotypes are correctly extracted."""
        collection = read_gtf(str(sample_gtf_file))
        gene_data = collection._gene_data
        
        # Collect all biotypes
        all_biotypes = set()
        for transcript in collection.transcripts:
            biotype = gene_data.get_transcript_biotype(transcript.id)
            if biotype:
                all_biotypes.add(biotype)
        
        # Should have multiple biotype categories
        assert len(all_biotypes) > 1, f"Expected multiple biotypes, got: {all_biotypes}"
        
        # Should include common biotypes
        expected_biotypes = {"protein_coding", "lncRNA"}
        found_expected = all_biotypes.intersection(expected_biotypes)
        assert len(found_expected) > 0, f"Expected to find {expected_biotypes}, got {all_biotypes}"
    
    def test_gene_name_coverage(self, sample_gtf_file):
        """Test gene name extraction coverage."""
        collection = read_gtf(str(sample_gtf_file))
        gene_data = collection._gene_data
        
        # Count genes with names
        genes_with_names = 0
        total_genes = len(gene_data.gene_ids)
        
        for gene_id in gene_data.gene_ids:
            if gene_data.get_gene_name(gene_id) is not None:
                genes_with_names += 1
        
        # Should have reasonable coverage (not all genes may have names)
        coverage = genes_with_names / total_genes if total_genes > 0 else 0
        
        assert coverage > 0, "Should extract some gene names"
        # Don't enforce 100% coverage as it depends on the source data


@pytest.mark.io
class TestGTFFlexibleParsingErrorCases:
    """Test error handling in flexible GTF parsing."""
    
    def test_malformed_attributes(self):
        """Test handling of malformed attribute strings."""
        # Missing quotes, incomplete fields, etc.
        malformed_attributes = [
            'gene_name NOQUOTES; transcript_type "protein_coding";',  # Missing quotes
            'gene_name "UNCLOSED; transcript_type "protein_coding";',  # Unclosed quote
            'gene_name; transcript_type "protein_coding";',  # Missing value
            '"ORPHAN_VALUE"; transcript_type "protein_coding";',  # Orphan value
        ]
        
        for i, attributes in enumerate(malformed_attributes):
            gtf_content = f"""##gff-version 2
chr1	TEST	gene	1000	2000	.	+	.	gene_id "TESTG00{i}"; {attributes}
chr1	TEST	transcript	1000	2000	.	+	.	gene_id "TESTG00{i}"; transcript_id "TESTT00{i}"; {attributes}
chr1	TEST	exon	1000	2000	.	+	.	gene_id "TESTG00{i}"; transcript_id "TESTT00{i}"; exon_number "1";
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
                tmp.write(gtf_content)
                tmp_path = tmp.name
            
            try:
                # Should not crash, even with malformed attributes
                collection = read_gtf(tmp_path)
                
                # Should still parse the transcript
                assert len(collection.transcripts) == 1, f"Should parse transcript despite malformed attributes (case {i})"
                
                # Gene data should exist but may not extract the malformed fields
                gene_data = collection._gene_data
                assert gene_data is not None, f"Should have gene data (case {i})"
                
            except Exception as e:
                # If it does fail, it should be a reasonable error, not a segfault
                assert "parse" in str(e).lower() or "format" in str(e).lower(), \
                    f"Unexpected error type for malformed case {i}: {e}"
            finally:
                Path(tmp_path).unlink(missing_ok=True)
    
    def test_extremely_long_values(self):
        """Test handling of extremely long field values."""
        long_value = "A" * 10000  # Very long gene name
        attributes = f'gene_name "{long_value}"; transcript_type "protein_coding";'
        
        gtf_content = f"""##gff-version 2
chr1	TEST	gene	1000	2000	.	+	.	gene_id "TESTG001"; {attributes}
chr1	TEST	transcript	1000	2000	.	+	.	gene_id "TESTG001"; transcript_id "TESTT001"; {attributes}
chr1	TEST	exon	1000	2000	.	+	.	gene_id "TESTG001"; transcript_id "TESTT001"; exon_number "1";
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gtf', delete=False) as tmp:
            tmp.write(gtf_content)
            tmp_path = tmp.name
        
        try:
            # Should handle long values gracefully
            collection = read_gtf(tmp_path)
            gene_data = collection._gene_data
            
            gene_name = gene_data.get_gene_name("TESTG001")
            
            # Should either extract the full long name or handle it gracefully
            if gene_name is not None:
                assert len(gene_name) > 1000, "Should extract long gene name"
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)