"""Enhanced 3D visualization component with interactive controls."""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import Optional, Dict, Any, Callable, List, Tuple


class Enhanced3DVisualization(ctk.CTkFrame):
    """Enhanced 3D visualization component with interactive controls."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configuration
        self.interaction_config = {
            'rotation_enabled': True,
            'zoom_enabled': True,
            'selection_enabled': True,
            'animation_enabled': False
        }
        
        # Data storage
        self.plot_data = {}
        self.selected_elements = []
        
        # Callbacks
        self.selection_callback = None
        self.update_callback = None
        
        # Create figure with better styling
        self.figure = Figure(figsize=(8, 8), dpi=100, facecolor='white')
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add control panel
        self.control_panel = ctk.CTkFrame(self, height=50)
        self.control_panel.pack(fill="x", padx=5, pady=2)
        
        self._create_control_buttons()
        self._connect_events()
        
        # Animation state
        self.animation_active = False
        self.rotation_angle = 0
    
    def _create_control_buttons(self):
        """Create 3D control buttons."""
        # Rotation controls
        ctk.CTkLabel(
            self.control_panel,
            text="Rotation:",
            font=("Arial", 10)
        ).pack(side="left", padx=5)
        
        self.rotate_x_btn = ctk.CTkButton(
            self.control_panel,
            text="↻ X",
            width=50,
            height=30,
            command=lambda: self._rotate_view('x', 15)
        )
        self.rotate_x_btn.pack(side="left", padx=2)
        
        self.rotate_y_btn = ctk.CTkButton(
            self.control_panel,
            text="↻ Y",
            width=50,
            height=30,
            command=lambda: self._rotate_view('y', 15)
        )
        self.rotate_y_btn.pack(side="left", padx=2)
        
        self.rotate_z_btn = ctk.CTkButton(
            self.control_panel,
            text="↻ Z",
            width=50,
            height=30,
            command=lambda: self._rotate_view('z', 15)
        )
        self.rotate_z_btn.pack(side="left", padx=2)
        
        # View presets
        ctk.CTkLabel(
            self.control_panel,
            text="View:",
            font=("Arial", 10)
        ).pack(side="left", padx=(20, 5))
        
        self.top_view_btn = ctk.CTkButton(
            self.control_panel,
            text="Top",
            width=60,
            height=30,
            command=lambda: self._set_view_preset('top')
        )
        self.top_view_btn.pack(side="left", padx=2)
        
        self.side_view_btn = ctk.CTkButton(
            self.control_panel,
            text="Side",
            width=60,
            height=30,
            command=lambda: self._set_view_preset('side')
        )
        self.side_view_btn.pack(side="left", padx=2)
        
        self.iso_view_btn = ctk.CTkButton(
            self.control_panel,
            text="Iso",
            width=60,
            height=30,
            command=lambda: self._set_view_preset('isometric')
        )
        self.iso_view_btn.pack(side="left", padx=2)
        
        # Animation toggle
        self.animate_btn = ctk.CTkButton(
            self.control_panel,
            text="🎬 Animate",
            width=80,
            height=30,
            command=self._toggle_animation
        )
        self.animate_btn.pack(side="left", padx=(20, 2))
        
        # Reset button
        self.reset_btn = ctk.CTkButton(
            self.control_panel,
            text="🏠 Reset",
            width=70,
            height=30,
            command=self._reset_view
        )
        self.reset_btn.pack(side="left", padx=2)
        
        # Export button
        self.export_btn = ctk.CTkButton(
            self.control_panel,
            text="💾 Export",
            width=70,
            height=30,
            command=self._export_3d_plot
        )
        self.export_btn.pack(side="right", padx=2)
    
    def _connect_events(self):
        """Connect matplotlib events."""
        self.canvas.mpl_connect('button_press_event', self._on_click)
        self.canvas.mpl_connect('motion_notify_event', self._on_hover)
    
    def configure_interactions(self, config: Dict[str, Any]):
        """Configure interactive features."""
        self.interaction_config.update(config)
    
    def set_selection_callback(self, callback: Callable):
        """Set callback for element selection."""
        self.selection_callback = callback
    
    def set_update_callback(self, callback: Callable):
        """Set callback for updates."""
        self.update_callback = callback
    
    def plot_3d_scatter(self, x_data, y_data, z_data, title="", **kwargs):
        """Create enhanced 3D scatter plot."""
        self.ax.clear()
        
        # Store data for interactions
        self.plot_data = {
            'type': '3d_scatter',
            'x_data': x_data,
            'y_data': y_data,
            'z_data': z_data,
            'title': title
        }
        
        # Enhanced styling options
        colors = kwargs.get('colors', '#3B8ED0')
        sizes = kwargs.get('sizes', 50)
        alpha = kwargs.get('alpha', 0.8)
        marker = kwargs.get('marker', 'o')
        
        scatter = self.ax.scatter(x_data, y_data, z_data, c=colors, marker=marker, 
                                s=sizes, alpha=alpha, edgecolors='black', linewidth=0.5)
        
        self._apply_3d_styling(title)
        self.canvas.draw()
        
        return scatter
    
    def plot_3d_surface(self, x_data, y_data, z_data, title="", **kwargs):
        """Create enhanced 3D surface plot."""
        self.ax.clear()
        
        # Store data for interactions
        self.plot_data = {
            'type': '3d_surface',
            'x_data': x_data,
            'y_data': y_data,
            'z_data': z_data,
            'title': title
        }
        
        # Enhanced styling options
        cmap = kwargs.get('cmap', 'viridis')
        alpha = kwargs.get('alpha', 0.8)
        
        surface = self.ax.plot_surface(x_data, y_data, z_data, cmap=cmap, alpha=alpha,
                                     linewidth=0, antialiased=True)
        
        # Add contour lines if requested
        if kwargs.get('show_contours', False):
            self.ax.contour(x_data, y_data, z_data, zdir='z', offset=np.min(z_data), 
                          cmap=cmap, alpha=0.5)
        
        # Add colorbar
        if kwargs.get('show_colorbar', True):
            self.figure.colorbar(surface, ax=self.ax, shrink=0.5, aspect=20)
        
        self._apply_3d_styling(title)
        self.canvas.draw()
        
        return surface
    
    def plot_graph_3d(self, nodes, edges, title="Graph Visualization", **kwargs):
        """Plot enhanced 3D graph visualization."""
        self.ax.clear()
        
        # Store data for interactions
        self.plot_data = {
            'type': '3d_graph',
            'nodes': nodes,
            'edges': edges,
            'title': title
        }
        
        # Enhanced node styling
        node_color = kwargs.get('node_color', 'red')
        node_size = kwargs.get('node_size', 100)
        edge_color = kwargs.get('edge_color', 'blue')
        edge_alpha = kwargs.get('edge_alpha', 0.6)
        edge_width = kwargs.get('edge_width', 1)
        
        # Plot nodes with labels
        x = [node[0] for node in nodes]
        y = [node[1] for node in nodes]
        z = [node[2] for node in nodes]
        
        node_scatter = self.ax.scatter(x, y, z, c=node_color, marker='o', s=node_size,
                                     alpha=0.8, edgecolors='black', linewidth=1)
        
        # Add node labels if provided
        if kwargs.get('node_labels'):
            labels = kwargs['node_labels']
            for i, (xi, yi, zi) in enumerate(zip(x, y, z)):
                if i < len(labels):
                    self.ax.text(xi, yi, zi, f'  {labels[i]}', fontsize=8)
        
        # Plot edges with enhanced styling
        edge_lines = []
        for edge in edges:
            start, end = edge
            if start < len(nodes) and end < len(nodes):
                line = self.ax.plot(
                    [nodes[start][0], nodes[end][0]],
                    [nodes[start][1], nodes[end][1]],
                    [nodes[start][2], nodes[end][2]],
                    color=edge_color, alpha=edge_alpha, linewidth=edge_width
                )[0]
                edge_lines.append(line)
        
        # Add graph metrics as text
        if kwargs.get('show_metrics', False):
            metrics_text = f"Nodes: {len(nodes)}\nEdges: {len(edges)}"
            self.ax.text2D(0.02, 0.98, metrics_text, transform=self.ax.transAxes,
                          verticalalignment='top', bbox=dict(boxstyle='round', 
                          facecolor='wheat', alpha=0.8))
        
        self._apply_3d_styling(title)
        self.canvas.draw()
        
        return node_scatter, edge_lines
    
    def plot_3d_wireframe(self, x_data, y_data, z_data, title="", **kwargs):
        """Create 3D wireframe plot."""
        self.ax.clear()
        
        # Store data for interactions
        self.plot_data = {
            'type': '3d_wireframe',
            'x_data': x_data,
            'y_data': y_data,
            'z_data': z_data,
            'title': title
        }
        
        # Enhanced styling options
        color = kwargs.get('color', 'blue')
        alpha = kwargs.get('alpha', 0.7)
        linewidth = kwargs.get('linewidth', 1)
        
        wireframe = self.ax.plot_wireframe(x_data, y_data, z_data, color=color,
                                         alpha=alpha, linewidth=linewidth)
        
        self._apply_3d_styling(title)
        self.canvas.draw()
        
        return wireframe
    
    def update_3d_data(self, new_data: Dict[str, Any]):
        """Update 3D plot with new data (for real-time updates)."""
        plot_type = new_data.get('type', self.plot_data.get('type', '3d_scatter'))
        
        if plot_type == '3d_scatter':
            self.plot_3d_scatter(
                new_data.get('x_data', []),
                new_data.get('y_data', []),
                new_data.get('z_data', []),
                new_data.get('title', '')
            )
        elif plot_type == '3d_surface':
            self.plot_3d_surface(
                new_data.get('x_data', []),
                new_data.get('y_data', []),
                new_data.get('z_data', []),
                new_data.get('title', '')
            )
        elif plot_type == '3d_graph':
            self.plot_graph_3d(
                new_data.get('nodes', []),
                new_data.get('edges', []),
                new_data.get('title', '')
            )
        
        # Trigger update callback if set
        if self.update_callback:
            self.update_callback(new_data)
    
    def _apply_3d_styling(self, title: str):
        """Apply consistent 3D styling."""
        self.ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        self.ax.set_xlabel('X', fontsize=12)
        self.ax.set_ylabel('Y', fontsize=12)
        self.ax.set_zlabel('Z', fontsize=12)
        
        # Set background color
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        
        # Make pane edges more subtle
        self.ax.xaxis.pane.set_edgecolor('gray')
        self.ax.yaxis.pane.set_edgecolor('gray')
        self.ax.zaxis.pane.set_edgecolor('gray')
        self.ax.xaxis.pane.set_alpha(0.1)
        self.ax.yaxis.pane.set_alpha(0.1)
        self.ax.zaxis.pane.set_alpha(0.1)
    
    def _rotate_view(self, axis: str, angle: float):
        """Rotate the 3D view around specified axis."""
        current_elev = self.ax.elev
        current_azim = self.ax.azim
        
        if axis == 'x':
            self.ax.view_init(elev=current_elev + angle, azim=current_azim)
        elif axis == 'y':
            self.ax.view_init(elev=current_elev, azim=current_azim + angle)
        elif axis == 'z':
            # Z rotation is more complex in matplotlib
            self.ax.view_init(elev=current_elev + angle/2, azim=current_azim + angle/2)
        
        self.canvas.draw()
    
    def _set_view_preset(self, preset: str):
        """Set predefined view angles."""
        if preset == 'top':
            self.ax.view_init(elev=90, azim=0)
        elif preset == 'side':
            self.ax.view_init(elev=0, azim=0)
        elif preset == 'isometric':
            self.ax.view_init(elev=30, azim=45)
        elif preset == 'front':
            self.ax.view_init(elev=0, azim=90)
        
        self.canvas.draw()
    
    def _toggle_animation(self):
        """Toggle automatic rotation animation."""
        self.animation_active = not self.animation_active
        
        if self.animation_active:
            self.animate_btn.configure(text="⏸️ Stop")
            self._start_animation()
        else:
            self.animate_btn.configure(text="🎬 Animate")
    
    def _start_animation(self):
        """Start rotation animation."""
        if self.animation_active:
            self.rotation_angle += 2
            self.ax.view_init(elev=30, azim=self.rotation_angle)
            self.canvas.draw()
            
            # Schedule next frame
            self.after(50, self._start_animation)
    
    def _reset_view(self):
        """Reset view to default."""
        self.ax.view_init(elev=30, azim=45)
        self.canvas.draw()
    
    def _export_3d_plot(self):
        """Export 3D plot to file."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("SVG files", "*.svg"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight')
    
    def _on_click(self, event):
        """Handle mouse click events for 3D selection."""
        if not self.interaction_config['selection_enabled'] or event.inaxes != self.ax:
            return
        
        if event.button == 1:  # Left click
            # 3D selection is more complex - simplified implementation
            if self.plot_data.get('type') == '3d_graph':
                nodes = self.plot_data.get('nodes', [])
                if nodes:
                    # Find closest node (simplified 2D projection)
                    min_dist = float('inf')
                    selected_node = None
                    
                    for i, node in enumerate(nodes):
                        # Project 3D point to 2D screen coordinates (simplified)
                        x_proj = node[0]
                        y_proj = node[1]
                        
                        dist = ((x_proj - event.xdata)**2 + (y_proj - event.ydata)**2)**0.5
                        if dist < min_dist:
                            min_dist = dist
                            selected_node = {'index': i, 'position': node}
                    
                    if selected_node and self.selection_callback:
                        self.selection_callback(selected_node)
    
    def _on_hover(self, event):
        """Handle mouse hover events."""
        if event.inaxes != self.ax:
            return
        
        # Could implement 3D hover tooltips here
        pass
    
    def clear(self):
        """Clear the 3D plot."""
        self.ax.clear()
        self.plot_data = {}
        self.selected_elements = []
        self.canvas.draw()


# Keep the original class for backward compatibility
class Visualization3D(Enhanced3DVisualization):
    """Backward compatible 3D visualization."""
    pass
