"""Enhanced sequence management page with comprehensive library management."""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Dict, Any, Optional
import threading
import time

from views.components import (
    PrimaryButton, SecondaryButton, DataTable, 
    SkeletonCard, LinearProgress, show_success, show_error, show_info, show_warning
)
from views.components.confirmation_dialog import ConfirmDialog
from viewmodels.sequence_management_viewmodel import SequenceManagementViewModel
from utils.pagination import debounce_call
from utils.logger import get_logger


class BatchOperationDialog(ctk.CTkToplevel):
    """Dialog for batch operations on sequences."""
    
    def __init__(self, parent, operation_type: str, sequence_count: int):
        super().__init__(parent)
        
        self.operation_type = operation_type
        self.sequence_count = sequence_count
        self.result = None
        
        self.title(f"Batch {operation_type.title()}")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _setup_ui(self):
        """Setup dialog UI."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text=f"Batch {self.operation_type.title()}",
            font=("Arial", 18, "bold")
        ).pack()
        
        ctk.CTkLabel(
            header_frame,
            text=f"Selected {self.sequence_count} sequences",
            font=("Arial", 12)
        ).pack(pady=(5, 0))
        
        # Options frame
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        if self.operation_type == "export":
            self._setup_export_options(options_frame)
        elif self.operation_type == "delete":
            self._setup_delete_options(options_frame)
        elif self.operation_type == "tag":
            self._setup_tag_options(options_frame)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        SecondaryButton(
            button_frame,
            text="Cancel",
            command=self._cancel
        ).pack(side="right", padx=(5, 0))
        
        PrimaryButton(
            button_frame,
            text="Execute",
            command=self._execute
        ).pack(side="right")
    
    def _setup_export_options(self, parent):
        """Setup export-specific options."""
        ctk.CTkLabel(parent, text="Export Format:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.export_format = ctk.CTkOptionMenu(
            parent,
            values=["FASTA", "CSV", "JSON"],
            width=200
        )
        self.export_format.pack(anchor="w", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(parent, text="Output File:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        file_frame = ctk.CTkFrame(parent, fg_color="transparent")
        file_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.output_file = ctk.CTkEntry(file_frame, placeholder_text="Select output file...")
        self.output_file.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        SecondaryButton(
            file_frame,
            text="Browse",
            width=80,
            command=self._browse_output_file
        ).pack(side="right")
        
        # Export options
        self.include_metadata = ctk.CTkCheckBox(parent, text="Include metadata")
        self.include_metadata.pack(anchor="w", padx=10, pady=5)
        
        self.include_tags = ctk.CTkCheckBox(parent, text="Include tags")
        self.include_tags.pack(anchor="w", padx=10, pady=5)
    
    def _setup_delete_options(self, parent):
        """Setup delete-specific options."""
        warning_frame = ctk.CTkFrame(parent, fg_color=("#ffebee", "#d32f2f"))
        warning_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            warning_frame,
            text="⚠️ Warning",
            font=("Arial", 14, "bold"),
            text_color=("#d32f2f", "#ffcdd2")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            warning_frame,
            text="This action cannot be undone. All selected sequences\nand their associated data will be permanently deleted.",
            font=("Arial", 11),
            text_color=("#d32f2f", "#ffcdd2")
        ).pack(pady=(0, 10))
        
        self.delete_analyses = ctk.CTkCheckBox(
            parent, 
            text="Also delete associated analyses",
            font=("Arial", 11)
        )
        self.delete_analyses.pack(anchor="w", padx=10, pady=10)
        self.delete_analyses.select()  # Default to selected
    
    def _setup_tag_options(self, parent):
        """Setup tag-specific options."""
        ctk.CTkLabel(parent, text="Operation:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.tag_operation = ctk.CTkOptionMenu(
            parent,
            values=["Add Tag", "Remove Tag"],
            width=200
        )
        self.tag_operation.pack(anchor="w", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(parent, text="Tag:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.tag_entry = ctk.CTkEntry(parent, placeholder_text="Enter tag name...")
        self.tag_entry.pack(fill="x", padx=10, pady=(0, 10))
    
    def _browse_output_file(self):
        """Browse for output file."""
        format_ext = {
            "FASTA": ".fasta",
            "CSV": ".csv", 
            "JSON": ".json"
        }
        
        current_format = self.export_format.get()
        ext = format_ext.get(current_format, ".txt")
        
        filename = filedialog.asksaveasfilename(
            title="Save Export File",
            defaultextension=ext,
            filetypes=[
                (f"{current_format} files", f"*{ext}"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.output_file.delete(0, tk.END)
            self.output_file.insert(0, filename)
    
    def _cancel(self):
        """Cancel dialog."""
        self.result = None
        self.destroy()
    
    def _execute(self):
        """Execute batch operation."""
        if self.operation_type == "export":
            if not self.output_file.get().strip():
                messagebox.showerror("Error", "Please select an output file.")
                return
            
            self.result = {
                'format': self.export_format.get().lower(),
                'output_path': self.output_file.get().strip(),
                'include_metadata': self.include_metadata.get(),
                'include_tags': self.include_tags.get()
            }
        
        elif self.operation_type == "delete":
            self.result = {
                'delete_analyses': self.delete_analyses.get()
            }
        
        elif self.operation_type == "tag":
            tag = self.tag_entry.get().strip()
            if not tag:
                messagebox.showerror("Error", "Please enter a tag name.")
                return
            
            operation = "add_tag" if self.tag_operation.get() == "Add Tag" else "remove_tag"
            self.result = {
                'operation': operation,
                'tag': tag
            }
        
        self.destroy()


class MetadataEditDialog(ctk.CTkToplevel):
    """Dialog for editing sequence metadata."""
    
    def __init__(self, parent, sequence_data: Dict[str, Any]):
        super().__init__(parent)
        
        self.sequence_data = sequence_data
        self.result = None
        
        self.title("Edit Sequence Metadata")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _setup_ui(self):
        """Setup dialog UI."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="Edit Sequence Metadata",
            font=("Arial", 18, "bold")
        ).pack()
        
        # Form frame
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Header field
        ctk.CTkLabel(form_frame, text="Header:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.header_entry = ctk.CTkEntry(form_frame, width=400)
        self.header_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.header_entry.insert(0, self.sequence_data.get('header', ''))
        
        # Sequence type
        ctk.CTkLabel(form_frame, text="Type:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.type_menu = ctk.CTkOptionMenu(form_frame, values=["dna", "rna", "protein"], width=200)
        self.type_menu.pack(anchor="w", padx=10, pady=(0, 10))
        self.type_menu.set(self.sequence_data.get('sequence_type', 'dna'))
        
        # Notes field
        ctk.CTkLabel(form_frame, text="Notes:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.notes_text = ctk.CTkTextbox(form_frame, height=80)
        self.notes_text.pack(fill="x", padx=10, pady=(0, 10))
        self.notes_text.insert("1.0", self.sequence_data.get('notes', ''))
        
        # Tags field
        ctk.CTkLabel(form_frame, text="Tags (comma-separated):", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.tags_entry = ctk.CTkEntry(form_frame, width=400)
        self.tags_entry.pack(fill="x", padx=10, pady=(0, 10))
        tags = self.sequence_data.get('tags', [])
        if isinstance(tags, list):
            self.tags_entry.insert(0, ', '.join(tags))
        else:
            self.tags_entry.insert(0, str(tags))
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        SecondaryButton(
            button_frame,
            text="Cancel",
            command=self._cancel
        ).pack(side="right", padx=(5, 0))
        
        PrimaryButton(
            button_frame,
            text="Save",
            command=self._save
        ).pack(side="right")
    
    def _cancel(self):
        """Cancel dialog."""
        self.result = None
        self.destroy()
    
    def _save(self):
        """Save metadata changes."""
        # Parse tags
        tags_text = self.tags_entry.get().strip()
        tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()] if tags_text else []
        
        self.result = {
            'header': self.header_entry.get().strip(),
            'sequence_type': self.type_menu.get(),
            'notes': self.notes_text.get("1.0", tk.END).strip(),
            'tags': tags
        }
        
        self.destroy()


class SequenceManagementPage(ctk.CTkFrame):
    """Enhanced sequence library and management page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.logger = get_logger(self.__class__.__name__)
        self.viewmodel = SequenceManagementViewModel()
        
        # Bind to ViewModel state changes
        self.viewmodel.bind_state_change(self._on_state_change)
        
        self._setup_ui()
        self._bind_events()
        
        # Load initial data
        self._load_sequences()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Header with statistics
        self._create_header()
        
        # Toolbar with search and filters
        self._create_toolbar()
        
        # Main content area
        self._create_main_content()
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self):
        """Create header with title and statistics."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        # Title and stats
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            title_frame,
            text="Sequence Management",
            font=("Arial", 24, "bold")
        ).pack(anchor="w")
        
        self.stats_label = ctk.CTkLabel(
            title_frame,
            text="Loading statistics...",
            font=("Arial", 12),
            text_color=("gray60", "gray40")
        )
        self.stats_label.pack(anchor="w", pady=(5, 0))
        
        # Action buttons
        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.pack(side="right")
        
        self.import_btn = PrimaryButton(
            button_frame,
            text="📁 Import",
            width=120,
            command=self._import_sequences
        )
        self.import_btn.pack(side="right", padx=5)
        
        self.export_btn = SecondaryButton(
            button_frame,
            text="💾 Export",
            width=120,
            command=self._export_selected
        )
        self.export_btn.pack(side="right", padx=5)
        
        self.refresh_btn = SecondaryButton(
            button_frame,
            text="🔄 Refresh",
            width=100,
            command=self._refresh_sequences
        )
        self.refresh_btn.pack(side="right", padx=5)
    
    def _create_toolbar(self):
        """Create toolbar with search and filters."""
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=20, pady=(0, 20))
        
        # Search section
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search sequences by name, notes, or tags...",
            width=300
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        
        # Filters
        self.type_filter = ctk.CTkOptionMenu(
            search_frame,
            values=["All Types", "DNA", "RNA", "Protein"],
            width=120,
            command=self._on_filter_changed
        )
        self.type_filter.pack(side="left", padx=5)
        
        self.sort_filter = ctk.CTkOptionMenu(
            search_frame,
            values=["Date (Newest)", "Date (Oldest)", "Name (A-Z)", "Name (Z-A)", "Length (Largest)", "Length (Smallest)"],
            width=150,
            command=self._on_sort_changed
        )
        self.sort_filter.pack(side="left", padx=5)
        
        # Batch operations
        batch_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        batch_frame.pack(side="right", padx=10, pady=10)
        
        self.select_all_btn = SecondaryButton(
            batch_frame,
            text="☑️ Select All",
            width=100,
            command=self._select_all
        )
        self.select_all_btn.pack(side="right", padx=5)
        
        self.batch_tag_btn = SecondaryButton(
            batch_frame,
            text="🏷️ Tag",
            width=80,
            command=self._batch_tag
        )
        self.batch_tag_btn.pack(side="right", padx=5)
        
        self.batch_delete_btn = SecondaryButton(
            batch_frame,
            text="🗑️ Delete",
            width=80,
            command=self._batch_delete
        )
        self.batch_delete_btn.pack(side="right", padx=5)
        
        self.edit_metadata_btn = SecondaryButton(
            batch_frame,
            text="✏️ Edit",
            width=80,
            command=self._edit_metadata
        )
        self.edit_metadata_btn.pack(side="right", padx=5)
    
    def _create_main_content(self):
        """Create main content area with sequence table."""
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Loading indicator
        self.loading_frame = ctk.CTkFrame(content_frame)
        self.loading_indicator = LinearProgress(self.loading_frame, mode="indeterminate")
        self.loading_indicator.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Sequence table
        self.table_frame = ctk.CTkFrame(content_frame)
        
        self.sequence_table = DataTable(
            self.table_frame,
            columns=["☑️", "ID", "Header", "Type", "Length", "GC%", "Tags", "Date Added"],
            column_widths=[40, 60, 200, 80, 80, 60, 150, 120],
            show_scrollbar=True
        )
        self.sequence_table.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pagination controls
        pagination_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        pagination_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.page_info_label = ctk.CTkLabel(
            pagination_frame,
            text="Page 1 of 1 (0 sequences)",
            font=("Arial", 11)
        )
        self.page_info_label.pack(side="left")
        
        # Page controls
        page_controls = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        page_controls.pack(side="right")
        
        self.prev_btn = SecondaryButton(
            page_controls,
            text="◀ Previous",
            width=80,
            command=self._previous_page
        )
        self.prev_btn.pack(side="left", padx=2)
        
        self.next_btn = SecondaryButton(
            page_controls,
            text="Next ▶",
            width=80,
            command=self._next_page
        )
        self.next_btn.pack(side="left", padx=2)
        
        self.page_size_menu = ctk.CTkOptionMenu(
            page_controls,
            values=["25", "50", "100", "200"],
            width=80,
            command=self._on_page_size_changed
        )
        self.page_size_menu.pack(side="left", padx=(10, 0))
        self.page_size_menu.set("50")
    
    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.pack(fill="x", padx=20, pady=(0, 20))
        self.status_bar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=("Arial", 10)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Progress bar for batch operations
        self.progress_bar = ctk.CTkProgressBar(self.status_bar, width=200)
        self.progress_bar.pack(side="right", padx=10, pady=5)
        self.progress_bar.pack_forget()  # Hidden by default
    
    def _bind_events(self):
        """Bind UI events."""
        # Table selection events
        self.sequence_table.bind_selection_change(self._on_selection_changed)
        self.sequence_table.bind_double_click(self._on_sequence_double_click)
    
    def _on_state_change(self, key: str, value: Any):
        """Handle ViewModel state changes."""
        if key == "filtered_sequences":
            self._update_sequence_table(value)
        elif key == "sequence_statistics":
            self._update_statistics(value)
        elif key == "selected_sequences":
            self._update_selection_ui(value)
        elif key == "current_page":
            self._update_pagination_ui()
        elif key == "total_pages":
            self._update_pagination_ui()
        elif key == "import_progress":
            self._update_import_progress(value)
        elif key == "export_progress":
            self._update_export_progress(value)
        elif key == "batch_operations":
            self._update_batch_operations(value)
    
    def _load_sequences(self):
        """Load sequences from ViewModel."""
        self._show_loading(True)
        self.viewmodel.load_sequences()
    
    def _refresh_sequences(self):
        """Refresh sequence list."""
        self.viewmodel.refresh_sequences()
    
    def _show_loading(self, show: bool):
        """Show or hide loading indicator."""
        if show:
            self.table_frame.pack_forget()
            self.loading_frame.pack(fill="both", expand=True, padx=10, pady=10)
            self.loading_indicator.start_indeterminate()
        else:
            self.loading_frame.pack_forget()
            self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
            self.loading_indicator.stop_indeterminate()
    
    def _update_sequence_table(self, sequences: List[Any]):
        """Update sequence table with new data."""
        self._show_loading(False)
        
        # Clear existing rows
        self.sequence_table.clear_rows()
        
        # Add sequences
        selected_ids = set(self.viewmodel.get_state('selected_sequences', []))
        
        for seq in sequences:
            checkbox_value = "☑️" if seq.id in selected_ids else "☐"
            
            # Format data
            tags_str = ", ".join(seq.tags[:3])  # Show first 3 tags
            if len(seq.tags) > 3:
                tags_str += f" (+{len(seq.tags) - 3})"
            
            gc_str = f"{seq.gc_percentage:.1f}%" if seq.gc_percentage else "N/A"
            date_str = seq.created_date.strftime("%Y-%m-%d") if seq.created_date else "N/A"
            
            row_data = [
                checkbox_value,
                str(seq.id),
                seq.header[:30] + "..." if len(seq.header) > 30 else seq.header,
                seq.sequence_type.upper(),
                f"{seq.length:,} bp",
                gc_str,
                tags_str,
                date_str
            ]
            
            self.sequence_table.add_row(row_data, data={'sequence_id': seq.id})
    
    def _update_statistics(self, stats: Dict[str, Any]):
        """Update statistics display."""
        if not stats:
            self.stats_label.configure(text="No statistics available")
            return
        
        total = stats.get('total_sequences', 0)
        dna = stats.get('dna_sequences', 0)
        rna = stats.get('rna_sequences', 0)
        protein = stats.get('protein_sequences', 0)
        avg_length = stats.get('avg_length', 0)
        
        stats_text = f"{total:,} sequences • DNA: {dna} • RNA: {rna} • Protein: {protein}"
        if avg_length > 0:
            stats_text += f" • Avg length: {avg_length:,.0f} bp"
        
        self.stats_label.configure(text=stats_text)
    
    def _update_selection_ui(self, selected_ids: List[int]):
        """Update UI based on selection."""
        count = len(selected_ids)
        
        # Update button states
        has_selection = count > 0
        self.export_btn.configure(state="normal" if has_selection else "disabled")
        self.batch_delete_btn.configure(state="normal" if has_selection else "disabled")
        self.batch_tag_btn.configure(state="normal" if has_selection else "disabled")
        self.edit_metadata_btn.configure(state="normal" if count == 1 else "disabled")
        
        # Update status
        if count > 0:
            self.status_label.configure(text=f"{count} sequence(s) selected")
        else:
            self.status_label.configure(text="Ready")
    
    def _update_pagination_ui(self):
        """Update pagination controls."""
        current_page = self.viewmodel.get_state('current_page', 0)
        total_pages = self.viewmodel.get_state('total_pages', 0)
        sequences = self.viewmodel.get_state('filtered_sequences', [])
        
        # Update page info
        start_idx = current_page * self.viewmodel.get_state('page_size', 50) + 1
        end_idx = start_idx + len(sequences) - 1
        total_sequences = self.viewmodel.get_state('sequence_statistics', {}).get('total_sequences', 0)
        
        if total_sequences > 0:
            page_text = f"Page {current_page + 1} of {total_pages} ({start_idx}-{end_idx} of {total_sequences:,} sequences)"
        else:
            page_text = "No sequences"
        
        self.page_info_label.configure(text=page_text)
        
        # Update button states
        self.prev_btn.configure(state="normal" if current_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if current_page < total_pages - 1 else "disabled")
    
    def _update_import_progress(self, progress: float):
        """Update import progress."""
        if progress > 0:
            self.progress_bar.pack(side="right", padx=10, pady=5)
            self.progress_bar.set(progress)
            self.status_label.configure(text=f"Importing sequences... {progress:.0%}")
        else:
            self.progress_bar.pack_forget()
    
    def _update_export_progress(self, progress: float):
        """Update export progress."""
        if progress > 0:
            self.progress_bar.pack(side="right", padx=10, pady=5)
            self.progress_bar.set(progress)
            self.status_label.configure(text=f"Exporting sequences... {progress:.0%}")
        else:
            self.progress_bar.pack_forget()
    
    def _update_batch_operations(self, operations: Dict[str, Any]):
        """Update batch operation status."""
        active_ops = [op for op in operations.values() if op.status == "running"]
        
        if active_ops:
            op = active_ops[0]  # Show first active operation
            self.progress_bar.pack(side="right", padx=10, pady=5)
            self.progress_bar.set(op.progress)
            self.status_label.configure(text=f"Batch {op.operation_type}: {op.get_completion_percentage():.0f}%")
        else:
            self.progress_bar.pack_forget()
    
    def _on_search_changed(self, event):
        """Handle search text changes with debouncing."""
        search_term = self.search_entry.get().strip()
        debounce_call("sequence_search", self._perform_search, 0.5, search_term)
    
    def _perform_search(self, search_term: str):
        """Perform the actual search."""
        if search_term:
            self.viewmodel.search_sequences(search_term)
        else:
            self.viewmodel.load_sequences()
    
    def _on_filter_changed(self, value):
        """Handle filter changes."""
        filter_criteria = {}
        
        if value != "All Types":
            filter_criteria['sequence_type'] = value.lower()
        
        self.viewmodel.apply_filters(filter_criteria)
    
    def _on_sort_changed(self, value):
        """Handle sort changes."""
        sort_mapping = {
            "Date (Newest)": ("created_date", False),
            "Date (Oldest)": ("created_date", True),
            "Name (A-Z)": ("header", True),
            "Name (Z-A)": ("header", False),
            "Length (Largest)": ("length", False),
            "Length (Smallest)": ("length", True)
        }
        
        field, ascending = sort_mapping.get(value, ("created_date", False))
        self.viewmodel.apply_sort(field, ascending)
    
    def _on_selection_changed(self, selected_rows: List[int]):
        """Handle table selection changes."""
        # Get sequence IDs from selected rows
        selected_ids = []
        for row_idx in selected_rows:
            row_data = self.sequence_table.get_row_data(row_idx)
            if row_data and 'sequence_id' in row_data:
                selected_ids.append(row_data['sequence_id'])
        
        # Update ViewModel
        for seq_id in selected_ids:
            self.viewmodel.select_sequence(seq_id, True)
    
    def _on_sequence_double_click(self, row_index: int):
        """Handle sequence double-click."""
        row_data = self.sequence_table.get_row_data(row_index)
        if row_data and 'sequence_id' in row_data:
            sequence_id = row_data['sequence_id']
            self._edit_sequence_metadata(sequence_id)
    
    def _select_all(self):
        """Select or deselect all sequences."""
        selected_count = len(self.viewmodel.get_state('selected_sequences', []))
        total_count = len(self.viewmodel.get_state('filtered_sequences', []))
        
        # If all are selected, deselect all; otherwise select all
        select_all = selected_count < total_count
        self.viewmodel.select_all_sequences(select_all)
        
        # Update button text
        self.select_all_btn.configure(text="☐ Deselect All" if select_all else "☑️ Select All")
    
    def _previous_page(self):
        """Go to previous page."""
        current_page = self.viewmodel.get_state('current_page', 0)
        if current_page > 0:
            self.viewmodel.set_page(current_page - 1)
    
    def _next_page(self):
        """Go to next page."""
        current_page = self.viewmodel.get_state('current_page', 0)
        total_pages = self.viewmodel.get_state('total_pages', 0)
        if current_page < total_pages - 1:
            self.viewmodel.set_page(current_page + 1)
    
    def _on_page_size_changed(self, value):
        """Handle page size changes."""
        try:
            page_size = int(value)
            self.viewmodel.set_page_size(page_size)
        except ValueError:
            pass
    
    def _import_sequences(self):
        """Import sequences from files."""
        file_paths = filedialog.askopenfilenames(
            title="Select Sequence Files",
            filetypes=[
                ("FASTA files", "*.fasta *.fa *.fas *.fna *.ffn *.faa *.frn"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            # For now, use project_id = 1 (would be selected from UI in real app)
            project_id = 1
            self.viewmodel.import_sequences(list(file_paths), project_id)
    
    def _export_selected(self):
        """Export selected sequences."""
        selected_ids = self.viewmodel.get_state('selected_sequences', [])
        if not selected_ids:
            messagebox.showwarning("No Selection", "Please select sequences to export.")
            return
        
        dialog = BatchOperationDialog(self, "export", len(selected_ids))
        self.wait_window(dialog)
        
        if dialog.result:
            self.viewmodel.export_sequences(
                selected_ids,
                dialog.result['format'],
                dialog.result['output_path'],
                dialog.result
            )
    
    def _batch_delete(self):
        """Delete selected sequences."""
        selected_ids = self.viewmodel.get_state('selected_sequences', [])
        if not selected_ids:
            messagebox.showwarning("No Selection", "Please select sequences to delete.")
            return
        
        dialog = BatchOperationDialog(self, "delete", len(selected_ids))
        self.wait_window(dialog)
        
        if dialog.result:
            self.viewmodel.start_batch_operation("delete", selected_ids, dialog.result)
    
    def _batch_tag(self):
        """Add or remove tags from selected sequences."""
        selected_ids = self.viewmodel.get_state('selected_sequences', [])
        if not selected_ids:
            messagebox.showwarning("No Selection", "Please select sequences to tag.")
            return
        
        dialog = BatchOperationDialog(self, "tag", len(selected_ids))
        self.wait_window(dialog)
        
        if dialog.result:
            operation_type = dialog.result['operation']
            parameters = {'tag': dialog.result['tag']}
            self.viewmodel.start_batch_operation(operation_type, selected_ids, parameters)
    
    def _edit_metadata(self):
        """Edit metadata for selected sequence."""
        selected_ids = self.viewmodel.get_state('selected_sequences', [])
        if len(selected_ids) != 1:
            messagebox.showwarning("Invalid Selection", "Please select exactly one sequence to edit.")
            return
        
        self._edit_sequence_metadata(selected_ids[0])
    
    def _edit_sequence_metadata(self, sequence_id: int):
        """Edit metadata for a specific sequence."""
        # Get sequence data
        sequences = self.viewmodel.get_state('sequences', [])
        sequence = next((s for s in sequences if s.id == sequence_id), None)
        
        if not sequence:
            messagebox.showerror("Error", "Sequence not found.")
            return
        
        # Show edit dialog
        sequence_data = {
            'header': sequence.header,
            'sequence_type': sequence.sequence_type,
            'notes': sequence.notes,
            'tags': sequence.tags
        }
        
        dialog = MetadataEditDialog(self, sequence_data)
        self.wait_window(dialog)
        
        if dialog.result:
            # Update sequence metadata
            self.viewmodel.start_metadata_editing(sequence_id)
            for field, value in dialog.result.items():
                self.viewmodel.update_metadata_form(field, value)
            self.viewmodel.save_metadata_changes()
    
    def cleanup(self):
        """Cleanup resources."""
        if hasattr(self, 'viewmodel'):
            self.viewmodel.cleanup()
