"""Comprehensive tests for all algorithms in GeneStudio."""

import pytest
import tempfile
import os
from algorithms.approximate_match import hamming_distance, edit_distance, find_approximate_matches
from algorithms.boyer_moore import boyer_moore_bad_char, boyer_moore_good_suffix
from algorithms.fasta_reader import read_fasta
from algorithms.overlap_graph import build_overlap_graph
from algorithms.sequence_ops import gc_percentage, reverse, complement, reverse_complement
from algorithms.suffix_array import build_suffix_array, inverse_suffix_array
from algorithms.translation import translate, CODON_TABLE


class TestApproximateMatch:
    """Test approximate matching algorithms."""
    
    def test_hamming_distance(self):
        """Test Hamming distance calculation."""
        # Equal strings
        assert hamming_distance("ATCG", "ATCG") == 0
        
        # Single difference
        assert hamming_distance("ATCG", "ATCC") == 1
        
        # Multiple differences
        assert hamming_distance("ATCG", "CGTA") == 4
        
        # Empty strings
        assert hamming_distance("", "") == 0
        
        # Different lengths should raise error
        with pytest.raises(ValueError):
            hamming_distance("ATCG", "ATC")
    
    def test_edit_distance(self):
        """Test edit distance (Levenshtein) calculation."""
        # Equal strings
        assert edit_distance("ATCG", "ATCG") == 0
        
        # Single insertion
        assert edit_distance("ATC", "ATCG") == 1
        
        # Single deletion
        assert edit_distance("ATCG", "ATC") == 1
        
        # Single substitution
        assert edit_distance("ATCG", "ATCC") == 1
        
        # Complex case
        assert edit_distance("KITTEN", "SITTING") == 3
        
        # Empty strings
        assert edit_distance("", "") == 0
        assert edit_distance("ABC", "") == 3
        assert edit_distance("", "ABC") == 3
    
    def test_find_approximate_matches(self):
        """Test finding approximate matches."""
        text = "ATCGATCGATCG"
        pattern = "ATC"
        
        # Exact matches with hamming distance
        matches = find_approximate_matches(text, pattern, 0, "hamming")
        assert matches == [0, 4, 8]
        
        # Approximate matches with edit distance
        matches = find_approximate_matches(text, pattern, 1, "edit")
        assert len(matches) > 0
        
        # No matches with strict threshold
        matches = find_approximate_matches("GGGGGG", "ATC", 0, "hamming")
        assert matches == []


class TestBoyerMoore:
    """Test Boyer-Moore pattern matching algorithms."""
    
    def test_boyer_moore_bad_char(self):
        """Test Boyer-Moore with bad character rule."""
        # Simple exact match
        matches = boyer_moore_bad_char("ATCGATCG", "ATC")
        assert matches == [0, 4]
        
        # No matches
        matches = boyer_moore_bad_char("GGGGGG", "ATC")
        assert matches == []
        
        # Single character pattern
        matches = boyer_moore_bad_char("AAABAA", "A")
        assert matches == [0, 1, 2, 4, 5]
        
        # Empty inputs
        assert boyer_moore_bad_char("", "ATC") == []
        assert boyer_moore_bad_char("ATC", "") == []
    
    def test_boyer_moore_good_suffix(self):
        """Test Boyer-Moore with good suffix rule."""
        # Simple exact match
        matches = boyer_moore_good_suffix("ATCGATCG", "ATC")
        assert matches == [0, 4]
        
        # Pattern with repeating suffix
        matches = boyer_moore_good_suffix("ABCABCABC", "ABC")
        assert matches == [0, 3, 6]
        
        # No matches
        matches = boyer_moore_good_suffix("GGGGGG", "ATC")
        assert matches == []


class TestFastaReader:
    """Test FASTA file reading functionality."""
    
    def test_read_fasta_valid(self):
        """Test reading valid FASTA file."""
        fasta_content = """>seq1
ATCGATCG
>seq2
GCTAGCTA
GCGCGCGC
>seq3
TTTTAAAA"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(fasta_content)
            temp_path = f.name
        
        try:
            sequences = read_fasta(temp_path)
            assert len(sequences) == 3
            assert sequences[0] == ("seq1", "ATCGATCG")
            assert sequences[1] == ("seq2", "GCTAGCTAGCGCGCGC")
            assert sequences[2] == ("seq3", "TTTTAAAA")
        finally:
            os.unlink(temp_path)
    
    def test_read_fasta_invalid_sequence(self):
        """Test reading FASTA with invalid DNA characters."""
        fasta_content = """>seq1
