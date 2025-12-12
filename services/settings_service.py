"""Settings service with configuration management and state persistence."""

from typing import Optional, List, Dict, Any, Tuple
import json
from pathlib import Path

from services.base_service import BaseService, ValidationError, ServiceError
from repositories.settings_repository import SettingsRepository
from models.settings_model import Setting


class SettingsService(BaseService[Setting]):
    """Service for settings management and configuration."""
    
    def __init__(self):
        """Initialize settings service."""
        super().__init__(SettingsRepository())
        self.settings_repository = self.repository
        self._settings_cache = {}  # Cache for frequently accessed settings
        self._cache_dirty = True
    
    def initialize_settings(self) -> Tuple[bool, str]:
        """Initialize default application settings."""
        def operation():
            self.settings_repository.initialize_default_settings()
            self._invalidate_cache()
            return "Default settings initialized successfully"
        
        return self.execute_with_logging(operation, "initialize_settings")
    
    def get_setting(self, key: str, default_value: Any = None) -> Tuple[bool, Any]:
        """Get a setting value with caching."""
        try:
            # Check cache first
            if not self._cache_dirty and key in self._settings_cache:
                return True, self._settings_cache[key]
            
            # Get from repository
            value = self.settings_repository.get_setting_value(key, default_value)
            
            # Update cache
            self._settings_cache[key] = value
            
            return True, value
            
        except Exception as e:
            return self.handle_unexpected_error(e, "get_setting")
    
    def set_setting(self, key: str, value: Any, value_type: str = "string", 
                   category: str = "general") -> Tuple[bool, Setting]:
        """Set a setting value."""
        def operation():
            setting = self.settings_repository.set_setting(key, value, value_type, category)
            
            # Update cache
            self._settings_cache[key] = value
            
            return setting
        
        return self.execute_with_logging(operation, "set_setting")
    
    def delete_setting(self, key: str) -> Tuple[bool, bool]:
        """Delete a setting."""
        def operation():
            success = self.settings_repository.delete_by_key(key)
            
            # Remove from cache
            self._settings_cache.pop(key, None)
            
            return success
        
        return self.execute_with_logging(operation, "delete_setting")
    
    def get_settings_by_category(self, category: str) -> Tuple[bool, List[Setting]]:
        """Get all settings in a category."""
        def operation():
            return self.settings_repository.get_by_category(category)
        
        return self.execute_with_logging(operation, "get_settings_by_category")
    
    def get_all_categories(self) -> Tuple[bool, List[str]]:
        """Get all setting categories."""
        def operation():
            return self.settings_repository.get_all_categories()
        
        return self.execute_with_logging(operation, "get_all_categories")
    
    def list_all_settings(self) -> Tuple[bool, List[Setting]]:
        """List all settings."""
        def operation():
            return self.settings_repository.list()
        
        return self.execute_with_logging(operation, "list_all_settings")
    
    # Convenience methods for common setting types
    
    def get_string_setting(self, key: str, default: str = "") -> str:
        """Get a string setting value."""
        success, value = self.get_setting(key, default)
        return str(value) if success and value is not None else default
    
    def set_string_setting(self, key: str, value: str, category: str = "general") -> Tuple[bool, Setting]:
        """Set a string setting."""
        return self.set_setting(key, value, "string", category)
    
    def get_int_setting(self, key: str, default: int = 0) -> int:
        """Get an integer setting value."""
        success, value = self.get_setting(key, default)
        if success and value is not None:
            try:
                return int(value)
            except (ValueError, TypeError):
                pass
        return default
    
    def set_int_setting(self, key: str, value: int, category: str = "general") -> Tuple[bool, Setting]:
        """Set an integer setting."""
        return self.set_setting(key, value, "int", category)
    
    def get_float_setting(self, key: str, default: float = 0.0) -> float:
        """Get a float setting value."""
        success, value = self.get_setting(key, default)
        if success and value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        return default
    
    def set_float_setting(self, key: str, value: float, category: str = "general") -> Tuple[bool, Setting]:
        """Set a float setting."""
        return self.set_setting(key, value, "float", category)
    
    def get_bool_setting(self, key: str, default: bool = False) -> bool:
        """Get a boolean setting value."""
        success, value = self.get_setting(key, default)
        if success and value is not None:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ['true', '1', 'yes', 'on']
            return bool(value)
        return default
    
    def set_bool_setting(self, key: str, value: bool, category: str = "general") -> Tuple[bool, Setting]:
        """Set a boolean setting."""
        return self.set_setting(key, value, "bool", category)
    
    def get_json_setting(self, key: str, default: Any = None) -> Any:
        """Get a JSON setting value."""
        success, value = self.get_setting(key, default)
        return value if success else default
    
    def set_json_setting(self, key: str, value: Any, category: str = "general") -> Tuple[bool, Setting]:
        """Set a JSON setting."""
        return self.set_setting(key, value, "json", category)
    
    # Application-specific settings
    
    def get_theme(self) -> str:
        """Get current theme."""
        return self.get_string_setting("theme", "dark")
    
    def set_theme(self, theme: str) -> Tuple[bool, Setting]:
        """Set application theme."""
        if theme not in ["light", "dark", "system"]:
            return False, "Invalid theme. Must be 'light', 'dark', or 'system'"
        return self.set_string_setting("theme", theme, "appearance")
    
    def get_font_size(self) -> int:
        """Get font size."""
        return self.get_int_setting("font_size", 12)
    
    def set_font_size(self, size: int) -> Tuple[bool, Setting]:
        """Set font size."""
        if size < 8 or size > 72:
            return False, "Font size must be between 8 and 72"
        return self.set_int_setting("font_size", size, "appearance")
    
    def get_auto_save_enabled(self) -> bool:
        """Get auto-save setting."""
        return self.get_bool_setting("auto_save", True)
    
    def set_auto_save_enabled(self, enabled: bool) -> Tuple[bool, Setting]:
        """Set auto-save setting."""
        return self.set_bool_setting("auto_save", enabled, "preferences")
    
    def get_auto_save_interval(self) -> int:
        """Get auto-save interval in seconds."""
        return self.get_int_setting("auto_save_interval", 300)
    
    def set_auto_save_interval(self, interval: int) -> Tuple[bool, Setting]:
        """Set auto-save interval."""
        if interval < 30 or interval > 3600:
            return False, "Auto-save interval must be between 30 and 3600 seconds"
        return self.set_int_setting("auto_save_interval", interval, "preferences")
    
    def get_recent_files_limit(self) -> int:
        """Get recent files limit."""
        return self.get_int_setting("recent_files_limit", 10)
    
    def set_recent_files_limit(self, limit: int) -> Tuple[bool, Setting]:
        """Set recent files limit."""
        if limit < 1 or limit > 50:
            return False, "Recent files limit must be between 1 and 50"
        return self.set_int_setting("recent_files_limit", limit, "preferences")
    
    def get_max_sequence_length(self) -> int:
        """Get maximum sequence length."""
        return self.get_int_setting("max_sequence_length", 1000000)
    
    def set_max_sequence_length(self, length: int) -> Tuple[bool, Setting]:
        """Set maximum sequence length."""
        if length < 1000 or length > 100000000:
            return False, "Maximum sequence length must be between 1,000 and 100,000,000"
        return self.set_int_setting("max_sequence_length", length, "advanced")
    
    def get_analysis_timeout(self) -> int:
        """Get analysis timeout in seconds."""
        return self.get_int_setting("analysis_timeout", 300)
    
    def set_analysis_timeout(self, timeout: int) -> Tuple[bool, Setting]:
        """Set analysis timeout."""
        if timeout < 10 or timeout > 3600:
            return False, "Analysis timeout must be between 10 and 3600 seconds"
        return self.set_int_setting("analysis_timeout", timeout, "advanced")
    
    # Settings import/export
    
    def export_settings(self, filepath: str) -> Tuple[bool, str]:
        """Export settings to a file."""
        def operation():
            settings_data = self.settings_repository.export_settings()
            
            export_path = Path(filepath)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w') as f:
                json.dump(settings_data, f, indent=2, default=str)
            
            return f"Settings exported to {filepath}"
        
        return self.execute_with_logging(operation, "export_settings")
    
    def import_settings(self, filepath: str) -> Tuple[bool, str]:
        """Import settings from a file."""
        def operation():
            import_path = Path(filepath)
            if not import_path.exists():
                raise ValidationError(f"Settings file not found: {filepath}")
            
            with open(import_path, 'r') as f:
                settings_data = json.load(f)
            
            if not isinstance(settings_data, dict):
                raise ValidationError("Invalid settings file format")
            
            imported_count = self.settings_repository.import_settings(settings_data)
            self._invalidate_cache()
            
            return f"Imported {imported_count} settings from {filepath}"
        
        return self.execute_with_logging(operation, "import_settings")
    
    def reset_settings_to_default(self, category: Optional[str] = None) -> Tuple[bool, str]:
        """Reset settings to default values."""
        def operation():
            if category:
                # Reset specific category
                settings = self.settings_repository.get_by_category(category)
                for setting in settings:
                    self.settings_repository.delete_by_key(setting.key)
            else:
                # Reset all settings
                settings = self.settings_repository.list()
                for setting in settings:
                    self.settings_repository.delete_by_key(setting.key)
            
            # Reinitialize defaults
            self.settings_repository.initialize_default_settings()
            self._invalidate_cache()
            
            if category:
                return f"Reset {category} settings to default"
            else:
                return "Reset all settings to default"
        
        return self.execute_with_logging(operation, "reset_settings_to_default")
    
    def get_settings_summary(self) -> Tuple[bool, Dict[str, Any]]:
        """Get a summary of settings information."""
        def operation():
            all_settings = self.settings_repository.list()
            categories = self.settings_repository.get_all_categories()
            
            summary = {
                'total_settings': len(all_settings),
                'categories': len(categories),
                'category_breakdown': {}
            }
            
            for category in categories:
                category_settings = self.settings_repository.get_by_category(category)
                summary['category_breakdown'][category] = len(category_settings)
            
            return summary
        
        return self.execute_with_logging(operation, "get_settings_summary")
    
    def validate_setting_value(self, key: str, value: Any, value_type: str) -> Tuple[bool, str]:
        """Validate a setting value before saving."""
        try:
            # Create temporary setting for validation
            temp_setting = Setting(key=key, value=str(value), value_type=value_type)
            temp_setting.set_typed_value(value)
            
            # Additional business rule validations
            if key == "font_size" and (value < 8 or value > 72):
                return False, "Font size must be between 8 and 72"
            
            if key == "auto_save_interval" and (value < 30 or value > 3600):
                return False, "Auto-save interval must be between 30 and 3600 seconds"
            
            if key == "recent_files_limit" and (value < 1 or value > 50):
                return False, "Recent files limit must be between 1 and 50"
            
            if key == "max_sequence_length" and (value < 1000 or value > 100000000):
                return False, "Maximum sequence length must be between 1,000 and 100,000,000"
            
            if key == "analysis_timeout" and (value < 10 or value > 3600):
                return False, "Analysis timeout must be between 10 and 3600 seconds"
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    def _invalidate_cache(self):
        """Invalidate the settings cache."""
        self._settings_cache.clear()
        self._cache_dirty = True
    
    def _refresh_cache(self):
        """Refresh the settings cache."""
        try:
            all_settings = self.settings_repository.list()
            self._settings_cache = {
                setting.key: setting.get_typed_value() 
                for setting in all_settings
            }
            self._cache_dirty = False
        except Exception as e:
            self.logger.error(f"Failed to refresh settings cache: {e}")
    
    def get_cached_settings(self) -> Dict[str, Any]:
        """Get all cached settings."""
        if self._cache_dirty:
            self._refresh_cache()
        return self._settings_cache.copy()