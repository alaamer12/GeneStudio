"""Export page."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton


class ExportPage(ctk.CTkFrame):
    """Data export page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Export Data",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        PrimaryButton(
            header,
            text="📤 Export",
            width=120
        ).pack(side="right")
        
        # Export configuration
        config_frame = ctk.CTkFrame(self)
        config_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            config_frame,
            text="Export Configuration",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(20, 15), anchor="w")
        
        # Data source
        ctk.CTkLabel(
            config_frame,
            text="Data Source:",
            font=("Arial", 11)
        ).pack(padx=20, pady=(10, 5), anchor="w")
        
        ctk.CTkOptionMenu(
            config_frame,
            values=["Current Sequence", "All Sequences", "Analysis Results", "Project Data"],
            width=300
        ).pack(padx=20, pady=(0, 15), anchor="w")
        
        # Format
        ctk.CTkLabel(
            config_frame,
            text="Export Format:",
            font=("Arial", 11)
        ).pack(padx=20, pady=(10, 5), anchor="w")
        
        format_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        format_frame.pack(padx=20, pady=(0, 15), anchor="w")
        
        ctk.CTkRadioButton(format_frame, text="FASTA", value=1).pack(side="left", padx=10)
        ctk.CTkRadioButton(format_frame, text="CSV", value=2).pack(side="left", padx=10)
        ctk.CTkRadioButton(format_frame, text="JSON", value=3).pack(side="left", padx=10)
        ctk.CTkRadioButton(format_frame, text="Excel", value=4).pack(side="left", padx=10)
        
        # Options
        ctk.CTkLabel(
            config_frame,
            text="Options:",
            font=("Arial", 11)
        ).pack(padx=20, pady=(15, 5), anchor="w")
        
        ctk.CTkCheckBox(
            config_frame,
            text="Include metadata"
        ).pack(padx=20, pady=5, anchor="w")
        
        ctk.CTkCheckBox(
            config_frame,
            text="Include analysis results"
        ).pack(padx=20, pady=5, anchor="w")
        
        ctk.CTkCheckBox(
            config_frame,
            text="Compress output"
        ).pack(padx=20, pady=5, anchor="w")
        
        # Output location
        ctk.CTkLabel(
            config_frame,
            text="Output Location:",
            font=("Arial", 11)
        ).pack(padx=20, pady=(15, 5), anchor="w")
        
        location_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        location_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkEntry(
            location_frame,
            placeholder_text="Select output folder...",
            width=400
        ).pack(side="left", padx=(0, 10))
        
        SecondaryButton(
            location_frame,
            text="Browse",
            width=100
        ).pack(side="left")
