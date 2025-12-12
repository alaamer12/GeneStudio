"""Error boundary component with retry functionality."""

import customtkinter as ctk
import traceback
from typing import Callable, Optional, Any
from utils.logger import get_logger


class ErrorFallback(ctk.CTkFrame):
    """Fallback component displayed when an error occurs."""
    
    def __init__(self, parent, error: Exception, on_retry: Optional[Callable] = None, 
                 context: str = "component", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.error = error
        self.on_retry = on_retry
        self.context = context
        
        # Configure appearance
        self.configure(fg_color=("gray95", "gray15"), corner_radius=8)
        
        # Create error display
        self._create_error_display()
    
    def _create_error_display(self):
        """Create the error display interface."""
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Error icon
        icon_label = ctk.CTkLabel(
            container,
            text="⚠️",
            font=("Arial", 48)
        )
        icon_label.pack(pady=(0, 20))
        
        # Error title
        title_label = ctk.CTkLabel(
            container,
            text=f"Something went wrong in {self.context}",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Error message
        error_message = str(self.error) if str(self.error) else "An unexpected error occurred"
        message_label = ctk.CTkLabel(
            container,
            text=error_message,
            font=("Arial", 12),
            wraplength=400,
            justify="center"
        )
        message_label.pack(pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(pady=(10, 0))
        
        # Retry button (if retry function provided)
        if self.on_retry:
            retry_button = ctk.CTkButton(
                buttons_frame,
                text="Try Again",
                command=self._handle_retry,
                fg_color="#1f6aa5",
                hover_color="#1a5a8a"
            )
            retry_button.pack(side="left", padx=(0, 10))
        
        # Details button
        details_button = ctk.CTkButton(
            buttons_frame,
            text="Show Details",
            command=self._show_details,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            border_color=("gray70", "gray30")
        )
        details_button.pack(side="left")
    
    def _handle_retry(self):
        """Handle retry button click."""
        if self.on_retry:
            try:
                self.on_retry()
            except Exception as e:
                # If retry fails, update the error display
                self.error = e
                self._update_error_display()
    
    def _show_details(self):
        """Show detailed error information in a dialog."""
        ErrorDetailsDialog(self, self.error, self.context)
    
    def _update_error_display(self):
        """Update error display with new error information."""
        # Clear current content
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate error display
        self._create_error_display()


class ErrorDetailsDialog(ctk.CTkToplevel):
    """Dialog showing detailed error information."""
    
    def __init__(self, parent, error: Exception, context: str):
        super().__init__(parent)
        
        self.error = error
        self.context = context
        
        # Configure dialog
        self.title("Error Details")
        self.geometry("600x400")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Center dialog
        self.after(10, self._center_dialog)
        
        # Create content
        self._create_content()
    
    def _center_dialog(self):
        """Center dialog on parent."""
        self.update_idletasks()
        
        # Get parent position
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
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Error in {self.context}",
            font=("Arial", 16, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Error type
        error_type_label = ctk.CTkLabel(
            main_frame,
            text=f"Error Type: {type(self.error).__name__}",
            font=("Arial", 12, "bold")
        )
        error_type_label.pack(anchor="w", pady=(0, 5))
        
        # Error message
        error_msg_label = ctk.CTkLabel(
            main_frame,
            text=f"Message: {str(self.error)}",
            font=("Arial", 12),
            wraplength=550,
            justify="left"
        )
        error_msg_label.pack(anchor="w", pady=(0, 10))
        
        # Stack trace
        trace_label = ctk.CTkLabel(
            main_frame,
            text="Stack Trace:",
            font=("Arial", 12, "bold")
        )
        trace_label.pack(anchor="w", pady=(10, 5))
        
        # Stack trace text
        trace_text = ctk.CTkTextbox(
            main_frame,
            font=("Courier", 10),
            wrap="word"
        )
        trace_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Get stack trace
        stack_trace = ''.join(traceback.format_exception(
            type(self.error), self.error, self.error.__traceback__
        ))
        trace_text.insert("1.0", stack_trace)
        trace_text.configure(state="disabled")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Copy button
        copy_button = ctk.CTkButton(
            buttons_frame,
            text="Copy to Clipboard",
            command=self._copy_to_clipboard,
            fg_color="#1f6aa5",
            hover_color="#1a5a8a"
        )
        copy_button.pack(side="left")
        
        # Close button
        close_button = ctk.CTkButton(
            buttons_frame,
            text="Close",
            command=self.destroy,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            border_color=("gray70", "gray30")
        )
        close_button.pack(side="right")
    
    def _copy_to_clipboard(self):
        """Copy error details to clipboard."""
        error_details = f"""Error in {self.context}
Error Type: {type(self.error).__name__}
Message: {str(self.error)}

Stack Trace:
{''.join(traceback.format_exception(type(self.error), self.error, self.error.__traceback__))}"""
        
        self.clipboard_clear()
        self.clipboard_append(error_details)
        
        # Show confirmation (if toast system is available)
        try:
            from views.components.toast_notifications import show_success
            show_success("Error details copied to clipboard")
        except ImportError:
            pass


class ErrorBoundary:
    """Error boundary that catches and handles component errors gracefully."""
    
    def __init__(self, parent, content_func: Callable, fallback_func: Optional[Callable] = None,
                 on_retry: Optional[Callable] = None, context: str = "component"):
        self.parent = parent
        self.content_func = content_func
        self.fallback_func = fallback_func or self._default_fallback
        self.on_retry = on_retry
        self.context = context
        self.logger = get_logger(__name__)
        
        self.current_widget = None
        
        # Initial render
        self.render()
    
    def render(self):
        """Render the content or fallback on error."""
        # Clear current widget
        if self.current_widget:
            self.current_widget.destroy()
        
        try:
            # Try to render content
            self.current_widget = self.content_func()
            
        except Exception as e:
            # Log the error
            self.logger.error(f"Error in {self.context}: {e}", exc_info=True)
            
            # Render fallback
            self.current_widget = self.fallback_func(e)
    
    def _default_fallback(self, error: Exception):
        """Default fallback component."""
        return ErrorFallback(
            self.parent,
            error=error,
            on_retry=self._handle_retry,
            context=self.context
        )
    
    def _handle_retry(self):
        """Handle retry request."""
        if self.on_retry:
            try:
                # Call custom retry function
                self.on_retry()
            except Exception as e:
                self.logger.error(f"Retry failed in {self.context}: {e}", exc_info=True)
        
        # Re-render regardless of retry function
        self.render()
    
    def update_content(self, new_content_func: Callable):
        """Update the content function and re-render."""
        self.content_func = new_content_func
        self.render()
    
    def get_widget(self):
        """Get the current widget (content or fallback)."""
        return self.current_widget


def with_error_boundary(content_func: Callable, parent, context: str = "component",
                       on_retry: Optional[Callable] = None) -> Any:
    """Decorator/wrapper function to wrap content with error boundary."""
    boundary = ErrorBoundary(
        parent=parent,
        content_func=content_func,
        context=context,
        on_retry=on_retry
    )
    return boundary.get_widget()