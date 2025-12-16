#!/usr/bin/env python3
"""
Demo script showcasing GeneStudio Pro enhanced features.
"""

import customtkinter as ctk
from views.components.visualization_panel import VisualizationPanel, StatisticsPanel
import tkinter as tk


def demo_visualizations():
    """Demo the enhanced visualization capabilities."""
    
    # Set appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create demo window
    root = ctk.CTk()
    root.title("GeneStudio Pro - Visualization Demo")
    root.geometry("1200x800")
    
    # Create notebook for different demos
    notebook = ctk.CTkTabview(root)
    notebook.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Demo sequence
    demo_sequence = "ATCGATCGATCGATCGAAAAAATTTTTGGGGGGCCCCCCATCGATCGATCGAAATTTGGGCCCATCG" * 10
    
    # Tab 1: Nucleotide Composition
    tab1 = notebook.add("Nucleotide Composition")
    viz1 = VisualizationPanel(tab1)
    viz1.pack(fill="both", expand=True)
    
    def show_composition():
        viz1.plot_nucleotide_composition(demo_sequence, "Demo: Nucleotide Composition")
    
    ctk.CTkButton(tab1, text="Show Composition", command=show_composition).pack(pady=10)
    
    # Tab 2: GC Content
    tab2 = notebook.add("GC Content Analysis")
    viz2 = VisualizationPanel(tab2)
    viz2.pack(fill="both", expand=True)
    
    def show_gc_content():
        viz2.plot_gc_content_window(demo_sequence, 50, "Demo: GC Content Analysis")
    
    ctk.CTkButton(tab2, text="Show GC Analysis", command=show_gc_content).pack(pady=10)
    
    # Tab 3: Pattern Matches
    tab3 = notebook.add("Pattern Matching")
    viz3 = VisualizationPanel(tab3)
    viz3.pack(fill="both", expand=True)
    
    def show_pattern_matches():
        # Demo matches for pattern "ATCG"
        matches = [i for i in range(0, len(demo_sequence)-3, 20) if demo_sequence[i:i+4] == "ATCG"]
        viz3.plot_pattern_matches(demo_sequence, matches, "ATCG", "Demo: Pattern Matches")
    
    ctk.CTkButton(tab3, text="Show Pattern Matches", command=show_pattern_matches).pack(pady=10)
    
    # Tab 4: Statistics
    tab4 = notebook.add("Statistics Panel")
    stats_panel = StatisticsPanel(tab4)
    stats_panel.pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_statistics():
        stats_panel.update_statistics(demo_sequence, "Demo Sequence")
    
    ctk.CTkButton(tab4, text="Show Statistics", command=show_statistics).pack(pady=10)
    
    # Show initial demos
    root.after(1000, show_composition)
    
    # Instructions
    info_label = ctk.CTkLabel(
        root,
        text="🧬 GeneStudio Pro Visualization Demo - Click buttons to see enhanced features!",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    info_label.pack(pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    print("🧬 Starting GeneStudio Pro Visualization Demo...")
    print("This demo showcases the enhanced visualization capabilities.")
    print("Close the demo window when finished.\n")
    
    try:
        demo_visualizations()
        print("✅ Demo completed successfully!")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")