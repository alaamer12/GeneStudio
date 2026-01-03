"""Confirmation dialogs for destructive actions."""

import customtkinter as ctk
from typing import Optional, Callable, Any


class ConfirmDialog(ctk.CTkToplevel):
    """Standard confirmation dialog."""
    
    def __init__(self, parent, title: str = "Confirm Action", 
                 message: str = "Are you sure you want to continue?",
                 confirm_text: str = "Confirm", cancel_text: str = "Cancel",
                 on_confirm: Optional[Callable] = None, 
                 on_cancel: Optional[Callable] = None,
                 destructive: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center dialog
        self.after(10, self._center_dialog)
        
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.destructive = destructive
        self.result = None
        
        # Create content
        self._create_content()
        
        # Bind keyboard shortcuts
        self.bind("<Return>", lambda e: self._handle_confirm())
        self.bind("<Escape>", lambda e: self._handle_cancel())
        
        # Focus on appropriate button
        self.after(100, self._set_focus)
    
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
        
        # Icon and message frame
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Icon
        icon = "⚠️" if self.destructive else "❓"
        icon_label = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=("Arial", 32)
        )
        icon_label.pack(pady=(10, 15))
        
        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text=self.message,
            font=("Arial", 14),
            wraplength=350,
            justify="center"
        )
        message_label.pack(pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            buttons_frame,
            text=self.cancel_text,
            command=self._handle_cancel,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            border_color=("gray70", "gray30"),
            width=100
        )
        self.cancel_button.pack(side="right", padx=(10, 0))
        
        # Confirm button
        confirm_color = "#d42f2f" if self.destructive else "#1f6aa5"
        confirm_hover = "#b02525" if self.destructive else "#1a5a8a"
        
        self.confirm_button = ctk.CTkButton(
            buttons_frame,
            text=self.confirm_text,
            command=self._handle_confirm,
            fg_color=confirm_color,
            hover_color=confirm_hover,
            width=100
        )
        self.confirm_button.pack(side="right")
    
    def _set_focus(self):
        """Set focus on appropriate button."""
        if self.destructive:
            # Focus cancel button for destructive actions
            self.cancel_button.focus_set()
        else:
            # Focus confirm button for non-destructive actions
            self.confirm_button.focus_set()
    
    def _handle_confirm(self):
        """Handle confirm button click."""
        self.result = True
        if self.on_confirm:
            self.on_confirm()
        self.grab_release()
        self.destroy()
    
    def _handle_cancel(self):
        """Handle cancel button click."""
        self.result = False
        if self.on_cancel:
            self.on_cancel()
        self.grab_release()
        self.destroy()
    
    def get_result(self) -> Optional[bool]:
        """Get the dialog result."""
        return self.result


class DestructiveActionDialog(ConfirmDialog):
    """Specialized dialog for destructive actions."""
    
    def __init__(self, parent, title: str = "Delete Item", 
                 message: str = "This action cannot be undone.",
                 item_name: Optional[str] = None,
                 confirm_text: str = "Delete", 
                 on_confirm: Optional[Callable] = None, **kwargs):
        
        # Customize message if item name provided
        if item_name:
            message = f"Are you sure you want to delete '{item_name}'? {message}"
        
        super().__init__(
            parent,
            title=title,
            message=message,
            confirm_text=confirm_text,
            cancel_text="Cancel",
            on_confirm=on_confirm,
            destructive=True,
            **kwargs
        )


class SaveChangesDialog(ConfirmDialog):
    """Dialog for unsaved changes confirmation."""
    
    def __init__(self, parent, filename: Optional[str] = None,
                 on_save: Optional[Callable] = None,
                 on_dont_save: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None, **kwargs):
        
        # Customize message based on filename
        if filename:
            message = f"Do you want to save changes to '{filename}'?"
        else:
            message = "Do you want to save your changes?"
        
        super().__init__(
            parent,
            title="Save Changes?",
            message=f"{message}\nYour changes will be lost if you don't save them.",
            confirm_text="Save",
            cancel_text="Cancel",
            on_confirm=on_save,
            on_cancel=on_cancel,
            **kwargs
        )
        
        # Add "Don't Save" button
        self.on_dont_save = on_dont_save
        self._add_dont_save_button()
    
    def _add_dont_save_button(self):
        """Add 'Don't Save' button to the dialog."""
        # Find buttons frame
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkFrame) and child.cget("fg_color") == "transparent":
                        buttons_frame = child
                        break
                break
        
        # Add "Don't Save" button
        dont_save_button = ctk.CTkButton(
            buttons_frame,
            text="Don't Save",
            command=self._handle_dont_save,
            fg_color="#ffa500",
            hover_color="#e6940a",
            width=100
        )
        dont_save_button.pack(side="right", padx=(0, 10))
    
    def _handle_dont_save(self):
        """Handle 'Don't Save' button click."""
        self.result = "dont_save"
        if self.on_dont_save:
            self.on_dont_save()
        self.grab_release()
        self.destroy()


