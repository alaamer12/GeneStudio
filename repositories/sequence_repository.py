"""Sequence repository with CRUD operations and metadata handling."""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json

from repositories.base_repository import BaseRepository, RepositoryError
from models.sequence_model_enhanced import Sequence


class SequenceRepository(BaseRepository[Sequence]):
    """Repository for sequence data access operations."""
    
    def __init__(self):
        """Initialize sequence repository."""
        super().__init__()
        self.data_dir = Path("data/sequences")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def create(self, sequence: Sequence) -> Sequence:
        """Create a new sequence."""
        try:
            # Prepare data for insertion
            data = sequence.to_dict()
            data.pop('id', None)  # Remove ID for auto-generation
            
            # Get next ID
            conn = self.db_manager.get_connection()
            result = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM sequences").fetchall()
            next_id = result[0][0]
            
            # Insert sequence metadata
            query = """
                INSERT INTO sequences (id, project_id, header, sequence, sequence_type, 
                                     length, gc_percentage, notes, tags, file_path, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                next_id, data['project_id'], data['header'], data['sequence'],
                data['sequence_type'], data['length'], data['gc_percentage'],
                data['notes'], data['tags'], data['file_path'], data['created_date']
            )
            
            conn.execute(query, params)
            sequence.id = next_id
            
            # For large sequences, store in file and update file_path
            if len(sequence.sequence) > 10000:  # Store sequences > 10KB in files
                file_path = self._store_sequence_file(sequence)
                sequence.file_path = str(file_path)
                
                # Update file path in database and clear sequence data
                update_query = "UPDATE sequences SET file_path = ?, sequence = '' WHERE id = ?"
                self._execute_query(update_query, (str(file_path), sequence.id))
            
            # Log activity
            self._log_activity("create", "sequence", sequence.id, 
                             f"Created sequence '{sequence.header}' in project {sequence.project_id}")
            
            return sequence
            
        except Exception as e:
            self.logger.error(f"Failed to create sequence: {e}")
            raise RepositoryError(f"Failed to create sequence: {e}")
    
    def get_by_id(self, sequence_id: int) -> Optional[Sequence]:
        """Get sequence by ID."""
        try:
            query = "SELECT * FROM sequences WHERE id = ?"
            result = self._execute_query(query, (sequence_id,))
            
            if not result:
                return None
            
            sequence = Sequence.from_dict(result[0])
            
            # Load sequence from file if stored externally
            if sequence.file_path and not sequence.sequence:
                sequence.sequence = self._load_sequence_file(sequence.file_path)
                # Recalculate properties
                sequence.__post_init__()
            
            return sequence
            
        except Exception as e:
            self.logger.error(f"Failed to get sequence {sequence_id}: {e}")
            raise RepositoryError(f"Failed to get sequence: {e}")
    
    def update(self, sequence: Sequence) -> bool:
        """Update an existing sequence."""
        try:
            if not sequence.id:
                raise RepositoryError("Sequence ID is required for update")
            
            # Prepare data for update
            data = sequence.to_dict()
            
            # Handle large sequence storage
            if len(sequence.sequence) > 10000:
                file_path = self._store_sequence_file(sequence)
                sequence.file_path = str(file_path)
                data['file_path'] = str(file_path)
                data['sequence'] = ''  # Clear sequence data from database
            
            query = """
                UPDATE sequences 
                SET project_id = ?, header = ?, sequence = ?, sequence_type = ?,
                    length = ?, gc_percentage = ?, notes = ?, tags = ?, file_path = ?
                WHERE id = ?
            """
            
            params = (
                data['project_id'], data['header'], data['sequence'],
                data['sequence_type'], data['length'], data['gc_percentage'],
                data['notes'], data['tags'], data['file_path'], sequence.id
            )
            
            self._execute_query(query, params)
            
            # Log activity
            self._log_activity("update", "sequence", sequence.id, 
                             f"Updated sequence '{sequence.header}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update sequence {sequence.id}: {e}")
            raise RepositoryError(f"Failed to update sequence: {e}")
    
    def delete(self, sequence_id: int) -> bool:
        """Delete a sequence and associated files."""
        try:
            # Get sequence info for cleanup
            sequence = self.get_by_id(sequence_id)
            if not sequence:
                return False
            
            # Delete associated analyses first
            analyses_query = "DELETE FROM analyses WHERE sequence_id = ?"
            self._execute_query(analyses_query, (sequence_id,))
            
            # Delete sequence file if exists
            if sequence.file_path:
                self._delete_sequence_file(sequence.file_path)
            
            # Delete sequence record
            query = "DELETE FROM sequences WHERE id = ?"
            self._execute_query(query, (sequence_id,))
            
            # Log activity
            self._log_activity("delete", "sequence", sequence_id, 
                             f"Deleted sequence '{sequence.header}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete sequence {sequence_id}: {e}")
            raise RepositoryError(f"Failed to delete sequence: {e}")
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Sequence]:
        """List sequences with optional filters."""
        try:
            base_query = "SELECT * FROM sequences"
            where_clause, params = self._build_where_clause(filters)
            order_clause = self._build_order_clause("created_date", order_desc=True)
            
            query = base_query + where_clause + order_clause
            result = self._execute_query(query, params)
            
            sequences = []
            for row in result:
                sequence = Sequence.from_dict(row)
                
                # Load sequence from file if needed (for small sequences only in list view)
                if sequence.file_path and not sequence.sequence and sequence.length <= 1000:
                    try:
                        sequence.sequence = self._load_sequence_file(sequence.file_path)
                        sequence.__post_init__()
                    except Exception as e:
                        self.logger.warning(f"Failed to load sequence file {sequence.file_path}: {e}")
                
                sequences.append(sequence)
            
            return sequences
            
        except Exception as e:
            self.logger.error(f"Failed to list sequences: {e}")
            raise RepositoryError(f"Failed to list sequences: {e}")
    
    def get_by_project(self, project_id: int) -> List[Sequence]:
        """Get all sequences for a project."""
        return self.list({"project_id": project_id})
    
    def get_by_type(self, sequence_type: str) -> List[Sequence]:
        """Get sequences by type (dna, rna, protein)."""
        return self.list({"sequence_type": sequence_type})
    
    def search_sequences(self, search_term: str, project_id: Optional[int] = None) -> List[Sequence]:
        """Search sequences by header or notes."""
        try:
            base_query = """
                SELECT * FROM sequences 
                WHERE (header ILIKE ? OR notes ILIKE ?)
            """
            
            params = [f"%{search_term}%", f"%{search_term}%"]
            
            if project_id:
                base_query += " AND project_id = ?"
                params.append(project_id)
            
            base_query += " ORDER BY created_date DESC"
            
            result = self._execute_query(base_query, tuple(params))
            
            return [Sequence.from_dict(row) for row in result]
            
        except Exception as e:
            self.logger.error(f"Failed to search sequences: {e}")
            raise RepositoryError(f"Failed to search sequences: {e}")
    
    def get_sequence_statistics(self, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Get sequence statistics."""
        try:
            base_query = """
                SELECT 
                    COUNT(*) as total_sequences,
                    COUNT(CASE WHEN sequence_type = 'dna' THEN 1 END) as dna_sequences,
                    COUNT(CASE WHEN sequence_type = 'rna' THEN 1 END) as rna_sequences,
                    COUNT(CASE WHEN sequence_type = 'protein' THEN 1 END) as protein_sequences,
                    AVG(length) as avg_length,
                    MAX(length) as max_length,
                    MIN(length) as min_length,
                    AVG(gc_percentage) as avg_gc_percentage
                FROM sequences
            """
            
            params = []
            if project_id:
                base_query += " WHERE project_id = ?"
                params.append(project_id)
            
            result = self._execute_query(base_query, tuple(params))
            if not result:
                return {}
            
            stats = result[0]
            
            # Convert None values to 0
            for key, value in stats.items():
                if value is None:
                    stats[key] = 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get sequence statistics: {e}")
            raise RepositoryError(f"Failed to get sequence statistics: {e}")
    
    def get_sequences_by_tag(self, tag: str, project_id: Optional[int] = None) -> List[Sequence]:
        """Get sequences by tag."""
        try:
            base_query = "SELECT * FROM sequences WHERE tags LIKE ?"
            params = [f"%{tag}%"]
            
            if project_id:
                base_query += " AND project_id = ?"
                params.append(project_id)
            
            base_query += " ORDER BY created_date DESC"
            
            result = self._execute_query(base_query, tuple(params))
            
            # Filter results to ensure exact tag match
            sequences = []
            for row in result:
                sequence = Sequence.from_dict(row)
                if sequence.has_tag(tag):
                    sequences.append(sequence)
            
            return sequences
            
        except Exception as e:
            self.logger.error(f"Failed to get sequences by tag: {e}")
            raise RepositoryError(f"Failed to get sequences by tag: {e}")
    
    def _store_sequence_file(self, sequence: Sequence) -> Path:
        """Store sequence data in a file."""
        try:
            file_path = self.data_dir / f"seq_{sequence.id}.fasta"
            
            with open(file_path, 'w') as f:
                f.write(f">{sequence.header}\n")
                # Write sequence in 80-character lines
                seq = sequence.sequence
                for i in range(0, len(seq), 80):
                    f.write(seq[i:i+80] + '\n')
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Failed to store sequence file: {e}")
            raise RepositoryError(f"Failed to store sequence file: {e}")
    
    def _load_sequence_file(self, file_path: str) -> str:
        """Load sequence data from a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Sequence file not found: {file_path}")
            
            sequence_lines = []
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('>'):
                        sequence_lines.append(line)
            
            return ''.join(sequence_lines)
            
        except Exception as e:
            self.logger.error(f"Failed to load sequence file {file_path}: {e}")
            raise RepositoryError(f"Failed to load sequence file: {e}")
    
    def _delete_sequence_file(self, file_path: str):
        """Delete sequence file."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                self.logger.info(f"Deleted sequence file: {file_path}")
        except Exception as e:
            self.logger.warning(f"Failed to delete sequence file {file_path}: {e}")
    
    def _log_activity(self, action: str, entity_type: str, entity_id: int, description: str):
        """Log activity for audit trail."""
        try:
            # Get next ID for activity log
            conn = self.db_manager.get_connection()
            result = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM activity_log").fetchall()
            next_id = result[0][0]
            
            query = """
                INSERT INTO activity_log (id, action, entity_type, entity_id, description)
                VALUES (?, ?, ?, ?, ?)
            """
            
            params = (next_id, action, entity_type, entity_id, description)
            conn.execute(query, params)
            
        except Exception as e:
            self.logger.warning(f"Failed to log activity: {e}")