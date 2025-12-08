"""
GeneStudio - DNA Sequence Analysis Application

A professional desktop GUI application for DNA sequence analysis implementing
core bioinformatics algorithms using CustomTkinter and MVVM architecture.
"""

import customtkinter as ctk
from views.main_window import MainWindow


def main():
    """Main entry point for GeneStudio application."""
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run application
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
