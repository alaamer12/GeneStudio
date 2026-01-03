"""Dashboard page - main landing page with real data binding."""

import customtkinter as ctk
from typing import Optional, Any
from views.components import (
    StatCard, ActionCard, InfoCard, PrimaryButton,
    SkeletonCard, EmptyDashboard, ErrorBoundary, with_error_boundary,
    show_success, show_error
)
from viewmodels.dashboard_viewmodel import DashboardViewModel
from utils.themed_tooltips import (
    create_tooltip, create_status_tooltip, create_info_button_tooltip,
    create_info_button_with_tooltip, TooltipTemplates
)


class DashboardPage(ctk.CTkFrame):
    """Dashboard with real-time stats and activity."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Initialize ViewModel
        self.viewmodel = DashboardViewModel()
        self.viewmodel.add_observer(self._on_state_changed)
        
        # Configure grid
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Create UI components
        self._create_header()
        self._create_stats_section()
        self._create_content_section()
        
        # Load initial data
        self.after(100, self._load_dashboard_data)
    
    def _create_header(self):
        """Create welcome header section."""
        self.welcome_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.welcome_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=20, pady=20)
        
        # Header with info button
        header_container = ctk.CTkFrame(self.welcome_frame, fg_color="transparent")
        header_container.pack(anchor="w", fill="x")
        
        title_label = ctk.CTkLabel(
            header_container,
            text="Welcome to GeneStudio Pro",
            font=("Arial", 28, "bold")
        )
        title_label.pack(side="left", anchor="w")
        
        # Info button for dashboard explanation
        info_button, info_tooltip = create_info_button_with_tooltip(
            header_container,
            "Dashboard Overview\n\n"
            "The dashboard provides a real-time overview of your bioinformatics work:\n"
            "• Statistics cards show current project and sequence counts\n"
            "• Recent activity tracks your latest analyses and operations\n"
            "• Quick actions provide shortcuts to common tasks\n\n"
            "All data updates automatically as you work with projects and sequences."
        )
        info_button.pack(side="left", padx=(10, 0))
        
        subtitle_label = ctk.CTkLabel(
            self.welcome_frame,
            text="Enterprise-grade DNA sequence analysis platform",
            font=("Arial", 14),
            text_color="gray"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Add tooltip to subtitle
        create_tooltip(
            subtitle_label,
            "Professional bioinformatics software for sequence analysis, "
            "pattern matching, and computational biology research"
        )
    
    def _create_stats_section(self):
        """Create statistics cards section."""
        # Create placeholder for stats cards
        self.stats_frames = []
        for i in range(4):
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.grid(row=1, column=i, padx=10, pady=10, sticky="nsew")
            self.stats_frames.append(frame)
        
        # Initially show skeleton loaders
        self._show_stats_loading()
    
    def _create_content_section(self):
        """Create main content section with actions and activity."""
        # Quick actions frame
        self.actions_frame = ctk.CTkFrame(self)
        self.actions_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Activity frame
        self.activity_frame = ctk.CTkFrame(self)
        self.activity_frame.grid(row=2, column=2, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Add tooltips to the main content frames
        create_tooltip(
            self.actions_frame,
            "Quick Actions: Shortcuts to common tasks like creating projects, "
            "importing sequences, and running analyses"
        )
        
        create_tooltip(
            self.activity_frame,
            "Recent Activity: Your latest actions and analysis results. "
            "Click on items to view details or continue work."
        )
        
        # Initially show loading states
        self._show_content_loading()
    
    def _show_stats_loading(self):
        """Show skeleton loading for stats cards."""
        for frame in self.stats_frames:
            # Clear frame and stop any skeleton animations
            for widget in frame.winfo_children():
                # Stop skeleton animations before destroying
                if hasattr(widget, 'stop_shimmer'):
                    widget.stop_shimmer()
                widget.destroy()
            
            # Add simple loading frame instead of skeleton card
            loading_frame = ctk.CTkFrame(frame, width=200, height=120)
            loading_label = ctk.CTkLabel(loading_frame, text="Loading...", text_color="gray")
            loading_label.pack(expand=True)
            loading_frame.pack(fill="both", expand=True)
    
    def _show_content_loading(self):
        """Show loading states for content sections."""
        # Clear frames
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
        for widget in self.activity_frame.winfo_children():
            widget.destroy()
        
        # Actions loading with info button
        actions_header = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        actions_header.pack(padx=20, pady=(20, 10), anchor="w", fill="x")
        
        actions_label = ctk.CTkLabel(
            actions_header,
            text="Quick Actions",
            font=("Arial", 16, "bold")
        )
        actions_label.pack(side="left", anchor="w")
        
        # Info button for quick actions
        actions_info_button, actions_info_tooltip = create_info_button_with_tooltip(
            actions_header,
            "Quick Actions\n\n"
            "Shortcuts to common bioinformatics tasks:\n"
            "• Create Project: Start a new research project\n"
            "• Import FASTA: Load sequence data from files\n"
            "• Run Analysis: Execute algorithms on sequences\n"
            "• View Reports: Access analysis results and exports\n\n"
            "Actions adapt based on your current data and workflow state."
        )
        actions_info_button.pack(side="left", padx=(10, 0))
        
        # Activity loading with info button
        activity_header = ctk.CTkFrame(self.activity_frame, fg_color="transparent")
        activity_header.pack(padx=20, pady=(20, 10), anchor="w", fill="x")
        
        activity_label = ctk.CTkLabel(
            activity_header,
            text="Recent Activity",
            font=("Arial", 16, "bold")
        )
        activity_label.pack(side="left", anchor="w")
        
        # Info button for recent activity
        activity_info_button, activity_info_tooltip = create_info_button_with_tooltip(
            activity_header,
            "Recent Activity Feed\n\n"
            "Tracks your latest bioinformatics work:\n"
            "• Project creation and modifications\n"
            "• Sequence imports and edits\n"
            "• Analysis executions and results\n"
            "• Export and report generation\n\n"
            "Click on any activity item to view details or continue where you left off."
        )
        activity_info_button.pack(side="left", padx=(10, 0))
    
    def _load_dashboard_data(self):
        """Load dashboard data through ViewModel."""
        self.viewmodel.load_dashboard_data()
    
    def _on_state_changed(self, key: Optional[str], value: Any):
        """Handle ViewModel state changes."""
        if key == 'statistics':
            self._update_statistics(value)
        elif key == 'recent_activity':
            self._update_activity(value)
        elif key == 'loading_load_dashboard':
            if value:
                self._show_loading_state()
            else:
                self._hide_loading_state()
        elif key == 'error_load_dashboard':
            if value:
                self._show_error_state(value)
    
    def _update_statistics(self, stats: dict):
        """Update statistics cards with real data."""
        if not stats:
            return
        
        # Define stat cards configuration with detailed tooltips
        stat_configs = [
            {
                'title': 'Total Sequences',
                'key': 'total_sequences',
                'icon': '🧬',
                'tooltip': TooltipTemplates.bioinformatics_term(
                    'Total Sequences',
                    'The total number of DNA, RNA, or protein sequences imported into all projects.',
                    'Includes sequences from FASTA files and manually entered sequences. '
                    'Each sequence can be analyzed using various bioinformatics algorithms.'
                )
            },
            {
                'title': 'Active Projects',
                'key': 'active_projects',
                'icon': '📁',
                'tooltip': TooltipTemplates.bioinformatics_term(
                    'Active Projects',
                    'Projects currently being worked on (not archived or completed).',
                    'Projects organize related sequences and analyses. '
                    'Each project can contain multiple sequences and analysis results.'
                )
            },
            {
                'title': 'Analyses Run',
                'key': 'total_analyses',
                'icon': '🔬',
                'tooltip': TooltipTemplates.bioinformatics_term(
                    'Analyses Run',
                    'Total number of computational analyses performed on sequences.',
                    'Includes pattern matching, GC content calculation, translation, '
                    'and other bioinformatics algorithms. Both completed and failed analyses are counted.'
                )
            },
            {
                'title': 'Completed Analyses',
                'key': 'completed_analyses',
                'icon': '✅',
                'tooltip': TooltipTemplates.bioinformatics_term(
                    'Completed Analyses',
                    'Number of analyses that finished successfully with results.',
                    'Successful analyses produce results that can be viewed, exported, '
                    'and used for further research. Failed analyses are not included in this count.'
                )
            }
        ]
        
        # Update each stat card
        for i, (frame, config) in enumerate(zip(self.stats_frames, stat_configs)):
            # Clear frame and stop any skeleton animations
            for widget in frame.winfo_children():
                # Stop skeleton animations before destroying
                if hasattr(widget, 'stop_shimmer'):
                    widget.stop_shimmer()
                widget.destroy()
            
            # Get the actual value from stats using the key
            value = str(stats.get(config['key'], 0))
            
            # Add real stat card
            stat_card = StatCard(
                frame,
                title=config['title'],
                value=value,
                icon=config['icon']
            )
            stat_card.pack(fill="both", expand=True)
            
            # Add status tooltip to the stat card
            create_status_tooltip(
                stat_card,
                lambda cfg=config, val=value: f"{cfg['title']}: {val}\n\n{cfg['tooltip']}"
            )
    
    def _update_activity(self, activity: list):
        """Update recent activity section."""
        # Clear activity frame content (keep header)
        for widget in self.activity_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                continue  # Keep the header
            widget.destroy()
        
        if not activity:
            # Show empty state
            InfoCard(
                self.activity_frame,
                title="No recent activity",
                content="Your recent analyses and projects will appear here"
            ).pack(padx=20, pady=(10, 20), fill="both", expand=True)
        else:
            # Show activity items
            activity_list = ctk.CTkScrollableFrame(self.activity_frame)
            activity_list.pack(padx=20, pady=(10, 20), fill="both", expand=True)
            
            for item in activity[:5]:  # Show top 5 items
                self._create_activity_item(activity_list, item)
    
    def _create_activity_item(self, parent, item: dict):
        """Create an activity item widget."""
        item_frame = ctk.CTkFrame(parent)
        item_frame.pack(fill="x", pady=5)
        
        # Configure grid
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            item_frame,
            text=item.get('icon', '📝'),
            font=("Arial", 16)
        )
        icon_label.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="w")
        
        # Content
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.grid(row=0, column=1, padx=(0, 15), pady=10, sticky="ew")
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text=item.get('title', 'Unknown Activity'),
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            content_frame,
            text=item.get('description', ''),
            font=("Arial", 10),
            text_color="gray",
            anchor="w"
        )
        desc_label.pack(anchor="w", pady=(2, 0))
        
        # Make clickable
        def on_click(event, activity_id=item.get('id')):
            if activity_id:
                self.viewmodel.handle_activity_click(activity_id)
        
        item_frame.bind("<Button-1>", on_click)
        item_frame.configure(cursor="hand2")
    
    def _show_loading_state(self):
        """Show loading state for entire dashboard."""
        # Stats already show skeleton loaders
        pass
    
    def _hide_loading_state(self):
        """Hide loading state."""
        pass
    
    def _show_error_state(self, error_message: str):
        """Show error state."""
        # Clear all content and show error
        for frame in self.stats_frames:
            for widget in frame.winfo_children():
                widget.destroy()
            
            error_label = ctk.CTkLabel(
                frame,
                text="⚠️\nError loading",
                font=("Arial", 12),
                text_color="#d42f2f",
                justify="center"
            )
            error_label.pack(expand=True)
    
    def _update_quick_actions(self):
        """Update quick actions section."""
        # Clear actions frame content (keep header)
        for widget in self.actions_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                continue  # Keep the header
            widget.destroy()
        
        # Check if empty state should be shown
        if self.viewmodel.is_empty_state():
            empty_config = self.viewmodel.get_empty_state_config()
            empty_dashboard = EmptyDashboard(
                self.actions_frame,
                on_create_project=self._handle_create_project,
                on_load_sample=self._handle_load_sample
            )
            empty_dashboard.pack(padx=20, pady=(10, 20), fill="both", expand=True)
            
            # Add tooltips to empty state buttons
            create_tooltip(
                empty_dashboard,
                "Getting Started: Create your first project or load sample data to begin "
                "exploring GeneStudio's bioinformatics capabilities"
            )
        else:
            # Show regular quick actions
            quick_actions = self.viewmodel.get_state('quick_actions', [])
            
            # Action tooltips mapping
            action_tooltips = {
                'create_project': TooltipTemplates.keyboard_shortcut(
                    'Create a new bioinformatics project to organize sequences and analyses',
                    'Ctrl+N'
                ),
                'import_fasta': TooltipTemplates.file_format(
                    'Import FASTA File',
                    '.fasta, .fa, .fas',
                    'Load DNA, RNA, or protein sequences from standard FASTA format files'
                ),
                'run_analysis': 'Execute bioinformatics algorithms on your sequences: '
                               'pattern matching, GC content, translation, and more',
                'view_reports': 'Access analysis results, generate reports, and export data '
                               'in multiple formats (PDF, Excel, CSV)'
            }
            
            for action in quick_actions:
                action_card = ActionCard(
                    self.actions_frame,
                    title=action['title'],
                    description=action['description'],
                    button_text=action['title'],
                    command=lambda a=action: self._handle_quick_action(a)
                )
                action_card.pack(padx=20, pady=10, fill="x")
                
                # Add tooltip to action card
                action_id = action.get('id', '')
                tooltip_text = action_tooltips.get(action_id, action.get('description', ''))
                create_tooltip(action_card, tooltip_text)
    
    def _handle_quick_action(self, action: dict):
        """Handle quick action button clicks."""
        action_id = action.get('id')
        if action_id:
            self.viewmodel.handle_quick_action(action_id)
            
            # Handle specific actions
            if action_id == 'create_project':
                self._handle_create_project()
            elif action_id == 'import_fasta':
                self._handle_import_fasta()
            elif action_id == 'run_analysis':
                self._handle_run_analysis()
            elif action_id == 'view_reports':
                self._handle_view_reports()
    
    def _handle_create_project(self):
        """Handle create project action."""
        # This would typically navigate to projects page or show create dialog
        show_success("Navigate to create project")
    
    def _handle_load_sample(self):
        """Handle load sample data action."""
        show_success("Loading sample data...")
    
    def _handle_import_fasta(self):
        """Handle import FASTA action."""
        show_success("Navigate to import FASTA")
    
    def _handle_run_analysis(self):
        """Handle run analysis action."""
        show_success("Navigate to analysis page")
    
    def _handle_view_reports(self):
        """Handle view reports action."""
        show_success("Navigate to reports page")
    
    def _add_action_tooltips(self):
        """Add tooltips to action buttons."""
        # This method would be called when action buttons are created
        # to add appropriate tooltips based on the action type
        pass
    
    def refresh_data(self):
        """Refresh dashboard data."""
        self.viewmodel.load_dashboard_data()
    
    def cleanup(self):
        """Cleanup resources when page is destroyed."""
        if hasattr(self, 'viewmodel'):
            self.viewmodel.cleanup()
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass
