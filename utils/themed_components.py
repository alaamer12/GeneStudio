"""Themed component system for consistent styling across the application."""

import customtkinter as ctk
from typing import Any, Dict, Optional, Callable
from utils.theme_manager import get_theme_manager


class ThemedComponent:
    """Mixin class for components that need theme support."""
    
    def __init__(self, *args, **kwargs):
        """Initialize themed component."""
        super().__init__(*args, **kwargs)
        
        # Get theme manager
        self._theme_manager = get_theme_manager()
        
        # Register for theme change notifications
        self._theme_manager.add_observer(self._on_theme_changed)
        
        # Apply initial theme
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply current theme to the component."""
        self._update_fonts()
        self._update_colors()
    
    def _update_fonts(self):
        """Update fonts based on current theme."""
        # Override in subclasses to implement specific font updates
        pass
    
    def _update_colors(self):
        """Update colors based on current theme."""
        # Override in subclasses to implement specific color updates
        pass
    
    def _on_theme_changed(self):
        """Handle theme change notification."""
        try:
            self._apply_theme()
        except Exception as e:
            print(f"Error updating theme for {self.__class__.__name__}: {e}")
    
    def destroy(self):
        """Clean up theme observer when component is destroyed."""
        try:
            self._theme_manager.remove_observer(self._on_theme_changed)
        except Exception:
            pass
        super().destroy()


class ThemedLabel(ThemedComponent, ctk.CTkLabel):
    """Themed label with automatic font management."""
    
    def __init__(self, parent, label_type: str = 'default', **kwargs):
        """
        Initialize themed label.
        
        Args:
            parent: Parent widget
            label_type: 'default', 'header', 'monospace'
            **kwargs: Additional CTkLabel arguments
        """
        self._label_type = label_type
        
        # Remove font from kwargs if present (we'll set it via theme)
        kwargs.pop('font', None)
        
        super().__init__(parent, **kwargs)
    
    def _update_fonts(self):
        """Update fonts based on current theme."""
        font_config = self._theme_manager.get_ctk_font(self._label_type)
        self.configure(font=font_config)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        text_color = self._theme_manager.get_color('text')
        self.configure(text_color=text_color)


class ThemedButton(ThemedComponent, ctk.CTkButton):
    """Themed button with automatic font management."""
    
    def __init__(self, parent, button_type: str = 'primary', **kwargs):
        """
        Initialize themed button.
        
        Args:
            parent: Parent widget
            button_type: 'primary', 'secondary'
            **kwargs: Additional CTkButton arguments
        """
        self._button_type = button_type
        
        # Remove theme-related kwargs (we'll set them via theme)
        kwargs.pop('font', None)
        kwargs.pop('fg_color', None)
        
        super().__init__(parent, **kwargs)
    
    def _update_fonts(self):
        """Update fonts based on current theme."""
        font_config = self._theme_manager.get_ctk_font('default')
        self.configure(font=font_config)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        button_config = self._theme_manager.get_button_config(self._button_type)
        self.configure(
            fg_color=button_config['fg_color'],
            text_color=button_config['text_color']
        )


class ThemedEntry(ThemedComponent, ctk.CTkEntry):
    """Themed entry with automatic font management."""
    
    def __init__(self, parent, **kwargs):
        """Initialize themed entry."""
        # Remove font from kwargs if present (we'll set it via theme)
        kwargs.pop('font', None)
        
        super().__init__(parent, **kwargs)
    
    def _update_fonts(self):
        """Update fonts based on current theme."""
        font_config = self._theme_manager.get_ctk_font('default')
        self.configure(font=font_config)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        text_color = self._theme_manager.get_color('text')
        border_color = self._theme_manager.get_color('border')
        self.configure(
            text_color=text_color,
            border_color=border_color
        )


class ThemedTextbox(ThemedComponent, ctk.CTkTextbox):
    """Themed textbox with automatic font management."""
    
    def __init__(self, parent, text_type: str = 'default', **kwargs):
        """
        Initialize themed textbox.
        
        Args:
            parent: Parent widget
            text_type: 'default', 'monospace'
            **kwargs: Additional CTkTextbox arguments
        """
        self._text_type = text_type
        
        # Remove font from kwargs if present (we'll set it via theme)
        kwargs.pop('font', None)
        
        super().__init__(parent, **kwargs)
    
    def _update_fonts(self):
        """Update fonts based on current theme."""
        font_config = self._theme_manager.get_ctk_font(self._text_type)
        self.configure(font=font_config)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        text_color = self._theme_manager.get_color('text')
        border_color = self._theme_manager.get_color('border')
        self.configure(
            text_color=text_color,
            border_color=border_color
        )


class ThemedFrame(ThemedComponent, ctk.CTkFrame):
    """Themed frame with automatic color management."""
    
    def __init__(self, parent, **kwargs):
        """Initialize themed frame."""
        super().__init__(parent, **kwargs)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        surface_color = self._theme_manager.get_color('surface')
        border_color = self._theme_manager.get_color('border')
        self.configure(
            fg_color=surface_color,
            border_color=border_color
        )


class ThemedOptionMenu(ThemedComponent, ctk.CTkOptionMenu):
    """Themed option menu with automatic font management."""
    
    def __init__(self, parent, **kwargs):
        """Initialize themed option menu."""
        # Remove font from kwargs if present (we'll set it via theme)
        kwargs.pop('font', None)
        
        super().__init__(parent, **kwargs)
    
    def _update_fonts(self):
        """Update fonts based on current theme."""
        font_config = self._theme_manager.get_ctk_font('default')
        self.configure(font=font_config)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        text_color = self._theme_manager.get_color('text')
        border_color = self._theme_manager.get_color('border')
        self.configure(
            text_color=text_color,
            border_color=border_color
        )


class ThemedCheckBox(ThemedComponent, ctk.CTkCheckBox):
    """Themed checkbox with automatic font management."""
    
    def __init__(self, parent, **kwargs):
        """Initialize themed checkbox."""
        # Remove font from kwargs if present (we'll set it via theme)
        kwargs.pop('font', None)
        
        super().__init__(parent, **kwargs)
    
    def _update_fonts(self):
        """Update fonts based on current theme."""
        font_config = self._theme_manager.get_ctk_font('default')
        self.configure(font=font_config)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        text_color = self._theme_manager.get_color('text')
        self.configure(text_color=text_color)


class ThemedRadioButton(ThemedComponent, ctk.CTkRadioButton):
    """Themed radio button with automatic font management."""
    
    def __init__(self, parent, **kwargs):
        """Initialize themed radio button."""
        # Remove font from kwargs if present (we'll set it via theme)
        kwargs.pop('font', None)
        
        super().__init__(parent, **kwargs)
    
    def _update_fonts(self):
        """Update fonts based on current theme."""
        font_config = self._theme_manager.get_ctk_font('default')
        self.configure(font=font_config)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        text_color = self._theme_manager.get_color('text')
        self.configure(text_color=text_color)


class ThemedProgressBar(ThemedComponent, ctk.CTkProgressBar):
    """Themed progress bar with automatic color management."""
    
    def __init__(self, parent, **kwargs):
        """Initialize themed progress bar."""
        super().__init__(parent, **kwargs)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        primary_color = self._theme_manager.get_color('primary')
        border_color = self._theme_manager.get_color('border')
        self.configure(
            progress_color=primary_color,
            border_color=border_color
        )


class ThemedSlider(ThemedComponent, ctk.CTkSlider):
    """Themed slider with automatic color management."""
    
    def __init__(self, parent, **kwargs):
        """Initialize themed slider."""
        super().__init__(parent, **kwargs)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        primary_color = self._theme_manager.get_color('primary')
        border_color = self._theme_manager.get_color('border')
        self.configure(
            progress_color=primary_color,
            border_color=border_color
        )


class ThemedSwitch(ThemedComponent, ctk.CTkSwitch):
    """Themed switch with automatic font and color management."""
    
    def __init__(self, parent, **kwargs):
        """Initialize themed switch."""
        # Remove font from kwargs if present (we'll set it via theme)
        kwargs.pop('font', None)
        
        super().__init__(parent, **kwargs)
    
    def _update_fonts(self):
        """Update fonts based on current theme."""
        font_config = self._theme_manager.get_ctk_font('default')
        self.configure(font=font_config)
    
    def _update_colors(self):
        """Update colors based on current theme."""
        text_color = self._theme_manager.get_color('text')
        primary_color = self._theme_manager.get_color('primary')
        self.configure(
            text_color=text_color,
            progress_color=primary_color
        )