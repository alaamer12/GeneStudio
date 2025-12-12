"""Themed tooltip system with consistent styling and multiple tooltip types."""

import customtkinter as ctk
from tktooltip import ToolTip
from typing import Optional, Callable, Union
from utils.theme_manager import get_theme_manager


class ThemedTooltip:
    """Themed tooltip wrapper with consistent styling."""
    
    def __init__(self, widget, message: Union[str, Callable], delay: float = 0.5, 
                 tooltip_type: str = 'default', follow: bool = False):
        """
        Initialize themed tooltip.
        
        Args:
            widget: Widget to attach tooltip to
            message: Tooltip message (string or callable that returns string)
            delay: Delay before showing tooltip in seconds
            tooltip_type: 'default', 'help', 'validation', 'status'
            follow: Whether tooltip follows mouse cursor
        """
        self.widget = widget
        self.message = message
        self.delay = delay
        self.tooltip_type = tooltip_type
        self.follow = follow
        
        # Get theme manager
        self._theme_manager = get_theme_manager()
        
        # Create tooltip with themed styling
        self._create_tooltip()
        
        # Register for theme changes
        self._theme_manager.add_observer(self._on_theme_changed)
    
    def _create_tooltip(self):
        """Create tooltip with current theme styling."""
        # Get theme configuration
        theme_config = self._get_theme_config()
        
        # Create tooltip
        self.tooltip = ToolTip(
            widget=self.widget,
            msg=self.message,
            delay=self.delay,
            follow=self.follow,
            parent_kwargs={
                "bg": theme_config['bg_color'],
                "padx": theme_config['padx'],
                "pady": theme_config['pady'],
                "relief": "solid",
                "borderwidth": 1
            },
            fg=theme_config['text_color'],
            bg=theme_config['bg_color'],
            font=theme_config['font']
        )
    
    def _get_theme_config(self) -> dict:
        """Get theme configuration for tooltip type."""
        # Get current appearance mode
        appearance_mode = ctk.get_appearance_mode().lower()
        is_dark = appearance_mode == "dark"
        
        # Base configuration
        base_config = {
            'font': self._theme_manager.get_font('default'),
            'padx': self._theme_manager.get_spacing('sm'),
            'pady': self._theme_manager.get_spacing('xs'),
        }
        
        # Get colors based on appearance mode
        surface_color = self._theme_manager.get_color('surface')
        text_color = self._theme_manager.get_color('text')
        
        bg_color = surface_color[1] if is_dark else surface_color[0]
        fg_color = text_color[1] if is_dark else text_color[0]
        
        # Type-specific configurations
        type_configs = {
            'default': {
                'bg_color': bg_color,
                'text_color': fg_color,
            },
            'help': {
                'bg_color': bg_color,
                'text_color': fg_color,
            },
            'validation': {
                'bg_color': bg_color,
                'text_color': fg_color,
            },
            'status': {
                'bg_color': bg_color,
                'text_color': fg_color,
            },
            'error': {
                'bg_color': self._theme_manager.get_color('error')[1 if is_dark else 0],
                'text_color': '#ffffff',
            },
            'warning': {
                'bg_color': self._theme_manager.get_color('warning')[1 if is_dark else 0],
                'text_color': '#ffffff',
            },
            'success': {
                'bg_color': self._theme_manager.get_color('success')[1 if is_dark else 0],
                'text_color': '#ffffff',
            }
        }
        
        # Merge base config with type-specific config
        config = {**base_config, **type_configs.get(self.tooltip_type, type_configs['default'])}
        
        return config
    
    def _on_theme_changed(self):
        """Handle theme change by recreating tooltip."""
        try:
            # Destroy old tooltip
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
            
            # Create new tooltip with updated theme
            self._create_tooltip()
        except Exception as e:
            print(f"Error updating tooltip theme: {e}")
    
    def update_message(self, message: Union[str, Callable]):
        """Update tooltip message."""
        self.message = message
        if hasattr(self, 'tooltip'):
            self.tooltip.msg = message
    
    def show(self):
        """Show tooltip manually."""
        if hasattr(self, 'tooltip'):
            self.tooltip.show()
    
    def hide(self):
        """Hide tooltip manually."""
        if hasattr(self, 'tooltip'):
            self.tooltip.hide()
    
    def destroy(self):
        """Destroy tooltip and clean up."""
        try:
            self._theme_manager.remove_observer(self._on_theme_changed)
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        except Exception:
            pass


# Tooltip creation utility functions
def create_tooltip(widget, message: Union[str, Callable], delay: float = 0.5, 
                  follow: bool = False) -> ThemedTooltip:
    """
    Create a basic themed tooltip.
    
    Args:
        widget: Widget to attach tooltip to
        message: Tooltip message (string or callable)
        delay: Delay before showing tooltip in seconds
        follow: Whether tooltip follows mouse cursor
    
    Returns:
        ThemedTooltip instance
    """
    return ThemedTooltip(widget, message, delay, 'default', follow)


def create_help_tooltip(widget, help_text: str, delay: float = 0.1) -> ThemedTooltip:
    """
    Create a help tooltip for explicit info buttons.
    
    Args:
        widget: Widget to attach tooltip to
        help_text: Help text to display
        delay: Delay before showing tooltip (faster for explicit help)
    
    Returns:
        ThemedTooltip instance
    """
    return ThemedTooltip(widget, help_text, delay, 'help', False)


