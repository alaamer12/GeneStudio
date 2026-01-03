"""Analysis data model with validation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class Analysis:
    """Analysis model with validation."""
    
    id: Optional[int] = None
    project_id: int = 0
    sequence_id: int = 0
    analysis_type: str = ""  # gc_content, pattern_match, translation, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    error_message: Optional[str] = None
    execution_time: float = 0.0
    created_date: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate analysis data after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate analysis data."""
        if not self.analysis_type or not self.analysis_type.strip():
            raise ValueError("Analysis type cannot be empty")
        
        valid_types = [
            "gc_content", "pattern_match", "translation", "reverse_complement",
            "suffix_array", "overlap_graph", "approximate_match", "boyer_moore"
        ]
        if self.analysis_type not in valid_types:
            raise ValueError(f"Analysis type must be one of: {valid_types}")
        
        valid_statuses = ["pending", "running", "completed", "failed"]
        if self.status not in valid_statuses:
            raise ValueError(f"Analysis status must be one of: {valid_statuses}")
        
        if self.project_id <= 0:
            raise ValueError("Project ID must be positive")
        
        if self.sequence_id <= 0:
            raise ValueError("Sequence ID must be positive")
        
        if self.execution_time < 0:
            raise ValueError("Execution time cannot be negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'sequence_id': self.sequence_id,
            'analysis_type': self.analysis_type,
            'parameters': json.dumps(self.parameters),
            'results': json.dumps(self.results),
            'status': self.status,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'created_date': self.created_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Analysis':
        """Create analysis from dictionary."""
        # Handle datetime conversion
        if isinstance(data.get('created_date'), str):
            data['created_date'] = datetime.fromisoformat(data['created_date'])
        
        # Handle JSON string conversion
        if isinstance(data.get('parameters'), str):
            data['parameters'] = json.loads(data['parameters'])
        if isinstance(data.get('results'), str):
            data['results'] = json.loads(data['results'])
        
        return cls(**data)
    
    def start_execution(self):
        """Mark analysis as running."""
        self.status = "running"
        self.error_message = None
    
    def complete_execution(self, results: Dict[str, Any], execution_time: float):
        """Mark analysis as completed with results."""
        self.status = "completed"
        self.results = results
        self.execution_time = execution_time
        self.error_message = None
    
    def fail_execution(self, error_message: str, execution_time: float = 0.0):
        """Mark analysis as failed with error message."""
        self.status = "failed"
        self.error_message = error_message
        self.execution_time = execution_time
        self.results = {}
    
    def is_completed(self) -> bool:
        """Check if analysis is completed."""
        return self.status == "completed"
    
    def is_failed(self) -> bool:
        """Check if analysis failed."""
        return self.status == "failed"
    
    def is_running(self) -> bool:
        """Check if analysis is running."""
        return self.status == "running"