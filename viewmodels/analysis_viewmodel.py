"""Analysis ViewModel with parameter configuration and async execution."""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from viewmodels.base_viewmodel import BaseViewModel
from services.analysis_service import AnalysisService
from services.sequence_service import SequenceService
from services.project_service import ProjectService
from models.analysis_model import Analysis


class AnalysisViewModel(BaseViewModel):
    """ViewModel for analysis page with parameter configuration and execution."""
    
    def __init__(self):
        """Initialize analysis ViewModel."""
        super().__init__()
        
        # Services
        self.analysis_service = AnalysisService()
        self.sequence_service = SequenceService()
        self.project_service = ProjectService()
        
        # Initialize analysis state
        self._initialize_analysis_state()
    
    def _initialize_analysis_state(self):
        """Initialize analysis-specific state."""
        self.update_state('current_project', None, notify=False)
        self.update_state('available_sequences', [], notify=False)
        self.update_state('selected_sequences', [], notify=False)
        self.update_state('analysis_types', self._get_analysis_types(), notify=False)
        self.update_state('selected_analysis_type', None, notify=False)
        self.update_state('analysis_parameters', {}, notify=False)
        self.update_state('parameter_errors', {}, notify=False)
        self.update_state('running_analyses', [], notify=False)
        self.update_state('completed_analyses', [], notify=False)
        self.update_state('current_results', None, notify=False)
        self.update_state('show_parameter_dialog', False, notify=False)
        self.update_state('show_results_dialog', False, notify=False)
    
    def _get_analysis_types(self) -> List[Dict[str, Any]]:
        """Get available analysis types."""
        return [
            {
                'id': 'gc_content',
                'name': 'GC Content Analysis',
                'description': 'Calculate GC percentage and nucleotide distribution',
                'icon': '📊',
                'parameters': [
                    {
                        'name': 'window_size',
                        'label': 'Window Size',
                        'type': 'integer',
                        'default': 100,
                        'min': 10,
                        'max': 1000,
                        'description': 'Size of sliding window for GC content calculation'
                    }
                ]
            },
            {
                'id': 'pattern_search',
                'name': 'Pattern Matching',
                'description': 'Search for specific patterns using Boyer-Moore algorithm',
                'icon': '🔍',
                'parameters': [
                    {
                        'name': 'pattern',
                        'label': 'Search Pattern',
                        'type': 'string',
                        'default': '',
                        'required': True,
                        'description': 'DNA sequence pattern to search for'
                    },
                    {
                        'name': 'case_sensitive',
                        'label': 'Case Sensitive',
                        'type': 'boolean',
                        'default': False,
                        'description': 'Whether to perform case-sensitive matching'
                    }
                ]
            },
            {
                'id': 'translation',
                'name': 'DNA Translation',
                'description': 'Translate DNA sequences to amino acids',
                'icon': '🧬',
                'parameters': [
                    {
                        'name': 'reading_frame',
                        'label': 'Reading Frame',
                        'type': 'choice',
                        'choices': [1, 2, 3, -1, -2, -3],
                        'default': 1,
                        'description': 'Reading frame for translation (1-3 forward, -1 to -3 reverse)'
                    }
                ]
            },
            {
                'id': 'suffix_array',
                'name': 'Suffix Array Analysis',
                'description': 'Build suffix array and perform pattern searches',
                'icon': '📊',
                'parameters': [
                    {
                        'name': 'pattern',
                        'label': 'Search Pattern',
                        'type': 'string',
                        'default': '',
                        'description': 'Pattern to search for using suffix array'
                    }
                ]
            }
        ]
    
    def select_analysis_type(self, analysis_type_id: str):
        """Select an analysis type."""
        analysis_types = self.get_state('analysis_types', [])
        selected_type = None
        
        for analysis_type in analysis_types:
            if analysis_type['id'] == analysis_type_id:
                selected_type = analysis_type
                break
        
        if selected_type:
            self.update_state('selected_analysis_type', selected_type)
            # Reset parameters to defaults
            default_params = {}
            for param in selected_type.get('parameters', []):
                if 'default' in param:
                    default_params[param['name']] = param['default']
            self.update_state('analysis_parameters', default_params)
            self.update_state('parameter_errors', {})
    
    def run_analysis(self, analysis_type_id: str, sequences: list, parameters: dict):
        """Run analysis on selected sequences."""
        self.log_action("run_analysis", {
            'type': analysis_type_id,
            'sequence_count': len(sequences),
            'parameters': parameters
        })
        
        def analysis_operation():
            # Validate parameters
            is_valid, errors = self._validate_parameters(analysis_type_id, parameters)
            if not is_valid:
                raise ValueError(f"Parameter validation failed: {errors}")
            
            # Run analysis through service
            success, result = self.analysis_service.run_analysis(
                analysis_type_id, sequences, parameters
            )
            
            if not success:
                raise Exception(result)
            
            return result
        
        def on_success(result):
            # Update running analyses
            running = self.get_state('running_analyses', [])
            running = [a for a in running if a['type'] != analysis_type_id]
            self.update_state('running_analyses', running)
            
            # Update completed analyses
            completed = self.get_state('completed_analyses', [])
            completed.append({
                'type': analysis_type_id,
                'sequences': len(sequences),
                'result': result,
                'timestamp': datetime.now()
            })
            self.update_state('completed_analyses', completed)
            
            # Set current results
            self.update_state('current_results', result)
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Analysis '{analysis_type_id}' completed successfully")
            except ImportError:
                pass
        
        def on_error(error):
            # Update running analyses
            running = self.get_state('running_analyses', [])
            running = [a for a in running if a['type'] != analysis_type_id]
            self.update_state('running_analyses', running)
            
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Analysis failed: {error}")
            except ImportError:
                pass
        
        # Add to running analyses
        running = self.get_state('running_analyses', [])
        running.append({
            'type': analysis_type_id,
            'sequences': len(sequences),
            'start_time': datetime.now()
        })
        self.update_state('running_analyses', running)
        
        # Execute analysis
        self.execute_async_operation("run_analysis", analysis_operation, on_success, on_error)
    
    def _validate_parameters(self, analysis_type_id: str, parameters: dict) -> tuple[bool, dict]:
        """Validate analysis parameters."""
        analysis_types = self.get_state('analysis_types', [])
        analysis_type = None
        
        for at in analysis_types:
            if at['id'] == analysis_type_id:
                analysis_type = at
                break
        
        if not analysis_type:
            return False, {'general': 'Invalid analysis type'}
        
        errors = {}
        
        for param_def in analysis_type.get('parameters', []):
            param_name = param_def['name']
            param_value = parameters.get(param_name)
            
            # Check required parameters
            if param_def.get('required', False) and not param_value:
                errors[param_name] = 'This parameter is required'
                continue
            
            # Type validation
            param_type = param_def.get('type', 'string')
            
            if param_type == 'integer':
                try:
                    int_value = int(param_value) if param_value else param_def.get('default', 0)
                    # Check min/max
                    if 'min' in param_def and int_value < param_def['min']:
                        errors[param_name] = f'Value must be at least {param_def["min"]}'
                    if 'max' in param_def and int_value > param_def['max']:
                        errors[param_name] = f'Value must be at most {param_def["max"]}'
                except ValueError:
                    errors[param_name] = 'Must be a valid integer'
            
            elif param_type == 'choice':
                choices = param_def.get('choices', [])
                if param_value and param_value not in choices:
                    errors[param_name] = f'Must be one of: {choices}'
        
        return len(errors) == 0, errors
    
    def set_current_project(self, project_id: int):
        """Set current project and load available sequences."""
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
            self.update_state('available_sequences', sequences)
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to load project: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("load_project", load_project_operation, on_success, on_error)
    
    def get_analysis_summary(self) -> dict:
        """Get analysis summary information."""
        running = self.get_state('running_analyses', [])
        completed = self.get_state('completed_analyses', [])
        
        return {
            'running_count': len(running),
            'completed_count': len(completed),
            'has_current_results': self.get_state('current_results') is not None,
            'available_sequences': len(self.get_state('available_sequences', [])),
            'selected_analysis': self.get_state('selected_analysis_type', {}).get('name', 'None')
        }
                       