"""ViewModel for comprehensive sequence management."""

from typing import List, Dict, Any, Optional, Tuple, Set
import time
from datetime import datetime
from pathlib import Path

from viewmodels.base_viewmodel import BaseViewModel
from services.sequence_service import SequenceService
from models.sequence_model_enhanced import Sequence
from utils.async_executor import AsyncExecutor
from utils.logger import get_logger


class BatchOperation:
    """Represents a batch operation on sequences."""
    
    def __init__(self, operation_type: str, sequence_ids: List[int], parameters: Dict[str, Any] = None):
        self.operation_id = f"batch_{int(time.time() * 1000)}"
        self.operation_type = operation_type
        self.sequence_ids = sequence_ids
        self.parameters = parameters or {}
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0.0
        self.individual_status = {seq_id: "pending" for seq_id in sequence_ids}
        self.error_messages = {}
        self.started_at = None
        self.completed_at = None
        self.results = {}
    
    def get_completion_percentage(self) -> float:
        """Get completion percentage."""
        return self.progress * 100
    
    def update_individual_status(self, sequence_id: int, status: str, error: str = None):
        """Update status for individual sequence."""
        self.individual_status[sequence_id] = status
        if error:
            self.error_messages[sequence_id] = error
        
        # Update overall progress
        completed = sum(1 for s in self.individual_status.values() if s in ["completed", "failed"])
        self.progress = completed / len(self.sequence_ids) if self.sequence_ids else 1.0


