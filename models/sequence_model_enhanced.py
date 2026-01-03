"""Enhanced sequence data model with validation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import re


@dataclass
class Sequence:
    """Enhanced sequence model with validation."""
    
    id: Optional[int] = None
    project_id: int = 0
    header: str = ""
    sequence: str = ""
    sequence_type: str = "dna"  # dna, rna, protein
    length: int = 0
    gc_percentage: float = 0.0
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)
    file_path: Optional[str] = None  # For large sequences stored as files
    
    def __post_init__(self):
        """Validate and calculate sequence properties after initialization."""
        if self.sequence:
            self.length = len(self.sequence)
            if self.sequence_type == "dna":
                self.gc_percentage = self._calculate_gc_percentage()
        self.validate()
    
    def validate(self) -> None:
        """Validate sequence data."""
        if not self.header or not self.header.strip():
            raise ValueError("Sequence header cannot be empty")
        
        if len(self.header) > 500:
            raise ValueError("Sequence header cannot exceed 500 characters")
        
        valid_types = ["dna", "rna", "protein"]
        if self.sequence_type not in valid_types:
            raise ValueError(f"Sequence type must be one of: {valid_types}")
        
        if self.sequence:
            self._validate_sequence_content()
        
        if self.project_id <= 0:
            raise ValueError("Project ID must be positive")
        
        if self.gc_percentage < 0 or self.gc_percentage > 100:
            raise ValueError("GC percentage must be between 0 and 100")
    
    def _validate_sequence_content(self) -> None:
        """Validate sequence content based on type."""
        if not self.sequence:
            return
        
        sequence_upper = self.sequence.upper()
        
        if self.sequence_type == "dna":
            valid_chars = set("ATCGN")
            invalid_chars = set(sequence_upper) - valid_chars
            if invalid_chars:
                raise ValueError(f"Invalid DNA characters: {invalid_chars}")
        
        elif self.sequence_type == "rna":
            valid_chars = set("AUCGN")
            invalid_chars = set(sequence_upper) - valid_chars
            if invalid_chars:
                raise ValueError(f"Invalid RNA characters: {invalid_chars}")
        
        elif self.sequence_type == "protein":
            valid_chars = set("ACDEFGHIKLMNPQRSTVWYX*")
            invalid_chars = set(sequence_upper) - valid_chars
            if invalid_chars:
                raise ValueError(f"Invalid protein characters: {invalid_chars}")
    
    def _calculate_gc_percentage(self) -> float:
        """Calculate GC percentage for DNA sequences."""
        if not self.sequence or self.sequence_type != "dna":
            return 0.0
        
        sequence_upper = self.sequence.upper()
        gc_count = sequence_upper.count('G') + sequence_upper.count('C')
        total_count = len([c for c in sequence_upper if c in 'ATCG'])
        
        if total_count == 0:
            return 0.0
        
        return round((gc_count / total_count) * 100, 2)
    
    def get_reverse_complement(self) -> str:
        """Get reverse complement for DNA sequences."""
        if self.sequence_type != "dna":
            raise ValueError("Reverse complement only available for DNA sequences")
        
        complement_map = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
        complement = ''.join(complement_map.get(c.upper(), c) for c in self.sequence)
        return complement[::-1]
    
    def translate_to_protein(self, frame: int = 0) -> str:
        """Translate DNA/RNA sequence to protein."""
        if self.sequence_type not in ["dna", "rna"]:
            raise ValueError("Translation only available for DNA/RNA sequences")
        
        if frame < 0 or frame > 2:
            raise ValueError("Frame must be 0, 1, or 2")
        
        # Standard genetic code
        codon_table = {
            'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
            'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
            'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
            'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
            'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
            'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
            'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
            'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
            'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
            'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
            'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
            'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
            'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
            'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
        }
        
        # Convert RNA to DNA for codon table lookup
        sequence = self.sequence.upper().replace('U', 'T')
        
        # Extract sequence starting from frame
        sequence = sequence[frame:]
        
        # Translate codons
        protein = []
        for i in range(0, len(sequence) - 2, 3):
            codon = sequence[i:i+3]
            if len(codon) == 3:
                amino_acid = codon_table.get(codon, 'X')
                protein.append(amino_acid)
        
        return ''.join(protein)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert sequence to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'header': self.header,
            'sequence': self.sequence,
            'sequence_type': self.sequence_type,
            'length': self.length,
            'gc_percentage': self.gc_percentage,
            'notes': self.notes,
            'tags': ','.join(self.tags) if self.tags else '',
            'created_date': self.created_date.isoformat(),
            'file_path': self.file_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Sequence':
        """Create sequence from dictionary."""
        # Handle datetime conversion
        if isinstance(data.get('created_date'), str):
            data['created_date'] = datetime.fromisoformat(data['created_date'])
        
        # Handle tags conversion
        if isinstance(data.get('tags'), str):
            data['tags'] = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
        
        return cls(**data)
    
    def add_tag(self, tag: str):
        """Add a tag to the sequence."""
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag from the sequence."""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if sequence has a specific tag."""
        return tag in self.tags