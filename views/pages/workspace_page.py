"""Workspace page - sequence editor and file management."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, IconButton


class WorkspacePage(ctk.CTkFrame):
    """Workspace with sequence editor and file manager."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Toolbar
        toolbar = ctk.CTkFrame(self, height=50)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        PrimaryButton(toolbar, text="📂 Open", width=100).pack(side="left", padx=5)
        PrimaryButton(toolbar, text="💾 Save", width=100).pack(side="left", padx=5)
        SecondaryButton(toolbar, text="📋 Copy", width=100).pack(side="left", padx=5)
        SecondaryButton(toolbar, text="✂️ Cut", width=100).pack(side="left", padx=5)
        SecondaryButton(toolbar, text="📌 Paste", width=100).pack(side="left", padx=5)
        
        # Separator
        ctk.CTkFrame(toolbar, width=2, fg_color="gray").pack(side="left", padx=10, fill="y")
        
        IconButton(toolbar, icon="🔍").pack(side="left", padx=5)
        IconButton(toolbar, icon="↩️").pack(side="left", padx=5)
        IconButton(toolbar, icon="↪️").pack(side="left", padx=5)
        
        # File browser sidebar
        file_browser = ctk.CTkFrame(self, width=250)
        file_browser.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        
        ctk.CTkLabel(
            file_browser,
            text="File Browser",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=15, anchor="w")
        
        # File tree (simplified)
        file_list = ctk.CTkTextbox(file_browser, width=230)
        file_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        file_list.insert("1.0", "📁 Projects\n")
        file_list.insert("end", "  📁 Project 1\n")
        file_list.insert("end", "    📄 sequence1.fasta\n")
        file_list.insert("end", "    📄 sequence2.fasta\n")
        file_list.insert("end", "  📁 Project 2\n")
        file_list.insert("end", "    📄 genome.fasta\n")
        file_list.configure(state="disabled")
        
        # Main editor area
        editor_frame = ctk.CTkFrame(self)
        editor_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        
        # Editor tabs
        tab_bar = ctk.CTkFrame(editor_frame, height=40)
        tab_bar.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            tab_bar,
            text="sequence1.fasta",
            fg_color=("gray75", "gray25"),
            width=150
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            tab_bar,
            text="➕",
            width=30,
            fg_color="transparent"
        ).pack(side="left", padx=2)
        
        # Sequence editor
        self.editor = ctk.CTkTextbox(editor_frame, font=("Courier", 11))
        self.editor.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Add sample sequence
        sample_seq = ">sample_sequence\nATGCGATCGATCGATCGATCGATCGATCGATCGATC\nGATCGATCGATCGATCGATCGATCGATCGATCGATC\nGATCGATCGATCGATCGATCGATCGATCGATCGATC"
        self.editor.insert("1.0", sample_seq)
        
        # Properties panel
        props_frame = ctk.CTkFrame(editor_frame)
        props_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        ctk.CTkLabel(
            props_frame,
            text="Length: 108 bp | GC%: 50.0% | Type: DNA",
            font=("Arial", 10)
        ).pack(padx=10, pady=10)