def create_validation_tooltip(widget, validation_msg: str, delay: float = 0.3) -> ThemedTooltip:
    """
    Create a validation tooltip for input fields.
    
    Args:
        widget: Widget to attach tooltip to
        validation_msg: Validation message to display
        delay: Delay before showing tooltip
    
    Returns:
        ThemedTooltip instance
    """
    return ThemedTooltip(widget, validation_msg, delay, 'validation', False)


def create_status_tooltip(widget, status_func: Callable, delay: float = 0.2) -> ThemedTooltip:
    """
    Create a status tooltip with dynamic content.
    
    Args:
        widget: Widget to attach tooltip to
        status_func: Function that returns current status string
        delay: Delay before showing tooltip
    
    Returns:
        ThemedTooltip instance
    """
    return ThemedTooltip(widget, status_func, delay, 'status', False)


def create_error_tooltip(widget, error_msg: str, delay: float = 0.1) -> ThemedTooltip:
    """
    Create an error tooltip with error styling.
    
    Args:
        widget: Widget to attach tooltip to
        error_msg: Error message to display
        delay: Delay before showing tooltip
    
    Returns:
        ThemedTooltip instance
    """
    return ThemedTooltip(widget, error_msg, delay, 'error', False)


def create_warning_tooltip(widget, warning_msg: str, delay: float = 0.1) -> ThemedTooltip:
    """
    Create a warning tooltip with warning styling.
    
    Args:
        widget: Widget to attach tooltip to
        warning_msg: Warning message to display
        delay: Delay before showing tooltip
    
    Returns:
        ThemedTooltip instance
    """
    return ThemedTooltip(widget, warning_msg, delay, 'warning', False)


def create_success_tooltip(widget, success_msg: str, delay: float = 0.1) -> ThemedTooltip:
    """
    Create a success tooltip with success styling.
    
    Args:
        widget: Widget to attach tooltip to
        success_msg: Success message to display
        delay: Delay before showing tooltip
    
    Returns:
        ThemedTooltip instance
    """
    return ThemedTooltip(widget, success_msg, delay, 'success', False)


def create_info_button_tooltip(widget, info_text: str) -> ThemedTooltip:
    """
    Create tooltip for explicit info buttons with bioinformatics explanations.
    
    Args:
        widget: Info button widget
        info_text: Detailed explanation text
    
    Returns:
        ThemedTooltip instance
    """
    return create_help_tooltip(widget, info_text, delay=0.1)


# Common tooltip delay constants
class TooltipDelays:
    """Standard tooltip delay constants."""
    ACTION = 0.5      # Standard for buttons/actions
    VALIDATION = 0.3  # Faster for input fields
    HELP = 0.1        # Immediate for explicit help buttons
    STATUS = 0.2      # Quick for status indicators
    HOVER = 0.5       # Default hover delay


# Tooltip message templates for common use cases
class TooltipTemplates:
    """Common tooltip message templates."""
    
    @staticmethod
    def keyboard_shortcut(action: str, shortcut: str) -> str:
        """Template for keyboard shortcut tooltips."""
        return f"{action} ({shortcut})"
    
    @staticmethod
    def file_format(format_name: str, extensions: str, description: str) -> str:
        """Template for file format tooltips."""
        return f"{format_name} ({extensions})\n{description}"
    
    @staticmethod
    def validation_format(field_name: str, format_desc: str, example: str = None) -> str:
        """Template for validation tooltips."""
        base = f"{field_name}: {format_desc}"
        if example:
            base += f"\nExample: {example}"
        return base
    
    @staticmethod
    def algorithm_info(name: str, description: str, complexity: str = None) -> str:
        """Template for algorithm explanation tooltips."""
        base = f"{name}\n\n{description}"
        if complexity:
            base += f"\n\nTime Complexity: {complexity}"
        return base
    
    @staticmethod
    def disabled_reason(action: str, reason: str, solution: str = None) -> str:
        """Template for disabled control tooltips."""
        base = f"{action} not available: {reason}"
        if solution:
            base += f"\n{solution}"
        return base
    
    @staticmethod
    def bioinformatics_term(term: str, definition: str, context: str = None) -> str:
        """Template for bioinformatics terminology tooltips."""
        base = f"{term}\n\n{definition}"
        if context:
            base += f"\n\n{context}"
        return base


# Helper function to create info buttons with tooltips
def create_info_button_with_tooltip(parent, help_text: str, **button_kwargs) -> tuple:
    """
    Create an info button with tooltip.
    
    Args:
        parent: Parent widget
        help_text: Help text for tooltip
        **button_kwargs: Additional button configuration
    
    Returns:
        Tuple of (button, tooltip)
    """
    from utils.themed_components import ThemedButton
    
    # Default button configuration for info buttons
    default_config = {
        'text': 'ℹ️',
        'width': 24,
        'height': 24,
        'font': ('Arial', 12),
        'button_type': 'secondary'
    }
    
    # Merge with provided kwargs
    config = {**default_config, **button_kwargs}
    
    # Create button
    info_button = ThemedButton(parent, **config)
    
    # Create tooltip
    tooltip = create_info_button_tooltip(info_button, help_text)
    
    return info_button, tooltip