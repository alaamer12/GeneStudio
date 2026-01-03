"""Search service with query processing, result ranking, and history management."""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import threading

from services.base_service import BaseService
from services.project_service import ProjectService
from services.sequence_service import SequenceService
from services.analysis_service import AnalysisService
from utils.search_engine import SearchEngine, SearchResult
from utils.logger import get_logger


class SearchService(BaseService):
    """Service for search operations with query processing and result ranking."""
    
    def __init__(self):
        """Initialize search service."""
        super().__init__(None)  # No repository needed
        self.search_engine = SearchEngine()
        self.project_service = ProjectService()
        self.sequence_service = SequenceService()
        self.analysis_service = AnalysisService()
        self._index_lock = threading.RLock()
        self.logger = get_logger(__name__)
        
        # Initialize indices
        self._initialize_indices()
    
    def search(self, query: str, data_types: Optional[List[str]] = None,
               filters: Optional[Dict[str, Any]] = None, limit: int = 50) -> Tuple[bool, List[SearchResult]]:
        """Perform search across all indexed data."""
        try:
            if not query or not query.strip():
                return True, []
            
            self.logger.info(f"Performing search: '{query}' in types: {data_types}")
            
            # Perform search
            results = self.search_engine.search(query, data_types, filters, limit)
            
            # Enhance results with additional metadata
            enhanced_results = []
            for result in results:
                enhanced_result = self._enhance_search_result(result)
                if enhanced_result:
                    enhanced_results.append(enhanced_result)
            
            # Re-rank results based on enhanced metadata
            enhanced_results = self._rerank_results(enhanced_results, query)
            
            self.logger.info(f"Search completed: {len(enhanced_results)} results")
            return True, enhanced_results
            
        except Exception as e:
            return self.handle_unexpected_error(e, "search")
    
    def get_search_suggestions(self, partial_query: str, limit: int = 5) -> Tuple[bool, List[str]]:
        """Get search suggestions for autocomplete."""
        try:
            suggestions = self.search_engine.suggest(partial_query, limit)
            return True, suggestions
            
        except Exception as e:
            return self.handle_unexpected_error(e, "get_search_suggestions")
    
    def get_search_history(self, limit: int = 20) -> Tuple[bool, List[Dict[str, Any]]]:
        """Get recent search history."""
        try:
            history = self.search_engine.get_search_history(limit)
            return True, history
            
        except Exception as e:
            return self.handle_unexpected_error(e, "get_search_history")
    
    def clear_search_history(self) -> Tuple[bool, bool]:
        """Clear search history."""
        try:
            self.search_engine.clear_search_history()
            return True, True
            
        except Exception as e:
            return self.handle_unexpected_error(e, "clear_search_history")
    
    def rebuild_indices(self) -> Tuple[bool, Dict[str, int]]:
        """Rebuild all search indices."""
        try:
            with self._index_lock:
                self.logger.info("Rebuilding search indices")
                
                stats = {}
                
                # Rebuild projects index
                success, projects = self.project_service.list_projects()
                if success:
                    project_items = []
                    for project in projects:
                        project_items.append({
                            'id': project.id,
                            'title': project.name,
                            'content': project.description or '',
                            'type': project.type,
                            'status': project.status,
                            'created_date': project.created_date,
                            'sequence_count': project.sequence_count
                        })
                    
                    self.search_engine.build_index('projects', project_items)
                    stats['projects'] = len(project_items)
                
                # Rebuild sequences index
                success, sequences = self.sequence_service.list_sequences()
                if success:
                    sequence_items = []
                    for sequence in sequences:
                        sequence_items.append({
                            'id': sequence.id,
                            'title': sequence.header,
                            'content': sequence.sequence[:1000],  # Limit content for indexing
                            'sequence_type': sequence.sequence_type,
                            'length': sequence.length,
                            'gc_percentage': getattr(sequence, 'gc_percentage', None),
                            'project_id': sequence.project_id,
                            'created_date': sequence.created_date
                        })
                    
                    self.search_engine.build_index('sequences', sequence_items)
                    stats['sequences'] = len(sequence_items)
                
                # Rebuild analyses index
                success, analyses = self.analysis_service.list_analyses()
                if success:
                    analysis_items = []
                    for analysis in analyses:
                        analysis_items.append({
                            'id': analysis.id,
                            'title': f"{analysis.analysis_type} Analysis",
                            'content': str(analysis.results) if analysis.results else '',
                            'analysis_type': analysis.analysis_type,
                            'status': analysis.status,
                            'project_id': analysis.project_id,
                            'sequence_id': analysis.sequence_id,
                            'created_date': analysis.created_date,
                            'execution_time': analysis.execution_time
                        })
                    
                    self.search_engine.build_index('analyses', analysis_items)
                    stats['analyses'] = len(analysis_items)
                
                self.logger.info(f"Search indices rebuilt: {stats}")
                return True, stats
                
        except Exception as e:
            return self.handle_unexpected_error(e, "rebuild_indices")
    
    def update_project_index(self, project_id: int) -> Tuple[bool, bool]:
        """Update project in search index."""
        try:
            success, project = self.project_service.get_project(project_id)
            if not success:
                return False, f"Project {project_id} not found"
            
            project_data = {
                'id': project.id,
                'title': project.name,
                'content': project.description or '',
                'type': project.type,
                'status': project.status,
                'created_date': project.created_date,
                'sequence_count': project.sequence_count
            }
            
            self.search_engine.update_index('projects', str(project_id), project_data)
            return True, True
            
        except Exception as e:
            return self.handle_unexpected_error(e, "update_project_index")
    
    def update_sequence_index(self, sequence_id: int) -> Tuple[bool, bool]:
        """Update sequence in search index."""
        try:
            success, sequence = self.sequence_service.get_sequence(sequence_id)
            if not success:
                return False, f"Sequence {sequence_id} not found"
            
            sequence_data = {
                'id': sequence.id,
                'title': sequence.header,
                'content': sequence.sequence[:1000],  # Limit content for indexing
                'sequence_type': sequence.sequence_type,
                'length': sequence.length,
                'gc_percentage': getattr(sequence, 'gc_percentage', None),
                'project_id': sequence.project_id,
                'created_date': sequence.created_date
            }
            
            self.search_engine.update_index('sequences', str(sequence_id), sequence_data)
            return True, True
            
        except Exception as e:
            return self.handle_unexpected_error(e, "update_sequence_index")
    
    def update_analysis_index(self, analysis_id: int) -> Tuple[bool, bool]:
        """Update analysis in search index."""
        try:
            success, analysis = self.analysis_service.get_analysis(analysis_id)
            if not success:
                return False, f"Analysis {analysis_id} not found"
            
            analysis_data = {
                'id': analysis.id,
                'title': f"{analysis.analysis_type} Analysis",
                'content': str(analysis.results) if analysis.results else '',
                'analysis_type': analysis.analysis_type,
                'status': analysis.status,
                'project_id': analysis.project_id,
                'sequence_id': analysis.sequence_id,
                'created_date': analysis.created_date,
                'execution_time': analysis.execution_time
            }
            
            self.search_engine.update_index('analyses', str(analysis_id), analysis_data)
            return True, True
            
        except Exception as e:
            return self.handle_unexpected_error(e, "update_analysis_index")
    
    def remove_from_index(self, data_type: str, item_id: int) -> Tuple[bool, bool]:
        """Remove item from search index."""
        try:
            self.search_engine.remove_from_index(data_type, str(item_id))
            return True, True
            
        except Exception as e:
            return self.handle_unexpected_error(e, "remove_from_index")
    
    def get_search_stats(self) -> Tuple[bool, Dict[str, Any]]:
        """Get search engine statistics."""
        try:
            stats = self.search_engine.get_index_stats()
            
            # Add additional statistics
            history = self.search_engine.get_search_history(100)
            
            # Calculate search frequency
            recent_searches = [h for h in history if h['timestamp'] > datetime.now() - timedelta(days=7)]
            
            enhanced_stats = {
                'indices': stats,
                'total_documents': sum(s['document_count'] for s in stats.values()),
                'search_history_count': len(history),
                'recent_searches_count': len(recent_searches),
                'most_searched_terms': self._get_popular_search_terms(history[:50])
            }
            
            return True, enhanced_stats
            
        except Exception as e:
            return self.handle_unexpected_error(e, "get_search_stats")
    
    def search_by_category(self, query: str, category: str, limit: int = 20) -> Tuple[bool, List[SearchResult]]:
        """Search within a specific category."""
        category_mapping = {
            'projects': ['projects'],
            'sequences': ['sequences'],
            'analyses': ['analyses'],
            'all': None
        }
        
        data_types = category_mapping.get(category)
        return self.search(query, data_types, None, limit)
    
    def advanced_search(self, criteria: Dict[str, Any]) -> Tuple[bool, List[SearchResult]]:
        """Perform advanced search with multiple criteria."""
        try:
            query = criteria.get('query', '')
            data_types = criteria.get('data_types')
            
            # Build filters from criteria
            filters = {}
            
            # Date range filter
            if criteria.get('date_from') or criteria.get('date_to'):
                filters['date_range'] = {}
                if criteria.get('date_from'):
                    filters['date_range']['start'] = criteria['date_from']
                if criteria.get('date_to'):
                    filters['date_range']['end'] = criteria['date_to']
            
            # Type-specific filters
            if criteria.get('project_type'):
                filters['type'] = criteria['project_type']
            
            if criteria.get('sequence_type'):
                filters['sequence_type'] = criteria['sequence_type']
            
            if criteria.get('analysis_type'):
                filters['analysis_type'] = criteria['analysis_type']
            
            # Status filter
            if criteria.get('status'):
                filters['status'] = criteria['status']
            
            limit = criteria.get('limit', 50)
            
            return self.search(query, data_types, filters, limit)
            
        except Exception as e:
            return self.handle_unexpected_error(e, "advanced_search")
    
    def _initialize_indices(self):
        """Initialize search indices on startup."""
        try:
            # Check if indices exist, if not rebuild them
            stats = self.search_engine.get_index_stats()
            if not stats or sum(s['document_count'] for s in stats.values()) == 0:
                self.logger.info("No search indices found, rebuilding...")
                self.rebuild_indices()
            else:
                self.logger.info(f"Search indices loaded: {stats}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize search indices: {e}")
    
    def _enhance_search_result(self, result: SearchResult) -> Optional[SearchResult]:
        """Enhance search result with additional metadata."""
        try:
            if result.type == 'projects':
                # Add project-specific metadata
                success, project = self.project_service.get_project(int(result.id))
                if success:
                    result.metadata.update({
                        'sequence_count': project.sequence_count,
                        'analysis_count': getattr(project, 'analysis_count', 0),
                        'status': project.status,
                        'type': project.type
                    })
            
            elif result.type == 'sequences':
                # Add sequence-specific metadata
                success, sequence = self.sequence_service.get_sequence(int(result.id))
                if success:
                    result.metadata.update({
                        'length': sequence.length,
                        'sequence_type': sequence.sequence_type,
                        'project_id': sequence.project_id
                    })
            
            elif result.type == 'analyses':
                # Add analysis-specific metadata
                success, analysis = self.analysis_service.get_analysis(int(result.id))
                if success:
                    result.metadata.update({
                        'analysis_type': analysis.analysis_type,
                        'status': analysis.status,
                        'execution_time': analysis.execution_time,
                        'project_id': analysis.project_id,
                        'sequence_id': analysis.sequence_id
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to enhance search result {result.id}: {e}")
            return result
    
    def _rerank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Re-rank results based on additional criteria."""
        try:
            query_lower = query.lower()
            
            for result in results:
                # Boost exact title matches
                if query_lower in result.title.lower():
                    result.relevance_score *= 1.5
                
                # Boost recent items
                days_old = (datetime.now() - result.created_date).days
                if days_old < 7:
                    result.relevance_score *= 1.2
                elif days_old < 30:
                    result.relevance_score *= 1.1
                
                # Type-specific boosts
                if result.type == 'projects':
                    # Boost active projects
                    if result.metadata.get('status') == 'active':
                        result.relevance_score *= 1.1
                
                elif result.type == 'sequences':
                    # Boost sequences with more metadata
                    if result.metadata.get('gc_percentage'):
                        result.relevance_score *= 1.05
                
                elif result.type == 'analyses':
                    # Boost completed analyses
                    if result.metadata.get('status') == 'completed':
                        result.relevance_score *= 1.1
            
            # Sort by updated relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to re-rank results: {e}")
            return results
    
    def _get_popular_search_terms(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get most popular search terms from history."""
        try:
            term_counts = {}
            
            for entry in history:
                query = entry['query'].lower().strip()
                if query:
                    term_counts[query] = term_counts.get(query, 0) + 1
            
            # Sort by frequency
            popular_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
            
            return [{'term': term, 'count': count} for term, count in popular_terms[:10]]
            
        except Exception as e:
            self.logger.error(f"Failed to get popular search terms: {e}")
            return []