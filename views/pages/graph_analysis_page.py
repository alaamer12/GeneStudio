"""Graph analysis page with enhanced functionality."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, Enhanced3DVisualization
from viewmodels.graph_analysis_viewmodel import GraphAnalysisViewModel
import numpy as np
from typing import Optional, Dict, Any


class GraphAnalysisPage(ctk.CTkFrame):
    """Enhanced graph analysis and visualization page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Initialize ViewModel
        self.viewmodel = GraphAnalysisViewModel()
        self.viewmodel.add_observer(self._on_viewmodel_update)
        
        # Current state
        self.current_project_id = None
        self.selected_sequences = []
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI components
        self._create_header()
        self._create_sidebar()
        self._create_visualization_area()
        
        # Initialize with default project (if any)
        self._load_initial_data()
    
    def _create_header(self):
        """Create the header section."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Graph Analysis",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            header,
            text="Ready",
            font=("Arial", 12),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=(20, 0))
        
        # Action buttons
        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.pack(side="right")
        
        self.export_btn = SecondaryButton(
            button_frame,
            text="💾 Export",
            width=100,
            command=self._export_graph,
            state="disabled"
        )
        self.export_btn.pack(side="right", padx=5)
        
        self.build_btn = PrimaryButton(
            button_frame,
            text="🔨 Build Graph",
            width=130,
            command=self._build_graph
        )
        self.build_btn.pack(side="right", padx=5)
    
    def _create_sidebar(self):
        """Create the sidebar with controls."""
        sidebar = ctk.CTkFrame(self, width=250)
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        sidebar.grid_propagate(False)
        
        # Sequence selection
        ctk.CTkLabel(
            sidebar,
            text="Sequence Selection",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=(15, 10), anchor="w")
        
        # Project selector
        project_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        project_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            project_frame,
            text="Project:",
            font=("Arial", 10)
        ).pack(anchor="w")
        
        self.project_selector = ctk.CTkOptionMenu(
            project_frame,
            values=["Select Project..."],
            width=200,
            command=self._on_project_selected
        )
        self.project_selector.pack(anchor="w", pady=2)
        
        # Sequence list
        ctk.CTkLabel(
            sidebar,
            text="Available Sequences:",
            font=("Arial", 10)
        ).pack(padx=15, pady=(10, 5), anchor="w")
        
        # Scrollable frame for sequences
        self.sequence_frame = ctk.CTkScrollableFrame(sidebar, height=150)
        self.sequence_frame.pack(fill="x", padx=15, pady=5)
        
        # Parameters section
        ctk.CTkLabel(
            sidebar,
            text="Parameters",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=(20, 10), anchor="w")
        
        # Min overlap parameter
        param_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        param_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            param_frame,
            text="Min Overlap Length:",
            font=("Arial", 10)
        ).pack(anchor="w")
        
        self.overlap_entry = ctk.CTkEntry(
            param_frame,
            placeholder_text="10",
            width=200
        )
        self.overlap_entry.pack(anchor="w", pady=2)
        self.overlap_entry.insert(0, "10")
        
        # Similarity threshold
        sim_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        sim_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            sim_frame,
            text="Similarity Threshold:",
            font=("Arial", 10)
        ).pack(anchor="w")
        
        self.similarity_entry = ctk.CTkEntry(
            sim_frame,
            placeholder_text="0.8",
            width=200
        )
        self.similarity_entry.pack(anchor="w", pady=2)
        self.similarity_entry.insert(0, "0.8")
        
        # Graph metrics section
        ctk.CTkLabel(
            sidebar,
            text="Graph Metrics",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=(20, 10), anchor="w")
        
        self.metrics_frame = ctk.CTkFrame(sidebar)
        self.metrics_frame.pack(fill="x", padx=15, pady=5)
        
        self.metrics_label = ctk.CTkLabel(
            self.metrics_frame,
            text="No graph generated",
            font=("Arial", 10),
            justify="left"
        )
        self.metrics_label.pack(padx=10, pady=10)
    
    def _create_visualization_area(self):
        """Create the main visualization area."""
        viz_frame = ctk.CTkFrame(self)
        viz_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        
        # 3D visualization with enhanced controls
        self.viz_3d = Enhanced3DVisualization(viz_frame)
        self.viz_3d.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Set up callbacks
        self.viz_3d.set_selection_callback(self._on_node_selected)
        
        # Selection info panel
        self.selection_frame = ctk.CTkFrame(viz_frame)
        self.selection_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.selection_label = ctk.CTkLabel(
            self.selection_frame,
            text="Click on nodes or edges to view details",
            font=("Arial", 10),
            justify="left"
        )
        self.selection_label.pack(padx=10, pady=10)
    
    def _load_initial_data(self):
        """Load initial data and populate UI."""
        # This would typically load available projects
        # For now, we'll use placeholder data
        self.project_selector.configure(values=["Project 1", "Project 2", "Demo Project"])
        self.project_selector.set("Demo Project")
        self._on_project_selected("Demo Project")
    
    def _on_project_selected(self, project_name: str):
        """Handle project selection."""
        if project_name == "Demo Project":
            # Load demo sequences
            self._load_demo_sequences()
        else:
            # In a real implementation, this would load actual project data
            self.current_project_id = 1  # Placeholder
            self.viewmodel.load_sequences_for_project(self.current_project_id)
    
    def _load_demo_sequences(self):
        """Load demo sequences for demonstration."""
        demo_sequences = [
            {"id": 1, "header": "Sequence_1", "length": 150},
            {"id": 2, "header": "Sequence_2", "length": 200},
            {"id": 3, "header": "Sequence_3", "length": 175},
            {"id": 4, "header": "Sequence_4", "length": 180},
            {"id": 5, "header": "Sequence_5", "length": 160}
        ]
        
        self._populate_sequence_list(demo_sequences)
    
    def _populate_sequence_list(self, sequences):
        """Populate the sequence selection list."""
        # Clear existing widgets
        for widget in self.sequence_frame.winfo_children():
            widget.destroy()
        
        self.sequence_checkboxes = {}
        
        for seq in sequences:
            frame = ctk.CTkFrame(self.sequence_frame, fg_color="transparent")
            frame.pack(fill="x", pady=2)
            
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                frame,
                text=f"{seq['header']} ({seq['length']} bp)",
                variable=var,
                font=("Arial", 10),
                command=self._on_sequence_selection_changed
            )
            checkbox.pack(anchor="w")
            
            self.sequence_checkboxes[seq['id']] = {
                'var': var,
                'checkbox': checkbox,
                'data': seq
            }
    
    def _on_sequence_selection_changed(self):
        """Handle sequence selection changes."""
        selected_ids = []
        for seq_id, checkbox_data in self.sequence_checkboxes.items():
            if checkbox_data['var'].get():
                selected_ids.append(seq_id)
        
        self.selected_sequences = selected_ids
        
        # Update build button state
        if len(selected_ids) >= 2:
            self.build_btn.configure(state="normal")
        else:
            self.build_btn.configure(state="disabled")
    
    def _build_graph(self):
        """Build overlap graph from selected sequences."""
        if len(self.selected_sequences) < 2:
            self._show_status("Please select at least 2 sequences", "error")
            return
        
        try:
            # Get parameters
            overlap_threshold = int(self.overlap_entry.get() or "10")
            similarity_threshold = float(self.similarity_entry.get() or "0.8")
            
            # Update status
            self._show_status("Building graph...", "info")
            
            # For demo, create a simple graph
            self._create_demo_graph(overlap_threshold)
            
        except ValueError as e:
            self._show_status(f"Invalid parameters: {e}", "error")
        except Exception as e:
            self._show_status(f"Error building graph: {e}", "error")
    
    def _create_demo_graph(self, overlap_threshold: int):
        """Create a demo graph for visualization."""
        # Generate demo graph data
        num_nodes = len(self.selected_sequences)
        
        # Create 3D positions for nodes
        angles = np.linspace(0, 2*np.pi, num_nodes, endpoint=False)
        radius = 0.3
        
        nodes = []
        for i, angle in enumerate(angles):
            x = 0.5 + radius * np.cos(angle)
            y = 0.5 + radius * np.sin(angle)
            z = 0.5 + 0.1 * np.sin(2 * angle)  # Add some Z variation
            nodes.append((x, y, z))
        
        # Create edges (simple ring + some cross connections)
        edges = []
        for i in range(num_nodes):
            # Ring connections
            edges.append((i, (i + 1) % num_nodes))
            
            # Some cross connections
            if i % 2 == 0 and i + 2 < num_nodes:
                edges.append((i, i + 2))
        
        # Get node labels
        node_labels = []
        for seq_id in self.selected_sequences:
            if seq_id in self.sequence_checkboxes:
                seq_data = self.sequence_checkboxes[seq_id]['data']
                node_labels.append(seq_data['header'])
        
        # Plot the graph
        self.viz_3d.plot_graph_3d(
            nodes, 
            edges, 
            title="Overlap Graph",
            node_labels=node_labels,
            show_metrics=True
        )
        
        # Update metrics
        self._update_metrics_display(num_nodes, len(edges))
        
        # Update status and enable export
        self._show_status("Graph generated successfully", "success")
        self.export_btn.configure(state="normal")
    
    def _update_metrics_display(self, num_nodes: int, num_edges: int):
        """Update the metrics display."""
        avg_degree = (2 * num_edges) / num_nodes if num_nodes > 0 else 0
        density = (2 * num_edges) / (num_nodes * (num_nodes - 1)) if num_nodes > 1 else 0
        
        metrics_text = f"""Nodes: {num_nodes}
