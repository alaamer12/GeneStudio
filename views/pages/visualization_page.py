"""Visualization page - interactive plots and charts."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, PlotCanvas, PieChart
import numpy as np


class VisualizationPage(ctk.CTkFrame):
    """Visualization hub with interactive plots."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Data Visualization",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        PrimaryButton(
            header,
            text="💾 Export Plot",
            width=130
        ).pack(side="right", padx=5)
        
        SecondaryButton(
            header,
            text="🔄 Refresh",
            width=130
        ).pack(side="right", padx=5)
        
        # Visualization types sidebar
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        
        ctk.CTkLabel(
            sidebar,
            text="Plot Types",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=15, anchor="w")
        
        plot_types = [
            "📈 Line Plot",
            "📊 Bar Chart",
            "🔵 Scatter Plot",
            "🟦 Heatmap",
            "🥧 Pie Chart",
            "🍩 Donut Chart",
            "📉 Area Chart",
            "📐 3D Surface",
            "🕸️ 3D Graph"
        ]
        
        for plot_type in plot_types:
            ctk.CTkButton(
                sidebar,
                text=plot_type,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda pt=plot_type: self._show_plot(pt)
            ).pack(fill="x", padx=10, pady=2)
        
        # Plot area
        plot_frame = ctk.CTkFrame(self)
        plot_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        
        # Plot controls
        controls = ctk.CTkFrame(plot_frame, height=60)
        controls.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            controls,
            text="Data Source:",
            font=("Arial", 11)
        ).pack(side="left", padx=10)
        
        ctk.CTkOptionMenu(
            controls,
            values=["Current Sequence", "Analysis Results", "Custom Data"],
            width=180
        ).pack(side="left", padx=5)
        
        PrimaryButton(
            controls,
            text="Generate Plot",
            width=120,
            command=self._generate_sample_plot
        ).pack(side="left", padx=10)
        
        # Plot canvas
        self.plot_canvas = PlotCanvas(plot_frame)
        self.plot_canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Generate initial plot
        self._generate_sample_plot()
        
    def _show_plot(self, plot_type):
        """Show selected plot type."""
        pass  # Placeholder
        
    def _generate_sample_plot(self):
        """Generate sample plot."""
        x = np.linspace(0, 100, 100)
        y = np.random.rand(100) * 50 + 25
        
        self.plot_canvas.plot_line(
            x, y,
            title="GC Content Distribution",
            xlabel="Position (bp)",
            ylabel="GC Content (%)"
        )
