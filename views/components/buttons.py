"""Custom button components."""

import customtkinter as ctk


class PrimaryButton(ctk.CTkButton):
    """Primary action button with consistent styling."""
    
    def __init__(self, parent, text: str, command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#36719F", "#144870"),
            **kwargs
        )


class SecondaryButton(ctk.CTkButton):
    """Secondary action button."""
    
    def __init__(self, parent, text: str, command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color="transparent",
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            **kwargs
        )


class DangerButton(ctk.CTkButton):
    """Danger/destructive action button."""
    
    def __init__(self, parent, text: str, command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color=("#D32F2F", "#B71C1C"),
            hover_color=("#C62828", "#A01010"),
            **kwargs
        )


class IconButton(ctk.CTkButton):
    """Icon-only button."""
    
    def __init__(self, parent, icon: str, command=None, **kwargs):
        super().__init__(
            parent,
            text=icon,
            command=command,
            width=40,
            height=40,
            **kwargs
        )


class ButtonGroup(ctk.CTkFrame):
    """Group of related buttons."""
    
    def __init__(self, parent, buttons: list, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        for i, btn_config in enumerate(buttons):
            btn = ctk.CTkButton(
                self,
                text=btn_config.get("text", ""),
                command=btn_config.get("command"),
                width=btn_config.get("width", 100)
            )
            btn.pack(side="left", padx=5)
