"""Font settings panel component for user font preference configuration."""

import customtkinter as ctk
import tkinter.font as tkfont
from typing import Optional, Callable, List
from utils.theme_manager import get_theme_manager
from utils.themed_components import ThemedLabel, ThemedButton, ThemedFrame, ThemedOptionMenu
from utils.themed_tooltips import create_tooltip, create_validation_tooltip


class FontSettingsPanel(ThemedFrame):
    """Font settings panel with live preview and theme integration."""
    
    def __init__(self, parent, on_change: Optional[Callable] = None, **kwargs):
        """
        Initialize font settings panel.
        
        Args:
            parent: Parent widget
            on_change: Callback function called when settings change
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)
        
        self.on_change = on_change
        self._theme_manager = get_theme_manager()
        
        # Font configuration variables
        self.font_family_var = ctk.StringVar()
        self.font_size_var = ctk.StringVar()
        self.header_font_family_var = ctk.StringVar()
        self.header_font_size_var = ctk.StringVar()
        self.mono_font_family_var = ctk.StringVar()
        self.mono_font_size_var = ctk.StringVar()
        
        # Available fonts
        self.available_fonts = self._get_available_fonts()
        self.font_sizes = ['8', '9', '10', '11', '12', '13', '14', '16', '18', '20', '22', '24']
        
        # Load current settings
        self._load_current_settings()
        
        # Create UI
        self._create_ui()
        
        # Set up change callbacks
        self._setup_callbacks()
    
    def _get_available_fonts(self) -> List[str]:
        """Get list of available system fonts."""
        try:
            # Get system fonts
            fonts = list(tkfont.families())
            
            # Filter to common, readable fonts
            common_fonts = [
                'Arial', 'Helvetica', 'Times New Roman', 'Georgia', 'Verdana',
                'Tahoma', 'Trebuchet MS', 'Calibri', 'Segoe UI', 'Open Sans',
                'Roboto', 'Lato', 'Source Sans Pro', 'Ubuntu', 'DejaVu Sans'
            ]
            
            # Include common monospace fonts
            mono_fonts = [
                'Courier New', 'Consolas', 'Monaco', 'Menlo', 'DejaVu Sans Mono',
                'Source Code Pro', 'Fira Code', 'JetBrains Mono', 'Ubuntu Mono'
            ]
            
            # Combine and filter available fonts
            preferred_fonts = common_fonts + mono_fonts
            available_preferred = [font for font in preferred_fonts if font in fonts]
            
            # Add other available fonts
            other_fonts = [font for font in sorted(fonts) if font not in preferred_fonts]
            
            return available_preferred + other_fonts
            
        except Exception:
            # Fallback to basic fonts
            return ['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana']
    
    def _load_current_settings(self):
        """Load current font settings from theme manager."""
        # Default fonts
        default_font = self._theme_manager.get_font('default')
        self.font_family_var.set(default_font[0])
        self.font_size_var.set(str(default_font[1]))
        
        # Header fonts
        header_font = self._theme_manager.get_font('header')
        self.header_font_family_var.set(header_font[0])
        self.header_font_size_var.set(str(header_font[1]))
        
        # Monospace fonts
        mono_font = self._theme_manager.get_font('monospace')
        self.mono_font_family_var.set(mono_font[0])
        self.mono_font_size_var.set(str(mono_font[1]))
    
    def _create_ui(self):
        """Create the font settings UI."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ThemedLabel(self, text="Font Settings", label_type='header')
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Default font section
        self._create_font_section("Default Font", 1, 
                                self.font_family_var, self.font_size_var,
                                "Used for most text in the application")
        
        # Header font section
        self._create_font_section("Header Font", 3,
                                self.header_font_family_var, self.header_font_size_var,
                                "Used for page titles and section headers")
        
        # Monospace font section
        self._create_font_section("Monospace Font", 5,
                                self.mono_font_family_var, self.mono_font_size_var,
                                "Used for code, sequences, and technical text")
        
        # Preview section
        self._create_preview_section(7)
        
        # Action buttons
        self._create_action_buttons(9)
    
    def _create_font_section(self, title: str, row: int, family_var: ctk.StringVar, 
                           size_var: ctk.StringVar, description: str):
        """Create a font configuration section."""
        # Section title
        title_label = ThemedLabel(self, text=title, label_type='default')
        title_label.grid(row=row, column=0, padx=20, pady=(15, 5), sticky="w")
        
        # Description tooltip
        create_tooltip(title_label, description, delay=0.3)
        
        # Font family dropdown
        family_label = ThemedLabel(self, text="Family:")
        family_label.grid(row=row+1, column=0, padx=(40, 10), pady=2, sticky="w")
        
        family_menu = ThemedOptionMenu(self, variable=family_var, values=self.available_fonts)
        family_menu.grid(row=row+1, column=1, padx=10, pady=2, sticky="ew")
        
        # Font size dropdown
        size_label = ThemedLabel(self, text="Size:")
        size_label.grid(row=row+1, column=2, padx=(20, 10), pady=2, sticky="w")
        
        size_menu = ThemedOptionMenu(self, variable=size_var, values=self.font_sizes)
        size_menu.grid(row=row+1, column=3, padx=10, pady=2, sticky="w")
        
        # Add tooltips
        create_validation_tooltip(family_menu, f"Select font family for {title.lower()}")
        create_validation_tooltip(size_menu, f"Select font size for {title.lower()} (8-24 pt)")
    
    def _create_preview_section(self, row: int):
        """Create font preview section."""
        # Preview title
        preview_label = ThemedLabel(self, text="Preview", label_type='header')
        preview_label.grid(row=row, column=0, columnspan=4, padx=20, pady=(20, 10), sticky="w")
        
        # Preview frame
        preview_frame = ThemedFrame(self)
        preview_frame.grid(row=row+1, column=0, columnspan=4, padx=20, pady=10, sticky="ew")
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Preview labels
        self.default_preview = ThemedLabel(preview_frame, 
                                         text="Default text: The quick brown fox jumps over the lazy dog",
                                         label_type='default')
        self.default_preview.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.header_preview = ThemedLabel(preview_frame,
                                        text="Header Text: GeneStudio Pro Analysis",
                                        label_type='header')
        self.header_preview.grid(row=1, column=0, padx=15, pady=5, sticky="w")
        
        self.mono_preview = ThemedLabel(preview_frame,
                                      text="Monospace: ATCGATCGATCG (DNA Sequence)",
                                      label_type='monospace')
        self.mono_preview.grid(row=2, column=0, padx=15, pady=(5, 10), sticky="w")
        
        # Add tooltips to preview
        create_tooltip(self.default_preview, "Preview of default font settings")
        create_tooltip(self.header_preview, "Preview of header font settings")
        create_tooltip(self.mono_preview, "Preview of monospace font settings")
    
    def _create_action_buttons(self, row: int):
        """Create action buttons."""
        button_frame = ThemedFrame(self)
        button_frame.grid(row=row, column=0, columnspan=4, padx=20, pady=20, sticky="ew")
        
        # Reset to defaults button
        reset_button = ThemedButton(button_frame, text="Reset to Defaults", 
                                  button_type='secondary', command=self._reset_to_defaults)
        reset_button.pack(side="left", padx=(0, 10))
        
        # Apply button
        apply_button = ThemedButton(button_frame, text="Apply Changes", 
                                  button_type='primary', command=self._apply_changes)
        apply_button.pack(side="right")
        
        # Add tooltips
        create_tooltip(reset_button, "Reset all font settings to application defaults")
        create_tooltip(apply_button, "Apply font changes to the entire application")
    
    def _setup_callbacks(self):
        """Set up change callbacks for live preview."""
        self.font_family_var.trace_add('write', self._on_font_change)
        self.font_size_var.trace_add('write', self._on_font_change)
        self.header_font_family_var.trace_add('write', self._on_font_change)
        self.header_font_size_var.trace_add('write', self._on_font_change)
        self.mono_font_family_var.trace_add('write', self._on_font_change)
        self.mono_font_size_var.trace_add('write', self._on_font_change)
    
    def _on_font_change(self, *args):
        """Handle font setting changes for live preview."""
        try:
            self._update_preview()
        except Exception as e:
            print(f"Error updating font preview: {e}")
    
    def _update_preview(self):
        """Update font preview with current settings."""
        try:
            # Update default font preview
            default_family = self.font_family_var.get()
            default_size = int(self.font_size_var.get()) if self.font_size_var.get().isdigit() else 12
            self.default_preview.configure(font=(default_family, default_size))
            
            # Update header font preview
            header_family = self.header_font_family_var.get()
            header_size = int(self.header_font_size_var.get()) if self.header_font_size_var.get().isdigit() else 16
            self.header_preview.configure(font=(header_family, header_size))
            
            # Update monospace font preview
            mono_family = self.mono_font_family_var.get()
            mono_size = int(self.mono_font_size_var.get()) if self.mono_font_size_var.get().isdigit() else 11
            self.mono_preview.configure(font=(mono_family, mono_size))
            
        except Exception as e:
            print(f"Error updating font preview: {e}")
    
    def _reset_to_defaults(self):
        """Reset font settings to defaults."""
        # Default values
        self.font_family_var.set('Arial')
        self.font_size_var.set('12')
        self.header_font_family_var.set('Arial')
        self.header_font_size_var.set('16')
        self.mono_font_family_var.set('Courier New')
        self.mono_font_size_var.set('11')
        
        # Update preview
        self._update_preview()
    
    def _apply_changes(self):
        """Apply font changes to theme manager."""
        try:
            # Validate font sizes
            default_size = int(self.font_size_var.get()) if self.font_size_var.get().isdigit() else 12
            header_size = int(self.header_font_size_var.get()) if self.header_font_size_var.get().isdigit() else 16
            mono_size = int(self.mono_font_size_var.get()) if self.mono_font_size_var.get().isdigit() else 11
            
            # Update theme manager
            self._theme_manager.update_theme(
                default_font_family=self.font_family_var.get(),
                default_font_size=default_size,
                header_font_family=self.header_font_family_var.get(),
                header_font_size=header_size,
                monospace_font_family=self.mono_font_family_var.get(),
                monospace_font_size=mono_size
            )
            
            # Call change callback
            if self.on_change:
                self.on_change()
                
            # Show success message
            from views.components.toast_notifications import show_success
            show_success("Font settings applied successfully!")
            
        except Exception as e:
            print(f"Error applying font changes: {e}")
            from views.components.toast_notifications import show_error
            show_error(f"Failed to apply font changes: {str(e)}")
    
    def get_current_settings(self) -> dict:
        """Get current font settings as dictionary."""
        return {
            'default_font_family': self.font_family_var.get(),
            'default_font_size': int(self.font_size_var.get()) if self.font_size_var.get().isdigit() else 12,
            'header_font_family': self.header_font_family_var.get(),
            'header_font_size': int(self.header_font_size_var.get()) if self.header_font_size_var.get().isdigit() else 16,
            'monospace_font_family': self.mono_font_family_var.get(),
            'monospace_font_size': int(self.mono_font_size_var.get()) if self.mono_font_size_var.get().isdigit() else 11
        }
    
    def set_settings(self, settings: dict):
        """Set font settings from dictionary."""
        if 'default_font_family' in settings:
            self.font_family_var.set(settings['default_font_family'])
        if 'default_font_size' in settings:
            self.font_size_var.set(str(settings['default_font_size']))
        if 'header_font_family' in settings:
            self.header_font_family_var.set(settings['header_font_family'])
        if 'header_font_size' in settings:
            self.header_font_size_var.set(str(settings['header_font_size']))
        if 'monospace_font_family' in settings:
            self.mono_font_family_var.set(settings['monospace_font_family'])
        if 'monospace_font_size' in settings:
            self.mono_font_size_var.set(str(settings['monospace_font_size']))
        
        # Update preview
        self._update_preview()