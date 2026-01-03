"""Settings data model with validation."""

from dataclasses import dataclass
from typing import Any, Union
import json


@dataclass
class Setting:
    """Setting model with validation."""
    
    key: str = ""
    value: str = ""
    value_type: str = "string"  # string, int, float, bool, json
    category: str = "general"  # appearance, preferences, advanced
    
    def __post_init__(self):
        """Validate setting data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate setting data."""
        if not self.key or not self.key.strip():
            raise ValueError("Setting key cannot be empty")
        
        if len(self.key) > 255:
            raise ValueError("Setting key cannot exceed 255 characters")
        
        valid_types = ["string", "int", "float", "bool", "json"]
        if self.value_type not in valid_types:
            raise ValueError(f"Value type must be one of: {valid_types}")
        
        valid_categories = ["general", "appearance", "preferences", "advanced"]
        if self.category not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        
        # Validate value based on type
        self._validate_value()
    
    def _validate_value(self) -> None:
        """Validate value based on its type."""
        if self.value_type == "int":
            try:
                int(self.value)
            except ValueError:
                raise ValueError(f"Value '{self.value}' is not a valid integer")
        
        elif self.value_type == "float":
            try:
                float(self.value)
            except ValueError:
                raise ValueError(f"Value '{self.value}' is not a valid float")
        
        elif self.value_type == "bool":
            if self.value.lower() not in ["true", "false", "1", "0"]:
                raise ValueError(f"Value '{self.value}' is not a valid boolean")
        
        elif self.value_type == "json":
            try:
                json.loads(self.value)
            except json.JSONDecodeError:
                raise ValueError(f"Value '{self.value}' is not valid JSON")
    
    def get_typed_value(self) -> Any:
        """Get the value converted to its proper type."""
        if self.value_type == "string":
            return self.value
        elif self.value_type == "int":
            return int(self.value)
        elif self.value_type == "float":
            return float(self.value)
        elif self.value_type == "bool":
            return self.value.lower() in ["true", "1"]
        elif self.value_type == "json":
            return json.loads(self.value)
        else:
            return self.value
    
    def set_typed_value(self, value: Any) -> None:
        """Set the value from a typed value."""
        if self.value_type == "string":
            self.value = str(value)
        elif self.value_type == "int":
            self.value = str(int(value))
        elif self.value_type == "float":
            self.value = str(float(value))
        elif self.value_type == "bool":
            self.value = "true" if bool(value) else "false"
        elif self.value_type == "json":
            self.value = json.dumps(value)
        else:
            self.value = str(value)
        
        # Validate the new value
        self._validate_value()
    
    def to_dict(self) -> dict:
        """Convert setting to dictionary."""
        return {
            'key': self.key,
            'value': self.value,
            'value_type': self.value_type,
            'category': self.category
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Setting':
        """Create setting from dictionary."""
        return cls(**data)
    
    @classmethod
    def create_string_setting(cls, key: str, value: str, category: str = "general") -> 'Setting':
        """Create a string setting."""
        return cls(key=key, value=value, value_type="string", category=category)
    
    @classmethod
    def create_int_setting(cls, key: str, value: int, category: str = "general") -> 'Setting':
        """Create an integer setting."""
        return cls(key=key, value=str(value), value_type="int", category=category)
    
    @classmethod
    def create_float_setting(cls, key: str, value: float, category: str = "general") -> 'Setting':
        """Create a float setting."""
        return cls(key=key, value=str(value), value_type="float", category=category)
    
    @classmethod
    def create_bool_setting(cls, key: str, value: bool, category: str = "general") -> 'Setting':
        """Create a boolean setting."""
        return cls(key=key, value="true" if value else "false", value_type="bool", category=category)
    
    @classmethod
    def create_json_setting(cls, key: str, value: Any, category: str = "general") -> 'Setting':
        """Create a JSON setting."""
        return cls(key=key, value=json.dumps(value), value_type="json", category=category)