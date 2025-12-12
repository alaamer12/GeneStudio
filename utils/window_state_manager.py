"""Window state management for GeneStudio Pro."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import tkinter as tk
from utils.platform_dirs import get_config_dir


class WindowStateManager:
    """Manages window state persistence and restoration."""
    
    def __init__(self, app_name: str = "GeneStudio"):
        self.app_name = app_name
        self.config_file = get_config_dir() / "window_state.json"
        self.default_state = {
            "geometry": "1400x900",
            "position": "center",
            "maximized": False,
            "minimized": False,
            "last_page": "dashboard"
        }
        
        # Minimum window dimensions
        self.min_width = 1200
        self.min_height = 700
    
    def save_window_state(self, window: tk.Tk) -> None:
        """Save current window state to file."""
        try:
            # Get current state
            geometry = window.geometry()
            state = window.state()
            
            window_state = {
                "geometry": geometry,
                "maximized": state == "zoomed",
                "minimized": state == "iconic",
                "last_saved": self._get_timestamp()
            }
            
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(window_state, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save window state: {e}")
    
    def restore_window_state(self, window: tk.Tk) -> None:
        """Restore window state from file."""
        try:
            # Load saved state
            saved_state = self._load_saved_state()
            
            # Set minimum size
            window.minsize(self.min_width, self.min_height)
            
            # Apply geometry
            geometry = saved_state.get("geometry", self.default_state["geometry"])
            
            # Validate and adjust geometry if needed
            geometry = self._validate_geometry(geometry)
            
            # Set geometry
            window.geometry(geometry)
            
            # Handle maximized state
            if saved_state.get("maximized", False):
                # Delay maximization to ensure proper restoration
                window.after(100, lambda: window.state("zoomed"))
            
            # Center window if no saved position or if centering is requested
            if saved_state.get("position") == "center" or not self._has_valid_position(geometry):
                window.after(100, lambda: self._center_window(window))
                
        except Exception as e:
            print(f"Failed to restore window state: {e}")
            # Fall back to default state
            self._apply_default_state(window)
    
    def _load_saved_state(self) -> Dict[str, Any]:
        """Load saved state from file."""
        if not self.config_file.exists():
            return self.default_state.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                saved_state = json.load(f)
                
            # Merge with defaults to handle missing keys
            state = self.default_state.copy()
            state.update(saved_state)
            return state
            
        except (json.JSONDecodeError, IOError):
            return self.default_state.copy()
    
    def _validate_geometry(self, geometry: str) -> str:
        """Validate and adjust geometry string."""
        try:
            # Parse geometry string (e.g., "1400x900+100+50")
            parts = geometry.replace('+', ' +').replace('-', ' -').split()
            size_part = parts[0]
            
            # Extract width and height
            width, height = map(int, size_part.split('x'))
            
            # Ensure minimum dimensions
            width = max(width, self.min_width)
            height = max(height, self.min_height)
            
            # Get screen dimensions
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            # Ensure window fits on screen
            width = min(width, screen_width - 100)
            height = min(height, screen_height - 100)
            
            # Reconstruct geometry string
            if len(parts) > 1:
                # Has position
                x_pos = parts[1] if len(parts) > 1 else "+100"
                y_pos = parts[2] if len(parts) > 2 else "+50"
                
                # Validate position
                x = int(x_pos.replace('+', '').replace('-', ''))
                y = int(y_pos.replace('+', '').replace('-', ''))
                
                # Ensure window is visible
                x = max(0, min(x, screen_width - width))
                y = max(0, min(y, screen_height - height))
                
                return f"{width}x{height}+{x}+{y}"
            else:
                return f"{width}x{height}"
                
        except (ValueError, IndexError):
            return f"{self.min_width}x{self.min_height}"
    
    def _has_valid_position(self, geometry: str) -> bool:
        """Check if geometry string has valid position."""
        return '+' in geometry or '-' in geometry
    
    def _center_window(self, window: tk.Tk) -> None:
        """Center window on screen."""
        window.update_idletasks()
        
        # Get window dimensions
        width = window.winfo_width()
        height = window.winfo_height()
        
        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Calculate center position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set position
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _apply_default_state(self, window: tk.Tk) -> None:
        """Apply default window state."""
        window.minsize(self.min_width, self.min_height)
        window.geometry(self.default_state["geometry"])
        # Always center on first startup
        window.after(100, lambda: self._center_window(window))
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_last_page(self) -> str:
        """Get the last active page."""
        saved_state = self._load_saved_state()
        return saved_state.get("last_page", self.default_state["last_page"])
    
    def save_last_page(self, page_name: str) -> None:
        """Save the last active page."""
        try:
            saved_state = self._load_saved_state()
            saved_state["last_page"] = page_name
            
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(saved_state, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save last page: {e}")
    
    def setup_window_callbacks(self, window: tk.Tk) -> None:
        """Set up window event callbacks for automatic state saving."""
        def on_configure(event):
            # Only save if the event is for the main window
            if event.widget == window:
                # Debounce rapid configure events
                if hasattr(window, '_configure_timer'):
                    window.after_cancel(window._configure_timer)
                window._configure_timer = window.after(500, lambda: self.save_window_state(window))
        
        def on_closing():
            self.save_window_state(window)
            window.quit()
        
        # Bind events
        window.bind("<Configure>", on_configure)
        window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Save state periodically
        def periodic_save():
            self.save_window_state(window)
            window.after(30000, periodic_save)  # Save every 30 seconds
        
        window.after(30000, periodic_save)