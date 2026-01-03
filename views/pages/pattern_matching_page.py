"""Pattern matching page."""

import customtkinter as ctk
from typing import Optional
from views.components import PrimaryButton, DataTable
from views.components.loading_indicators import LinearProgress
from views.components.toast_notifications import show_success, show_error, show_info
from viewmodels.pattern_matching_viewmodel import PatternMatchingViewModel
from utils.themed_tooltips import (
    create_tooltip, create_validation_tooltip, create_info_button_tooltip,
    create_info_button_with_tooltip, TooltipTemplates, create_status_tooltip
)


class PatternMatchingPage(ctk.CTkFrame):
    """Pattern matching analysis page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Initialize ViewModel
        self.viewmodel = PatternMatchingViewModel()
        self.viewmodel.add_observer(self._on_viewmodel_state_changed)
        
        # UI References
        self.pattern_entry = None
        self.algorithm_menu = None
        self.case_sensitive_cb = None
        self.highlight_matches_cb = None
        self.show_statistics_cb = None
        self.search_button = None
        self.progress_bar = None
        self.results_table = None
        self.sequence_listbox = None
        self.project_menu = None
        
        self._create_ui()
        
        # Load initial data
        self._load_initial_data()
    
    def _create_ui(self):
        """Create the user interface."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        # Title with info button
        title_container = ctk.CTkFrame(header, fg_color="transparent")
        title_container.pack(side="left", fill="x", expand=True)
        
        title_label = ctk.CTkLabel(
            title_container,
            text="Pattern Matching",
            font=("Arial", 24, "bold")
        )
        title_label.pack(side="left")
        
        # Info button for pattern matching
        pattern_info_button, pattern_info_tooltip = create_info_button_with_tooltip(
            title_container,
            "Pattern Matching Algorithms\n\n"
            "Find occurrences of specific patterns in biological sequences:\n\n"
            "Available Algorithms:\n"
            "• Boyer-Moore (Bad Character): Skips characters not in pattern\n"
            "• Boyer-Moore (Good Suffix): Uses suffix information for skipping\n"
            "• Suffix Array: Pre-built index for fast searching\n"
            "• KMP (Knuth-Morris-Pratt): Uses failure function for efficiency\n"
            "• Naive: Simple brute-force approach for comparison\n\n"
            "Applications:\n"
            "• Finding restriction enzyme sites\n"
            "• Locating regulatory sequences\n"
            "• Identifying conserved motifs\n"
            "• Searching for known sequence patterns"
        )
        pattern_info_button.pack(side="left", padx=(10, 0))
        
        # Action buttons
        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.pack(side="right")
        
        self.compare_button = PrimaryButton(
            button_frame,
            text="⚖️ Compare",
            width=120,
            command=self._compare_algorithms
        )
        self.compare_button.pack(side="left", padx=(0, 10))
        
        self.search_button = PrimaryButton(
            button_frame,
            text="🔍 Search",
            width=120,
            command=self._execute_search
        )
        self.search_button.pack(side="left")
        
        # Add tooltips to buttons
        create_tooltip(
            self.search_button,
            TooltipTemplates.keyboard_shortcut(
                "Execute pattern search with selected algorithm and parameters",
                "Ctrl+Enter"
            )
        )
        
        create_tooltip(
            self.compare_button,
            "Compare Algorithm Performance\n\n"
            "Run the same pattern search with multiple algorithms to compare:\n"
            "• Execution time\n"
            "• Memory usage\n"
            "• Match accuracy\n\n"
            "Useful for selecting the best algorithm for your data."
        )
        
        # Configuration
        config_frame = ctk.CTkFrame(self)
        config_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Configuration header with info button
        config_header_container = ctk.CTkFrame(config_frame, fg_color="transparent")
        config_header_container.pack(padx=20, pady=(15, 10), anchor="w", fill="x")
        
        config_header_label = ctk.CTkLabel(
            config_header_container,
            text="Search Configuration",
            font=("Arial", 14, "bold")
        )
        config_header_label.pack(side="left", anchor="w")
        
        # Info button for search configuration
        config_info_button, config_info_tooltip = create_info_button_with_tooltip(
            config_header_container,
            "Search Configuration\n\n"
            "Configure pattern matching parameters:\n"
            "• Pattern: The sequence motif to search for\n"
            "• Algorithm: Choose search method based on your needs\n"
            "• Options: Customize search behavior and output\n\n"
            "Tips:\n"
            "• Use IUPAC nucleotide codes (A, T, G, C, N, R, Y, etc.)\n"
            "• Longer patterns generally search faster with Boyer-Moore\n"
            "• Case sensitivity affects exact matching requirements\n"
            "• Statistics show algorithm performance metrics"
        )
        config_info_button.pack(side="left", padx=(10, 0))
        
        # Project selection
        project_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        project_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            project_frame,
            text="Project:",
            width=100
        ).pack(side="left", padx=(0, 10))
        
        self.project_menu = ctk.CTkOptionMenu(
            project_frame,
            values=["Select Project..."],
            width=300,
            command=self._on_project_selected
        )
        self.project_menu.pack(side="left")
        
        # Pattern input
        pattern_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        pattern_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            pattern_frame,
            text="Pattern:",
            width=100
        ).pack(side="left", padx=(0, 10))
        
        self.pattern_entry = ctk.CTkEntry(
            pattern_frame,
            placeholder_text="Enter DNA pattern (e.g., ATCG)",
            width=300
        )
        self.pattern_entry.pack(side="left")
        self.pattern_entry.bind("<KeyRelease>", self._on_pattern_changed)
        
        # Add validation tooltip to pattern entry
        create_validation_tooltip(
            self.pattern_entry,
            TooltipTemplates.validation_format(
                "Search Pattern",
                "DNA/RNA sequence using IUPAC nucleotide codes",
                "ATCGATCG or ATNNNNTCG (N = any nucleotide)"
            ) + "\n\nIUPAC Codes:\n" +
            "A=Adenine, T=Thymine, G=Guanine, C=Cytosine\n" +
            "N=Any, R=A/G, Y=C/T, S=G/C, W=A/T, K=G/T, M=A/C"
        )
        
        # Algorithm selector
        algo_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        algo_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            algo_frame,
            text="Algorithm:",
            width=100
        ).pack(side="left", padx=(0, 10))
        
        self.algorithm_menu = ctk.CTkOptionMenu(
            algo_frame,
            values=["Select Algorithm..."],
            width=300,
            command=self._on_algorithm_selected
        )
        self.algorithm_menu.pack(side="left")
        
        # Add tooltip to algorithm selector
        create_tooltip(
            self.algorithm_menu,
            "Algorithm Selection\n\n"
            "Choose pattern matching algorithm:\n\n"
            "• Boyer-Moore (Bad Char): O(n/m) average, best for long patterns\n"
            "• Boyer-Moore (Good Suffix): O(n) worst case, uses suffix info\n"
            "• Suffix Array: O(m log n) after O(n log n) preprocessing\n"
            "• KMP: O(n+m) guaranteed, good for repetitive patterns\n"
            "• Naive: O(nm) brute force, simple but slow\n\n"
            "Recommendations:\n"
            "• Long patterns (>10 bp): Boyer-Moore\n"
            "• Short patterns (<5 bp): KMP or Naive\n"
            "• Multiple searches: Suffix Array\n"
            "• Educational purposes: Compare all algorithms"
        )
        
        # Options
        # Sequence selection
        sequence_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        sequence_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            sequence_frame,
            text="Sequences:",
            width=100
        ).pack(side="left", padx=(0, 10), anchor="n")
        
        sequence_container = ctk.CTkFrame(sequence_frame)
        sequence_container.pack(side="left", fill="x", expand=True)
        
        self.sequence_listbox = ctk.CTkScrollableFrame(sequence_container, height=100)
        self.sequence_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Options
        options_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        self.case_sensitive_cb = ctk.CTkCheckBox(
            options_frame, 
            text="Case sensitive",
            command=self._on_option_changed
        )
        self.case_sensitive_cb.pack(side="left", padx=10)
        
        self.highlight_matches_cb = ctk.CTkCheckBox(
            options_frame, 
            text="Highlight matches",
            command=self._on_option_changed
        )
        self.highlight_matches_cb.pack(side="left", padx=10)
        
        self.show_statistics_cb = ctk.CTkCheckBox(
            options_frame, 
            text="Show statistics",
            command=self._on_option_changed
        )
        self.show_statistics_cb.pack(side="left", padx=10)
        
        # Add tooltips to option checkboxes
        create_tooltip(
            self.case_sensitive_cb,
            "Case Sensitive Matching\n\n"
            "When enabled, pattern matching distinguishes between uppercase and lowercase letters.\n"
            "• Enabled: 'ATG' ≠ 'atg'\n"
            "• Disabled: 'ATG' = 'atg' = 'AtG'\n\n"
            "Note: Most biological sequences use uppercase by convention."
        )
        
        create_tooltip(
            self.highlight_matches_cb,
            "Highlight Matches\n\n"
            "Visually highlight found patterns in the sequence display.\n"
            "• Shows exact match positions with colored background\n"
            "• Useful for visualizing pattern distribution\n"
            "• May impact performance with many matches"
        )
        
        create_tooltip(
            self.show_statistics_cb,
            "Algorithm Performance Statistics\n\n"
            "Display detailed performance metrics:\n"
            "• Execution time (milliseconds)\n"
            "• Number of character comparisons\n"
            "• Memory usage\n"
            "• Preprocessing time (for applicable algorithms)\n\n"
            "Useful for comparing algorithm efficiency on your data."
        )
        
        # Results
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Results header with info button
        results_header_container = ctk.CTkFrame(results_frame, fg_color="transparent")
        results_header_container.pack(padx=20, pady=(15, 10), anchor="w", fill="x")
        
        results_header_label = ctk.CTkLabel(
            results_header_container,
            text="Search Results",
            font=("Arial", 14, "bold")
        )
        results_header_label.pack(side="left", anchor="w")
        
        # Info button for search results
        results_info_button, results_info_tooltip = create_info_button_with_tooltip(
            results_header_container,
            "Pattern Matching Results\n\n"
            "Displays all pattern occurrences found in sequences:\n\n"
            "Columns:\n"
            "• Position: 0-based index where pattern starts\n"
            "• Match: The actual matched sequence (may differ with IUPAC codes)\n"
            "• Context: Surrounding sequence for verification\n"
            "• Score: Match quality (100% for exact matches)\n\n"
            "Features:\n"
            "• Click column headers to sort results\n"
            "• Double-click rows to view detailed match information\n"
            "• Export results to CSV, Excel, or text formats\n"
            "• Performance statistics shown when enabled"
        )
        results_info_button.pack(side="left", padx=(10, 0))
        
        # Progress bar
        self.progress_bar = LinearProgress(results_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.pack_forget()  # Initially hidden
        
        # Results table
        self.results_table = DataTable(
            results_frame,
            columns=["Sequence", "Position", "Match", "Context", "Score"]
        )
        self.results_table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Add tooltip to results table
        create_status_tooltip(
            self.results_table,
            lambda: "Pattern Matching Results Table\n\n"
                    "Shows all matches found in the selected sequences. "
                    "Results are sorted by position by default. "
                    "Click column headers to sort by different criteria."
        )
        
        # Export frame
        export_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        export_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            export_frame,
            text="Export Results:",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=(0, 10))
        
        export_formats = ["CSV", "JSON", "TXT", "HTML"]
        for fmt in export_formats:
            export_btn = ctk.CTkButton(
                export_frame,
                text=fmt,
                width=60,
                command=lambda f=fmt: self._export_results(f)
            )
            export_btn.pack(side="left", padx=5)
    
    def _load_initial_data(self):
        """Load initial data for the page."""
        # Load available algorithms
        algorithms = self.viewmodel.get_state('available_algorithms', [])
        if algorithms:
            algorithm_names = [algo['name'] for algo in algorithms]
            self.algorithm_menu.configure(values=algorithm_names)
        
        # Load projects (placeholder - would need project service integration)
        # For now, just show placeholder
        self.project_menu.configure(values=["Sample Project", "Demo Project"])
    
    def _on_viewmodel_state_changed(self, state_key: str, state_value):
        """Handle ViewModel state changes."""
        if state_key == "selected_algorithm":
            self._update_algorithm_selection(state_value)
        elif state_key == "available_sequences":
            self._update_sequence_list(state_value)
        elif state_key == "search_results":
            self._update_results_table(state_value)
        elif state_key == "is_searching":
            self._update_search_state(state_value)
        elif state_key == "search_progress":
            self._update_progress(state_value)
        elif state_key == "performance_comparison":
            self._update_performance_display(state_value)
    
    def _on_project_selected(self, project_name: str):
        """Handle project selection."""
        # For demo purposes, use project ID 1
        # In real implementation, would map project name to ID
        if project_name != "Select Project...":
            self.viewmodel.set_current_project(1)
    
    def _on_algorithm_selected(self, algorithm_name: str):
        """Handle algorithm selection."""
        algorithms = self.viewmodel.get_state('available_algorithms', [])
        for algo in algorithms:
            if algo['name'] == algorithm_name:
                self.viewmodel.select_algorithm(algo['id'])
                break
    
    def _on_pattern_changed(self, event):
        """Handle pattern input changes."""
        pattern = self.pattern_entry.get()
        self.viewmodel.set_search_pattern(pattern)
    
    def _on_option_changed(self):
        """Handle option checkbox changes."""
        # Update ViewModel parameters based on checkboxes
        params = {}
        if hasattr(self, 'case_sensitive_cb'):
            params['case_sensitive'] = self.case_sensitive_cb.get()
        
        # Update other parameters as needed
        for param_name, value in params.items():
            self.viewmodel.set_algorithm_parameter(param_name, value)
    
    def _execute_search(self):
        """Execute pattern search."""
        # Get selected sequences
        selected_sequences = self._get_selected_sequences()
        if selected_sequences:
            self.viewmodel.select_sequences(selected_sequences)
        
        self.viewmodel.execute_pattern_search(compare_algorithms=False)
    
    def _compare_algorithms(self):
        """Execute algorithm comparison."""
        # Get selected sequences
        selected_sequences = self._get_selected_sequences()
        if selected_sequences:
            self.viewmodel.select_sequences(selected_sequences)
        
        self.viewmodel.execute_pattern_search(compare_algorithms=True)
    
    def _export_results(self, format_type: str):
        """Export results in specified format."""
        include_performance = self.show_statistics_cb.get() if hasattr(self, 'show_statistics_cb') else False
        self.viewmodel.export_results(format_type, include_performance)
    
    def _get_selected_sequences(self):
        """Get list of selected sequence IDs."""
        # For demo purposes, return [1, 2]
        # In real implementation, would get from sequence selection UI
        return [1, 2]
    
    def _update_algorithm_selection(self, algorithm):
        """Update UI based on algorithm selection."""
        if algorithm:
            self.algorithm_menu.set(algorithm['name'])
    
    def _update_sequence_list(self, sequences):
        """Update sequence selection list."""
        # Clear existing sequence widgets
        for widget in self.sequence_listbox.winfo_children():
            widget.destroy()
        
        # Add sequence checkboxes
        for sequence in sequences:
            cb = ctk.CTkCheckBox(
                self.sequence_listbox,
                text=f"{sequence.header} ({sequence.length} bp)"
            )
            cb.pack(anchor="w", pady=2)
    
    def _update_results_table(self, results):
        """Update results table with search results."""
        # Clear existing results
        self.results_table.clear()
        
        # Add new results
        for result in results:
            for match in result.get('matches', []):
                self.results_table.add_row([
                    result.get('sequence_header', 'Unknown'),
                    str(match.get('position', 0)),
                    match.get('match_text', ''),
                    match.get('context', ''),
                    f"{match.get('score', 0):.1f}%"
                ])
    
    def _update_search_state(self, is_searching: bool):
        """Update UI based on search state."""
        if is_searching:
            self.search_button.configure(text="⏹️ Cancel", command=self._cancel_search)
            self.compare_button.configure(state="disabled")
            self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
            self.progress_bar.start()
        else:
            self.search_button.configure(text="🔍 Search", command=self._execute_search)
            self.compare_button.configure(state="normal")
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
    
    def _update_progress(self, progress: float):
        """Update search progress."""
        # Progress bar is indeterminate for now
        pass
    
    def _update_performance_display(self, performance_data):
        """Update performance comparison display."""
        if performance_data:
            show_info(f"Algorithm comparison completed: {len(performance_data)} algorithms tested")
    
    def _cancel_search(self):
        """Cancel running search."""
        self.viewmodel.cancel_pattern_search()
