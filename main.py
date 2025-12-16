"""
GeneStudio Pro - Advanced DNA Sequence Analysis Application

A professional desktop GUI application for DNA sequence analysis implementing
core bioinformatics algorithms with advanced visualizations using CustomTkinter,
matplotlib, and MVVM architecture.
"""

import customtkinter as ctk
from views.enhanced_main_window import EnhancedMainWindow
from views.components.splash_screen import SplashScreen


def main():
    """Main entry point for GeneStudio Pro application."""
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Show splash screen
    splash = SplashScreen()
    splash.show_and_wait(duration=3.5)
    
    # Create and run enhanced application
    app = EnhancedMainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
