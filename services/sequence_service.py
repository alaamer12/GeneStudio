"""Sequence service with FASTA import, validation, and metadata calculation."""

from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import time

from services.base_service import BaseService, ValidationError, ServiceError
from repositories.sequence_repository import SequenceRepository
from models.sequence_model_enhanced import Sequence
from algorithms import fasta_reader, sequence_ops
from utils.cache_manager import get_cache_manager, cached
from utils.resource_manager import get_memory_manager, StreamingProcessor
from utils.search_engine import get_search_engine


class SequenceService(BaseService[Sequence]):
    """Service for sequence management operations."""
    
    def __init__(self):
        """Initialize sequence service."""
        super().__init__(SequenceRepository())
        self.sequence_repository = self.repository
        self.cache_manager = get_cache_manager()
        self.memory_manager = get_memory_manager()
        self.search_engine = get_search_engine()
        self.streaming_processor = StreamingProcessor(memory_manager=self.memory_manager)
    
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
    
    def import_sequences_from_files(self, file_paths: List[str], project_id: int, 
                                   import_options: Dict[str, Any] = None) -> Tuple[bool, List[Sequence]]:
        """Import sequences from multiple files with format validation."""
        def operation():
            import_options = import_options or {}
            all_imported_sequences = []
            
            for file_path in file_paths:
                try:
                    # Validate and import single file
                    success, sequences = self._import_single_file(file_path, project_id, import_options)
                    if success:
                        all_imported_sequences.extend(sequences)
                    else:
                        self.logger.warning(f"Failed to import {file_path}: {sequences}")
                except Exception as e:
                    self.logger.error(f"Error importing {file_path}: {e}")
                    continue
            
            if not all_imported_sequences:
                raise ServiceError("No sequences could be imported from any file")
            
            self.logger.info(f"Successfully imported {len(all_imported_sequences)} sequences from {len(file_paths)} files")
            return all_imported_sequences
        
        return self.execute_with_logging(operation, "import_sequences_from_files")
    
    def import_fasta_file(self, filepath: str, project_id: int) -> Tuple[bool, List[Sequence]]:
        """Import sequences from a single FASTA file."""
        return self._import_single_file(filepath, project_id, {})
    
    def _import_single_file(self, filepath: str, project_id: int, 
                           import_options: Dict[str, Any]) -> Tuple[bool, List[Sequence]]:
        """Import sequences from a single file with format validation and streaming support."""
        try:
            # Validate file path
            file_path = Path(filepath)
            if not file_path.exists():
                return False, f"File not found: {filepath}"
            
            # Validate file format
            format_validation = self._validate_file_format(file_path)
            if not format_validation['is_valid']:
                return False, format_validation['error']
            
            file_format = format_validation['format']
            
            # Check file size limits
            file_size = file_path.stat().st_size
            max_size = import_options.get('max_file_size', 100 * 1024 * 1024)  # 100MB default
            use_streaming = file_size > 10 * 1024 * 1024  # Use streaming for files > 10MB
            
            if file_size > max_size:
                return False, f"File is too large (max {max_size // (1024*1024)}MB)"
            
            # Parse file based on format
            if file_format in ['fasta', 'multi-fasta']:
                if use_streaming:
                    return self._import_fasta_streaming(file_path, project_id, import_options)
                else:
                    sequences_data = self._parse_fasta_file(file_path, import_options)
            else:
                return False, f"Unsupported file format: {file_format}"
            
            if not sequences_data:
                return False, "No valid sequences found in file"
            
            # Create and save sequence objects
            imported_sequences = []
            total_sequences = len(sequences_data)
            
            for i, (header, seq) in enumerate(sequences_data):
                try:
                    # Memory management for large imports
                    if i % 100 == 0:
                        self.memory_manager.auto_manage_memory()
                    
                    # Apply import options
                    if import_options.get('skip_duplicates', False):
                        # Check for duplicate headers in project
                        existing = self.sequence_repository.get_by_header(header, project_id)
                        if existing:
                            self.logger.info(f"Skipping duplicate sequence: {header}")
                            continue
                    
                    # Detect or override sequence type
                    if import_options.get('force_sequence_type'):
                        seq_type = import_options['force_sequence_type']
                    else:
                        seq_type = self._detect_sequence_type(seq)
                    
                    # Apply sequence transformations
                    processed_seq = self._process_sequence(seq, import_options)
                    
                    # Create sequence object
                    sequence = Sequence(
                        project_id=project_id,
                        header=header,
                        sequence=processed_seq,
                        sequence_type=seq_type,
                        notes=import_options.get('default_notes', ''),
                        tags=import_options.get('default_tags', [])
                    )
                    
                    # Validate sequence
                    is_valid, error_msg = self.validate_sequence_data(sequence)
                    if not is_valid:
                        self.logger.warning(f"Invalid sequence '{header}': {error_msg}")
                        if not import_options.get('skip_invalid', True):
                            return False, f"Invalid sequence '{header}': {error_msg}"
                        continue
                    
                    # Save sequence
                    created_seq = self.sequence_repository.create(sequence)
                    imported_sequences.append(created_seq)
                    
                    # Update search index
                    self._update_search_index(created_seq)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to import sequence '{header}': {e}")
                    if not import_options.get('continue_on_error', True):
                        return False, f"Failed to import sequence '{header}': {e}"
                    continue
            
            if not imported_sequences:
                return False, "No sequences could be imported from the file"
            
            self.logger.info(f"Successfully imported {len(imported_sequences)} sequences from {filepath}")
            return True, imported_sequences
            
        except Exception as e:
            self.logger.error(f"Unexpected error importing {filepath}: {e}")
            return False, f"Import failed: {e}"
    
    def _import_fasta_streaming(self, file_path: Path, project_id: int, 
                               import_options: Dict[str, Any]) -> Tuple[bool, List[Sequence]]:
        """Import FASTA file using streaming for large files."""
        try:
            imported_sequences = []
            current_header = None
            current_sequence = []
            sequence_count = 0
            
            def process_sequence(header: str, sequence: str) -> Optional[Sequence]:
                """Process a single sequence."""
                try:
                    # Apply import options
                    if import_options.get('skip_duplicates', False):
                        existing = self.sequence_repository.get_by_header(header, project_id)
                        if existing:
                            return None
                    
                    # Detect sequence type
                    if import_options.get('force_sequence_type'):
                        seq_type = import_options['force_sequence_type']
                    else:
                        seq_type = self._detect_sequence_type(sequence)
                    
                    # Process sequence
                    processed_seq = self._process_sequence(sequence, import_options)
                    
                    # Create sequence object
                    seq_obj = Sequence(
                        project_id=project_id,
                        header=header,
                        sequence=processed_seq,
                        sequence_type=seq_type,
                        notes=import_options.get('default_notes', ''),
                        tags=import_options.get('default_tags', [])
                    )
                    
                    # Validate
                    is_valid, error_msg = self.validate_sequence_data(seq_obj)
                    if not is_valid:
                        self.logger.warning(f"Invalid sequence '{header}': {error_msg}")
                        return None
                    
                    # Save
                    created_seq = self.sequence_repository.create(seq_obj)
                    self._update_search_index(created_seq)
                    
                    return created_seq
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process sequence '{header}': {e}")
                    return None
            
            # Stream process the file
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    if line.startswith('>'):
                        # Process previous sequence if exists
                        if current_header and current_sequence:
                            seq_data = ''.join(current_sequence)
                            result = process_sequence(current_header, seq_data)
                            if result:
                                imported_sequences.append(result)
                                sequence_count += 1
                        
                        # Start new sequence
                        current_header = line[1:]  # Remove '>'
                        current_sequence = []
                        
                        # Memory management
                        if sequence_count % 50 == 0:
                            self.memory_manager.auto_manage_memory()
                    
                    elif line and current_header:
                        current_sequence.append(line)
                
                # Process last sequence
                if current_header and current_sequence:
                    seq_data = ''.join(current_sequence)
                    result = process_sequence(current_header, seq_data)
                    if result:
                        imported_sequences.append(result)
            
            if not imported_sequences:
                return False, "No sequences could be imported from the file"
            
            self.logger.info(f"Successfully streamed import of {len(imported_sequences)} sequences from {file_path}")
            return True, imported_sequences
            
        except Exception as e:
            self.logger.error(f"Streaming import failed for {file_path}: {e}")
            return False, f"Streaming import failed: {e}"
    
    def _update_search_index(self, sequence: Sequence):
        """Update search index with new sequence."""
        try:
            search_data = {
                'id': sequence.id,
                'title': sequence.header,
                'content': f"{sequence.header} {sequence.notes} {' '.join(sequence.tags)}",
                'sequence_type': sequence.sequence_type,
                'length': sequence.length,
                'created_date': sequence.created_date
            }
            
            self.search_engine.update_index('sequence', str(sequence.id), search_data)
            
        except Exception as e:
            self.logger.warning(f"Failed to update search index for sequence {sequence.id}: {e}")
    
    def _validate_file_format(self, file_path: Path) -> Dict[str, Any]:
        """Validate file format and return format information."""
        try:
            # Check file extension
            extension = file_path.suffix.lower()
            
            # Supported FASTA extensions
            fasta_extensions = ['.fasta', '.fa', '.fas', '.fna', '.ffn', '.faa', '.frn']
            
            if extension in fasta_extensions:
                # Validate FASTA content
                return self._validate_fasta_content(file_path)
            else:
                return {
                    'is_valid': False,
                    'error': f"Unsupported file extension: {extension}. Supported: {', '.join(fasta_extensions)}",
                    'format': None
                }
        
        except Exception as e:
            return {
                'is_valid': False,
                'error': f"File validation error: {e}",
                'format': None
            }
    
    def _validate_fasta_content(self, file_path: Path) -> Dict[str, Any]:
        """Validate FASTA file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read first few lines to validate format
                lines = []
                for i, line in enumerate(f):
                    lines.append(line.strip())
                    if i >= 10:  # Check first 10 lines
                        break
            
            if not lines:
                return {
                    'is_valid': False,
                    'error': "File is empty",
                    'format': None
                }
            
            # Check for FASTA header
            has_header = False
            sequence_count = 0
            
            for line in lines:
                if line.startswith('>'):
                    has_header = True
                    sequence_count += 1
                elif line and not line.startswith('>') and has_header:
                    # Validate sequence characters
                    if not self._is_valid_sequence_line(line):
                        return {
                            'is_valid': False,
                            'error': f"Invalid sequence characters in line: {line[:50]}...",
                            'format': None
                        }
            
            if not has_header:
                return {
                    'is_valid': False,
                    'error': "No FASTA headers found (lines starting with '>')",
                    'format': None
                }
            
            format_type = 'multi-fasta' if sequence_count > 1 else 'fasta'
            
            return {
                'is_valid': True,
                'error': None,
                'format': format_type,
                'sequence_count': sequence_count
            }
        
        except UnicodeDecodeError:
            return {
                'is_valid': False,
                'error': "File encoding error. Please ensure file is UTF-8 encoded.",
                'format': None
            }
        except Exception as e:
            return {
                'is_valid': False,
                'error': f"Content validation error: {e}",
                'format': None
            }
    
    def _is_valid_sequence_line(self, line: str) -> bool:
        """Check if a line contains valid sequence characters."""
        # Allow common sequence characters and whitespace
        valid_chars = set('ATCGRYSWKMBDHVN-.*atcgryswkmbdhvn ')
        return all(c in valid_chars for c in line)
    
    def _parse_fasta_file(self, file_path: Path, import_options: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Parse FASTA file with import options."""
        try:
            sequences_data = fasta_reader.read_fasta(str(file_path))
            
            # Apply import filters
            if import_options.get('min_length'):
                min_len = import_options['min_length']
                sequences_data = [(h, s) for h, s in sequences_data if len(s) >= min_len]
            
            if import_options.get('max_length'):
                max_len = import_options['max_length']
                sequences_data = [(h, s) for h, s in sequences_data if len(s) <= max_len]
            
            if import_options.get('header_filter'):
                header_pattern = import_options['header_filter']
                import re
                sequences_data = [(h, s) for h, s in sequences_data if re.search(header_pattern, h)]
            
            return sequences_data
            
        except Exception as e:
            raise ValidationError(f"Failed to parse FASTA file: {e}")
    
    def _process_sequence(self, sequence: str, import_options: Dict[str, Any]) -> str:
        """Process sequence based on import options."""
        processed_seq = sequence
        
        # Remove whitespace and newlines
        processed_seq = ''.join(processed_seq.split())
        
        # Convert to uppercase if requested
        if import_options.get('uppercase', True):
            processed_seq = processed_seq.upper()
        
        # Remove invalid characters if requested
        if import_options.get('clean_sequence', False):
            valid_chars = set('ATCGRYSWKMBDHVN')
            processed_seq = ''.join(c for c in processed_seq if c in valid_chars)
        
        # Replace ambiguous characters if requested
        if import_options.get('replace_ambiguous', False):
            replacements = import_options.get('ambiguous_replacements', {'N': 'A'})
            for old_char, new_char in replacements.items():
                processed_seq = processed_seq.replace(old_char, new_char)
        
        return processed_seq
    
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
    
    @cached(ttl=3600)  # Cache for 1 hour
    def calculate_sequence_properties(self, sequence: Sequence) -> Tuple[bool, Dict[str, Any]]:
        """Calculate additional properties for a sequence."""
        def operation():
            # Check cache first using sequence hash as key
            cache_key = f"seq_props_{sequence.id}_{hash(sequence.sequence)}"
            cached_props = self.cache_manager.get(cache_key)
            
            if cached_props is not None:
                return cached_props
            
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
            
            # Cache the result
            self.cache_manager.put(cache_key, properties, ttl=3600)
            
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