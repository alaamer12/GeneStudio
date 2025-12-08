"""FASTA file reader for GeneStudio."""

def read_fasta(filepath: str) -> list[tuple[str, str]]:
    """
    Parse a FASTA file and return list of (header, sequence) tuples.
    
    Args:
        filepath: Path to FASTA file
        
    Returns:
        List of tuples containing (header, sequence)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    sequences = []
    current_header = None
    current_sequence = []
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('>'):
                    # Save previous sequence if exists
                    if current_header is not None:
                        seq = ''.join(current_sequence).upper()
                        if not _validate_dna(seq):
                            raise ValueError(f"Invalid DNA sequence for {current_header}")
                        sequences.append((current_header, seq))
                    
                    # Start new sequence
                    current_header = line[1:].strip()
                    current_sequence = []
                else:
                    current_sequence.append(line)
            
            # Save last sequence
            if current_header is not None:
                seq = ''.join(current_sequence).upper()
                if not _validate_dna(seq):
                    raise ValueError(f"Invalid DNA sequence for {current_header}")
                sequences.append((current_header, seq))
                
    except FileNotFoundError:
        raise FileNotFoundError(f"FASTA file not found: {filepath}")
    
    if not sequences:
        raise ValueError("No valid sequences found in FASTA file")
    
    return sequences


def _validate_dna(sequence: str) -> bool:
    """Validate that sequence contains only valid DNA characters."""
    valid_chars = set('ATCG')
    return all(c in valid_chars for c in sequence)
