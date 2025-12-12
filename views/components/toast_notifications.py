"""Toast notification system with auto-dismiss and manual dismiss."""

import customtkinter as ctk
import threading
import time
from typing import Optional, List, Callable
from enum import Enum
from utils.theme_manager import get_theme_manager


class ToastType(Enum):
    """Toast notification types."""
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


class Toast(ctk.CTkFrame):
    """Individual toast notification."""
    
    def __init__(self, parent, message: str, toast_type: ToastType, 
                 duration: Optional[int] = None, on_close: Optional[Callable] = None,
                 width: int = 320, height: int = 80):
        super().__init__(parent, corner_radius=8, width=width, height=height)
        
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
        """Configure toast appearance using theme manager."""
        theme = get_theme_manager()
        
        # Get toast configuration from theme manager
        toast_type_map = {
            ToastType.SUCCESS: 'success',
            ToastType.ERROR: 'error',
            ToastType.INFO: 'info',
            ToastType.WARNING: 'warning'
        }
        
        toast_type_str = toast_type_map.get(self.toast_type, 'info')
        self.toast_config = theme.get_toast_config(toast_type_str)
        
        # Configure with theme styling
        self.configure(
            fg_color=self.toast_config['background_color'],
            border_width=1,
            border_color=self.toast_config['border_color'],
            corner_radius=self.toast_config['border_radius']
        )
    
    def _create_content(self):
        """Create toast content using theme manager."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Icon symbols
        icons = {
            ToastType.SUCCESS: "✓",
            ToastType.ERROR: "✗", 
            ToastType.INFO: "ℹ",
            ToastType.WARNING: "⚠"
        }
        
        # Circular icon with themed colored background
        icon_frame = ctk.CTkFrame(
            self,
            width=28,
            height=28,
            fg_color=self.toast_config['icon_color'],
            corner_radius=14
        )
        icon_frame.grid(row=0, column=0, padx=(self.toast_config['spacing'], 12), pady=self.toast_config['spacing'], sticky="w")
        icon_frame.grid_propagate(False)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icons.get(self.toast_type, "ℹ"),
            font=(self.toast_config['font'][0], 12, "bold"),
            text_color="white"
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Message with themed typography
        self.message_label = ctk.CTkLabel(
            self,
            text=self.message,
            font=self.toast_config['font'],
            text_color=self.toast_config['text_color'],
            wraplength=220,
            justify="left",
            anchor="w"
        )
        self.message_label.grid(row=0, column=1, padx=(0, 12), pady=self.toast_config['spacing'], sticky="ew")
        
        # Close button with themed styling
        close_button = ctk.CTkButton(
            self,
            text="×",
            font=(self.toast_config['font'][0], 16, "bold"),
            text_color=("gray40", "gray60"),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            width=20,
            height=20,
            corner_radius=10,
            command=self.close
        )
        close_button.grid(row=0, column=2, padx=(0, self.toast_config['spacing']), pady=self.toast_config['spacing'], sticky="e")
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        self.configure(border_color=("gray60", "gray50"))
        # Pause auto-dismiss on hover
        if self.auto_dismiss_timer:
            self.pause_auto_dismiss()
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        self.configure(border_color=("gray70", "gray40"))
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
        """Animate toast sliding in from right with smooth easing."""
        def animate():
            steps = 15
            duration_ms = 200
            step_delay = duration_ms // steps
            
            for i in range(steps + 1):
                # Ease-out animation curve
                progress = i / steps
                eased_progress = 1 - (1 - progress) ** 3  # Cubic ease-out
                
                new_x = self.current_x + (self.target_x - self.current_x) * eased_progress
                
                self.after(i * step_delay, lambda x=new_x: self.place(x=x))
        
        threading.Thread(target=animate, daemon=True).start()
    
    def animate_out(self, callback: Optional[Callable] = None):
        """Animate toast sliding out to right with smooth easing."""
        def animate():
            steps = 12
            duration_ms = 150
            step_delay = duration_ms // steps
            slide_distance = 350
            
            start_x = self.winfo_x()
            
            for i in range(steps + 1):
                # Ease-in animation curve
                progress = i / steps
                eased_progress = progress ** 2  # Quadratic ease-in
                
                new_x = start_x + (slide_distance * eased_progress)
                
                self.after(i * step_delay, lambda x=new_x: self.place(x=x))
            
            # Call callback after animation
            if callback:
                self.after(duration_ms + 10, callback)
        
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
        toast_width = 320
        toast_height = 80
        
        toast = Toast(
            self.container,
            message=message,
            toast_type=toast_type,
            duration=duration,
            on_close=self._on_toast_close,
            width=toast_width,
            height=toast_height
        )
        
        # Position toast
        self._position_toast(toast)
        
        # Add to list
        self.toasts.append(toast)
        
        return toast
    
    def _position_toast(self, toast: Toast):
        """Position toast in the container (bottom-right corner)."""
        # Toast dimensions
        toast_height = 80
        toast_width = 320
        margin = 20
        spacing = 10
        
        # Get container dimensions
        self.container.update_idletasks()  # Ensure accurate dimensions
        container_width = self.container.winfo_width()
        container_height = self.container.winfo_height()
        
        # Ensure minimum container size for toast visibility
        if container_width < toast_width + (margin * 2):
            container_width = toast_width + (margin * 2)
        if container_height < toast_height + (margin * 2):
            container_height = toast_height + (margin * 2)
        
        # Calculate position (bottom-right corner with upward stacking)
        x = container_width - toast_width - margin
        y = container_height - margin - toast_height - (len(self.toasts) * (toast_height + spacing))
        
        # Ensure toast stays within bounds
        x = max(margin, min(x, container_width - toast_width - margin))
        y = max(margin, min(y, container_height - toast_height - margin))
        
        # Place toast
        toast.place(x=x, y=y)
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
        toast_width = 320
        margin = 20
        spacing = 10
        
        self.container.update_idletasks()
        container_width = self.container.winfo_width()
        container_height = self.container.winfo_height()
        
        # Reposition all remaining toasts
        for i, toast in enumerate(self.toasts):
            x = container_width - toast_width - margin
            y = container_height - margin - toast_height - (i * (toast_height + spacing))
            
            # Ensure toast stays within bounds
            x = max(margin, min(x, container_width - toast_width - margin))
            y = max(margin, min(y, container_height - toast_height - margin))
            
            # Animate to new position
            toast.place(x=x, y=y)
    
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