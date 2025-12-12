"""Projects page with project management functionality and confirmation dialogs."""

import customtkinter as ctk
from typing import Optional, Any, List
from views.components import (
    PrimaryButton, SecondaryButton, DataTable, StatCard,
    EmptyProjects, SkeletonCard, DestructiveActionDialog, InputDialog,
    show_success, show_error, show_confirm_dialog, show_input_dialog
)
from viewmodels.project_viewmodel import ProjectViewModel
from utils.themed_tooltips import (
    create_tooltip, create_validation_tooltip, create_info_button_tooltip,
    create_info_button_with_tooltip, TooltipTemplates, create_status_tooltip
)


class ProjectsPage(ctk.CTkFrame):
    """Projects management page with real data binding."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Initialize ViewModel
        self.viewmodel = ProjectViewModel()
        self.viewmodel.add_observer(self._on_state_changed)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Create UI components
        self._create_header()
        self._create_toolbar()
        self._create_content_area()
        
        # Load initial data
        self.after(100, self._load_projects)
    
    def _create_header(self):
        """Create page header with title and actions."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title with info button
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.grid(row=0, column=0, sticky="w")
        
        title_label = ctk.CTkLabel(
            title_container,
            text="Project Management",
            font=("Arial", 24, "bold")
        )
        title_label.pack(side="left", anchor="w")
        
        # Info button for project management explanation
        info_button, info_tooltip = create_info_button_with_tooltip(
            title_container,
            "Project Management\n\n"
            "Projects organize your bioinformatics work:\n"
            "• Container for related sequences and analyses\n"
            "• Track progress with status indicators (Active, Archived, Completed)\n"
            "• Manage metadata like creation dates and descriptions\n"
            "• Bulk operations for efficient workflow management\n\n"
            "Project Types:\n"
            "• Sequence Analysis: General sequence processing\n"
            "• Genome Assembly: Large-scale genome projects\n"
            "• Comparative Analysis: Multi-sequence comparisons"
        )
        info_button.pack(side="left", padx=(10, 0))
        
        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=1, sticky="e")
        
        self.create_button = PrimaryButton(
            actions_frame,
            text="➕ Create Project",
            width=140,
            command=self._handle_create_project
        )
        self.create_button.pack(side="right", padx=5)
        
        self.import_button = SecondaryButton(
            actions_frame,
            text="📥 Import",
            width=100,
            command=self._handle_import_project
        )
        self.import_button.pack(side="right", padx=5)
        
        # Add tooltips to action buttons
        create_tooltip(
            self.create_button,
            TooltipTemplates.keyboard_shortcut(
                "Create a new bioinformatics project to organize sequences and analyses",
                "Ctrl+N"
            )
        )
        
        create_tooltip(
            self.import_button,
            "Import existing project data from backup files or other GeneStudio installations"
        )
    
    def _create_toolbar(self):
        """Create toolbar with search and filters."""
        toolbar_frame = ctk.CTkFrame(self)
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        toolbar_frame.grid_columnconfigure(0, weight=1)
        
        # Left side - search and filters
        left_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="ew")
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="🔍 Search projects...",
            width=300
        )
        self.search_entry.pack(side="left", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        
        # Status filter
        self.status_filter = ctk.CTkOptionMenu(
            left_frame,
            values=["All Status", "Active", "Archived", "Completed"],
            width=120,
            command=self._on_status_filter_changed
        )
        self.status_filter.pack(side="left", padx=5, pady=10)
        
        # Sort options
        self.sort_option = ctk.CTkOptionMenu(
            left_frame,
            values=["Modified Date", "Created Date", "Name", "Status"],
            width=120,
            command=self._on_sort_changed
        )
        self.sort_option.pack(side="left", padx=5, pady=10)
        
        # Add tooltips to search and filter controls
        create_validation_tooltip(
            self.search_entry,
            "Search projects by name or description. Search is case-insensitive and updates as you type."
        )
        
        create_tooltip(
            self.status_filter,
            TooltipTemplates.bioinformatics_term(
                "Project Status Filter",
                "Filter projects by their current status:",
                "• Active: Currently being worked on\n"
                "• Archived: Stored for reference, not actively used\n"
                "• Completed: Finished projects with final results"
            )
        )
        
        create_tooltip(
            self.sort_option,
            "Sort projects by different criteria:\n"
            "• Modified Date: Most recently changed first\n"
            "• Created Date: Newest projects first\n"
            "• Name: Alphabetical order\n"
            "• Status: Group by status (Active, Archived, Completed)"
        )
        
        # Right side - bulk actions
        right_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="e")
        
        self.delete_selected_button = SecondaryButton(
            right_frame,
            text="🗑️ Delete Selected",
            width=140,
            command=self._handle_delete_selected,
            fg_color="#d42f2f",
            hover_color="#b02525"
        )
        self.delete_selected_button.pack(side="right", padx=10, pady=10)
        
        self.archive_selected_button = SecondaryButton(
            right_frame,
            text="📦 Archive Selected",
            width=140,
            command=self._handle_archive_selected
        )
        self.archive_selected_button.pack(side="right", padx=5, pady=10)
        
        # Add tooltips to bulk action buttons
        create_tooltip(
            self.delete_selected_button,
            TooltipTemplates.disabled_reason(
                "Delete Selected Projects",
                "Permanently remove selected projects and all their data",
                "Select projects by clicking on them first. This action cannot be undone."
            )
        )
        
        create_tooltip(
            self.archive_selected_button,
            "Archive selected projects to remove them from active view while preserving all data. "
            "Archived projects can be restored later."
        )
    
    def _create_content_area(self):
        """Create main content area."""
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Initially show loading state
        self._show_loading_state()
    
    def _show_loading_state(self):
        """Show loading skeleton cards."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create grid of skeleton cards
        for i in range(6):  # Show 6 skeleton cards
            row = i // 3
            col = i % 3
            
            skeleton = SkeletonCard(self.content_frame, width=250, height=150)
            skeleton.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        for i in range(3):
            self.content_frame.grid_columnconfigure(i, weight=1)
    
    def _show_empty_state(self):
        """Show empty state when no projects exist."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Show empty projects state
        EmptyProjects(
            self.content_frame,
            on_create_project=self._handle_create_project,
            on_import_project=self._handle_import_project
        ).pack(fill="both", expand=True)
    
    def _show_projects_grid(self, projects: List):
        """Show projects in a grid layout."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if not projects:
            self._show_empty_state()
            return
        
        # Create scrollable frame for projects
        scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid
        for i in range(3):  # 3 columns
            scroll_frame.grid_columnconfigure(i, weight=1)
        
        # Create project cards
        for i, project in enumerate(projects):
            row = i // 3
            col = i % 3
            
            project_card = self._create_project_card(scroll_frame, project)
            project_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
    
    def _create_project_card(self, parent, project):
        """Create a project card widget."""
        card = ctk.CTkFrame(parent, corner_radius=8)
        
        # Configure grid
        card.grid_columnconfigure(0, weight=1)
        
        # Header with project name and status
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Project name
        name_label = ctk.CTkLabel(
            header_frame,
            text=project.name,
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="ew")
        
        # Status badge
        status_colors = {
            'active': '#2fa572',
            'archived': '#ffa500',
            'completed': '#1f6aa5'
        }
        status_color = status_colors.get(project.status, '#6b7280')
        
        status_label = ctk.CTkLabel(
            header_frame,
            text=project.status.title(),
            font=("Arial", 10, "bold"),
            fg_color=status_color,
            corner_radius=12,
            width=60,
            height=20
        )
        status_label.grid(row=0, column=1, sticky="e", padx=(10, 0))
        
        # Add status tooltip
        status_descriptions = {
            'active': 'Active project - currently being worked on with ongoing analyses',
            'archived': 'Archived project - stored for reference, not actively used',
            'completed': 'Completed project - finished with final results available'
        }
        create_status_tooltip(
            status_label,
            lambda: f"Status: {project.status.title()}\n\n{status_descriptions.get(project.status, 'Unknown status')}"
        )
        
        # Description
        if project.description:
            desc_label = ctk.CTkLabel(
                card,
                text=project.description[:100] + ("..." if len(project.description) > 100 else ""),
                font=("Arial", 10),
                text_color="gray",
                anchor="w",
                justify="left",
                wraplength=200
            )
            desc_label.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        # Stats
        stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        stats_text = f"📄 {project.sequence_count} sequences • 🔬 {project.analysis_count} analyses"
        stats_label = ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=("Arial", 9),
            text_color="gray"
        )
        stats_label.pack(anchor="w")
        
        # Dates
        dates_text = f"Created: {project.created_date.strftime('%Y-%m-%d')}"
        if project.modified_date != project.created_date:
            dates_text += f" • Modified: {project.modified_date.strftime('%Y-%m-%d')}"
        
        dates_label = ctk.CTkLabel(
            stats_frame,
            text=dates_text,
            font=("Arial", 8),
            text_color="gray"
        )
        dates_label.pack(anchor="w", pady=(2, 0))
        
        # Actions
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Open button
        open_button = PrimaryButton(
            actions_frame,
            text="Open",
            width=60,
            height=25,
            font=("Arial", 10),
            command=lambda p=project: self._handle_open_project(p)
        )
        open_button.pack(side="left")
        
        # More actions menu
        more_button = SecondaryButton(
            actions_frame,
            text="⋯",
            width=30,
            height=25,
            font=("Arial", 12),
            command=lambda p=project: self._show_project_menu(p)
        )
        more_button.pack(side="right")
        
        # Add tooltips to project action buttons
        create_tooltip(
            open_button,
            f"Open '{project.name}' project to view sequences, run analyses, and manage data"
        )
        
        create_tooltip(
            more_button,
            "More actions: Edit project details, duplicate, archive, or delete this project"
        )
        
        # Make card clickable for selection
        def on_card_click(event, proj=project):
            self._toggle_project_selection(proj.id)
        
        card.bind("<Button-1>", on_card_click)
        
        # Highlight if selected
        selected_projects = self.viewmodel.get_state('selected_projects', [])
        if project.id in selected_projects:
            card.configure(border_width=2, border_color="#3b82f6")
        
        return card
    
    def _load_projects(self):
        """Load projects through ViewModel."""
        self.viewmodel.load_projects()
    
    def _on_state_changed(self, key: Optional[str], value: Any):
        """Handle ViewModel state changes."""
        if key == 'projects':
            self._update_projects_display(value)
        elif key == 'loading_load_projects':
            if value:
                self._show_loading_state()
        elif key == 'selected_projects':
            self._update_selection_display()
        elif key == 'pending_deletion':
            if value:
                self._show_deletion_confirmation(value)
        elif key == 'pending_bulk_deletion':
            if value:
                self._show_bulk_deletion_confirmation(value)
        elif key == 'show_create_dialog':
            if value:
                self._show_create_project_dialog()
        elif key == 'show_edit_dialog':
            if value:
                self._show_edit_project_dialog()
    
    def _update_projects_display(self, projects: List):
        """Update the projects display."""
        if self.viewmodel.is_empty_state():
            self._show_empty_state()
        else:
            self._show_projects_grid(projects)
    
    def _update_selection_display(self):
        """Update visual selection indicators."""
        # This would update the visual selection state of project cards
        # For now, we'll trigger a refresh of the display
        projects = self.viewmodel.get_state('projects', [])
        if projects:
            self._show_projects_grid(projects)
    
    def _show_deletion_confirmation(self, project):
        """Show single project deletion confirmation."""
        DestructiveActionDialog(
            self,
            title="Delete Project",
            message="This action cannot be undone. All sequences and analyses in this project will be permanently deleted.",
            item_name=project.name,
            on_confirm=lambda: self.viewmodel.delete_project(project.id, confirmed=True)
        )
    
    def _show_bulk_deletion_confirmation(self, projects: List):
        """Show bulk deletion confirmation."""
        project_names = [p.name for p in projects[:3]]  # Show first 3 names
        if len(projects) > 3:
            project_names.append(f"and {len(projects) - 3} more")
        
        names_text = ", ".join(project_names)
        
        DestructiveActionDialog(
            self,
            title=f"Delete {len(projects)} Projects",
            message=f"This action cannot be undone. All data in these projects will be permanently deleted:\n\n{names_text}",
            confirm_text="Delete All",
            on_confirm=lambda: self.viewmodel.bulk_delete_projects(
                [p.id for p in projects], confirmed=True
            )
        )
    
    def _show_create_project_dialog(self):
        """Show create project dialog."""
        CreateProjectDialog(self, self.viewmodel)
    
    def _show_edit_project_dialog(self):
        """Show edit project dialog."""
        current_project = self.viewmodel.get_state('current_project')
        if current_project:
            EditProjectDialog(self, self.viewmodel, current_project)
    
    def _show_project_menu(self, project):
        """Show project context menu."""
        ProjectContextMenu(self, project, self.viewmodel)
    
    # Event handlers
    def _on_search_changed(self, event):
        """Handle search text changes."""
        search_term = self.search_entry.get()
        self.viewmodel.search_projects(search_term)
    
    def _on_status_filter_changed(self, value):
        """Handle status filter changes."""
        status_map = {
            "All Status": "all",
            "Active": "active",
            "Archived": "archived",
            "Completed": "completed"
        }
        status = status_map.get(value, "all")
        self.viewmodel.filter_by_status(status)
    
    def _on_sort_changed(self, value):
        """Handle sort option changes."""
        sort_map = {
            "Modified Date": "modified_date",
            "Created Date": "created_date",
            "Name": "name",
            "Status": "status"
        }
        sort_by = sort_map.get(value, "modified_date")
        self.viewmodel.sort_projects(sort_by)
    
    def _handle_create_project(self):
        """Handle create project action."""
        self.viewmodel.show_create_dialog()
    
    def _handle_import_project(self):
        """Handle import project action."""
        show_success("Import project functionality would be implemented here")
    
    def _handle_delete_selected(self):
        """Handle delete selected projects action."""
        selected_ids = self.viewmodel.get_state('selected_projects', [])
        if selected_ids:
            self.viewmodel.bulk_delete_projects(selected_ids)
        else:
            show_error("No projects selected")
    
    def _handle_archive_selected(self):
        """Handle archive selected projects action."""
        selected_ids = self.viewmodel.get_state('selected_projects', [])
        if selected_ids:
            for project_id in selected_ids:
                self.viewmodel.archive_project(project_id)
        else:
            show_error("No projects selected")
    
    def _handle_open_project(self, project):
        """Handle open project action."""
        self.viewmodel.select_project(project.id)
        show_success(f"Opening project: {project.name}")
        # This would typically navigate to the workspace or project details
    
    def _toggle_project_selection(self, project_id: int):
        """Toggle project selection."""
        self.viewmodel.toggle_project_selection(project_id)
    
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


class CreateProjectDialog(ctk.CTkToplevel):
    """Dialog for creating new projects."""
    
    def __init__(self, parent, viewmodel: ProjectViewModel):
        super().__init__(parent)
        
        self.viewmodel = viewmodel
        
        # Configure dialog
        self.title("Create New Project")
        self.geometry("500x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center dialog
        self.after(10, self._center_dialog)
        
        # Create content
        self._create_content()
    
    def _center_dialog(self):
        """Center dialog on parent."""
        self.update_idletasks()
        
        parent = self.master
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_content(self):
        """Create dialog content."""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Create New Project",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Form fields
        # Project name
        name_label = ctk.CTkLabel(main_frame, text="Project Name *", anchor="w")
        name_label.pack(fill="x", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter project name",
            height=35
        )
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        # Project type
        type_label = ctk.CTkLabel(main_frame, text="Project Type", anchor="w")
        type_label.pack(fill="x", pady=(0, 5))
        
        self.type_option = ctk.CTkOptionMenu(
            main_frame,
            values=["Sequence Analysis", "Genome Assembly", "Comparative Analysis"],
            height=35
        )
        self.type_option.pack(fill="x", pady=(0, 15))
        
        # Description
        desc_label = ctk.CTkLabel(main_frame, text="Description", anchor="w")
        desc_label.pack(fill="x", pady=(0, 5))
        
        self.desc_text = ctk.CTkTextbox(main_frame, height=100)
        self.desc_text.pack(fill="x", pady=(0, 20))
        
        # Add tooltips to form fields
        create_validation_tooltip(
            self.name_entry,
            TooltipTemplates.validation_format(
                "Project Name",
                "Unique identifier for your project (required)",
                "My DNA Analysis Project"
            )
        )
        
        create_tooltip(
            self.type_option,
            TooltipTemplates.bioinformatics_term(
                "Project Types",
                "Choose the type that best matches your research:",
                "• Sequence Analysis: General sequence processing and analysis\n"
                "• Genome Assembly: Large-scale genome reconstruction projects\n"
                "• Comparative Analysis: Multi-sequence comparison studies"
            )
        )
        
        create_validation_tooltip(
            self.desc_text,
            "Optional description of your project goals, methods, or notes. "
            "This helps organize your work and provides context for collaborators."
        )
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        cancel_button = SecondaryButton(
            buttons_frame,
            text="Cancel",
            width=100,
            command=self._handle_cancel
        )
        cancel_button.pack(side="right", padx=(10, 0))
        
        create_button = PrimaryButton(
            buttons_frame,
            text="Create Project",
            width=120,
            command=self._handle_create
        )
        create_button.pack(side="right")
        
        # Add tooltips to dialog buttons
        create_tooltip(cancel_button, "Cancel project creation and close dialog (Esc)")
        create_tooltip(create_button, "Create new project with the specified settings (Enter)")
        
        # Focus name entry
        self.after(100, lambda: self.name_entry.focus_set())
    
    def _handle_create(self):
        """Handle create button click."""
        # Get form data
        name = self.name_entry.get().strip()
        project_type = self.type_option.get().lower().replace(" ", "_")
        description = self.desc_text.get("1.0", "end-1c").strip()
        
        # Validate
        if not name:
            show_error("Project name is required")
            self.name_entry.focus_set()
            return
        
        # Create project data
        project_data = {
            'name': name,
            'type': project_type,
            'description': description
        }
        
        # Create project through ViewModel
        self.viewmodel.create_project(project_data)
        
        # Close dialog
        self._close_dialog()
    
    def _handle_cancel(self):
        """Handle cancel button click."""
        self.viewmodel.hide_create_dialog()
        self._close_dialog()
    
    def _close_dialog(self):
        """Close the dialog."""
        self.grab_release()
        self.destroy()


class EditProjectDialog(CreateProjectDialog):
    """Dialog for editing existing projects."""
    
    def __init__(self, parent, viewmodel: ProjectViewModel, project):
        self.project = project
        super().__init__(parent, viewmodel)
        
        # Update dialog for editing
        self.title("Edit Project")
        
        # Pre-fill form with project data
        self.name_entry.insert(0, project.name)
        self.type_option.set(project.type.replace("_", " ").title())
        if project.description:
            self.desc_text.insert("1.0", project.description)
    
    def _handle_create(self):
        """Handle update button click."""
        # Get form data
        name = self.name_entry.get().strip()
        project_type = self.type_option.get().lower().replace(" ", "_")
        description = self.desc_text.get("1.0", "end-1c").strip()
        
        # Validate
        if not name:
            show_error("Project name is required")
            self.name_entry.focus_set()
            return
        
        # Update project
        self.project.name = name
        self.project.type = project_type
        self.project.description = description
        
        # Update through ViewModel
        self.viewmodel.update_project(self.project)
        
        # Close dialog
        self._close_dialog()


class ProjectContextMenu(ctk.CTkToplevel):
    """Context menu for project actions."""
    
    def __init__(self, parent, project, viewmodel: ProjectViewModel):
        super().__init__(parent)
        
        self.project = project
        self.viewmodel = viewmodel
        
        # Configure as popup menu
        self.overrideredirect(True)
        self.configure(fg_color=("gray90", "gray20"))
        
        # Position near cursor
        x = parent.winfo_pointerx()
        y = parent.winfo_pointery()
        self.geometry(f"150x200+{x}+{y}")
        
        # Create menu items
        self._create_menu_items()
        
        # Auto-close on focus loss
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.focus_set()
    
    def _create_menu_items(self):
        """Create context menu items."""
        # Open
        open_btn = ctk.CTkButton(
            self,
            text="📂 Open",
            command=self._handle_open,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            anchor="w",
            height=30
        )
        open_btn.pack(fill="x", padx=5, pady=2)
        
        # Edit
        edit_btn = ctk.CTkButton(
            self,
            text="✏️ Edit",
            command=self._handle_edit,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            anchor="w",
            height=30
        )
        edit_btn.pack(fill="x", padx=5, pady=2)
        
        # Duplicate
        duplicate_btn = ctk.CTkButton(
            self,
            text="📋 Duplicate",
            command=self._handle_duplicate,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            anchor="w",
            height=30
        )
        duplicate_btn.pack(fill="x", padx=5, pady=2)
        
        # Archive/Restore
        if self.project.status == 'archived':
            archive_btn = ctk.CTkButton(
                self,
                text="📤 Restore",
                command=self._handle_restore,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                anchor="w",
                height=30
            )
        else:
            archive_btn = ctk.CTkButton(
                self,
                text="📦 Archive",
                command=self._handle_archive,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                anchor="w",
                height=30
            )
        archive_btn.pack(fill="x", padx=5, pady=2)
        
        # Separator
        separator = ctk.CTkFrame(self, height=1, fg_color="gray")
        separator.pack(fill="x", padx=5, pady=5)
        
        # Delete
        delete_btn = ctk.CTkButton(
            self,
            text="🗑️ Delete",
            command=self._handle_delete,
            fg_color="transparent",
            text_color="#d42f2f",
            hover_color="#b02525",
            anchor="w",
            height=30
        )
        delete_btn.pack(fill="x", padx=5, pady=2)
    
    def _handle_open(self):
        """Handle open action."""
        self.viewmodel.select_project(self.project.id)
        show_success(f"Opening project: {self.project.name}")
        self.destroy()
    
    def _handle_edit(self):
        """Handle edit action."""
        self.viewmodel.show_edit_dialog(self.project.id)
        self.destroy()
    
    def _handle_duplicate(self):
        """Handle duplicate action."""
        new_name = show_input_dialog(
            self,
            title="Duplicate Project",
            message="Enter name for the duplicated project:",
            default_value=f"{self.project.name} (Copy)"
        )
        
        if new_name:
            self.viewmodel.duplicate_project(self.project.id, new_name)
        
        self.destroy()
    
    def _handle_archive(self):
        """Handle archive action."""
        self.viewmodel.archive_project(self.project.id)
        self.destroy()
    
    def _handle_restore(self):
        """Handle restore action."""
        self.viewmodel.restore_project(self.project.id)
        self.destroy()
    
    def _handle_delete(self):
        """Handle delete action."""
        self.viewmodel.delete_project(self.project.id)
        self.destroy()