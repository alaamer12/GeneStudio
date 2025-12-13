"""Enterprise main window with multi-page navigation."""

import customtkinter as ctk
from views.page_manager import PageManager
from views.components import NavigationSidebar, Header, Footer, set_toast_container
from views.pages import (
    DashboardPage, WorkspacePage, AnalysisPage,
    VisualizationPage, PatternMatchingPage, GraphAnalysisPage,
    ReportsPage, SettingsPage, SequenceManagementPage, HelpPage, ExportPage
)
from views.pages.projects_page import ProjectsPage
from utils.window_state_manager import WindowStateManager


class MainWindowPro(ctk.CTk):
    """Enterprise-grade main window with multi-page navigation."""
    
    def __init__(self):
        super().__init__()
        
        # Hide window completely during initialization to prevent flickering
        self.withdraw()
        self.overrideredirect(True)  # Remove window decorations temporarily
        
        # Window state manager
        self.window_state_manager = WindowStateManager()
        
        # Window configuration
        self.title("GeneStudio Pro - Enterprise DNA Sequence Analysis")
        
        # Set up window state management (minimum size, restore state)
        self.window_state_manager.restore_window_state(self)
        self.window_state_manager.setup_window_callbacks(self)
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Header
        self.header = Header(self)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Navigation sidebar
        self.navigation = NavigationSidebar(self, on_navigate=self._on_navigate)
        self.navigation.grid(row=1, column=0, sticky="nsew")
        
        # Content area
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Page manager
        self.page_manager = PageManager(content_frame)
        
        # Register all pages
        self._register_pages()
        
        # Footer
        self.footer = Footer(self)
        self.footer.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Set up toast notification container
        set_toast_container(self)
        
        # Initialize with dashboard page to avoid lazy loading flicker
        self.page_manager.show_page("dashboard")
        
        # Show last active page or dashboard by default
        last_page = self.window_state_manager.get_last_page()
        if last_page != "dashboard":
            self.page_manager.show_page(last_page)
        self.navigation.set_active_page(last_page)
        
        # Show window after all initialization is complete
        self.after(50, self._show_window_after_init)
        
    def _register_pages(self):
        """Register all application pages."""
        self.page_manager.register_page("dashboard", DashboardPage)
        self.page_manager.register_page("projects", ProjectsPage)
        self.page_manager.register_page("workspace", WorkspacePage)
        self.page_manager.register_page("analysis", AnalysisPage)
        self.page_manager.register_page("pattern_matching", PatternMatchingPage)
        self.page_manager.register_page("sequence_management", SequenceManagementPage)
        self.page_manager.register_page("visualization", VisualizationPage)
        self.page_manager.register_page("graph_analysis", GraphAnalysisPage)
        self.page_manager.register_page("reports", ReportsPage)
        self.page_manager.register_page("export", ExportPage)
        self.page_manager.register_page("settings", SettingsPage)
        self.page_manager.register_page("help", HelpPage)
        
    def _on_navigate(self, page_id: str):
        """Handle navigation to a page."""
        # Update page
        self.page_manager.show_page(page_id)
        
        # Save last active page
        self.window_state_manager.save_last_page(page_id)
        
        # Update breadcrumb
        page_names = {
            "dashboard": "Dashboard",
            "projects": "Projects",
            "workspace": "Workspace",
            "analysis": "Analysis Tools",
            "pattern_matching": "Pattern Matching",
            "sequence_management": "Sequence Management",
            "visualization": "Visualizations",
            "graph_analysis": "Graph Analysis",
            "reports": "Reports",
            "export": "Export Data",
            "settings": "Settings",
            "help": "Help & Documentation"
        }
        
        self.header.update_breadcrumb(page_names.get(page_id, page_id))
        
        # Update footer
        self.footer.set_status(f"Viewing: {page_names.get(page_id, page_id)}")
    
    def _show_window_after_init(self):
        """Show window after all initialization is complete."""
        # Restore window decorations
        self.overrideredirect(False)
        
        # Show the window
        self.deiconify()
        
        # Ensure proper window state
        self.lift()
        self.focus_force()
        
        # Apply any pending window state changes
        self.update_idletasks()
