"""Projects page - project management."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, DataTable, ActionCard


class ProjectsPage(ctk.CTkFrame):
    """Project management page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="Projects",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        PrimaryButton(
            header_frame,
            text="➕ New Project",
            width=150
        ).pack(side="right", padx=5)
        
        SecondaryButton(
            header_frame,
            text="📂 Open Project",
            width=150
        ).pack(side="right", padx=5)
        
        # Project templates
        templates_frame = ctk.CTkFrame(self)
        templates_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            templates_frame,
            text="Project Templates",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        template_cards = ctk.CTkFrame(templates_frame, fg_color="transparent")
        template_cards.pack(fill="x", padx=20, pady=(0, 15))
        
        ActionCard(
            template_cards,
            title="Sequence Analysis",
            description="Basic sequence operations and pattern matching",
            button_text="Use Template"
        ).pack(side="left", padx=5, fill="both", expand=True)
        
        ActionCard(
            template_cards,
            title="Genome Assembly",
            description="Overlap graph and de novo assembly",
            button_text="Use Template"
        ).pack(side="left", padx=5, fill="both", expand=True)
        
        ActionCard(
            template_cards,
            title="Comparative Analysis",
            description="Multiple sequence alignment and comparison",
            button_text="Use Template"
        ).pack(side="left", padx=5, fill="both", expand=True)
        
        # Recent projects table
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            table_frame,
            text="Recent Projects",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        self.projects_table = DataTable(
            table_frame,
            columns=["Project Name", "Type", "Created", "Last Modified", "Status"]
        )
        self.projects_table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Add sample data
        self.projects_table.add_row(["Sample Project 1", "Sequence Analysis", "2024-12-01", "2024-12-08", "Active"])
        self.projects_table.add_row(["Genome Assembly", "Assembly", "2024-11-28", "2024-12-05", "Completed"])
