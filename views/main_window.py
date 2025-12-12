"""Enterprise main window with multi-page navigation."""

import customtkinter as ctk
from views.page_manager import PageManager
from views.components import NavigationSidebar, Header, Footer
from views.pages import (
    DashboardPage, ProjectsPage, WorkspacePage, AnalysisPage,
    VisualizationPage, PatternMatchingPage, GraphAnalysisPage,
    ReportsPage, SettingsPage, SequenceManagementPage, HelpPage, ExportPage
)


class MainWindowPro(ctk.CTk):
    """Enterprise-grade main window with multi-page navigation."""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("GeneStudio Pro - Enterprise DNA Sequence Analysis")
        self.geometry("1400x900")
        
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
        
        # Show dashboard by default
        self.navigation.set_active_page("dashboard")
        
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
