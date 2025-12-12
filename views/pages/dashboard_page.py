"""Dashboard page - main landing page with real data binding."""

import customtkinter as ctk
from typing import Optional, Any
from views.components import (
    StatCard, ActionCard, InfoCard, PrimaryButton,
    SkeletonCard, EmptyDashboard, ErrorBoundary, with_error_boundary,
    show_success, show_error
)
from viewmodels.dashboard_viewmodel import DashboardViewModel


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
        
        ctk.CTkLabel(
            self.welcome_frame,
            text="Welcome to GeneStudio Pro",
            font=("Arial", 28, "bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            self.welcome_frame,
            text="Enterprise-grade DNA sequence analysis platform",
            font=("Arial", 14),
            text_color="gray"
        ).pack(anchor="w", pady=(5, 0))
    
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
        
        # Initially show loading states
        self._show_content_loading()
    
    def _show_stats_loading(self):
        """Show skeleton loading for stats cards."""
        for frame in self.stats_frames:
            # Clear frame
            for widget in frame.winfo_children():
                widget.destroy()
            
            # Add skeleton card
            skeleton = SkeletonCard(frame, width=200, height=120)
            skeleton.pack(fill="both", expand=True)
    
    def _show_content_loading(self):
        """Show loading states for content sections."""
        # Clear frames
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
        for widget in self.activity_frame.winfo_children():
            widget.destroy()
        
        # Actions loading
        ctk.CTkLabel(
            self.actions_frame,
            text="Quick Actions",
            font=("Arial", 16, "bold")
        ).pack(padx=20, pady=(20, 10), anchor="w")
        
        # Activity loading
        ctk.CTkLabel(
            self.activity_frame,
            text="Recent Activity",
            font=("Arial", 16, "bold")
        ).pack(padx=20, pady=(20, 10), anchor="w")
    
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
        
        # Define stat cards configuration
        stat_configs = [
            {
                'title': 'Total Sequences',
                'value': str(stats.get('total_sequences', 0)),
                'icon': '🧬'
            },
            {
                'title': 'Active Projects',
                'value': str(stats.get('active_projects', 0)),
                'icon': '📁'
            },
            {
                'title': 'Analyses Run',
                'value': str(stats.get('total_analyses', 0)),
                'icon': '🔬'
            },
            {
                'title': 'Completed Analyses',
                'value': str(stats.get('completed_analyses', 0)),
                'icon': '✅'
            }
        ]
        
        # Update each stat card
        for i, (frame, config) in enumerate(zip(self.stats_frames, stat_configs)):
            # Clear frame
            for widget in frame.winfo_children():
                widget.destroy()
            
            # Add real stat card
            StatCard(
                frame,
                title=config['title'],
                value=config['value'],
                icon=config['icon']
            ).pack(fill="both", expand=True)
    
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
            EmptyDashboard(
                self.actions_frame,
                on_create_project=self._handle_create_project,
                on_load_sample=self._handle_load_sample
            ).pack(padx=20, pady=(10, 20), fill="both", expand=True)
        else:
            # Show regular quick actions
            quick_actions = self.viewmodel.get_state('quick_actions', [])
            
            for action in quick_actions:
                ActionCard(
                    self.actions_frame,
                    title=action['title'],
                    description=action['description'],
                    button_text=action['title'],
                    command=lambda a=action: self._handle_quick_action(a)
                ).pack(padx=20, pady=10, fill="x")
    
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
