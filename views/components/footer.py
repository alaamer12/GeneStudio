"""Footer status bar component."""

import customtkinter as ctk
from datetime import datetime
import threading


class Footer(ctk.CTkFrame):
    """Status bar footer with system information."""
    
    def __init__(self, parent):
        """Initialize footer."""
        super().__init__(parent, height=30, corner_radius=0)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=("Arial", 10),
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=10, sticky="w")
        
        # Center info
        self.info_label = ctk.CTkLabel(
            self,
            text="No project loaded",
            font=("Arial", 10),
            text_color="gray"
        )
        self.info_label.grid(row=0, column=1, sticky="ew")
        
        # Time label
        self.time_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 10),
            anchor="e"
        )
        self.time_label.grid(row=0, column=2, padx=10, sticky="e")
        
        # Start time update
        self._update_time()
        
    def _update_time(self):
        """Update time display."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=f"🕐 {current_time}")
        self.after(1000, self._update_time)
        
    def set_status(self, status: str):
        """Update status message."""
        self.status_label.configure(text=status)
        
    def set_info(self, info: str):
        """Update info message."""
        self.info_label.configure(text=info)
