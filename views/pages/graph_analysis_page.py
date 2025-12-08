"""Graph analysis page."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, Visualization3D
import numpy as np


class GraphAnalysisPage(ctk.CTkFrame):
    """Graph analysis and visualization page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Graph Analysis",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        PrimaryButton(
            header,
            text="🔨 Build Graph",
            width=130
        ).pack(side="right", padx=5)
        
        # Graph types sidebar
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        
        ctk.CTkLabel(
            sidebar,
            text="Graph Types",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=15, anchor="w")
        
        graph_types = [
            "🕸️ Overlap Graph",
            "🔷 De Bruijn Graph",
            "🌳 Phylogenetic Tree",
            "🔗 Alignment Graph",
            "📊 Dependency Graph"
        ]
        
        for graph_type in graph_types:
            ctk.CTkButton(
                sidebar,
                text=graph_type,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30")
            ).pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(
            sidebar,
            text="\nParameters",
            font=("Arial", 12, "bold")
        ).pack(padx=15, pady=(20, 10), anchor="w")
        
        # Min overlap
        param_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        param_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            param_frame,
            text="Min Overlap:",
            font=("Arial", 10)
        ).pack(anchor="w")
        
        ctk.CTkEntry(
            param_frame,
            placeholder_text="3",
            width=150
        ).pack(anchor="w", pady=2)
        
        # Visualization area
        viz_frame = ctk.CTkFrame(self)
        viz_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        
        # Controls
        controls = ctk.CTkFrame(viz_frame, height=60)
        controls.pack(fill="x", padx=10, pady=10)
        
        SecondaryButton(
            controls,
            text="🔄 Rotate",
            width=100
        ).pack(side="left", padx=5)
        
        SecondaryButton(
            controls,
            text="🔍 Zoom In",
            width=100
        ).pack(side="left", padx=5)
        
        SecondaryButton(
            controls,
            text="🔎 Zoom Out",
            width=100
        ).pack(side="left", padx=5)
        
        SecondaryButton(
            controls,
            text="💾 Export",
            width=100
        ).pack(side="left", padx=5)
        
        # 3D visualization
        self.viz_3d = Visualization3D(viz_frame)
        self.viz_3d.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Generate sample graph
        self._generate_sample_graph()
        
        # Graph info
        info_frame = ctk.CTkFrame(viz_frame)
        info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            info_frame,
            text="Nodes: 10 | Edges: 15 | Components: 1",
            font=("Arial", 10)
        ).pack(padx=10, pady=10)
        
    def _generate_sample_graph(self):
        """Generate sample 3D graph."""
        # Create sample nodes
        nodes = [(np.random.rand(), np.random.rand(), np.random.rand()) for _ in range(10)]
        
        # Create sample edges
        edges = [(i, (i + 1) % 10) for i in range(10)]
        edges += [(i, (i + 3) % 10) for i in range(0, 10, 2)]
        
        self.viz_3d.plot_graph_3d(nodes, edges, "Overlap Graph Visualization")
