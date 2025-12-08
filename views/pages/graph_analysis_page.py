"""Graph analysis page."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, Visualization3D
import numpy as np


class GraphAnalysisPage(ctk.CTkFrame):
    """Graph analysis and visualization page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Set fixed seed for session
        np.random.seed(123)
        
        # Generate fixed session data for different graph types
        self.session_graphs = {
            'overlap': self._generate_overlap_graph(),
            'debruijn': self._generate_debruijn_graph(),
            'phylogenetic': self._generate_phylogenetic_tree(),
            'alignment': self._generate_alignment_graph(),
            'dependency': self._generate_dependency_graph()
        }
        
        self.current_graph_type = 'overlap'
        
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
            width=130,
            command=self._rebuild_graph
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
            ("🕸️ Overlap Graph", "overlap"),
            ("🔷 De Bruijn Graph", "debruijn"),
            ("🌳 Phylogenetic Tree", "phylogenetic"),
            ("🔗 Alignment Graph", "alignment"),
            ("📊 Dependency Graph", "dependency")
        ]
        
        self.graph_buttons = {}
        for display_name, graph_id in graph_types:
            btn = ctk.CTkButton(
                sidebar,
                text=display_name,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda gid=graph_id: self._show_graph(gid)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.graph_buttons[graph_id] = btn
        
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
        
        self.overlap_entry = ctk.CTkEntry(
            param_frame,
            placeholder_text="3",
            width=150
        )
        self.overlap_entry.pack(anchor="w", pady=2)
        self.overlap_entry.insert(0, "3")
        
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
        
        # Graph info
        self.info_frame = ctk.CTkFrame(viz_frame)
        self.info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=("Arial", 10)
        )
        self.info_label.pack(padx=10, pady=10)
        
        # Show initial graph
        self._show_graph('overlap')
        
    def _generate_overlap_graph(self):
        """Generate overlap graph data."""
        nodes = [(np.random.rand(), np.random.rand(), np.random.rand()) for _ in range(10)]
        edges = [(i, (i + 1) % 10) for i in range(10)]
        edges += [(i, (i + 3) % 10) for i in range(0, 10, 2)]
        return nodes, edges
        
    def _generate_debruijn_graph(self):
        """Generate De Bruijn graph data."""
        nodes = [(np.random.rand(), np.random.rand(), np.random.rand()) for _ in range(12)]
        edges = [(i, (i + 1) % 12) for i in range(12)]
        edges += [(i, (i + 2) % 12) for i in range(0, 12, 3)]
        return nodes, edges
        
    def _generate_phylogenetic_tree(self):
        """Generate phylogenetic tree data."""
        # Tree structure
        nodes = [
            (0.5, 0.5, 0.9),  # Root
            (0.3, 0.4, 0.7), (0.7, 0.4, 0.7),  # Level 1
            (0.2, 0.3, 0.5), (0.4, 0.3, 0.5), (0.6, 0.3, 0.5), (0.8, 0.3, 0.5),  # Level 2
            (0.1, 0.2, 0.3), (0.3, 0.2, 0.3), (0.5, 0.2, 0.3), (0.7, 0.2, 0.3), (0.9, 0.2, 0.3)  # Level 3
        ]
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (4, 8), (5, 9), (6, 10), (6, 11)]
        return nodes, edges
        
    def _generate_alignment_graph(self):
        """Generate alignment graph data."""
        nodes = [(np.random.rand(), np.random.rand(), np.random.rand()) for _ in range(8)]
        edges = [(i, i + 1) for i in range(7)]
        edges += [(0, 3), (2, 5), (4, 7)]
        return nodes, edges
        
    def _generate_dependency_graph(self):
        """Generate dependency graph data."""
        nodes = [(np.random.rand(), np.random.rand(), np.random.rand()) for _ in range(15)]
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (6, 9), (7, 10), (8, 11), (9, 12), (10, 13), (11, 14)]
        return nodes, edges
        
    def _show_graph(self, graph_type):
        """Show selected graph type."""
        # Reset button colors
        for btn in self.graph_buttons.values():
            btn.configure(fg_color="transparent")
        
        # Highlight selected button
        if graph_type in self.graph_buttons:
            self.graph_buttons[graph_type].configure(fg_color=("gray75", "gray25"))
        
        self.current_graph_type = graph_type
        
        # Get graph data
        nodes, edges = self.session_graphs[graph_type]
        
        # Update visualization
        graph_titles = {
            'overlap': 'Overlap Graph Visualization',
            'debruijn': 'De Bruijn Graph Visualization',
            'phylogenetic': 'Phylogenetic Tree',
            'alignment': 'Alignment Graph',
            'dependency': 'Dependency Graph'
        }
        
        self.viz_3d.plot_graph_3d(nodes, edges, graph_titles[graph_type])
        
        # Update info
        self.info_label.configure(
            text=f"Nodes: {len(nodes)} | Edges: {len(edges)} | Components: 1"
        )
        
    def _rebuild_graph(self):
        """Rebuild current graph."""
        self._show_graph(self.current_graph_type)

