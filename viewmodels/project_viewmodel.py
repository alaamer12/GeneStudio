"""Project ViewModel with CRUD operations and confirmation dialogs."""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from viewmodels.base_viewmodel import BaseViewModel
from services.project_service import ProjectService
from models.project_model import Project


class ProjectViewModel(BaseViewModel):
    """ViewModel for project management with CRUD operations."""
    
    def __init__(self):
        """Initialize project ViewModel."""
        super().__init__()
        
        # Services
        self.project_service = ProjectService()
        
        # Initialize project state
        self._initialize_project_state()
    
    def _initialize_project_state(self):
        """Initialize project-specific state."""
        self.update_state('projects', [], notify=False)
        self.update_state('current_project', None, notify=False)
        self.update_state('selected_projects', [], notify=False)
        self.update_state('search_term', '', notify=False)
        self.update_state('filter_status', 'all', notify=False)
        self.update_state('sort_by', 'modified_date', notify=False)
        self.update_state('sort_order', 'desc', notify=False)
        self.update_state('show_create_dialog', False, notify=False)
        self.update_state('show_edit_dialog', False, notify=False)
        self.update_state('pending_deletion', None, notify=False)
    
    def load_projects(self, filters: Optional[Dict[str, Any]] = None) -> None:
        """Load projects with optional filters."""
        self.log_action("load_projects", {'filters': filters})
        
        def load_operation():
            # Apply current filters if none provided
            current_filters = filters if filters is not None else self._build_current_filters()
            
            success, projects = self.project_service.list_projects(current_filters)
            if not success:
                raise Exception(projects)  # projects contains error message
            
            return projects
        
        def on_success(projects):
            self.update_state('projects', projects)
            
            # Show success message if not initial load
            if self.get_state('projects'):
                try:
                    from views.components.toast_notifications import show_success
                    show_success(f"Loaded {len(projects)} projects")
                except ImportError:
                    pass
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to load projects: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("load_projects", load_operation, on_success, on_error)
    
    def _build_current_filters(self) -> Dict[str, Any]:
        """Build filters from current state."""
        filters = {}
        
        # Search term
        search_term = self.get_state('search_term', '').strip()
        if search_term:
            filters['search'] = search_term
        
        # Status filter
        status_filter = self.get_state('filter_status', 'all')
        if status_filter != 'all':
            filters['status'] = status_filter
        
        # Sorting
        sort_by = self.get_state('sort_by', 'modified_date')
        sort_order = self.get_state('sort_order', 'desc')
        filters['order_by'] = sort_by
        filters['order'] = sort_order
        
        return filters
    
    def create_project(self, project_data: Dict[str, Any]) -> None:
        """Create a new project."""
        self.log_action("create_project", {'name': project_data.get('name')})
        
        def create_operation():
            success, result = self.project_service.create_project(
                name=project_data['name'],
                project_type=project_data.get('type', 'sequence_analysis'),
                description=project_data.get('description', ''),
                metadata=project_data.get('metadata', {})
            )
            
            if not success:
                raise Exception(result)  # result contains error message
            
            return result  # result is the created project
        
        def on_success(project):
            # Add to projects list
            current_projects = self.get_state('projects', [])
            current_projects.insert(0, project)  # Add at beginning
            self.update_state('projects', current_projects)
            
            # Set as current project
            self.update_state('current_project', project)
            
            # Close create dialog
            self.update_state('show_create_dialog', False)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Project '{project.name}' created successfully")
            except ImportError:
                pass
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to create project: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("create_project", create_operation, on_success, on_error)
    
    def update_project(self, project: Project) -> None:
        """Update an existing project."""
        self.log_action("update_project", {'id': project.id, 'name': project.name})
        
        def update_operation():
            success, result = self.project_service.update_project(project)
            if not success:
                raise Exception(result)
            
            # Get updated project
            success, updated_project = self.project_service.get_project(project.id)
            if not success:
                raise Exception(updated_project)
            
            return updated_project
        
        def on_success(updated_project):
            # Update in projects list
            current_projects = self.get_state('projects', [])
            for i, p in enumerate(current_projects):
                if p.id == updated_project.id:
                    current_projects[i] = updated_project
                    break
            self.update_state('projects', current_projects)
            
            # Update current project if it's the same
            current_project = self.get_state('current_project')
            if current_project and current_project.id == updated_project.id:
                self.update_state('current_project', updated_project)
            
            # Close edit dialog
            self.update_state('show_edit_dialog', False)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Project '{updated_project.name}' updated successfully")
            except ImportError:
                pass
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to update project: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("update_project", update_operation, on_success, on_error)
    
    def delete_project(self, project_id: int, confirmed: bool = False) -> None:
        """Delete a project with confirmation."""
        project = self._find_project_by_id(project_id)
        if not project:
            return
        
        self.log_action("delete_project", {'id': project_id, 'name': project.name, 'confirmed': confirmed})
        
        if not confirmed:
            # Show confirmation dialog
            self.update_state('pending_deletion', project)
            return
        
        def delete_operation():
            success, result = self.project_service.delete_project(project_id)
            if not success:
                raise Exception(result)
            return result
        
        def on_success(result):
            # Remove from projects list
            current_projects = self.get_state('projects', [])
            current_projects = [p for p in current_projects if p.id != project_id]
            self.update_state('projects', current_projects)
            
            # Clear current project if it was deleted
            current_project = self.get_state('current_project')
            if current_project and current_project.id == project_id:
                self.update_state('current_project', None)
            
            # Clear pending deletion
            self.update_state('pending_deletion', None)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Project '{project.name}' deleted successfully")
            except ImportError:
                pass
        
        def on_error(error):
            # Clear pending deletion
            self.update_state('pending_deletion', None)
            
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to delete project: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("delete_project", delete_operation, on_success, on_error)
    
    def cancel_deletion(self) -> None:
        """Cancel pending project deletion."""
        self.update_state('pending_deletion', None)
        self.log_action("cancel_deletion")
    
    def duplicate_project(self, project_id: int, new_name: str) -> None:
        """Duplicate a project."""
        project = self._find_project_by_id(project_id)
        if not project:
            return
        
        self.log_action("duplicate_project", {'id': project_id, 'new_name': new_name})
        
        def duplicate_operation():
            success, result = self.project_service.duplicate_project(project_id, new_name)
            if not success:
                raise Exception(result)
            return result
        
        def on_success(duplicated_project):
            # Add to projects list
            current_projects = self.get_state('projects', [])
            current_projects.insert(0, duplicated_project)
            self.update_state('projects', current_projects)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Project duplicated as '{duplicated_project.name}'")
            except ImportError:
                pass
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to duplicate project: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("duplicate_project", duplicate_operation, on_success, on_error)
    
    def archive_project(self, project_id: int) -> None:
        """Archive a project."""
        project = self._find_project_by_id(project_id)
        if not project:
            return
        
        self.log_action("archive_project", {'id': project_id, 'name': project.name})
        
        def archive_operation():
            success, result = self.project_service.archive_project(project_id)
            if not success:
                raise Exception(result)
            
            # Get updated project
            success, updated_project = self.project_service.get_project(project_id)
            if not success:
                raise Exception(updated_project)
            
            return updated_project
        
        def on_success(updated_project):
            # Update in projects list
            current_projects = self.get_state('projects', [])
            for i, p in enumerate(current_projects):
                if p.id == updated_project.id:
                    current_projects[i] = updated_project
                    break
            self.update_state('projects', current_projects)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Project '{updated_project.name}' archived")
            except ImportError:
                pass
        
        self.execute_async_operation("archive_project", archive_operation, on_success)
    
    def restore_project(self, project_id: int) -> None:
        """Restore an archived project."""
        project = self._find_project_by_id(project_id)
        if not project:
            return
        
        self.log_action("restore_project", {'id': project_id, 'name': project.name})
        
        def restore_operation():
            success, result = self.project_service.restore_project(project_id)
            if not success:
                raise Exception(result)
            
            # Get updated project
            success, updated_project = self.project_service.get_project(project_id)
            if not success:
                raise Exception(updated_project)
            
            return updated_project
        
        def on_success(updated_project):
            # Update in projects list
            current_projects = self.get_state('projects', [])
            for i, p in enumerate(current_projects):
                if p.id == updated_project.id:
                    current_projects[i] = updated_project
                    break
            self.update_state('projects', current_projects)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Project '{updated_project.name}' restored")
            except ImportError:
                pass
        
        self.execute_async_operation("restore_project", restore_operation, on_success)
    
    def search_projects(self, search_term: str) -> None:
        """Search projects by term."""
        self.log_action("search_projects", {'term': search_term})
        
        self.update_state('search_term', search_term)
        
        # Reload projects with search filter
        self.load_projects()
    
    def filter_by_status(self, status: str) -> None:
        """Filter projects by status."""
        self.log_action("filter_by_status", {'status': status})
        
        self.update_state('filter_status', status)
        
        # Reload projects with status filter
        self.load_projects()
    
    def sort_projects(self, sort_by: str, sort_order: str = 'desc') -> None:
        """Sort projects by field and order."""
        self.log_action("sort_projects", {'sort_by': sort_by, 'order': sort_order})
        
        self.update_state('sort_by', sort_by)
        self.update_state('sort_order', sort_order)
        
        # Reload projects with new sorting
        self.load_projects()
    
    def select_project(self, project_id: int) -> None:
        """Select a project as current."""
        project = self._find_project_by_id(project_id)
        if project:
            self.update_state('current_project', project)
            self.log_action("select_project", {'id': project_id, 'name': project.name})
    
    def toggle_project_selection(self, project_id: int) -> None:
        """Toggle project selection for bulk operations."""
        selected = self.get_state('selected_projects', [])
        
        if project_id in selected:
            selected.remove(project_id)
        else:
            selected.append(project_id)
        
        self.update_state('selected_projects', selected)
        self.log_action("toggle_selection", {'id': project_id, 'selected': project_id in selected})
    
    def clear_selection(self) -> None:
        """Clear all project selections."""
        self.update_state('selected_projects', [])
        self.log_action("clear_selection")
    
    def bulk_delete_projects(self, project_ids: List[int], confirmed: bool = False) -> None:
        """Delete multiple projects with confirmation."""
        if not confirmed:
            # Show bulk confirmation dialog
            projects = [self._find_project_by_id(pid) for pid in project_ids]
            projects = [p for p in projects if p is not None]
            self.update_state('pending_bulk_deletion', projects)
            return
        
        self.log_action("bulk_delete_projects", {'count': len(project_ids)})
        
        def bulk_delete_operation():
            failed_deletions = []
            
            for project_id in project_ids:
                success, result = self.project_service.delete_project(project_id)
                if not success:
                    failed_deletions.append((project_id, result))
            
            if failed_deletions:
                raise Exception(f"Failed to delete {len(failed_deletions)} projects")
            
            return len(project_ids)
        
        def on_success(deleted_count):
            # Remove deleted projects from list
            current_projects = self.get_state('projects', [])
            current_projects = [p for p in current_projects if p.id not in project_ids]
            self.update_state('projects', current_projects)
            
            # Clear selections
            self.clear_selection()
            
            # Clear pending deletion
            self.update_state('pending_bulk_deletion', None)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Deleted {deleted_count} projects successfully")
            except ImportError:
                pass
        
        def on_error(error):
            # Clear pending deletion
            self.update_state('pending_bulk_deletion', None)
            
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Bulk deletion failed: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("bulk_delete", bulk_delete_operation, on_success, on_error)
    
    def show_create_dialog(self) -> None:
        """Show create project dialog."""
        self.update_state('show_create_dialog', True)
        self.log_action("show_create_dialog")
    
    def hide_create_dialog(self) -> None:
        """Hide create project dialog."""
        self.update_state('show_create_dialog', False)
        self.log_action("hide_create_dialog")
    
    def show_edit_dialog(self, project_id: int) -> None:
        """Show edit project dialog."""
        project = self._find_project_by_id(project_id)
        if project:
            self.update_state('current_project', project)
            self.update_state('show_edit_dialog', True)
            self.log_action("show_edit_dialog", {'id': project_id})
    
    def hide_edit_dialog(self) -> None:
        """Hide edit project dialog."""
        self.update_state('show_edit_dialog', False)
        self.log_action("hide_edit_dialog")
    
    def _find_project_by_id(self, project_id: int) -> Optional[Project]:
        """Find project by ID in current projects list."""
        projects = self.get_state('projects', [])
        for project in projects:
            if project.id == project_id:
                return project
        return None
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get summary of current projects."""
        projects = self.get_state('projects', [])
        
        if not projects:
            return {
                'total': 0,
                'active': 0,
                'archived': 0,
                'completed': 0,
                'empty_state': True
            }
        
        summary = {
            'total': len(projects),
            'active': len([p for p in projects if p.status == 'active']),
            'archived': len([p for p in projects if p.status == 'archived']),
            'completed': len([p for p in projects if p.status == 'completed']),
            'empty_state': False
        }
        
        return summary
    
    def is_empty_state(self) -> bool:
        """Check if should show empty state."""
        projects = self.get_state('projects', [])
        return len(projects) == 0 and not self.is_loading('load_projects')
    
    def validate_project_data(self, data: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
        """Validate project data."""
        rules = {
            'name': lambda x: (bool(x and x.strip()), "Project name is required"),
            'type': lambda x: (x in ['sequence_analysis', 'genome_assembly', 'comparative'], 
                              "Invalid project type")
        }
        
        return self.validate_input(data, rules)