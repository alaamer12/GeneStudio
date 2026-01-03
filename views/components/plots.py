"""2D plotting components using matplotlib with interactive controls."""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
import numpy as np
from typing import Optional, Dict, Any, Callable, List


class InteractivePlotCanvas(ctk.CTkFrame):
    """Interactive 2D plot canvas with enhanced controls."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Plot configuration
        self.plot_config = {
            'zoom_enabled': True,
            'pan_enabled': True,
            'selection_enabled': True,
            'hover_info': True,
            'crosshair': False,
            'grid': True
        }
        
        # Data and callbacks
        self.plot_data = {}
        self.update_callback = None
        self.selection_callback = None
        
        # Create figure with better styling
        plt.style.use('default')
        self.figure = Figure(figsize=(8, 6), dpi=100, facecolor='white')
        self.ax = self.figure.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add navigation toolbar
        self.toolbar_frame = ctk.CTkFrame(self, height=40)
        self.toolbar_frame.pack(fill="x", padx=5, pady=2)
        
        # Custom toolbar buttons
        self._create_toolbar_buttons()
        
        # Interactive features
        self.cursor = None
        self.selected_points = []
        
        # Connect events
        self._connect_events()
    
    def _create_toolbar_buttons(self):
        """Create custom toolbar buttons."""
        # Zoom button
        self.zoom_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="🔍 Zoom",
            width=80,
            height=30,
            command=self._toggle_zoom
        )
        self.zoom_btn.pack(side="left", padx=2)
        
        # Pan button
        self.pan_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="✋ Pan",
            width=80,
            height=30,
            command=self._toggle_pan
        )
        self.pan_btn.pack(side="left", padx=2)
        
        # Reset view button
        self.reset_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="🏠 Reset",
            width=80,
            height=30,
            command=self._reset_view
        )
        self.reset_btn.pack(side="left", padx=2)
        
        # Grid toggle
        self.grid_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="⊞ Grid",
            width=80,
            height=30,
            command=self._toggle_grid
        )
        self.grid_btn.pack(side="left", padx=2)
        
        # Crosshair toggle
        self.crosshair_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="✛ Crosshair",
            width=90,
            height=30,
            command=self._toggle_crosshair
        )
        self.crosshair_btn.pack(side="left", padx=2)
        
        # Export button
        self.export_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="💾 Export",
            width=80,
            height=30,
            command=self._export_plot
        )
        self.export_btn.pack(side="right", padx=2)
    
    def _connect_events(self):
        """Connect matplotlib events."""
        self.canvas.mpl_connect('button_press_event', self._on_click)
        self.canvas.mpl_connect('motion_notify_event', self._on_hover)
        self.canvas.mpl_connect('key_press_event', self._on_key_press)
    
    def configure_interactions(self, config: Dict[str, Any]):
        """Configure interactive features."""
        self.plot_config.update(config)
        
        # Update crosshair
        if self.plot_config['crosshair'] and not self.cursor:
            self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=1)
        elif not self.plot_config['crosshair'] and self.cursor:
            self.cursor = None
        
        # Update grid
        self.ax.grid(self.plot_config['grid'], alpha=0.3)
        self.canvas.draw()
    
    def set_update_callback(self, callback: Callable):
        """Set callback for real-time updates."""
        self.update_callback = callback
    
    def set_selection_callback(self, callback: Callable):
        """Set callback for point selection."""
        self.selection_callback = callback
    
    def plot_line(self, x_data, y_data, title="", xlabel="", ylabel="", **kwargs):
        """Create an interactive line plot."""
        self.ax.clear()
        
        # Store data for interactions
        self.plot_data = {
            'type': 'line',
            'x_data': x_data,
            'y_data': y_data,
            'title': title,
            'xlabel': xlabel,
            'ylabel': ylabel
        }
        
        # Plot with enhanced styling
        line_color = kwargs.get('color', '#1f77b4')
        line_width = kwargs.get('linewidth', 2)
        alpha = kwargs.get('alpha', 0.8)
        
        line, = self.ax.plot(x_data, y_data, color=line_color, linewidth=line_width, alpha=alpha)
        
        # Add markers for data points if requested
        if kwargs.get('show_markers', False):
            self.ax.scatter(x_data, y_data, color=line_color, s=30, alpha=0.7, zorder=5)
        
        self._apply_styling(title, xlabel, ylabel)
        self.canvas.draw()
        
        return line
    
    def plot_bar(self, categories, values, title="", xlabel="", ylabel="", **kwargs):
        """Create an interactive bar chart."""
        self.ax.clear()
        
        # Store data for interactions
        self.plot_data = {
            'type': 'bar',
            'categories': categories,
            'values': values,
            'title': title,
            'xlabel': xlabel,
            'ylabel': ylabel
        }
        
        # Plot with enhanced styling
        bar_color = kwargs.get('color', '#3B8ED0')
        alpha = kwargs.get('alpha', 0.8)
        
        bars = self.ax.bar(categories, values, color=bar_color, alpha=alpha)
        
        # Add value labels on bars if requested
        if kwargs.get('show_values', False):
            for bar, value in zip(bars, values):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                           f'{value:.1f}', ha='center', va='bottom', fontsize=9)
        
        self._apply_styling(title, xlabel, ylabel)
        self.canvas.draw()
        
        return bars
    
    def plot_scatter(self, x_data, y_data, title="", xlabel="", ylabel="", **kwargs):
        """Create an interactive scatter plot."""
        self.ax.clear()
        
        # Store data for interactions
        self.plot_data = {
            'type': 'scatter',
            'x_data': x_data,
            'y_data': y_data,
            'title': title,
            'xlabel': xlabel,
            'ylabel': ylabel
        }
        
        # Plot with enhanced styling
        scatter_color = kwargs.get('color', '#ff7f0e')
        size = kwargs.get('s', 50)
        alpha = kwargs.get('alpha', 0.6)
        
        scatter = self.ax.scatter(x_data, y_data, c=scatter_color, s=size, alpha=alpha)
        
        # Add trend line if requested
        if kwargs.get('show_trend', False):
            z = np.polyfit(x_data, y_data, 1)
            p = np.poly1d(z)
            self.ax.plot(x_data, p(x_data), "r--", alpha=0.8, linewidth=1)
        
        self._apply_styling(title, xlabel, ylabel)
        self.canvas.draw()
        
        return scatter
    
    def plot_heatmap(self, data, title="", **kwargs):
        """Create an interactive heatmap."""
        self.ax.clear()
        
        # Store data for interactions
        self.plot_data = {
            'type': 'heatmap',
            'data': data,
            'title': title
        }
        
        # Plot with enhanced styling
        cmap = kwargs.get('cmap', 'viridis')
        
        im = self.ax.imshow(data, cmap=cmap, aspect='auto', interpolation='nearest')
        
        # Add colorbar
        if not hasattr(self, '_colorbar') or self._colorbar is None:
            self._colorbar = self.figure.colorbar(im, ax=self.ax)
        else:
            self._colorbar.update_normal(im)
        
        # Add value annotations if requested
        if kwargs.get('show_values', False):
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    text = self.ax.text(j, i, f'{data[i, j]:.2f}',
                                      ha="center", va="center", color="white", fontsize=8)
        
        self.ax.set_title(title)
        self.ax.grid(self.plot_config['grid'], alpha=0.3)
        self.canvas.draw()
        
        return im
    
    def plot_multiple_series(self, data_series: List[Dict[str, Any]], title="", xlabel="", ylabel=""):
        """Plot multiple data series on the same axes."""
        self.ax.clear()
        
        # Store data for interactions
        self.plot_data = {
            'type': 'multiple_series',
            'series': data_series,
            'title': title,
            'xlabel': xlabel,
            'ylabel': ylabel
        }
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(data_series)))
        
        for i, series in enumerate(data_series):
            x_data = series.get('x_data', [])
            y_data = series.get('y_data', [])
            label = series.get('label', f'Series {i+1}')
            plot_type = series.get('type', 'line')
            
            if plot_type == 'line':
                self.ax.plot(x_data, y_data, color=colors[i], label=label, linewidth=2)
            elif plot_type == 'scatter':
                self.ax.scatter(x_data, y_data, color=colors[i], label=label, alpha=0.7)
            elif plot_type == 'bar':
                self.ax.bar(x_data, y_data, color=colors[i], label=label, alpha=0.7)
        
        # Add legend
        self.ax.legend(loc='best')
        
        self._apply_styling(title, xlabel, ylabel)
        self.canvas.draw()
    
    def update_data(self, new_data: Dict[str, Any]):
        """Update plot with new data (for real-time updates)."""
        plot_type = new_data.get('type', self.plot_data.get('type', 'line'))
        
        if plot_type == 'line':
            self.plot_line(
                new_data.get('x_data', []),
                new_data.get('y_data', []),
                new_data.get('title', ''),
                new_data.get('xlabel', ''),
                new_data.get('ylabel', '')
            )
        elif plot_type == 'bar':
            self.plot_bar(
                new_data.get('categories', []),
                new_data.get('values', []),
                new_data.get('title', ''),
                new_data.get('xlabel', ''),
                new_data.get('ylabel', '')
            )
        elif plot_type == 'scatter':
            self.plot_scatter(
                new_data.get('x_data', []),
                new_data.get('y_data', []),
                new_data.get('title', ''),
                new_data.get('xlabel', ''),
                new_data.get('ylabel', '')
            )
        elif plot_type == 'heatmap':
            self.plot_heatmap(
                new_data.get('data', []),
                new_data.get('title', '')
            )
        
        # Trigger update callback if set
        if self.update_callback:
            self.update_callback(new_data)
    
    def _apply_styling(self, title: str, xlabel: str, ylabel: str):
        """Apply consistent styling to plots."""
        self.ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        self.ax.set_xlabel(xlabel, fontsize=12)
        self.ax.set_ylabel(ylabel, fontsize=12)
        self.ax.grid(self.plot_config['grid'], alpha=0.3)
        
        # Improve tick formatting
        self.ax.tick_params(axis='both', which='major', labelsize=10)
        
        # Set background color
        self.ax.set_facecolor('#fafafa')
    
    def _toggle_zoom(self):
        """Toggle zoom mode."""
        # This would integrate with matplotlib's zoom functionality
        pass
    
    def _toggle_pan(self):
        """Toggle pan mode."""
        # This would integrate with matplotlib's pan functionality
        pass
    
    def _reset_view(self):
        """Reset view to original bounds."""
        self.ax.relim()
        self.ax.autoscale()
        self.canvas.draw()
    
    def _toggle_grid(self):
        """Toggle grid visibility."""
        self.plot_config['grid'] = not self.plot_config['grid']
        self.ax.grid(self.plot_config['grid'], alpha=0.3)
        self.canvas.draw()
    
    def _toggle_crosshair(self):
        """Toggle crosshair cursor."""
        self.plot_config['crosshair'] = not self.plot_config['crosshair']
        self.configure_interactions(self.plot_config)
    
    def _export_plot(self):
        """Export plot to file."""
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
        """Handle mouse click events."""
        if event.inaxes != self.ax:
            return
        
        if self.plot_config['selection_enabled'] and event.button == 1:  # Left click
            # Find nearest data point
            if 'x_data' in self.plot_data and 'y_data' in self.plot_data:
                x_data = self.plot_data['x_data']
                y_data = self.plot_data['y_data']
                
                if x_data and y_data:
                    # Find closest point
                    distances = [(abs(x - event.xdata) + abs(y - event.ydata)) 
                               for x, y in zip(x_data, y_data)]
                    closest_idx = distances.index(min(distances))
                    
                    selected_point = {
                        'index': closest_idx,
                        'x': x_data[closest_idx],
                        'y': y_data[closest_idx]
                    }
                    
                    # Highlight selected point
                    self.ax.scatter([selected_point['x']], [selected_point['y']], 
                                  color='red', s=100, zorder=10, marker='o', 
                                  facecolors='none', edgecolors='red', linewidth=2)
                    self.canvas.draw()
                    
                    # Trigger selection callback
                    if self.selection_callback:
                        self.selection_callback(selected_point)
    
    def _on_hover(self, event):
        """Handle mouse hover events."""
        if not self.plot_config['hover_info'] or event.inaxes != self.ax:
            return
        
        # Show coordinates in status (could be enhanced with tooltips)
        if event.xdata is not None and event.ydata is not None:
            # This could be connected to a status bar or tooltip
            pass
    
    def _on_key_press(self, event):
        """Handle key press events."""
        if event.key == 'r':
            self._reset_view()
        elif event.key == 'g':
            self._toggle_grid()
        elif event.key == 'c':
            self._toggle_crosshair()
    
    def clear(self):
        """Clear the plot."""
        self.ax.clear()
        self.plot_data = {}
        if hasattr(self, '_colorbar') and self._colorbar:
            self._colorbar.remove()
            self._colorbar = None
        self.canvas.draw()


# Keep the original PlotCanvas for backward compatibility
class PlotCanvas(InteractivePlotCanvas):
    """Backward compatible plot canvas."""
    pass


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
