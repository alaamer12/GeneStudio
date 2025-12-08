"""Dashboard page - main landing page."""

import customtkinter as ctk
from views.components import StatCard, ActionCard, InfoCard, PrimaryButton


class DashboardPage(ctk.CTkFrame):
    """Dashboard with stats and quick actions."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Welcome section
        welcome_frame = ctk.CTkFrame(self, fg_color="transparent")
        welcome_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(
            welcome_frame,
            text="Welcome to GeneStudio Pro",
            font=("Arial", 28, "bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            welcome_frame,
            text="Enterprise-grade DNA sequence analysis platform",
            font=("Arial", 14),
            text_color="gray"
        ).pack(anchor="w", pady=(5, 0))
        
        # Stats cards
        StatCard(
            self,
            title="Total Sequences",
            value="0",
            icon="🧬"
        ).grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        StatCard(
            self,
            title="Active Projects",
            value="0",
            icon="📁"
        ).grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        StatCard(
            self,
            title="Analyses Run",
            value="0",
            icon="🔬"
        ).grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        
        StatCard(
            self,
            title="Reports Generated",
            value="0",
            icon="📊"
        ).grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
        
        # Quick actions
        actions_frame = ctk.CTkFrame(self)
        actions_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=("Arial", 16, "bold")
        ).pack(padx=20, pady=(20, 10), anchor="w")
        
        ActionCard(
            actions_frame,
            title="New Project",
            description="Create a new analysis project",
            button_text="Create Project"
        ).pack(padx=20, pady=10, fill="x")
        
        ActionCard(
            actions_frame,
            title="Load Sequences",
            description="Import FASTA files for analysis",
            button_text="Load FASTA"
        ).pack(padx=20, pady=10, fill="x")
        
        ActionCard(
            actions_frame,
            title="Run Analysis",
            description="Start a new sequence analysis",
            button_text="Start Analysis"
        ).pack(padx=20, pady=(10, 20), fill="x")
        
        # Recent activity
        activity_frame = ctk.CTkFrame(self)
        activity_frame.grid(row=2, column=2, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            activity_frame,
            text="Recent Activity",
            font=("Arial", 16, "bold")
        ).pack(padx=20, pady=(20, 10), anchor="w")
        
        InfoCard(
            activity_frame,
            title="No recent activity",
            content="Your recent analyses and projects will appear here"
        ).pack(padx=20, pady=(10, 20), fill="both", expand=True)