Edges: {num_edges}
Avg Degree: {avg_degree:.2f}
Density: {density:.3f}
Components: 1"""
        
        self.metrics_label.configure(text=metrics_text)
    
    def _on_node_selected(self, node_info: Dict[str, Any]):
        """Handle node selection in the graph."""
        node_index = node_info.get('index', 0)
        
        if node_index < len(self.selected_sequences):
            seq_id = self.selected_sequences[node_index]
            if seq_id in self.sequence_checkboxes:
                seq_data = self.sequence_checkboxes[seq_id]['data']
                
                selection_text = f"""Selected Node: {seq_data['header']}
Length: {seq_data['length']} bp
Position: {node_info.get('position', 'N/A')}
Connections: Available in full implementation"""
                
                self.selection_label.configure(text=selection_text)
    
    def _export_graph(self):
        """Export the current graph."""
        from tkinter import filedialog, messagebox
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("SVG files", "*.svg"),
                    ("JSON files", "*.json"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                # For demo, just export the visualization
                self.viz_3d._export_3d_plot()
                messagebox.showinfo("Export", f"Graph exported successfully!")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export graph: {e}")
    
    def _show_status(self, message: str, status_type: str = "info"):
        """Show status message."""
        colors = {
            "info": "gray",
            "success": "green",
            "error": "red",
            "warning": "orange"
        }
        
        self.status_label.configure(
            text=message,
            text_color=colors.get(status_type, "gray")
        )
        
        # Auto-clear status after 5 seconds for non-error messages
        if status_type != "error":
            self.after(5000, lambda: self.status_label.configure(text="Ready", text_color="gray"))
    
    def _on_viewmodel_update(self, key: str, value: Any):
        """Handle ViewModel state updates."""
        if key == 'available_sequences':
            self._populate_sequence_list(value)
        elif key == 'graph_data':
            self._update_graph_visualization(value)
        elif key == 'graph_metrics':
            self._update_metrics_from_viewmodel(value)
        elif key == 'error':
            if value:
                self._show_status(value, "error")
        elif key == 'loading':
            if value:
                self._show_status("Loading...", "info")
    
    def _update_graph_visualization(self, graph_data: Dict[str, Any]):
        """Update the 3D visualization with new graph data."""
        if not graph_data:
            return
        
        nodes_data = graph_data.get('nodes', [])
        edges_data = graph_data.get('edges', [])
        
        # Extract positions and create visualization data
        nodes = [node['position'] for node in nodes_data]
        edges = [(edge['source'], edge['target']) for edge in edges_data]
        node_labels = [node['header'] for node in nodes_data]
        
        # Plot the graph
        self.viz_3d.plot_graph_3d(
            nodes,
            edges,
            title="Overlap Graph",
            node_labels=node_labels,
            show_metrics=True
        )
        
        self.export_btn.configure(state="normal")
    
    def _update_metrics_from_viewmodel(self, metrics: Dict[str, Any]):
        """Update metrics display from ViewModel data."""
        if not metrics:
            return
        
        metrics_text = f"""Nodes: {metrics.get('node_count', 0)}
Edges: {metrics.get('edge_count', 0)}
Avg Degree: {metrics.get('average_degree', 0)}
Density: {metrics.get('density', 0)}
Components: {metrics.get('connected_components', 0)}"""
        
        self.metrics_label.configure(text=metrics_text)


