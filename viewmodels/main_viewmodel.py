"""ViewModel for GeneStudio - Business logic and state management."""

from models.sequence_model import SequenceData, MatchResult, GraphData
import algorithms as alg


class MainViewModel:
    """Main ViewModel handling business logic for GeneStudio."""
    
    def __init__(self):
        """Initialize ViewModel."""
        self.sequences: list[SequenceData] = []
        self.current_sequence_index: int = 0
        self.last_match_result: MatchResult | None = None
        self.last_graph_result: GraphData | None = None
    
    # File Operations
    
    def load_fasta_file(self, filepath: str) -> tuple[bool, str]:
        """
        Load sequences from FASTA file.
        
        Returns:
            (success, message) tuple
        """
        try:
            sequences = alg.read_fasta(filepath)
            self.sequences = [SequenceData(header, seq) for header, seq in sequences]
            self.current_sequence_index = 0
            return True, f"Loaded {len(self.sequences)} sequence(s)"
        except Exception as e:
            return False, f"Error loading file: {str(e)}"
    
    def get_current_sequence(self) -> SequenceData | None:
        """Get currently selected sequence."""
        if 0 <= self.current_sequence_index < len(self.sequences):
            return self.sequences[self.current_sequence_index]
        return None
    
    def set_current_sequence(self, index: int):
        """Set current sequence by index."""
        if 0 <= index < len(self.sequences):
            self.current_sequence_index = index
    
    # Basic Operations
    
    def calculate_gc_percentage(self) -> tuple[bool, str]:
        """Calculate GC percentage for current sequence."""
        seq = self.get_current_sequence()
        if not seq:
            return False, "No sequence loaded"
        
        gc = alg.gc_percentage(seq.sequence)
        return True, f"GC%: {gc * 100:.2f}%"
    
    def get_reverse(self) -> tuple[bool, str]:
        """Get reverse of current sequence."""
        seq = self.get_current_sequence()
        if not seq:
            return False, "No sequence loaded"
        
        result = alg.reverse(seq.sequence)
        return True, result
    
    def get_complement(self) -> tuple[bool, str]:
        """Get complement of current sequence."""
        seq = self.get_current_sequence()
        if not seq:
            return False, "No sequence loaded"
        
        result = alg.complement(seq.sequence)
        return True, result
    
    def get_reverse_complement(self) -> tuple[bool, str]:
        """Get reverse complement of current sequence."""
        seq = self.get_current_sequence()
        if not seq:
            return False, "No sequence loaded"
        
        result = alg.reverse_complement(seq.sequence)
        return True, result
    
    # Translation
    
    def translate_sequence(self) -> tuple[bool, str]:
        """Translate current DNA sequence to amino acids."""
        seq = self.get_current_sequence()
        if not seq:
            return False, "No sequence loaded"
        
        result = alg.translate(seq.sequence)
        return True, result
    
    # Pattern Matching
    
    def search_boyer_moore_bad_char(self, pattern: str) -> tuple[bool, str]:
        """Search using Boyer-Moore bad character rule."""
        seq = self.get_current_sequence()
        if not seq:
            return False, "No sequence loaded"
        
        if not pattern:
            return False, "Pattern cannot be empty"
        
        pattern = pattern.upper()
        positions = alg.boyer_moore_bad_char(seq.sequence, pattern)
        self.last_match_result = MatchResult(pattern, positions, "Boyer-Moore (Bad Char)")
        
        return True, f"Found {len(positions)} match(es) at positions: {positions}"
    
    def search_boyer_moore_good_suffix(self, pattern: str) -> tuple[bool, str]:
        """Search using Boyer-Moore with good suffix rule."""
        seq = self.get_current_sequence()
        if not seq:
            return False, "No sequence loaded"
        
        if not pattern:
            return False, "Pattern cannot be empty"
        
        pattern = pattern.upper()
        positions = alg.boyer_moore_good_suffix(seq.sequence, pattern)
        self.last_match_result = MatchResult(pattern, positions, "Boyer-Moore (Good Suffix)")
        
        return True, f"Found {len(positions)} match(es) at positions: {positions}"
    
    # Suffix Array
    
    def build_suffix_array(self) -> tuple[bool, str]:
        """Build suffix array for current sequence."""
        seq = self.get_current_sequence()
        if not seq:
            return False, "No sequence loaded"
        
        sa = alg.build_suffix_array(seq.sequence)
        isa = alg.inverse_suffix_array(sa)
        
        result = f"Suffix Array (first 20): {sa[:20]}\n"
        result += f"Inverse Suffix Array (first 20): {isa[:20]}"
        
        return True, result
    
    # Overlap Graph
    
    def build_overlap_graph(self, min_overlap: int) -> tuple[bool, str]:
        """Build overlap graph from all loaded sequences."""
        if len(self.sequences) < 2:
            return False, "Need at least 2 sequences to build overlap graph"
        
        if min_overlap < 1:
            return False, "Minimum overlap must be at least 1"
        
        sequences = [seq.sequence for seq in self.sequences]
        graph = alg.build_overlap_graph(sequences, min_overlap)
        
        self.last_graph_result = GraphData(graph, min_overlap, len(sequences))
        
        # Format result
        result = f"Overlap Graph (min overlap: {min_overlap}):\n"
        for node, neighbors in graph.items():
            if neighbors:
                result += f"Seq {node} -> {neighbors}\n"
        
        if not any(graph.values()):
            result += "No overlaps found with given minimum overlap length"
        
        return True, result
    
    # Approximate Matching
    
    def search_hamming(self, pattern: str, max_distance: int) -> tuple[bool, str]:
        """Search using Hamming distance."""
        seq = self.get_current_sequence()
        if not seq:
            return False, "No sequence loaded"
        
        if not pattern:
            return False, "Pattern cannot be empty"
        
        pattern = pattern.upper()
        
        try:
            positions = alg.find_approximate_matches(seq.sequence, pattern, max_distance, 'hamming')
            self.last_match_result = MatchResult(pattern, positions, f"Hamming (d≤{max_distance})")
            return True, f"Found {len(positions)} match(es) at positions: {positions}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def search_edit_distance(self, pattern: str, max_distance: int) -> tuple[bool, str]:
        """Search using edit distance."""
        seq = self.get_current_sequence()
        if not seq:
            return False, "No sequence loaded"
        
        if not pattern:
            return False, "Pattern cannot be empty"
        
        pattern = pattern.upper()
        positions = alg.find_approximate_matches(seq.sequence, pattern, max_distance, 'edit')
        self.last_match_result = MatchResult(pattern, positions, f"Edit Distance (d≤{max_distance})")
        
        return True, f"Found {len(positions)} match(es) at positions: {positions}"
