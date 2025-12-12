"""Toast notification system with auto-dismiss and manual dismiss."""

import customtkinter as ctk
import threading
import time
from typing import Optional, List, Callable
from enum import Enum


class ToastType(Enum):
    """Toast notification types."""
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


class Toast(ctk.CTkFrame):
    """Individual toast notification."""
    
    def __init__(self, parent, message: str, toast_type: ToastType, 
                 duration: Optional[int] = None, on_close: Optional[Callable] = None):
        super().__init__(parent, corner_radius=8)
        
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        self.on_close = on_close
        self.auto_dismiss_timer = None
        
        # Configure appearance based on type
        self._configure_appearance()
        
        # Create content
        self._create_content()
        
        # Start auto-dismiss timer if duration is set
        if duration and duration > 0:
            self.start_auto_dismiss()
        
        # Animation properties
        self.target_x = 0
        self.current_x = 300  # Start off-screen
        self.animate_in()
    
    def _configure_appearance(self):
        """Configure toast appearance based on type."""
        colors = {
            ToastType.SUCCESS: {"bg": "#2fa572", "hover": "#268a5f"},
            ToastType.ERROR: {"bg": "#d42f2f", "hover": "#b02525"},
            ToastType.INFO: {"bg": "#1f6aa5", "hover": "#1a5a8a"},
            ToastType.WARNING: {"bg": "#ffa500", "hover": "#e6940a"}
        }
        
        color_config = colors.get(self.toast_type, colors[ToastType.INFO])
        self.configure(fg_color=color_config["bg"])
        
        # Store colors for hover effects
        self.bg_color = color_config["bg"]
        self.hover_color = color_config["hover"]
    
    def _create_content(self):
        """Create toast content."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Icon
        icons = {
            ToastType.SUCCESS: "✓",
            ToastType.ERROR: "✗",
            ToastType.INFO: "ℹ",
            ToastType.WARNING: "⚠"
        }
        
        icon_label = ctk.CTkLabel(
            self,
            text=icons.get(self.toast_type, "ℹ"),
            font=("Arial", 16, "bold"),
            text_color="white",
            width=30
        )
        icon_label.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="w")
        
        # Message
        self.message_label = ctk.CTkLabel(
            self,
            text=self.message,
            font=("Arial", 12),
            text_color="white",
            wraplength=250,
            justify="left"
        )
        self.message_label.grid(row=0, column=1, padx=(5, 10), pady=15, sticky="ew")
        
        # Close button
        close_button = ctk.CTkButton(
            self,
            text="×",
            font=("Arial", 16, "bold"),
            text_color="white",
            fg_color="transparent",
            hover_color=self.hover_color,
            width=30,
            height=30,
            command=self.close
        )
        close_button.grid(row=0, column=2, padx=(5, 10), pady=15, sticky="e")
        
        # Bind hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        self.configure(fg_color=self.hover_color)
        # Pause auto-dismiss on hover
        if self.auto_dismiss_timer:
            self.pause_auto_dismiss()
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        self.configure(fg_color=self.bg_color)
        # Resume auto-dismiss after hover
        if self.duration and self.duration > 0:
            self.start_auto_dismiss()
    
    def start_auto_dismiss(self):
        """Start auto-dismiss timer."""
        if self.auto_dismiss_timer:
            self.auto_dismiss_timer.cancel()
        
        self.auto_dismiss_timer = threading.Timer(self.duration / 1000.0, self.close)
        self.auto_dismiss_timer.start()
    
    def pause_auto_dismiss(self):
        """Pause auto-dismiss timer."""
        if self.auto_dismiss_timer:
            self.auto_dismiss_timer.cancel()
            self.auto_dismiss_timer = None
    
    def animate_in(self):
        """Animate toast sliding in from right."""
        def animate():
            steps = 20
            step_size = (self.current_x - self.target_x) / steps
            
            for i in range(steps):
                self.current_x -= step_size
                self.after(i * 10, lambda x=self.current_x: self.place(x=x))
        
        threading.Thread(target=animate, daemon=True).start()
    
    def animate_out(self, callback: Optional[Callable] = None):
        """Animate toast sliding out to right."""
        def animate():
            steps = 15
            step_size = 300 / steps
            
            for i in range(steps):
                new_x = self.current_x + step_size
                self.after(i * 8, lambda x=new_x: self.place(x=x))
                self.current_x = new_x
            
            # Call callback after animation
            if callback:
                self.after(steps * 8, callback)
        
        threading.Thread(target=animate, daemon=True).start()
    
    def close(self):
        """Close the toast with animation."""
        # Cancel auto-dismiss timer
        if self.auto_dismiss_timer:
            self.auto_dismiss_timer.cancel()
        
        # Animate out and then destroy
        self.animate_out(self._destroy_after_animation)
    
    def _destroy_after_animation(self):
        """Destroy toast after animation completes."""
        if self.on_close:
            self.on_close(self)
        self.destroy()


class ToastManager:
    """Singleton manager for toast notifications."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.toasts: List[Toast] = []
            self.container = None
            self.max_toasts = 5
            self._initialized = True
    
    def set_container(self, container):
        """Set the container for toast notifications."""
        self.container = container
    
    def show_toast(self, message: str, toast_type: ToastType, 
                   duration: Optional[int] = None) -> Toast:
        """Show a toast notification."""
        if not self.container:
            raise RuntimeError("Toast container not set. Call set_container() first.")
        
        # Set default duration based on type
        if duration is None:
            if toast_type in [ToastType.SUCCESS, ToastType.INFO]:
                duration = 3000  # 3 seconds
            else:  # ERROR, WARNING
                duration = 0  # Manual dismiss only
        
        # Remove oldest toast if at max capacity
        if len(self.toasts) >= self.max_toasts:
            oldest_toast = self.toasts[0]
            oldest_toast.close()
        
        # Create new toast
        toast = Toast(
            self.container,
            message=message,
            toast_type=toast_type,
            duration=duration,
            on_close=self._on_toast_close
        )
        
        # Position toast
        self._position_toast(toast)
        
        # Add to list
        self.toasts.append(toast)
        
        return toast
    
    def _position_toast(self, toast: Toast):
        """Position toast in the container."""
        # Calculate position (bottom-right corner with stacking)
        toast_height = 80
        toast_width = 320
        margin = 20
        
        # Get container dimensions
        container_width = self.container.winfo_width()
        container_height = self.container.winfo_height()
        
        # Calculate position
        x = container_width - toast_width - margin
        y = container_height - margin - (len(self.toasts) * (toast_height + 10))
        
        # Place toast
        toast.place(x=x, y=y, width=toast_width, height=toast_height)
        toast.target_x = x
    
    def _on_toast_close(self, toast: Toast):
        """Handle toast close event."""
        if toast in self.toasts:
            self.toasts.remove(toast)
            # Reposition remaining toasts
            self._reposition_toasts()
    
    def _reposition_toasts(self):
        """Reposition remaining toasts after one is closed."""
        toast_height = 80
        margin = 20
        
        container_height = self.container.winfo_height()
        
        for i, toast in enumerate(self.toasts):
            new_y = container_height - margin - ((i + 1) * (toast_height + 10))
            toast.place(y=new_y)
    
    def clear_all(self):
        """Clear all toast notifications."""
        for toast in self.toasts.copy():
            toast.close()
    
    def show_success(self, message: str, duration: int = 3000) -> Toast:
        """Show success toast."""
        return self.show_toast(message, ToastType.SUCCESS, duration)
    
    def show_error(self, message: str) -> Toast:
        """Show error toast (manual dismiss)."""
        return self.show_toast(message, ToastType.ERROR, duration=0)
    
    def show_info(self, message: str, duration: int = 5000) -> Toast:
        """Show info toast."""
        return self.show_toast(message, ToastType.INFO, duration)
    
    def show_warning(self, message: str) -> Toast:
        """Show warning toast (manual dismiss)."""
        return self.show_toast(message, ToastType.WARNING, duration=0)


# Global toast manager instance
_toast_manager = ToastManager()


def set_toast_container(container):
    """Set the container for toast notifications."""
    _toast_manager.set_container(container)


def show_success(message: str, duration: int = 3000) -> Toast:
    """Show success toast notification."""
    return _toast_manager.show_success(message, duration)


def show_error(message: str) -> Toast:
    """Show error toast notification."""
    return _toast_manager.show_error(message)


def show_info(message: str, duration: int = 5000) -> Toast:
    """Show info toast notification."""
    return _toast_manager.show_info(message, duration)


def show_warning(message: str) -> Toast:
    """Show warning toast notification."""
    return _toast_manager.show_warning(message)


def clear_all_toasts():
    """Clear all toast notifications."""
    _toast_manager.clear_all()