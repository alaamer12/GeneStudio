"""Navigation sidebar component."""

import customtkinter as ctk
from typing import Callable, Optional


class NavigationSidebar(ctk.CTkFrame):
    """Professional navigation sidebar with icons and collapsible menu."""
    
    def __init__(self, parent, on_navigate: Callable[[str], None]):
        """
        Initialize navigation sidebar.
        
        Args:
            parent: Parent widget
            on_navigate: Callback function when navigation item is clicked
        """
        super().__init__(parent, width=250, corner_radius=0)
        
        self.on_navigate = on_navigate
        self.current_page = None
        self.nav_buttons = {}
        
        # Configure grid
        self.grid_rowconfigure(20, weight=1)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(
            title_frame,
            text="🧬 GeneStudio Pro",
            font=("Arial", 20, "bold")
        ).pack()
        
        # Navigation items
        self._create_nav_section("MAIN", 1)
        self._create_nav_item("Dashboard", "🏠", "dashboard", 2)
        self._create_nav_item("Projects", "📁", "projects", 3)
        self._create_nav_item("Workspace", "💼", "workspace", 4)
        
        self._create_nav_section("ANALYSIS", 5)
        self._create_nav_item("Analysis Tools", "🔬", "analysis", 6)
        self._create_nav_item("Pattern Matching", "🔍", "pattern_matching", 7)
        self._create_nav_item("Sequence Mgmt", "📊", "sequence_management", 8)
        
        self._create_nav_section("VISUALIZATION", 9)
        self._create_nav_item("Visualizations", "📈", "visualization", 10)
        self._create_nav_item("Graph Analysis", "🕸️", "graph_analysis", 11)
        
        self._create_nav_section("REPORTS", 12)
        self._create_nav_item("Reports", "📄", "reports", 13)
        self._create_nav_item("Export Data", "💾", "export", 14)
        
        self._create_nav_section("SYSTEM", 15)
        self._create_nav_item("Settings", "⚙️", "settings", 16)
        self._create_nav_item("Help", "❓", "help", 17)
        
        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=21, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(
            footer,
            text="v2.0 Enterprise",
            font=("Arial", 10),
            text_color="gray"
        ).pack()
        
    def _create_nav_section(self, title: str, row: int):
        """Create a navigation section header."""
        label = ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 10, "bold"),
            text_color="gray",
            anchor="w"
        )
        label.grid(row=row, column=0, padx=20, pady=(15, 5), sticky="ew")
        
    def _create_nav_item(self, text: str, icon: str, page_id: str, row: int):
        """Create a navigation item button."""
        btn = ctk.CTkButton(
            self,
            text=f"{icon}  {text}",
            anchor="w",
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            command=lambda: self._navigate_to(page_id)
        )
        btn.grid(row=row, column=0, padx=10, pady=2, sticky="ew")
        self.nav_buttons[page_id] = btn
        
    def _navigate_to(self, page_id: str):
        """Handle navigation to a page."""
        # Reset all buttons
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent")
        
        # Highlight current button
        if page_id in self.nav_buttons:
            self.nav_buttons[page_id].configure(fg_color=("gray75", "gray25"))
        
        self.current_page = page_id
        self.on_navigate(page_id)
        
    def set_active_page(self, page_id: str):
        """Set active page programmatically."""
        self._navigate_to(page_id)
