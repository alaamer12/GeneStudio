"""2D plotting components using matplotlib."""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class PlotCanvas(ctk.CTkFrame):
    """Interactive 2D plot canvas."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create figure
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def plot_line(self, x_data, y_data, title="", xlabel="", ylabel=""):
        """Create a line plot."""
        self.ax.clear()
        self.ax.plot(x_data, y_data, linewidth=2)
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
        
    def plot_bar(self, categories, values, title="", xlabel="", ylabel=""):
        """Create a bar chart."""
        self.ax.clear()
        self.ax.bar(categories, values, color='#3B8ED0')
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True, alpha=0.3, axis='y')
        self.canvas.draw()
        
    def plot_scatter(self, x_data, y_data, title="", xlabel="", ylabel=""):
        """Create a scatter plot."""
        self.ax.clear()
        self.ax.scatter(x_data, y_data, alpha=0.6, s=50)
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
        
    def plot_heatmap(self, data, title=""):
        """Create a heatmap."""
        self.ax.clear()
        im = self.ax.imshow(data, cmap='viridis', aspect='auto')
        self.ax.set_title(title)
        self.figure.colorbar(im, ax=self.ax)
        self.canvas.draw()
        
    def clear(self):
        """Clear the plot."""
        self.ax.clear()
        self.canvas.draw()


class GCContentPlot(PlotCanvas):
    """Specialized plot for GC content visualization."""
    
    def plot_gc_content(self, sequence: str, window_size: int = 100):
        """Plot GC content across sequence."""
        gc_values = []
        positions = []
        
        for i in range(0, len(sequence) - window_size, window_size // 2):
            window = sequence[i:i + window_size]
            gc_count = sum(1 for base in window if base in 'GC')
            gc_percent = (gc_count / len(window)) * 100
            gc_values.append(gc_percent)
            positions.append(i)
        
        self.plot_line(
            positions,
            gc_values,
            title="GC Content Distribution",
            xlabel="Position (bp)",
            ylabel="GC Content (%)"
        )


class NucleotideDistributionPlot(PlotCanvas):
    """Plot for nucleotide distribution."""
    
    def plot_distribution(self, sequence: str):
        """Plot nucleotide distribution."""
        counts = {
            'A': sequence.count('A'),
            'T': sequence.count('T'),
            'C': sequence.count('C'),
            'G': sequence.count('G')
        }
        
        self.plot_bar(
            list(counts.keys()),
            list(counts.values()),
            title="Nucleotide Distribution",
            xlabel="Nucleotide",
            ylabel="Count"
        )