class SequenceManagementViewModel(BaseViewModel):
    """ViewModel for comprehensive sequence management."""
    
    def __init__(self):
        """Initialize sequence management ViewModel."""
        super().__init__()
        self.sequence_service = SequenceService()
        self.logger = get_logger(self.__class__.__name__)
        
        # Batch operations tracking
        self.active_batch_operations: Dict[str, BatchOperation] = {}
        
        # Initialize state
        self._initialize_sequence_state()
    
    def _initialize_sequence_state(self):
        """Initialize sequence-specific state."""
        self.update_state('sequences', [], notify=False)
        self.update_state('filtered_sequences', [], notify=False)
        self.update_state('selected_sequences', [], notify=False)
        self.update_state('search_term', '', notify=False)
        self.update_state('filter_criteria', {}, notify=False)
        self.update_state('sort_criteria', {'field': 'created_date', 'ascending': False}, notify=False)
        self.update_state('current_project_id', None, notify=False)
        self.update_state('available_tags', [], notify=False)
        self.update_state('sequence_statistics', {}, notify=False)
        self.update_state('batch_operations', {}, notify=False)
        self.update_state('import_progress', 0.0, notify=False)
        self.update_state('export_progress', 0.0, notify=False)
        
        # Pagination state
        self.update_state('page_size', 50, notify=False)
        self.update_state('current_page', 0, notify=False)
        self.update_state('total_pages', 0, notify=False)
        
        # Metadata editing state
        self.update_state('editing_sequence_id', None, notify=False)
        self.update_state('metadata_form_data', {}, notify=False)
    
    def load_sequences(self, project_id: Optional[int] = None, force_refresh: bool = False):
        """Load sequences for the current project."""
        if not force_refresh and self.is_loading('load_sequences'):
            return
        
        self.update_state('current_project_id', project_id)
        
        def load_operation():
            if project_id:
                success, result = self.sequence_service.get_sequences_by_project(project_id)
            else:
                success, result = self.sequence_service.list_sequences()
            
            if not success:
                raise Exception(result)
            return result
        
        def on_success(sequences):
            self.update_state('sequences', sequences)
            self._apply_filters_and_sort()
            self._update_available_tags()
            self._update_statistics()
            self.log_action('load_sequences', {'count': len(sequences), 'project_id': project_id})
        
        def on_error(error):
            self.logger.error(f"Failed to load sequences: {error}")
        
        self.execute_async_operation('load_sequences', load_operation, on_success, on_error)
    
    def search_sequences(self, search_term: str):
        """Search sequences by header, notes, or tags."""
        self.update_state('search_term', search_term)
        
        if not search_term.strip():
            # If empty search, show all sequences
            self._apply_filters_and_sort()
            return
        
        def search_operation():
            success, result = self.sequence_service.search_sequences(
                search_term, self.get_state('current_project_id')
            )
            if not success:
                raise Exception(result)
            return result
        
        def on_success(sequences):
            self.update_state('sequences', sequences)
            self._apply_filters_and_sort()
            self.log_action('search_sequences', {'term': search_term, 'results': len(sequences)})
        
        def on_error(error):
            self.logger.error(f"Search failed: {error}")
        
        self.execute_async_operation('search_sequences', search_operation, on_success, on_error)
    
    def apply_filters(self, filter_criteria: Dict[str, Any]):
        """Apply filters to sequence list."""
        self.update_state('filter_criteria', filter_criteria)
        self._apply_filters_and_sort()
        self.log_action('apply_filters', filter_criteria)
    
    def apply_sort(self, field: str, ascending: bool = True):
        """Apply sorting to sequence list."""
        sort_criteria = {'field': field, 'ascending': ascending}
        self.update_state('sort_criteria', sort_criteria)
        self._apply_filters_and_sort()
        self.log_action('apply_sort', sort_criteria)
    
    def _apply_filters_and_sort(self):
        """Apply current filters and sorting to sequences."""
        sequences = self.get_state('sequences', [])
        filter_criteria = self.get_state('filter_criteria', {})
        sort_criteria = self.get_state('sort_criteria', {})
        
        # Apply filters
        filtered_sequences = sequences
        
        if filter_criteria.get('sequence_type'):
            seq_type = filter_criteria['sequence_type']
            filtered_sequences = [s for s in filtered_sequences if s.sequence_type == seq_type]
        
        if filter_criteria.get('min_length'):
            min_len = filter_criteria['min_length']
            filtered_sequences = [s for s in filtered_sequences if s.length >= min_len]
        
        if filter_criteria.get('max_length'):
            max_len = filter_criteria['max_length']
            filtered_sequences = [s for s in filtered_sequences if s.length <= max_len]
        
        if filter_criteria.get('tags'):
            required_tags = set(filter_criteria['tags'])
            filtered_sequences = [s for s in filtered_sequences 
                                if required_tags.issubset(set(s.tags))]
        
        if filter_criteria.get('date_range'):
            start_date, end_date = filter_criteria['date_range']
            filtered_sequences = [s for s in filtered_sequences 
                                if start_date <= s.created_date <= end_date]
        
        # Apply sorting
        if sort_criteria.get('field'):
            field = sort_criteria['field']
            ascending = sort_criteria.get('ascending', True)
            
            try:
                if field == 'header':
                    filtered_sequences.sort(key=lambda s: s.header.lower(), reverse=not ascending)
                elif field == 'length':
                    filtered_sequences.sort(key=lambda s: s.length, reverse=not ascending)
                elif field == 'gc_percentage':
                    filtered_sequences.sort(key=lambda s: s.gc_percentage or 0, reverse=not ascending)
                elif field == 'sequence_type':
                    filtered_sequences.sort(key=lambda s: s.sequence_type, reverse=not ascending)
                elif field == 'created_date':
                    filtered_sequences.sort(key=lambda s: s.created_date, reverse=not ascending)
                elif field == 'tag_count':
                    filtered_sequences.sort(key=lambda s: len(s.tags), reverse=not ascending)
            except Exception as e:
                self.logger.warning(f"Failed to sort by {field}: {e}")
        
        # Update pagination
        page_size = self.get_state('page_size', 50)
        total_pages = (len(filtered_sequences) + page_size - 1) // page_size
        self.update_state('total_pages', total_pages)
        
        # Apply pagination
        current_page = min(self.get_state('current_page', 0), max(0, total_pages - 1))
        self.update_state('current_page', current_page)
        
        start_idx = current_page * page_size
        end_idx = start_idx + page_size
        paginated_sequences = filtered_sequences[start_idx:end_idx]
        
        self.update_state('filtered_sequences', paginated_sequences)
    
    def set_page(self, page: int):
        """Set current page for pagination."""
        total_pages = self.get_state('total_pages', 0)
        if 0 <= page < total_pages:
            self.update_state('current_page', page)
            self._apply_filters_and_sort()
    
    def set_page_size(self, page_size: int):
        """Set page size for pagination."""
        if page_size > 0:
            self.update_state('page_size', page_size)
            self.update_state('current_page', 0)  # Reset to first page
            self._apply_filters_and_sort()
    
    def select_sequence(self, sequence_id: int, selected: bool = True):
        """Select or deselect a sequence."""
        selected_sequences = set(self.get_state('selected_sequences', []))
        
        if selected:
            selected_sequences.add(sequence_id)
        else:
            selected_sequences.discard(sequence_id)
        
        self.update_state('selected_sequences', list(selected_sequences))
    
    def select_all_sequences(self, selected: bool = True):
        """Select or deselect all visible sequences."""
        if selected:
            sequence_ids = [s.id for s in self.get_state('filtered_sequences', [])]
            self.update_state('selected_sequences', sequence_ids)
        else:
            self.update_state('selected_sequences', [])
    
    def get_selected_sequences(self) -> List[Sequence]:
        """Get currently selected sequences."""
        selected_ids = set(self.get_state('selected_sequences', []))
        all_sequences = self.get_state('sequences', [])
        return [s for s in all_sequences if s.id in selected_ids]
    
    def import_sequences(self, file_paths: List[str], project_id: int, 
                        import_options: Dict[str, Any] = None):
        """Import sequences from multiple files."""
        if not file_paths:
            return
        
        import_options = import_options or {}
        
        def import_operation(progress_callback):
            imported_sequences = []
            total_files = len(file_paths)
            
            for i, file_path in enumerate(file_paths):
                try:
                    # Update progress
                    file_progress = i / total_files
                    progress_callback(file_progress)
                    
                    # Import file
                    success, result = self.sequence_service.import_fasta_file(file_path, project_id)
                    if success:
                        imported_sequences.extend(result)
                        self.logger.info(f"Imported {len(result)} sequences from {file_path}")
                    else:
                        self.logger.error(f"Failed to import {file_path}: {result}")
                
                except Exception as e:
                    self.logger.error(f"Error importing {file_path}: {e}")
            
            progress_callback(1.0)
            return imported_sequences
        
        def progress_callback(progress):
            self.update_state('import_progress', progress)
        
        def on_success(imported_sequences):
            self.update_state('import_progress', 0.0)
            self.load_sequences(project_id, force_refresh=True)
            self.log_action('import_sequences', {
                'files': len(file_paths), 
                'imported': len(imported_sequences)
            })
        
        def on_error(error):
            self.update_state('import_progress', 0.0)
            self.logger.error(f"Import failed: {error}")
        
        AsyncExecutor.run_with_progress(import_operation, progress_callback, on_success, on_error)
    
    def export_sequences(self, sequence_ids: List[int], export_format: str, 
                        output_path: str, export_options: Dict[str, Any] = None):
        """Export selected sequences."""
        if not sequence_ids:
            return
        
        export_options = export_options or {}
        
        def export_operation(progress_callback):
            progress_callback(0.1)
            
            if export_format.lower() == 'fasta':
                success, result = self.sequence_service.export_sequences_to_fasta(
                    sequence_ids, output_path
                )
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            progress_callback(0.9)
            
            if not success:
                raise Exception(result)
            
            progress_callback(1.0)
            return result
        
        def progress_callback(progress):
            self.update_state('export_progress', progress)
        
        def on_success(result_path):
            self.update_state('export_progress', 0.0)
            self.log_action('export_sequences', {
                'count': len(sequence_ids),
                'format': export_format,
                'path': result_path
            })
        
        def on_error(error):
            self.update_state('export_progress', 0.0)
            self.logger.error(f"Export failed: {error}")
        
        AsyncExecutor.run_with_progress(export_operation, progress_callback, on_success, on_error)
    
    def start_batch_operation(self, operation_type: str, sequence_ids: List[int], 
                             parameters: Dict[str, Any] = None) -> str:
        """Start a batch operation on multiple sequences."""
        if not sequence_ids:
            raise ValueError("No sequences specified for batch operation")
        
        batch_op = BatchOperation(operation_type, sequence_ids, parameters)
        self.active_batch_operations[batch_op.operation_id] = batch_op
        
        # Update state
        batch_ops = self.get_state('batch_operations', {})
        batch_ops[batch_op.operation_id] = batch_op
        self.update_state('batch_operations', batch_ops)
        
        # Start the operation
        self._execute_batch_operation(batch_op)
        
        self.log_action('start_batch_operation', {
            'type': operation_type,
            'count': len(sequence_ids),
            'operation_id': batch_op.operation_id
        })
        
        return batch_op.operation_id
    
    def _execute_batch_operation(self, batch_op: BatchOperation):
        """Execute a batch operation asynchronously."""
        def batch_operation():
            batch_op.status = "running"
            batch_op.started_at = datetime.now()
            
            try:
                if batch_op.operation_type == "delete":
                    self._execute_batch_delete(batch_op)
                elif batch_op.operation_type == "export":
                    self._execute_batch_export(batch_op)
                elif batch_op.operation_type == "add_tag":
                    self._execute_batch_add_tag(batch_op)
                elif batch_op.operation_type == "remove_tag":
                    self._execute_batch_remove_tag(batch_op)
                elif batch_op.operation_type == "update_metadata":
                    self._execute_batch_update_metadata(batch_op)
                else:
                    raise ValueError(f"Unknown batch operation: {batch_op.operation_type}")
                
                batch_op.status = "completed"
                
            except Exception as e:
                batch_op.status = "failed"
                self.logger.error(f"Batch operation {batch_op.operation_id} failed: {e}")
            
            finally:
                batch_op.completed_at = datetime.now()
                self._update_batch_operation_state(batch_op)
        
        AsyncExecutor.run_async(batch_operation)
    
    def _execute_batch_delete(self, batch_op: BatchOperation):
        """Execute batch delete operation."""
        for i, sequence_id in enumerate(batch_op.sequence_ids):
            try:
                success, result = self.sequence_service.delete_sequence(sequence_id)
                if success:
                    batch_op.update_individual_status(sequence_id, "completed")
                else:
                    batch_op.update_individual_status(sequence_id, "failed", str(result))
            except Exception as e:
                batch_op.update_individual_status(sequence_id, "failed", str(e))
            
            # Update progress
            batch_op.progress = (i + 1) / len(batch_op.sequence_ids)
            self._update_batch_operation_state(batch_op)
    
    def _execute_batch_export(self, batch_op: BatchOperation):
        """Execute batch export operation."""
        try:
            export_format = batch_op.parameters.get('format', 'fasta')
            output_path = batch_op.parameters.get('output_path')
            
            if not output_path:
                raise ValueError("Output path not specified for batch export")
            
            success, result = self.sequence_service.export_sequences_to_fasta(
                batch_op.sequence_ids, output_path
            )
            
            if success:
                for sequence_id in batch_op.sequence_ids:
                    batch_op.update_individual_status(sequence_id, "completed")
                batch_op.results['export_path'] = result
            else:
                for sequence_id in batch_op.sequence_ids:
                    batch_op.update_individual_status(sequence_id, "failed", str(result))
        
        except Exception as e:
            for sequence_id in batch_op.sequence_ids:
                batch_op.update_individual_status(sequence_id, "failed", str(e))
        
        batch_op.progress = 1.0
        self._update_batch_operation_state(batch_op)
    
    def _execute_batch_add_tag(self, batch_op: BatchOperation):
        """Execute batch add tag operation."""
        tag = batch_op.parameters.get('tag')
        if not tag:
            raise ValueError("Tag not specified for batch add tag operation")
        
        for i, sequence_id in enumerate(batch_op.sequence_ids):
            try:
                success, result = self.sequence_service.add_tag_to_sequence(sequence_id, tag)
                if success:
                    batch_op.update_individual_status(sequence_id, "completed")
                else:
                    batch_op.update_individual_status(sequence_id, "failed", str(result))
            except Exception as e:
                batch_op.update_individual_status(sequence_id, "failed", str(e))
            
            batch_op.progress = (i + 1) / len(batch_op.sequence_ids)
            self._update_batch_operation_state(batch_op)
    
    def _execute_batch_remove_tag(self, batch_op: BatchOperation):
        """Execute batch remove tag operation."""
        tag = batch_op.parameters.get('tag')
        if not tag:
            raise ValueError("Tag not specified for batch remove tag operation")
        
        for i, sequence_id in enumerate(batch_op.sequence_ids):
            try:
                success, result = self.sequence_service.remove_tag_from_sequence(sequence_id, tag)
                if success:
                    batch_op.update_individual_status(sequence_id, "completed")
                else:
                    batch_op.update_individual_status(sequence_id, "failed", str(result))
            except Exception as e:
                batch_op.update_individual_status(sequence_id, "failed", str(e))
            
            batch_op.progress = (i + 1) / len(batch_op.sequence_ids)
            self._update_batch_operation_state(batch_op)
    
    def _execute_batch_update_metadata(self, batch_op: BatchOperation):
        """Execute batch metadata update operation."""
        metadata_updates = batch_op.parameters.get('metadata', {})
        if not metadata_updates:
            raise ValueError("Metadata updates not specified")
        
        for i, sequence_id in enumerate(batch_op.sequence_ids):
            try:
                # Get current sequence
                success, sequence = self.sequence_service.get_sequence(sequence_id)
                if not success:
                    batch_op.update_individual_status(sequence_id, "failed", str(sequence))
                    continue
                
                # Apply metadata updates
                if 'notes' in metadata_updates:
                    sequence.notes = metadata_updates['notes']
                if 'tags' in metadata_updates:
                    sequence.tags = metadata_updates['tags']
                
                # Update sequence
                success, result = self.sequence_service.update_sequence(sequence)
                if success:
                    batch_op.update_individual_status(sequence_id, "completed")
                else:
                    batch_op.update_individual_status(sequence_id, "failed", str(result))
            
            except Exception as e:
                batch_op.update_individual_status(sequence_id, "failed", str(e))
            
            batch_op.progress = (i + 1) / len(batch_op.sequence_ids)
            self._update_batch_operation_state(batch_op)
    
    def _update_batch_operation_state(self, batch_op: BatchOperation):
        """Update batch operation state in ViewModel."""
        batch_ops = self.get_state('batch_operations', {})
        batch_ops[batch_op.operation_id] = batch_op
        self.update_state('batch_operations', batch_ops)
    
    def get_batch_operation_status(self, operation_id: str) -> Optional[BatchOperation]:
        """Get status of a batch operation."""
        return self.active_batch_operations.get(operation_id)
    
    def cancel_batch_operation(self, operation_id: str) -> bool:
        """Cancel a running batch operation."""
        # Note: This is a simplified implementation
        # In a real system, you'd need more sophisticated cancellation
        batch_op = self.active_batch_operations.get(operation_id)
        if batch_op and batch_op.status == "running":
            batch_op.status = "cancelled"
            self._update_batch_operation_state(batch_op)
            return True
        return False
    
    def start_metadata_editing(self, sequence_id: int):
        """Start editing metadata for a sequence."""
        sequences = self.get_state('sequences', [])
        sequence = next((s for s in sequences if s.id == sequence_id), None)
        
        if sequence:
            self.update_state('editing_sequence_id', sequence_id)
            self.update_state('metadata_form_data', {
                'header': sequence.header,
                'notes': sequence.notes,
                'tags': sequence.tags.copy(),
                'sequence_type': sequence.sequence_type
            })
    
    def update_metadata_form(self, field: str, value: Any):
        """Update metadata form data."""
        form_data = self.get_state('metadata_form_data', {})
        form_data[field] = value
        self.update_state('metadata_form_data', form_data)
    
    def save_metadata_changes(self):
        """Save metadata changes for the currently editing sequence."""
        sequence_id = self.get_state('editing_sequence_id')
        form_data = self.get_state('metadata_form_data', {})
        
        if not sequence_id or not form_data:
            return
        
        def save_operation():
            # Get current sequence
            success, sequence = self.sequence_service.get_sequence(sequence_id)
            if not success:
                raise Exception(sequence)
            
            # Apply changes
            sequence.header = form_data.get('header', sequence.header)
            sequence.notes = form_data.get('notes', sequence.notes)
            sequence.tags = form_data.get('tags', sequence.tags)
            sequence.sequence_type = form_data.get('sequence_type', sequence.sequence_type)
            
            # Save changes
            success, result = self.sequence_service.update_sequence(sequence)
            if not success:
                raise Exception(result)
            
            return sequence
        
        def on_success(updated_sequence):
            self.update_state('editing_sequence_id', None)
            self.update_state('metadata_form_data', {})
            self.load_sequences(self.get_state('current_project_id'), force_refresh=True)
            self.log_action('save_metadata', {'sequence_id': sequence_id})
        
        def on_error(error):
            self.logger.error(f"Failed to save metadata: {error}")
        
        self.execute_async_operation('save_metadata', save_operation, on_success, on_error)
    
    def cancel_metadata_editing(self):
        """Cancel metadata editing."""
        self.update_state('editing_sequence_id', None)
        self.update_state('metadata_form_data', {})
    
    def _update_available_tags(self):
        """Update list of available tags from all sequences."""
        sequences = self.get_state('sequences', [])
        all_tags = set()
        
        for sequence in sequences:
            all_tags.update(sequence.tags)
        
        self.update_state('available_tags', sorted(list(all_tags)))
    
    def _update_statistics(self):
        """Update sequence statistics."""
        def stats_operation():
            project_id = self.get_state('current_project_id')
            success, result = self.sequence_service.get_sequence_statistics(project_id)
            if not success:
                raise Exception(result)
            return result
        
        def on_success(stats):
            self.update_state('sequence_statistics', stats)
        
        def on_error(error):
            self.logger.error(f"Failed to update statistics: {error}")
        
        self.execute_async_operation('update_statistics', stats_operation, on_success, on_error)
    
    def get_sequences_by_tag(self, tag: str):
        """Filter sequences by tag."""
        def tag_operation():
            project_id = self.get_state('current_project_id')
            success, result = self.sequence_service.get_sequences_by_tag(tag, project_id)
            if not success:
                raise Exception(result)
            return result
        
        def on_success(sequences):
            self.update_state('sequences', sequences)
            self._apply_filters_and_sort()
            self.log_action('filter_by_tag', {'tag': tag, 'results': len(sequences)})
        
        def on_error(error):
            self.logger.error(f"Failed to filter by tag: {error}")
        
        self.execute_async_operation('filter_by_tag', tag_operation, on_success, on_error)
    
    def refresh_sequences(self):
        """Refresh the sequence list."""
        project_id = self.get_state('current_project_id')
        self.load_sequences(project_id, force_refresh=True)
    
    def cleanup(self):
        """Cleanup resources."""
        # Cancel any active batch operations
        for operation_id in list(self.active_batch_operations.keys()):
            self.cancel_batch_operation(operation_id)
        
        super().cleanup()