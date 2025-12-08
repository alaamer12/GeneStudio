"""Header component with breadcrumbs and actions."""

import customtkinter as ctk
from datetime import datetime


class Header(ctk.CTkFrame):
    """Professional header bar with breadcrumbs and actions."""
    
    def __init__(self, parent):
        """Initialize header."""
        super().__init__(parent, height=60, corner_radius=0)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Breadcrumb area
        self.breadcrumb_label = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        self.breadcrumb_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search sequences, patterns...",
            width=300
        )
        self.search_entry.pack(side="left", padx=5)
        
        # Notification button
        self.notif_btn = ctk.CTkButton(
            search_frame,
            text="🔔",
            width=40,
            command=self._show_notifications
        )
        self.notif_btn.pack(side="left", padx=5)
        
        # User profile button
        self.profile_btn = ctk.CTkButton(
            search_frame,
            text="👤 User",
            width=100,
            command=self._show_profile_menu
        )
        self.profile_btn.pack(side="left", padx=5)
        
    def update_breadcrumb(self, page_name: str):
        """Update breadcrumb text."""
        self.breadcrumb_label.configure(text=page_name)
        
    def _show_notifications(self):
        """Show notifications panel."""
        # Placeholder for notifications
        pass
        
    def _show_profile_menu(self):
        """Show user profile menu."""
        # Placeholder for profile menu
        pass
