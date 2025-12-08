"""Pages package initialization."""

from .dashboard_page import DashboardPage
from .projects_page import ProjectsPage
from .workspace_page import WorkspacePage
from .analysis_page import AnalysisPage
from .visualization_page import VisualizationPage
from .pattern_matching_page import PatternMatchingPage
from .graph_analysis_page import GraphAnalysisPage
from .reports_page import ReportsPage
from .settings_page import SettingsPage
from .sequence_management_page import SequenceManagementPage
from .help_page import HelpPage
from .export_page import ExportPage

__all__ = [
    'DashboardPage',
    'ProjectsPage',
    'WorkspacePage',
    'AnalysisPage',
    'VisualizationPage',
    'PatternMatchingPage',
    'GraphAnalysisPage',
    'ReportsPage',
    'SettingsPage',
    'SequenceManagementPage',
    'HelpPage',
    'ExportPage',
]
