"""Header component with breadcrumbs and actions."""

import customtkinter as ctk
from datetime import datetime
from typing import Optional, Callable
from viewmodels.search_viewmodel import SearchViewModel


class Header(ctk.CTkFrame):
    """Professional header bar with breadcrumbs and actions."""
    
    def __init__(self, parent, on_search_result: Optional[Callable] = None):
        """Initialize header."""
        super().__init__(parent, height=60, corner_radius=0)
        
        # Store callback
        self.on_search_result = on_search_result
        
        # Initialize search ViewModel
        self.search_viewmodel = SearchViewModel()
        self.search_viewmodel.add_observer(self._on_search_state_changed)
        
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
        
        # Search area
        search_container = ctk.CTkFrame(self, fg_color="transparent")
        search_container.grid(row=0, column=1, padx=20, pady=15, sticky="ew")
        search_container.grid_columnconfigure(0, weight=1)
        
        # Search frame with dropdown
        self.search_frame = ctk.CTkFrame(search_container, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, sticky="e")
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="🔍 Search sequences, projects, analyses...",
            width=350
        )
        self.search_entry.pack(side="left", padx=5)
        
        # Bind search events
        self.search_entry.bind("<KeyRelease>", self._on_search_input)
        self.search_entry.bind("<FocusIn>", self._on_search_focus)
        self.search_entry.bind("<FocusOut>", self._on_search_blur)
        self.search_entry.bind("<Return>", self._on_search_enter)
        
        # Category filter
        self.category_menu = ctk.CTkOptionMenu(
            self.search_frame,
            values=["All", "Projects", "Sequences", "Analyses"],
            width=100,
            command=self._on_category_changed
        )
        self.category_menu.pack(side="left", padx=5)
        
        # Search dropdown (initially hidden)
        self.search_dropdown = None
        
        # Action buttons
        action_frame = ctk.CTkFrame(search_container, fg_color="transparent")
        action_frame.grid(row=0, column=1, padx=(10, 0), sticky="e")
        
        # Notification button
        self.notif_btn = ctk.CTkButton(
            action_frame,
            text="🔔",
            width=40,
            command=self._show_notifications
        )
        self.notif_btn.pack(side="left", padx=5)
        
        # User profile button
        self.profile_btn = ctk.CTkButton(
            action_frame,
            text="👤 User",
            width=100,
            command=self._show_profile_menu
        )
        self.profile_btn.pack(side="left", padx=5)
        
    def update_breadcrumb(self, page_name: str):
        """Update breadcrumb text."""
        self.breadcrumb_label.configure(text=page_name)
    
    def _on_search_input(self, event):
        """Handle search input with debouncing."""
        query = self.search_entry.get()
        self.search_viewmodel.set_search_query(query)
    
    def _on_search_focus(self, event):
        """Handle search entry focus."""
        query = self.search_entry.get()
        if query.strip():
            self.search_viewmodel.show_search_dropdown(True)
    
    def _on_search_blur(self, event):
        """Handle search entry blur."""
        # Delay hiding dropdown to allow for clicks
        self.after(200, lambda: self.search_viewmodel.show_search_dropdown(False))
    
    def _on_search_enter(self, event):
        """Handle Enter key in search."""
        self.search_viewmodel.perform_immediate_search()
    
    def _on_category_changed(self, category: str):
        """Handle category filter change."""
        category_mapping = {
            "All": "all",
            "Projects": "projects", 
            "Sequences": "sequences",
            "Analyses": "analyses"
        }
        self.search_viewmodel.set_search_category(category_mapping.get(category, "all"))
    
    def _on_search_state_changed(self, state_key: str, state_value):
        """Handle search state changes."""
        if state_key == "show_search_dropdown":
            self._update_search_dropdown(state_value)
        elif state_key == "search_results":
            self._update_search_results(state_value)
        elif state_key == "search_suggestions":
            self._update_search_suggestions(state_value)
        elif state_key == "is_searching":
            self._update_search_loading(state_value)
    
    def _update_search_dropdown(self, show: bool):
        """Update search dropdown visibility."""
        if show and not self.search_dropdown:
            self._create_search_dropdown()
        elif not show and self.search_dropdown:
            self._hide_search_dropdown()
    
    def _create_search_dropdown(self):
        """Create search results dropdown."""
        if self.search_dropdown:
            return
        
        # Get search entry position
        entry_x = self.search_entry.winfo_x()
        entry_y = self.search_entry.winfo_y() + self.search_entry.winfo_height()
        entry_width = self.search_entry.winfo_width()
        
        # Create dropdown frame
        self.search_dropdown = ctk.CTkFrame(
            self.search_frame,
            width=entry_width + 100,
            height=300,
            corner_radius=8
        )
        self.search_dropdown.place(x=entry_x, y=entry_y + 5)
        
        # Create scrollable frame for results
        self.search_scroll = ctk.CTkScrollableFrame(
            self.search_dropdown,
            width=entry_width + 80,
            height=280
        )
        self.search_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Update with current results
        results = self.search_viewmodel.get_state("search_results", [])
        suggestions = self.search_viewmodel.get_state("search_suggestions", [])
        self._populate_dropdown(results, suggestions)
    
    def _hide_search_dropdown(self):
        """Hide search dropdown."""
        if self.search_dropdown:
            self.search_dropdown.destroy()
            self.search_dropdown = None
    
    def _populate_dropdown(self, results, suggestions):
        """Populate dropdown with results and suggestions."""
        if not self.search_dropdown:
            return
        
        # Clear existing content
        for widget in self.search_scroll.winfo_children():
            widget.destroy()
        
        # Add suggestions if no results
        if not results and suggestions:
            ctk.CTkLabel(
                self.search_scroll,
                text="Suggestions:",
                font=("Arial", 12, "bold"),
                anchor="w"
            ).pack(fill="x", pady=(0, 5))
            
            for suggestion in suggestions[:5]:
                suggestion_btn = ctk.CTkButton(
                    self.search_scroll,
                    text=suggestion,
                    anchor="w",
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray80", "gray25"),
                    command=lambda s=suggestion: self._select_suggestion(s)
                )
                suggestion_btn.pack(fill="x", pady=1)
        
        # Add search results
        if results:
            # Group by category
            categories = {}
            for result in results[:10]:  # Limit to 10 results
                if result.type not in categories:
                    categories[result.type] = []
                categories[result.type].append(result)
            
            for category, category_results in categories.items():
                # Category header
                ctk.CTkLabel(
                    self.search_scroll,
                    text=f"{category.title()} ({len(category_results)})",
                    font=("Arial", 12, "bold"),
                    anchor="w"
                ).pack(fill="x", pady=(10, 5))
                
                # Results
                for result in category_results[:3]:  # Limit per category
                    result_frame = ctk.CTkFrame(self.search_scroll, fg_color="transparent")
                    result_frame.pack(fill="x", pady=1)
                    
                    result_btn = ctk.CTkButton(
                        result_frame,
                        text=result.title,
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray25"),
                        command=lambda r=result: self._select_result(r)
                    )
                    result_btn.pack(side="left", fill="x", expand=True)
                    
                    # Score indicator
                    score_label = ctk.CTkLabel(
                        result_frame,
                        text=f"{result.relevance_score:.1f}",
                        width=40,
                        font=("Arial", 10)
                    )
                    score_label.pack(side="right", padx=(5, 0))
    
    def _select_suggestion(self, suggestion: str):
        """Select a search suggestion."""
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, suggestion)
        self.search_viewmodel.select_suggestion(suggestion)
        self._hide_search_dropdown()
    
    def _select_result(self, result):
        """Select a search result."""
        navigation_info = self.search_viewmodel.select_search_result(result)
        self._hide_search_dropdown()
        
        # Notify parent about navigation
        if self.on_search_result:
            self.on_search_result(navigation_info)
    
    def _update_search_results(self, results):
        """Update search results in dropdown."""
        if self.search_dropdown:
            suggestions = self.search_viewmodel.get_state("search_suggestions", [])
            self._populate_dropdown(results, suggestions)
    
    def _update_search_suggestions(self, suggestions):
        """Update search suggestions in dropdown."""
        if self.search_dropdown:
            results = self.search_viewmodel.get_state("search_results", [])
            self._populate_dropdown(results, suggestions)
    
    def _update_search_loading(self, is_loading: bool):
        """Update search loading state."""
        if is_loading:
            self.search_entry.configure(placeholder_text="🔍 Searching...")
        else:
            self.search_entry.configure(placeholder_text="🔍 Search sequences, projects, analyses...")
        
    def _show_notifications(self):
        """Show notifications panel."""
        # Placeholder for notifications
        pass
        
    def _show_profile_menu(self):
        """Show user profile menu."""
        # Placeholder for profile menu
        pass
