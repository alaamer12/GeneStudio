"""Settings page."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton


class SettingsPage(ctk.CTkFrame):
    """Application settings page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Settings",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        PrimaryButton(
            header,
            text="💾 Save Settings",
            width=140
        ).pack(side="right", padx=5)
        
        SecondaryButton(
            header,
            text="↩️ Reset",
            width=100
        ).pack(side="right", padx=5)
        
        # Settings tabs
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Appearance tab
        appearance_tab = tabview.add("Appearance")
        
        ctk.CTkLabel(
            appearance_tab,
            text="Theme",
            font=("Arial", 12, "bold")
        ).pack(padx=20, pady=(20, 10), anchor="w")
        
        ctk.CTkOptionMenu(
            appearance_tab,
            values=["Dark", "Light", "System"],
            width=200
        ).pack(padx=20, pady=(0, 20), anchor="w")
        
        ctk.CTkLabel(
            appearance_tab,
            text="Color Scheme",
            font=("Arial", 12, "bold")
        ).pack(padx=20, pady=(10, 10), anchor="w")
        
        ctk.CTkOptionMenu(
            appearance_tab,
            values=["Blue", "Green", "Purple", "Red"],
            width=200
        ).pack(padx=20, pady=(0, 20), anchor="w")
        
        ctk.CTkLabel(
            appearance_tab,
            text="Font Size",
            font=("Arial", 12, "bold")
        ).pack(padx=20, pady=(10, 10), anchor="w")
        
        ctk.CTkSlider(
            appearance_tab,
            from_=10,
            to=20,
            number_of_steps=10
        ).pack(padx=20, pady=(0, 20), anchor="w", fill="x")
        
        # Preferences tab
        prefs_tab = tabview.add("Preferences")
        
        ctk.CTkCheckBox(
            prefs_tab,
            text="Auto-save projects"
        ).pack(padx=20, pady=10, anchor="w")
        
        ctk.CTkCheckBox(
            prefs_tab,
            text="Show line numbers in editor"
        ).pack(padx=20, pady=10, anchor="w")
        
        ctk.CTkCheckBox(
            prefs_tab,
            text="Enable syntax highlighting"
        ).pack(padx=20, pady=10, anchor="w")
        
        ctk.CTkCheckBox(
            prefs_tab,
            text="Confirm before deleting"
        ).pack(padx=20, pady=10, anchor="w")
        
        ctk.CTkCheckBox(
            prefs_tab,
            text="Show tooltips"
        ).pack(padx=20, pady=10, anchor="w")
        
        # Advanced tab
        advanced_tab = tabview.add("Advanced")
        
        ctk.CTkLabel(
            advanced_tab,
            text="Performance",
            font=("Arial", 12, "bold")
        ).pack(padx=20, pady=(20, 10), anchor="w")
        
        ctk.CTkLabel(
            advanced_tab,
            text="Max threads:",
            font=("Arial", 10)
        ).pack(padx=20, pady=(5, 2), anchor="w")
        
        ctk.CTkEntry(
            advanced_tab,
            placeholder_text="4",
            width=100
        ).pack(padx=20, pady=(0, 15), anchor="w")
        
        ctk.CTkLabel(
            advanced_tab,
            text="Cache size (MB):",
            font=("Arial", 10)
        ).pack(padx=20, pady=(5, 2), anchor="w")
        
        ctk.CTkEntry(
            advanced_tab,
            placeholder_text="512",
            width=100
        ).pack(padx=20, pady=(0, 15), anchor="w")
        
        ctk.CTkCheckBox(
            advanced_tab,
            text="Enable debug mode"
        ).pack(padx=20, pady=10, anchor="w")
        
        ctk.CTkCheckBox(
            advanced_tab,
            text="Log all operations"
        ).pack(padx=20, pady=10, anchor="w")
