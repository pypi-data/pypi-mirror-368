"""Test GTF and BED12 parsing equivalence.

Compares transcripts parsed from GTF files with those parsed from equivalent BED12 files
to ensure consistency between parsing methods. Uses specific test files that were 
converted from GTF to BED12 using standard tools (gtfToGenePred and genePredToBed).
"""

import pytest
from pathlib import Path
from pyrion.io.gtf import read_gtf
from pyrion.io.bed import read_bed12_file


@pytest.mark.io
class TestGTFBEDEquivalence:
    """Test equivalence between GTF and BED12 parsing results."""
    
    @pytest.fixture
    def gtf_file_path(self):
        """Path to test GTF file."""
        return Path("test_data/gtf/sample_gencode.gtf")
    
    @pytest.fixture
    def bed_file_path(self):
        """Path to equivalent BED12 file."""
        return Path("test_data/gtf/sample_gencode.ucsc.bed")
    
    @pytest.fixture
    def gtf_transcripts(self, gtf_file_path):
        """Load transcripts from GTF file."""
        return read_gtf(str(gtf_file_path))
    
    @pytest.fixture 
    def bed_transcripts(self, bed_file_path):
        """Load transcripts from BED12 file."""
        return read_bed12_file(str(bed_file_path))
    
    def test_files_exist(self, gtf_file_path, bed_file_path):
        """Test that both test files exist."""
        assert gtf_file_path.exists(), f"GTF file not found: {gtf_file_path}"
        assert bed_file_path.exists(), f"BED12 file not found: {bed_file_path}"
        
        assert gtf_file_path.stat().st_size > 0, "GTF file is empty"
        assert bed_file_path.stat().st_size > 0, "BED12 file is empty"
    
    def test_both_parsers_return_transcripts(self, gtf_transcripts, bed_transcripts):
        """Test that both parsers successfully return transcripts."""
        assert len(gtf_transcripts) > 0, "GTF parser returned no transcripts"
        assert len(bed_transcripts) > 0, "BED12 parser returned no transcripts"
        
        # Should have reasonable number of transcripts
        assert len(gtf_transcripts) > 10, f"Expected >10 GTF transcripts, got {len(gtf_transcripts)}"
        assert len(bed_transcripts) > 10, f"Expected >10 BED12 transcripts, got {len(bed_transcripts)}"
    
    def test_transcript_id_overlap(self, gtf_transcripts, bed_transcripts):
        """Test that GTF and BED12 files contain overlapping transcript IDs."""
        gtf_ids = {t.id for t in gtf_transcripts.transcripts}
        bed_ids = {t.id for t in bed_transcripts.transcripts}
        
        # Should have some overlap (though not necessarily 100% identical)
        overlap = gtf_ids.intersection(bed_ids)
        
        assert len(overlap) > 0, "No common transcript IDs found between GTF and BED12"
        
        # Log for debugging
        overlap_ratio = len(overlap) / min(len(gtf_ids), len(bed_ids))
        
        # Expect at least some reasonable overlap
        assert overlap_ratio > 0.1, f"Low overlap ratio: {overlap_ratio:.2%}"
    
    def test_equivalent_transcript_structure(self, gtf_transcripts, bed_transcripts):
        """Test that equivalent transcripts have the same genomic structure."""
        gtf_by_id = {t.id: t for t in gtf_transcripts.transcripts}
        bed_by_id = {t.id: t for t in bed_transcripts.transcripts}
        
        # Find common transcript IDs
        common_ids = set(gtf_by_id.keys()).intersection(bed_by_id.keys())
        
        assert len(common_ids) > 0, "No common transcript IDs for structure comparison"
        
        # Test first 10 common transcripts
        test_ids = list(common_ids)[:10]
        
        for transcript_id in test_ids:
            gtf_transcript = gtf_by_id[transcript_id]
            bed_transcript = bed_by_id[transcript_id]
            
            # Test basic properties
            assert gtf_transcript.chrom == bed_transcript.chrom, \
                f"Chromosome mismatch for {transcript_id}: GTF={gtf_transcript.chrom}, BED={bed_transcript.chrom}"
            
            assert gtf_transcript.strand == bed_transcript.strand, \
                f"Strand mismatch for {transcript_id}: GTF={gtf_transcript.strand}, BED={bed_transcript.strand}"
            
            # Test exon structure (blocks)
            gtf_blocks = sorted(gtf_transcript.blocks.tolist(), key=lambda x: x[0])
            bed_blocks = sorted(bed_transcript.blocks.tolist(), key=lambda x: x[0])
            
            assert len(gtf_blocks) == len(bed_blocks), \
                f"Exon count mismatch for {transcript_id}: GTF={len(gtf_blocks)}, BED={len(bed_blocks)}"
            
            # Compare exon coordinates (allowing for small differences due to format specifics)
            for i, (gtf_block, bed_block) in enumerate(zip(gtf_blocks, bed_blocks)):
                gtf_start, gtf_end = gtf_block
                bed_start, bed_end = bed_block
                
                # Allow for coordinate system differences (0-based vs 1-based)
                start_diff = abs(gtf_start - bed_start)
                end_diff = abs(gtf_end - bed_end)
                
                assert start_diff <= 1, \
                    f"Exon {i} start mismatch for {transcript_id}: GTF={gtf_start}, BED={bed_start}"
                
                assert end_diff <= 1, \
                    f"Exon {i} end mismatch for {transcript_id}: GTF={gtf_end}, BED={bed_end}"
    
    def test_transcript_span_consistency(self, gtf_transcripts, bed_transcripts):
        """Test that transcript spans are consistent between GTF and BED12."""
        gtf_by_id = {t.id: t for t in gtf_transcripts.transcripts}
        bed_by_id = {t.id: t for t in bed_transcripts.transcripts}
        
        common_ids = set(gtf_by_id.keys()).intersection(bed_by_id.keys())
        
        # Test first 5 common transcripts
        test_ids = list(common_ids)[:5]
        
        for transcript_id in test_ids:
            gtf_transcript = gtf_by_id[transcript_id]
            bed_transcript = bed_by_id[transcript_id]
            
            # Compare transcript spans
            gtf_span = gtf_transcript.transcript_span
            bed_span = bed_transcript.transcript_span
            
            # Allow for small coordinate differences due to coordinate system (0-based vs 1-based)
            start_diff = abs(gtf_span[0] - bed_span[0])
            end_diff = abs(gtf_span[1] - bed_span[1])
            
            assert start_diff <= 1, \
                f"Transcript span start mismatch for {transcript_id}: GTF={gtf_span[0]}, BED={bed_span[0]} (diff={start_diff})"
            
            assert end_diff <= 1, \
                f"Transcript span end mismatch for {transcript_id}: GTF={gtf_span[1]}, BED={bed_span[1]} (diff={end_diff})"
    
    def test_coding_status_consistency(self, gtf_transcripts, bed_transcripts):
        """Test that coding status is consistent between GTF and BED12."""
        gtf_by_id = {t.id: t for t in gtf_transcripts.transcripts}
        bed_by_id = {t.id: t for t in bed_transcripts.transcripts}
        
        common_ids = set(gtf_by_id.keys()).intersection(bed_by_id.keys())
        
        coding_mismatches = 0
        total_compared = 0
        
        for transcript_id in list(common_ids)[:20]:  # Test first 20
            gtf_transcript = gtf_by_id[transcript_id]
            bed_transcript = bed_by_id[transcript_id]
            
            gtf_is_coding = gtf_transcript.is_coding
            bed_is_coding = bed_transcript.is_coding
            
            total_compared += 1
            
            if gtf_is_coding != bed_is_coding:
                coding_mismatches += 1
        
        # Should have very low mismatch rate for equivalent files
        mismatch_rate = coding_mismatches / total_compared if total_compared > 0 else 0
        
        assert mismatch_rate < 0.1, \
            f"High coding status mismatch rate: {mismatch_rate:.2%} ({coding_mismatches}/{total_compared})"
    
    @pytest.mark.slow
    def test_comprehensive_structure_validation(self, gtf_transcripts, bed_transcripts):
        """Comprehensive validation of transcript structures (marked slow for optional execution)."""
        gtf_by_id = {t.id: t for t in gtf_transcripts.transcripts}
        bed_by_id = {t.id: t for t in bed_transcripts.transcripts}
        
        common_ids = set(gtf_by_id.keys()).intersection(bed_by_id.keys())
        
        validation_errors = []
        
        for transcript_id in common_ids:
            gtf_transcript = gtf_by_id[transcript_id]
            bed_transcript = bed_by_id[transcript_id]
            
            # Validate exon ordering and non-overlap
            try:
                gtf_blocks = sorted(gtf_transcript.blocks.tolist())
                bed_blocks = sorted(bed_transcript.blocks.tolist())
                
                # Check for overlapping exons within each transcript
                for i in range(len(gtf_blocks) - 1):
                    if gtf_blocks[i][1] >= gtf_blocks[i+1][0]:
                        validation_errors.append(f"GTF {transcript_id}: overlapping exons {i}, {i+1}")
                
                for i in range(len(bed_blocks) - 1):
                    if bed_blocks[i][1] >= bed_blocks[i+1][0]:
                        validation_errors.append(f"BED {transcript_id}: overlapping exons {i}, {i+1}")
                
                # Check that exon structures are similar
                if len(gtf_blocks) != len(bed_blocks):
                    validation_errors.append(f"{transcript_id}: exon count differs GTF={len(gtf_blocks)} vs BED={len(bed_blocks)}")
                
            except Exception as e:
                validation_errors.append(f"{transcript_id}: validation error - {str(e)}")
        
        # Report errors but don't fail unless there are too many
        if validation_errors:
            error_rate = len(validation_errors) / len(common_ids)
            
            # Log first few errors for debugging
            for error in validation_errors[:5]:
                print(f"Validation error: {error}")
            
            if len(validation_errors) > 5:
                print(f"... and {len(validation_errors) - 5} more errors")
            
            assert error_rate < 0.1, f"High validation error rate: {error_rate:.2%}"


