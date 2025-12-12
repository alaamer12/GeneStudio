"""Workspace page - sequence editor and file management with real data binding."""

import customtkinter as ctk
from typing import Optional, Any, List
from pathlib import Path
import tkinter as tk
from views.components import (
    PrimaryButton, SecondaryButton, IconButton, DataTable,
    EmptyWorkspace, SkeletonText, LinearProgress, 
    show_success, show_error, show_confirm_dialog, SaveChangesDialog
)
from viewmodels.workspace_viewmodel import WorkspaceViewModel


class WorkspacePage(ctk.CTkFrame):
    """Workspace with real sequence editor and file management."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Initialize ViewModel
        self.viewmodel = WorkspaceViewModel()
        self.viewmodel.add_observer(self._on_state_changed)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI components
        self._create_toolbar()
        self._create_main_content()
        
        # Load initial data
        self.after(100, self._initialize_workspace)
    
    def _create_toolbar(self):
        """Create toolbar with file operations."""
        self.toolbar = ctk.CTkFrame(self, height=50)
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # File operations
        self.open_button = PrimaryButton(
            self.toolbar, 
            text="📂 Open", 
            width=100,
            command=self._handle_open_file
        )
        self.open_button.pack(side="left", padx=5)
        
        self.save_button = PrimaryButton(
            self.toolbar, 
            text="💾 Save", 
            width=100,
            command=self._handle_save_file
        )
        self.save_button.pack(side="left", padx=5)
        
        self.new_button = SecondaryButton(
            self.toolbar, 
            text="📄 New", 
            width=100,
            command=self._handle_new_sequence
        )
        self.new_button.pack(side="left", padx=5)
        
        # Edit operations
        SecondaryButton(
            self.toolbar, 
            text="📋 Copy", 
            width=100,
            command=self._handle_copy
        ).pack(side="left", padx=5)
        
        SecondaryButton(
            self.toolbar, 
            text="✂️ Cut", 
            width=100,
            command=self._handle_cut
        ).pack(side="left", padx=5)
        
        SecondaryButton(
            self.toolbar, 
            text="📌 Paste", 
            width=100,
            command=self._handle_paste
        ).pack(side="left", padx=5)
        
        # Separator
        ctk.CTkFrame(self.toolbar, width=2, fg_color="gray").pack(side="left", padx=10, fill="y")
        
        # Tools
        IconButton(self.toolbar, icon="🔍", command=self._handle_search).pack(side="left", padx=5)
        IconButton(self.toolbar, icon="↩️", command=self._handle_undo).pack(side="left", padx=5)
        IconButton(self.toolbar, icon="↪️", command=self._handle_redo).pack(side="left", padx=5)
        
        # Status info
        self.status_label = ctk.CTkLabel(
            self.toolbar,
            text="Ready",
            font=("Arial", 10),
            text_color="gray"
        )
        self.status_label.pack(side="right", padx=10)
    
    def _create_main_content(self):
        """Create main content area with file browser and editor."""
        # File browser sidebar
        self.file_browser = ctk.CTkFrame(self, width=250)
        self.file_browser.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        
        # Browser header
        browser_header = ctk.CTkFrame(self.file_browser, height=40)
        browser_header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            browser_header,
            text="File Browser",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=15, pady=10)
        
        # Import button
        import_button = IconButton(
            browser_header,
            icon="📥",
            command=self._handle_import_fasta
        )
        import_button.pack(side="right", padx=10)
        
        # Path navigation
        self.path_frame = ctk.CTkFrame(self.file_browser)
        self.path_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        self.path_label = ctk.CTkLabel(
            self.path_frame,
            text="",
            font=("Arial", 10),
            anchor="w"
        )
        self.path_label.pack(fill="x", padx=10, pady=5)
        
        # File list
        self.file_list_frame = ctk.CTkFrame(self.file_browser)
        self.file_list_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Main editor area
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        
        # Initially show empty state
        self._show_empty_state()
    
    def _initialize_workspace(self):
        """Initialize workspace with default file browser path."""
        self.viewmodel.browse_files()
    
    def _on_state_changed(self, key: Optional[str], value: Any):
        """Handle ViewModel state changes."""
        if key == 'file_browser_path':
            self._update_path_display(value)
        elif key == 'file_browser_files':
            self._update_file_list(value)
        elif key == 'current_sequence':
            self._update_editor_content()
        elif key == 'sequence_content':
            self._update_sequence_display()
        elif key == 'sequence_header':
            self._update_header_display()
        elif key == 'is_editing':
            self._update_editor_mode(value)
        elif key == 'has_unsaved_changes':
            self._update_save_button_state(value)
        elif key == 'loading':
            self._update_loading_state(value)
        elif key == 'show_save_dialog':
            if value:
                self._show_save_changes_dialog()
    
    def _update_path_display(self, path: str):
        """Update the current path display."""
        # Truncate long paths
        display_path = path
        if len(display_path) > 40:
            display_path = "..." + display_path[-37:]
        
        self.path_label.configure(text=display_path)
    
    def _update_file_list(self, files: List[dict]):
        """Update the file browser list."""
        # Clear current file list
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        
        if not files:
            # Show empty file browser
            empty_label = ctk.CTkLabel(
                self.file_list_frame,
                text="No files found",
                text_color="gray"
            )
            empty_label.pack(expand=True)
            return
        
        # Create scrollable file list
        file_scroll = ctk.CTkScrollableFrame(self.file_list_frame)
        file_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        for file_info in files:
            self._create_file_item(file_scroll, file_info)
    
    def _create_file_item(self, parent, file_info: dict):
        """Create a file item in the browser."""
        item_frame = ctk.CTkFrame(parent, height=30)
        item_frame.pack(fill="x", pady=1)
        item_frame.pack_propagate(False)
        
        # Configure grid
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        if file_info['type'] == 'directory':
            icon = "📁" if not file_info.get('is_parent') else "⬆️"
        elif file_info.get('is_fasta'):
            icon = "🧬"
        else:
            icon = "📄"
        
        icon_label = ctk.CTkLabel(
            item_frame,
            text=icon,
            font=("Arial", 12),
            width=20
        )
        icon_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
        
        # Name
        name_label = ctk.CTkLabel(
            item_frame,
            text=file_info['name'],
            font=("Arial", 10),
            anchor="w"
        )
        name_label.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ew")
        
        # Make clickable
        def on_click(event, file_path=file_info['path'], file_type=file_info['type']):
            if file_type == 'directory':
                self.viewmodel.browse_files(file_path)
            else:
                self.viewmodel.select_file(file_path)
        
        def on_double_click(event, file_path=file_info['path'], file_type=file_info['type']):
            if file_type == 'file' and file_info.get('is_fasta'):
                self._handle_import_single_file(file_path)
        
        item_frame.bind("<Button-1>", on_click)
        item_frame.bind("<Double-Button-1>", on_double_click)
        item_frame.configure(cursor="hand2")
        
        # Highlight selected files
        selected_files = self.viewmodel.get_state('selected_files', [])
        if file_info['path'] in selected_files:
            item_frame.configure(fg_color=("#3b82f6", "#1e40af"))
    
    def _update_editor_content(self):
        """Update editor with current sequence."""
        current_sequence = self.viewmodel.get_state('current_sequence')
        
        if current_sequence is None:
            self._show_empty_state()
        else:
            self._show_editor()
    
    def _show_empty_state(self):
        """Show empty state in editor area."""
        # Clear editor frame
        for widget in self.editor_frame.winfo_children():
            widget.destroy()
        
        # Show empty workspace
        EmptyWorkspace(
            self.editor_frame,
            on_open_file=self._handle_open_file,
            on_create_file=self._handle_new_sequence
        ).pack(fill="both", expand=True)
    
    def _show_editor(self):
        """Show sequence editor interface."""
        # Clear editor frame
        for widget in self.editor_frame.winfo_children():
            widget.destroy()
        
        # Header with sequence info
        self._create_editor_header()
        
        # Editor content
        self._create_editor_content()
        
        # Properties panel
        self._create_properties_panel()
    
    def _create_editor_header(self):
        """Create editor header with sequence info."""
        header_frame = ctk.CTkFrame(self.editor_frame, height=40)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        # Sequence name/header
        current_sequence = self.viewmodel.get_state('current_sequence')
        sequence_header = self.viewmodel.get_state('sequence_header', '')
        
        if self.viewmodel.get_state('is_editing', False):
            # Editable header
            self.header_entry = ctk.CTkEntry(
                header_frame,
                font=("Arial", 12, "bold"),
                placeholder_text="Sequence header"
            )
            self.header_entry.pack(side="left", fill="x", expand=True, padx=10, pady=5)
            self.header_entry.insert(0, sequence_header)
            self.header_entry.bind("<KeyRelease>", self._on_header_changed)
        else:
            # Read-only header
            header_label = ctk.CTkLabel(
                header_frame,
                text=sequence_header or "Untitled Sequence",
                font=("Arial", 12, "bold"),
                anchor="w"
            )
            header_label.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        # Edit/Save buttons
        if self.viewmodel.get_state('is_editing', False):
            # Save and Cancel buttons
            save_btn = PrimaryButton(
                header_frame,
                text="💾 Save",
                width=80,
                command=self._handle_save_sequence
            )
            save_btn.pack(side="right", padx=5)
            
            cancel_btn = SecondaryButton(
                header_frame,
                text="❌ Cancel",
                width=80,
                command=self._handle_cancel_editing
            )
            cancel_btn.pack(side="right", padx=5)
        else:
            # Edit button
            edit_btn = SecondaryButton(
                header_frame,
                text="✏️ Edit",
                width=80,
                command=self._handle_edit_sequence
            )
            edit_btn.pack(side="right", padx=5)
    
    def _create_editor_content(self):
        """Create main editor content area."""
        # Editor with sequence content
        is_editing = self.viewmodel.get_state('is_editing', False)
        sequence_content = self.viewmodel.get_state('sequence_content', '')
        
        self.editor = ctk.CTkTextbox(
            self.editor_frame,
            font=("Courier", 11),
            wrap="char"
        )
        self.editor.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Set content
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", sequence_content)
        
        # Configure state
        if is_editing:
            self.editor.configure(state="normal")
            self.editor.bind("<KeyRelease>", self._on_content_changed)
        else:
            self.editor.configure(state="disabled")
    
    def _create_properties_panel(self):
        """Create properties panel showing sequence stats."""
        props_frame = ctk.CTkFrame(self.editor_frame)
        props_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Calculate sequence properties
        sequence_content = self.viewmodel.get_state('sequence_content', '')
        current_sequence = self.viewmodel.get_state('current_sequence')
        
        if current_sequence and sequence_content:
            # Remove header line and whitespace
            lines = sequence_content.split('\n')
            seq_only = ''.join(line.strip() for line in lines if not line.startswith('>'))
            
            length = len(seq_only)
            gc_count = seq_only.upper().count('G') + seq_only.upper().count('C')
            gc_percent = (gc_count / length * 100) if length > 0 else 0
            seq_type = current_sequence.sequence_type.upper()
            
            stats_text = f"Length: {length} bp | GC%: {gc_percent:.1f}% | Type: {seq_type}"
        else:
            stats_text = "No sequence loaded"
        
        ctk.CTkLabel(
            props_frame,
            text=stats_text,
            font=("Arial", 10)
        ).pack(padx=10, pady=10)
    
    def _on_header_changed(self, event):
        """Handle header text changes."""
        if hasattr(self, 'header_entry'):
            new_header = self.header_entry.get()
            self.viewmodel.update_sequence_header(new_header)
    
    def _on_content_changed(self, event):
        """Handle sequence content changes."""
        new_content = self.editor.get("1.0", "end-1c")
        self.viewmodel.update_sequence_content(new_content)
    
    def _update_sequence_display(self):
        """Update sequence display when content changes."""
        if hasattr(self, 'editor'):
            sequence_content = self.viewmodel.get_state('sequence_content', '')
            current_content = self.editor.get("1.0", "end-1c")
            
            if current_content != sequence_content:
                # Update without triggering change event
                self.editor.unbind("<KeyRelease>")
                self.editor.delete("1.0", "end")
                self.editor.insert("1.0", sequence_content)
                if self.viewmodel.get_state('is_editing', False):
                    self.editor.bind("<KeyRelease>", self._on_content_changed)
    
    def _update_header_display(self):
        """Update header display when header changes."""
        if hasattr(self, 'header_entry'):
            sequence_header = self.viewmodel.get_state('sequence_header', '')
            current_header = self.header_entry.get()
            
            if current_header != sequence_header:
                self.header_entry.delete(0, "end")
                self.header_entry.insert(0, sequence_header)
    
    def _update_editor_mode(self, is_editing: bool):
        """Update editor mode (editing vs viewing)."""
        # Recreate editor interface to reflect new mode
        current_sequence = self.viewmodel.get_state('current_sequence')
        if current_sequence:
            self._show_editor()
    
    def _update_save_button_state(self, has_changes: bool):
        """Update save button state based on unsaved changes."""
        if hasattr(self, 'save_button'):
            if has_changes:
                self.save_button.configure(text="💾 Save*")
            else:
                self.save_button.configure(text="💾 Save")
    
    def _update_loading_state(self, loading: bool):
        """Update UI loading state."""
        if loading:
            self.status_label.configure(text="Loading...")
        else:
            self.status_label.configure(text="Ready")
    
    def _show_save_changes_dialog(self):
        """Show save changes confirmation dialog."""
        current_sequence = self.viewmodel.get_state('current_sequence')
        filename = current_sequence.header if current_sequence else "sequence"
        
        dialog = SaveChangesDialog(
            self,
            filename=filename,
            on_save=self._handle_save_and_continue,
            on_dont_save=self._handle_discard_changes,
            on_cancel=self._handle_cancel_save_dialog
        )
    
    def _handle_save_and_continue(self):
        """Handle save and continue from dialog."""
        self.viewmodel.save_sequence()
    
    def _handle_discard_changes(self):
        """Handle discard changes from dialog."""
        self.viewmodel.confirm_discard_changes()
    
    def _handle_cancel_save_dialog(self):
        """Handle cancel from save dialog."""
        self.viewmodel.update_state('show_save_dialog', False)
    
    # Event handlers
    def _handle_open_file(self):
        """Handle open file action."""
        # This would typically show a file dialog
        show_success("Open file dialog would appear here")
    
    def _handle_save_file(self):
        """Handle save file action."""
        if self.viewmodel.get_state('current_sequence'):
            self.viewmodel.save_sequence()
        else:
            show_error("No sequence to save")
    
    def _handle_new_sequence(self):
        """Handle new sequence action."""
        self.viewmodel.create_new_sequence()
    
    def _handle_copy(self):
        """Handle copy action."""
        if hasattr(self, 'editor'):
            try:
                selected_text = self.editor.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                show_success("Text copied to clipboard")
            except tk.TclError:
                show_error("No text selected")
    
    def _handle_cut(self):
        """Handle cut action."""
        if hasattr(self, 'editor') and self.viewmodel.get_state('is_editing', False):
            try:
                selected_text = self.editor.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.editor.delete("sel.first", "sel.last")
                show_success("Text cut to clipboard")
            except tk.TclError:
                show_error("No text selected")
    
    def _handle_paste(self):
        """Handle paste action."""
        if hasattr(self, 'editor') and self.viewmodel.get_state('is_editing', False):
            try:
                clipboard_text = self.clipboard_get()
                self.editor.insert("insert", clipboard_text)
                show_success("Text pasted from clipboard")
            except tk.TclError:
                show_error("Nothing to paste")
    
    def _handle_search(self):
        """Handle search action."""
        show_success("Search functionality would be implemented here")
    
    def _handle_undo(self):
        """Handle undo action."""
        if hasattr(self, 'editor'):
            try:
                self.editor.edit_undo()
            except tk.TclError:
                show_error("Nothing to undo")
    
    def _handle_redo(self):
        """Handle redo action."""
        if hasattr(self, 'editor'):
            try:
                self.editor.edit_redo()
            except tk.TclError:
                show_error("Nothing to redo")
    
    def _handle_import_fasta(self):
        """Handle import FASTA files action."""
        selected_files = self.viewmodel.get_state('selected_files', [])
        if selected_files:
            # Filter for FASTA files
            fasta_files = []
            for file_path in selected_files:
                if file_path.lower().endswith(('.fasta', '.fa', '.fas', '.fna')):
                    fasta_files.append(file_path)
            
            if fasta_files:
                self.viewmodel.import_fasta_files(fasta_files)
            else:
                show_error("No FASTA files selected")
        else:
            show_error("No files selected")
    
    def _handle_import_single_file(self, file_path: str):
        """Handle import of a single FASTA file."""
        self.viewmodel.import_fasta_files([file_path])
    
    def _handle_edit_sequence(self):
        """Handle edit sequence action."""
        self.viewmodel.edit_sequence()
    
    def _handle_save_sequence(self):
        """Handle save sequence action."""
        self.viewmodel.save_sequence()
    
    def _handle_cancel_editing(self):
        """Handle cancel editing action."""
        self.viewmodel.cancel_editing()
    
    def set_current_project(self, project_id: int):
        """Set the current project for workspace operations."""
        self.viewmodel.set_current_project(project_id)
    
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
