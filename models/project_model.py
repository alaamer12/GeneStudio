"""Project data model with validation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import json


@dataclass
class Project:
    """Enhanced project model with validation."""
    
    id: Optional[int] = None
    name: str = ""
    type: str = "sequence_analysis"  # sequence_analysis, genome_assembly, comparative
    description: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, archived, completed
    sequence_count: int = 0
    analysis_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate project data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate project data."""
        if not self.name or not self.name.strip():
            raise ValueError("Project name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Project name cannot exceed 255 characters")
        
        valid_types = ["sequence_analysis", "genome_assembly", "comparative"]
        if self.type not in valid_types:
            raise ValueError(f"Project type must be one of: {valid_types}")
        
        valid_statuses = ["active", "archived", "completed"]
        if self.status not in valid_statuses:
            raise ValueError(f"Project status must be one of: {valid_statuses}")
        
        if self.sequence_count < 0:
            raise ValueError("Sequence count cannot be negative")
        
        if self.analysis_count < 0:
            raise ValueError("Analysis count cannot be negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat(),
            'status': self.status,
            'sequence_count': self.sequence_count,
            'analysis_count': self.analysis_count,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create project from dictionary."""
        # Handle datetime conversion
        if isinstance(data.get('created_date'), str):
            data['created_date'] = datetime.fromisoformat(data['created_date'])
        if isinstance(data.get('modified_date'), str):
            data['modified_date'] = datetime.fromisoformat(data['modified_date'])
        
        # Handle metadata JSON string
        if isinstance(data.get('metadata'), str):
            data['metadata'] = json.loads(data['metadata'])
        
        return cls(**data)
    
    def update_modified_date(self):
        """Update the modified date to current time."""
        self.modified_date = datetime.now()
    
    def add_sequence(self):
        """Increment sequence count."""
        self.sequence_count += 1
        self.update_modified_date()
    
    def remove_sequence(self):
        """Decrement sequence count."""
        if self.sequence_count > 0:
            self.sequence_count -= 1
            self.update_modified_date()
    
    def add_analysis(self):
        """Increment analysis count."""
        self.analysis_count += 1
        self.update_modified_date()
    
    def remove_analysis(self):
        """Decrement analysis count."""
        if self.analysis_count > 0:
            self.analysis_count -= 1
            self.update_modified_date()