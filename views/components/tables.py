"""Table components for data display."""

import customtkinter as ctk
from tkinter import ttk


class DataTable(ctk.CTkFrame):
    """Professional data table with sorting and selection."""
    
    def __init__(self, parent, columns: list, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create treeview
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=150)
        
        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.sort_reverse = False
        
    def add_row(self, values: list):
        """Add a row to the table."""
        self.tree.insert("", "end", values=values)
        
    def clear(self):
        """Clear all rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
    def _sort_by(self, col):
        """Sort table by column."""
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children("")]
        data.sort(reverse=self.sort_reverse)
        
        for index, (val, item) in enumerate(data):
            self.tree.move(item, "", index)
        
        self.sort_reverse = not self.sort_reverse
