"""
Enhanced professional main window for GeneStudio with matplotlib visualizations.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
from viewmodels.main_viewmodel import MainViewModel
from views.components.visualization_panel import VisualizationPanel, StatisticsPanel


class EnhancedMainWindow(ctk.CTk):
    """Enhanced professional main application window with advanced visualizations."""
    
    def __init__(self):
        """Initialize enhanced main window."""
        super().__init__()
        
        # Window configuration
        self.title("GeneStudio Pro - Advanced DNA Sequence Analysis")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Initialize ViewModel
        self.viewmodel = MainViewModel()
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._setup_ui()
        self._setup_menu()
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Left sidebar for controls
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        self._setup_sidebar()
        self._setup_main_content()
    
    def _setup_sidebar(self):
        """Setup the left sidebar with controls."""
        # Logo/Title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="GeneStudio Pro",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # File operations
        self._setup_file_section()
        
        # Analysis controls
        self._setup_analysis_section()
        
        # Statistics panel
        self.stats_panel = StatisticsPanel(self.sidebar)
        self.stats_panel.grid(row=4, column=0, sticky="nsew", padx=10, pady=10) 
   
    def _setup_file_section(self):
        """Setup file operations section."""
        file_frame = ctk.CTkFrame(self.sidebar)
        file_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        file_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            file_frame,
            text="File Operations",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, pady=(10, 5))
        
        # Load file button
        self.load_btn = ctk.CTkButton(
            file_frame,
            text="📁 Load FASTA File",
            command=self._load_file,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.load_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Sequence selector
        ctk.CTkLabel(file_frame, text="Select Sequence:").grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.sequence_var = ctk.StringVar(value="No sequences loaded")
        self.sequence_menu = ctk.CTkOptionMenu(
            file_frame,
            variable=self.sequence_var,
            values=["No sequences loaded"],
            command=self._on_sequence_selected
        )
        self.sequence_menu.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
    
    def _setup_analysis_section(self):
        """Setup analysis controls section."""
        analysis_frame = ctk.CTkFrame(self.sidebar)
        analysis_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        analysis_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            analysis_frame,
            text="Analysis Tools",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, pady=(10, 5))
        
        # Analysis buttons
        buttons = [
            ("🧬 Nucleotide Composition", self._show_composition),
            ("📊 GC Content Analysis", self._show_gc_analysis),
            ("🔍 Pattern Search", self._show_pattern_search),
            ("🧮 Suffix Array", self._show_suffix_array),
            ("🕸️ Overlap Graph", self._show_overlap_graph),
            ("🎯 Approximate Matching", self._show_approximate_matching)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(
                analysis_frame,
                text=text,
                command=command,
                height=35,
                font=ctk.CTkFont(size=12)
            )
            btn.grid(row=i+1, column=0, sticky="ew", padx=10, pady=2)
    
    def _setup_main_content(self):
        """Setup main content area."""
        # Top toolbar
        toolbar = ctk.CTkFrame(self.main_frame, height=60)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        toolbar.grid_columnconfigure(1, weight=1)
        
        # Current analysis label
        self.current_analysis_label = ctk.CTkLabel(
            toolbar,
            text="Welcome to GeneStudio Pro",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.current_analysis_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Export button
        self.export_btn = ctk.CTkButton(
            toolbar,
            text="💾 Export Results",
            command=self._export_results,
            width=150,
            height=35
        )
        self.export_btn.grid(row=0, column=2, padx=20, pady=15)
        
        # Main visualization area
        self.viz_panel = VisualizationPanel(self.main_frame)
        self.viz_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
    
    def _setup_menu(self):
        """Setup application menu bar using buttons."""
        # Menu bar frame
        menu_frame = ctk.CTkFrame(self, height=40, corner_radius=0)
        menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        menu_frame.grid_columnconfigure(3, weight=1)
        
        # Adjust main content to account for menu
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(0, 2))
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=(2, 0))
        self.grid_rowconfigure(1, weight=1)
        
        # Menu buttons
        file_btn = ctk.CTkButton(
            menu_frame,
            text="File",
            width=60,
            height=30,
            command=self._show_file_menu
        )
        file_btn.grid(row=0, column=0, padx=5, pady=5)
        
        tools_btn = ctk.CTkButton(
            menu_frame,
            text="Tools",
            width=60,
            height=30,
            command=self._show_tools_menu
        )
        tools_btn.grid(row=0, column=1, padx=5, pady=5)
        
        help_btn = ctk.CTkButton(
            menu_frame,
            text="Help",
            width=60,
            height=30,
            command=self._show_help_menu
        )
        help_btn.grid(row=0, column=2, padx=5, pady=5)
    
    def _show_file_menu(self):
        """Show file menu options."""
        from views.components.splash_screen import AboutDialog
        
        menu = ctk.CTkToplevel(self)
        menu.title("File Menu")
        menu.geometry("200x150")
        menu.transient(self)
        menu.grab_set()
        
        ctk.CTkButton(menu, text="Load FASTA File", command=lambda: [menu.destroy(), self._load_file()]).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(menu, text="Export Results", command=lambda: [menu.destroy(), self._export_results()]).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(menu, text="Exit", command=lambda: [menu.destroy(), self.quit()]).pack(pady=5, padx=10, fill="x")
    
    def _show_tools_menu(self):
        """Show tools menu options."""
        menu = ctk.CTkToplevel(self)
        menu.title("Tools Menu")
        menu.geometry("250x200")
        menu.transient(self)
        menu.grab_set()
        
        ctk.CTkButton(menu, text="Nucleotide Composition", command=lambda: [menu.destroy(), self._show_composition()]).pack(pady=3, padx=10, fill="x")
        ctk.CTkButton(menu, text="GC Content Analysis", command=lambda: [menu.destroy(), self._show_gc_analysis()]).pack(pady=3, padx=10, fill="x")
        ctk.CTkButton(menu, text="Pattern Search", command=lambda: [menu.destroy(), self._show_pattern_search()]).pack(pady=3, padx=10, fill="x")
        ctk.CTkButton(menu, text="Suffix Array", command=lambda: [menu.destroy(), self._show_suffix_array()]).pack(pady=3, padx=10, fill="x")
    
    def _show_help_menu(self):
        """Show help menu options."""
        from views.components.splash_screen import AboutDialog
        
        menu = ctk.CTkToplevel(self)
        menu.title("Help Menu")
        menu.geometry("200x120")
        menu.transient(self)
        menu.grab_set()
        
        ctk.CTkButton(menu, text="User Guide", command=lambda: [menu.destroy(), self._show_user_guide()]).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(menu, text="About", command=lambda: [menu.destroy(), AboutDialog(self)]).pack(pady=5, padx=10, fill="x")
    
    def _show_user_guide(self):
        """Show user guide."""
        try:
            import webbrowser
            import os
            
            guide_path = os.path.join(os.getcwd(), "USER_GUIDE.md")
            if os.path.exists(guide_path):
                webbrowser.open(f"file://{guide_path}")
            else:
                messagebox.showinfo("User Guide", "User guide not found. Please check the USER_GUIDE.md file.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open user guide: {str(e)}")  
  
    # Event handlers
    
    def _load_file(self):
        """Load FASTA file with enhanced error handling."""
        filepath = filedialog.askopenfilename(
            title="Select FASTA File",
            filetypes=[
                ("FASTA files", "*.fasta *.fa *.fas"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not filepath:
            return
        
        try:
            success, message = self.viewmodel.load_fasta_file(filepath)
            
            if success:
                # Update sequence selector
                seq_options = [
                    f"{i}: {seq.header[:50]}..." if len(seq.header) > 50 else f"{i}: {seq.header}"
                    for i, seq in enumerate(self.viewmodel.sequences)
                ]
                self.sequence_menu.configure(values=seq_options)
                if seq_options:
                    self.sequence_var.set(seq_options[0])
                    self._on_sequence_selected(seq_options[0])
                
                messagebox.showinfo("Success", f"Loaded {len(self.viewmodel.sequences)} sequences")
            else:
                messagebox.showerror("Error", f"Failed to load file: {message}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error loading file: {str(e)}")
    
    def _on_sequence_selected(self, choice):
        """Handle sequence selection with validation."""
        if not choice or choice == "No sequences loaded":
            return
        
        try:
            index = int(choice.split(":")[0])
            if 0 <= index < len(self.viewmodel.sequences):
                self.viewmodel.set_current_sequence(index)
                self._update_statistics()
                self._refresh_current_analysis()
        except (ValueError, IndexError) as e:
            messagebox.showerror("Error", f"Invalid sequence selection: {str(e)}")
    
    def _update_statistics(self):
        """Update statistics panel with current sequence."""
        seq = self.viewmodel.get_current_sequence()
        if seq:
            self.stats_panel.update_statistics(seq.sequence, seq.header)
    
    def _refresh_current_analysis(self):
        """Refresh the current analysis view."""
        # This will be called when sequence changes to update the current view
        pass
    
    def _show_composition(self):
        """Show nucleotide composition analysis."""
        seq = self.viewmodel.get_current_sequence()
        if not seq:
            messagebox.showwarning("Warning", "Please load a sequence first")
            return
        
        self.current_analysis_label.configure(text="Nucleotide Composition Analysis")
        self.viz_panel.plot_nucleotide_composition(
            seq.sequence, 
            f"Nucleotide Composition - {seq.header[:30]}..."
        )
    
    def _show_gc_analysis(self):
        """Show GC content analysis."""
        seq = self.viewmodel.get_current_sequence()
        if not seq:
            messagebox.showwarning("Warning", "Please load a sequence first")
            return
        
        self.current_analysis_label.configure(text="GC Content Analysis")
        
        # Determine appropriate window size
        window_size = min(max(len(seq.sequence) // 50, 10), 1000)
        
        self.viz_panel.plot_gc_content_window(
            seq.sequence,
            window_size,
            f"GC Content Analysis - {seq.header[:30]}..."
        )  
  
    def _show_pattern_search(self):
        """Show pattern search interface."""
        seq = self.viewmodel.get_current_sequence()
        if not seq:
            messagebox.showwarning("Warning", "Please load a sequence first")
            return
        
        # Create pattern input dialog
        dialog = PatternSearchDialog(self, seq.sequence)
        self.wait_window(dialog)
    
    def _show_suffix_array(self):
        """Show suffix array visualization."""
        seq = self.viewmodel.get_current_sequence()
        if not seq:
            messagebox.showwarning("Warning", "Please load a sequence first")
            return
        
        if len(seq.sequence) > 10000:
            result = messagebox.askyesno(
                "Large Sequence", 
                f"Sequence is {len(seq.sequence)} bp long. "
                "Suffix array visualization may be slow. Continue?"
            )
            if not result:
                return
        
        self.current_analysis_label.configure(text="Suffix Array Analysis")
        
        try:
            success, result = self.viewmodel.build_suffix_array()
            if success and isinstance(result, str) and "Suffix Array:" in result:
                # Parse suffix array from result string
                lines = result.split('\n')
                sa_line = next((line for line in lines if line.startswith("Suffix Array:")), None)
                if sa_line:
                    sa_str = sa_line.replace("Suffix Array: [", "").replace("]", "")
                    suffix_array = [int(x.strip()) for x in sa_str.split(',') if x.strip().isdigit()]
                    
                    self.viz_panel.plot_suffix_array_visualization(
                        suffix_array,
                        seq.sequence,
                        f"Suffix Array - {seq.header[:30]}..."
                    )
            else:
                messagebox.showerror("Error", "Failed to build suffix array")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error building suffix array: {str(e)}")
    
    def _show_overlap_graph(self):
        """Show overlap graph interface."""
        seq = self.viewmodel.get_current_sequence()
        if not seq:
            messagebox.showwarning("Warning", "Please load a sequence first")
            return
        
        # Create overlap graph dialog
        dialog = OverlapGraphDialog(self)
        self.wait_window(dialog)
    
    def _show_approximate_matching(self):
        """Show approximate matching interface."""
        seq = self.viewmodel.get_current_sequence()
        if not seq:
            messagebox.showwarning("Warning", "Please load a sequence first")
            return
        
        # Create approximate matching dialog
        dialog = ApproximateMatchDialog(self, seq.sequence)
        self.wait_window(dialog)
    
    def _export_results(self):
        """Export current analysis results."""
        # This will export the current visualization
        self.viz_panel._export_plot()


class PatternSearchDialog(ctk.CTkToplevel):
    """Dialog for pattern search operations."""
    
    def __init__(self, parent, sequence):
        super().__init__(parent)
        
        self.sequence = sequence
        self.parent = parent
        
        self.title("Pattern Search")
        self.geometry("500x300")
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        # Pattern input
        ctk.CTkLabel(self, text="Enter Pattern:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.pattern_entry = ctk.CTkEntry(self, width=300, placeholder_text="e.g., ATCG")
        self.pattern_entry.pack(pady=5)
        
        # Algorithm selection
        ctk.CTkLabel(self, text="Select Algorithm:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))
        
        self.algorithm_var = ctk.StringVar(value="Boyer-Moore (Bad Character)")
        algorithms = ["Boyer-Moore (Bad Character)", "Boyer-Moore (Good Suffix)"]
        
        for algo in algorithms:
            ctk.CTkRadioButton(self, text=algo, variable=self.algorithm_var, value=algo).pack(pady=2)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Search", command=self._search).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)
    
    def _search(self):
        """Perform pattern search."""
        pattern = self.pattern_entry.get().strip().upper()
        
        if not pattern:
            messagebox.showwarning("Warning", "Please enter a pattern")
            return
        
        if not all(c in 'ATCGN' for c in pattern):
            messagebox.showwarning("Warning", "Pattern must contain only valid nucleotides (A, T, C, G, N)")
            return
        
        try:
            algorithm = self.algorithm_var.get()
            
            if "Bad Character" in algorithm:
                success, result = self.parent.viewmodel.search_boyer_moore_bad_char(pattern)
            else:
                success, result = self.parent.viewmodel.search_boyer_moore_good_suffix(pattern)
            
            if success:
                # Parse matches from result
                matches = self._parse_matches(result)
                
                self.parent.current_analysis_label.configure(text=f"Pattern Search Results - {algorithm}")
                self.parent.viz_panel.plot_pattern_matches(
                    self.sequence,
                    matches,
                    pattern,
                    f"Pattern Matches: {pattern}"
                )
                
                self.destroy()
            else:
                messagebox.showerror("Error", f"Search failed: {result}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Search error: {str(e)}")
    
    def _parse_matches(self, result_text):
        """Parse match positions from result text."""
        matches = []
        lines = result_text.split('\n')
        
        for line in lines:
            if 'Position' in line and ':' in line:
                try:
                    pos_str = line.split(':')[0].replace('Position', '').strip()
                    if pos_str.isdigit():
                        matches.append(int(pos_str))
                except (ValueError, IndexError):
                    continue
        
        return matches


class OverlapGraphDialog(ctk.CTkToplevel):
    """Dialog for overlap graph operations."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        
        self.title("Overlap Graph Analysis")
        self.geometry("400x200")
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        ctk.CTkLabel(self, text="Minimum Overlap Length:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)
        
        self.overlap_entry = ctk.CTkEntry(self, width=100, placeholder_text="3")
        self.overlap_entry.pack(pady=5)
        self.overlap_entry.insert(0, "3")
        
        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=30)
        
        ctk.CTkButton(btn_frame, text="Build Graph", command=self._build_graph).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)
    
    def _build_graph(self):
        """Build overlap graph."""
        try:
            min_overlap = int(self.overlap_entry.get())
            
            if min_overlap < 1:
                messagebox.showwarning("Warning", "Minimum overlap must be at least 1")
                return
            
            success, result = self.parent.viewmodel.build_overlap_graph(min_overlap)
            
            if success:
                # Parse graph data for visualization
                graph_data = self._parse_graph_data(result)
                
                self.parent.current_analysis_label.configure(text="Overlap Graph Analysis")
                self.parent.viz_panel.plot_overlap_graph_stats(
                    graph_data,
                    f"Overlap Graph (min overlap: {min_overlap})"
                )
                
                self.destroy()
            else:
                messagebox.showerror("Error", f"Failed to build graph: {result}")
                
        except ValueError:
            messagebox.showerror("Error", "Minimum overlap must be a valid integer")
        except Exception as e:
            messagebox.showerror("Error", f"Graph building error: {str(e)}")
    
    def _parse_graph_data(self, result_text):
        """Parse graph data from result text."""
        graph_data = {}
        lines = result_text.split('\n')
        
        for line in lines:
            if '->' in line:
                try:
                    parts = line.split('->')
                    if len(parts) == 2:
                        node = parts[0].strip()
                        neighbors_str = parts[1].strip()
                        
                        if neighbors_str == '[]':
                            neighbors = []
                        else:
                            neighbors = [n.strip() for n in neighbors_str.replace('[', '').replace(']', '').split(',') if n.strip()]
                        
                        graph_data[node] = neighbors
                except Exception:
                    continue
        
        return graph_data


