"""Visualization ViewModel for advanced data visualization and plot management."""

from typing import Optional, List, Dict, Any, Tuple, Callable
import numpy as np
from datetime import datetime

from viewmodels.base_viewmodel import BaseViewModel
from services.visualization_service import VisualizationService
from services.sequence_service import SequenceService
from services.analysis_service import AnalysisService
from utils.logger import get_logger


class VisualizationViewModel(BaseViewModel):
    """ViewModel for advanced data visualization."""
    
    def __init__(self):
        """Initialize visualization ViewModel."""
        super().__init__()
        self.visualization_service = VisualizationService()
        self.sequence_service = SequenceService()
        self.analysis_service = AnalysisService()
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize state
        self._initialize_visualization_state()
    
    def _initialize_state(self):
        """Initialize default state."""
        super()._initialize_state()
        self._initialize_visualization_state()
    
    def _initialize_visualization_state(self):
        """Initialize visualization-specific state."""
        self.update_state('plot_types', [
            'line', 'bar', 'scatter', 'heatmap', 'pie', 'donut', 
            'area', '3d_surface', '3d_scatter', '3d_graph'
        ], notify=False)
        
        self.update_state('active_plots', {}, notify=False)
        self.update_state('current_plot_id', None, notify=False)
        self.update_state('available_data_sources', [], notify=False)
        self.update_state('plot_configurations', {}, notify=False)
        self.update_state('interaction_mode', 'select', notify=False)  # select, zoom, pan
        self.update_state('real_time_enabled', False, notify=False)
        self.update_state('export_options', {
            'formats': ['png', 'svg', 'pdf', 'eps', 'jpg'],
            'resolutions': [(800, 600), (1920, 1080), (3840, 2160)],
            'dpi_options': [72, 150, 300, 600]
        }, notify=False)
    
    def create_plot(self, plot_type: str, data_sources: List[Dict[str, Any]], 
                   config: Optional[Dict[str, Any]] = None) -> None:
        """Create a new plot with specified configuration."""
        def operation():
            # Validate plot type
            if plot_type not in self.get_state('plot_types', []):
                raise Exception(f"Unsupported plot type: {plot_type}")
            
            # Set default configuration
            plot_config = config or {}
            plot_config.update({
                'title': plot_config.get('title', f'{plot_type.title()} Plot'),
                'xlabel': plot_config.get('xlabel', 'X'),
                'ylabel': plot_config.get('ylabel', 'Y'),
                'theme': plot_config.get('theme', 'default'),
                'interactive': plot_config.get('interactive', True)
            })
            
            # Create plot through service
            success, plot_id = self.visualization_service.create_plot_configuration(
                plot_type, data_sources, plot_config
            )
            
            if not success:
                raise Exception(f"Failed to create plot: {plot_id}")
            
            return plot_id
        
        def on_success(plot_id):
            # Add to active plots
            active_plots = self.get_state('active_plots', {})
            active_plots[plot_id] = {
                'type': plot_type,
                'created_at': datetime.now(),
                'data_sources': data_sources,
                'config': config or {}
            }
            
            self.update_state('active_plots', active_plots)
            self.update_state('current_plot_id', plot_id)
            
            # Load initial data
            self.update_plot_data(plot_id)
            
            self.log_action("create_plot", {
                "plot_id": plot_id,
                "plot_type": plot_type,
                "data_source_count": len(data_sources)
            })
        
        def on_error(error):
            self.set_error(f"Failed to create plot: {error}", "create_plot")
        
        self.execute_async_operation("create_plot", operation, on_success, on_error)
    
    def update_plot_data(self, plot_id: str, force_refresh: bool = False) -> None:
        """Update plot data from bound sources."""
        def operation():
            success, plot_data = self.visualization_service.update_plot_data(plot_id, force_refresh)
            if not success:
                raise Exception(f"Failed to update plot data: {plot_data}")
            return plot_data
        
        def on_success(plot_data):
            # Update plot data in state
            plot_configurations = self.get_state('plot_configurations', {})
            plot_configurations[plot_id] = plot_data
            self.update_state('plot_configurations', plot_configurations)
            
            # Notify plot update
            self.notify_observers('plot_data_updated', {'plot_id': plot_id, 'data': plot_data})
            
            self.log_action("update_plot_data", {"plot_id": plot_id})
        
        def on_error(error):
            self.set_error(f"Failed to update plot data: {error}", "update_plot_data")
        
        self.execute_async_operation("update_plot_data", operation, on_success, on_error)
    
    def configure_plot_interactions(self, plot_id: str, interactions: Dict[str, Any]) -> None:
        """Configure interactive controls for a plot."""
        try:
            active_plots = self.get_state('active_plots', {})
            if plot_id not in active_plots:
                self.set_error(f"Plot {plot_id} not found", "configure_interactions")
                return
            
            # Update plot configuration
            plot_config = active_plots[plot_id]['config']
            plot_config.update({
                'zoom_enabled': interactions.get('zoom_enabled', True),
                'pan_enabled': interactions.get('pan_enabled', True),
                'selection_enabled': interactions.get('selection_enabled', True),
                'hover_info': interactions.get('hover_info', True),
                'crosshair': interactions.get('crosshair', False),
                'grid': interactions.get('grid', True)
            })
            
            active_plots[plot_id]['config'] = plot_config
            self.update_state('active_plots', active_plots)
            
            # Notify interaction update
            self.notify_observers('plot_interactions_updated', {
                'plot_id': plot_id, 
                'interactions': interactions
            })
            
            self.log_action("configure_plot_interactions", {
                "plot_id": plot_id,
                "interactions": list(interactions.keys())
            })
            
        except Exception as e:
            self.set_error(f"Error configuring interactions: {e}", "configure_interactions")
    
    def enable_real_time_updates(self, plot_id: str) -> None:
        """Enable real-time data binding for a plot."""
        def operation():
            def update_callback(plot_data):
                # Schedule UI update on main thread
                self._schedule_ui_update(lambda: self._handle_real_time_update(plot_id, plot_data))
            
            success, message = self.visualization_service.bind_real_time_data(plot_id, update_callback)
            if not success:
                raise Exception(f"Failed to enable real-time updates: {message}")
            
            return message
        
        def on_success(message):
            self.update_state('real_time_enabled', True)
            
            # Update plot status
            active_plots = self.get_state('active_plots', {})
            if plot_id in active_plots:
                active_plots[plot_id]['real_time'] = True
                self.update_state('active_plots', active_plots)
            
            self.log_action("enable_real_time_updates", {"plot_id": plot_id})
        
        def on_error(error):
            self.set_error(f"Failed to enable real-time updates: {error}", "real_time_updates")
        
        self.execute_async_operation("enable_real_time", operation, on_success, on_error)
    
    def combine_data_sources(self, source_configs: List[Dict[str, Any]], 
                           combination_type: str = 'merge') -> None:
        """Combine multiple data sources for comparative visualizations."""
        def operation():
            success, combined_data = self.visualization_service.combine_data_sources(
                source_configs, combination_type
            )
            if not success:
                raise Exception(f"Failed to combine data sources: {combined_data}")
            
            return combined_data
        
        def on_success(combined_data):
            # Create a new plot with combined data
            plot_config = {
                'title': f'Combined Data ({combination_type})',
                'combination_type': combination_type,
                'source_count': len(source_configs)
            }
            
            # Determine appropriate plot type based on data
            plot_type = self._determine_plot_type_for_data(combined_data)
            
            # Create data source configuration for combined data
            combined_source = [{
                'type': 'custom',
                'source_id': 'combined',
                'data': combined_data
            }]
            
            # Create the plot
            self.create_plot(plot_type, combined_source, plot_config)
            
            self.log_action("combine_data_sources", {
                "combination_type": combination_type,
                "source_count": len(source_configs)
            })
        
        def on_error(error):
            self.set_error(f"Failed to combine data sources: {error}", "combine_data")
        
        self.execute_async_operation("combine_data", operation, on_success, on_error)
    
    def export_plot(self, plot_id: str, format_type: str, output_path: str, 
                   export_options: Optional[Dict[str, Any]] = None) -> None:
        """Export plot as high-quality image."""
        def operation():
            success, export_path = self.visualization_service.export_plot(
                plot_id, format_type, output_path, export_options
            )
            if not success:
                raise Exception(f"Failed to export plot: {export_path}")
            
            return export_path
        
        def on_success(export_path):
            self.log_action("export_plot", {
                "plot_id": plot_id,
                "format": format_type,
                "path": export_path
            })
        
        def on_error(error):
            self.set_error(f"Export failed: {error}", "export_plot")
        
        self.execute_async_operation("export_plot", operation, on_success, on_error)
    
    def load_available_data_sources(self, project_id: Optional[int] = None) -> None:
        """Load available data sources for visualization."""
        def operation():
            data_sources = []
            
            # Load sequences
            if project_id:
                success, sequences = self.sequence_service.get_sequences_by_project(project_id)
            else:
                success, sequences = self.sequence_service.list_sequences()
            
            if success:
                for seq in sequences:
                    data_sources.append({
                        'type': 'sequence',
                        'id': seq.id,
                        'name': seq.header,
                        'description': f'Sequence ({seq.length} bp)',
                        'data_types': ['gc_content', 'base_composition', 'length_distribution']
                    })
            
            # Load analyses
            if project_id:
                success, analyses = self.analysis_service.get_analyses_by_project(project_id)
            else:
                success, analyses = self.analysis_service.list_analyses()
            
            if success:
                for analysis in analyses:
                    if analysis.status == 'completed':
                        data_sources.append({
                            'type': 'analysis',
                            'id': analysis.id,
                            'name': f'{analysis.analysis_type} Analysis',
                            'description': f'Analysis results from {analysis.created_date}',
                            'data_types': ['results']
                        })
            
            return data_sources
        
        def on_success(data_sources):
            self.update_state('available_data_sources', data_sources)
            self.log_action("load_data_sources", {"count": len(data_sources)})
        
        def on_error(error):
            self.set_error(f"Failed to load data sources: {error}", "load_data_sources")
        
        self.execute_async_operation("load_data_sources", operation, on_success, on_error)
    
    def select_plot(self, plot_id: str) -> None:
        """Select a plot as the current active plot."""
        try:
            active_plots = self.get_state('active_plots', {})
            if plot_id not in active_plots:
                self.set_error(f"Plot {plot_id} not found", "select_plot")
                return
            
            self.update_state('current_plot_id', plot_id)
            
            # Load plot data if not already loaded
            plot_configurations = self.get_state('plot_configurations', {})
            if plot_id not in plot_configurations:
                self.update_plot_data(plot_id)
            
            self.log_action("select_plot", {"plot_id": plot_id})
            
        except Exception as e:
            self.set_error(f"Error selecting plot: {e}", "select_plot")
    
    def remove_plot(self, plot_id: str) -> None:
        """Remove a plot and clean up resources."""
        def operation():
            success, message = self.visualization_service.remove_plot(plot_id)
            if not success:
                raise Exception(f"Failed to remove plot: {message}")
            return message
        
        def on_success(message):
            # Remove from local state
            active_plots = self.get_state('active_plots', {})
            active_plots.pop(plot_id, None)
            self.update_state('active_plots', active_plots)
            
            plot_configurations = self.get_state('plot_configurations', {})
            plot_configurations.pop(plot_id, None)
            self.update_state('plot_configurations', plot_configurations)
            
            # Update current plot if it was removed
            if self.get_state('current_plot_id') == plot_id:
                remaining_plots = list(active_plots.keys())
                new_current = remaining_plots[0] if remaining_plots else None
                self.update_state('current_plot_id', new_current)
            
            self.log_action("remove_plot", {"plot_id": plot_id})
        
        def on_error(error):
            self.set_error(f"Failed to remove plot: {error}", "remove_plot")
        
        self.execute_async_operation("remove_plot", operation, on_success, on_error)
    
    def update_plot_configuration(self, plot_id: str, config_updates: Dict[str, Any]) -> None:
        """Update plot configuration."""
        try:
            active_plots = self.get_state('active_plots', {})
            if plot_id not in active_plots:
                self.set_error(f"Plot {plot_id} not found", "update_config")
                return
            
            # Update configuration
            plot_config = active_plots[plot_id]['config']
            plot_config.update(config_updates)
            active_plots[plot_id]['config'] = plot_config
            
            self.update_state('active_plots', active_plots)
            
            # Refresh plot data if needed
            if any(key in config_updates for key in ['data_sources', 'filters', 'parameters']):
                self.update_plot_data(plot_id, force_refresh=True)
            
            # Notify configuration update
            self.notify_observers('plot_config_updated', {
                'plot_id': plot_id,
                'updates': config_updates
            })
            
            self.log_action("update_plot_configuration", {
                "plot_id": plot_id,
                "updates": list(config_updates.keys())
            })
            
        except Exception as e:
            self.set_error(f"Error updating configuration: {e}", "update_config")
    
    def set_interaction_mode(self, mode: str) -> None:
        """Set the interaction mode for plots."""
        try:
            valid_modes = ['select', 'zoom', 'pan', 'measure']
            if mode not in valid_modes:
                self.set_error(f"Invalid interaction mode: {mode}", "set_interaction_mode")
                return
            
            self.update_state('interaction_mode', mode)
            
            # Notify all active plots of mode change
            self.notify_observers('interaction_mode_changed', {'mode': mode})
            
            self.log_action("set_interaction_mode", {"mode": mode})
            
        except Exception as e:
            self.set_error(f"Error setting interaction mode: {e}", "set_interaction_mode")
    
    def get_plot_statistics(self, plot_id: str) -> None:
        """Get statistics about a plot."""
        def operation():
            success, stats = self.visualization_service.get_plot_statistics(plot_id)
            if not success:
                raise Exception(f"Failed to get plot statistics: {stats}")
            return stats
        
        def on_success(stats):
            # Update plot statistics in state
            active_plots = self.get_state('active_plots', {})
            if plot_id in active_plots:
                active_plots[plot_id]['statistics'] = stats
                self.update_state('active_plots', active_plots)
            
            self.log_action("get_plot_statistics", {"plot_id": plot_id})
        
        def on_error(error):
            self.set_error(f"Failed to get statistics: {error}", "get_statistics")
        
        self.execute_async_operation("get_statistics", operation, on_success, on_error)
    
    def _handle_real_time_update(self, plot_id: str, plot_data: Dict[str, Any]) -> None:
        """Handle real-time plot data update on main thread."""
        try:
            # Update plot configuration
            plot_configurations = self.get_state('plot_configurations', {})
            plot_configurations[plot_id] = plot_data
            self.update_state('plot_configurations', plot_configurations)
            
            # Notify observers
            self.notify_observers('real_time_update', {
                'plot_id': plot_id,
                'data': plot_data,
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            self.logger.error(f"Error handling real-time update: {e}")
    
    def _determine_plot_type_for_data(self, data: Dict[str, Any]) -> str:
        """Determine appropriate plot type based on data structure."""
        # Simple heuristics for plot type selection
        if 'matrix_data' in data:
            return 'heatmap'
        elif 'labels' in data and 'values' in data:
            return 'pie'
        elif 'x_data' in data and 'y_data' in data and 'z_data' in data:
            return '3d_scatter'
        elif 'x_data' in data and 'y_data' in data:
            return 'line'
        elif 'categories' in data and 'values' in data:
            return 'bar'
        else:
            return 'line'  # Default fallback
    
    def get_current_plot_data(self) -> Optional[Dict[str, Any]]:
        """Get data for the currently selected plot."""
        current_plot_id = self.get_state('current_plot_id')
        if not current_plot_id:
            return None
        
        plot_configurations = self.get_state('plot_configurations', {})
        return plot_configurations.get(current_plot_id)
    
    def get_plot_summary(self) -> Dict[str, Any]:
        """Get a summary of all active plots."""
        active_plots = self.get_state('active_plots', {})
        current_plot_id = self.get_state('current_plot_id')
        
        return {
            'total_plots': len(active_plots),
            'current_plot': current_plot_id,
            'plot_types': [plot['type'] for plot in active_plots.values()],
            'real_time_plots': len([p for p in active_plots.values() if p.get('real_time', False)]),
            'available_data_sources': len(self.get_state('available_data_sources', [])),
            'interaction_mode': self.get_state('interaction_mode', 'select')
        }