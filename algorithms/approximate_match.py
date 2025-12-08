"""Approximate pattern matching algorithms for GeneStudio."""

def hamming_distance(s1: str, s2: str) -> int:
    """
    Calculate Hamming distance between two strings (bonus).
    Strings must be of equal length.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Number of positions where characters differ
        
    Raises:
        ValueError: If strings have different lengths
    """
    if len(s1) != len(s2):
        raise ValueError("Strings must have equal length for Hamming distance")
    
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def edit_distance(s1: str, s2: str) -> int:
    """
    Calculate edit distance (Levenshtein distance) using dynamic programming.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Minimum number of edits (insertions, deletions, substitutions)
    """
    m, n = len(s1), len(s2)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1
            
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Deletion
                dp[i][j - 1] + 1,      # Insertion
                dp[i - 1][j - 1] + cost  # Substitution
            )
    
    return dp[m][n]


def find_approximate_matches(text: str, pattern: str, max_dist: int, method: str = 'edit') -> list[int]:
    """
    Find all approximate matches of pattern in text within distance threshold.
    
    Args:
        text: Text to search in
        pattern: Pattern to search for
        max_dist: Maximum distance threshold
        method: 'hamming' or 'edit' distance
        
    Returns:
        List of starting positions where pattern matches within threshold
    """
    matches = []
    n = len(text)
    m = len(pattern)
    
    if method == 'hamming':
        # Hamming distance requires equal length
        for i in range(n - m + 1):
            substring = text[i:i + m]
            if hamming_distance(substring, pattern) <= max_dist:
                matches.append(i)
    else:  # edit distance
        for i in range(n - m + 1):
            # Check various window sizes around pattern length
            for window_size in range(max(1, m - max_dist), min(n - i, m + max_dist) + 1):
                substring = text[i:i + window_size]
                if edit_distance(substring, pattern) <= max_dist:
                    matches.append(i)
                    break
    
    return matches
