"""Search ViewModel with real-time search state management and debounced input handling."""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import threading
import time

from viewmodels.base_viewmodel import BaseViewModel
from services.search_service import SearchService
from utils.search_engine import SearchResult


class SearchViewModel(BaseViewModel):
    """ViewModel for search functionality with real-time updates and debouncing."""
    
    def __init__(self):
        """Initialize search ViewModel."""
        super().__init__()
        
        # Services
        self.search_service = SearchService()
        
        # Debouncing
        self._search_timer: Optional[threading.Timer] = None
        self._debounce_delay = 0.3  # 300ms delay
        
        # Initialize search state
        self._initialize_search_state()
    
    def _initialize_search_state(self):
        """Initialize search-specific state."""
        self.update_state('search_query', '', notify=False)
        self.update_state('search_results', [], notify=False)
        self.update_state('search_suggestions', [], notify=False)
        self.update_state('search_history', [], notify=False)
        self.update_state('is_searching', False, notify=False)
        self.update_state('search_error', None, notify=False)
        self.update_state('selected_category', 'all', notify=False)
        self.update_state('search_filters', {}, notify=False)
        self.update_state('results_count', 0, notify=False)
        self.update_state('search_stats', {}, notify=False)
        self.update_state('show_advanced_search', False, notify=False)
        self.update_state('show_search_dropdown', False, notify=False)
        
        # Load initial data
        self._load_search_history()
        self._load_search_stats()
    
    def set_search_query(self, query: str, immediate: bool = False):
        """Set search query with debounced execution."""
        self.update_state('search_query', query)
        self.update_state('search_error', None)
        
        # Cancel previous timer
        if self._search_timer:
            self._search_timer.cancel()
        
        if query.strip():
            if immediate:
                self._perform_search(query)
            else:
                # Debounced search
                self._search_timer = threading.Timer(
                    self._debounce_delay,
                    lambda: self._perform_search(query)
                )
                self._search_timer.start()
            
            # Get suggestions immediately for non-empty queries
            self._get_suggestions(query)
        else:
            # Clear results for empty query
            self.update_state('search_results', [])
            self.update_state('search_suggestions', [])
            self.update_state('results_count', 0)
            self.update_state('show_search_dropdown', False)
    
    def perform_immediate_search(self, query: Optional[str] = None):
        """Perform immediate search without debouncing."""
        search_query = query or self.get_state('search_query', '')
        if search_query.strip():
            self._perform_search(search_query)
    
    def set_search_category(self, category: str):
        """Set search category filter."""
        self.update_state('selected_category', category)
        
        # Re-search with new category if there's a query
        query = self.get_state('search_query', '')
        if query.strip():
            self.perform_immediate_search(query)
    
    def set_search_filters(self, filters: Dict[str, Any]):
        """Set advanced search filters."""
        self.update_state('search_filters', filters)
        
        # Re-search with new filters if there's a query
        query = self.get_state('search_query', '')
        if query.strip():
            self.perform_immediate_search(query)
    
    def toggle_advanced_search(self):
        """Toggle advanced search panel."""
        current = self.get_state('show_advanced_search', False)
        self.update_state('show_advanced_search', not current)
    
    def clear_search(self):
        """Clear search query and results."""
        self.update_state('search_query', '')
        self.update_state('search_results', [])
        self.update_state('search_suggestions', [])
        self.update_state('results_count', 0)
        self.update_state('search_error', None)
        self.update_state('show_search_dropdown', False)
        
        # Cancel any pending search
        if self._search_timer:
            self._search_timer.cancel()
    
    def select_suggestion(self, suggestion: str):
        """Select a search suggestion."""
        self.update_state('search_query', suggestion)
        self.update_state('show_search_dropdown', False)
        self.perform_immediate_search(suggestion)
    
    def select_search_result(self, result: SearchResult) -> Dict[str, Any]:
        """Select a search result and return navigation info."""
        self.log_action("select_search_result", {
            'result_id': result.id,
            'result_type': result.type,
            'relevance_score': result.relevance_score
        })
        
        # Return navigation information
        navigation_info = {
            'type': result.type,
            'id': result.id,
            'title': result.title
        }
        
        if result.type == 'projects':
            navigation_info['page'] = 'projects'
            navigation_info['action'] = 'open_project'
        elif result.type == 'sequences':
            navigation_info['page'] = 'workspace'
            navigation_info['action'] = 'open_sequence'
            navigation_info['project_id'] = result.metadata.get('project_id')
        elif result.type == 'analyses':
            navigation_info['page'] = 'analysis'
            navigation_info['action'] = 'view_analysis'
            navigation_info['project_id'] = result.metadata.get('project_id')
            navigation_info['sequence_id'] = result.metadata.get('sequence_id')
        
        return navigation_info
    
    def clear_search_history(self):
        """Clear search history."""
        def clear_operation():
            return self.search_service.clear_search_history()
        
        def on_success(result):
            self.update_state('search_history', [])
            try:
                from views.components.toast_notifications import show_success
                show_success("Search history cleared")
            except ImportError:
                pass
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to clear search history: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("clear_search_history", clear_operation, on_success, on_error)
    
    def rebuild_search_index(self):
        """Rebuild search indices."""
        def rebuild_operation():
            return self.search_service.rebuild_indices()
        
        def on_success(result):
            success, stats = result
            if success:
                self._load_search_stats()
                try:
                    from views.components.toast_notifications import show_success
                    total_docs = sum(stats.values())
                    show_success(f"Search index rebuilt: {total_docs} documents indexed")
                except ImportError:
                    pass
        
        def on_error(error):
            try:
                from views.components.toast_notifications import show_error
                show_error(f"Failed to rebuild search index: {error}")
            except ImportError:
                pass
        
        self.execute_async_operation("rebuild_search_index", rebuild_operation, on_success, on_error)
    
    def get_search_summary(self) -> Dict[str, Any]:
        """Get search summary information."""
        results = self.get_state('search_results', [])
        query = self.get_state('search_query', '')
        
        # Categorize results
        result_categories = {}
        for result in results:
            category = result.type
            if category not in result_categories:
                result_categories[category] = 0
            result_categories[category] += 1
        
        return {
            'query': query,
            'total_results': len(results),
            'categories': result_categories,
            'is_searching': self.get_state('is_searching', False),
            'has_error': self.get_state('search_error') is not None,
            'selected_category': self.get_state('selected_category', 'all')
        }
    
    def show_search_dropdown(self, show: bool = True):
        """Show or hide search dropdown."""
        self.update_state('show_search_dropdown', show)
    
    def _perform_search(self, query: str):
        """Perform the actual search operation."""
        if not query.strip():
            return
        
        self.log_action("perform_search", {'query': query})
        
        def search_operation():
            category = self.get_state('selected_category', 'all')
            filters = self.get_state('search_filters', {})
            
            # Map category to data types
            data_types = None
            if category != 'all':
                category_mapping = {
                    'projects': ['projects'],
                    'sequences': ['sequences'],
                    'analyses': ['analyses']
                }
                data_types = category_mapping.get(category)
            
            return self.search_service.search(query, data_types, filters)
        
        def on_success(result):
            success, results = result
            if success:
                self.update_state('search_results', results)
                self.update_state('results_count', len(results))
                self.update_state('show_search_dropdown', len(results) > 0)
                
                # Update search history
                self._load_search_history()
            else:
                self.update_state('search_error', results)
            
            self.update_state('is_searching', False)
        
        def on_error(error):
            self.update_state('search_error', str(error))
            self.update_state('search_results', [])
            self.update_state('results_count', 0)
            self.update_state('is_searching', False)
        
        # Set searching state
        self.update_state('is_searching', True)
        self.update_state('search_error', None)
        
        # Execute search
        self.execute_async_operation("search", search_operation, on_success, on_error)
    
    def _get_suggestions(self, query: str):
        """Get search suggestions for autocomplete."""
        if len(query) < 2:  # Only suggest for queries with 2+ characters
            self.update_state('search_suggestions', [])
            return
        
        def suggestions_operation():
            return self.search_service.get_search_suggestions(query)
        
        def on_success(result):
            success, suggestions = result
            if success:
                self.update_state('search_suggestions', suggestions)
        
        def on_error(error):
            self.update_state('search_suggestions', [])
        
        self.execute_async_operation("get_suggestions", suggestions_operation, on_success, on_error)
    
    def _load_search_history(self):
        """Load search history."""
        def history_operation():
            return self.search_service.get_search_history()
        
        def on_success(result):
            success, history = result
            if success:
                self.update_state('search_history', history)
        
        def on_error(error):
            self.update_state('search_history', [])
        
        self.execute_async_operation("load_search_history", history_operation, on_success, on_error)
    
    def _load_search_stats(self):
        """Load search statistics."""
        def stats_operation():
            return self.search_service.get_search_stats()
        
        def on_success(result):
            success, stats = result
            if success:
                self.update_state('search_stats', stats)
        
        def on_error(error):
            self.update_state('search_stats', {})
        
        self.execute_async_operation("load_search_stats", stats_operation, on_success, on_error)
    
    def get_category_results_count(self, category: str) -> int:
        """Get number of results for a specific category."""
        results = self.get_state('search_results', [])
        if category == 'all':
            return len(results)
        
        return len([r for r in results if r.type == category])
    
    def get_filtered_results(self, category: str = None) -> List[SearchResult]:
        """Get results filtered by category."""
        results = self.get_state('search_results', [])
        
        if not category or category == 'all':
            return results
        
        return [r for r in results if r.type == category]