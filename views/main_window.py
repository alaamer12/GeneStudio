"""Main GUI window for GeneStudio using CustomTkinter."""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from viewmodels.main_viewmodel import MainViewModel


class MainWindow(ctk.CTk):
    """Main application window with tabbed interface."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        # Window configuration
        self.title("GeneStudio - DNA Sequence Analysis")
        self.geometry("1000x700")
        
        # Initialize ViewModel
        self.viewmodel = MainViewModel()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create tabbed interface
        self.tabview = ctk.CTkTabview(self, width=950, height=650)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Create tabs
        self.tab_file = self.tabview.add("File & Sequence")
        self.tab_basic = self.tabview.add("Basic Operations")
        self.tab_translation = self.tabview.add("Translation")
        self.tab_pattern = self.tabview.add("Pattern Matching")
        self.tab_suffix = self.tabview.add("Suffix Array")
        self.tab_graph = self.tabview.add("Overlap Graph")
        self.tab_approx = self.tabview.add("Approximate Matching")
        
        # Setup each tab
        self._setup_file_tab()
        self._setup_basic_operations_tab()
        self._setup_translation_tab()
        self._setup_pattern_matching_tab()
        self._setup_suffix_array_tab()
        self._setup_overlap_graph_tab()
        self._setup_approximate_matching_tab()
    
    def _setup_file_tab(self):
        """Setup file loading and sequence display tab."""
        # Load button
        load_btn = ctk.CTkButton(
            self.tab_file,
            text="Load FASTA File",
            command=self._load_file,
            width=200,
            height=40
        )
        load_btn.pack(pady=10)
        
        # Sequence selector
        selector_frame = ctk.CTkFrame(self.tab_file)
        selector_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(selector_frame, text="Select Sequence:").pack(side="left", padx=5)
        
        self.sequence_var = ctk.StringVar(value="No sequences loaded")
        self.sequence_menu = ctk.CTkOptionMenu(
            selector_frame,
            variable=self.sequence_var,
            values=["No sequences loaded"],
            command=self._on_sequence_selected,
            width=300
        )
        self.sequence_menu.pack(side="left", padx=5)
        
        # Sequence display
        ctk.CTkLabel(self.tab_file, text="Sequence:").pack(pady=(10, 5))
        
        self.sequence_text = ctk.CTkTextbox(self.tab_file, width=900, height=400)
        self.sequence_text.pack(pady=5, padx=20)
    
    def _setup_basic_operations_tab(self):
        """Setup basic operations tab."""
        # Buttons frame
        btn_frame = ctk.CTkFrame(self.tab_basic)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="GC Percentage",
            command=self._calc_gc,
            width=150
        ).grid(row=0, column=0, padx=10, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Reverse",
            command=self._get_reverse,
            width=150
        ).grid(row=0, column=1, padx=10, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Complement",
            command=self._get_complement,
            width=150
        ).grid(row=1, column=0, padx=10, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Reverse Complement",
            command=self._get_reverse_complement,
            width=150
        ).grid(row=1, column=1, padx=10, pady=5)
        
        # Result display
        ctk.CTkLabel(self.tab_basic, text="Result:").pack(pady=(10, 5))
        self.basic_result = ctk.CTkTextbox(self.tab_basic, width=900, height=400)
        self.basic_result.pack(pady=5, padx=20)
    
    def _setup_translation_tab(self):
        """Setup translation tab."""
        ctk.CTkButton(
            self.tab_translation,
            text="Translate to Amino Acids",
            command=self._translate,
            width=200,
            height=40
        ).pack(pady=20)
        
        ctk.CTkLabel(self.tab_translation, text="Amino Acid Sequence:").pack(pady=(10, 5))
        self.translation_result = ctk.CTkTextbox(self.tab_translation, width=900, height=400)
        self.translation_result.pack(pady=5, padx=20)
    
    def _setup_pattern_matching_tab(self):
        """Setup pattern matching tab."""
        # Input frame
        input_frame = ctk.CTkFrame(self.tab_pattern)
        input_frame.pack(pady=20, fill="x", padx=20)
        
        ctk.CTkLabel(input_frame, text="Pattern:").pack(side="left", padx=5)
        self.pattern_entry = ctk.CTkEntry(input_frame, width=300)
        self.pattern_entry.pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.tab_pattern)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Boyer-Moore (Bad Char)",
            command=self._search_bad_char,
            width=200
        ).grid(row=0, column=0, padx=10, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Boyer-Moore (Good Suffix)",
            command=self._search_good_suffix,
            width=200
        ).grid(row=0, column=1, padx=10, pady=5)
        
        # Result display
        ctk.CTkLabel(self.tab_pattern, text="Results:").pack(pady=(10, 5))
        self.pattern_result = ctk.CTkTextbox(self.tab_pattern, width=900, height=350)
        self.pattern_result.pack(pady=5, padx=20)
    
    def _setup_suffix_array_tab(self):
        """Setup suffix array tab."""
        ctk.CTkButton(
            self.tab_suffix,
            text="Build Suffix Array",
            command=self._build_suffix_array,
            width=200,
            height=40
        ).pack(pady=20)
        
        ctk.CTkLabel(self.tab_suffix, text="Suffix Array & Inverse:").pack(pady=(10, 5))
        self.suffix_result = ctk.CTkTextbox(self.tab_suffix, width=900, height=400)
        self.suffix_result.pack(pady=5, padx=20)
    
    def _setup_overlap_graph_tab(self):
        """Setup overlap graph tab."""
        # Input frame
        input_frame = ctk.CTkFrame(self.tab_graph)
        input_frame.pack(pady=20, fill="x", padx=20)
        
        ctk.CTkLabel(input_frame, text="Minimum Overlap:").pack(side="left", padx=5)
        self.overlap_entry = ctk.CTkEntry(input_frame, width=100)
        self.overlap_entry.insert(0, "3")
        self.overlap_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            input_frame,
            text="Build Graph",
            command=self._build_graph,
            width=150
        ).pack(side="left", padx=10)
        
        # Result display
        ctk.CTkLabel(self.tab_graph, text="Overlap Graph (Adjacency List):").pack(pady=(10, 5))
        self.graph_result = ctk.CTkTextbox(self.tab_graph, width=900, height=400)
        self.graph_result.pack(pady=5, padx=20)
    
    def _setup_approximate_matching_tab(self):
        """Setup approximate matching tab."""
        # Input frame
        input_frame = ctk.CTkFrame(self.tab_approx)
        input_frame.pack(pady=20, fill="x", padx=20)
        
        ctk.CTkLabel(input_frame, text="Pattern:").pack(side="left", padx=5)
        self.approx_pattern_entry = ctk.CTkEntry(input_frame, width=200)
        self.approx_pattern_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(input_frame, text="Max Distance:").pack(side="left", padx=5)
        self.distance_entry = ctk.CTkEntry(input_frame, width=80)
        self.distance_entry.insert(0, "2")
        self.distance_entry.pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.tab_approx)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Hamming Distance",
            command=self._search_hamming,
            width=180
        ).grid(row=0, column=0, padx=10, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Edit Distance",
            command=self._search_edit,
            width=180
        ).grid(row=0, column=1, padx=10, pady=5)
        
        # Result display
        ctk.CTkLabel(self.tab_approx, text="Results:").pack(pady=(10, 5))
        self.approx_result = ctk.CTkTextbox(self.tab_approx, width=900, height=350)
        self.approx_result.pack(pady=5, padx=20)
    
    # Event handlers
    
    def _load_file(self):
        """Load FASTA file."""
        filepath = filedialog.askopenfilename(
            title="Select FASTA File",
            filetypes=[("FASTA files", "*.fasta *.fa"), ("All files", "*.*")]
        )
        
        if filepath:
            success, message = self.viewmodel.load_fasta_file(filepath)
            
            if success:
                # Update sequence selector
                seq_options = [
                    f"{i}: {seq.header[:50]}" 
                    for i, seq in enumerate(self.viewmodel.sequences)
                ]
                self.sequence_menu.configure(values=seq_options)
                self.sequence_var.set(seq_options[0])
                self._update_sequence_display()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
    
    def _on_sequence_selected(self, choice):
        """Handle sequence selection."""
        if choice and choice != "No sequences loaded":
            index = int(choice.split(":")[0])
            self.viewmodel.set_current_sequence(index)
            self._update_sequence_display()
    
    def _update_sequence_display(self):
        """Update sequence display."""
        seq = self.viewmodel.get_current_sequence()
        if seq:
            self.sequence_text.delete("1.0", "end")
            self.sequence_text.insert("1.0", f"Header: {seq.header}\n")
            self.sequence_text.insert("end", f"Length: {seq.length} bp\n\n")
            self.sequence_text.insert("end", f"Sequence:\n{seq.sequence}")
    
    def _calc_gc(self):
        """Calculate GC percentage."""
        success, result = self.viewmodel.calculate_gc_percentage()
        self.basic_result.delete("1.0", "end")
        self.basic_result.insert("1.0", result)
    
    def _get_reverse(self):
        """Get reverse sequence."""
        success, result = self.viewmodel.get_reverse()
        self.basic_result.delete("1.0", "end")
        self.basic_result.insert("1.0", result)
    
    def _get_complement(self):
        """Get complement sequence."""
        success, result = self.viewmodel.get_complement()
        self.basic_result.delete("1.0", "end")
        self.basic_result.insert("1.0", result)
    
    def _get_reverse_complement(self):
        """Get reverse complement sequence."""
        success, result = self.viewmodel.get_reverse_complement()
        self.basic_result.delete("1.0", "end")
        self.basic_result.insert("1.0", result)
    
    def _translate(self):
        """Translate sequence."""
        success, result = self.viewmodel.translate_sequence()
        self.translation_result.delete("1.0", "end")
        self.translation_result.insert("1.0", result)
    
    def _search_bad_char(self):
        """Search using Boyer-Moore bad character."""
        pattern = self.pattern_entry.get()
        success, result = self.viewmodel.search_boyer_moore_bad_char(pattern)
        self.pattern_result.delete("1.0", "end")
        self.pattern_result.insert("1.0", result)
    
    def _search_good_suffix(self):
        """Search using Boyer-Moore good suffix."""
        pattern = self.pattern_entry.get()
        success, result = self.viewmodel.search_boyer_moore_good_suffix(pattern)
        self.pattern_result.delete("1.0", "end")
        self.pattern_result.insert("1.0", result)
    
    def _build_suffix_array(self):
        """Build suffix array."""
        success, result = self.viewmodel.build_suffix_array()
        self.suffix_result.delete("1.0", "end")
        self.suffix_result.insert("1.0", result)
    
    def _build_graph(self):
        """Build overlap graph."""
        try:
            min_overlap = int(self.overlap_entry.get())
            success, result = self.viewmodel.build_overlap_graph(min_overlap)
            self.graph_result.delete("1.0", "end")
            self.graph_result.insert("1.0", result)
            
            if not success:
                messagebox.showerror("Error", result)
        except ValueError:
            messagebox.showerror("Error", "Minimum overlap must be an integer")
    
    def _search_hamming(self):
        """Search using Hamming distance."""
        pattern = self.approx_pattern_entry.get()
        try:
            max_dist = int(self.distance_entry.get())
            success, result = self.viewmodel.search_hamming(pattern, max_dist)
            self.approx_result.delete("1.0", "end")
            self.approx_result.insert("1.0", result)
            
            if not success:
                messagebox.showerror("Error", result)
        except ValueError:
            messagebox.showerror("Error", "Max distance must be an integer")
    
    def _search_edit(self):
        """Search using edit distance."""
        pattern = self.approx_pattern_entry.get()
        try:
            max_dist = int(self.distance_entry.get())
            success, result = self.viewmodel.search_edit_distance(pattern, max_dist)
            self.approx_result.delete("1.0", "end")
            self.approx_result.insert("1.0", result)
            
            if not success:
                messagebox.showerror("Error", result)
        except ValueError:
            messagebox.showerror("Error", "Max distance must be an integer")
