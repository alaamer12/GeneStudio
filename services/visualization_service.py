"""Visualization service with plot data binding and real-time update capabilities."""

from typing import Optional, List, Dict, Any, Tuple, Callable, Union
import numpy as np
from datetime import datetime
import threading
import time
from pathlib import Path

from services.base_service import BaseService, ValidationError, ServiceError
from repositories.sequence_repository import SequenceRepository
from repositories.analysis_repository import AnalysisRepository
from models.sequence_model_enhanced import Sequence
from models.analysis_model import Analysis
from utils.logger import get_logger


class VisualizationService(BaseService):
    """Service for visualization data binding and plot management."""
    
    def __init__(self):
        """Initialize visualization service."""
        # Use sequence repository as base for now
        super().__init__(SequenceRepository())
        self.sequence_repository = SequenceRepository()
        self.analysis_repository = AnalysisRepository()
        self.logger = get_logger(self.__class__.__name__)
        
        # Data binding registry
        self._data_bindings = {}  # plot_id -> data_source_config
        self._plot_cache = {}     # plot_id -> cached_data
        self._update_callbacks = {}  # plot_id -> callback_function
        self._binding_lock = threading.Lock()
        
        # Supported plot types
        self.supported_plot_types = [
            'line', 'bar', 'scatter', 'heatmap', 'pie', 'donut', 
            'area', '3d_surface', '3d_scatter', '3d_graph'
        ]
        
        # Export formats
        self.export_formats = ['png', 'svg', 'pdf', 'eps', 'jpg']
    
    def create_plot_configuration(self, plot_type: str, data_sources: List[Dict[str, Any]], 
                                 config: Dict[str, Any]) -> Tuple[bool, str]:
        """Create a new plot configuration."""
        def operation():
            # Validate plot type
            if plot_type not in self.supported_plot_types:
                raise ValidationError(f"Unsupported plot type: {plot_type}")
            
            # Validate data sources
            if not data_sources:
                raise ValidationError("At least one data source is required")
            
            for source in data_sources:
                if not self._validate_data_source(source):
                    raise ValidationError(f"Invalid data source configuration: {source}")
            
            # Generate unique plot ID
            plot_id = f"{plot_type}_{int(time.time() * 1000)}"
            
            # Create plot configuration
            plot_config = {
                'id': plot_id,
                'type': plot_type,
                'data_sources': data_sources,
                'config': config,
                'created_at': datetime.now(),
                'last_updated': datetime.now()
            }
            
            # Store configuration
            with self._binding_lock:
                self._data_bindings[plot_id] = plot_config
            
            return plot_id
        
        return self.execute_with_logging(operation, "create_plot_configuration")
    
    def bind_real_time_data(self, plot_id: str, update_callback: Callable) -> Tuple[bool, str]:
        """Bind real-time data updates to a plot."""
        try:
            if plot_id not in self._data_bindings:
                return False, f"Plot {plot_id} not found"
            
            with self._binding_lock:
                self._update_callbacks[plot_id] = update_callback
            
            # Start monitoring data changes
            self._start_data_monitoring(plot_id)
            
            return True, "Real-time binding established"
            
        except Exception as e:
            return self.handle_unexpected_error(e, "bind_real_time_data")
    
    def update_plot_data(self, plot_id: str, force_refresh: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """Update plot data from bound sources."""
        def operation():
            if plot_id not in self._data_bindings:
                raise ValidationError(f"Plot {plot_id} not found")
            
            plot_config = self._data_bindings[plot_id]
            
            # Check cache if not forcing refresh
            if not force_refresh and plot_id in self._plot_cache:
                cached_data = self._plot_cache[plot_id]
                cache_age = (datetime.now() - cached_data['timestamp']).total_seconds()
                if cache_age < 30:  # Use cache if less than 30 seconds old
                    return cached_data['data']
            
            # Fetch fresh data
            plot_data = self._fetch_plot_data(plot_config)
            
            # Update cache
            with self._binding_lock:
                self._plot_cache[plot_id] = {
                    'data': plot_data,
                    'timestamp': datetime.now()
                }
                self._data_bindings[plot_id]['last_updated'] = datetime.now()
            
            # Trigger callback if registered
            if plot_id in self._update_callbacks:
                try:
                    self._update_callbacks[plot_id](plot_data)
                except Exception as e:
                    self.logger.warning(f"Plot update callback failed: {e}")
            
            return plot_data
        
        return self.execute_with_logging(operation, "update_plot_data")
    
    def get_plot_data(self, plot_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Get current plot data."""
        try:
            if plot_id not in self._data_bindings:
                return False, f"Plot {plot_id} not found"
            
            # Try cache first
            if plot_id in self._plot_cache:
                return True, self._plot_cache[plot_id]['data']
            
            # Fetch fresh data
            return self.update_plot_data(plot_id)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "get_plot_data")
    
    def combine_data_sources(self, source_configs: List[Dict[str, Any]], 
                           combination_type: str = 'merge') -> Tuple[bool, Dict[str, Any]]:
        """Combine multiple data sources for comparative visualizations."""
        def operation():
            if not source_configs:
                raise ValidationError("No data sources provided")
            
            combined_data = {}
            
            if combination_type == 'merge':
                # Merge data from multiple sources
                for i, source_config in enumerate(source_configs):
                    source_data = self._fetch_single_data_source(source_config)
                    
                    # Add source identifier to data
                    for key, value in source_data.items():
                        combined_key = f"{key}_source_{i}"
                        combined_data[combined_key] = value
            
            elif combination_type == 'overlay':
                # Overlay data (same x-axis, multiple y-series)
                base_data = self._fetch_single_data_source(source_configs[0])
                combined_data = base_data.copy()
                
                for i, source_config in enumerate(source_configs[1:], 1):
                    source_data = self._fetch_single_data_source(source_config)
                    
                    # Add additional y-series
                    if 'y_data' in source_data:
                        combined_data[f'y_data_{i}'] = source_data['y_data']
                    if 'labels' in source_data:
                        combined_data[f'labels_{i}'] = source_data['labels']
            
            elif combination_type == 'compare':
                # Side-by-side comparison
                combined_data['sources'] = []
                for source_config in source_configs:
                    source_data = self._fetch_single_data_source(source_config)
                    combined_data['sources'].append(source_data)
            
            else:
                raise ValidationError(f"Unknown combination type: {combination_type}")
            
            combined_data['combination_type'] = combination_type
            combined_data['source_count'] = len(source_configs)
            
            return combined_data
        
        return self.execute_with_logging(operation, "combine_data_sources")
    
    def export_plot(self, plot_id: str, format_type: str, output_path: str, 
                   export_options: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Export plot as high-quality image."""
        def operation():
            if plot_id not in self._data_bindings:
                raise ValidationError(f"Plot {plot_id} not found")
            
            if format_type not in self.export_formats:
                raise ValidationError(f"Unsupported export format: {format_type}")
            
            # Get plot data
            success, plot_data = self.get_plot_data(plot_id)
            if not success:
                raise ServiceError(f"Failed to get plot data: {plot_data}")
            
            # Get plot configuration
            plot_config = self._data_bindings[plot_id]
            
            # Set up export options
            options = export_options or {}
            resolution = options.get('resolution', (1920, 1080))
            dpi = options.get('dpi', 300)
            
            # Create output path
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Export based on plot type
            export_path = self._export_plot_image(
                plot_config, plot_data, output_file, format_type, resolution, dpi
            )
            
            return export_path
        
        return self.execute_with_logging(operation, "export_plot")
    
    def get_plot_statistics(self, plot_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Get statistics about a plot."""
        try:
            if plot_id not in self._data_bindings:
                return False, f"Plot {plot_id} not found"
            
            plot_config = self._data_bindings[plot_id]
            
            # Get plot data
            success, plot_data = self.get_plot_data(plot_id)
            if not success:
                return False, f"Failed to get plot data: {plot_data}"
            
            # Calculate statistics
            stats = {
                'plot_id': plot_id,
                'plot_type': plot_config['type'],
                'data_source_count': len(plot_config['data_sources']),
                'created_at': plot_config['created_at'],
                'last_updated': plot_config['last_updated'],
                'has_real_time_binding': plot_id in self._update_callbacks,
                'cache_status': 'cached' if plot_id in self._plot_cache else 'not_cached'
            }
            
            # Add data-specific statistics
            if plot_data:
                stats.update(self._calculate_data_statistics(plot_data))
            
            return True, stats
            
        except Exception as e:
            return self.handle_unexpected_error(e, "get_plot_statistics")
    
    def remove_plot(self, plot_id: str) -> Tuple[bool, str]:
        """Remove a plot and clean up resources."""
        try:
            if plot_id not in self._data_bindings:
                return False, f"Plot {plot_id} not found"
            
            with self._binding_lock:
                # Remove from all registries
                self._data_bindings.pop(plot_id, None)
                self._plot_cache.pop(plot_id, None)
                self._update_callbacks.pop(plot_id, None)
            
            return True, "Plot removed successfully"
            
        except Exception as e:
            return self.handle_unexpected_error(e, "remove_plot")
    
    def list_active_plots(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """List all active plots."""
        try:
            plots = []
            
            with self._binding_lock:
                for plot_id, config in self._data_bindings.items():
                    plot_info = {
                        'id': plot_id,
                        'type': config['type'],
                        'created_at': config['created_at'],
                        'last_updated': config['last_updated'],
                        'data_source_count': len(config['data_sources']),
                        'has_real_time_binding': plot_id in self._update_callbacks,
                        'is_cached': plot_id in self._plot_cache
                    }
                    plots.append(plot_info)
            
            return True, plots
            
        except Exception as e:
            return self.handle_unexpected_error(e, "list_active_plots")
    
    def _validate_data_source(self, source: Dict[str, Any]) -> bool:
        """Validate a data source configuration."""
        required_fields = ['type', 'source_id']
        
        # Check required fields
        for field in required_fields:
            if field not in source:
                return False
        
        # Validate source type
        valid_types = ['sequence', 'analysis', 'project', 'custom']
        if source['type'] not in valid_types:
            return False
        
        # Validate source ID
        if not isinstance(source['source_id'], (int, str)):
            return False
        
        return True
    
    def _fetch_plot_data(self, plot_config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data for a plot from its configured sources."""
        plot_type = plot_config['type']
        data_sources = plot_config['data_sources']
        
        # Fetch data from all sources
        source_data = []
        for source in data_sources:
            data = self._fetch_single_data_source(source)
            source_data.append(data)
        
        # Process data based on plot type
        if plot_type in ['line', 'area']:
            return self._process_line_data(source_data, plot_config)
        elif plot_type == 'bar':
            return self._process_bar_data(source_data, plot_config)
        elif plot_type == 'scatter':
            return self._process_scatter_data(source_data, plot_config)
        elif plot_type == 'heatmap':
            return self._process_heatmap_data(source_data, plot_config)
        elif plot_type in ['pie', 'donut']:
            return self._process_pie_data(source_data, plot_config)
        elif plot_type.startswith('3d'):
            return self._process_3d_data(source_data, plot_config)
        else:
            # Generic data processing
            return {
                'raw_data': source_data,
                'plot_type': plot_type,
                'timestamp': datetime.now()
            }
    
    def _fetch_single_data_source(self, source_config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from a single source."""
        source_type = source_config['type']
        source_id = source_config['source_id']
        
        if source_type == 'sequence':
            return self._fetch_sequence_data(source_id, source_config)
        elif source_type == 'analysis':
            return self._fetch_analysis_data(source_id, source_config)
        elif source_type == 'project':
            return self._fetch_project_data(source_id, source_config)
        elif source_type == 'custom':
            return self._fetch_custom_data(source_config)
        else:
            raise ValidationError(f"Unknown source type: {source_type}")
    
    def _fetch_sequence_data(self, sequence_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from a sequence."""
        sequence = self.sequence_repository.get_by_id(sequence_id)
        if not sequence:
            raise ValidationError(f"Sequence {sequence_id} not found")
        
        data_type = config.get('data_type', 'gc_content')
        
        if data_type == 'gc_content':
            # Calculate GC content across sequence
            window_size = config.get('window_size', 100)
            step_size = config.get('step_size', window_size // 2)
            
            positions = []
            gc_values = []
            
            seq = sequence.sequence.upper()
            for i in range(0, len(seq) - window_size + 1, step_size):
                window = seq[i:i + window_size]
                gc_count = sum(1 for base in window if base in 'GC')
                gc_percent = (gc_count / len(window)) * 100
                
                positions.append(i + window_size // 2)
                gc_values.append(gc_percent)
            
            return {
                'x_data': positions,
                'y_data': gc_values,
                'title': f'GC Content - {sequence.header}',
                'xlabel': 'Position (bp)',
                'ylabel': 'GC Content (%)'
            }
        
        elif data_type == 'base_composition':
            # Base composition
            seq = sequence.sequence.upper()
            composition = {
                'A': seq.count('A'),
                'T': seq.count('T'),
                'C': seq.count('C'),
                'G': seq.count('G')
            }
            
            return {
                'labels': list(composition.keys()),
                'values': list(composition.values()),
                'title': f'Base Composition - {sequence.header}'
            }
        
        elif data_type == 'length_distribution':
            # For multiple sequences, this would show length distribution
            return {
                'values': [sequence.length],
                'labels': [sequence.header],
                'title': 'Sequence Length'
            }
        
        else:
            raise ValidationError(f"Unknown sequence data type: {data_type}")
    
    def _fetch_analysis_data(self, analysis_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from an analysis result."""
        analysis = self.analysis_repository.get_by_id(analysis_id)
        if not analysis:
            raise ValidationError(f"Analysis {analysis_id} not found")
        
        if not analysis.results:
            raise ValidationError(f"Analysis {analysis_id} has no results")
        
        # Extract relevant data based on analysis type
        if analysis.analysis_type == 'pattern_match':
            matches = analysis.results.get('matches', [])
            return {
                'x_data': matches,
                'y_data': [1] * len(matches),  # Simple presence indicator
                'title': f'Pattern Matches - {analysis.results.get("pattern", "")}',
                'xlabel': 'Position',
                'ylabel': 'Match'
            }
        
        elif analysis.analysis_type == 'gc_content':
            # Use the GC percentage result
            gc_pct = analysis.results.get('gc_percentage', 0)
            base_comp = analysis.results.get('base_composition', {})
            
            return {
                'labels': list(base_comp.keys()),
                'values': list(base_comp.values()),
                'title': f'Base Composition (GC: {gc_pct}%)'
            }
        
        else:
            # Generic analysis result
            return {
                'raw_results': analysis.results,
                'analysis_type': analysis.analysis_type,
                'title': f'Analysis Results - {analysis.analysis_type}'
            }
    
    def _fetch_project_data(self, project_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch aggregated data from a project."""
        # Get all sequences in project
        sequences = self.sequence_repository.get_by_project(project_id)
        
        data_type = config.get('data_type', 'sequence_lengths')
        
        if data_type == 'sequence_lengths':
            lengths = [seq.length for seq in sequences]
            headers = [seq.header[:20] + '...' if len(seq.header) > 20 else seq.header for seq in sequences]
            
            return {
                'x_data': list(range(len(sequences))),
                'y_data': lengths,
                'labels': headers,
                'title': f'Sequence Lengths (Project {project_id})',
                'xlabel': 'Sequence Index',
                'ylabel': 'Length (bp)'
            }
        
        elif data_type == 'gc_distribution':
            gc_values = [seq.gc_percentage for seq in sequences]
            
            return {
                'values': gc_values,
                'title': f'GC Content Distribution (Project {project_id})',
                'xlabel': 'GC Content (%)',
                'ylabel': 'Frequency'
            }
        
        else:
            raise ValidationError(f"Unknown project data type: {data_type}")
    
    def _fetch_custom_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch custom data from configuration."""
        # For demonstration, generate sample data
        data_generator = config.get('generator', 'random')
        
        if data_generator == 'random':
            size = config.get('size', 100)
            np.random.seed(config.get('seed', 42))
            
            return {
                'x_data': np.linspace(0, 10, size),
                'y_data': np.random.normal(0, 1, size),
                'title': 'Random Data',
                'xlabel': 'X',
                'ylabel': 'Y'
            }
        
        elif data_generator == 'sine_wave':
            size = config.get('size', 100)
            frequency = config.get('frequency', 1)
            
            x = np.linspace(0, 4 * np.pi, size)
            y = np.sin(frequency * x)
            
            return {
                'x_data': x,
                'y_data': y,
                'title': f'Sine Wave (f={frequency})',
                'xlabel': 'X',
                'ylabel': 'sin(x)'
            }
        
        else:
            raise ValidationError(f"Unknown data generator: {data_generator}")
    
    def _process_line_data(self, source_data: List[Dict], config: Dict) -> Dict[str, Any]:
        """Process data for line/area plots."""
        if not source_data:
            raise ValidationError("No data sources provided")
        
        # Use first source as primary
        primary_data = source_data[0]
        
        result = {
            'x_data': primary_data.get('x_data', []),
            'y_data': primary_data.get('y_data', []),
            'title': primary_data.get('title', 'Line Plot'),
            'xlabel': primary_data.get('xlabel', 'X'),
            'ylabel': primary_data.get('ylabel', 'Y')
        }
        
        # Add additional series if multiple sources
        if len(source_data) > 1:
            result['additional_series'] = []
            for i, data in enumerate(source_data[1:], 1):
                result['additional_series'].append({
                    'x_data': data.get('x_data', []),
                    'y_data': data.get('y_data', []),
                    'label': data.get('title', f'Series {i}')
                })
        
        return result
    
    def _process_bar_data(self, source_data: List[Dict], config: Dict) -> Dict[str, Any]:
        """Process data for bar charts."""
        if not source_data:
            raise ValidationError("No data sources provided")
        
        primary_data = source_data[0]
        
        return {
            'categories': primary_data.get('labels', primary_data.get('x_data', [])),
            'values': primary_data.get('values', primary_data.get('y_data', [])),
            'title': primary_data.get('title', 'Bar Chart'),
            'xlabel': primary_data.get('xlabel', 'Category'),
            'ylabel': primary_data.get('ylabel', 'Value')
        }
    
    def _process_scatter_data(self, source_data: List[Dict], config: Dict) -> Dict[str, Any]:
        """Process data for scatter plots."""
        if not source_data:
            raise ValidationError("No data sources provided")
        
        primary_data = source_data[0]
        
        return {
            'x_data': primary_data.get('x_data', []),
            'y_data': primary_data.get('y_data', []),
            'title': primary_data.get('title', 'Scatter Plot'),
            'xlabel': primary_data.get('xlabel', 'X'),
            'ylabel': primary_data.get('ylabel', 'Y')
        }
    
    def _process_heatmap_data(self, source_data: List[Dict], config: Dict) -> Dict[str, Any]:
        """Process data for heatmaps."""
        if not source_data:
            raise ValidationError("No data sources provided")
        
        primary_data = source_data[0]
        
        # Convert to 2D array if needed
        data = primary_data.get('matrix_data')
        if data is None:
            # Try to create matrix from x,y,z data
            x_data = primary_data.get('x_data', [])
            y_data = primary_data.get('y_data', [])
            z_data = primary_data.get('z_data', [])
            
            if x_data and y_data and z_data:
                # Create simple grid
                size = int(np.sqrt(len(z_data)))
                data = np.array(z_data[:size*size]).reshape(size, size)
            else:
                # Generate sample data
                data = np.random.rand(10, 10)
        
        return {
            'matrix_data': data,
            'title': primary_data.get('title', 'Heatmap')
        }
    
    def _process_pie_data(self, source_data: List[Dict], config: Dict) -> Dict[str, Any]:
        """Process data for pie/donut charts."""
        if not source_data:
            raise ValidationError("No data sources provided")
        
        primary_data = source_data[0]
        
        return {
            'labels': primary_data.get('labels', []),
            'values': primary_data.get('values', []),
            'title': primary_data.get('title', 'Pie Chart')
        }
    
    def _process_3d_data(self, source_data: List[Dict], config: Dict) -> Dict[str, Any]:
        """Process data for 3D plots."""
        if not source_data:
            raise ValidationError("No data sources provided")
        
        primary_data = source_data[0]
        plot_type = config['type']
        
        if plot_type == '3d_scatter':
            return {
                'x_data': primary_data.get('x_data', []),
                'y_data': primary_data.get('y_data', []),
                'z_data': primary_data.get('z_data', []),
                'title': primary_data.get('title', '3D Scatter Plot')
            }
        
        elif plot_type == '3d_surface':
            return {
                'x_data': primary_data.get('x_data', []),
                'y_data': primary_data.get('y_data', []),
                'z_data': primary_data.get('z_data', []),
                'title': primary_data.get('title', '3D Surface Plot')
            }
        
        elif plot_type == '3d_graph':
            return {
                'nodes': primary_data.get('nodes', []),
                'edges': primary_data.get('edges', []),
                'title': primary_data.get('title', '3D Graph')
            }
        
        return primary_data
    
    def _calculate_data_statistics(self, plot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics for plot data."""
        stats = {}
        
        # Count data points
        if 'x_data' in plot_data and 'y_data' in plot_data:
            stats['data_points'] = min(len(plot_data['x_data']), len(plot_data['y_data']))
        elif 'values' in plot_data:
            stats['data_points'] = len(plot_data['values'])
        elif 'matrix_data' in plot_data:
            matrix = plot_data['matrix_data']
            if hasattr(matrix, 'shape'):
                stats['matrix_shape'] = matrix.shape
                stats['data_points'] = matrix.size
        
        # Calculate value ranges
        numeric_fields = ['y_data', 'values', 'z_data']
        for field in numeric_fields:
            if field in plot_data:
                values = plot_data[field]
                if values and all(isinstance(v, (int, float)) for v in values):
                    stats[f'{field}_min'] = min(values)
                    stats[f'{field}_max'] = max(values)
                    stats[f'{field}_mean'] = sum(values) / len(values)
        
        return stats
    
    def _export_plot_image(self, plot_config: Dict, plot_data: Dict, 
                          output_file: Path, format_type: str, 
                          resolution: Tuple[int, int], dpi: int) -> str:
        """Export plot as image file."""
        import matplotlib.pyplot as plt
        
        # Create figure with specified resolution
        fig_width = resolution[0] / dpi
        fig_height = resolution[1] / dpi
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
        
        plot_type = plot_config['type']
        
        try:
            # Generate plot based on type
            if plot_type == 'line':
                ax.plot(plot_data.get('x_data', []), plot_data.get('y_data', []))
            elif plot_type == 'bar':
                ax.bar(plot_data.get('categories', []), plot_data.get('values', []))
            elif plot_type == 'scatter':
                ax.scatter(plot_data.get('x_data', []), plot_data.get('y_data', []))
            elif plot_type == 'heatmap':
                im = ax.imshow(plot_data.get('matrix_data', []), cmap='viridis')
                plt.colorbar(im, ax=ax)
            # Add more plot types as needed
            
            # Set labels and title
            ax.set_title(plot_data.get('title', ''))
            ax.set_xlabel(plot_data.get('xlabel', ''))
            ax.set_ylabel(plot_data.get('ylabel', ''))
            
            # Save figure
            plt.tight_layout()
            plt.savefig(output_file, format=format_type, dpi=dpi, bbox_inches='tight')
            plt.close(fig)
            
            return str(output_file)
            
        except Exception as e:
            plt.close(fig)
            raise ServiceError(f"Failed to export plot: {e}")
    
    def _start_data_monitoring(self, plot_id: str):
        """Start monitoring data changes for real-time updates."""
        # This is a simplified implementation
        # In a real system, this would monitor database changes, file modifications, etc.
        def monitor():
            while plot_id in self._update_callbacks:
                try:
                    # Check for data updates every 5 seconds
                    time.sleep(5)
                    
                    # Update plot data
                    self.update_plot_data(plot_id, force_refresh=True)
                    
                except Exception as e:
                    self.logger.error(f"Data monitoring error for plot {plot_id}: {e}")
                    break
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()