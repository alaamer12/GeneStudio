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
                       