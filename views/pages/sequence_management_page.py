"""Sequence management page."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, DataTable


class SequenceManagementPage(ctk.CTkFrame):
    """Sequence library and management page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Sequence Management",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        PrimaryButton(
            header,
            text="➕ Import",
            width=120
        ).pack(side="right", padx=5)
        
        SecondaryButton(
            header,
            text="💾 Export",
            width=120
        ).pack(side="right", padx=5)
        
        # Toolbar
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkEntry(
            toolbar,
            placeholder_text="🔍 Search sequences...",
            width=300
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkOptionMenu(
            toolbar,
            values=["All Types", "DNA", "RNA", "Protein"],
            width=120
        ).pack(side="left", padx=5, pady=10)
        
        SecondaryButton(
            toolbar,
            text="🗑️ Delete Selected",
            width=140
        ).pack(side="right", padx=10, pady=10)
        
        SecondaryButton(
            toolbar,
            text="✏️ Edit Metadata",
            width=140
        ).pack(side="right", padx=5, pady=10)
        
        # Sequence table
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.sequence_table = DataTable(
            table_frame,
            columns=["ID", "Name", "Type", "Length", "GC%", "Date Added"]
        )
        self.sequence_table.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add sample data
        self.sequence_table.add_row(["SEQ001", "example_sequence", "DNA", "240 bp", "50.0%", "2024-12-08"])
        self.sequence_table.add_row(["SEQ002", "gc_rich_sequence", "DNA", "60 bp", "100.0%", "2024-12-08"])
        self.sequence_table.add_row(["SEQ003", "at_rich_sequence", "DNA", "58 bp", "0.0%", "2024-12-08"])
