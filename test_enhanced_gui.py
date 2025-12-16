#!/usr/bin/env python3
"""
Test script for the enhanced GeneStudio Pro GUI.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test imports
    print("Testing imports...")
    
    import customtkinter as ctk
    print("✓ CustomTkinter imported successfully")
    
    import matplotlib.pyplot as plt
    print("✓ Matplotlib imported successfully")
    
    import numpy as np
    print("✓ NumPy imported successfully")
    
    from views.enhanced_main_window import EnhancedMainWindow
    print("✓ Enhanced main window imported successfully")
    
    from views.components.visualization_panel import VisualizationPanel, StatisticsPanel
    print("✓ Visualization components imported successfully")
    
    from views.components.splash_screen import SplashScreen, AboutDialog
    print("✓ Splash screen components imported successfully")
    
    print("\n✅ All imports successful!")
    print("\nTo run the enhanced application, use: python main.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPlease install missing dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)