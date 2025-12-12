"""Project service with project management operations and validation."""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from services.base_service import BaseService, ValidationError, ServiceError
from repositories.project_repository import ProjectRepository
from models.project_model import Project


class ProjectService(BaseService[Project]):
    """Service for project management operations."""
    
    def __init__(self):
        """Initialize project service."""
        super().__init__(ProjectRepository())
        self.project_repository = self.repository
    
    def create_project(self, name: str, project_type: str = "sequence_analysis", 
                      description: str = "", metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, Project]:
        """Create a new project with validation."""
        try:
            # Validate project name uniqueness
            existing = self.project_repository.get_by_name(name)
            if existing:
                return False, f"Project with name '{name}' already exists"
            
            # Create project
            project = Project(
                name=name.strip(),
                type=project_type,
                description=description.strip(),
                metadata=metadata or {}
            )
            
            return self.create_entity(project)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "create_project")
    
    def get_project(self, project_id: int) -> Tuple[bool, Optional[Project]]:
        """Get a project by ID."""
        return self.get_entity(project_id)
    
    def update_project(self, project: Project) -> Tuple[bool, bool]:
        """Update a project with validation."""
        try:
            # Validate project exists
            existing = self.project_repository.get_by_id(project.id)
            if not existing:
                return self.handle_not_found("Project", project.id)
            
            # Check name uniqueness if name changed
            if existing.name != project.name:
                name_conflict = self.project_repository.get_by_name(project.name)
                if name_conflict and name_conflict.id != project.id:
                    return False, f"Project with name '{project.name}' already exists"
            
            return self.update_entity(project)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "update_project")
    
    def delete_project(self, project_id: int) -> Tuple[bool, bool]:
        """Delete a project and all associated data."""
        try:
            # Validate project exists
            project = self.project_repository.get_by_id(project_id)
            if not project:
                return self.handle_not_found("Project", project_id)
            
            # Check if project has sequences or analyses
            if project.sequence_count > 0 or project.analysis_count > 0:
                self.logger.warning(f"Deleting project {project_id} with {project.sequence_count} sequences and {project.analysis_count} analyses")
            
            return self.delete_entity(project_id)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "delete_project")
    
    def list_projects(self, filters: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[Project]]:
        """List projects with optional filters."""
        def operation():
            return self.project_repository.list(filters)
        
        return self.execute_with_logging(operation, "list_projects")
    
    def get_active_projects(self) -> Tuple[bool, List[Project]]:
        """Get all active projects."""
        def operation():
            return self.project_repository.get_active_projects()
        
        return self.execute_with_logging(operation, "get_active_projects")
    
    def search_projects(self, search_term: str) -> Tuple[bool, List[Project]]:
        """Search projects by name or description."""
        def operation():
            if not search_term or not search_term.strip():
                raise ValidationError("Search term cannot be empty")
            
            return self.project_repository.search_projects(search_term.strip())
        
        return self.execute_with_logging(operation, "search_projects")
    
    def archive_project(self, project_id: int) -> Tuple[bool, bool]:
        """Archive a project."""
        try:
            project = self.project_repository.get_by_id(project_id)
            if not project:
                return self.handle_not_found("Project", project_id)
            
            project.status = "archived"
            return self.update_entity(project)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "archive_project")
    
    def restore_project(self, project_id: int) -> Tuple[bool, bool]:
        """Restore an archived project."""
        try:
            project = self.project_repository.get_by_id(project_id)
            if not project:
                return self.handle_not_found("Project", project_id)
            
            project.status = "active"
            return self.update_entity(project)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "restore_project")
    
    def complete_project(self, project_id: int) -> Tuple[bool, bool]:
        """Mark a project as completed."""
        try:
            project = self.project_repository.get_by_id(project_id)
            if not project:
                return self.handle_not_found("Project", project_id)
            
            project.status = "completed"
            return self.update_entity(project)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "complete_project")
    
    def get_project_statistics(self) -> Tuple[bool, Dict[str, Any]]:
        """Get project statistics for dashboard."""
        def operation():
            return self.project_repository.get_project_statistics()
        
        return self.execute_with_logging(operation, "get_project_statistics")
    
    def duplicate_project(self, project_id: int, new_name: str) -> Tuple[bool, Project]:
        """Duplicate a project (metadata only, not sequences/analyses)."""
        try:
            # Get original project
            original = self.project_repository.get_by_id(project_id)
            if not original:
                return self.handle_not_found("Project", project_id)
            
            # Check name uniqueness
            existing = self.project_repository.get_by_name(new_name)
            if existing:
                return False, f"Project with name '{new_name}' already exists"
            
            # Create duplicate
            duplicate = Project(
                name=new_name.strip(),
                type=original.type,
                description=f"Copy of {original.name}",
                metadata=original.metadata.copy(),
                status="active"
            )
            
            return self.create_entity(duplicate)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "duplicate_project")
    
    def update_project_metadata(self, project_id: int, metadata: Dict[str, Any]) -> Tuple[bool, bool]:
        """Update project metadata."""
        try:
            project = self.project_repository.get_by_id(project_id)
            if not project:
                return self.handle_not_found("Project", project_id)
            
            project.metadata.update(metadata)
            return self.update_entity(project)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "update_project_metadata")
    
    def increment_sequence_count(self, project_id: int) -> Tuple[bool, bool]:
        """Increment sequence count for a project."""
        def operation():
            return self.project_repository.update_sequence_count(project_id, 1)
        
        return self.execute_with_logging(operation, "increment_sequence_count")
    
    def decrement_sequence_count(self, project_id: int) -> Tuple[bool, bool]:
        """Decrement sequence count for a project."""
        def operation():
            return self.project_repository.update_sequence_count(project_id, -1)
        
        return self.execute_with_logging(operation, "decrement_sequence_count")
    
    def increment_analysis_count(self, project_id: int) -> Tuple[bool, bool]:
        """Increment analysis count for a project."""
        def operation():
            return self.project_repository.update_analysis_count(project_id, 1)
        
        return self.execute_with_logging(operation, "increment_analysis_count")
    
    def decrement_analysis_count(self, project_id: int) -> Tuple[bool, bool]:
        """Decrement analysis count for a project."""
        def operation():
            return self.project_repository.update_analysis_count(project_id, -1)
        
        return self.execute_with_logging(operation, "decrement_analysis_count")
    
    def validate_project_data(self, project: Project) -> Tuple[bool, str]:
        """Validate project data with business rules."""
        try:
            # Basic model validation
            project.validate()
            
            # Business rule validations
            if len(project.name.strip()) < 2:
                return False, "Project name must be at least 2 characters long"
            
            if len(project.name) > 100:
                return False, "Project name cannot exceed 100 characters"
            
            # Check for invalid characters in name
            invalid_chars = set(project.name) & set('<>:"/\\|?*')
            if invalid_chars:
                return False, f"Project name contains invalid characters: {invalid_chars}"
            
            # Validate metadata size
            if len(str(project.metadata)) > 10000:  # 10KB limit
                return False, "Project metadata is too large (max 10KB)"
            
            return True, ""
            
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            self.logger.error(f"Unexpected validation error: {e}")
            return False, f"Validation error: {e}"
    
    def get_project_summary(self, project_id: int) -> Tuple[bool, Dict[str, Any]]:
        """Get a summary of project information."""
        try:
            project = self.project_repository.get_by_id(project_id)
            if not project:
                return self.handle_not_found("Project", project_id)
            
            summary = {
                'id': project.id,
                'name': project.name,
                'type': project.type,
                'status': project.status,
                'created_date': project.created_date,
                'modified_date': project.modified_date,
                'sequence_count': project.sequence_count,
                'analysis_count': project.analysis_count,
                'description_length': len(project.description),
                'has_metadata': bool(project.metadata),
                'age_days': (datetime.now() - project.created_date).days
            }
            
            return True, summary
            
        except Exception as e:
            return self.handle_unexpected_error(e, "get_project_summary")
    
    def get_projects_by_type(self, project_type: str) -> Tuple[bool, List[Project]]:
        """Get projects by type."""
        def operation():
            return self.project_repository.list({"type": project_type})
        
        return self.execute_with_logging(operation, "get_projects_by_type")
    
    def get_projects_by_status(self, status: str) -> Tuple[bool, List[Project]]:
        """Get projects by status."""
        def operation():
            return self.project_repository.list({"status": status})
        
        return self.execute_with_logging(operation, "get_projects_by_status")