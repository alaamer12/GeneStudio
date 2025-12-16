"""
Professional visualization components using matplotlib for GeneStudio.
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import seaborn as sns
from typing import List, Dict, Any, Optional


class VisualizationPanel(ctk.CTkFrame):
    """Professional visualization panel with matplotlib integration."""
    
    def __init__(self, parent, **kwargs):
        """Initialize visualization panel."""
        super().__init__(parent, **kwargs)
        
        # Configure matplotlib style
        plt.style.use('dark_background')
        sns.set_palette("husl")
        
        # Create figure and canvas
        self.figure = Figure(figsize=(10, 6), dpi=100, facecolor='#212121')
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Toolbar frame
        self.toolbar_frame = ctk.CTkFrame(self)
        self.toolbar_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Export button
        self.export_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="Export Plot",
            command=self._export_plot,
            width=100,
            height=30
        )
        self.export_btn.pack(side="right", padx=5, pady=5)
        
        # Clear button
        self.clear_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="Clear",
            command=self._clear_plot,
            width=80,
            height=30
        )
        self.clear_btn.pack(side="right", padx=5, pady=5)
    
    def plot_nucleotide_composition(self, sequence: str, title: str = "Nucleotide Composition"):
        """Plot nucleotide composition as a professional pie chart."""
        self.figure.clear()
        
        # Count nucleotides
        counts = {'A': 0, 'T': 0, 'G': 0, 'C': 0, 'N': 0}
        for nucleotide in sequence.upper():
            if nucleotide in counts:
                counts[nucleotide] += 1
            else:
                counts['N'] += 1
        
        # Remove zero counts
        counts = {k: v for k, v in counts.items() if v > 0}
        
        # Create subplot
        ax = self.figure.add_subplot(111)
        
        # Colors for nucleotides
        colors = {'A': '#FF6B6B', 'T': '#4ECDC4', 'G': '#45B7D1', 'C': '#96CEB4', 'N': '#FFEAA7'}
        plot_colors = [colors.get(k, '#95A5A6') for k in counts.keys()]
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            counts.values(),
            labels=counts.keys(),
            colors=plot_colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': 'white', 'fontsize': 12}
        )
        
        # Enhance appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=20)
        
        # Add statistics text
        total = sum(counts.values())
        gc_content = (counts.get('G', 0) + counts.get('C', 0)) / total * 100 if total > 0 else 0
        
        stats_text = f"Total: {total:,} bp\nGC Content: {gc_content:.1f}%"
        ax.text(1.3, 0.5, stats_text, transform=ax.transAxes, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#2C3E50', alpha=0.8),
                color='white', fontsize=11, verticalalignment='center')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_gc_content_window(self, sequence: str, window_size: int = 100, 
                              title: str = "GC Content Along Sequence"):
        """Plot GC content in sliding windows."""
        self.figure.clear()
        
        if len(sequence) < window_size:
            window_size = len(sequence) // 4 if len(sequence) > 4 else 1
        
        positions = []
        gc_contents = []
        
        for i in range(0, len(sequence) - window_size + 1, window_size // 4):
            window = sequence[i:i + window_size].upper()
            gc_count = window.count('G') + window.count('C')
            gc_content = (gc_count / len(window)) * 100 if len(window) > 0 else 0
            
            positions.append(i + window_size // 2)
            gc_contents.append(gc_content)
        
        # Create subplot
        ax = self.figure.add_subplot(111)
        
        # Plot line with gradient fill
        ax.plot(positions, gc_contents, color='#3498DB', linewidth=2, alpha=0.8)
        ax.fill_between(positions, gc_contents, alpha=0.3, color='#3498DB')
        
        # Add average line
        avg_gc = np.mean(gc_contents) if gc_contents else 0
        ax.axhline(y=avg_gc, color='#E74C3C', linestyle='--', linewidth=2, 
                  label=f'Average: {avg_gc:.1f}%')
        
        # Styling
        ax.set_xlabel('Position (bp)', color='white', fontsize=12)
        ax.set_ylabel('GC Content (%)', color='white', fontsize=12)
        ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend(facecolor='#2C3E50', edgecolor='none')
        
        # Format axes
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_pattern_matches(self, sequence: str, matches: List[int], pattern: str,
                           title: str = "Pattern Match Positions"):
        """Visualize pattern matches along the sequence."""
        self.figure.clear()
        
        if not matches:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No matches found', transform=ax.transAxes,
                   ha='center', va='center', color='white', fontsize=16)
            ax.set_title(title, color='white', fontsize=14, fontweight='bold')
            self.canvas.draw()
            return
        
        # Create subplot
        ax = self.figure.add_subplot(111)
        
        # Plot sequence length as background
        seq_length = len(sequence)
        ax.barh(0, seq_length, height=0.5, color='#34495E', alpha=0.3, label='Sequence')
        
        # Plot matches
        for i, match_pos in enumerate(matches):
            ax.barh(0, len(pattern), left=match_pos, height=0.3, 
                   color='#E74C3C', alpha=0.8)
        
        # Styling
        ax.set_xlabel('Position (bp)', color='white', fontsize=12)
        ax.set_title(f'{title}\nPattern: {pattern} | Matches: {len(matches)}', 
                    color='white', fontsize=14, fontweight='bold', pad=20)
        ax.set_yticks([])
        ax.grid(True, alpha=0.3, axis='x')
        
        # Format axes
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add match statistics
        if matches:
            stats_text = f"Total matches: {len(matches)}\n"
            stats_text += f"First match: {min(matches)}\n"
            stats_text += f"Last match: {max(matches)}\n"
            stats_text += f"Density: {len(matches)/seq_length*1000:.2f} per kb"
            
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='#2C3E50', alpha=0.8),
                   color='white', fontsize=10, verticalalignment='top')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_suffix_array_visualization(self, suffix_array: List[int], sequence: str,
                                      title: str = "Suffix Array Visualization"):
        """Visualize suffix array structure."""
        self.figure.clear()
        
        # Limit display for large arrays
        display_limit = 50
        if len(suffix_array) > display_limit:
            indices = np.linspace(0, len(suffix_array)-1, display_limit, dtype=int)
            display_sa = [suffix_array[i] for i in indices]
            display_positions = indices
        else:
            display_sa = suffix_array
            display_positions = list(range(len(suffix_array)))
        
        # Create subplot
        ax = self.figure.add_subplot(111)
        
        # Create heatmap-style visualization
        colors = plt.cm.viridis(np.array(display_sa) / len(sequence))
        bars = ax.bar(display_positions, display_sa, color=colors, alpha=0.8)
        
        # Styling
        ax.set_xlabel('Suffix Array Index', color='white', fontsize=12)
        ax.set_ylabel('Starting Position in Sequence', color='white', fontsize=12)
        ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        # Format axes
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, 
                                  norm=plt.Normalize(vmin=0, vmax=len(sequence)))
        sm.set_array([])
        cbar = self.figure.colorbar(sm, ax=ax)
        cbar.set_label('Position in Sequence', color='white', fontsize=10)
        cbar.ax.tick_params(colors='white')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_overlap_graph_stats(self, graph_data: Dict[str, List[str]], 
                                title: str = "Overlap Graph Statistics"):
        """Visualize overlap graph statistics."""
        self.figure.clear()
        
        if not graph_data:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No graph data available', transform=ax.transAxes,
                   ha='center', va='center', color='white', fontsize=16)
            ax.set_title(title, color='white', fontsize=14, fontweight='bold')
            self.canvas.draw()
            return
        
        # Calculate statistics
        node_degrees = [len(neighbors) for neighbors in graph_data.values()]
        
        # Create subplots
        fig = self.figure
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        
        # Degree distribution histogram
        ax1.hist(node_degrees, bins=max(1, len(set(node_degrees))), 
                color='#3498DB', alpha=0.7, edgecolor='white')
        ax1.set_xlabel('Node Degree', color='white', fontsize=10)
        ax1.set_ylabel('Frequency', color='white', fontsize=10)
        ax1.set_title('Degree Distribution', color='white', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(colors='white')
        
        # Graph statistics pie chart
        total_nodes = len(graph_data)
        isolated_nodes = sum(1 for deg in node_degrees if deg == 0)
        connected_nodes = total_nodes - isolated_nodes
        
        if total_nodes > 0:
            sizes = [connected_nodes, isolated_nodes]
            labels = ['Connected', 'Isolated']
            colors = ['#2ECC71', '#E74C3C']
            
            wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors,
                                              autopct='%1.1f%%', startangle=90,
                                              textprops={'color': 'white'})
            ax2.set_title('Node Connectivity', color='white', fontsize=12, fontweight='bold')
        
        # Format axes
        for ax in [ax1, ax2]:
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        fig.suptitle(title, color='white', fontsize=14, fontweight='bold')
        fig.tight_layout()
        self.canvas.draw()
    
    def _export_plot(self):
        """Export current plot to file."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight', 
                              facecolor='#212121', edgecolor='none')
    
    def _clear_plot(self):
        """Clear the current plot."""
        self.figure.clear()
        self.canvas.draw()