class ApproximateMatchDialog(ctk.CTkToplevel):
    """Dialog for approximate matching operations."""
    
    def __init__(self, parent, sequence):
        super().__init__(parent)
        
        self.sequence = sequence
        self.parent = parent
        
        self.title("Approximate Matching")
        self.geometry("500x350")
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        # Pattern input
        ctk.CTkLabel(self, text="Enter Pattern:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.pattern_entry = ctk.CTkEntry(self, width=300, placeholder_text="e.g., ATCG")
        self.pattern_entry.pack(pady=5)
        
        # Distance input
        ctk.CTkLabel(self, text="Maximum Distance:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))
        
        self.distance_entry = ctk.CTkEntry(self, width=100, placeholder_text="2")
        self.distance_entry.pack(pady=5)
        self.distance_entry.insert(0, "2")
        
        # Algorithm selection
        ctk.CTkLabel(self, text="Select Algorithm:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))
        
        self.algorithm_var = ctk.StringVar(value="Hamming Distance")
        algorithms = ["Hamming Distance", "Edit Distance"]
        
        for algo in algorithms:
            ctk.CTkRadioButton(self, text=algo, variable=self.algorithm_var, value=algo).pack(pady=2)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Search", command=self._search).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)
    
    def _search(self):
        """Perform approximate matching search."""
        pattern = self.pattern_entry.get().strip().upper()
        
        if not pattern:
            messagebox.showwarning("Warning", "Please enter a pattern")
            return
        
        if not all(c in 'ATCGN' for c in pattern):
            messagebox.showwarning("Warning", "Pattern must contain only valid nucleotides (A, T, C, G, N)")
            return
        
        try:
            max_distance = int(self.distance_entry.get())
            
            if max_distance < 0:
                messagebox.showwarning("Warning", "Maximum distance must be non-negative")
                return
            
            algorithm = self.algorithm_var.get()
            
            if algorithm == "Hamming Distance":
                success, result = self.parent.viewmodel.search_hamming(pattern, max_distance)
            else:
                success, result = self.parent.viewmodel.search_edit_distance(pattern, max_distance)
            
            if success:
                # Parse matches from result
                matches = self._parse_matches(result)
                
                self.parent.current_analysis_label.configure(text=f"Approximate Matching - {algorithm}")
                self.parent.viz_panel.plot_pattern_matches(
                    self.sequence,
                    matches,
                    pattern,
                    f"Approximate Matches: {pattern} (max dist: {max_distance})"
                )
                
                self.destroy()
            else:
                messagebox.showerror("Error", f"Search failed: {result}")
                
        except ValueError:
            messagebox.showerror("Error", "Maximum distance must be a valid integer")
        except Exception as e:
            messagebox.showerror("Error", f"Search error: {str(e)}")
    
    def _parse_matches(self, result_text):
        """Parse match positions from result text."""
        matches = []
        lines = result_text.split('\n')
        
        for line in lines:
            if 'Position' in line and ':' in line:
                try:
                    pos_str = line.split(':')[0].replace('Position', '').strip()
                    if pos_str.isdigit():
                        matches.append(int(pos_str))
                except (ValueError, IndexError):
                    continue
        
        return matches