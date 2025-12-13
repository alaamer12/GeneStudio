"""Pattern Matching ViewModel with algorithm selection and parameter configuration."""

from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass
import time
import threading

from viewmodels.base_viewmodel import BaseViewModel
from services.analysis_service import AnalysisService
from services.sequence_service import SequenceService
from services.project_service import ProjectService
from models.analysis_model import Analysis
import algorithms


@dataclass
class PatternMatchResult:
    """Pattern matching result with algorithm performance metrics."""
    sequence_id: str
    pattern: str
    algorithm: str
    matches: List[Dict[str, Any]]  # position, score, context
    execution_time: float
    memory_usage: float
    parameters: Dict[str, Any]
    statistics: Dict[str, Any]  # total_matches, avg_score, etc.
    
    def get_match_positions(self) -> List[int]:
        """Get list of match positions."""
        return [match['position'] for match in self.matches]


class PatternMatchingViewModel(BaseViewModel):
    """ViewModel for pattern matching algorithms with performance comparison."""
    
    def __init__(self):
        """Initialize pattern matching ViewModel."""
        super().__init__()
        
        # Services
        self.analysis_service = AnalysisService()
        self.sequence_service = SequenceService()
        self.project_service = ProjectService()
        
        # Initialize pattern matching state
        self._initialize_pattern_matching_state()
    
    def _initialize_pattern_matching_state(self):
        """Initialize pattern matching specific state."""
        self.update_state('available_algorithms', self._get_available_algorithms(), notify=False)
        self.update_state('selected_algorithm', None, notify=False)
        self.update_state('algorithm_parameters', {}, notify=False)
        self.update_state('parameter_errors', {}, notify=False)
        self.update_state('search_pattern', '', notify=False)
        self.update_state('selected_sequences', [], notify=False)
        self.update_state('available_sequences', [], notify=False)
        self.update_state('current_project', None, notify=False)
        self.update_state('search_results', [], notify=False)
        self.update_state('is_searching', False, notify=False)
        self.update_state('search_progress', 0.0, notify=False)
        self.update_state('performance_comparison', {}, notify=False)
        self.update_state('show_performance_stats', True, notify=False)
        self.update_state('highlight_matches', True, notify=False)
        self.update_state('case_sensitive', False, notify=False)
        self.update_state('running_analyses', {}, notify=False)
        self.update_state('export_formats', ['CSV', 'JSON', 'TXT', 'HTML'], notify=False)
    
    def _get_available_algorithms(self) -> List[Dict[str, Any]]:
        """Get available pattern matching algorithms with metadata."""
        return [
            {
                'id': 'boyer_moore_bad_char',
                'name': 'Boyer-Moore (Bad Character)',
                'description': 'Fast pattern matching using bad character rule',
                'complexity': 'O(n/m) average, O(nm) worst case',
                'best_for': 'Long patterns, large texts',
                'preprocessing': 'O(m + σ) where σ is alphabet size',
                'icon': '🚀',
                'parameters': [
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
                'id': 'boyer_moore_good_suffix',
                'name': 'Boyer-Moore (Good Suffix)',
                'description': 'Boyer-Moore with both bad character and good suffix rules',
                'complexity': 'O(n) worst case, O(n/m) average',
                'best_for': 'Repetitive patterns, guaranteed performance',
                'preprocessing': 'O(m)',
                'icon': '⚡',
                'parameters': [
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
                'id': 'suffix_array',
                'name': 'Suffix Array',
                'description': 'Pattern matching using pre-built suffix array',
                'complexity': 'O(m log n) search after O(n log n) preprocessing',
                'best_for': 'Multiple searches on same text',
                'preprocessing': 'O(n log n)',
                'icon': '📊',
                'parameters': [
                    {
                        'name': 'build_lcp',
                        'label': 'Build LCP Array',
                        'type': 'boolean',
                        'default': False,
                        'description': 'Build Longest Common Prefix array for enhanced searching'
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
                'id': 'kmp',
                'name': 'KMP (Knuth-Morris-Pratt)',
                'description': 'Linear time pattern matching with failure function',
                'complexity': 'O(n + m) guaranteed',
                'best_for': 'Repetitive patterns, guaranteed linear time',
                'preprocessing': 'O(m)',
                'icon': '🎯',
                'parameters': [
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
                'id': 'naive',
                'name': 'Naive (Brute Force)',
                'description': 'Simple brute-force pattern matching',
                'complexity': 'O(nm) always',
                'best_for': 'Educational purposes, very short patterns',
                'preprocessing': 'None',
                'icon': '🔍',
                'parameters': [
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
                'id': 'approximate',
                'name': 'Approximate Matching',
                'description': 'Find approximate matches with edit distance',
                'complexity': 'O(nm × k) where k is max distance',
                'best_for': 'Fuzzy matching, sequence variants',
                'preprocessing': 'None',
                'icon': '🎲',
                'parameters': [
                    {
                        'name': 'max_distance',
                        'label': 'Max Edit Distance',
                        'type': 'integer',
                        'default': 1,
                        'min': 0,
                        'max': 10,
                        'description': 'Maximum allowed edit distance for matches'
                    },
                    {
                        'name': 'distance_type',
                        'label': 'Distance Type',
                        'type': 'choice',
                        'choices': ['edit', 'hamming'],
                        'default': 'edit',
                        'description': 'Type of distance metric to use'
                    },
                    {
                        'name': 'case_sensitive',
                        'label': 'Case Sensitive',
                        'type': 'boolean',
                        'default': False,
                        'description': 'Whether to perform case-sensitive matching'
                    }
                ]
            }
        ]
    
    def select_algorithm(self, algorithm_id: str):
        """Select pattern matching algorithm and load parameters."""
        algorithms = self.get_state('available_algorithms', [])
        selected_algorithm = None
        
        for algorithm in algorithms:
            if algorithm['id'] == algorithm_id:
                selected_algorithm = algorithm
                break
        
        if selected_algorithm:
            self.update_state('selected_algorithm', selected_algorithm)
            
            # Reset parameters to defaults
            default_params = {}
            for param in selected_algorithm.get('parameters', []):
                if 'default' in param:
                    default_params[param['name']] = param['default']
            
            self.update_state('algorithm_parameters', default_params)
            self.update_state('parameter_errors', {})
            
            self.log_action("select_algorithm", {'algorithm_id': algorithm_id})
    
    def set_algorithm_parameter(self, param_name: str, value: Any):
        """Set algorithm parameter value."""
        parameters = self.get_state('algorithm_parameters', {}).copy()
        parameters[param_name] = value
        self.update_state('algorithm_parameters', parameters)
        
        # Validate parameter
        self._validate_parameter(param_name, value)
    
    def set_search_pattern(self, pattern: str):
        """Set the search pattern."""
        self.update_state('search_pattern', pattern)
        
        # Clear previous results when pattern changes
        if pattern != self.get_state('search_pattern', ''):
            self.update_state('search_results', [])
            self.update_state('performance_comparison', {})
    
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
            # Clear selected sequences when project changes
            self.update_state('selected_sequences', [])
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to load project: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("load_project", load_project_operation, on_success, on_error)
    
    def select_sequences(self, sequence_ids: List[int]):
        """Select sequences for pattern matching."""
        available_sequences = self.get_state('available_sequences', [])
        selected_sequences = [seq for seq in available_sequences if seq.id in sequence_ids]
        self.update_state('selected_sequences', selected_sequences)
    
    def execute_pattern_search(self, compare_algorithms: bool = False):
        """Execute pattern matching with progress tracking and cancellation support."""
        pattern = self.get_state('search_pattern', '').strip()
        selected_algorithm = self.get_state('selected_algorithm')
        selected_sequences = self.get_state('selected_sequences', [])
        parameters = self.get_state('algorithm_parameters', {})
        
        # Validation
        if not pattern:
            try:
                from views.components.toast_notifications import show_error
                show_error("Please enter a search pattern")
            except ImportError:
                pass
            return
        
        if not selected_algorithm:
            try:
                from views.components.toast_notifications import show_error
                show_error("Please select an algorithm")
            except ImportError:
                pass
            return
        
        if not selected_sequences:
            try:
                from views.components.toast_notifications import show_error
                show_error("Please select sequences to search")
            except ImportError:
                pass
            return
        
        # Validate parameters
        if not self._validate_all_parameters():
            return
        
        self.log_action("execute_pattern_search", {
            'pattern': pattern,
            'algorithm': selected_algorithm['id'],
            'sequence_count': len(selected_sequences),
            'compare_algorithms': compare_algorithms
        })
        
        if compare_algorithms:
            self._execute_algorithm_comparison(pattern, selected_sequences, parameters)
        else:
            self._execute_single_algorithm(pattern, selected_algorithm, selected_sequences, parameters)
    
    def cancel_pattern_search(self):
        """Cancel running pattern search."""
        running_analyses = self.get_state('running_analyses', {})
        
        for analysis_id in list(running_analyses.keys()):
            success, result = self.analysis_service.cancel_analysis(analysis_id)
            if success:
                del running_analyses[analysis_id]
        
        self.update_state('running_analyses', running_analyses)
        self.update_state('is_searching', False)
        self.update_state('search_progress', 0.0)
        
        try:
            from views.components.toast_notifications import show_info
            show_info("Pattern search cancelled")
        except ImportError:
            pass
    
    def export_results(self, format_type: str, include_performance: bool = True):
        """Export pattern matching results in specified format."""
        results = self.get_state('search_results', [])
        performance_data = self.get_state('performance_comparison', {})
        
        if not results:
            try:
                from views.components.toast_notifications import show_error
                show_error("No results to export")
            except ImportError:
                pass
            return
        
        self.log_action("export_results", {
            'format': format_type,
            'result_count': len(results),
            'include_performance': include_performance
        })
        
        def export_operation():
            return self._generate_export_data(results, performance_data, format_type, include_performance)
        
        def on_success(export_data):
            # Save export data to file
            filename = self._save_export_file(export_data, format_type)
            
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Results exported to {filename}")
            except ImportError:
                pass
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Export failed: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("export_results", export_operation, on_success, on_error)
    
    def get_algorithm_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for algorithm comparison."""
        performance_data = self.get_state('performance_comparison', {})
        
        if not performance_data:
            return {}
        
        summary = {
            'algorithms_compared': len(performance_data),
            'fastest_algorithm': None,
            'most_accurate': None,
            'memory_efficient': None
        }
        
        # Find fastest algorithm
        fastest_time = float('inf')
        for algo_id, data in performance_data.items():
            if data['execution_time'] < fastest_time:
                fastest_time = data['execution_time']
                summary['fastest_algorithm'] = algo_id
        
        # Find most accurate (most matches found)
        max_matches = 0
        for algo_id, data in performance_data.items():
            total_matches = sum(len(result['matches']) for result in data['results'])
            if total_matches > max_matches:
                max_matches = total_matches
                summary['most_accurate'] = algo_id
        
        # Find most memory efficient
        min_memory = float('inf')
        for algo_id, data in performance_data.items():
            if data['memory_usage'] < min_memory:
                min_memory = data['memory_usage']
                summary['memory_efficient'] = algo_id
        
        return summary
    
    def get_search_summary(self) -> Dict[str, Any]:
        """Get search summary information."""
        results = self.get_state('search_results', [])
        pattern = self.get_state('search_pattern', '')
        selected_algorithm = self.get_state('selected_algorithm')
        
        total_matches = sum(len(result.get('matches', [])) for result in results)
        
        return {
            'pattern': pattern,
            'algorithm': selected_algorithm['name'] if selected_algorithm else 'None',
            'sequences_searched': len(self.get_state('selected_sequences', [])),
            'total_matches': total_matches,
            'results_count': len(results),
            'is_searching': self.get_state('is_searching', False),
            'has_performance_data': bool(self.get_state('performance_comparison', {}))
        }
    
    def _execute_single_algorithm(self, pattern: str, algorithm: Dict[str, Any], 
                                 sequences: List[Any], parameters: Dict[str, Any]):
        """Execute pattern matching with a single algorithm."""
        def search_operation():
            results = []
            start_time = time.time()
            
            for sequence in sequences:
                # Prepare sequence text
                seq_text = sequence.sequence
                if not parameters.get('case_sensitive', False):
                    seq_text = seq_text.upper()
                    pattern_text = pattern.upper()
                else:
                    pattern_text = pattern
                
                # Execute algorithm
                matches = self._execute_algorithm(algorithm['id'], seq_text, pattern_text, parameters)
                
                # Process matches
                processed_matches = []
                for match_pos in matches:
                    context_start = max(0, match_pos - 10)
                    context_end = min(len(seq_text), match_pos + len(pattern_text) + 10)
                    context = seq_text[context_start:context_end]
                    
                    processed_matches.append({
                        'position': match_pos,
                        'match_text': seq_text[match_pos:match_pos + len(pattern_text)],
                        'context': context,
                        'score': 100.0  # Exact match score
                    })
                
                results.append({
                    'sequence_id': sequence.id,
                    'sequence_header': sequence.header,
                    'matches': processed_matches,
                    'match_count': len(processed_matches)
                })
            
            execution_time = time.time() - start_time
            
            return {
                'results': results,
                'execution_time': execution_time,
                'algorithm': algorithm['id'],
                'pattern': pattern,
                'parameters': parameters
            }
        
        def on_success(result):
            self.update_state('search_results', result['results'])
            self.update_state('is_searching', False)
            self.update_state('search_progress', 100.0)
            
            # Store performance data
            performance_data = {
                algorithm['id']: {
                    'execution_time': result['execution_time'],
                    'memory_usage': 0,  # Would need memory profiling
                    'results': result['results']
                }
            }
            self.update_state('performance_comparison', performance_data)
            
            total_matches = sum(len(r['matches']) for r in result['results'])
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Pattern search completed: {total_matches} matches found in {result['execution_time']:.3f}s")
            except ImportError:
                pass
        
        def on_error(error):
            self.update_state('is_searching', False)
            self.update_state('search_progress', 0.0)
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Pattern search failed: {error}")
            except ImportError:
                pass
        
        # Set searching state
        self.update_state('is_searching', True)
        self.update_state('search_progress', 0.0)
        
        # Execute search
        self.execute_async_operation("pattern_search", search_operation, on_success, on_error)
    
    def _execute_algorithm_comparison(self, pattern: str, sequences: List[Any], parameters: Dict[str, Any]):
        """Execute pattern matching with multiple algorithms for comparison."""
        algorithms = self.get_state('available_algorithms', [])
        
        def comparison_operation():
            comparison_results = {}
            
            for algorithm in algorithms:
                if algorithm['id'] == 'approximate':
                    continue  # Skip approximate for comparison
                
                start_time = time.time()
                results = []
                
                for sequence in sequences:
                    # Prepare sequence text
                    seq_text = sequence.sequence
                    if not parameters.get('case_sensitive', False):
                        seq_text = seq_text.upper()
                        pattern_text = pattern.upper()
                    else:
                        pattern_text = pattern
                    
                    # Execute algorithm
                    matches = self._execute_algorithm(algorithm['id'], seq_text, pattern_text, parameters)
                    
                    # Process matches
                    processed_matches = []
                    for match_pos in matches:
                        context_start = max(0, match_pos - 10)
                        context_end = min(len(seq_text), match_pos + len(pattern_text) + 10)
                        context = seq_text[context_start:context_end]
                        
                        processed_matches.append({
                            'position': match_pos,
                            'match_text': seq_text[match_pos:match_pos + len(pattern_text)],
                            'context': context,
                            'score': 100.0
                        })
                    
                    results.append({
                        'sequence_id': sequence.id,
                        'sequence_header': sequence.header,
                        'matches': processed_matches,
                        'match_count': len(processed_matches)
                    })
                
                execution_time = time.time() - start_time
                
                comparison_results[algorithm['id']] = {
                    'execution_time': execution_time,
                    'memory_usage': 0,  # Would need memory profiling
                    'results': results,
                    'algorithm_name': algorithm['name']
                }
            
            return comparison_results
        
        def on_success(comparison_results):
            self.update_state('performance_comparison', comparison_results)
            self.update_state('is_searching', False)
            self.update_state('search_progress', 100.0)
            
            # Use results from fastest algorithm as main results
            fastest_algo = min(comparison_results.keys(), 
                             key=lambda k: comparison_results[k]['execution_time'])
            self.update_state('search_results', comparison_results[fastest_algo]['results'])
            
            try:
                from views.components.toast_notifications import show_success
                show_success(f"Algorithm comparison completed: {len(comparison_results)} algorithms tested")
            except ImportError:
                pass
        
        def on_error(error):
            self.update_state('is_searching', False)
            self.update_state('search_progress', 0.0)
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Algorithm comparison failed: {error}")
            except ImportError:
                pass
        
        # Set searching state
        self.update_state('is_searching', True)
        self.update_state('search_progress', 0.0)
        
        # Execute comparison
        self.execute_async_operation("algorithm_comparison", comparison_operation, on_success, on_error)
    
    def _execute_algorithm(self, algorithm_id: str, text: str, pattern: str, parameters: Dict[str, Any]) -> List[int]:
        """Execute specific pattern matching algorithm."""
        if algorithm_id == 'boyer_moore_bad_char':
            return algorithms.boyer_moore_bad_char(text, pattern)
        elif algorithm_id == 'boyer_moore_good_suffix':
            return algorithms.boyer_moore_good_suffix(text, pattern)
        elif algorithm_id == 'suffix_array':
            # For suffix array, we need to implement search functionality
            suffix_array = algorithms.build_suffix_array(text)
            return self._suffix_array_search(text, pattern, suffix_array)
        elif algorithm_id == 'kmp':
            return self._kmp_search(text, pattern)
        elif algorithm_id == 'naive':
            return self._naive_search(text, pattern)
        elif algorithm_id == 'approximate':
            max_distance = parameters.get('max_distance', 1)
            distance_type = parameters.get('distance_type', 'edit')
            return algorithms.find_approximate_matches(text, pattern, max_dist=max_distance, method=distance_type)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_id}")
    
    def _suffix_array_search(self, text: str, pattern: str, suffix_array: List[int]) -> List[int]:
        """Search using suffix array (binary search)."""
        matches = []
        n = len(text)
        m = len(pattern)
        
        # Binary search for pattern in suffix array
        left, right = 0, len(suffix_array) - 1
        
        while left <= right:
            mid = (left + right) // 2
            suffix_start = suffix_array[mid]
            
            if suffix_start + m > n:
                suffix = text[suffix_start:]
            else:
                suffix = text[suffix_start:suffix_start + m]
            
            if suffix == pattern:
                # Found match, collect all matches
                matches.append(suffix_start)
                
                # Search left for more matches
                i = mid - 1
                while i >= 0:
                    suffix_start = suffix_array[i]
                    if suffix_start + m <= n and text[suffix_start:suffix_start + m] == pattern:
                        matches.append(suffix_start)
                        i -= 1
                    else:
                        break
                
                # Search right for more matches
                i = mid + 1
                while i < len(suffix_array):
                    suffix_start = suffix_array[i]
                    if suffix_start + m <= n and text[suffix_start:suffix_start + m] == pattern:
                        matches.append(suffix_start)
                        i += 1
                    else:
                        break
                
                break
            elif suffix < pattern:
                left = mid + 1
            else:
                right = mid - 1
        
        return sorted(matches)
    
    def _kmp_search(self, text: str, pattern: str) -> List[int]:
        """KMP pattern matching algorithm."""
        def compute_lps(pattern):
            m = len(pattern)
            lps = [0] * m
            length = 0
            i = 1
            
            while i < m:
                if pattern[i] == pattern[length]:
                    length += 1
                    lps[i] = length
                    i += 1
                else:
                    if length != 0:
                        length = lps[length - 1]
                    else:
                        lps[i] = 0
                        i += 1
            return lps
        
        matches = []
        n = len(text)
        m = len(pattern)
        
        if m == 0:
            return matches
        
        lps = compute_lps(pattern)
        i = j = 0
        
        while i < n:
            if pattern[j] == text[i]:
                i += 1
                j += 1
            
            if j == m:
                matches.append(i - j)
                j = lps[j - 1]
            elif i < n and pattern[j] != text[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        
        return matches
    
    def _naive_search(self, text: str, pattern: str) -> List[int]:
        """Naive pattern matching algorithm."""
        matches = []
        n = len(text)
        m = len(pattern)
        
        for i in range(n - m + 1):
            if text[i:i + m] == pattern:
                matches.append(i)
        
        return matches
    
    def _validate_parameter(self, param_name: str, value: Any):
        """Validate a single parameter."""
        selected_algorithm = self.get_state('selected_algorithm')
        if not selected_algorithm:
            return
        
        errors = self.get_state('parameter_errors', {}).copy()
        
        # Find parameter definition
        param_def = None
        for param in selected_algorithm.get('parameters', []):
            if param['name'] == param_name:
                param_def = param
                break
        
        if not param_def:
            return
        
        # Validate based on type
        param_type = param_def.get('type', 'string')
        
        if param_type == 'integer':
            try:
                int_value = int(value)
                if 'min' in param_def and int_value < param_def['min']:
                    errors[param_name] = f'Value must be at least {param_def["min"]}'
                elif 'max' in param_def and int_value > param_def['max']:
                    errors[param_name] = f'Value must be at most {param_def["max"]}'
                else:
                    errors.pop(param_name, None)
            except ValueError:
                errors[param_name] = 'Must be a valid integer'
        
        elif param_type == 'choice':
            choices = param_def.get('choices', [])
            if value not in choices:
                errors[param_name] = f'Must be one of: {choices}'
            else:
                errors.pop(param_name, None)
        
        else:
            errors.pop(param_name, None)
        
        self.update_state('parameter_errors', errors)
    
    def _validate_all_parameters(self) -> bool:
        """Validate all algorithm parameters."""
        selected_algorithm = self.get_state('selected_algorithm')
        parameters = self.get_state('algorithm_parameters', {})
        
        if not selected_algorithm:
            return False
        
        errors = {}
        
        for param_def in selected_algorithm.get('parameters', []):
            param_name = param_def['name']
            param_value = parameters.get(param_name)
            
            # Check required parameters
            if param_def.get('required', False) and param_value is None:
                errors[param_name] = 'This parameter is required'
        
        self.update_state('parameter_errors', errors)
        
        if errors:
            try:
                from views.components.toast_notifications import show_error
                show_error("Please fix parameter errors before searching")
            except ImportError:
                pass
            return False
        
        return True
    
    def _generate_export_data(self, results: List[Dict[str, Any]], performance_data: Dict[str, Any], 
                             format_type: str, include_performance: bool) -> str:
        """Generate export data in specified format."""
        if format_type == 'CSV':
            return self._generate_csv_export(results, performance_data, include_performance)
        elif format_type == 'JSON':
            return self._generate_json_export(results, performance_data, include_performance)
        elif format_type == 'TXT':
            return self._generate_txt_export(results, performance_data, include_performance)
        elif format_type == 'HTML':
            return self._generate_html_export(results, performance_data, include_performance)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _generate_csv_export(self, results: List[Dict[str, Any]], performance_data: Dict[str, Any], 
                            include_performance: bool) -> str:
        """Generate CSV export data."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Sequence ID', 'Sequence Header', 'Position', 'Match Text', 'Context', 'Score'])
        
        # Write match data
        for result in results:
            for match in result['matches']:
                writer.writerow([
                    result['sequence_id'],
                    result['sequence_header'],
                    match['position'],
                    match['match_text'],
                    match['context'],
                    match['score']
                ])
        
        # Write performance data if requested
        if include_performance and performance_data:
            writer.writerow([])  # Empty row
            writer.writerow(['Algorithm Performance'])
            writer.writerow(['Algorithm', 'Execution Time (s)', 'Memory Usage (MB)', 'Total Matches'])
            
            for algo_id, data in performance_data.items():
                total_matches = sum(len(r['matches']) for r in data['results'])
                writer.writerow([
                    algo_id,
                    f"{data['execution_time']:.6f}",
                    f"{data['memory_usage']:.2f}",
                    total_matches
                ])
        
        return output.getvalue()
    
    def _generate_json_export(self, results: List[Dict[str, Any]], performance_data: Dict[str, Any], 
                             include_performance: bool) -> str:
        """Generate JSON export data."""
        import json
        
        export_data = {
            'search_results': results,
            'export_timestamp': datetime.now().isoformat(),
            'pattern': self.get_state('search_pattern', ''),
            'algorithm': self.get_state('selected_algorithm', {}).get('id', 'unknown')
        }
        
        if include_performance and performance_data:
            export_data['performance_data'] = performance_data
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def _generate_txt_export(self, results: List[Dict[str, Any]], performance_data: Dict[str, Any], 
                            include_performance: bool) -> str:
        """Generate plain text export data."""
        lines = []
        lines.append("Pattern Matching Results")
        lines.append("=" * 50)
        lines.append(f"Pattern: {self.get_state('search_pattern', '')}")
        lines.append(f"Algorithm: {self.get_state('selected_algorithm', {}).get('name', 'Unknown')}")
        lines.append(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        for result in results:
            lines.append(f"Sequence: {result['sequence_header']} (ID: {result['sequence_id']})")
            lines.append(f"Matches found: {result['match_count']}")
            lines.append("-" * 30)
            
            for i, match in enumerate(result['matches'], 1):
                lines.append(f"  Match {i}:")
                lines.append(f"    Position: {match['position']}")
                lines.append(f"    Text: {match['match_text']}")
                lines.append(f"    Context: {match['context']}")
                lines.append(f"    Score: {match['score']}%")
                lines.append("")
        
        if include_performance and performance_data:
            lines.append("Performance Comparison")
            lines.append("=" * 50)
            
            for algo_id, data in performance_data.items():
                total_matches = sum(len(r['matches']) for r in data['results'])
                lines.append(f"Algorithm: {algo_id}")
                lines.append(f"  Execution Time: {data['execution_time']:.6f} seconds")
                lines.append(f"  Memory Usage: {data['memory_usage']:.2f} MB")
                lines.append(f"  Total Matches: {total_matches}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html_export(self, results: List[Dict[str, Any]], performance_data: Dict[str, Any], 
                             include_performance: bool) -> str:
        """Generate HTML export data."""
        html_parts = []
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html><head><title>Pattern Matching Results</title>")
        html_parts.append("<style>")
        html_parts.append("body { font-family: Arial, sans-serif; margin: 20px; }")
        html_parts.append("table { border-collapse: collapse; width: 100%; margin: 20px 0; }")
        html_parts.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html_parts.append("th { background-color: #f2f2f2; }")
        html_parts.append(".match-text { font-family: monospace; background-color: #ffffcc; }")
        html_parts.append("</style></head><body>")
        
        html_parts.append("<h1>Pattern Matching Results</h1>")
        html_parts.append(f"<p><strong>Pattern:</strong> {self.get_state('search_pattern', '')}</p>")
        html_parts.append(f"<p><strong>Algorithm:</strong> {self.get_state('selected_algorithm', {}).get('name', 'Unknown')}</p>")
        html_parts.append(f"<p><strong>Export Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        html_parts.append("<h2>Match Results</h2>")
        html_parts.append("<table>")
        html_parts.append("<tr><th>Sequence</th><th>Position</th><th>Match</th><th>Context</th><th>Score</th></tr>")
        
        for result in results:
            for match in result['matches']:
                html_parts.append("<tr>")
                html_parts.append(f"<td>{result['sequence_header']}</td>")
                html_parts.append(f"<td>{match['position']}</td>")
                html_parts.append(f"<td class='match-text'>{match['match_text']}</td>")
                html_parts.append(f"<td class='match-text'>{match['context']}</td>")
                html_parts.append(f"<td>{match['score']}%</td>")
                html_parts.append("</tr>")
        
        html_parts.append("</table>")
        
        if include_performance and performance_data:
            html_parts.append("<h2>Performance Comparison</h2>")
            html_parts.append("<table>")
            html_parts.append("<tr><th>Algorithm</th><th>Execution Time (s)</th><th>Memory Usage (MB)</th><th>Total Matches</th></tr>")
            
            for algo_id, data in performance_data.items():
                total_matches = sum(len(r['matches']) for r in data['results'])
                html_parts.append("<tr>")
                html_parts.append(f"<td>{algo_id}</td>")
                html_parts.append(f"<td>{data['execution_time']:.6f}</td>")
                html_parts.append(f"<td>{data['memory_usage']:.2f}</td>")
                html_parts.append(f"<td>{total_matches}</td>")
                html_parts.append("</tr>")
            
            html_parts.append("</table>")
        
        html_parts.append("</body></html>")
        
        return "\n".join(html_parts)
    
    def _save_export_file(self, export_data: str, format_type: str) -> str:
        """Save export data to file and return filename."""
        import os
        from utils.platform_dirs import get_app_data_dir
        
        # Create exports directory
        exports_dir = os.path.join(get_app_data_dir(), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pattern = self.get_state('search_pattern', 'pattern').replace(' ', '_')[:20]
        filename = f"pattern_search_{pattern}_{timestamp}.{format_type.lower()}"
        filepath = os.path.join(exports_dir, filename)
        
        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(export_data)
        
        return filename