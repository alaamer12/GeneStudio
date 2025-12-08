"""Suffix array construction and operations for GeneStudio."""

def build_suffix_array(text: str) -> list[int]:
    """
    Construct suffix array for a text string.
    
    Args:
        text: Input text
        
    Returns:
        Suffix array (list of starting indices sorted lexicographically)
    """
    if not text:
        return []
    
    # Create list of (suffix, index) tuples
    suffixes = [(text[i:], i) for i in range(len(text))]
    
    # Sort by suffix lexicographically
    suffixes.sort(key=lambda x: x[0])
    
    # Extract indices
    return [index for _, index in suffixes]


def inverse_suffix_array(sa: list[int]) -> list[int]:
    """
    Compute inverse suffix array from suffix array.
    
    Args:
        sa: Suffix array
        
    Returns:
        Inverse suffix array where ISA[SA[i]] = i
    """
    n = len(sa)
    isa = [0] * n
    
    for i in range(n):
        isa[sa[i]] = i
    
    return isa
