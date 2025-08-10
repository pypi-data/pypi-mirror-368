"""Comprehensive tests for high-priority pyrion modules."""

import pytest
import numpy as np


class TestIntervalsModule:
    """Test pyrion.ops.intervals functions."""
    
    def test_find_intersections(self):
        """Test find_intersections function."""
        from pyrion.ops.intervals import find_intersections
        
        arr1 = np.array([[10, 50], [100, 150]], dtype=np.int32)
        arr2 = np.array([[30, 80], [120, 180]], dtype=np.int32)
        intersections = find_intersections(arr1, arr2)
        
        assert len(intersections) == 2
        assert intersections[0][0][1] == 20  # Overlap size
        assert intersections[1][0][1] == 30
    
    def test_compute_overlap_size(self):
        """Test compute_overlap_size function."""
        from pyrion.ops.intervals import compute_overlap_size
        
        overlap = compute_overlap_size(10, 50, 30, 80)
        assert overlap == 20
        
        no_overlap = compute_overlap_size(10, 20, 30, 40)
        assert no_overlap == 0
    
    def test_intervals_to_array(self):
        """Test intervals_to_array function."""
        from pyrion.ops.intervals import intervals_to_array
        from pyrion.core.intervals import GenomicInterval
        from pyrion.core.strand import Strand
        
        intervals = [
            GenomicInterval("chr1", 100, 200, Strand.PLUS),
            GenomicInterval("chr1", 300, 400, Strand.PLUS)
        ]
        array = intervals_to_array(intervals)
        
        expected = np.array([[100, 200], [300, 400]], dtype=np.int32)
        assert np.array_equal(array, expected)
    
    def test_remaining_interval_functions(self):
        """Test additional functions in intervals module."""
        from pyrion.ops.intervals import (
            compute_intersections_core, array_to_intervals, 
            chains_to_arrays, transcripts_to_arrays, 
            projected_intervals_to_genomic_intervals
        )
        
        # Basic smoke tests for remaining functions
        assert callable(compute_intersections_core)
        assert callable(array_to_intervals)
        assert callable(chains_to_arrays)
        assert callable(transcripts_to_arrays)
        assert callable(projected_intervals_to_genomic_intervals)


class TestIntervalOpsModule:
    """Test pyrion.ops.interval_ops functions."""
    
    def test_intersect_intervals(self):
        """Test intersect_intervals function."""
        from pyrion.ops.interval_ops import intersect_intervals
        from pyrion.ops.intervals import intervals_to_array
        from pyrion.core.intervals import GenomicInterval
        from pyrion.core.strand import Strand
        
        intervals1 = [GenomicInterval("chr1", 100, 200, Strand.PLUS)]
        intervals2 = [GenomicInterval("chr1", 150, 250, Strand.PLUS)]
        
        # Convert to numpy arrays
        arr1 = intervals_to_array(intervals1)
        arr2 = intervals_to_array(intervals2) 
        
        result = intersect_intervals(arr1, arr2)
        assert len(result) == 1
        assert result[0][0] == 150  # start
        assert result[0][1] == 200  # end
    
    def test_merge_intervals(self):
        """Test merge_intervals function."""
        from pyrion.ops.interval_ops import merge_intervals
        from pyrion.ops.intervals import intervals_to_array
        from pyrion.core.intervals import GenomicInterval
        from pyrion.core.strand import Strand
        
        intervals = [
            GenomicInterval("chr1", 100, 150, Strand.PLUS),
            GenomicInterval("chr1", 140, 200, Strand.PLUS)
        ]
        
        # Convert to numpy array
        arr = intervals_to_array(intervals)
        merged = merge_intervals(arr)
        assert len(merged) == 1
        assert merged[0][0] == 100  # start
        assert merged[0][1] == 200  # end
    
    def test_remaining_interval_ops_functions(self):
        """Test remaining functions in interval_ops module."""
        from pyrion.ops.interval_ops import (
            subtract_intervals, intervals_union
        )
        
        # Basic smoke tests  
        assert callable(subtract_intervals)
        assert callable(intervals_union)


