"""Workspace ViewModel with file operations and sequence editing."""

from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import os

from viewmodels.base_viewmodel import BaseViewModel
from services.sequence_service import SequenceService
from services.project_service import ProjectService
from models.sequence_model import Sequence


class WorkspaceViewModel(BaseViewModel):
    """ViewModel for workspace page with file operations and sequence editing."""
    
    def __init__(self):
        """Initialize workspace ViewModel."""
        super().__init__()
        
        # Services
        self.sequence_service = SequenceService()
        self.project_service = ProjectService()
        
        # Initialize workspace state
        self._initialize_workspace_state()
    
    def _initialize_workspace_state(self):
        """Initialize workspace-specific state."""
        self.update_state('current_project', None, notify=False)
        self.update_state('sequences', [], notify=False)
        self.update_state('current_sequence', None, notify=False)
        self.update_state('sequence_content', '', notify=False)
        self.update_state('sequence_header', '', notify=False)
        self.update_state('is_editing', False, notify=False)
        self.update_state('has_unsaved_changes', False, notify=False)
        self.update_state('file_browser_path', str(Path.home()), notify=False)
        self.update_state('file_browser_files', [], notify=False)
        self.update_state('selected_files', [], notify=False)
        self.update_state('import_progress', 0, notify=False)
        self.update_state('show_import_dialog', False, notify=False)
        self.update_state('show_save_dialog', False, notify=False)
        self.update_state('editor_mode', 'view', notify=False)  # view, edit, create
    
    def set_current_project(self, project_id: int) -> None:
        """Set the current project for workspace operations."""
        self.log_action("set_current_project", {'project_id': project_id})
        
        def load_project_operation():
            # Get project
            success, project = self.project_service.get_project(project_id)
            if not success:
                raise Exception(project)
            
            # Get project sequences
            seq_success, sequences = self.sequence_service.get_sequences_by_project(project_id)
            if not seq_success:
                raise Exception(sequences)
            
            return project, sequences
        
        def on_success(result):
            project, sequences = result
            self.update_state('current_project', project)
            self.update_state('sequences', sequences)
            
            # Clear current sequence if it's not in the new project
            current_seq = self.get_state('current_sequence')
            if current_seq and current_seq.project_id != project_id:
                self.update_state('current_sequence', None)
                self.update_state('sequence_content', '')
                self.update_state('sequence_header', '')
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to load project: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("load_project", load_project_operation, on_success, on_error)
    
    def browse_files(self, path: Optional[str] = None) -> None:
        """Browse files in the specified directory."""
        if path is None:
            path = self.get_state('file_browser_path', str(Path.home()))
        
        self.log_action("browse_files", {'path': path})
        
        def browse_operation():
            try:
                path_obj = Path(path)
                if not path_obj.exists():
                    raise Exception(f"Path does not exist: {path}")
                
                if not path_obj.is_dir():
                    raise Exception(f"Path is not a directory: {path}")
                
                files = []
                
                # Add parent directory entry if not at root
                if path_obj.parent != path_obj:
                    files.append({
                        'name': '..',
                        'path': str(path_obj.parent),
                        'type': 'directory',
                        'size': 0,
                        'modified': None,
                        'is_parent': True
                    })
                
                # List directory contents
                for item in sorted(path_obj.iterdir()):
                    try:
                        stat = item.stat()
                        file_info = {
                            'name': item.name,
                            'path': str(item),
                            'type': 'directory' if item.is_dir() else 'file',
                            'size': stat.st_size if item.is_file() else 0,
                            'modified': stat.st_mtime,
                            'is_fasta': item.suffix.lower() in ['.fasta', '.fa', '.fas', '.fna'],
                            'is_parent': False
                        }
                        files.append(file_info)
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
                
                return path, files
                
            except Exception as e:
                raise Exception(f"Failed to browse directory: {e}")
        
        def on_success(result):
            current_path, files = result
            self.update_state('file_browser_path', current_path)
            self.update_state('file_browser_files', files)
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(str(error))
            except ImportError:
                pass
        
        self.execute_async_operation("browse_files", browse_operation, on_success, on_error)
    
    def select_file(self, file_path: str, multi_select: bool = False) -> None:
        """Select a file in the browser."""
        self.log_action("select_file", {'path': file_path, 'multi': multi_select})
        
        selected_files = self.get_state('selected_files', [])
        
        if multi_select:
            if file_path in selected_files:
                selected_files.remove(file_path)
            else:
                selected_files.append(file_path)
        else:
            selected_files = [file_path] if file_path not in selected_files else []
        
        self.update_state('selected_files', selected_files)
    
    def import_fasta_files(self, file_paths: List[str], project_id: Optional[int] = None) -> None:
        """Import FASTA files into the current project."""
        if project_id is None:
            current_project = self.get_state('current_project')
            if not current_project:
                try:
                    from views.components.toast_notifications import show_error
                    show_error("No project selected for import")
                except ImportError:
                    pass
                return
            project_id = current_project.id
        
        self.log_action("import_fasta_files", {'count': len(file_paths), 'project_id': project_id})
        
        def import_operation():
            imported_sequences = []
            total_files = len(file_paths)
            
            for i, file_path in enumerate(file_paths):
                # Update progress
                progress = (i / total_files) * 100
                self.update_state('import_progress', progress)
                
                try:
                    # Import sequences from file
                    success, sequences = self.sequence_service.import_fasta_file(file_path, project_id)
                    if success:
                        imported_sequences.extend(sequences)
                    else:
                        self.logger.warning(f"Failed to import {file_path}: {sequences}")
                
                except Exception as e:
                    self.logger.error(f"Error importing {file_path}: {e}")
            
            # Final progress update
            self.update_state('import_progress', 100)
            
            return imported_sequences
        
        def on_success(imported_sequences):
            # Update sequences list
            current_sequences = self.get_state('sequences', [])
            current_sequences.extend(imported_sequences)
            self.update_state('sequences', current_sequences)
            
            # Clear selection and progress
            self.update_state('selected_files', [])
            self.update_state('import_progress', 0)
            self.update_state('show_import_dialog', False)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Imported {len(imported_sequences)} sequences from {len(file_paths)} files")
            except ImportError:
                pass
        
        def on_error(error):
            self.update_state('import_progress', 0)
            self.update_state('show_import_dialog', False)
            
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Import failed: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("import_fasta", import_operation, on_success, on_error)
    
    def load_sequence(self, sequence_id: int) -> None:
        """Load a sequence for viewing/editing."""
        self.log_action("load_sequence", {'sequence_id': sequence_id})
        
        def load_operation():
            success, sequence = self.sequence_service.get_sequence(sequence_id)
            if not success:
                raise Exception(sequence)
            
            # Get sequence content
            content_success, content = self.sequence_service.get_sequence_content(sequence_id)
            if not content_success:
                raise Exception(content)
            
            return sequence, content
        
        def on_success(result):
            sequence, content = result
            self.update_state('current_sequence', sequence)
            self.update_state('sequence_content', content)
            self.update_state('sequence_header', sequence.header)
            self.update_state('editor_mode', 'view')
            self.update_state('has_unsaved_changes', False)
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to load sequence: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("load_sequence", load_operation, on_success, on_error)
    
    def create_new_sequence(self, project_id: Optional[int] = None) -> None:
        """Create a new sequence for editing."""
        if project_id is None:
            current_project = self.get_state('current_project')
            if not current_project:
                try:
                    from views.components.toast_notifications import show_error
                    show_error("No project selected")
                except ImportError:
                    pass
                return
            project_id = current_project.id
        
        self.log_action("create_new_sequence", {'project_id': project_id})
        
        # Create empty sequence
        new_sequence = Sequence(
            project_id=project_id,
            header="New Sequence",
            sequence="",
            sequence_type="dna"
        )
        
        self.update_state('current_sequence', new_sequence)
        self.update_state('sequence_content', '')
        self.update_state('sequence_header', 'New Sequence')
        self.update_state('editor_mode', 'create')
        self.update_state('is_editing', True)
        self.update_state('has_unsaved_changes', False)
    
    def edit_sequence(self) -> None:
        """Start editing the current sequence."""
        current_sequence = self.get_state('current_sequence')
        if not current_sequence:
            return
        
        self.log_action("edit_sequence", {'sequence_id': current_sequence.id})
        
        self.update_state('editor_mode', 'edit')
        self.update_state('is_editing', True)
    
    def update_sequence_content(self, content: str) -> None:
        """Update sequence content during editing."""
        self.update_state('sequence_content', content)
        self.update_state('has_unsaved_changes', True)
    
    def update_sequence_header(self, header: str) -> None:
        """Update sequence header during editing."""
        self.update_state('sequence_header', header)
        self.update_state('has_unsaved_changes', True)
    
    def save_sequence(self) -> None:
        """Save the current sequence."""
        current_sequence = self.get_state('current_sequence')
        if not current_sequence:
            return
        
        content = self.get_state('sequence_content', '')
        header = self.get_state('sequence_header', '')
        editor_mode = self.get_state('editor_mode', 'view')
        
        self.log_action("save_sequence", {
            'sequence_id': current_sequence.id,
            'mode': editor_mode,
            'content_length': len(content)
        })
        
        def save_operation():
            # Update sequence data
            current_sequence.header = header.strip()
            current_sequence.sequence = content.strip()
            
            if editor_mode == 'create':
                # Create new sequence
                success, saved_sequence = self.sequence_service.create_sequence(current_sequence)
                if not success:
                    raise Exception(saved_sequence)
                return saved_sequence, 'created'
            else:
                # Update existing sequence
                success, result = self.sequence_service.update_sequence(current_sequence)
                if not success:
                    raise Exception(result)
                
                # Get updated sequence
                success, updated_sequence = self.sequence_service.get_sequence(current_sequence.id)
                if not success:
                    raise Exception(updated_sequence)
                
                return updated_sequence, 'updated'
        
        def on_success(result):
            saved_sequence, action = result
            
            # Update state
            self.update_state('current_sequence', saved_sequence)
            self.update_state('editor_mode', 'view')
            self.update_state('is_editing', False)
            self.update_state('has_unsaved_changes', False)
            
            # Update sequences list
            current_sequences = self.get_state('sequences', [])
            if action == 'created':
                current_sequences.append(saved_sequence)
            else:
                # Update existing sequence in list
                for i, seq in enumerate(current_sequences):
                    if seq.id == saved_sequence.id:
                        current_sequences[i] = saved_sequence
                        break
            self.update_state('sequences', current_sequences)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                action_text = "created" if action == 'created' else "saved"
                show_success(f"Sequence '{saved_sequence.header}' {action_text} successfully")
            except ImportError:
                pass
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to save sequence: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("save_sequence", save_operation, on_success, on_error)
    
    def cancel_editing(self) -> None:
        """Cancel sequence editing."""
        self.log_action("cancel_editing")
        
        has_changes = self.get_state('has_unsaved_changes', False)
        
        if has_changes:
            # Show confirmation dialog
            self.update_state('show_save_dialog', True)
        else:
            self._discard_changes()
    
    def _discard_changes(self) -> None:
        """Discard unsaved changes."""
        editor_mode = self.get_state('editor_mode', 'view')
        
        if editor_mode == 'create':
            # Clear new sequence
            self.update_state('current_sequence', None)
            self.update_state('sequence_content', '')
            self.update_state('sequence_header', '')
        else:
            # Reload original sequence
            current_sequence = self.get_state('current_sequence')
            if current_sequence:
                self.load_sequence(current_sequence.id)
                return  # load_sequence will update the state
        
        self.update_state('editor_mode', 'view')
        self.update_state('is_editing', False)
        self.update_state('has_unsaved_changes', False)
    
    def confirm_discard_changes(self) -> None:
        """Confirm discarding unsaved changes."""
        self.update_state('show_save_dialog', False)
        self._discard_changes()
        self.log_action("discard_changes")
    
    def delete_sequence(self, sequence_id: int, confirmed: bool = False) -> None:
        """Delete a sequence with confirmation."""
        sequence = self._find_sequence_by_id(sequence_id)
        if not sequence:
            return
        
        self.log_action("delete_sequence", {'sequence_id': sequence_id, 'confirmed': confirmed})
        
        if not confirmed:
            # Show confirmation dialog
            self.update_state('pending_sequence_deletion', sequence)
            return
        
        def delete_operation():
            success, result = self.sequence_service.delete_sequence(sequence_id)
            if not success:
                raise Exception(result)
            return result
        
        def on_success(result):
            # Remove from sequences list
            current_sequences = self.get_state('sequences', [])
            current_sequences = [s for s in current_sequences if s.id != sequence_id]
            self.update_state('sequences', current_sequences)
            
            # Clear current sequence if it was deleted
            current_sequence = self.get_state('current_sequence')
            if current_sequence and current_sequence.id == sequence_id:
                self.update_state('current_sequence', None)
                self.update_state('sequence_content', '')
                self.update_state('sequence_header', '')
            
            # Clear pending deletion
            self.update_state('pending_sequence_deletion', None)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Sequence '{sequence.header}' deleted successfully")
            except ImportError:
                pass
        
        def on_error(error):
            self.update_state('pending_sequence_deletion', None)
            
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to delete sequence: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("delete_sequence", delete_operation, on_success, on_error)
    
    def export_sequence(self, sequence_id: int, file_path: str) -> None:
        """Export a sequence to a file."""
        sequence = self._find_sequence_by_id(sequence_id)
        if not sequence:
            return
        
        self.log_action("export_sequence", {'sequence_id': sequence_id, 'path': file_path})
        
        def export_operation():
            success, result = self.sequence_service.export_sequence(sequence_id, file_path)
            if not success:
                raise Exception(result)
            return result
        
        def on_success(result):
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Sequence exported to {file_path}")
            except ImportError:
                pass
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Export failed: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("export_sequence", export_operation, on_success, on_error)
    
    def _find_sequence_by_id(self, sequence_id: int) -> Optional[Sequence]:
        """Find sequence by ID in current sequences list."""
        sequences = self.get_state('sequences', [])
        for sequence in sequences:
            if sequence.id == sequence_id:
                return sequence
        return None
    
    def get_workspace_summary(self) -> Dict[str, Any]:
        """Get workspace summary information."""
        current_project = self.get_state('current_project')
        sequences = self.get_state('sequences', [])
        current_sequence = self.get_state('current_sequence')
        
        return {
            'has_project': current_project is not None,
            'project_name': current_project.name if current_project else None,
            'sequence_count': len(sequences),
            'has_current_sequence': current_sequence is not None,
            'current_sequence_name': current_sequence.header if current_sequence else None,
            'is_editing': self.get_state('is_editing', False),
            'has_unsaved_changes': self.get_state('has_unsaved_changes', False),
            'empty_state': len(sequences) == 0 and not self.is_loading()
        }
    
    def is_empty_state(self) -> bool:
        """Check if workspace should show empty state."""
        current_project = self.get_state('current_project')
        sequences = self.get_state('sequences', [])
        
        return current_project is None or (len(sequences) == 0 and not self.is_loading())
    
    def validate_sequence_data(self, header: str, content: str, sequence_type: str = 'dna') -> tuple[bool, Dict[str, str]]:
        """Validate sequence data."""
        errors = {}
        
        # Validate header
        if not header or not header.strip():
            errors['header'] = "Sequence header is required"
        elif len(header.strip()) > 200:
            errors['header'] = "Header is too long (max 200 characters)"
        
        # Validate content
        if not content or not content.strip():
            errors['content'] = "Sequence content is required"
        else:
            # Validate sequence characters based on type
            content_clean = content.strip().upper()
            if sequence_type == 'dna':
                valid_chars = set('ATCGN')
                invalid_chars = set(content_clean) - valid_chars
                if invalid_chars:
                    errors['content'] = f"Invalid DNA characters: {', '.join(sorted(invalid_chars))}"
            elif sequence_type == 'rna':
                valid_chars = set('AUCGN')
                invalid_chars = set(content_clean) - valid_chars
                if invalid_chars:
                    errors['content'] = f"Invalid RNA characters: {', '.join(sorted(invalid_chars))}"
            elif sequence_type == 'protein':
                valid_chars = set('ACDEFGHIKLMNPQRSTVWY*')
                invalid_chars = set(content_clean) - valid_chars
                if invalid_chars:
                    errors['content'] = f"Invalid protein characters: {', '.join(sorted(invalid_chars))}"
        
        return len(errors) == 0, errors