class InputDialog(ctk.CTkToplevel):
    """Dialog for text input with validation."""
    
    def __init__(self, parent, title: str = "Input Required",
                 message: str = "Please enter a value:",
                 default_value: str = "",
                 placeholder: str = "",
                 validator: Optional[Callable[[str], tuple[bool, str]]] = None,
                 on_confirm: Optional[Callable[[str], None]] = None,
                 on_cancel: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title(title)
        self.geometry("400x250")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center dialog
        self.after(10, self._center_dialog)
        
        self.message = message
        self.default_value = default_value
        self.placeholder = placeholder
        self.validator = validator
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.result = None
        
        # Create content
        self._create_content()
        
        # Bind keyboard shortcuts
        self.bind("<Return>", lambda e: self._handle_confirm())
        self.bind("<Escape>", lambda e: self._handle_cancel())
        
        # Focus input field
        self.after(100, lambda: self.input_entry.focus_set())
    
    def _center_dialog(self):
        """Center dialog on parent window."""
        self.update_idletasks()
        
        parent = self.master
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
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
        message_label = ctk.CTkLabel(
            main_frame,
            text=self.message,
            font=("Arial", 14),
            wraplength=350,
            justify="left"
        )
        message_label.pack(anchor="w", pady=(0, 15))
        
        # Input field
        self.input_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text=self.placeholder,
            font=("Arial", 12),
            height=35
        )
        self.input_entry.pack(fill="x", pady=(0, 10))
        
        # Set default value
        if self.default_value:
            self.input_entry.insert(0, self.default_value)
            self.input_entry.select_range(0, "end")
        
        # Error label (initially hidden)
        self.error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=("Arial", 11),
            text_color="#d42f2f"
        )
        self.error_label.pack(anchor="w", pady=(0, 15))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self._handle_cancel,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            border_color=("gray70", "gray30"),
            width=100
        )
        cancel_button.pack(side="right", padx=(10, 0))
        
        # Confirm button
        self.confirm_button = ctk.CTkButton(
            buttons_frame,
            text="OK",
            command=self._handle_confirm,
            fg_color="#1f6aa5",
            hover_color="#1a5a8a",
            width=100
        )
        self.confirm_button.pack(side="right")
    
    def _validate_input(self, value: str) -> tuple[bool, str]:
        """Validate input value."""
        if self.validator:
            return self.validator(value)
        return True, ""
    
    def _handle_confirm(self):
        """Handle confirm button click."""
        value = self.input_entry.get().strip()
        
        # Validate input
        is_valid, error_message = self._validate_input(value)
        
        if not is_valid:
            # Show error
            self.error_label.configure(text=error_message)
            self.input_entry.focus_set()
            return
        
        # Clear error
        self.error_label.configure(text="")
        
        # Set result and close
        self.result = value
        if self.on_confirm:
            self.on_confirm(value)
        self.grab_release()
        self.destroy()
    
    def _handle_cancel(self):
        """Handle cancel button click."""
        self.result = None
        if self.on_cancel:
            self.on_cancel()
        self.grab_release()
        self.destroy()
    
    def get_result(self) -> Optional[str]:
        """Get the input result."""
        return self.result


def show_confirm_dialog(parent, title: str = "Confirm Action",
                       message: str = "Are you sure?",
                       confirm_text: str = "Confirm",
                       cancel_text: str = "Cancel") -> bool:
    """Show a confirmation dialog and return the result."""
    result = [False]  # Use list to allow modification in nested function
    
    def on_confirm():
        result[0] = True
    
    dialog = ConfirmDialog(
        parent,
        title=title,
        message=message,
        confirm_text=confirm_text,
        cancel_text=cancel_text,
        on_confirm=on_confirm
    )
    
    # Wait for dialog to close
    parent.wait_window(dialog)
    
    return result[0]


def show_destructive_dialog(parent, title: str = "Delete Item",
                           message: str = "This action cannot be undone.",
                           item_name: Optional[str] = None) -> bool:
    """Show a destructive action dialog and return the result."""
    result = [False]
    
    def on_confirm():
        result[0] = True
    
    dialog = DestructiveActionDialog(
        parent,
        title=title,
        message=message,
        item_name=item_name,
        on_confirm=on_confirm
    )
    
    parent.wait_window(dialog)
    return result[0]


def show_input_dialog(parent, title: str = "Input Required",
                     message: str = "Please enter a value:",
                     default_value: str = "",
                     placeholder: str = "",
                     validator: Optional[Callable[[str], tuple[bool, str]]] = None) -> Optional[str]:
    """Show an input dialog and return the result."""
    result = [None]
    
    def on_confirm(value: str):
        result[0] = value
    
    dialog = InputDialog(
        parent,
        title=title,
        message=message,
        default_value=default_value,
        placeholder=placeholder,
        validator=validator,
        on_confirm=on_confirm
    )
    
    parent.wait_window(dialog)
    return result[0]