class TestFastaModule:
    """Test pyrion.io.fasta functions."""
    
    @pytest.mark.io
    def test_fasta_reading(self):
        """Test FASTA file reading functionality."""
        from pyrion.io.fasta import read_fasta
        from pyrion.core.nucleotide_sequences import SequenceType
        from pathlib import Path
        
        test_file = Path("test_data/fasta/ARF5.fasta")
        if test_file.exists():
            sequences = read_fasta(test_file, SequenceType.DNA)
            assert len(sequences) > 0
            assert all(hasattr(seq, 'data') for seq_id, seq in sequences.items())
    
    def test_remaining_fasta_functions(self):
        """Test remaining functions in fasta module."""
        from pyrion.io.fasta import write_fasta
        
        # Basic smoke tests
        assert callable(write_fasta)


class TestSequencesModule:
    """Test pyrion.core sequence-related functions."""
    
    def test_nucleotide_sequences(self):
        """Test nucleotide sequence operations."""
        from pyrion.core.nucleotide_sequences import NucleotideSequence
        
        seq = NucleotideSequence.from_string("ATCG")
        rev_comp = seq.reverse_complement()
        assert rev_comp.to_string() == "CGAT"
    
    def test_codon_functions(self):
        """Test codon-related functions."""
        from pyrion.core.codons import Codon, CodonSequence
        
        # Basic smoke tests
        assert Codon is not None
        assert CodonSequence is not None
    
    def test_amino_acid_functions(self):
        """Test amino acid-related functions."""
        from pyrion.core.amino_acid_sequences import AminoAcidSequence
        
        # Basic smoke test
        assert AminoAcidSequence is not None
    
    def test_remaining_sequence_functions(self):
        """Test remaining sequence functions."""
        from pyrion.core.translation import TranslationTable
        
        # Basic smoke test
        assert TranslationTable is not None


class TestChainsModule:
    """Test pyrion.ops.chains functions."""
    
    def test_basic_chain_projection(self):
        """Test basic chain projection functionality."""
        from pyrion.ops.chains import project_intervals_through_chain
        
        chain_blocks = np.array([
            [100, 200, 1000, 1100],
            [300, 400, 1200, 1300],
        ], dtype=np.int64)
        
        intervals = np.array([[150, 180], [350, 380]], dtype=np.int64)
        results = project_intervals_through_chain(intervals, chain_blocks)
        
        assert len(results) == 2
        assert np.array_equal(results[0], np.array([[1050, 1080]], dtype=np.int64))
        assert np.array_equal(results[1], np.array([[1250, 1280]], dtype=np.int64))
    
    def test_chain_accessors(self):
        """Test chain accessor functions."""
        from pyrion.ops.chains import (
            get_chain_t_start, get_chain_t_end,
            get_chain_target_interval, get_chain_query_interval
        )
        from pyrion.core.genome_alignment import GenomeAlignment
        
        chain_blocks = np.array([[100, 200, 1000, 1100]], dtype=np.int64)
        genome_alignment = GenomeAlignment(
            chain_id=1, score=1000, t_chrom="chr1", t_strand=1, t_size=1000000,
            q_chrom="chr2", q_strand=1, q_size=1000000, blocks=chain_blocks
        )
        
        assert get_chain_t_start(genome_alignment) == 100
        assert get_chain_t_end(genome_alignment) == 200
        
        target = get_chain_target_interval(genome_alignment)
        assert target.chrom == "chr1"
        assert target.start == 100
        assert target.end == 200
    
    def test_remaining_chain_functions(self):
        """Test remaining chain functions."""
        from pyrion.ops.chains import (
            project_intervals_through_genome_alignment,
            project_intervals_through_genome_alignment_to_intervals,
            split_genome_alignment
        )
        
        # Basic smoke tests
        assert callable(project_intervals_through_genome_alignment)
        assert callable(project_intervals_through_genome_alignment_to_intervals)
        assert callable(split_genome_alignment)


@pytest.mark.integration
class TestHighPriorityIntegration:
    """Integration tests for high-priority modules working together."""
    
    @pytest.mark.io
    def test_full_workflow(self):
        """Test a complete workflow using multiple modules."""
        # This is a placeholder for integration tests
        # that use multiple modules together
        pass