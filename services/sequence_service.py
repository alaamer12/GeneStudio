"""Sequence service with FASTA import, validation, and metadata calculation."""

from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import time

from services.base_service import BaseService, ValidationError, ServiceError
from repositories.sequence_repository import SequenceRepository
from models.sequence_model_enhanced import Sequence
from algorithms import fasta_reader, sequence_ops


class SequenceService(BaseService[Sequence]):
    """Service for sequence management operations."""
    
    def __init__(self):
        """Initialize sequence service."""
        super().__init__(SequenceRepository())
        self.sequence_repository = self.repository
    
    def create_sequence(self, project_id: int, header: str, sequence: str, 
                       sequence_type: str = "dna", notes: str = "", 
                       tags: Optional[List[str]] = None) -> Tuple[bool, Sequence]:
        """Create a new sequence with validation and metadata calculation."""
        try:
            # Create sequence object
            seq_obj = Sequence(
                project_id=project_id,
                header=header.strip(),
                sequence=sequence.upper().strip(),
                sequence_type=sequence_type,
                notes=notes.strip(),
                tags=tags or []
            )
            
            # Validate sequence
            is_valid, error_msg = self.validate_sequence_data(seq_obj)
            if not is_valid:
                return False, error_msg
            
            return self.create_entity(seq_obj)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "create_sequence")
    
    def get_sequence(self, sequence_id: int) -> Tuple[bool, Optional[Sequence]]:
        """Get a sequence by ID."""
        return self.get_entity(sequence_id)
    
    def update_sequence(self, sequence: Sequence) -> Tuple[bool, bool]:
        """Update a sequence with validation."""
        try:
            # Validate sequence exists
            existing = self.sequence_repository.get_by_id(sequence.id)
            if not existing:
                return self.handle_not_found("Sequence", sequence.id)
            
            # Validate sequence data
            is_valid, error_msg = self.validate_sequence_data(sequence)
            if not is_valid:
                return False, error_msg
            
            return self.update_entity(sequence)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "update_sequence")
    
    def delete_sequence(self, sequence_id: int) -> Tuple[bool, bool]:
        """Delete a sequence and associated data."""
        return self.delete_entity(sequence_id)
    
    def list_sequences(self, filters: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[Sequence]]:
        """List sequences with optional filters."""
        def operation():
            return self.sequence_repository.list(filters)
        
        return self.execute_with_logging(operation, "list_sequences")
    
    def get_sequences_by_project(self, project_id: int) -> Tuple[bool, List[Sequence]]:
        """Get all sequences for a project."""
        def operation():
            return self.sequence_repository.get_by_project(project_id)
        
        return self.execute_with_logging(operation, "get_sequences_by_project")
    
    def import_fasta_file(self, filepath: str, project_id: int) -> Tuple[bool, List[Sequence]]:
        """Import sequences from a FASTA file."""
        def operation():
            # Validate file path
            file_path = Path(filepath)
            if not file_path.exists():
                raise ValidationError(f"FASTA file not found: {filepath}")
            
            if not file_path.suffix.lower() in ['.fasta', '.fa', '.fas', '.fna']:
                raise ValidationError("File must have a FASTA extension (.fasta, .fa, .fas, .fna)")
            
            # Check file size (limit to 100MB)
            file_size = file_path.stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB
                raise ValidationError("FASTA file is too large (max 100MB)")
            
            # Parse FASTA file
            try:
                sequences_data = fasta_reader.read_fasta(filepath)
            except Exception as e:
                raise ValidationError(f"Failed to parse FASTA file: {e}")
            
            if not sequences_data:
                raise ValidationError("No valid sequences found in FASTA file")
            
            # Create sequence objects
            imported_sequences = []
            for header, seq in sequences_data:
                try:
                    # Detect sequence type
                    seq_type = self._detect_sequence_type(seq)
                    
                    # Create sequence
                    sequence = Sequence(
                        project_id=project_id,
                        header=header,
                        sequence=seq,
                        sequence_type=seq_type
                    )
                    
                    # Save sequence
                    created_seq = self.sequence_repository.create(sequence)
                    imported_sequences.append(created_seq)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to import sequence '{header}': {e}")
                    continue
            
            if not imported_sequences:
                raise ServiceError("No sequences could be imported from the file")
            
            self.logger.info(f"Successfully imported {len(imported_sequences)} sequences from {filepath}")
            return imported_sequences
        
        return self.execute_with_logging(operation, "import_fasta_file")
    
    def export_sequences_to_fasta(self, sequence_ids: List[int], output_path: str) -> Tuple[bool, str]:
        """Export sequences to a FASTA file."""
        def operation():
            if not sequence_ids:
                raise ValidationError("No sequences specified for export")
            
            # Get sequences
            sequences = []
            for seq_id in sequence_ids:
                seq = self.sequence_repository.get_by_id(seq_id)
                if seq:
                    sequences.append(seq)
                else:
                    self.logger.warning(f"Sequence {seq_id} not found, skipping")
            
            if not sequences:
                raise ServiceError("No valid sequences found for export")
            
            # Write FASTA file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                for seq in sequences:
                    f.write(f">{seq.header}\n")
                    # Write sequence in 80-character lines
                    sequence_data = seq.sequence
                    for i in range(0, len(sequence_data), 80):
                        f.write(sequence_data[i:i+80] + '\n')
            
            self.logger.info(f"Exported {len(sequences)} sequences to {output_path}")
            return output_path
        
        return self.execute_with_logging(operation, "export_sequences_to_fasta")
    
    def search_sequences(self, search_term: str, project_id: Optional[int] = None) -> Tuple[bool, List[Sequence]]:
        """Search sequences by header or notes."""
        def operation():
            if not search_term or not search_term.strip():
                raise ValidationError("Search term cannot be empty")
            
            return self.sequence_repository.search_sequences(search_term.strip(), project_id)
        
        return self.execute_with_logging(operation, "search_sequences")
    
    def get_sequence_statistics(self, project_id: Optional[int] = None) -> Tuple[bool, Dict[str, Any]]:
        """Get sequence statistics."""
        def operation():
            return self.sequence_repository.get_sequence_statistics(project_id)
        
        return self.execute_with_logging(operation, "get_sequence_statistics")
    
    def calculate_sequence_properties(self, sequence: Sequence) -> Tuple[bool, Dict[str, Any]]:
        """Calculate additional properties for a sequence."""
        def operation():
            properties = {
                'length': sequence.length,
                'gc_percentage': sequence.gc_percentage
            }
            
            if sequence.sequence_type == "dna":
                # Calculate additional DNA properties
                seq = sequence.sequence.upper()
                
                # Base composition
                properties['base_composition'] = {
                    'A': seq.count('A'),
                    'T': seq.count('T'),
                    'C': seq.count('C'),
                    'G': seq.count('G'),
                    'N': seq.count('N')
                }
                
                # AT/GC ratio
                at_count = properties['base_composition']['A'] + properties['base_composition']['T']
                gc_count = properties['base_composition']['G'] + properties['base_composition']['C']
                if gc_count > 0:
                    properties['at_gc_ratio'] = at_count / gc_count
                else:
                    properties['at_gc_ratio'] = float('inf') if at_count > 0 else 0
                
                # Reverse complement
                try:
                    properties['reverse_complement'] = sequence.get_reverse_complement()
                except Exception as e:
                    self.logger.warning(f"Failed to calculate reverse complement: {e}")
                
                # Translation in all frames
                properties['translations'] = {}
                for frame in range(3):
                    try:
                        properties['translations'][f'frame_{frame}'] = sequence.translate_to_protein(frame)
                    except Exception as e:
                        self.logger.warning(f"Failed to translate frame {frame}: {e}")
            
            elif sequence.sequence_type == "protein":
                # Calculate protein properties
                seq = sequence.sequence.upper()
                
                # Amino acid composition
                amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
                properties['amino_acid_composition'] = {aa: seq.count(aa) for aa in amino_acids}
                
                # Molecular weight (approximate)
                aa_weights = {
                    'A': 89.1, 'C': 121.0, 'D': 133.1, 'E': 147.1, 'F': 165.2,
                    'G': 75.1, 'H': 155.2, 'I': 131.2, 'K': 146.2, 'L': 131.2,
                    'M': 149.2, 'N': 132.1, 'P': 115.1, 'Q': 146.2, 'R': 174.2,
                    'S': 105.1, 'T': 119.1, 'V': 117.1, 'W': 204.2, 'Y': 181.2
                }
                
                molecular_weight = sum(aa_weights.get(aa, 0) for aa in seq if aa != '*')
                properties['molecular_weight'] = molecular_weight
            
            return properties
        
        return self.execute_with_logging(operation, "calculate_sequence_properties")
    
    def get_sequences_by_tag(self, tag: str, project_id: Optional[int] = None) -> Tuple[bool, List[Sequence]]:
        """Get sequences by tag."""
        def operation():
            if not tag or not tag.strip():
                raise ValidationError("Tag cannot be empty")
            
            return self.sequence_repository.get_sequences_by_tag(tag.strip(), project_id)
        
        return self.execute_with_logging(operation, "get_sequences_by_tag")
    
    def add_tag_to_sequence(self, sequence_id: int, tag: str) -> Tuple[bool, bool]:
        """Add a tag to a sequence."""
        try:
            sequence = self.sequence_repository.get_by_id(sequence_id)
            if not sequence:
                return self.handle_not_found("Sequence", sequence_id)
            
            tag = tag.strip()
            if not tag:
                return False, "Tag cannot be empty"
            
            sequence.add_tag(tag)
            return self.update_entity(sequence)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "add_tag_to_sequence")
    
    def remove_tag_from_sequence(self, sequence_id: int, tag: str) -> Tuple[bool, bool]:
        """Remove a tag from a sequence."""
        try:
            sequence = self.sequence_repository.get_by_id(sequence_id)
            if not sequence:
                return self.handle_not_found("Sequence", sequence_id)
            
            sequence.remove_tag(tag.strip())
            return self.update_entity(sequence)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "remove_tag_from_sequence")
    
    def validate_sequence_data(self, sequence: Sequence) -> Tuple[bool, str]:
        """Validate sequence data with business rules."""
        try:
            # Basic model validation
            sequence.validate()
            
            # Business rule validations
            if len(sequence.header.strip()) < 1:
                return False, "Sequence header cannot be empty"
            
            if len(sequence.sequence) == 0:
                return False, "Sequence cannot be empty"
            
            if len(sequence.sequence) > 10000000:  # 10MB limit
                return False, "Sequence is too large (max 10 million characters)"
            
            # Validate sequence content based on type
            if sequence.sequence_type == "dna":
                invalid_chars = set(sequence.sequence.upper()) - set("ATCGN")
                if invalid_chars:
                    return False, f"Invalid DNA characters: {invalid_chars}"
            
            elif sequence.sequence_type == "rna":
                invalid_chars = set(sequence.sequence.upper()) - set("AUCGN")
                if invalid_chars:
                    return False, f"Invalid RNA characters: {invalid_chars}"
            
            elif sequence.sequence_type == "protein":
                invalid_chars = set(sequence.sequence.upper()) - set("ACDEFGHIKLMNPQRSTVWYX*")
                if invalid_chars:
                    return False, f"Invalid protein characters: {invalid_chars}"
            
            return True, ""
            
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            self.logger.error(f"Unexpected validation error: {e}")
            return False, f"Validation error: {e}"
    
    def _detect_sequence_type(self, sequence: str) -> str:
        """Detect sequence type based on content."""
        seq = sequence.upper()
        
        # Count different character types
        dna_chars = set("ATCG")
        rna_chars = set("AUCG")
        protein_chars = set("ACDEFGHIKLMNPQRSTVWY")
        
        dna_count = sum(1 for c in seq if c in dna_chars)
        rna_count = sum(1 for c in seq if c in rna_chars)
        protein_count = sum(1 for c in seq if c in protein_chars)
        
        total_chars = len(seq)
        
        # Calculate percentages
        dna_pct = dna_count / total_chars if total_chars > 0 else 0
        rna_pct = rna_count / total_chars if total_chars > 0 else 0
        protein_pct = protein_count / total_chars if total_chars > 0 else 0
        
        # Decision logic
        if 'U' in seq and 'T' not in seq and rna_pct > 0.8:
            return "rna"
        elif dna_pct > 0.8:
            return "dna"
        elif protein_pct > 0.6:
            return "protein"
        else:
            # Default to DNA for ambiguous cases
            return "dna"
    
    def get_sequence_summary(self, sequence_id: int) -> Tuple[bool, Dict[str, Any]]:
        """Get a summary of sequence information."""
        try:
            sequence = self.sequence_repository.get_by_id(sequence_id)
            if not sequence:
                return self.handle_not_found("Sequence", sequence_id)
            
            summary = {
                'id': sequence.id,
                'header': sequence.header,
                'sequence_type': sequence.sequence_type,
                'length': sequence.length,
                'gc_percentage': sequence.gc_percentage,
                'tag_count': len(sequence.tags),
                'has_notes': bool(sequence.notes),
                'created_date': sequence.created_date,
                'stored_in_file': bool(sequence.file_path)
            }
            
            return True, summary
            
        except Exception as e:
            return self.handle_unexpected_error(e, "get_sequence_summary")