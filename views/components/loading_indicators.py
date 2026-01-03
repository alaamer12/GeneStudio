"""Loading indicators for operation feedback."""

import customtkinter as ctk
import threading
import time
import math
from typing import Optional, Callable


class LinearProgress(ctk.CTkProgressBar):
    """Enhanced progress bar for determinate and indeterminate operations."""
    
    def __init__(self, parent, mode: str = "determinate", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.mode = mode
        self.indeterminate_active = False
        self.indeterminate_position = 0.0
        self.animation_thread = None
        
        # Configure appearance
        self.configure(
            progress_color="#1f6aa5",
            fg_color="#2b2b2b",
            height=6
        )
        
        if mode == "indeterminate":
            self.start_indeterminate()
    
    def set_mode(self, mode: str):
        """Change the progress bar mode."""
        if self.mode == "indeterminate" and mode == "determinate":
            self.stop_indeterminate()
        elif self.mode == "determinate" and mode == "indeterminate":
            self.start_indeterminate()
        
        self.mode = mode
    
    def start_indeterminate(self):
        """Start indeterminate animation."""
        if not self.indeterminate_active:
            self.indeterminate_active = True
            self.animation_thread = threading.Thread(target=self._animate_indeterminate, daemon=True)
            self.animation_thread.start()
    
    def stop_indeterminate(self):
        """Stop indeterminate animation."""
        self.indeterminate_active = False
        self.set(0)
    
    def _animate_indeterminate(self):
        """Animate indeterminate progress."""
        while self.indeterminate_active:
            try:
                # Create a wave-like animation
                self.indeterminate_position += 0.02
                if self.indeterminate_position > 2 * math.pi:
                    self.indeterminate_position = 0
                
                # Calculate progress value (0.0 to 1.0)
                progress = (math.sin(self.indeterminate_position) + 1) / 2
                progress = max(0.1, progress * 0.8)  # Keep it visible
                
                # Update on main thread
                self.after(0, lambda p=progress: self.set(p))
                
                time.sleep(0.05)
                
            except Exception:
                break
    
    def set_progress(self, value: float, text: Optional[str] = None):
        """Set progress value with optional text update."""
        if self.mode == "determinate":
            self.set(max(0.0, min(1.0, value)))
    
    def destroy(self):
        """Clean up animation when destroying."""
        self.stop_indeterminate()
        super().destroy()


class CircularProgress(ctk.CTkFrame):
    """Circular progress indicator."""
    
    def __init__(self, parent, size: int = 40, **kwargs):
        super().__init__(parent, width=size, height=size, fg_color="transparent", **kwargs)
        
        self.size = size
        self.active = False
        self.angle = 0
        self.animation_thread = None
        
        # Create canvas for drawing
        self.canvas = ctk.CTkCanvas(
            self,
            width=size,
            height=size,
            bg=self._get_appearance_mode_color(),
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Bind appearance mode changes
        self.bind("<Configure>", self._on_configure)
    
    def _get_appearance_mode_color(self) -> str:
        """Get background color based on appearance mode."""
        if ctk.get_appearance_mode() == "Dark":
            return "#212121"
        else:
            return "#f0f0f0"
    
    def _on_configure(self, event):
        """Handle configuration changes."""
        self.canvas.configure(bg=self._get_appearance_mode_color())
    
    def start(self):
        """Start the circular animation."""
        if not self.active:
            self.active = True
            self.animation_thread = threading.Thread(target=self._animate, daemon=True)
            self.animation_thread.start()
    
    def stop(self):
        """Stop the circular animation."""
        self.active = False
        self.canvas.delete("all")
    
    def _animate(self):
        """Animate the circular progress."""
        while self.active:
            try:
                self.angle += 10
                if self.angle >= 360:
                    self.angle = 0
                
                # Update on main thread
                self.after(0, self._draw_spinner)
                
                time.sleep(0.05)
                
            except Exception:
                break
    
    def _draw_spinner(self):
        """Draw the spinning indicator."""
        self.canvas.delete("all")
        
        center = self.size // 2
        radius = center - 5
        
        # Draw multiple arcs for spinner effect
        for i in range(8):
            start_angle = self.angle + (i * 45)
            opacity = 1.0 - (i * 0.1)
            
            # Calculate color with opacity
            color = f"#{int(31 * opacity):02x}{int(106 * opacity):02x}{int(165 * opacity):02x}"
            
            self.canvas.create_arc(
                center - radius, center - radius,
                center + radius, center + radius,
                start=start_angle, extent=30,
                outline=color, width=3,
                style="arc"
            )
    
    def destroy(self):
        """Clean up animation when destroying."""
        self.stop()
        super().destroy()


class LoadingOverlay(ctk.CTkFrame):
    """Full-page loading overlay with cancellation support."""
    
    def __init__(self, parent, message: str = "Loading...", 
                 cancellable: bool = False, on_cancel: Optional[Callable] = None, **kwargs):
        super().__init__(parent, fg_color=("gray90", "gray10"), **kwargs)
        
        self.message = message
        self.cancellable = cancellable
        self.on_cancel = on_cancel
        
        # Configure overlay
        self.configure(corner_radius=0)
        
        # Create content
        self._create_content()
        
        # Make overlay modal
        self.grab_set()
        self.focus_set()
    
    def _create_content(self):
        """Create overlay content."""
        # Center container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Spinner
        self.spinner = CircularProgress(container, size=60)
        self.spinner.pack(pady=(0, 20))
        self.spinner.start()
        
        # Message
        self.message_label = ctk.CTkLabel(
            container,
            text=self.message,
            font=("Arial", 16)
        )
        self.message_label.pack(pady=(0, 20))
        
        # Cancel button (if cancellable)
        if self.cancellable and self.on_cancel:
            self.cancel_button = ctk.CTkButton(
                container,
                text="Cancel",
                command=self._handle_cancel,
                fg_color="#d42f2f",
                hover_color="#b02525"
            )
            self.cancel_button.pack()
    
    def _handle_cancel(self):
        """Handle cancel button click."""
        if self.on_cancel:
            self.on_cancel()
        self.close()
    
    def update_message(self, message: str):
        """Update the loading message."""
        self.message = message
        self.message_label.configure(text=message)
    
    def close(self):
        """Close the loading overlay."""
        self.spinner.stop()
        self.grab_release()
        self.destroy()
    
    def destroy(self):
        """Clean up when destroying."""
        if hasattr(self, 'spinner'):
            self.spinner.stop()
        super().destroy()


class ProgressDialog(ctk.CTkToplevel):
    """Progress dialog for long-running operations."""
    
    def __init__(self, parent, title: str = "Progress", message: str = "Processing...",
                 cancellable: bool = False, on_cancel: Optional[Callable] = None):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.after(10, self._center_dialog)
        
        self.message = message
        self.cancellable = cancellable
        self.on_cancel = on_cancel
        self.cancelled = False
        
        # Create content
        self._create_content()
    
    def _center_dialog(self):
        """Center dialog on parent window."""
        self.update_idletasks()
        
        # Get parent window position and size
        parent = self.master
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calculate center position
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_content(self):
        """Create dialog content."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Message
        self.message_label = ctk.CTkLabel(
            main_frame,
            text=self.message,
            font=("Arial", 14),
            wraplength=350
        )
        self.message_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress_bar = LinearProgress(main_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        if self.cancellable and self.on_cancel:
            # Cancel button
            self.cancel_button = ctk.CTkButton(
                buttons_frame,
                text="Cancel",
                command=self._handle_cancel,
                fg_color="#d42f2f",
                hover_color="#b02525"
            )
            self.cancel_button.pack(side="right")
    
    def _handle_cancel(self):
        """Handle cancel button click."""
        self.cancelled = True
        if self.on_cancel:
            self.on_cancel()
        self.close()
    
    def update_progress(self, value: float, message: Optional[str] = None):
        """Update progress value and optional message."""
        self.progress_bar.set_mode("determinate")
        self.progress_bar.set_progress(value)
        
        if message:
            self.update_message(message)
    
    def update_message(self, message: str):
        """Update the progress message."""
        self.message = message
        self.message_label.configure(text=message)
    
    def set_indeterminate(self, message: Optional[str] = None):
        """Set progress to indeterminate mode."""
        self.progress_bar.set_mode("indeterminate")
        
        if message:
            self.update_message(message)
    
    def close(self):
        """Close the progress dialog."""
        self.grab_release()
        self.destroy()
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self.cancelled