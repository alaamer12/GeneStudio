"""Advanced search engine with indexing and fuzzy matching capabilities."""

import re
import json
import sqlite3
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
import time
from difflib import SequenceMatcher
from utils.logger import get_logger


@dataclass
class SearchResult:
    """Search result with relevance scoring."""
    id: str
    type: str  # 'sequence', 'project', 'analysis'
    title: str
    content: str
    relevance_score: float
    metadata: Dict[str, Any]
    highlight_positions: List[Tuple[int, int]]
    created_date: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['created_date'] = self.created_date.isoformat()
        return result


class SearchIndex:
    """Full-text search index for a specific data type."""
    
    def __init__(self, data_type: str, index_dir: str = "data/search_indices"):
        self.data_type = data_type
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.index_dir / f"{data_type}_index.db"
        self.logger = get_logger(f"SearchIndex_{data_type}")
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite FTS database."""
        with sqlite3.connect(self.db_path) as conn:
            # Create FTS5 table for full-text search
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {self.data_type}_fts 
                USING fts5(
                    id UNINDEXED,
                    title,
                    content,
                    metadata UNINDEXED,
                    created_date UNINDEXED
                )
            """)
            
            # Create metadata table for additional filtering
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.data_type}_meta (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content_length INTEGER,
                    metadata TEXT,
                    created_date TEXT,
                    last_updated TEXT
                )
            """)
            
            conn.commit()
    
    def add_document(self, doc_id: str, title: str, content: str, 
                    metadata: Dict[str, Any] = None, created_date: datetime = None):
        """Add or update a document in the index."""
        metadata = metadata or {}
        created_date = created_date or datetime.now()
        
        metadata_json = json.dumps(metadata)
        created_date_str = created_date.isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Insert into FTS table
            conn.execute(f"""
                INSERT OR REPLACE INTO {self.data_type}_fts 
                (id, title, content, metadata, created_date)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_id, title, content, metadata_json, created_date_str))
            
            # Insert into metadata table
            conn.execute(f"""
                INSERT OR REPLACE INTO {self.data_type}_meta
                (id, title, content_length, metadata, created_date, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, title, len(content), metadata_json, 
                  created_date_str, datetime.now().isoformat()))
            
            conn.commit()
    
    def remove_document(self, doc_id: str):
        """Remove a document from the index."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"DELETE FROM {self.data_type}_fts WHERE id = ?", (doc_id,))
            conn.execute(f"DELETE FROM {self.data_type}_meta WHERE id = ?", (doc_id,))
            conn.commit()
    
    def search(self, query: str, limit: int = 50, filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Search documents in the index."""
        if not query.strip():
            return []
        
        # Prepare FTS query
        fts_query = self._prepare_fts_query(query)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Base FTS search
            sql = f"""
                SELECT fts.id, fts.title, fts.content, fts.metadata, fts.created_date,
                       bm25(fts) as relevance_score
                FROM {self.data_type}_fts fts
                WHERE fts MATCH ?
                ORDER BY relevance_score
                LIMIT ?
            """
            
            cursor = conn.execute(sql, (fts_query, limit))
            results = []
            
            for row in cursor:
                try:
                    metadata = json.loads(row['metadata']) if row['metadata'] else {}
                    created_date = datetime.fromisoformat(row['created_date'])
                    
                    # Calculate highlight positions
                    highlight_positions = self._find_highlight_positions(row['content'], query)
                    
                    result = SearchResult(
                        id=row['id'],
                        type=self.data_type,
                        title=row['title'],
                        content=row['content'],
                        relevance_score=abs(row['relevance_score']),  # BM25 returns negative scores
                        metadata=metadata,
                        highlight_positions=highlight_positions,
                        created_date=created_date
                    )
                    
                    # Apply additional filters
                    if self._passes_filters(result, filters):
                        results.append(result)
                
                except Exception as e:
                    self.logger.warning(f"Error processing search result: {e}")
                    continue
            
            return results
    
    def _prepare_fts_query(self, query: str) -> str:
        """Prepare query for FTS5."""
        # Clean and tokenize query
        tokens = re.findall(r'\w+', query.lower())
        
        if not tokens:
            return query
        
        # Build FTS query with prefix matching
        fts_tokens = []
        for token in tokens:
            if len(token) >= 3:
                fts_tokens.append(f"{token}*")  # Prefix matching
            else:
                fts_tokens.append(token)
        
        return " ".join(fts_tokens)
    
    def _find_highlight_positions(self, content: str, query: str) -> List[Tuple[int, int]]:
        """Find positions of query terms in content for highlighting."""
        positions = []
        tokens = re.findall(r'\w+', query.lower())
        
        for token in tokens:
            if len(token) < 2:
                continue
            
            # Find all occurrences of the token
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            for match in pattern.finditer(content):
                positions.append((match.start(), match.end()))
        
        # Merge overlapping positions
        if positions:
            positions.sort()
            merged = [positions[0]]
            
            for start, end in positions[1:]:
                last_start, last_end = merged[-1]
                if start <= last_end + 1:  # Overlapping or adjacent
                    merged[-1] = (last_start, max(last_end, end))
                else:
                    merged.append((start, end))
            
            positions = merged
        
        return positions
    
    def _passes_filters(self, result: SearchResult, filters: Dict[str, Any]) -> bool:
        """Check if result passes additional filters."""
        if not filters:
            return True
        
        # Date range filter
        if 'date_range' in filters:
            start_date, end_date = filters['date_range']
            if not (start_date <= result.created_date <= end_date):
                return False
        
        # Metadata filters
        for key, value in filters.items():
            if key.startswith('meta_'):
                meta_key = key[5:]  # Remove 'meta_' prefix
                if meta_key in result.metadata:
                    if result.metadata[meta_key] != value:
                        return False
        
        return True
    
    def get_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query."""
        if len(partial_query) < 2:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            # Get titles that start with the partial query
            cursor = conn.execute(f"""
                SELECT DISTINCT title
                FROM {self.data_type}_meta
                WHERE title LIKE ? 
                ORDER BY title
                LIMIT ?
            """, (f"{partial_query}%", limit))
            
            suggestions = [row[0] for row in cursor]
            
            # If not enough suggestions, try fuzzy matching
            if len(suggestions) < limit:
                cursor = conn.execute(f"""
                    SELECT DISTINCT title
                    FROM {self.data_type}_meta
                    WHERE title NOT LIKE ?
                    ORDER BY title
                    LIMIT ?
                """, (f"{partial_query}%", limit * 2))
                
                all_titles = [row[0] for row in cursor]
                
                # Use fuzzy matching to find similar titles
                fuzzy_matches = []
                for title in all_titles:
                    similarity = SequenceMatcher(None, partial_query.lower(), title.lower()).ratio()
                    if similarity > 0.6:  # 60% similarity threshold
                        fuzzy_matches.append((title, similarity))
                
                # Sort by similarity and add to suggestions
                fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
                for title, _ in fuzzy_matches[:limit - len(suggestions)]:
                    suggestions.append(title)
            
            return suggestions
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {self.data_type}_meta")
            doc_count = cursor.fetchone()[0]
            
            cursor = conn.execute(f"""
                SELECT AVG(content_length), MAX(content_length), MIN(content_length)
                FROM {self.data_type}_meta
            """)
            avg_length, max_length, min_length = cursor.fetchone()
            
            return {
                'document_count': doc_count,
                'average_content_length': avg_length or 0,
                'max_content_length': max_length or 0,
                'min_content_length': min_length or 0,
                'index_size_mb': self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
            }


class SearchEngine:
    """Advanced search engine with indexing and fuzzy matching."""
    
    def __init__(self, index_dir: str = "data/search_indices"):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.indices: Dict[str, SearchIndex] = {}
        self.fuzzy_threshold = 0.8
        self.logger = get_logger(self.__class__.__name__)
        
        # Search history
        self.search_history: List[str] = []
        self.max_history = 100
        
        # Thread safety
        self._lock = threading.RLock()
    
    def get_index(self, data_type: str) -> SearchIndex:
        """Get or create index for data type."""
        with self._lock:
            if data_type not in self.indices:
                self.indices[data_type] = SearchIndex(data_type, str(self.index_dir))
            return self.indices[data_type]
    
    def build_index(self, data_type: str, items: List[Dict[str, Any]]):
        """Build search index for specific data type."""
        index = self.get_index(data_type)
        
        self.logger.info(f"Building index for {data_type} with {len(items)} items")
        
        for item in items:
            try:
                doc_id = str(item.get('id', ''))
                title = item.get('title', item.get('header', item.get('name', '')))
                content = item.get('content', item.get('sequence', item.get('description', '')))
                metadata = {k: v for k, v in item.items() if k not in ['id', 'title', 'content']}
                created_date = item.get('created_date')
                
                if isinstance(created_date, str):
                    created_date = datetime.fromisoformat(created_date)
                elif not isinstance(created_date, datetime):
                    created_date = datetime.now()
                
                index.add_document(doc_id, title, content, metadata, created_date)
                
            except Exception as e:
                self.logger.warning(f"Failed to index item {item.get('id', 'unknown')}: {e}")
        
        self.logger.info(f"Index built for {data_type}")
    
    def search(self, query: str, data_types: List[str] = None, 
               filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Perform fuzzy search across indexed data."""
        if not query.strip():
            return []
        
        # Add to search history
        self._add_to_history(query)
        
        # Default to all available indices if no types specified
        if data_types is None:
            data_types = list(self.indices.keys())
        
        all_results = []
        
        for data_type in data_types:
            if data_type in self.indices:
                try:
                    results = self.indices[data_type].search(query, filters=filters)
                    all_results.extend(results)
                except Exception as e:
                    self.logger.error(f"Search failed for {data_type}: {e}")
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Apply fuzzy matching if needed
        if len(all_results) < 10:  # If few results, try fuzzy matching
            fuzzy_results = self._fuzzy_search(query, data_types, filters)
            
            # Merge results, avoiding duplicates
            existing_ids = {r.id for r in all_results}
            for result in fuzzy_results:
                if result.id not in existing_ids:
                    all_results.append(result)
        
        return all_results
    
    def _fuzzy_search(self, query: str, data_types: List[str], 
                     filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Perform fuzzy search when exact search yields few results."""
        fuzzy_results = []
        
        # Generate fuzzy query variations
        query_variations = self._generate_fuzzy_queries(query)
        
        for variation in query_variations:
            for data_type in data_types:
                if data_type in self.indices:
                    try:
                        results = self.indices[data_type].search(variation, limit=20, filters=filters)
                        
                        # Adjust relevance scores for fuzzy matches
                        for result in results:
                            similarity = SequenceMatcher(None, query.lower(), variation.lower()).ratio()
                            result.relevance_score *= similarity * 0.8  # Reduce score for fuzzy matches
                        
                        fuzzy_results.extend(results)
                        
                    except Exception as e:
                        self.logger.warning(f"Fuzzy search failed for {data_type}: {e}")
        
        return fuzzy_results
    
    def _generate_fuzzy_queries(self, query: str) -> List[str]:
        """Generate fuzzy query variations."""
        variations = []
        tokens = query.split()
        
        # Single token variations
        for token in tokens:
            if len(token) > 3:
                # Remove last character (typo simulation)
                variations.append(token[:-1])
                # Add wildcard
                variations.append(f"{token[:-1]}*")
        
        # Partial queries
        if len(tokens) > 1:
            # First half of tokens
            variations.append(" ".join(tokens[:len(tokens)//2]))
            # Last half of tokens
            variations.append(" ".join(tokens[len(tokens)//2:]))
        
        return variations
    
    def suggest(self, partial_query: str) -> List[str]:
        """Provide search suggestions based on query history and indices."""
        suggestions = set()
        
        # Get suggestions from search history
        history_suggestions = self._get_history_suggestions(partial_query)
        suggestions.update(history_suggestions)
        
        # Get suggestions from indices
        for index in self.indices.values():
            try:
                index_suggestions = index.get_suggestions(partial_query, limit=5)
                suggestions.update(index_suggestions)
            except Exception as e:
                self.logger.warning(f"Failed to get suggestions from index: {e}")
        
        # Sort by relevance (history first, then alphabetical)
        sorted_suggestions = []
        
        # Add history suggestions first
        for suggestion in history_suggestions:
            if suggestion in suggestions:
                sorted_suggestions.append(suggestion)
                suggestions.remove(suggestion)
        
        # Add remaining suggestions alphabetically
        sorted_suggestions.extend(sorted(suggestions))
        
        return sorted_suggestions[:10]  # Limit to 10 suggestions
    
    def _get_history_suggestions(self, partial_query: str) -> List[str]:
        """Get suggestions from search history."""
        suggestions = []
        partial_lower = partial_query.lower()
        
        for query in reversed(self.search_history):  # Most recent first
            if query.lower().startswith(partial_lower) and query not in suggestions:
                suggestions.append(query)
                if len(suggestions) >= 5:
                    break
        
        return suggestions
    
    def _add_to_history(self, query: str):
        """Add query to search history."""
        query = query.strip()
        if not query or len(query) < 2:
            return
        
        # Remove if already exists
        if query in self.search_history:
            self.search_history.remove(query)
        
        # Add to front
        self.search_history.insert(0, query)
        
        # Limit history size
        if len(self.search_history) > self.max_history:
            self.search_history = self.search_history[:self.max_history]
    
    def update_index(self, data_type: str, item_id: str, item_data: Dict[str, Any]):
        """Update index when data changes."""
        index = self.get_index(data_type)
        
        try:
            title = item_data.get('title', item_data.get('header', item_data.get('name', '')))
            content = item_data.get('content', item_data.get('sequence', item_data.get('description', '')))
            metadata = {k: v for k, v in item_data.items() if k not in ['id', 'title', 'content']}
            created_date = item_data.get('created_date')
            
            if isinstance(created_date, str):
                created_date = datetime.fromisoformat(created_date)
            elif not isinstance(created_date, datetime):
                created_date = datetime.now()
            
            index.add_document(item_id, title, content, metadata, created_date)
            
        except Exception as e:
            self.logger.error(f"Failed to update index for {data_type}:{item_id}: {e}")
    
    def remove_from_index(self, data_type: str, item_id: str):
        """Remove item from index."""
        if data_type in self.indices:
            try:
                self.indices[data_type].remove_document(item_id)
            except Exception as e:
                self.logger.error(f"Failed to remove from index {data_type}:{item_id}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive search engine statistics."""
        stats = {
            'indices': {},
            'search_history_size': len(self.search_history),
            'total_documents': 0
        }
        
        for data_type, index in self.indices.items():
            try:
                index_stats = index.get_stats()
                stats['indices'][data_type] = index_stats
                stats['total_documents'] += index_stats['document_count']
            except Exception as e:
                self.logger.warning(f"Failed to get stats for {data_type}: {e}")
                stats['indices'][data_type] = {'error': str(e)}
        
        return stats
    
    def clear_history(self):
        """Clear search history."""
        self.search_history.clear()
    
    def rebuild_all_indices(self):
        """Rebuild all indices (useful for maintenance)."""
        self.logger.info("Rebuilding all search indices")
        
        for data_type in list(self.indices.keys()):
            try:
                # Remove old index
                index = self.indices[data_type]
                if index.db_path.exists():
                    index.db_path.unlink()
                
                # Create new index
                self.indices[data_type] = SearchIndex(data_type, str(self.index_dir))
                
            except Exception as e:
                self.logger.error(f"Failed to rebuild index for {data_type}: {e}")
        
        self.logger.info("Index rebuild completed")


# Global search engine instance
_global_search_engine = None
_search_engine_lock = threading.Lock()


def get_search_engine() -> SearchEngine:
    """Get the global search engine instance."""
    global _global_search_engine
    
    if _global_search_engine is None:
        with _search_engine_lock:
            if _global_search_engine is None:
                _global_search_engine = SearchEngine()
    
    return _global_search_engine