ATCGXYZ"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(fasta_content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid DNA sequence"):
                read_fasta(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_read_fasta_file_not_found(self):
        """Test reading non-existent FASTA file."""
        with pytest.raises(FileNotFoundError):
            read_fasta("nonexistent.fasta")


class TestOverlapGraph:
    """Test overlap graph construction."""
    
    def test_build_overlap_graph(self):
        """Test building overlap graph from sequences."""
        sequences = ["ATCGATCG", "TCGATCGA", "GATCGATT"]
        graph = build_overlap_graph(sequences, 3)
        
        # Check that overlaps are detected correctly
        assert isinstance(graph, dict)
        assert len(graph) == 3
        
        # Verify specific overlaps
        # seq0 "ATCGATCG" suffix "TCG" matches seq1 "TCGATCGA" prefix "TCG"
        assert 1 in graph[0]
    
    def test_build_overlap_graph_no_overlaps(self):
        """Test overlap graph with no valid overlaps."""
        sequences = ["AAAA", "TTTT", "CCCC"]
        graph = build_overlap_graph(sequences, 2)
        
        # No overlaps should be found
        for neighbors in graph.values():
            assert len(neighbors) == 0
    
    def test_build_overlap_graph_empty(self):
        """Test overlap graph with empty input."""
        graph = build_overlap_graph([], 3)
        assert graph == {}


class TestSequenceOps:
    """Test basic DNA sequence operations."""
    
    def test_gc_percentage(self):
        """Test GC percentage calculation."""
        # 50% GC content
        assert gc_percentage("ATCG") == 0.5
        
        # 100% GC content
        assert gc_percentage("GCGC") == 1.0
        
        # 0% GC content
        assert gc_percentage("ATAT") == 0.0
        
        # Empty sequence
        assert gc_percentage("") == 0.0
        
        # Case insensitive
        assert gc_percentage("atcg") == 0.5
    
    def test_reverse(self):
        """Test sequence reversal."""
        assert reverse("ATCG") == "GCTA"
        assert reverse("") == ""
        assert reverse("A") == "A"
    
    def test_complement(self):
        """Test DNA complement."""
        assert complement("ATCG") == "TAGC"
        assert complement("") == ""
        assert complement("atcg") == "TAGC"  # Should handle lowercase
    
    def test_reverse_complement(self):
        """Test reverse complement."""
        assert reverse_complement("ATCG") == "CGAT"
        assert reverse_complement("") == ""
        
        # Verify it's actually reverse of complement
        seq = "ATCGATCG"
        assert reverse_complement(seq) == reverse(complement(seq))


class TestSuffixArray:
    """Test suffix array construction and operations."""
    
    def test_build_suffix_array(self):
        """Test suffix array construction."""
        # Simple case
        sa = build_suffix_array("banana")
        assert len(sa) == 6
        assert all(isinstance(i, int) for i in sa)
        
        # Empty string
        assert build_suffix_array("") == []
        
        # Single character
        assert build_suffix_array("a") == [0]
    
    def test_inverse_suffix_array(self):
        """Test inverse suffix array computation."""
        text = "banana"
        sa = build_suffix_array(text)
        isa = inverse_suffix_array(sa)
        
        # Verify ISA[SA[i]] = i property
        for i in range(len(sa)):
            assert isa[sa[i]] == i
        
        # Verify SA[ISA[i]] = i property
        for i in range(len(isa)):
            assert sa[isa[i]] == i


class TestTranslation:
    """Test DNA to amino acid translation."""
    
    def test_translate_basic(self):
        """Test basic DNA translation."""
        # Start codon ATG -> M
        assert translate("ATG") == "M"
        
        # Stop codon TAA -> *
        assert translate("TAA") == "*"
        
        # Multiple codons
        assert translate("ATGAAATAG") == "MK*"
        
        # Case insensitive
        assert translate("atg") == "M"
    
    def test_translate_incomplete_codon(self):
        """Test translation with incomplete final codon."""
        # Should only translate complete codons
        assert translate("ATGAA") == "M"  # Only ATG is complete
        assert translate("AT") == ""      # No complete codons
    
    def test_translate_unknown_codon(self):
        """Test translation with unknown codon."""
        # Invalid codon should return 'X'
        assert translate("XYZ") == "X"
    
    def test_codon_table_completeness(self):
        """Test that codon table has all 64 codons."""
        bases = ['A', 'T', 'C', 'G']
        expected_codons = set()
        
        for b1 in bases:
            for b2 in bases:
                for b3 in bases:
                    expected_codons.add(b1 + b2 + b3)
        
        assert len(CODON_TABLE) == 64
        assert set(CODON_TABLE.keys()) == expected_codons


if __name__ == "__main__":
    pytest.main([__file__])