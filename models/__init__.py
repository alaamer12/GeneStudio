"""Models package for GeneStudio."""

from .sequence_model import SequenceData, MatchResult, GraphData
from .project_model import Project
from .sequence_model_enhanced import Sequence
from .analysis_model import Analysis
from .settings_model import Setting

__all__ = [
    'SequenceData', 'MatchResult', 'GraphData',  # Legacy models
    'Project', 'Sequence', 'Analysis', 'Setting'  # Enhanced models
]
