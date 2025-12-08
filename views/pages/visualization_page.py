"""Visualization page - interactive plots and charts."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, PlotCanvas, PieChart, DonutChart, AreaChart, Visualization3D
import numpy as np


class VisualizationPage(ctk.CTkFrame):
    """Visualization hub with interactive plots."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Set fixed seed for session
        np.random.seed(42)
        
        # Generate fixed session data
        self.session_data = {
            'line': (np.linspace(0, 100, 100), np.random.rand(100) * 50 + 25),
            'bar': (['A', 'T', 'C', 'G'], np.random.randint(50, 150, 4)),
            'scatter': (np.random.rand(50) * 100, np.random.rand(50) * 100),
            'heatmap': np.random.rand(10, 10),
            'pie': (['A', 'T', 'C', 'G'], np.random.randint(20, 100, 4)),
            'area': (np.linspace(0, 100, 100), np.random.rand(100) * 30 + 40),
            '3d_scatter': (np.random.rand(30), np.random.rand(30), np.random.rand(30)),
            '3d_surface': None  # Will generate on demand
        }
        
        # Current plot type
        self.current_plot_type = "line"
        
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
            width=130,
            command=self._refresh_plot
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
            ("📈 Line Plot", "line"),
            ("📊 Bar Chart", "bar"),
            ("🔵 Scatter Plot", "scatter"),
            ("🟦 Heatmap", "heatmap"),
            ("🥧 Pie Chart", "pie"),
            ("🍩 Donut Chart", "donut"),
            ("📉 Area Chart", "area"),
            ("📐 3D Surface", "3d_surface"),
            ("🕸️ 3D Graph", "3d_graph")
        ]
        
        self.plot_buttons = {}
        for display_name, plot_id in plot_types:
            btn = ctk.CTkButton(
                sidebar,
                text=display_name,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda pid=plot_id: self._show_plot(pid)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.plot_buttons[plot_id] = btn
        
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
            command=self._refresh_plot
        ).pack(side="left", padx=10)
        
        # Container for different plot types
        self.plot_container = ctk.CTkFrame(plot_frame, fg_color="transparent")
        self.plot_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create plot canvases
        self.plot_canvas_2d = PlotCanvas(self.plot_container)
        self.pie_chart = PieChart(self.plot_container)
        self.donut_chart = DonutChart(self.plot_container)
        self.area_chart = AreaChart(self.plot_container)
        self.viz_3d = Visualization3D(self.plot_container)
        
        # Show initial plot
        self._show_plot("line")
        
    def _show_plot(self, plot_type):
        """Show selected plot type."""
        # Hide all plots
        self.plot_canvas_2d.pack_forget()
        self.pie_chart.pack_forget()
        self.donut_chart.pack_forget()
        self.area_chart.pack_forget()
        self.viz_3d.pack_forget()
        
        # Reset button colors
        for btn in self.plot_buttons.values():
            btn.configure(fg_color="transparent")
        
        # Highlight selected button
        if plot_type in self.plot_buttons:
            self.plot_buttons[plot_type].configure(fg_color=("gray75", "gray25"))
        
        self.current_plot_type = plot_type
        
        # Show and generate appropriate plot
        if plot_type == "line":
            self.plot_canvas_2d.pack(fill="both", expand=True)
            x, y = self.session_data['line']
            self.plot_canvas_2d.plot_line(
                x, y,
                title="GC Content Distribution",
                xlabel="Position (bp)",
                ylabel="GC Content (%)"
            )
        
        elif plot_type == "bar":
            self.plot_canvas_2d.pack(fill="both", expand=True)
            categories, values = self.session_data['bar']
            self.plot_canvas_2d.plot_bar(
                categories, values,
                title="Nucleotide Distribution",
                xlabel="Nucleotide",
                ylabel="Count"
            )
        
        elif plot_type == "scatter":
            self.plot_canvas_2d.pack(fill="both", expand=True)
            x, y = self.session_data['scatter']
            self.plot_canvas_2d.plot_scatter(
                x, y,
                title="Sequence Similarity Scores",
                xlabel="Sequence A",
                ylabel="Sequence B"
            )
        
        elif plot_type == "heatmap":
            self.plot_canvas_2d.pack(fill="both", expand=True)
            data = self.session_data['heatmap']
            self.plot_canvas_2d.plot_heatmap(
                data,
                title="Similarity Matrix"
            )
        
        elif plot_type == "pie":
            self.pie_chart.pack(fill="both", expand=True)
            labels, values = self.session_data['pie']
            self.pie_chart.plot(
                labels, values,
                title="Base Composition"
            )
        
        elif plot_type == "donut":
            self.donut_chart.pack(fill="both", expand=True)
            labels, values = self.session_data['pie']
            self.donut_chart.plot(
                labels, values,
                title="Base Composition (Donut)"
            )
        
        elif plot_type == "area":
            self.area_chart.pack(fill="both", expand=True)
            x, y = self.session_data['area']
            self.area_chart.plot(
                x, y,
                title="Coverage Analysis",
                xlabel="Position (bp)",
                ylabel="Coverage"
            )
        
        elif plot_type == "3d_surface":
            self.viz_3d.pack(fill="both", expand=True)
            x = np.linspace(-5, 5, 50)
            y = np.linspace(-5, 5, 50)
            X, Y = np.meshgrid(x, y)
            Z = np.sin(np.sqrt(X**2 + Y**2))
            self.viz_3d.plot_3d_surface(X, Y, Z, "3D Surface Plot")
        
        elif plot_type == "3d_graph":
            self.viz_3d.pack(fill="both", expand=True)
            # Generate fixed 3D graph
            np.random.seed(42)
            nodes = [(np.random.rand(), np.random.rand(), np.random.rand()) for _ in range(10)]
            edges = [(i, (i + 1) % 10) for i in range(10)]
            edges += [(i, (i + 3) % 10) for i in range(0, 10, 2)]
            self.viz_3d.plot_graph_3d(nodes, edges, "3D Graph Visualization")
        
    def _refresh_plot(self):
        """Refresh current plot."""
        self._show_plot(self.current_plot_type)

