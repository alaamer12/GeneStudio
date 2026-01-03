"""Analysis service with algorithm integration and async execution."""

from typing import Optional, List, Dict, Any, Tuple, Callable
import time
import threading
from datetime import datetime

from services.base_service import BaseService, ValidationError, ServiceError
from repositories.analysis_repository import AnalysisRepository
from repositories.sequence_repository import SequenceRepository
from models.analysis_model import Analysis
from models.sequence_model_enhanced import Sequence
import algorithms


class AnalysisService(BaseService[Analysis]):
    """Service for analysis management and execution."""
    
    def __init__(self):
        """Initialize analysis service."""
        super().__init__(AnalysisRepository())
        self.analysis_repository = self.repository
        self.sequence_repository = SequenceRepository()
        self._running_analyses = {}  # Track running analyses
        self._analysis_lock = threading.Lock()
    
    def create_analysis(self, project_id: int, sequence_id: int, analysis_type: str,
                       parameters: Optional[Dict[str, Any]] = None) -> Tuple[bool, Analysis]:
        """Create a new analysis."""
        try:
            # Validate sequence exists
            sequence = self.sequence_repository.get_by_id(sequence_id)
            if not sequence:
                return False, f"Sequence with ID {sequence_id} not found"
            
            # Validate analysis type
            if not self._is_valid_analysis_type(analysis_type):
                return False, f"Invalid analysis type: {analysis_type}"
            
            # Create analysis
            analysis = Analysis(
                project_id=project_id,
                sequence_id=sequence_id,
                analysis_type=analysis_type,
                parameters=parameters or {},
                status="pending"
            )
            
            return self.create_entity(analysis)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "create_analysis")
    
    def execute_analysis(self, analysis_id: int, async_execution: bool = True) -> Tuple[bool, Any]:
        """Execute an analysis."""
        try:
            analysis = self.analysis_repository.get_by_id(analysis_id)
            if not analysis:
                return self.handle_not_found("Analysis", analysis_id)
            
            if analysis.status == "running":
                return False, "Analysis is already running"
            
            if async_execution:
                # Execute asynchronously
                thread = threading.Thread(
                    target=self._execute_analysis_async,
                    args=(analysis,),
                    daemon=True
                )
                thread.start()
                
                with self._analysis_lock:
                    self._running_analyses[analysis_id] = thread
                
                return True, "Analysis started asynchronously"
            else:
                # Execute synchronously
                return self._execute_analysis_sync(analysis)
                
        except Exception as e:
            return self.handle_unexpected_error(e, "execute_analysis")
    
    def get_analysis(self, analysis_id: int) -> Tuple[bool, Optional[Analysis]]:
        """Get an analysis by ID."""
        return self.get_entity(analysis_id)
    
    def update_analysis(self, analysis: Analysis) -> Tuple[bool, bool]:
        """Update an analysis."""
        return self.update_entity(analysis)
    
    def delete_analysis(self, analysis_id: int) -> Tuple[bool, bool]:
        """Delete an analysis."""
        try:
            # Cancel if running
            self.cancel_analysis(analysis_id)
            return self.delete_entity(analysis_id)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "delete_analysis")
    
    def list_analyses(self, filters: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[Analysis]]:
        """List analyses with optional filters."""
        def operation():
            return self.analysis_repository.list(filters)
        
        return self.execute_with_logging(operation, "list_analyses")
    
    def get_analyses_by_project(self, project_id: int) -> Tuple[bool, List[Analysis]]:
        """Get all analyses for a project."""
        def operation():
            return self.analysis_repository.get_by_project(project_id)
        
        return self.execute_with_logging(operation, "get_analyses_by_project")
    
    def get_analyses_by_sequence(self, sequence_id: int) -> Tuple[bool, List[Analysis]]:
        """Get all analyses for a sequence."""
        def operation():
            return self.analysis_repository.get_by_sequence(sequence_id)
        
        return self.execute_with_logging(operation, "get_analyses_by_sequence")
    
    def get_running_analyses(self) -> Tuple[bool, List[Analysis]]:
        """Get all currently running analyses."""
        def operation():
            return self.analysis_repository.get_running_analyses()
        
        return self.execute_with_logging(operation, "get_running_analyses")
    
    def cancel_analysis(self, analysis_id: int) -> Tuple[bool, bool]:
        """Cancel a running analysis."""
        try:
            with self._analysis_lock:
                if analysis_id in self._running_analyses:
                    # Note: Python threads can't be forcibly terminated
                    # We can only mark the analysis as cancelled
                    del self._running_analyses[analysis_id]
            
            # Update analysis status
            analysis = self.analysis_repository.get_by_id(analysis_id)
            if analysis and analysis.status == "running":
                analysis.fail_execution("Analysis cancelled by user")
                self.analysis_repository.update(analysis)
                return True, True
            
            return False, "Analysis is not running"
            
        except Exception as e:
            return self.handle_unexpected_error(e, "cancel_analysis")
    
    def get_analysis_statistics(self, project_id: Optional[int] = None) -> Tuple[bool, Dict[str, Any]]:
        """Get analysis statistics."""
        def operation():
            return self.analysis_repository.get_analysis_statistics(project_id)
        
        return self.execute_with_logging(operation, "get_analysis_statistics")
    
    def get_available_analysis_types(self) -> List[Dict[str, Any]]:
        """Get list of available analysis types with descriptions."""
        return [
            {
                'type': 'gc_content',
                'name': 'GC Content Analysis',
                'description': 'Calculate GC percentage and base composition',
                'parameters': [],
                'sequence_types': ['dna']
            },
            {
                'type': 'pattern_match',
                'name': 'Pattern Matching',
                'description': 'Find pattern occurrences using Boyer-Moore algorithm',
                'parameters': [
                    {'name': 'pattern', 'type': 'string', 'required': True, 'description': 'Pattern to search for'}
                ],
                'sequence_types': ['dna', 'rna', 'protein']
            },
            {
                'type': 'translation',
                'name': 'DNA Translation',
                'description': 'Translate DNA sequence to protein',
                'parameters': [
                    {'name': 'frame', 'type': 'int', 'required': False, 'default': 0, 'description': 'Reading frame (0, 1, or 2)'}
                ],
                'sequence_types': ['dna', 'rna']
            },
            {
                'type': 'reverse_complement',
                'name': 'Reverse Complement',
                'description': 'Calculate reverse complement of DNA sequence',
                'parameters': [],
                'sequence_types': ['dna']
            },
            {
                'type': 'suffix_array',
                'name': 'Suffix Array',
                'description': 'Build suffix array for pattern searching',
                'parameters': [],
                'sequence_types': ['dna', 'rna', 'protein']
            },
            {
                'type': 'approximate_match',
                'name': 'Approximate Matching',
                'description': 'Find approximate pattern matches with edit distance',
                'parameters': [
                    {'name': 'pattern', 'type': 'string', 'required': True, 'description': 'Pattern to search for'},
                    {'name': 'max_distance', 'type': 'int', 'required': False, 'default': 1, 'description': 'Maximum edit distance'}
                ],
                'sequence_types': ['dna', 'rna', 'protein']
            },
            {
                'type': 'overlap_graph',
                'name': 'Overlap Graph',
                'description': 'Build overlap graph for sequence assembly',
                'parameters': [
                    {'name': 'min_overlap', 'type': 'int', 'required': False, 'default': 10, 'description': 'Minimum overlap length'}
                ],
                'sequence_types': ['dna']
            }
        ]
    
    def _execute_analysis_async(self, analysis: Analysis):
        """Execute analysis asynchronously."""
        try:
            # Mark as running
            analysis.start_execution()
            self.analysis_repository.update(analysis)
            
            # Execute analysis
            success, result = self._execute_analysis_sync(analysis)
            
            # Clean up running analyses tracking
            with self._analysis_lock:
                self._running_analyses.pop(analysis.id, None)
                
        except Exception as e:
            self.logger.error(f"Async analysis execution failed: {e}")
            analysis.fail_execution(str(e))
            self.analysis_repository.update(analysis)
    
    def _execute_analysis_sync(self, analysis: Analysis) -> Tuple[bool, Any]:
        """Execute analysis synchronously."""
        start_time = time.time()
        
        try:
            # Get sequence
            sequence = self.sequence_repository.get_by_id(analysis.sequence_id)
            if not sequence:
                raise ServiceError(f"Sequence {analysis.sequence_id} not found")
            
            # Mark as running
            analysis.start_execution()
            self.analysis_repository.update(analysis)
            
            # Execute based on analysis type
            results = self._execute_algorithm(analysis.analysis_type, sequence, analysis.parameters)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Mark as completed
            analysis.complete_execution(results, execution_time)
            self.analysis_repository.update(analysis)
            
            return True, results
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            # Mark as failed
            analysis.fail_execution(error_msg, execution_time)
            self.analysis_repository.update(analysis)
            
            return False, error_msg
    
    def _execute_algorithm(self, analysis_type: str, sequence: Sequence, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specific algorithm based on analysis type."""
        seq_data = sequence.sequence
        
        if analysis_type == "gc_content":
            gc_pct = algorithms.gc_percentage(seq_data)
            base_counts = {
                'A': seq_data.count('A'),
                'T': seq_data.count('T'),
                'C': seq_data.count('C'),
                'G': seq_data.count('G'),
                'N': seq_data.count('N')
            }
            
            return {
                'gc_percentage': round(gc_pct * 100, 2),
                'base_composition': base_counts,
                'sequence_length': len(seq_data)
            }
        
        elif analysis_type == "pattern_match":
            pattern = parameters.get('pattern', '')
            if not pattern:
                raise ValidationError("Pattern parameter is required")
            
            # Use Boyer-Moore algorithm
            matches = algorithms.boyer_moore_bad_char(seq_data, pattern)
            
            return {
                'pattern': pattern,
                'matches': matches,
                'match_count': len(matches),
                'sequence_length': len(seq_data)
            }
        
        elif analysis_type == "translation":
            if sequence.sequence_type not in ['dna', 'rna']:
                raise ValidationError("Translation only available for DNA/RNA sequences")
            
            frame = parameters.get('frame', 0)
            if frame not in [0, 1, 2]:
                raise ValidationError("Frame must be 0, 1, or 2")
            
            protein = sequence.translate_to_protein(frame)
            
            return {
                'frame': frame,
                'protein_sequence': protein,
                'protein_length': len(protein),
                'stop_codons': protein.count('*')
            }
        
        elif analysis_type == "reverse_complement":
            if sequence.sequence_type != 'dna':
                raise ValidationError("Reverse complement only available for DNA sequences")
            
            rev_comp = sequence.get_reverse_complement()
            
            return {
                'original_sequence': seq_data,
                'reverse_complement': rev_comp,
                'sequence_length': len(seq_data)
            }
        
        elif analysis_type == "suffix_array":
            suffix_array = algorithms.build_suffix_array(seq_data)
            
            return {
                'suffix_array': suffix_array,
                'sequence_length': len(seq_data),
                'array_length': len(suffix_array)
            }
        
        elif analysis_type == "approximate_match":
            pattern = parameters.get('pattern', '')
            max_distance = parameters.get('max_distance', 1)
            
            if not pattern:
                raise ValidationError("Pattern parameter is required")
            
            matches = algorithms.find_approximate_matches(seq_data, pattern, max_distance)
            
            return {
                'pattern': pattern,
                'max_distance': max_distance,
                'matches': matches,
                'match_count': len(matches),
                'sequence_length': len(seq_data)
            }
        
        elif analysis_type == "overlap_graph":
            min_overlap = parameters.get('min_overlap', 10)
            
            # For single sequence, create self-overlap analysis
            sequences = [seq_data]  # In real implementation, this would be multiple sequences
            graph = algorithms.build_overlap_graph(sequences, min_overlap)
            
            return {
                'min_overlap': min_overlap,
                'adjacency_list': graph,
                'node_count': len(sequences),
                'edge_count': sum(len(edges) for edges in graph.values())
            }
        
        else:
            raise ValidationError(f"Unknown analysis type: {analysis_type}")
    
    def _is_valid_analysis_type(self, analysis_type: str) -> bool:
        """Check if analysis type is valid."""
        valid_types = [
            'gc_content', 'pattern_match', 'translation', 'reverse_complement',
            'suffix_array', 'approximate_match', 'overlap_graph'
        ]
        return analysis_type in valid_types
    
    def get_analysis_summary(self, analysis_id: int) -> Tuple[bool, Dict[str, Any]]:
        """Get a summary of analysis information."""
        try:
            analysis = self.analysis_repository.get_by_id(analysis_id)
            if not analysis:
                return self.handle_not_found("Analysis", analysis_id)
            
            summary = {
                'id': analysis.id,
                'analysis_type': analysis.analysis_type,
                'status': analysis.status,
                'execution_time': analysis.execution_time,
                'created_date': analysis.created_date,
                'has_results': bool(analysis.results),
                'has_error': bool(analysis.error_message),
                'parameter_count': len(analysis.parameters)
            }
            
            return True, summary
            
        except Exception as e:
            return self.handle_unexpected_error(e, "get_analysis_summary")