"""Pattern matching page."""

import customtkinter as ctk
from views.components import PrimaryButton, DataTable


class PatternMatchingPage(ctk.CTkFrame):
    """Pattern matching analysis page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Pattern Matching",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        PrimaryButton(
            header,
            text="🔍 Search",
            width=120
        ).pack(side="right")
        
        # Configuration
        config_frame = ctk.CTkFrame(self)
        config_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            config_frame,
            text="Search Configuration",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        # Pattern input
        pattern_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        pattern_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            pattern_frame,
            text="Pattern:",
            width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkEntry(
            pattern_frame,
            placeholder_text="Enter DNA pattern (e.g., ATCG)",
            width=300
        ).pack(side="left")
        
        # Algorithm selector
        algo_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        algo_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            algo_frame,
            text="Algorithm:",
            width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkOptionMenu(
            algo_frame,
            values=["Boyer-Moore (Bad Char)", "Boyer-Moore (Good Suffix)", "Suffix Array", "KMP", "Naive"],
            width=300
        ).pack(side="left")
        
        # Options
        options_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        ctk.CTkCheckBox(options_frame, text="Case sensitive").pack(side="left", padx=10)
        ctk.CTkCheckBox(options_frame, text="Highlight matches").pack(side="left", padx=10)
        ctk.CTkCheckBox(options_frame, text="Show statistics").pack(side="left", padx=10)
        
        # Results
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            results_frame,
            text="Search Results",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        self.results_table = DataTable(
            results_frame,
            columns=["Position", "Match", "Context", "Score"]
        )
        self.results_table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Add sample results
        self.results_table.add_row(["0", "ATCG", "...ATCGATCG...", "100%"])
        self.results_table.add_row(["10", "ATCG", "...ATCGATCG...", "100%"])
