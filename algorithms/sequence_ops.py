"""Basic DNA sequence operations for GeneStudio."""

def gc_percentage(seq: str) -> float:
    """
    Calculate GC percentage of a DNA sequence.
    
    Args:
        seq: DNA sequence string
        
    Returns:
        GC percentage as float (0.0 to 1.0)
    """
    if not seq:
        return 0.0
    
    seq = seq.upper()
    gc_count = sum(1 for base in seq if base in 'GC')
    return gc_count / len(seq)


def reverse(seq: str) -> str:
    """
    Reverse a DNA sequence.
    
    Args:
        seq: DNA sequence string
        
    Returns:
        Reversed sequence
    """
    return seq[::-1]


def complement(seq: str) -> str:
    """
    Get complement of a DNA sequence (A↔T, C↔G).
    
    Args:
        seq: DNA sequence string
        
    Returns:
        Complement sequence
    """
    complement_map = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    seq = seq.upper()
    return ''.join(complement_map.get(base, base) for base in seq)


def reverse_complement(seq: str) -> str:
    """
    Get reverse complement of a DNA sequence.
    
    Args:
        seq: DNA sequence string
        
    Returns:
        Reverse complement sequence
    """
    return reverse(complement(seq))
