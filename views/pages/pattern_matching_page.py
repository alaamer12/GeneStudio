"""Pattern matching page."""

import customtkinter as ctk
from views.components import PrimaryButton, DataTable
from utils.themed_tooltips import (
    create_tooltip, create_validation_tooltip, create_info_button_tooltip,
    create_info_button_with_tooltip, TooltipTemplates, create_status_tooltip
)


class PatternMatchingPage(ctk.CTkFrame):
    """Pattern matching analysis page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
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
        
        search_button = PrimaryButton(
            header,
            text="🔍 Search",
            width=120
        )
        search_button.pack(side="right")
        
        # Add tooltip to search button
        create_tooltip(
            search_button,
            TooltipTemplates.keyboard_shortcut(
                "Execute pattern search with selected algorithm and parameters",
                "Ctrl+Enter"
            )
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
        
        # Pattern input
        pattern_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        pattern_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            pattern_frame,
            text="Pattern:",
            width=100
        ).pack(side="left", padx=(0, 10))
        
        pattern_entry = ctk.CTkEntry(
            pattern_frame,
            placeholder_text="Enter DNA pattern (e.g., ATCG)",
            width=300
        )
        pattern_entry.pack(side="left")
        
        # Add validation tooltip to pattern entry
        create_validation_tooltip(
            pattern_entry,
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
        
        algo_menu = ctk.CTkOptionMenu(
            algo_frame,
            values=["Boyer-Moore (Bad Char)", "Boyer-Moore (Good Suffix)", "Suffix Array", "KMP", "Naive"],
            width=300
        )
        algo_menu.pack(side="left")
        
        # Add tooltip to algorithm selector
        create_tooltip(
            algo_menu,
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
        options_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        case_sensitive_cb = ctk.CTkCheckBox(options_frame, text="Case sensitive")
        case_sensitive_cb.pack(side="left", padx=10)
        
        highlight_matches_cb = ctk.CTkCheckBox(options_frame, text="Highlight matches")
        highlight_matches_cb.pack(side="left", padx=10)
        
        show_statistics_cb = ctk.CTkCheckBox(options_frame, text="Show statistics")
        show_statistics_cb.pack(side="left", padx=10)
        
        # Add tooltips to option checkboxes
        create_tooltip(
            case_sensitive_cb,
            "Case Sensitive Matching\n\n"
            "When enabled, pattern matching distinguishes between uppercase and lowercase letters.\n"
            "• Enabled: 'ATG' ≠ 'atg'\n"
            "• Disabled: 'ATG' = 'atg' = 'AtG'\n\n"
            "Note: Most biological sequences use uppercase by convention."
        )
        
        create_tooltip(
            highlight_matches_cb,
            "Highlight Matches\n\n"
            "Visually highlight found patterns in the sequence display.\n"
            "• Shows exact match positions with colored background\n"
            "• Useful for visualizing pattern distribution\n"
            "• May impact performance with many matches"
        )
        
        create_tooltip(
            show_statistics_cb,
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
        
        self.results_table = DataTable(
            results_frame,
            columns=["Position", "Match", "Context", "Score"]
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
        
        # Add sample results
        self.results_table.add_row(["0", "ATCG", "...ATCGATCG...", "100%"])
        self.results_table.add_row(["10", "ATCG", "...ATCGATCG...", "100%"])
