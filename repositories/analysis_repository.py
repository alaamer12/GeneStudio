"""Analysis repository with CRUD operations and result storage."""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json

from repositories.base_repository import BaseRepository, RepositoryError
from models.analysis_model import Analysis


class AnalysisRepository(BaseRepository[Analysis]):
    """Repository for analysis data access operations."""
    
    def __init__(self):
        """Initialize analysis repository."""
        super().__init__()
        self.results_dir = Path("data/analyses")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def create(self, analysis: Analysis) -> Analysis:
        """Create a new analysis."""
        try:
            # Prepare data for insertion
            data = analysis.to_dict()
            data.pop('id', None)  # Remove ID for auto-generation
            
            # Get next ID
            conn = self.db_manager.get_connection()
            result = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM analyses").fetchall()
            next_id = result[0][0]
            
            # Insert analysis
            query = """
                INSERT INTO analyses (id, project_id, sequence_id, analysis_type, parameters,
                                    results, status, error_message, execution_time, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                next_id, data['project_id'], data['sequence_id'], data['analysis_type'],
                data['parameters'], data['results'], data['status'],
                data['error_message'], data['execution_time'], data['created_date']
            )
            
            conn.execute(query, params)
            analysis.id = next_id
            
            # Store large results in file if needed
            if len(data['results']) > 50000:  # Store results > 50KB in files
                file_path = self._store_results_file(analysis)
                
                # Update with file reference
                update_query = "UPDATE analyses SET results = ? WHERE id = ?"
                file_ref = json.dumps({"file_path": str(file_path), "stored_externally": True})
                self._execute_query(update_query, (file_ref, analysis.id))
            
            # Log activity
            self._log_activity("create", "analysis", analysis.id,
                             f"Created {analysis.analysis_type} analysis for sequence {analysis.sequence_id}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to create analysis: {e}")
            raise RepositoryError(f"Failed to create analysis: {e}")
    
    def get_by_id(self, analysis_id: int) -> Optional[Analysis]:
        """Get analysis by ID."""
        try:
            query = "SELECT * FROM analyses WHERE id = ?"
            result = self._execute_query(query, (analysis_id,))
            
            if not result:
                return None
            
            analysis = Analysis.from_dict(result[0])
            
            # Load results from file if stored externally
            if isinstance(analysis.results, dict) and analysis.results.get("stored_externally"):
                file_path = analysis.results.get("file_path")
                if file_path:
                    analysis.results = self._load_results_file(file_path)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get analysis {analysis_id}: {e}")
            raise RepositoryError(f"Failed to get analysis: {e}")
    
    def update(self, analysis: Analysis) -> bool:
        """Update an existing analysis."""
        try:
            if not analysis.id:
                raise RepositoryError("Analysis ID is required for update")
            
            # Prepare data for update
            data = analysis.to_dict()
            
            # Handle large results storage
            if len(data['results']) > 50000:
                file_path = self._store_results_file(analysis)
                data['results'] = json.dumps({"file_path": str(file_path), "stored_externally": True})
            
            query = """
                UPDATE analyses 
                SET project_id = ?, sequence_id = ?, analysis_type = ?, parameters = ?,
                    results = ?, status = ?, error_message = ?, execution_time = ?
                WHERE id = ?
            """
            
            params = (
                data['project_id'], data['sequence_id'], data['analysis_type'],
                data['parameters'], data['results'], data['status'],
                data['error_message'], data['execution_time'], analysis.id
            )
            
            self._execute_query(query, params)
            
            # Log activity
            self._log_activity("update", "analysis", analysis.id,
                             f"Updated {analysis.analysis_type} analysis")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update analysis {analysis.id}: {e}")
            raise RepositoryError(f"Failed to update analysis: {e}")
    
    def delete(self, analysis_id: int) -> bool:
        """Delete an analysis and associated files."""
        try:
            # Get analysis info for cleanup
            analysis = self.get_by_id(analysis_id)
            if not analysis:
                return False
            
            # Delete results file if exists
            if isinstance(analysis.results, dict) and analysis.results.get("stored_externally"):
                file_path = analysis.results.get("file_path")
                if file_path:
                    self._delete_results_file(file_path)
            
            # Delete analysis record
            query = "DELETE FROM analyses WHERE id = ?"
            self._execute_query(query, (analysis_id,))
            
            # Log activity
            self._log_activity("delete", "analysis", analysis_id,
                             f"Deleted {analysis.analysis_type} analysis")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete analysis {analysis_id}: {e}")
            raise RepositoryError(f"Failed to delete analysis: {e}")
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Analysis]:
        """List analyses with optional filters."""
        try:
            base_query = "SELECT * FROM analyses"
            where_clause, params = self._build_where_clause(filters)
            order_clause = self._build_order_clause("created_date", order_desc=True)
            
            query = base_query + where_clause + order_clause
            result = self._execute_query(query, params)
            
            analyses = []
            for row in result:
                analysis = Analysis.from_dict(row)
                
                # Don't load large external results in list view for performance
                if isinstance(analysis.results, dict) and analysis.results.get("stored_externally"):
                    analysis.results = {"stored_externally": True, "summary": "Large results stored in file"}
                
                analyses.append(analysis)
            
            return analyses
            
        except Exception as e:
            self.logger.error(f"Failed to list analyses: {e}")
            raise RepositoryError(f"Failed to list analyses: {e}")
    
    def get_by_project(self, project_id: int) -> List[Analysis]:
        """Get all analyses for a project."""
        return self.list({"project_id": project_id})
    
    def get_by_sequence(self, sequence_id: int) -> List[Analysis]:
        """Get all analyses for a sequence."""
        return self.list({"sequence_id": sequence_id})
    
    def get_by_type(self, analysis_type: str) -> List[Analysis]:
        """Get analyses by type."""
        return self.list({"analysis_type": analysis_type})
    
    def get_by_status(self, status: str) -> List[Analysis]:
        """Get analyses by status."""
        return self.list({"status": status})
    
    def get_running_analyses(self) -> List[Analysis]:
        """Get all currently running analyses."""
        return self.get_by_status("running")
    
    def get_failed_analyses(self) -> List[Analysis]:
        """Get all failed analyses."""
        return self.get_by_status("failed")
    
    def get_analysis_statistics(self, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Get analysis statistics."""
        try:
            base_query = """
                SELECT 
                    COUNT(*) as total_analyses,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_analyses,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_analyses,
                    COUNT(CASE WHEN status = 'running' THEN 1 END) as running_analyses,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_analyses,
                    AVG(execution_time) as avg_execution_time,
                    MAX(execution_time) as max_execution_time
                FROM analyses
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
            
            # Get analysis type breakdown
            type_query = """
                SELECT analysis_type, COUNT(*) as count
                FROM analyses
            """
            
            if project_id:
                type_query += " WHERE project_id = ?"
            
            type_query += " GROUP BY analysis_type ORDER BY count DESC"
            
            type_result = self._execute_query(type_query, tuple(params))
            stats['analysis_types'] = {row['analysis_type']: row['count'] for row in type_result}
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get analysis statistics: {e}")
            raise RepositoryError(f"Failed to get analysis statistics: {e}")
    
    def get_recent_analyses(self, limit: int = 10, project_id: Optional[int] = None) -> List[Analysis]:
        """Get recent analyses."""
        try:
            base_query = "SELECT * FROM analyses"
            params = []
            
            if project_id:
                base_query += " WHERE project_id = ?"
                params.append(project_id)
            
            base_query += " ORDER BY created_date DESC"
            base_query += self._build_limit_clause(limit)
            
            result = self._execute_query(base_query, tuple(params))
            
            return [Analysis.from_dict(row) for row in result]
            
        except Exception as e:
            self.logger.error(f"Failed to get recent analyses: {e}")
            raise RepositoryError(f"Failed to get recent analyses: {e}")
    
    def search_analyses(self, search_term: str, project_id: Optional[int] = None) -> List[Analysis]:
        """Search analyses by type or error message."""
        try:
            base_query = """
                SELECT * FROM analyses 
                WHERE (analysis_type ILIKE ? OR error_message ILIKE ?)
            """
            
            params = [f"%{search_term}%", f"%{search_term}%"]
            
            if project_id:
                base_query += " AND project_id = ?"
                params.append(project_id)
            
            base_query += " ORDER BY created_date DESC"
            
            result = self._execute_query(base_query, tuple(params))
            
            return [Analysis.from_dict(row) for row in result]
            
        except Exception as e:
            self.logger.error(f"Failed to search analyses: {e}")
            raise RepositoryError(f"Failed to search analyses: {e}")
    
    def _store_results_file(self, analysis: Analysis) -> Path:
        """Store analysis results in a file."""
        try:
            file_path = self.results_dir / f"analysis_{analysis.id}_results.json"
            
            with open(file_path, 'w') as f:
                json.dump(analysis.results, f, indent=2)
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"Failed to store results file: {e}")
            raise RepositoryError(f"Failed to store results file: {e}")
    
    def _load_results_file(self, file_path: str) -> Dict[str, Any]:
        """Load analysis results from a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Results file not found: {file_path}")
            
            with open(path, 'r') as f:
                return json.load(f)
            
        except Exception as e:
            self.logger.error(f"Failed to load results file {file_path}: {e}")
            raise RepositoryError(f"Failed to load results file: {e}")
    
    def _delete_results_file(self, file_path: str):
        """Delete results file."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                self.logger.info(f"Deleted results file: {file_path}")
        except Exception as e:
            self.logger.warning(f"Failed to delete results file {file_path}: {e}")
    
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