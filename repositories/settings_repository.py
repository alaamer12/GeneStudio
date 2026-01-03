"""Settings repository with configuration persistence."""

from typing import Optional, List, Dict, Any

from repositories.base_repository import BaseRepository, RepositoryError
from models.settings_model import Setting


class SettingsRepository(BaseRepository[Setting]):
    """Repository for settings data access operations."""
    
    def create(self, setting: Setting) -> Setting:
        """Create a new setting."""
        try:
            # Check if setting already exists
            existing = self.get_by_key(setting.key)
            if existing:
                raise RepositoryError(f"Setting with key '{setting.key}' already exists")
            
            # Insert setting
            query = """
                INSERT INTO settings (key, value, value_type, category)
                VALUES (?, ?, ?, ?)
            """
            
            params = (setting.key, setting.value, setting.value_type, setting.category)
            self._execute_query(query, params)
            
            # Log activity
            self._log_activity("create", "setting", None, f"Created setting '{setting.key}'")
            
            return setting
            
        except Exception as e:
            self.logger.error(f"Failed to create setting: {e}")
            raise RepositoryError(f"Failed to create setting: {e}")
    
    def get_by_id(self, entity_id: int) -> Optional[Setting]:
        """Get by ID not applicable for settings (key-based)."""
        raise NotImplementedError("Settings use key-based access, use get_by_key instead")
    
    def get_by_key(self, key: str) -> Optional[Setting]:
        """Get setting by key."""
        try:
            query = "SELECT * FROM settings WHERE key = ?"
            result = self._execute_query(query, (key,))
            
            if not result:
                return None
            
            return Setting.from_dict(result[0])
            
        except Exception as e:
            self.logger.error(f"Failed to get setting '{key}': {e}")
            raise RepositoryError(f"Failed to get setting: {e}")
    
    def update(self, setting: Setting) -> bool:
        """Update an existing setting."""
        try:
            if not setting.key:
                raise RepositoryError("Setting key is required for update")
            
            # Check if setting exists
            existing = self.get_by_key(setting.key)
            if not existing:
                raise RepositoryError(f"Setting with key '{setting.key}' does not exist")
            
            query = """
                UPDATE settings 
                SET value = ?, value_type = ?, category = ?
                WHERE key = ?
            """
            
            params = (setting.value, setting.value_type, setting.category, setting.key)
            self._execute_query(query, params)
            
            # Log activity
            self._log_activity("update", "setting", None, f"Updated setting '{setting.key}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update setting '{setting.key}': {e}")
            raise RepositoryError(f"Failed to update setting: {e}")
    
    def delete(self, entity_id: int) -> bool:
        """Delete by ID not applicable for settings (key-based)."""
        raise NotImplementedError("Settings use key-based access, use delete_by_key instead")
    
    def delete_by_key(self, key: str) -> bool:
        """Delete a setting by key."""
        try:
            # Check if setting exists
            existing = self.get_by_key(key)
            if not existing:
                return False
            
            query = "DELETE FROM settings WHERE key = ?"
            self._execute_query(query, (key,))
            
            # Log activity
            self._log_activity("delete", "setting", None, f"Deleted setting '{key}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete setting '{key}': {e}")
            raise RepositoryError(f"Failed to delete setting: {e}")
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Setting]:
        """List settings with optional filters."""
        try:
            base_query = "SELECT * FROM settings"
            where_clause, params = self._build_where_clause(filters)
            order_clause = self._build_order_clause("category, key")
            
            query = base_query + where_clause + order_clause
            result = self._execute_query(query, params)
            
            return [Setting.from_dict(row) for row in result]
            
        except Exception as e:
            self.logger.error(f"Failed to list settings: {e}")
            raise RepositoryError(f"Failed to list settings: {e}")
    
    def get_by_category(self, category: str) -> List[Setting]:
        """Get all settings in a category."""
        return self.list({"category": category})
    
    def get_all_categories(self) -> List[str]:
        """Get all setting categories."""
        try:
            query = "SELECT DISTINCT category FROM settings ORDER BY category"
            result = self._execute_query(query)
            
            return [row['category'] for row in result]
            
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            raise RepositoryError(f"Failed to get categories: {e}")
    
    def set_setting(self, key: str, value: Any, value_type: str = "string", category: str = "general") -> Setting:
        """Set a setting value (create or update)."""
        try:
            setting = Setting(key=key, value=str(value), value_type=value_type, category=category)
            setting.set_typed_value(value)  # This will validate and convert the value
            
            existing = self.get_by_key(key)
            if existing:
                # Update existing setting
                existing.set_typed_value(value)
                existing.value_type = value_type
                existing.category = category
                self.update(existing)
                return existing
            else:
                # Create new setting
                return self.create(setting)
                
        except Exception as e:
            self.logger.error(f"Failed to set setting '{key}': {e}")
            raise RepositoryError(f"Failed to set setting: {e}")
    
    def get_setting_value(self, key: str, default_value: Any = None) -> Any:
        """Get a setting value with optional default."""
        try:
            setting = self.get_by_key(key)
            if setting:
                return setting.get_typed_value()
            return default_value
            
        except Exception as e:
            self.logger.error(f"Failed to get setting value '{key}': {e}")
            return default_value
    
    def get_string_setting(self, key: str, default: str = "") -> str:
        """Get a string setting value."""
        value = self.get_setting_value(key, default)
        return str(value) if value is not None else default
    
    def get_int_setting(self, key: str, default: int = 0) -> int:
        """Get an integer setting value."""
        value = self.get_setting_value(key, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def get_float_setting(self, key: str, default: float = 0.0) -> float:
        """Get a float setting value."""
        value = self.get_setting_value(key, default)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def get_bool_setting(self, key: str, default: bool = False) -> bool:
        """Get a boolean setting value."""
        value = self.get_setting_value(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']
        return bool(value) if value is not None else default
    
    def get_json_setting(self, key: str, default: Any = None) -> Any:
        """Get a JSON setting value."""
        return self.get_setting_value(key, default)
    
    def initialize_default_settings(self) -> None:
        """Initialize default application settings."""
        try:
            default_settings = [
                # Appearance settings
                Setting.create_string_setting("theme", "dark", "appearance"),
                Setting.create_string_setting("color_scheme", "blue", "appearance"),
                Setting.create_int_setting("font_size", 12, "appearance"),
                Setting.create_string_setting("font_family", "Segoe UI", "appearance"),
                
                # Preferences settings
                Setting.create_bool_setting("auto_save", True, "preferences"),
                Setting.create_int_setting("auto_save_interval", 300, "preferences"),  # 5 minutes
                Setting.create_bool_setting("show_line_numbers", True, "preferences"),
                Setting.create_bool_setting("word_wrap", True, "preferences"),
                Setting.create_int_setting("recent_files_limit", 10, "preferences"),
                
                # Advanced settings
                Setting.create_int_setting("max_sequence_length", 1000000, "advanced"),
                Setting.create_int_setting("analysis_timeout", 300, "advanced"),  # 5 minutes
                Setting.create_bool_setting("enable_logging", True, "advanced"),
                Setting.create_string_setting("log_level", "INFO", "advanced"),
                Setting.create_bool_setting("check_updates", True, "advanced"),
                
                # General settings
                Setting.create_string_setting("default_project_type", "sequence_analysis", "general"),
                Setting.create_string_setting("default_sequence_type", "dna", "general"),
                Setting.create_bool_setting("confirm_deletions", True, "general"),
                Setting.create_int_setting("page_size", 50, "general"),
            ]
            
            for setting in default_settings:
                existing = self.get_by_key(setting.key)
                if not existing:
                    self.create(setting)
                    self.logger.info(f"Initialized default setting: {setting.key}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize default settings: {e}")
            raise RepositoryError(f"Failed to initialize default settings: {e}")
    
    def export_settings(self) -> Dict[str, Any]:
        """Export all settings as a dictionary."""
        try:
            settings = self.list()
            export_data = {}
            
            for setting in settings:
                export_data[setting.key] = {
                    'value': setting.get_typed_value(),
                    'type': setting.value_type,
                    'category': setting.category
                }
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            raise RepositoryError(f"Failed to export settings: {e}")
    
    def import_settings(self, settings_data: Dict[str, Any]) -> int:
        """Import settings from a dictionary. Returns count of imported settings."""
        try:
            imported_count = 0
            
            for key, data in settings_data.items():
                try:
                    value = data.get('value')
                    value_type = data.get('type', 'string')
                    category = data.get('category', 'general')
                    
                    self.set_setting(key, value, value_type, category)
                    imported_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to import setting '{key}': {e}")
            
            self.logger.info(f"Imported {imported_count} settings")
            return imported_count
            
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            raise RepositoryError(f"Failed to import settings: {e}")
    
    def _log_activity(self, action: str, entity_type: str, entity_id: Optional[int], description: str):
        """Log activity for audit trail."""
        try:
            # Get next ID for activity log
            conn = self.db_manager.get_connection()
            result = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM activity_log").fetchall()
            next_id = result[0][0]
            
            query = """
                INSERT INTO activity_log (id, action, entity_type, entity_id, description)
                VALUES (?, ?, ?, ?, ?)
            """
            
            params = (next_id, action, entity_type, entity_id, description)
            conn.execute(query, params)
            
        except Exception as e:
            self.logger.warning(f"Failed to log activity: {e}")