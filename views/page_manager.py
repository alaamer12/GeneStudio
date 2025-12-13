"""Page Manager - Central routing and page management system."""

import customtkinter as ctk
from typing import Dict, Callable, Optional


class PageManager:
    """Manages page registration, routing, and navigation."""
    
    def __init__(self, parent: ctk.CTkFrame):
        """
        Initialize page manager.
        
        Args:
            parent: Parent frame to contain pages
        """
        self.parent = parent
        self.pages: Dict[str, ctk.CTkFrame] = {}
        self.page_constructors: Dict[str, Callable] = {}
        self.current_page: Optional[str] = None
        self.history: list[str] = []
        
    def register_page(self, name: str, page_constructor: Callable):
        """
        Register a page constructor.
        
        Args:
            name: Page identifier
            page_constructor: Function that creates the page
        """
        self.page_constructors[name] = page_constructor
        
    def show_page(self, name: str):
        """
        Show a specific page.
        
        Args:
            name: Page identifier
        """
        # Hide current page
        if self.current_page and self.current_page in self.pages:
            self.pages[self.current_page].pack_forget()
        
        # Create page if it doesn't exist (fallback for non-preloaded pages)
        if name not in self.pages:
            if name in self.page_constructors:
                self.pages[name] = self.page_constructors[name](self.parent)
            else:
                raise ValueError(f"Page '{name}' not registered")
        
        # Show new page
        self.pages[name].pack(fill="both", expand=True)
        
        # Update history
        if self.current_page and self.current_page != name:
            self.history.append(self.current_page)
        self.current_page = name
        
    def go_back(self):
        """Navigate to previous page in history."""
        if self.history:
            previous_page = self.history.pop()
            self.show_page(previous_page)
            
    def get_current_page(self) -> Optional[str]:
        """Get current page name."""
        return self.current_page
