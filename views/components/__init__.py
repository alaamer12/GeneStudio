"""Components package initialization."""

from .navigation import NavigationSidebar
from .header import Header
from .footer import Footer
from .buttons import PrimaryButton, SecondaryButton, DangerButton, IconButton, ButtonGroup
from .cards import StatCard, InfoCard, ActionCard
from .tables import DataTable
from .modals import Modal, ConfirmDialog, InputDialog, ProgressDialog
from .plots import PlotCanvas, GCContentPlot, NucleotideDistributionPlot
from .charts import PieChart, DonutChart, AreaChart
from .visualization_3d import Visualization3D

# New UX Components
from .skeleton_loader import SkeletonCard, SkeletonTable, SkeletonText, SkeletonList
from .loading_indicators import LinearProgress, CircularProgress, LoadingOverlay, ProgressDialog as NewProgressDialog
from .toast_notifications import show_success, show_error, show_info, show_warning, clear_all_toasts, set_toast_container
from .error_boundary import ErrorBoundary, ErrorFallback, with_error_boundary
from .empty_states import (
    EmptyState, EmptyDashboard, EmptyProjects, EmptySequences, EmptyAnalyses,
    EmptyResults, EmptyReports, EmptySearch, EmptyWorkspace, EmptyVisualization,
    EmptyActivity, EmptySettings, EmptyError
)
from .confirmation_dialog import (
    ConfirmDialog as NewConfirmDialog, DestructiveActionDialog, SaveChangesDialog, InputDialog as NewInputDialog,
    show_confirm_dialog, show_destructive_dialog, show_input_dialog
)

__all__ = [
    # Existing components
    'NavigationSidebar',
    'Header',
    'Footer',
    'PrimaryButton',
    'SecondaryButton',
    'DangerButton',
    'IconButton',
    'ButtonGroup',
    'StatCard',
    'InfoCard',
    'ActionCard',
    'DataTable',
    'Modal',
    'ConfirmDialog',
    'InputDialog',
    'ProgressDialog',
    'PlotCanvas',
    'GCContentPlot',
    'NucleotideDistributionPlot',
    'PieChart',
    'DonutChart',
    'AreaChart',
    'Visualization3D',
    
    # New UX components
    'SkeletonCard',
    'SkeletonTable',
    'SkeletonText',
    'SkeletonList',
    'LinearProgress',
    'CircularProgress',
    'LoadingOverlay',
    'NewProgressDialog',
    'show_success',
    'show_error',
    'show_info',
    'show_warning',
    'clear_all_toasts',
    'set_toast_container',
    'ErrorBoundary',
    'ErrorFallback',
    'with_error_boundary',
    'EmptyState',
    'EmptyDashboard',
    'EmptyProjects',
    'EmptySequences',
    'EmptyAnalyses',
    'EmptyResults',
    'EmptyReports',
    'EmptySearch',
    'EmptyWorkspace',
    'EmptyVisualization',
    'EmptyActivity',
    'EmptySettings',
    'EmptyError',
    'NewConfirmDialog',
    'DestructiveActionDialog',
    'SaveChangesDialog',
    'NewInputDialog',
    'show_confirm_dialog',
    'show_destructive_dialog',
    'show_input_dialog',
]
