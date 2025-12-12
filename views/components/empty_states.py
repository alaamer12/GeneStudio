"""Empty state components with guidance messages and action buttons."""

import customtkinter as ctk
from typing import Optional, Callable


class EmptyState(ctk.CTkFrame):
    """Generic empty state component with icon, message, and action."""
    
    def __init__(self, parent, icon: str = "📁", title: str = "No data available",
                 message: str = "There's nothing here yet.", 
                 action_text: Optional[str] = None,
                 action_callback: Optional[Callable] = None,
                 secondary_action_text: Optional[str] = None,
                 secondary_action_callback: Optional[Callable] = None,
                 **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.icon = icon
        self.title = title
        self.message = message
        self.action_text = action_text
        self.action_callback = action_callback
        self.secondary_action_text = secondary_action_text
        self.secondary_action_callback = secondary_action_callback
        
        # Create content
        self._create_content()
    
    def _create_content(self):
        """Create empty state content."""
        # Center container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Icon
        icon_label = ctk.CTkLabel(
            container,
            text=self.icon,
            font=("Arial", 64)
        )
        icon_label.pack(pady=(0, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text=self.title,
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            container,
            text=self.message,
            font=("Arial", 14),
            text_color="gray",
            wraplength=400,
            justify="center"
        )
        message_label.pack(pady=(0, 30))
        
        # Actions
        if self.action_text and self.action_callback:
            actions_frame = ctk.CTkFrame(container, fg_color="transparent")
            actions_frame.pack()
            
            # Primary action
            primary_button = ctk.CTkButton(
                actions_frame,
                text=self.action_text,
                command=self.action_callback,
                font=("Arial", 14, "bold"),
                height=40,
                fg_color="#1f6aa5",
                hover_color="#1a5a8a"
            )
            primary_button.pack(side="left", padx=(0, 10) if self.secondary_action_text else 0)
            
            # Secondary action
            if self.secondary_action_text and self.secondary_action_callback:
                secondary_button = ctk.CTkButton(
                    actions_frame,
                    text=self.secondary_action_text,
                    command=self.secondary_action_callback,
                    font=("Arial", 14),
                    height=40,
                    fg_color="transparent",
                    border_width=1,
                    text_color=("gray10", "gray90"),
                    border_color=("gray70", "gray30")
                )
                secondary_button.pack(side="left")


class EmptyDashboard(EmptyState):
    """Dashboard-specific empty state with project creation guidance."""
    
    def __init__(self, parent, on_create_project: Optional[Callable] = None,
                 on_load_sample: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="🧬",
            title="Welcome to GeneStudio Pro",
            message="Get started by creating your first project or loading sample data to explore the features.",
            action_text="Create Project",
            action_callback=on_create_project,
            secondary_action_text="Load Sample Data",
            secondary_action_callback=on_load_sample,
            **kwargs
        )


class EmptyProjects(EmptyState):
    """Projects page empty state."""
    
    def __init__(self, parent, on_create_project: Optional[Callable] = None,
                 on_import_project: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="📁",
            title="No projects yet",
            message="Create your first project to organize your sequences and analyses, or import an existing project.",
            action_text="Create New Project",
            action_callback=on_create_project,
            secondary_action_text="Import Project",
            secondary_action_callback=on_import_project,
            **kwargs
        )


class EmptySequences(EmptyState):
    """Sequences empty state with import instructions."""
    
    def __init__(self, parent, on_import_fasta: Optional[Callable] = None,
                 on_create_sequence: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="🧬",
            title="No sequences loaded",
            message="Import FASTA files to start analyzing sequences, or create sequences manually.",
            action_text="Import FASTA",
            action_callback=on_import_fasta,
            secondary_action_text="Create Sequence",
            secondary_action_callback=on_create_sequence,
            **kwargs
        )


class EmptyAnalyses(EmptyState):
    """Analyses empty state with analysis suggestions."""
    
    def __init__(self, parent, on_run_analysis: Optional[Callable] = None,
                 on_view_templates: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="🔬",
            title="No analyses run yet",
            message="Run your first analysis on loaded sequences to see computational results and insights.",
            action_text="Run Analysis",
            action_callback=on_run_analysis,
            secondary_action_text="View Templates",
            secondary_action_callback=on_view_templates,
            **kwargs
        )


class EmptyResults(EmptyState):
    """Analysis results empty state."""
    
    def __init__(self, parent, on_run_analysis: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="📊",
            title="No results available",
            message="Run an analysis to see results and visualizations here.",
            action_text="Run Analysis",
            action_callback=on_run_analysis,
            **kwargs
        )


class EmptyReports(EmptyState):
    """Reports empty state."""
    
    def __init__(self, parent, on_generate_report: Optional[Callable] = None,
                 on_view_templates: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="📋",
            title="No reports generated",
            message="Generate reports from your analyses to share and document your findings.",
            action_text="Generate Report",
            action_callback=on_generate_report,
            secondary_action_text="View Templates",
            secondary_action_callback=on_view_templates,
            **kwargs
        )


class EmptySearch(EmptyState):
    """Search results empty state."""
    
    def __init__(self, parent, search_term: str = "", on_clear_search: Optional[Callable] = None,
                 on_modify_search: Optional[Callable] = None, **kwargs):
        message = f"No results found for '{search_term}'" if search_term else "No search results"
        suggestion = "Try different keywords or check your spelling." if search_term else "Enter a search term to find items."
        
        super().__init__(
            parent,
            icon="🔍",
            title="No results found",
            message=f"{message}. {suggestion}",
            action_text="Clear Search" if search_term else "Start Searching",
            action_callback=on_clear_search or on_modify_search,
            secondary_action_text="Modify Search" if search_term else None,
            secondary_action_callback=on_modify_search if search_term else None,
            **kwargs
        )


class EmptyWorkspace(EmptyState):
    """Workspace empty state."""
    
    def __init__(self, parent, on_open_file: Optional[Callable] = None,
                 on_create_file: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="📝",
            title="Workspace is empty",
            message="Open existing files or create new ones to start working with sequences.",
            action_text="Open File",
            action_callback=on_open_file,
            secondary_action_text="Create New",
            secondary_action_callback=on_create_file,
            **kwargs
        )


class EmptyVisualization(EmptyState):
    """Visualization empty state."""
    
    def __init__(self, parent, on_load_data: Optional[Callable] = None,
                 on_select_visualization: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="📈",
            title="No data to visualize",
            message="Load data or select a different visualization type to see charts and graphs.",
            action_text="Load Data",
            action_callback=on_load_data,
            secondary_action_text="Select Visualization",
            secondary_action_callback=on_select_visualization,
            **kwargs
        )


class EmptyActivity(EmptyState):
    """Activity feed empty state."""
    
    def __init__(self, parent, on_start_working: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="📝",
            title="No recent activity",
            message="Your recent actions and changes will appear here as you work with projects and sequences.",
            action_text="Start Working",
            action_callback=on_start_working,
            **kwargs
        )


class EmptySettings(EmptyState):
    """Settings empty state (for specific setting categories)."""
    
    def __init__(self, parent, category: str = "settings", 
                 on_reset_defaults: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="⚙️",
            title=f"No {category} configured",
            message=f"Configure your {category} to customize the application behavior.",
            action_text="Reset to Defaults",
            action_callback=on_reset_defaults,
            **kwargs
        )


class EmptyError(EmptyState):
    """Error state for when data loading fails."""
    
    def __init__(self, parent, error_message: str = "Failed to load data",
                 on_retry: Optional[Callable] = None,
                 on_report_issue: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            icon="⚠️",
            title="Something went wrong",
            message=f"{error_message}. Please try again or report the issue if it persists.",
            action_text="Try Again",
            action_callback=on_retry,
            secondary_action_text="Report Issue",
            secondary_action_callback=on_report_issue,
            **kwargs
        )