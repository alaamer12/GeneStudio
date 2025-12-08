"""Boyer-Moore pattern matching algorithms for GeneStudio."""

def boyer_moore_bad_char(text: str, pattern: str) -> list[int]:
    """
    Boyer-Moore pattern matching using bad character rule.
    
    Args:
        text: Text to search in
        pattern: Pattern to search for
        
    Returns:
        List of starting positions where pattern is found
    """
    if not pattern or not text:
        return []
    
    matches = []
    n = len(text)
    m = len(pattern)
    
    # Build bad character table
    bad_char = _build_bad_char_table(pattern)
    
    # Search
    s = 0  # shift of pattern relative to text
    while s <= n - m:
        j = m - 1
        
        # Keep reducing j while characters match
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        
        if j < 0:
            # Pattern found
            matches.append(s)
            # Shift pattern to align with next character
            s += (m - bad_char.get(text[s + m], -1) - 1) if s + m < n else 1
        else:
            # Shift pattern using bad character rule
            s += max(1, j - bad_char.get(text[s + j], -1))
    
    return matches


def boyer_moore_good_suffix(text: str, pattern: str) -> list[int]:
    """
    Boyer-Moore pattern matching using both bad character and good suffix rules (bonus).
    
    Args:
        text: Text to search in
        pattern: Pattern to search for
        
    Returns:
        List of starting positions where pattern is found
    """
    if not pattern or not text:
        return []
    
    matches = []
    n = len(text)
    m = len(pattern)
    
    # Build tables
    bad_char = _build_bad_char_table(pattern)
    good_suffix = _build_good_suffix_table(pattern)
    
    # Search
    s = 0
    while s <= n - m:
        j = m - 1
        
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        
        if j < 0:
            matches.append(s)
            s += good_suffix[0]
        else:
            # Use maximum shift from both rules
            bad_char_shift = j - bad_char.get(text[s + j], -1)
            good_suffix_shift = good_suffix[j + 1]
            s += max(bad_char_shift, good_suffix_shift)
    
    return matches


def _build_bad_char_table(pattern: str) -> dict:
    """Build bad character shift table."""
    table = {}
    for i in range(len(pattern) - 1):
        table[pattern[i]] = i
    return table


def _build_good_suffix_table(pattern: str) -> list[int]:
    """Build good suffix shift table."""
    m = len(pattern)
    shift = [0] * (m + 1)
    border = [0] * (m + 1)
    
    # Preprocessing
    i = m
    j = m + 1
    border[i] = j
    
    while i > 0:
        while j <= m and pattern[i - 1] != pattern[j - 1]:
            if shift[j] == 0:
                shift[j] = j - i
            j = border[j]
        i -= 1
        j -= 1
        border[i] = j
    
    # Fill remaining entries
    j = border[0]
    for i in range(m + 1):
        if shift[i] == 0:
            shift[i] = j
        if i == j:
            j = border[j]
    
    return shift
