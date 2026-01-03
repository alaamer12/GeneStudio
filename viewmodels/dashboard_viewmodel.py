"""Dashboard ViewModel with statistics management and real-time updates."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from viewmodels.base_viewmodel import BaseViewModel
from services.project_service import ProjectService
from services.sequence_service import SequenceService
from services.analysis_service import AnalysisService


class DashboardViewModel(BaseViewModel):
    """ViewModel for dashboard page with statistics and activity management."""
    
    def __init__(self):
        """Initialize dashboard ViewModel."""
        super().__init__()
        
        # Services
        self.project_service = ProjectService()
        self.sequence_service = SequenceService()
        self.analysis_service = AnalysisService()
        
        # Initialize dashboard state
        self._initialize_dashboard_state()
    
    def _initialize_dashboard_state(self):
        """Initialize dashboard-specific state."""
        self.update_state('statistics', {
            'total_projects': 0,
            'active_projects': 0,
            'total_sequences': 0,
            'total_analyses': 0,
            'completed_analyses': 0,
            'recent_activity_count': 0
        }, notify=False)
        
        self.update_state('recent_activity', [], notify=False)
        self.update_state('quick_actions', self._get_quick_actions(), notify=False)
        self.update_state('last_updated', None, notify=False)
    
    def _get_quick_actions(self) -> List[Dict[str, Any]]:
        """Get available quick actions."""
        return [
            {
                'id': 'create_project',
                'title': 'New Project',
                'description': 'Create a new analysis project',
                'icon': '📁',
                'action': 'create_project'
            },
            {
                'id': 'import_fasta',
                'title': 'Import FASTA',
                'description': 'Load sequences from FASTA files',
                'icon': '🧬',
                'action': 'import_fasta'
            },
            {
                'id': 'run_analysis',
                'title': 'Run Analysis',
                'description': 'Start a new sequence analysis',
                'icon': '🔬',
                'action': 'run_analysis'
            },
            {
                'id': 'view_reports',
                'title': 'View Reports',
                'description': 'Browse generated reports',
                'icon': '📊',
                'action': 'view_reports'
            }
        ]
    
    def load_dashboard_data(self) -> None:
        """Load all dashboard data asynchronously."""
        self.log_action("load_dashboard_data")
        
        def load_operation():
            # Load statistics
            stats_success, statistics = self._load_statistics()
            if not stats_success:
                raise Exception(f"Failed to load statistics: {statistics}")
            
            # Load recent activity
            activity_success, activity = self._load_recent_activity()
            if not activity_success:
                raise Exception(f"Failed to load activity: {activity}")
            
            return {
                'statistics': statistics,
                'recent_activity': activity
            }
        
        def on_success(data):
            self.update_state('statistics', data['statistics'])
            self.update_state('recent_activity', data['recent_activity'])
            self.update_state('last_updated', datetime.now())
            
            # Show success message
            try:
                from views.components.toast_notifications import show_success
                show_success("Dashboard updated successfully")
            except ImportError:
                pass
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to load dashboard data: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("load_dashboard", load_operation, on_success, on_error)
    
    def _load_statistics(self) -> tuple[bool, Dict[str, Any]]:
        """Load dashboard statistics."""
        try:
            # Get project statistics
            proj_success, proj_stats = self.project_service.get_project_statistics()
            if not proj_success:
                return False, proj_stats
            
            # Get sequence statistics
            seq_success, seq_stats = self.sequence_service.get_sequence_statistics()
            if not seq_success:
                return False, seq_stats
            
            # Get analysis statistics
            analysis_success, analysis_stats = self.analysis_service.get_analysis_statistics()
            if not analysis_success:
                return False, analysis_stats
            
            # Combine statistics
            combined_stats = {
                'total_projects': proj_stats.get('total_count', 0),
                'active_projects': proj_stats.get('active_count', 0),
                'archived_projects': proj_stats.get('archived_count', 0),
                'completed_projects': proj_stats.get('completed_count', 0),
                'total_sequences': seq_stats.get('total_count', 0),
                'total_analyses': analysis_stats.get('total_count', 0),
                'completed_analyses': analysis_stats.get('completed_count', 0),
                'running_analyses': analysis_stats.get('running_count', 0),
                'failed_analyses': analysis_stats.get('failed_count', 0),
                'recent_activity_count': self._count_recent_activity()
            }
            
            return True, combined_stats
            
        except Exception as e:
            self.logger.error(f"Error loading statistics: {e}")
            return False, str(e)
    
    def _load_recent_activity(self) -> tuple[bool, List[Dict[str, Any]]]:
        """Load recent activity data."""
        try:
            # Get recent projects (get all and sort in memory for now)
            proj_success, all_projects = self.project_service.list_projects()
            recent_projects = []
            if proj_success:
                # Sort by modified_date and take first 5
                sorted_projects = sorted(all_projects, key=lambda p: p.modified_date, reverse=True)
                recent_projects = sorted_projects[:5]
            
            # Get recent analyses (get all and sort in memory for now)
            analysis_success, all_analyses = self.analysis_service.list_analyses()
            recent_analyses = []
            if analysis_success:
                # Sort by created_date and take first 5
                sorted_analyses = sorted(all_analyses, key=lambda a: a.created_date, reverse=True)
                recent_analyses = sorted_analyses[:5]
            
            activity = []
            
            # Add project activities
            if proj_success:
                for project in recent_projects:
                    activity.append({
                        'id': f"project_{project.id}",
                        'type': 'project',
                        'title': f"Project: {project.name}",
                        'description': f"Modified {self._format_relative_time(project.modified_date)}",
                        'timestamp': project.modified_date,
                        'icon': '📁',
                        'action': f"view_project_{project.id}"
                    })
            
            # Add analysis activities
            if analysis_success:
                for analysis in recent_analyses:
                    status_icon = {
                        'completed': '✅',
                        'running': '⏳',
                        'failed': '❌',
                        'pending': '⏸️'
                    }.get(analysis.status, '🔬')
                    
                    activity.append({
                        'id': f"analysis_{analysis.id}",
                        'type': 'analysis',
                        'title': f"Analysis: {analysis.analysis_type}",
                        'description': f"{analysis.status.title()} • {self._format_relative_time(analysis.created_date)}",
                        'timestamp': analysis.created_date,
                        'icon': status_icon,
                        'action': f"view_analysis_{analysis.id}"
                    })
            
            # Sort by timestamp (most recent first)
            activity.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Limit to 10 items
            activity = activity[:10]
            
            return True, activity
            
        except Exception as e:
            self.logger.error(f"Error loading recent activity: {e}")
            return False, str(e)
    
    def _count_recent_activity(self) -> int:
        """Count recent activity items (last 7 days)."""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            
            # Count recent projects (use proper date filtering)
            proj_success, all_projects = self.project_service.list_projects()
            proj_count = 0
            if proj_success:
                proj_count = len([p for p in all_projects if p.modified_date >= cutoff_date])
            
            # Count recent analyses (use proper date filtering)
            analysis_success, all_analyses = self.analysis_service.list_analyses()
            analysis_count = 0
            if analysis_success:
                analysis_count = len([a for a in all_analyses if a.created_date >= cutoff_date])
            
            return proj_count + analysis_count
            
        except Exception as e:
            self.logger.error(f"Error counting recent activity: {e}")
            return 0
    
    def _format_relative_time(self, timestamp: datetime) -> str:
        """Format timestamp as relative time."""
        try:
            now = datetime.now()
            diff = now - timestamp
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "Just now"
                
        except Exception:
            return "Unknown"
    
    def refresh_statistics(self) -> None:
        """Refresh dashboard statistics."""
        self.log_action("refresh_statistics")
        
        def refresh_operation():
            return self._load_statistics()
        
        def on_success(result):
            success, statistics = result
            if success:
                self.update_state('statistics', statistics)
                self.update_state('last_updated', datetime.now())
        
        self.execute_async_operation("refresh_stats", refresh_operation, on_success)
    
    def refresh_activity(self) -> None:
        """Refresh recent activity."""
        self.log_action("refresh_activity")
        
        def refresh_operation():
            return self._load_recent_activity()
        
        def on_success(result):
            success, activity = result
            if success:
                self.update_state('recent_activity', activity)
                self.update_state('last_updated', datetime.now())
        
        self.execute_async_operation("refresh_activity", refresh_operation, on_success)
    
    def handle_quick_action(self, action_id: str) -> None:
        """Handle quick action button clicks."""
        self.log_action("quick_action", {'action_id': action_id})
        
        # Update state to indicate action was triggered
        self.update_state('last_action', {
            'id': action_id,
            'timestamp': datetime.now()
        })
        
        # The actual navigation/action will be handled by the view
        # This just tracks the action in the ViewModel
    
    def handle_activity_click(self, activity_id: str) -> None:
        """Handle activity item clicks."""
        self.log_action("activity_click", {'activity_id': activity_id})
        
        # Update state to indicate activity was clicked
        self.update_state('last_activity_click', {
            'id': activity_id,
            'timestamp': datetime.now()
        })
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get formatted statistics summary."""
        stats = self.get_state('statistics', {})
        
        return {
            'projects': {
                'total': stats.get('total_projects', 0),
                'active': stats.get('active_projects', 0),
                'completion_rate': self._calculate_completion_rate(stats)
            },
            'sequences': {
                'total': stats.get('total_sequences', 0),
                'avg_per_project': self._calculate_avg_sequences_per_project(stats)
            },
            'analyses': {
                'total': stats.get('total_analyses', 0),
                'completed': stats.get('completed_analyses', 0),
                'success_rate': self._calculate_analysis_success_rate(stats)
            },
            'activity': {
                'recent_count': stats.get('recent_activity_count', 0)
            }
        }
    
    def _calculate_completion_rate(self, stats: Dict[str, Any]) -> float:
        """Calculate project completion rate."""
        total = stats.get('total_projects', 0)
        completed = stats.get('completed_projects', 0)
        
        if total == 0:
            return 0.0
        
        return (completed / total) * 100
    
    def _calculate_avg_sequences_per_project(self, stats: Dict[str, Any]) -> float:
        """Calculate average sequences per project."""
        total_projects = stats.get('total_projects', 0)
        total_sequences = stats.get('total_sequences', 0)
        
        if total_projects == 0:
            return 0.0
        
        return total_sequences / total_projects
    
    def _calculate_analysis_success_rate(self, stats: Dict[str, Any]) -> float:
        """Calculate analysis success rate."""
        total = stats.get('total_analyses', 0)
        completed = stats.get('completed_analyses', 0)
        
        if total == 0:
            return 0.0
        
        return (completed / total) * 100
    
    def is_empty_state(self) -> bool:
        """Check if dashboard should show empty state."""
        stats = self.get_state('statistics', {})
        return stats.get('total_projects', 0) == 0
    
    def get_empty_state_config(self) -> Dict[str, Any]:
        """Get configuration for empty state."""
        return {
            'icon': '🧬',
            'title': 'Welcome to GeneStudio Pro',
            'message': 'Get started by creating your first project or loading sample data to explore the features.',
            'primary_action': 'Create Project',
            'secondary_action': 'Load Sample Data'
        }