"""Modal dialog components."""

import customtkinter as ctk


class Modal(ctk.CTkToplevel):
    """Base modal dialog."""
    
    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
    def close(self):
        """Close the modal."""
        self.grab_release()
        self.destroy()


class ConfirmDialog(Modal):
    """Confirmation dialog."""
    
    def __init__(self, parent, title: str, message: str, on_confirm=None):
        super().__init__(parent, title, 400, 200)
        
        self.on_confirm = on_confirm
        
        # Message
        ctk.CTkLabel(
            self.content_frame,
            text=message,
            wraplength=350,
            font=("Arial", 12)
        ).pack(pady=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.close,
            fg_color="gray"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Confirm",
            command=self._confirm
        ).pack(side="left", padx=5)
        
    def _confirm(self):
        """Handle confirmation."""
        if self.on_confirm:
            self.on_confirm()
        self.close()


class InputDialog(Modal):
    """Input dialog for getting user input."""
    
    def __init__(self, parent, title: str, prompt: str, on_submit=None):
        super().__init__(parent, title, 400, 250)
        
        self.on_submit = on_submit
        
        # Prompt
        ctk.CTkLabel(
            self.content_frame,
            text=prompt,
            font=("Arial", 12)
        ).pack(pady=10)
        
        # Input
        self.entry = ctk.CTkEntry(self.content_frame, width=300)
        self.entry.pack(pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.close,
            fg_color="gray"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Submit",
            command=self._submit
        ).pack(side="left", padx=5)
        
    def _submit(self):
        """Handle submission."""
        if self.on_submit:
            self.on_submit(self.entry.get())
        self.close()


class ProgressDialog(Modal):
    """Progress dialog with progress bar."""
    
    def __init__(self, parent, title: str, message: str):
        super().__init__(parent, title, 400, 200)
        
        # Message
        ctk.CTkLabel(
            self.content_frame,
            text=message,
            font=("Arial", 12)
        ).pack(pady=20)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.content_frame, width=300)
        self.progress.pack(pady=20)
        self.progress.set(0)
        
    def update_progress(self, value: float):
        """Update progress (0.0 to 1.0)."""
        self.progress.set(value)
        self.update()
