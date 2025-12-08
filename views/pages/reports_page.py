"""Reports page."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, DataTable, ActionCard


class ReportsPage(ctk.CTkFrame):
    """Reports generation and management page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Reports",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        PrimaryButton(
            header,
            text="📄 New Report",
            width=140
        ).pack(side="right", padx=5)
        
        # Report templates
        templates_frame = ctk.CTkFrame(self)
        templates_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            templates_frame,
            text="Report Templates",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        templates_grid = ctk.CTkFrame(templates_frame, fg_color="transparent")
        templates_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        ActionCard(
            templates_grid,
            title="Analysis Summary",
            description="Comprehensive analysis results",
            button_text="Generate"
        ).pack(side="left", padx=5, fill="both", expand=True)
        
        ActionCard(
            templates_grid,
            title="Quality Report",
            description="Sequence quality metrics",
            button_text="Generate"
        ).pack(side="left", padx=5, fill="both", expand=True)
        
        ActionCard(
            templates_grid,
            title="Custom Report",
            description="Build your own report",
            button_text="Create"
        ).pack(side="left", padx=5, fill="both", expand=True)
        
        # Export options
        export_frame = ctk.CTkFrame(self)
        export_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            export_frame,
            text="Export Options",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        export_buttons = ctk.CTkFrame(export_frame, fg_color="transparent")
        export_buttons.pack(fill="x", padx=20, pady=(0, 15))
        
        SecondaryButton(export_buttons, text="📄 PDF", width=100).pack(side="left", padx=5)
        SecondaryButton(export_buttons, text="📊 Excel", width=100).pack(side="left", padx=5)
        SecondaryButton(export_buttons, text="📝 CSV", width=100).pack(side="left", padx=5)
        SecondaryButton(export_buttons, text="🌐 HTML", width=100).pack(side="left", padx=5)
        SecondaryButton(export_buttons, text="📋 JSON", width=100).pack(side="left", padx=5)
        
        # Recent reports
        reports_frame = ctk.CTkFrame(self)
        reports_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            reports_frame,
            text="Recent Reports",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        self.reports_table = DataTable(
            reports_frame,
            columns=["Report Name", "Type", "Generated", "Format", "Status"]
        )
        self.reports_table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Sample data
        self.reports_table.add_row(["Analysis_Report_001", "Analysis Summary", "2024-12-08 10:30", "PDF", "Ready"])
        self.reports_table.add_row(["Quality_Check_002", "Quality Report", "2024-12-07 15:45", "Excel", "Ready"])
