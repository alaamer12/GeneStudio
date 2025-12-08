"""Analysis page - comprehensive analysis tools."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, DataTable


class AnalysisPage(ctk.CTkFrame):
    """Analysis tools page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Analysis types sidebar
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        ctk.CTkLabel(
            sidebar,
            text="Analysis Types",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=15, anchor="w")
        
        analysis_types = [
            "🧬 Basic Operations",
            "🔍 Pattern Matching",
            "🧪 Translation",
            "📊 Suffix Arrays",
            "🎯 Approximate Matching",
            "📈 Statistical Analysis",
            "🔬 Motif Discovery",
            "🧮 Alignment",
            "📉 Quality Control"
        ]
        
        for analysis in analysis_types:
            ctk.CTkButton(
                sidebar,
                text=analysis,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30")
            ).pack(fill="x", padx=10, pady=2)
        
        # Main analysis area
        main_area = ctk.CTkFrame(self)
        main_area.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Header
        header = ctk.CTkFrame(main_area, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Basic Operations",
            font=("Arial", 20, "bold")
        ).pack(side="left")
        
        PrimaryButton(
            header,
            text="▶️ Run Analysis",
            width=150
        ).pack(side="right")
        
        # Configuration panel
        config_frame = ctk.CTkFrame(main_area)
        config_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            config_frame,
            text="Configuration",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        # Input sequence
        ctk.CTkLabel(
            config_frame,
            text="Input Sequence:",
            font=("Arial", 11)
        ).pack(padx=20, pady=(5, 2), anchor="w")
        
        sequence_input = ctk.CTkTextbox(config_frame, height=100)
        sequence_input.pack(fill="x", padx=20, pady=(0, 10))
        sequence_input.insert("1.0", "ATCGATCGATCGATCG")
        
        # Operation selector
        op_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        op_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            op_frame,
            text="Operation:",
            font=("Arial", 11)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkOptionMenu(
            op_frame,
            values=["GC Content", "Reverse", "Complement", "Reverse Complement"],
            width=200
        ).pack(side="left")
        
        # Results panel
        results_frame = ctk.CTkFrame(main_area)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            results_frame,
            text="Results",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        self.results_text = ctk.CTkTextbox(results_frame, font=("Courier", 11))
        self.results_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.results_text.insert("1.0", "Results will appear here after running analysis...")
        self.results_text.configure(state="disabled")
