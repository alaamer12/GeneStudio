"""Card components for displaying information."""

import customtkinter as ctk


class StatCard(ctk.CTkFrame):
    """Card displaying a statistic with icon and value."""
    
    def __init__(self, parent, title: str, value: str, icon: str = "📊", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Icon
        icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Arial", 32)
        )
        icon_label.pack(pady=(15, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            self,
            text=value,
            font=("Arial", 24, "bold")
        )
        value_label.pack(pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 12),
            text_color="gray"
        )
        title_label.pack(pady=(5, 15))
        
    def update_value(self, value: str):
        """Update the displayed value."""
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("font")[1] == 24:
                widget.configure(text=value)
                break


class InfoCard(ctk.CTkFrame):
    """Card for displaying information with title and content."""
    
    def __init__(self, parent, title: str, content: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=15, pady=(15, 5))
        
        # Content
        self.content_label = ctk.CTkLabel(
            self,
            text=content,
            font=("Arial", 11),
            anchor="w",
            justify="left"
        )
        self.content_label.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
    def update_content(self, content: str):
        """Update card content."""
        self.content_label.configure(text=content)


class ActionCard(ctk.CTkFrame):
    """Card with action button."""
    
    def __init__(self, parent, title: str, description: str, 
                 button_text: str, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Title
        ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", padx=15, pady=(15, 5))
        
        # Description
        ctk.CTkLabel(
            self,
            text=description,
            font=("Arial", 11),
            text_color="gray",
            anchor="w",
            wraplength=250
        ).pack(fill="x", padx=15, pady=5)
        
        # Button
        ctk.CTkButton(
            self,
            text=button_text,
            command=command
        ).pack(padx=15, pady=15)
