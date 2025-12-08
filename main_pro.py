"""
GeneStudio Pro - Enterprise Edition

A professional desktop GUI application for DNA sequence analysis implementing
core bioinformatics algorithms with enterprise-grade multi-page interface.
"""

import customtkinter as ctk
from views.main_window_pro import MainWindowPro


def main():
    """Main entry point for GeneStudio Pro application."""
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run enterprise application
    app = MainWindowPro()
    app.mainloop()


if __name__ == "__main__":
    main()
