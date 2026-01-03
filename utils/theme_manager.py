"""Centralized theme management system for GeneStudio Pro."""

import customtkinter as ctk
from typing import Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
import threading
import json
from pathlib import Path


@dataclass
class ThemeConfig:
    """Theme configuration data class."""
    
    # Fonts
    default_font_family: str = "Arial"
    default_font_size: int = 12
    header_font_family: str = "Arial"
    header_font_size: int = 16
    monospace_font_family: str = "Courier New"
    monospace_font_size: int = 11
    
    # Colors (support both light and dark modes)
    primary_color: Tuple[str, str] = ("#1f6aa5", "#1f6aa5")
    secondary_color: Tuple[str, str] = ("#144870", "#144870")
    success_color: Tuple[str, str] = ("#2fa572", "#2fa572")
    error_color: Tuple[str, str] = ("#d42f2f", "#d42f2f")
    warning_color: Tuple[str, str] = ("#ffa500", "#ffa500")
    info_color: Tuple[str, str] = ("#1f6aa5", "#1f6aa5")
    
    # UI Colors
    background_color: Tuple[str, str] = ("#f0f0f0", "#1a1a1a")
    surface_color: Tuple[str, str] = ("#ffffff", "#2b2b2b")
    text_color: Tuple[str, str] = ("#000000", "#ffffff")
    text_secondary_color: Tuple[str, str] = ("#666666", "#a0a0a0")
    border_color: Tuple[str, str] = ("#cccccc", "#404040")
    
    # Spacing
    spacing_xs: int = 4
    spacing_sm: int = 8
    spacing_md: int = 16
    spacing_lg: int = 24
    spacing_xl: int = 32
    
    # Border radius
    border_radius_sm: int = 4
    border_radius_md: int = 8
    border_radius_lg: int = 12
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme config to dictionary."""
        return {
            'fonts': {
                'default_family': self.default_font_family,
                'default_size': self.default_font_size,
                'header_family': self.header_font_family,
                'header_size': self.header_font_size,
                'monospace_family': self.monospace_font_family,
                'monospace_size': self.monospace_font_size,
            },
            'colors': {
                'primary': self.primary_color,
                'secondary': self.secondary_color,
                'success': self.success_color,
                'error': self.error_color,
                'warning': self.warning_color,
                'info': self.info_color,
                'background': self.background_color,
                'surface': self.surface_color,
                'text': self.text_color,
                'text_secondary': self.text_secondary_color,
                'border': self.border_color,
            },
            'spacing': {
                'xs': self.spacing_xs,
                'sm': self.spacing_sm,
                'md': self.spacing_md,
                'lg': self.spacing_lg,
                'xl': self.spacing_xl,
            },
            'border_radius': {
                'sm': self.border_radius_sm,
                'md': self.border_radius_md,
                'lg': self.border_radius_lg,
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeConfig':
        """Create theme config from dictionary."""
        fonts = data.get('fonts', {})
        colors = data.get('colors', {})
        spacing = data.get('spacing', {})
        border_radius = data.get('border_radius', {})
        
        return cls(
            default_font_family=fonts.get('default_family', 'Arial'),
            default_font_size=fonts.get('default_size', 12),
            header_font_family=fonts.get('header_family', 'Arial'),
            header_font_size=fonts.get('header_size', 16),
            monospace_font_family=fonts.get('monospace_family', 'Courier New'),
            monospace_font_size=fonts.get('monospace_size', 11),
            
            primary_color=tuple(colors.get('primary', ('#1f6aa5', '#1f6aa5'))),
            secondary_color=tuple(colors.get('secondary', ('#144870', '#144870'))),
            success_color=tuple(colors.get('success', ('#2fa572', '#2fa572'))),
            error_color=tuple(colors.get('error', ('#d42f2f', '#d42f2f'))),
            warning_color=tuple(colors.get('warning', ('#ffa500', '#ffa500'))),
            info_color=tuple(colors.get('info', ('#1f6aa5', '#1f6aa5'))),
            background_color=tuple(colors.get('background', ('#f0f0f0', '#1a1a1a'))),
            surface_color=tuple(colors.get('surface', ('#ffffff', '#2b2b2b'))),
            text_color=tuple(colors.get('text', ('#000000', '#ffffff'))),
            text_secondary_color=tuple(colors.get('text_secondary', ('#666666', '#a0a0a0'))),
            border_color=tuple(colors.get('border', ('#cccccc', '#404040'))),
            
            spacing_xs=spacing.get('xs', 4),
            spacing_sm=spacing.get('sm', 8),
            spacing_md=spacing.get('md', 16),
            spacing_lg=spacing.get('lg', 24),
            spacing_xl=spacing.get('xl', 32),
            
            border_radius_sm=border_radius.get('sm', 4),
            border_radius_md=border_radius.get('md', 8),
            border_radius_lg=border_radius.get('lg', 12),
        )


class ThemeManager:
    """Centralized theme management with caching and dynamic updates."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for theme manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize theme manager."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._config = ThemeConfig()
        self._observers: list[Callable] = []
        self._font_cache: Dict[str, Tuple[str, int]] = {}
        self._color_cache: Dict[str, Tuple[str, str]] = {}
        self._settings_service = None
        
        # Load theme from settings
        self._load_theme_from_settings()
    
    def set_settings_service(self, settings_service):
        """Set the settings service for persistence."""
        self._settings_service = settings_service
        self._load_theme_from_settings()
    
    def _load_theme_from_settings(self):
        """Load theme configuration from settings service."""
        if not self._settings_service:
            return
        
        try:
            # Load theme settings
            theme_data = {}
            
            # Font settings
            font_family = self._get_setting('theme.font.family', self._config.default_font_family)
            font_size = self._get_setting('theme.font.size', self._config.default_font_size)
            header_font_family = self._get_setting('theme.font.header_family', self._config.header_font_family)
            header_font_size = self._get_setting('theme.font.header_size', self._config.header_font_size)
            mono_font_family = self._get_setting('theme.font.monospace_family', self._config.monospace_font_family)
            mono_font_size = self._get_setting('theme.font.monospace_size', self._config.monospace_font_size)
            
            # Update config
            self._config.default_font_family = font_family
            self._config.default_font_size = font_size
            self._config.header_font_family = header_font_family
            self._config.header_font_size = header_font_size
            self._config.monospace_font_family = mono_font_family
            self._config.monospace_font_size = mono_font_size
            
            # Clear caches when settings change
            self._clear_caches()
            
        except Exception as e:
            print(f"Failed to load theme from settings: {e}")
    
    def _get_setting(self, key: str, default: Any) -> Any:
        """Get setting value with fallback to default."""
        if not self._settings_service:
            return default
        
        try:
            success, setting = self._settings_service.get_setting(key)
            if success and setting:
                return setting.get_typed_value()
        except Exception:
            pass
        
        return default
    
    def _clear_caches(self):
        """Clear all caches when theme changes."""
        self._font_cache.clear()
        self._color_cache.clear()
    
    def add_observer(self, callback: Callable):
        """Add observer for theme changes."""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remove_observer(self, callback: Callable):
        """Remove observer for theme changes."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self):
        """Notify all observers of theme changes."""
        for callback in self._observers:
            try:
                callback()
            except Exception as e:
                print(f"Error notifying theme observer: {e}")
    
    def update_theme(self, **kwargs):
        """Update theme configuration and notify observers."""
        # Update config
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        # Clear caches
        self._clear_caches()
        
        # Save to settings
        self._save_theme_to_settings()
        
        # Notify observers
        self._notify_observers()
    
    def _save_theme_to_settings(self):
        """Save theme configuration to settings service."""
        if not self._settings_service:
            return
        
        try:
            # Save font settings
            self._settings_service.set_setting('theme.font.family', self._config.default_font_family, 'string', 'appearance')
            self._settings_service.set_setting('theme.font.size', self._config.default_font_size, 'int', 'appearance')
            self._settings_service.set_setting('theme.font.header_family', self._config.header_font_family, 'string', 'appearance')
            self._settings_service.set_setting('theme.font.header_size', self._config.header_font_size, 'int', 'appearance')
            self._settings_service.set_setting('theme.font.monospace_family', self._config.monospace_font_family, 'string', 'appearance')
            self._settings_service.set_setting('theme.font.monospace_size', self._config.monospace_font_size, 'int', 'appearance')
            
        except Exception as e:
            print(f"Failed to save theme to settings: {e}")
    
    # Font methods with caching
    def get_font(self, font_type: str = 'default', weight: str = 'normal') -> Tuple[str, int, str]:
        """
        Get font configuration with caching.
        
        Args:
            font_type: 'default', 'header', 'monospace'
            weight: 'normal', 'bold'
        
        Returns:
            Tuple of (family, size, weight)
        """
        cache_key = f"{font_type}_{weight}"
        
        if cache_key not in self._font_cache:
            if font_type == 'header':
                family = self._config.header_font_family
                size = self._config.header_font_size
            elif font_type == 'monospace':
                family = self._config.monospace_font_family
                size = self._config.monospace_font_size
            else:  # default
                family = self._config.default_font_family
                size = self._config.default_font_size
            
            self._font_cache[cache_key] = (family, size, weight)
        
        return self._font_cache[cache_key]
    
    def get_ctk_font(self, font_type: str = 'default', weight: str = 'normal') -> Tuple[str, int, str]:
        """Get font tuple for CustomTkinter components."""
        family, size, font_weight = self.get_font(font_type, weight)
        return (family, size, font_weight)
    
    # Color methods with caching
    def get_color(self, color_type: str) -> Tuple[str, str]:
        """
        Get color configuration with caching.
        
        Args:
            color_type: 'primary', 'secondary', 'success', 'error', 'warning', 'info',
                       'background', 'surface', 'text', 'text_secondary', 'border'
        
        Returns:
            Tuple of (light_mode_color, dark_mode_color)
        """
        if color_type not in self._color_cache:
            color_map = {
                'primary': self._config.primary_color,
                'secondary': self._config.secondary_color,
                'success': self._config.success_color,
                'error': self._config.error_color,
                'warning': self._config.warning_color,
                'info': self._config.info_color,
                'background': self._config.background_color,
                'surface': self._config.surface_color,
                'text': self._config.text_color,
                'text_secondary': self._config.text_secondary_color,
                'border': self._config.border_color,
            }
            
            self._color_cache[color_type] = color_map.get(color_type, ('#000000', '#ffffff'))
        
        return self._color_cache[color_type]
    
    # Spacing methods
    def get_spacing(self, size: str) -> int:
        """Get spacing value."""
        spacing_map = {
            'xs': self._config.spacing_xs,
            'sm': self._config.spacing_sm,
            'md': self._config.spacing_md,
            'lg': self._config.spacing_lg,
            'xl': self._config.spacing_xl,
        }
        return spacing_map.get(size, self._config.spacing_md)
    
    def get_border_radius(self, size: str) -> int:
        """Get border radius value."""
        radius_map = {
            'sm': self._config.border_radius_sm,
            'md': self._config.border_radius_md,
            'lg': self._config.border_radius_lg,
        }
        return radius_map.get(size, self._config.border_radius_md)
    
    # Convenience methods for common use cases
    def get_toast_config(self, toast_type: str) -> Dict[str, Any]:
        """Get complete configuration for toast notifications."""
        color_map = {
            'success': 'success',
            'error': 'error',
            'warning': 'warning',
            'info': 'info'
        }
        
        color_type = color_map.get(toast_type, 'info')
        
        return {
            'font': self.get_ctk_font('default'),
            'icon_color': self.get_color(color_type),
            'background_color': self.get_color('surface'),
            'text_color': self.get_color('text'),
            'border_color': self.get_color('border'),
            'border_radius': self.get_border_radius('md'),
            'spacing': self.get_spacing('md')
        }
    
    def get_button_config(self, button_type: str = 'primary') -> Dict[str, Any]:
        """Get complete configuration for buttons."""
        color_type = 'primary' if button_type == 'primary' else 'secondary'
        
        return {
            'font': self.get_ctk_font('default'),
            'fg_color': self.get_color(color_type),
            'text_color': self.get_color('text'),
            'border_radius': self.get_border_radius('md')
        }
    
    def get_label_config(self, label_type: str = 'default') -> Dict[str, Any]:
        """Get complete configuration for labels."""
        font_type = 'header' if label_type == 'header' else 'default'
        
        return {
            'font': self.get_ctk_font(font_type),
            'text_color': self.get_color('text')
        }


# Global theme manager instance
_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


# Convenience functions for easy access
def get_font(font_type: str = 'default', weight: str = 'normal') -> Tuple[str, int, str]:
    """Get font configuration."""
    return get_theme_manager().get_font(font_type, weight)


def get_color(color_type: str) -> Tuple[str, str]:
    """Get color configuration."""
    return get_theme_manager().get_color(color_type)


def get_spacing(size: str) -> int:
    """Get spacing value."""
    return get_theme_manager().get_spacing(size)


def get_border_radius(size: str) -> int:
    """Get border radius value."""
    return get_theme_manager().get_border_radius(size)