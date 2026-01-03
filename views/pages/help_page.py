"""Help page."""

import customtkinter as ctk


class HelpPage(ctk.CTkFrame):
    """Help and documentation page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Help & Documentation",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        # Search
        ctk.CTkEntry(
            header,
            placeholder_text="🔍 Search help topics...",
            width=300
        ).pack(side="right")
        
        # Content
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Help topics
        topics = ctk.CTkTextbox(content_frame, font=("Arial", 11))
        topics.pack(fill="both", expand=True, padx=20, pady=20)
        
        help_text = """
📚 GeneStudio Pro - Help & Documentation

=== GETTING STARTED ===

Welcome to GeneStudio Pro! This enterprise-grade DNA sequence analysis platform provides 
comprehensive tools for bioinformatics research.

=== MAIN FEATURES ===

🏠 Dashboard
   - View project statistics
   - Quick access to common tasks
   - Recent activity tracking

📁 Projects
   - Create and manage analysis projects
   - Use pre-built templates
   - Organize your work efficiently

💼 Workspace
   - Edit sequences directly
   - Manage files and folders
   - Integrated file browser

🔬 Analysis Tools
   - Basic sequence operations (GC%, reverse, complement)
   - Pattern matching (Boyer-Moore, suffix arrays)
   - Translation (DNA to amino acids)
   - Approximate matching (Hamming, edit distance)

📈 Visualization
   - Interactive 2D plots
   - 3D graph visualization
   - Multiple chart types
   - Export capabilities

🕸️ Graph Analysis
   - Overlap graph construction
   - De Bruijn graphs
   - 3D visualization
   - Graph metrics

📄 Reports
   - Generate comprehensive reports
   - Multiple export formats (PDF, Excel, CSV, HTML)
   - Custom report templates

⚙️ Settings
   - Customize appearance
   - Configure preferences
   - Advanced options

=== KEYBOARD SHORTCUTS ===

Ctrl+N  - New Project
Ctrl+O  - Open Project
Ctrl+S  - Save
Ctrl+F  - Find/Search
Ctrl+Z  - Undo
Ctrl+Y  - Redo

=== SUPPORT ===

For additional help, please visit:
- Documentation: docs.genestudio.com
- Support: support@genestudio.com
- Community: community.genestudio.com

Version 2.0 Enterprise Edition
© 2024 GeneStudio. All rights reserved.
"""
        
        topics.insert("1.0", help_text)
        topics.configure(state="disabled")
