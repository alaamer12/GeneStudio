"""Project repository with CRUD operations and project lifecycle management."""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from repositories.base_repository import BaseRepository, RepositoryError
from models.project_model import Project


class ProjectRepository(BaseRepository[Project]):
    """Repository for project data access operations."""
    
    def create(self, project: Project) -> Project:
        """Create a new project."""
        try:
            # Prepare data for insertion
            data = project.to_dict()
            data.pop('id', None)  # Remove ID for auto-generation
            
            # Convert datetime objects to strings
            data['created_date'] = project.created_date.isoformat()
            data['modified_date'] = project.modified_date.isoformat()
            data['metadata'] = json.dumps(project.metadata)
            
            # Get next ID
            conn = self.db_manager.get_connection()
            result = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM projects").fetchall()
            next_id = result[0][0]
            
            # Insert project
            query = """
                INSERT INTO projects (id, name, type, description, created_date, modified_date, 
                                    status, sequence_count, analysis_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                next_id, data['name'], data['type'], data['description'],
                data['created_date'], data['modified_date'], data['status'],
                data['sequence_count'], data['analysis_count'], data['metadata']
            )
            
            conn.execute(query, params)
            project.id = next_id
            
            # Log activity
            self._log_activity("create", "project", project.id, f"Created project '{project.name}'")
            
            return project
            
        except Exception as e:
            self.logger.error(f"Failed to create project: {e}")
            raise RepositoryError(f"Failed to create project: {e}")
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        try:
            query = "SELECT * FROM projects WHERE id = ?"
            result = self._execute_query(query, (project_id,))
            
            if not result:
                return None
            
            return Project.from_dict(result[0])
            
        except Exception as e:
            self.logger.error(f"Failed to get project {project_id}: {e}")
            raise RepositoryError(f"Failed to get project: {e}")
    
    def update(self, project: Project) -> bool:
        """Update an existing project."""
        try:
            if not project.id:
                raise RepositoryError("Project ID is required for update")
            
            # Update modified date
            project.update_modified_date()
            
            # Prepare data for update
            data = project.to_dict()
            
            query = """
                UPDATE projects 
                SET name = ?, type = ?, description = ?, modified_date = ?, 
                    status = ?, sequence_count = ?, analysis_count = ?, metadata = ?
                WHERE id = ?
            """
            
            params = (
                data['name'], data['type'], data['description'],
                data['modified_date'], data['status'],
                data['sequence_count'], data['analysis_count'],
                json.dumps(project.metadata), project.id
            )
            
            self._execute_query(query, params)
            
            # Log activity
            self._log_activity("update", "project", project.id, f"Updated project '{project.name}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update project {project.id}: {e}")
            raise RepositoryError(f"Failed to update project: {e}")
    
    def delete(self, project_id: int) -> bool:
        """Delete a project and all associated data."""
        try:
            # Get project name for logging
            project = self.get_by_id(project_id)
            project_name = project.name if project else f"ID {project_id}"
            
            # Delete in transaction (cascading deletes handled by foreign keys)
            def delete_operations(conn):
                # Delete analyses first
                conn.execute("DELETE FROM analyses WHERE project_id = ?", (project_id,))
                # Delete sequences
                conn.execute("DELETE FROM sequences WHERE project_id = ?", (project_id,))
                # Delete project
                conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            
            self._execute_transaction([delete_operations])
            
            # Log activity
            self._log_activity("delete", "project", project_id, f"Deleted project '{project_name}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete project {project_id}: {e}")
            raise RepositoryError(f"Failed to delete project: {e}")
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Project]:
        """List projects with optional filters."""
        try:
            base_query = "SELECT * FROM projects"
            where_clause, params = self._build_where_clause(filters)
            order_clause = self._build_order_clause("modified_date", order_desc=True)
            
            query = base_query + where_clause + order_clause
            result = self._execute_query(query, params)
            
            return [Project.from_dict(row) for row in result]
            
        except Exception as e:
            self.logger.error(f"Failed to list projects: {e}")
            raise RepositoryError(f"Failed to list projects: {e}")
    
    def get_by_name(self, name: str) -> Optional[Project]:
        """Get project by name."""
        try:
            query = "SELECT * FROM projects WHERE name = ?"
            result = self._execute_query(query, (name,))
            
            if not result:
                return None
            
            return Project.from_dict(result[0])
            
        except Exception as e:
            self.logger.error(f"Failed to get project by name '{name}': {e}")
            raise RepositoryError(f"Failed to get project by name: {e}")
    
    def get_active_projects(self) -> List[Project]:
        """Get all active projects."""
        return self.list({"status": "active"})
    
    def get_project_statistics(self) -> Dict[str, Any]:
        """Get project statistics for dashboard."""
        try:
            stats_query = """
                SELECT 
                    COUNT(*) as total_projects,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_projects,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_projects,
                    COUNT(CASE WHEN status = 'archived' THEN 1 END) as archived_projects,
                    SUM(sequence_count) as total_sequences,
                    SUM(analysis_count) as total_analyses
                FROM projects
            """
            
            result = self._execute_query(stats_query)
            if not result:
                return {}
            
            stats = result[0]
            
            # Get recent activity
            recent_query = """
                SELECT COUNT(*) as recent_projects
                FROM projects 
                WHERE created_date >= (CURRENT_TIMESTAMP - INTERVAL 7 DAY)
            """
            
            recent_result = self._execute_query(recent_query)
            if recent_result:
                stats['recent_projects'] = recent_result[0]['recent_projects']
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get project statistics: {e}")
            raise RepositoryError(f"Failed to get project statistics: {e}")
    
    def update_sequence_count(self, project_id: int, delta: int) -> bool:
        """Update sequence count for a project."""
        try:
            query = """
                UPDATE projects 
                SET sequence_count = sequence_count + ?, modified_date = ?
                WHERE id = ?
            """
            
            params = (delta, datetime.now().isoformat(), project_id)
            self._execute_query(query, params)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update sequence count for project {project_id}: {e}")
            raise RepositoryError(f"Failed to update sequence count: {e}")
    
    def update_analysis_count(self, project_id: int, delta: int) -> bool:
        """Update analysis count for a project."""
        try:
            query = """
                UPDATE projects 
                SET analysis_count = analysis_count + ?, modified_date = ?
                WHERE id = ?
            """
            
            params = (delta, datetime.now().isoformat(), project_id)
            self._execute_query(query, params)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update analysis count for project {project_id}: {e}")
            raise RepositoryError(f"Failed to update analysis count: {e}")
    
    def search_projects(self, search_term: str) -> List[Project]:
        """Search projects by name or description."""
        try:
            query = """
                SELECT * FROM projects 
                WHERE name ILIKE ? OR description ILIKE ?
                ORDER BY modified_date DESC
            """
            
            search_pattern = f"%{search_term}%"
            result = self._execute_query(query, (search_pattern, search_pattern))
            
            return [Project.from_dict(row) for row in result]
            
        except Exception as e:
            self.logger.error(f"Failed to search projects: {e}")
            raise RepositoryError(f"Failed to search projects: {e}")
    
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