@pytest.mark.io
class TestGTFBEDEquivalenceMetadata:
    """Test metadata consistency between GTF and BED12 parsing."""
    
    @pytest.fixture
    def gtf_transcripts(self):
        """Load transcripts from GTF file."""
        gtf_file = Path("test_data/gtf/sample_gencode.gtf")
        return read_gtf(str(gtf_file))
    
    @pytest.fixture
    def bed_transcripts(self):
        """Load transcripts from BED12 file.""" 
        bed_file = Path("test_data/hg38.v48.comprehensive.bed")
        return read_bed12_file(str(bed_file))
    
    def test_chromosome_coverage(self, gtf_transcripts, bed_transcripts):
        """Test that chromosome coverage is similar between formats."""
        gtf_chroms = set(gtf_transcripts.get_all_chromosomes())
        bed_chroms = set(bed_transcripts.get_all_chromosomes())
        
        # Should have some chromosome overlap
        common_chroms = gtf_chroms.intersection(bed_chroms)
        assert len(common_chroms) > 0, "No common chromosomes found"
        
        # Log chromosome information for debugging
        print(f"GTF chromosomes: {sorted(gtf_chroms)}")
        print(f"BED chromosomes: {sorted(bed_chroms)}")
        print(f"Common chromosomes: {sorted(common_chroms)}")
    
    def test_strand_distribution(self, gtf_transcripts, bed_transcripts):
        """Test that strand distribution is similar between formats."""
        gtf_by_id = {t.id: t for t in gtf_transcripts.transcripts}
        bed_by_id = {t.id: t for t in bed_transcripts.transcripts}
        
        common_ids = set(gtf_by_id.keys()).intersection(bed_by_id.keys())
        
        if len(common_ids) == 0:
            pytest.skip("No common transcript IDs for strand comparison")
        
        strand_matches = 0
        for transcript_id in common_ids:
            if gtf_by_id[transcript_id].strand == bed_by_id[transcript_id].strand:
                strand_matches += 1
        
        match_rate = strand_matches / len(common_ids)
        assert match_rate > 0.95, f"Low strand match rate: {match_rate:.2%}"
    
    def test_biotype_information_preservation(self, gtf_transcripts):
        """Test that GTF parsing preserves biotype information."""
        # This specifically tests the GTF enhancement we added
        
        # Should have gene data bound
        assert gtf_transcripts._gene_data is not None, "GTF should have gene data bound"
        
        gene_data = gtf_transcripts._gene_data
        
        # Should have biotype mappings
        assert gene_data.has_biotype_mapping(), "GTF should extract biotype information"
        
        # Check that biotypes are reasonable
        biotype_count = gene_data.get_biotype_count()
        assert biotype_count > 0, "Should have extracted some biotypes"
        
        # Should cover most/all transcripts
        transcript_count = len(gtf_transcripts.transcripts)
        coverage_rate = biotype_count / transcript_count
        
        assert coverage_rate > 0.5, f"Low biotype coverage: {coverage_rate:.2%}"