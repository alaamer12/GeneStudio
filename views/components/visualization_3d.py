"""3D visualization component."""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


class Visualization3D(ctk.CTkFrame):
    """3D visualization component."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.figure = Figure(figsize=(8, 8), dpi=100)
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def plot_3d_scatter(self, x_data, y_data, z_data, title=""):
        """Create 3D scatter plot."""
        self.ax.clear()
        self.ax.scatter(x_data, y_data, z_data, c='#3B8ED0', marker='o', s=50)
        self.ax.set_title(title)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.canvas.draw()
        
    def plot_3d_surface(self, x_data, y_data, z_data, title=""):
        """Create 3D surface plot."""
        self.ax.clear()
        self.ax.plot_surface(x_data, y_data, z_data, cmap='viridis', alpha=0.8)
        self.ax.set_title(title)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.canvas.draw()
        
    def plot_graph_3d(self, nodes, edges, title="Graph Visualization"):
        """Plot 3D graph visualization."""
        self.ax.clear()
        
        # Plot nodes
        x = [node[0] for node in nodes]
        y = [node[1] for node in nodes]
        z = [node[2] for node in nodes]
        self.ax.scatter(x, y, z, c='red', marker='o', s=100)
        
        # Plot edges
        for edge in edges:
            start, end = edge
            self.ax.plot(
                [nodes[start][0], nodes[end][0]],
                [nodes[start][1], nodes[end][1]],
                [nodes[start][2], nodes[end][2]],
                'b-', alpha=0.6
            )
        
        self.ax.set_title(title)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.canvas.draw()
        
    def clear(self):
        """Clear the plot."""
        self.ax.clear()
        self.canvas.draw()
