"""Graph Analysis ViewModel for overlap graph generation and 3D visualization management."""

from typing import Optional, List, Dict, Any, Tuple, Callable
import numpy as np
from datetime import datetime

from viewmodels.base_viewmodel import BaseViewModel
from services.sequence_service import SequenceService
from services.analysis_service import AnalysisService
from algorithms.overlap_graph import build_overlap_graph
from models.sequence_model_enhanced import Sequence
from utils.logger import get_logger


class GraphAnalysisViewModel(BaseViewModel):
    """ViewModel for overlap graph analysis and 3D visualization."""
    
    def __init__(self):
        """Initialize graph analysis ViewModel."""
        super().__init__()
        self.sequence_service = SequenceService()
        self.analysis_service = AnalysisService()
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize state
        self._initialize_graph_state()
    
    def _initialize_state(self):
        """Initialize default state."""
        super()._initialize_state()
        self._initialize_graph_state()
    
    def _initialize_graph_state(self):
        """Initialize graph-specific state."""
        self.update_state('selected_sequences', [], notify=False)
        self.update_state('graph_data', None, notify=False)
        self.update_state('graph_metrics', {}, notify=False)
        self.update_state('overlap_threshold', 10, notify=False)
        self.update_state('similarity_threshold', 0.8, notify=False)
        self.update_state('graph_type', 'overlap', notify=False)
        self.update_state('visualization_mode', '3d', notify=False)
        self.update_state('selected_node', None, notify=False)
        self.update_state('selected_edge', None, notify=False)
        self.update_state('export_formats', ['json', 'csv', 'graphml', 'png', 'svg'], notify=False)
    
    def load_sequences_for_project(self, project_id: int) -> None:
        """Load sequences for a project."""
        def operation():
            success, sequences = self.sequence_service.get_sequences_by_project(project_id)
            if not success:
                raise Exception(f"Failed to load sequences: {sequences}")
            return sequences
        
        def on_success(sequences):
            self.update_state('available_sequences', sequences)
            self.log_action("load_sequences_for_project", {"project_id": project_id, "count": len(sequences)})
        
        def on_error(error):
            self.set_error(f"Failed to load sequences: {error}", "load_sequences")
        
        self.execute_async_operation("load_sequences", operation, on_success, on_error)
    
    def select_sequences(self, sequence_ids: List[int]) -> None:
        """Select sequences for graph analysis."""
        try:
            if not sequence_ids:
                self.set_error("No sequences selected", "select_sequences")
                return
            
            if len(sequence_ids) < 2:
                self.set_error("At least 2 sequences required for graph analysis", "select_sequences")
                return
            
            # Get sequence objects
            selected_sequences = []
            for seq_id in sequence_ids:
                success, sequence = self.sequence_service.get_sequence(seq_id)
                if success and sequence:
                    selected_sequences.append(sequence)
                else:
                    self.logger.warning(f"Could not load sequence {seq_id}")
            
            if len(selected_sequences) < 2:
                self.set_error("Could not load enough valid sequences", "select_sequences")
                return
            
            self.update_state('selected_sequences', selected_sequences)
            self.clear_error("select_sequences")
            self.log_action("select_sequences", {"count": len(selected_sequences)})
            
        except Exception as e:
            self.set_error(f"Error selecting sequences: {e}", "select_sequences")
    
    def generate_overlap_graph(self, overlap_threshold: Optional[int] = None, 
                              similarity_threshold: Optional[float] = None) -> None:
        """Generate overlap graph from selected sequences."""
        def operation():
            sequences = self.get_state('selected_sequences', [])
            if len(sequences) < 2:
                raise Exception("At least 2 sequences required for graph generation")
            
            # Use provided thresholds or defaults
            min_overlap = overlap_threshold or self.get_state('overlap_threshold', 10)
            sim_threshold = similarity_threshold or self.get_state('similarity_threshold', 0.8)
            
            # Extract sequence strings
            sequence_strings = [seq.sequence for seq in sequences]
            
            # Build overlap graph using existing algorithm
            adjacency_list = build_overlap_graph(sequence_strings, min_overlap)
            
            # Generate 3D positions for nodes
            node_positions = self._generate_3d_positions(len(sequences))
            
            # Create graph data structure
            graph_data = {
                'nodes': [
                    {
                        'id': i,
                        'sequence_id': sequences[i].id,
                        'header': sequences[i].header,
                        'length': sequences[i].length,
                        'position': node_positions[i],
                        'degree': len(adjacency_list.get(i, []))
                    }
                    for i in range(len(sequences))
                ],
                'edges': [
                    {
                        'source': source,
                        'target': target,
                        'overlap_length': self._calculate_overlap_length(
                            sequences[source].sequence, 
                            sequences[target].sequence, 
                            min_overlap
                        )
                    }
                    for source, targets in adjacency_list.items()
                    for target in targets
                ],
                'parameters': {
                    'min_overlap': min_overlap,
                    'similarity_threshold': sim_threshold,
                    'sequence_count': len(sequences)
                }
            }
            
            return graph_data
        
        def on_success(graph_data):
            self.update_state('graph_data', graph_data)
            self.update_state('overlap_threshold', graph_data['parameters']['min_overlap'])
            self.update_state('similarity_threshold', graph_data['parameters']['similarity_threshold'])
            
            # Calculate metrics
            metrics = self._calculate_graph_metrics(graph_data)
            self.update_state('graph_metrics', metrics)
            
            self.clear_error("generate_graph")
            self.log_action("generate_overlap_graph", {
                "nodes": len(graph_data['nodes']),
                "edges": len(graph_data['edges']),
                "min_overlap": graph_data['parameters']['min_overlap']
            })
        
        def on_error(error):
            self.set_error(f"Failed to generate graph: {error}", "generate_graph")
        
        self.execute_async_operation("generate_graph", operation, on_success, on_error)
    
    def handle_node_selection(self, node_id: int) -> None:
        """Handle selection of a graph node."""
        try:
            graph_data = self.get_state('graph_data')
            if not graph_data:
                return
            
            # Find node data
            selected_node = None
            for node in graph_data['nodes']:
                if node['id'] == node_id:
                    selected_node = node
                    break
            
            if selected_node:
                # Get detailed sequence information
                sequence_id = selected_node['sequence_id']
                success, sequence = self.sequence_service.get_sequence(sequence_id)
                
                if success and sequence:
                    node_details = {
                        'node_id': node_id,
                        'sequence': sequence,
                        'connections': self._get_node_connections(node_id, graph_data),
                        'metrics': self._calculate_node_metrics(node_id, graph_data)
                    }
                    
                    self.update_state('selected_node', node_details)
                    self.update_state('selected_edge', None)  # Clear edge selection
                    self.log_action("select_node", {"node_id": node_id})
            
        except Exception as e:
            self.set_error(f"Error selecting node: {e}", "node_selection")
    
    def handle_edge_selection(self, source_id: int, target_id: int) -> None:
        """Handle selection of a graph edge."""
        try:
            graph_data = self.get_state('graph_data')
            if not graph_data:
                return
            
            # Find edge data
            selected_edge = None
            for edge in graph_data['edges']:
                if edge['source'] == source_id and edge['target'] == target_id:
                    selected_edge = edge
                    break
            
            if selected_edge:
                # Get sequence information for both nodes
                sequences = self.get_state('selected_sequences', [])
                source_seq = sequences[source_id] if source_id < len(sequences) else None
                target_seq = sequences[target_id] if target_id < len(sequences) else None
                
                if source_seq and target_seq:
                    edge_details = {
                        'source_node': source_id,
                        'target_node': target_id,
                        'source_sequence': source_seq,
                        'target_sequence': target_seq,
                        'overlap_length': selected_edge['overlap_length'],
                        'overlap_details': self._analyze_overlap(source_seq.sequence, target_seq.sequence)
                    }
                    
                    self.update_state('selected_edge', edge_details)
                    self.update_state('selected_node', None)  # Clear node selection
                    self.log_action("select_edge", {"source": source_id, "target": target_id})
            
        except Exception as e:
            self.set_error(f"Error selecting edge: {e}", "edge_selection")
    
    def calculate_graph_metrics(self) -> None:
        """Calculate comprehensive graph metrics."""
        try:
            graph_data = self.get_state('graph_data')
            if not graph_data:
                self.set_error("No graph data available", "calculate_metrics")
                return
            
            metrics = self._calculate_graph_metrics(graph_data)
            self.update_state('graph_metrics', metrics)
            self.log_action("calculate_graph_metrics", metrics)
            
        except Exception as e:
            self.set_error(f"Error calculating metrics: {e}", "calculate_metrics")
    
    def export_graph_data(self, format_type: str, output_path: str) -> None:
        """Export graph data in specified format."""
        def operation():
            graph_data = self.get_state('graph_data')
            if not graph_data:
                raise Exception("No graph data to export")
            
            if format_type not in self.get_state('export_formats', []):
                raise Exception(f"Unsupported export format: {format_type}")
            
            return self._export_graph_format(graph_data, format_type, output_path)
        
        def on_success(export_path):
            self.log_action("export_graph_data", {"format": format_type, "path": export_path})
        
        def on_error(error):
            self.set_error(f"Export failed: {error}", "export_graph")
        
        self.execute_async_operation("export_graph", operation, on_success, on_error)
    
    def update_visualization_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update visualization parameters."""
        try:
            # Update overlap threshold
            if 'overlap_threshold' in parameters:
                threshold = int(parameters['overlap_threshold'])
                if threshold > 0:
                    self.update_state('overlap_threshold', threshold)
            
            # Update similarity threshold
            if 'similarity_threshold' in parameters:
                sim_threshold = float(parameters['similarity_threshold'])
                if 0.0 <= sim_threshold <= 1.0:
                    self.update_state('similarity_threshold', sim_threshold)
            
            # Update visualization mode
            if 'visualization_mode' in parameters:
                mode = parameters['visualization_mode']
                if mode in ['2d', '3d', 'force_directed']:
                    self.update_state('visualization_mode', mode)
            
            self.log_action("update_visualization_parameters", parameters)
            
        except Exception as e:
            self.set_error(f"Error updating parameters: {e}", "update_parameters")
    
    def _generate_3d_positions(self, num_nodes: int) -> List[Tuple[float, float, float]]:
        """Generate 3D positions for graph nodes."""
        # Use a simple circular layout in 3D space
        positions = []
        
        if num_nodes == 1:
            positions.append((0.5, 0.5, 0.5))
        else:
            # Arrange nodes in a 3D spiral
            for i in range(num_nodes):
                angle = 2 * np.pi * i / num_nodes
                height = i / (num_nodes - 1) if num_nodes > 1 else 0.5
                
                x = 0.5 + 0.3 * np.cos(angle)
                y = 0.5 + 0.3 * np.sin(angle)
                z = 0.2 + 0.6 * height
                
                positions.append((x, y, z))
        
        return positions
    
    def _calculate_overlap_length(self, seq1: str, seq2: str, min_overlap: int) -> int:
        """Calculate actual overlap length between two sequences."""
        from algorithms.overlap_graph import _find_overlap
        return _find_overlap(seq1, seq2, min_overlap)
    
    def _calculate_graph_metrics(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive graph metrics."""
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        
        # Basic metrics
        num_nodes = len(nodes)
        num_edges = len(edges)
        
        # Node degrees
        node_degrees = {node['id']: node['degree'] for node in nodes}
        
        # Connected components (simplified - assumes single component for now)
        connected_components = 1
        
        # Average degree
        avg_degree = sum(node_degrees.values()) / num_nodes if num_nodes > 0 else 0
        
        # Density
        max_edges = num_nodes * (num_nodes - 1) / 2
        density = num_edges / max_edges if max_edges > 0 else 0
        
        # Overlap statistics
        overlap_lengths = [edge['overlap_length'] for edge in edges]
        avg_overlap = sum(overlap_lengths) / len(overlap_lengths) if overlap_lengths else 0
        max_overlap = max(overlap_lengths) if overlap_lengths else 0
        min_overlap = min(overlap_lengths) if overlap_lengths else 0
        
        return {
            'node_count': num_nodes,
            'edge_count': num_edges,
            'connected_components': connected_components,
            'average_degree': round(avg_degree, 2),
            'density': round(density, 3),
            'node_degrees': node_degrees,
            'overlap_statistics': {
                'average': round(avg_overlap, 2),
                'maximum': max_overlap,
                'minimum': min_overlap
            }
        }
    
    def _get_node_connections(self, node_id: int, graph_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get connections for a specific node."""
        connections = []
        
        for edge in graph_data['edges']:
            if edge['source'] == node_id:
                # Outgoing connection
                target_node = next((n for n in graph_data['nodes'] if n['id'] == edge['target']), None)
                if target_node:
                    connections.append({
                        'type': 'outgoing',
                        'target_id': edge['target'],
                        'target_header': target_node['header'],
                        'overlap_length': edge['overlap_length']
                    })
            elif edge['target'] == node_id:
                # Incoming connection
                source_node = next((n for n in graph_data['nodes'] if n['id'] == edge['source']), None)
                if source_node:
                    connections.append({
                        'type': 'incoming',
                        'source_id': edge['source'],
                        'source_header': source_node['header'],
                        'overlap_length': edge['overlap_length']
                    })
        
        return connections
    
    def _calculate_node_metrics(self, node_id: int, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for a specific node."""
        node = next((n for n in graph_data['nodes'] if n['id'] == node_id), None)
        if not node:
            return {}
        
        connections = self._get_node_connections(node_id, graph_data)
        
        return {
            'degree': node['degree'],
            'in_degree': len([c for c in connections if c['type'] == 'incoming']),
            'out_degree': len([c for c in connections if c['type'] == 'outgoing']),
            'sequence_length': node['length'],
            'connection_count': len(connections)
        }
    
    def _analyze_overlap(self, seq1: str, seq2: str) -> Dict[str, Any]:
        """Analyze overlap between two sequences."""
        overlap_len = self._calculate_overlap_length(seq1, seq2, 1)
        
        if overlap_len > 0:
            overlap_seq = seq1[-overlap_len:]
            return {
                'length': overlap_len,
                'sequence': overlap_seq,
                'percentage_seq1': round((overlap_len / len(seq1)) * 100, 2),
                'percentage_seq2': round((overlap_len / len(seq2)) * 100, 2)
            }
        
        return {'length': 0, 'sequence': '', 'percentage_seq1': 0, 'percentage_seq2': 0}
    
    def _export_graph_format(self, graph_data: Dict[str, Any], format_type: str, output_path: str) -> str:
        """Export graph data in specified format."""
        import json
        import csv
        from pathlib import Path
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format_type == 'json':
            with open(output_file, 'w') as f:
                json.dump(graph_data, f, indent=2, default=str)
        
        elif format_type == 'csv':
            # Export nodes and edges as separate CSV files
            nodes_file = output_file.with_suffix('.nodes.csv')
            edges_file = output_file.with_suffix('.edges.csv')
            
            # Export nodes
            with open(nodes_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'sequence_id', 'header', 'length', 'degree'])
                writer.writeheader()
                for node in graph_data['nodes']:
                    writer.writerow({
                        'id': node['id'],
                        'sequence_id': node['sequence_id'],
                        'header': node['header'],
                        'length': node['length'],
                        'degree': node['degree']
                    })
            
            # Export edges
            with open(edges_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['source', 'target', 'overlap_length'])
                writer.writeheader()
                for edge in graph_data['edges']:
                    writer.writerow(edge)
        
        elif format_type == 'graphml':
            # Simple GraphML export
            with open(output_file, 'w') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n')
                f.write('  <graph id="overlap_graph" edgedefault="directed">\n')
                
                # Write nodes
                for node in graph_data['nodes']:
                    f.write(f'    <node id="{node["id"]}">\n')
                    f.write(f'      <data key="header">{node["header"]}</data>\n')
                    f.write(f'      <data key="length">{node["length"]}</data>\n')
                    f.write('    </node>\n')
                
                # Write edges
                for edge in graph_data['edges']:
                    f.write(f'    <edge source="{edge["source"]}" target="{edge["target"]}">\n')
                    f.write(f'      <data key="overlap_length">{edge["overlap_length"]}</data>\n')
                    f.write('    </edge>\n')
                
                f.write('  </graph>\n')
                f.write('</graphml>\n')
        
        else:
            raise Exception(f"Unsupported export format: {format_type}")
        
        return str(output_file)
    
    def get_graph_summary(self) -> Dict[str, Any]:
        """Get a summary of the current graph."""
        graph_data = self.get_state('graph_data')
        metrics = self.get_state('graph_metrics', {})
        
        if not graph_data:
            return {'status': 'no_graph', 'message': 'No graph generated'}
        
        return {
            'status': 'ready',
            'nodes': len(graph_data['nodes']),
            'edges': len(graph_data['edges']),
            'parameters': graph_data['parameters'],
            'metrics': metrics,
            'has_selection': bool(self.get_state('selected_node') or self.get_state('selected_edge'))
        }