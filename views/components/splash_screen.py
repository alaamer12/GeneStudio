"""
Professional splash screen for GeneStudio Pro.
"""

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import threading
import time


class SplashScreen(ctk.CTkToplevel):
    """Professional splash screen with loading animation."""
    
    def __init__(self, parent=None):
        """Initialize splash screen."""
        super().__init__(parent)
        
        # Window configuration
        self.title("")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Remove window decorations
        self.overrideredirect(True)
        
        # Center on screen
        self._center_window()
        
        # Setup UI
        self._setup_ui()
        
        # Start loading animation
        self.loading = True
        self._animate_loading()
    
    def _center_window(self):
        """Center the splash screen on the display."""
        self.update_idletasks()
        width = 600
        height = 400
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_ui(self):
        """Setup splash screen UI."""
        # Main frame with gradient-like background
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Logo/Title area
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(pady=(40, 20))
        
        # App title
        title_label = ctk.CTkLabel(
            title_frame,
            text="GeneStudio Pro",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#3498DB"
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Advanced DNA Sequence Analysis",
            font=ctk.CTkFont(size=16),
            text_color="#7F8C8D"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Version
        version_label = ctk.CTkLabel(
            title_frame,
            text="Version 2.0 Professional",
            font=ctk.CTkFont(size=12),
            text_color="#95A5A6"
        )
        version_label.pack(pady=(10, 0))
        
        # Loading area
        loading_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        loading_frame.pack(pady=(40, 20))
        
        # Loading progress bar
        self.progress_bar = ctk.CTkProgressBar(
            loading_frame,
            width=300,
            height=8,
            progress_color="#3498DB"
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # Loading text
        self.loading_label = ctk.CTkLabel(
            loading_frame,
            text="Initializing application...",
            font=ctk.CTkFont(size=12),
            text_color="#BDC3C7"
        )
        self.loading_label.pack()
        
        # Features list
        features_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        features_frame.pack(pady=(20, 40))
        
        features_text = "• Advanced Visualizations  • Pattern Matching  • Sequence Analysis"
        features_label = ctk.CTkLabel(
            features_frame,
            text=features_text,
            font=ctk.CTkFont(size=11),
            text_color="#7F8C8D"
        )
        features_label.pack()
    
    def _animate_loading(self):
        """Animate the loading process."""
        def loading_thread():
            steps = [
                ("Initializing components...", 0.2),
                ("Loading algorithms...", 0.4),
                ("Setting up visualizations...", 0.6),
                ("Preparing interface...", 0.8),
                ("Ready!", 1.0)
            ]
            
            for text, progress in steps:
                if not self.loading:
                    break
                
                # Update UI in main thread
                self.after(0, lambda t=text, p=progress: self._update_loading(t, p))
                time.sleep(0.8)
            
            # Close splash screen
            if self.loading:
                self.after(0, self._close_splash)
        
        threading.Thread(target=loading_thread, daemon=True).start()
    
    def _update_loading(self, text, progress):
        """Update loading display."""
        if hasattr(self, 'loading_label') and hasattr(self, 'progress_bar'):
            self.loading_label.configure(text=text)
            self.progress_bar.set(progress)
    
    def _close_splash(self):
        """Close the splash screen."""
        self.loading = False
        self.destroy()
    
    def show_and_wait(self, duration=4.0):
        """Show splash screen and wait for specified duration."""
        self.lift()
        self.focus_force()
        
        # Auto-close after duration
        self.after(int(duration * 1000), self._close_splash)
        
        # Wait for window to close
        self.wait_window()


class AboutDialog(ctk.CTkToplevel):
    """Professional about dialog."""
    
    def __init__(self, parent):
        """Initialize about dialog."""
        super().__init__(parent)
        
        self.title("About GeneStudio Pro")
        self.geometry("500x600")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self._center_on_parent(parent)
        
        self._setup_ui()
    
    def _center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.update_idletasks()
        
        # Get parent position and size
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - 500) // 2
        y = parent_y + (parent_height - 600) // 2
        
        self.geometry(f"500x600+{x}+{y}")
    
    def _setup_ui(self):
        """Setup about dialog UI."""
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="GeneStudio Pro",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#3498DB"
        )
        title_label.pack(pady=(0, 10))
        
        # Version and build info
        version_label = ctk.CTkLabel(
            main_frame,
            text="Version 2.0 Professional Edition",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        version_label.pack(pady=5)
        
        # Description
        desc_text = """
Advanced DNA Sequence Analysis Application

GeneStudio Pro is a comprehensive bioinformatics tool designed for 
professional DNA sequence analysis. It combines powerful algorithms 
with intuitive visualizations to provide insights into genetic data.
        """
        
        desc_label = ctk.CTkLabel(
            main_frame,
            text=desc_text.strip(),
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        desc_label.pack(pady=20)
        
        # Features
        features_frame = ctk.CTkFrame(main_frame)
        features_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            features_frame,
            text="Key Features",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        features = [
            "• Advanced sequence visualization with matplotlib",
            "• Boyer-Moore pattern matching algorithms",
            "• Suffix array construction and analysis",
            "• Overlap graph generation",
            "• Approximate matching (Hamming & Edit distance)",
            "• GC content analysis with sliding windows",
            "• Nucleotide composition analysis",
            "• Professional export capabilities",
            "• MVVM architecture for maintainability"
        ]
        
        for feature in features:
            ctk.CTkLabel(
                features_frame,
                text=feature,
                font=ctk.CTkFont(size=11),
                anchor="w"
            ).pack(anchor="w", padx=20, pady=1)
        
        # Technical info
        tech_frame = ctk.CTkFrame(main_frame)
        tech_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            tech_frame,
            text="Technical Information",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        tech_info = [
            "• Built with Python and CustomTkinter",
            "• Matplotlib for professional visualizations",
            "• NumPy and Pandas for data processing",
            "• Seaborn for enhanced plotting",
            "• Modular MVVM architecture",
            "• Comprehensive error handling",
            "• Input validation and sanitization"
        ]
        
        for info in tech_info:
            ctk.CTkLabel(
                tech_frame,
                text=info,
                font=ctk.CTkFont(size=11),
                anchor="w"
            ).pack(anchor="w", padx=20, pady=1)
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            command=self.destroy,
            width=100,
            height=35
        )
        close_btn.pack(pady=20)