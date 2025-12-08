"""Overlap graph construction for GeneStudio."""

def build_overlap_graph(sequences: list[str], min_overlap: int) -> dict:
    """
    Build overlap graph from sequences based on suffix-prefix overlaps.
    
    Args:
        sequences: List of DNA sequences
        min_overlap: Minimum overlap length required
        
    Returns:
        Adjacency list representation as dict {seq_index: [overlapping_seq_indices]}
    """
    n = len(sequences)
    graph = {i: [] for i in range(n)}
    
    # Check all pairs for overlaps
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            
            overlap_len = _find_overlap(sequences[i], sequences[j], min_overlap)
            if overlap_len >= min_overlap:
                graph[i].append(j)
    
    return graph


def _find_overlap(s1: str, s2: str, min_length: int) -> int:
    """
    Find the length of suffix-prefix overlap between two sequences.
    
    Args:
        s1: First sequence (check suffix)
        s2: Second sequence (check prefix)
        min_length: Minimum overlap to consider
        
    Returns:
        Length of overlap (0 if no valid overlap)
    """
    max_overlap = min(len(s1), len(s2))
    
    # Check from longest possible overlap down to min_length
    for overlap_len in range(max_overlap, min_length - 1, -1):
        if s1[-overlap_len:] == s2[:overlap_len]:
            return overlap_len
    
    return 0