class StatisticsPanel(ctk.CTkFrame):
    """Professional statistics display panel."""
    
    def __init__(self, parent, **kwargs):
        """Initialize statistics panel."""
        super().__init__(parent, **kwargs)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="Sequence Statistics", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 20))
        
        # Statistics frame
        self.stats_frame = ctk.CTkScrollableFrame(self, height=200)
        self.stats_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.stats_labels = {}
    
    def update_statistics(self, sequence: str, header: str = ""):
        """Update statistics display."""
        # Clear existing labels
        for label in self.stats_labels.values():
            label.destroy()
        self.stats_labels.clear()
        
        if not sequence:
            return
        
        # Calculate statistics
        stats = self._calculate_statistics(sequence)
        
        # Display statistics
        row = 0
        for key, value in stats.items():
            # Key label
            key_label = ctk.CTkLabel(
                self.stats_frame,
                text=f"{key}:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            key_label.grid(row=row, column=0, sticky="w", padx=(10, 5), pady=2)
            
            # Value label
            value_label = ctk.CTkLabel(
                self.stats_frame,
                text=str(value),
                anchor="w"
            )
            value_label.grid(row=row, column=1, sticky="w", padx=(5, 10), pady=2)
            
            self.stats_labels[key] = (key_label, value_label)
            row += 1
    
    def _calculate_statistics(self, sequence: str) -> Dict[str, Any]:
        """Calculate comprehensive sequence statistics."""
        seq_upper = sequence.upper()
        length = len(seq_upper)
        
        if length == 0:
            return {"Length": "0 bp"}
        
        # Nucleotide counts
        counts = {'A': 0, 'T': 0, 'G': 0, 'C': 0, 'N': 0}
        for nucleotide in seq_upper:
            if nucleotide in counts:
                counts[nucleotide] += 1
            else:
                counts['N'] += 1
        
        # Calculate percentages and ratios
        gc_content = (counts['G'] + counts['C']) / length * 100
        at_content = (counts['A'] + counts['T']) / length * 100
        
        # Purine/Pyrimidine content
        purines = counts['A'] + counts['G']  # A, G
        pyrimidines = counts['T'] + counts['C']  # T, C
        
        stats = {
            "Length": f"{length:,} bp",
            "GC Content": f"{gc_content:.2f}%",
            "AT Content": f"{at_content:.2f}%",
            "Adenine (A)": f"{counts['A']:,} ({counts['A']/length*100:.1f}%)",
            "Thymine (T)": f"{counts['T']:,} ({counts['T']/length*100:.1f}%)",
            "Guanine (G)": f"{counts['G']:,} ({counts['G']/length*100:.1f}%)",
            "Cytosine (C)": f"{counts['C']:,} ({counts['C']/length*100:.1f}%)",
            "Unknown (N)": f"{counts['N']:,} ({counts['N']/length*100:.1f}%)",
            "Purines (A+G)": f"{purines:,} ({purines/length*100:.1f}%)",
            "Pyrimidines (T+C)": f"{pyrimidines:,} ({pyrimidines/length*100:.1f}%)"
        }
        
        # Add molecular weight (approximate)
        # Average molecular weights: A=331, T=322, G=347, C=307
        mol_weight = (counts['A'] * 331 + counts['T'] * 322 + 
                     counts['G'] * 347 + counts['C'] * 307) / 1000
        stats["Molecular Weight"] = f"{mol_weight:.1f} kDa"
        
        return stats