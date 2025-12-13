"""Search engine with full-text indexing and fuzzy matching capabilities."""

import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from difflib import SequenceMatcher
import threading
import os

from utils.logger import get_logger
from utils.platform_dirs import get_app_data_dir


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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """Create from dictionary."""
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        return cls(**data)


class SearchIndex:
    """Full-text search index for a specific data type."""
    
    def __init__(self, data_type: str):
        """Initialize search index."""
        self.data_type = data_type
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.word_index: Dict[str, Set[str]] = {}  # word -> set of document IDs
        self.ngram_index: Dict[str, Set[str]] = {}  # ngram -> set of document IDs
        self._lock = threading.RLock()
        self.logger = get_logger(__name__)
    
    def add_document(self, doc_id: str, title: str, content: str, metadata: Dict[str, Any] = None):
        """Add or update a document in the index."""
        with self._lock:
            # Store document
            self.documents[doc_id] = {
                'title': title,
                'content': content,
                'metadata': metadata or {},
                'indexed_date': datetime.now()
            }
            
            # Index words and n-grams
            self._index_text(doc_id, title + " " + content)
    
    def remove_document(self, doc_id: str):
        """Remove a document from the index."""
        with self._lock:
            if doc_id in self.documents:
                # Remove from word index
                for word_set in self.word_index.values():
                    word_set.discard(doc_id)
                
                # Remove from n-gram index
                for ngram_set in self.ngram_index.values():
                    ngram_set.discard(doc_id)
                
                # Remove document
                del self.documents[doc_id]
    
    def search(self, query: str, fuzzy_threshold: float = 0.6) -> List[Tuple[str, float]]:
        """Search for documents matching the query."""
        with self._lock:
            if not query.strip():
                return []
            
            query_words = self._tokenize(query.lower())
            if not query_words:
                return []
            
            # Find matching documents
            doc_scores: Dict[str, float] = {}
            
            for word in query_words:
                # Exact word matches
                if word in self.word_index:
                    for doc_id in self.word_index[word]:
                        doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1.0
                
                # Fuzzy word matches
                for indexed_word in self.word_index:
                    similarity = SequenceMatcher(None, word, indexed_word).ratio()
                    if similarity >= fuzzy_threshold and similarity < 1.0:
                        for doc_id in self.word_index[indexed_word]:
                            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + similarity * 0.8
                
                # N-gram matches for partial word matching
                ngrams = self._generate_ngrams(word, 3)
                for ngram in ngrams:
                    if ngram in self.ngram_index:
                        for doc_id in self.ngram_index[ngram]:
                            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 0.3
            
            # Normalize scores by query length and document relevance
            for doc_id in doc_scores:
                doc = self.documents[doc_id]
                # Boost title matches
                title_matches = sum(1 for word in query_words if word in doc['title'].lower())
                if title_matches > 0:
                    doc_scores[doc_id] += title_matches * 0.5
                
                # Normalize by query length
                doc_scores[doc_id] /= len(query_words)
            
            # Sort by score and return
            return sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    
    def _index_text(self, doc_id: str, text: str):
        """Index text for a document."""
        words = self._tokenize(text.lower())
        
        # Index words
        for word in words:
            if word not in self.word_index:
                self.word_index[word] = set()
            self.word_index[word].add(doc_id)
        
        # Index n-grams for fuzzy matching
        for word in words:
            ngrams = self._generate_ngrams(word, 3)
            for ngram in ngrams:
                if ngram not in self.ngram_index:
                    self.ngram_index[ngram] = set()
                self.ngram_index[ngram].add(doc_id)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Remove special characters and split
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        # Filter out very short words
        return [word for word in words if len(word) >= 2]
    
    def _generate_ngrams(self, text: str, n: int) -> List[str]:
        """Generate n-grams from text."""
        if len(text) < n:
            return [text]
        return [text[i:i+n] for i in range(len(text) - n + 1)]
    
    def get_document_count(self) -> int:
        """Get number of indexed documents."""
        return len(self.documents)
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        return self.documents.get(doc_id)


class SearchEngine:
    """Advanced search engine with indexing and fuzzy matching."""
    
    def __init__(self, index_path: Optional[str] = None):
        """Initialize search engine."""
        self.index_path = index_path or os.path.join(get_app_data_dir(), "search_index")
        self.indices: Dict[str, SearchIndex] = {}
        self.fuzzy_threshold = 0.6
        self.search_history: List[Dict[str, Any]] = []
        self.max_history = 100
        self._lock = threading.RLock()
        self.logger = get_logger(__name__)
        
        # Ensure index directory exists
        os.makedirs(self.index_path, exist_ok=True)
        
        # Load existing indices
        self._load_indices()
    
    def build_index(self, data_type: str, items: List[Dict[str, Any]]) -> None:
        """Build search index for specific data type."""
        with self._lock:
            self.logger.info(f"Building search index for {data_type} with {len(items)} items")
            
            # Create new index
            index = SearchIndex(data_type)
            
            # Add items to index
            for item in items:
                doc_id = str(item.get('id', ''))
                title = item.get('title', item.get('name', item.get('header', '')))
                content = item.get('content', item.get('description', item.get('sequence', '')))
                metadata = {k: v for k, v in item.items() if k not in ['id', 'title', 'name', 'header', 'content', 'description', 'sequence']}
                
                if doc_id and (title or content):
                    index.add_document(doc_id, title, content, metadata)
            
            # Store index
            self.indices[data_type] = index
            
            # Save to disk
            self._save_index(data_type, index)
            
            self.logger.info(f"Built search index for {data_type}: {index.get_document_count()} documents")
    
    def search(self, query: str, data_types: Optional[List[str]] = None, 
               filters: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[SearchResult]:
        """Perform fuzzy search across indexed data."""
        with self._lock:
            if not query.strip():
                return []
            
            # Record search in history
            self._add_to_history(query, data_types, filters)
            
            # Determine which indices to search
            search_indices = data_types or list(self.indices.keys())
            
            all_results = []
            
            for data_type in search_indices:
                if data_type not in self.indices:
                    continue
                
                index = self.indices[data_type]
                matches = index.search(query, self.fuzzy_threshold)
                
                # Convert to SearchResult objects
                for doc_id, score in matches:
                    doc = index.get_document(doc_id)
                    if doc and self._passes_filters(doc, filters):
                        # Find highlight positions
                        highlight_positions = self._find_highlights(query, doc['title'] + " " + doc['content'])
                        
                        result = SearchResult(
                            id=doc_id,
                            type=data_type,
                            title=doc['title'],
                            content=doc['content'],
                            relevance_score=score,
                            metadata=doc['metadata'],
                            highlight_positions=highlight_positions,
                            created_date=doc['indexed_date']
                        )
                        all_results.append(result)
            
            # Sort by relevance score and limit results
            all_results.sort(key=lambda x: x.relevance_score, reverse=True)
            return all_results[:limit]
    
    def suggest(self, partial_query: str, limit: int = 5) -> List[str]:
        """Provide search suggestions based on query history and index."""
        with self._lock:
            if not partial_query.strip():
                return []
            
            suggestions = set()
            partial_lower = partial_query.lower()
            
            # Suggestions from search history
            for entry in reversed(self.search_history):
                query = entry['query'].lower()
                if partial_lower in query and query != partial_lower:
                    suggestions.add(entry['query'])
                    if len(suggestions) >= limit:
                        break
            
            # Suggestions from indexed words
            if len(suggestions) < limit:
                for data_type, index in self.indices.items():
                    for word in index.word_index:
                        if partial_lower in word and len(word) > len(partial_lower):
                            suggestions.add(word.capitalize())
                            if len(suggestions) >= limit:
                                break
                    if len(suggestions) >= limit:
                        break
            
            return list(suggestions)[:limit]
    
    def update_index(self, data_type: str, item_id: str, item_data: Dict[str, Any]) -> None:
        """Update index when data changes."""
        with self._lock:
            if data_type not in self.indices:
                # Create index if it doesn't exist
                self.indices[data_type] = SearchIndex(data_type)
            
            index = self.indices[data_type]
            
            title = item_data.get('title', item_data.get('name', item_data.get('header', '')))
            content = item_data.get('content', item_data.get('description', item_data.get('sequence', '')))
            metadata = {k: v for k, v in item_data.items() if k not in ['id', 'title', 'name', 'header', 'content', 'description', 'sequence']}
            
            if title or content:
                index.add_document(item_id, title, content, metadata)
                self._save_index(data_type, index)
    
    def remove_from_index(self, data_type: str, item_id: str) -> None:
        """Remove item from index."""
        with self._lock:
            if data_type in self.indices:
                self.indices[data_type].remove_document(item_id)
                self._save_index(data_type, self.indices[data_type])
    
    def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent search history."""
        return list(reversed(self.search_history[-limit:]))
    
    def clear_search_history(self) -> None:
        """Clear search history."""
        with self._lock:
            self.search_history.clear()
            self._save_history()
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get search index statistics."""
        stats = {}
        for data_type, index in self.indices.items():
            stats[data_type] = {
                'document_count': index.get_document_count(),
                'word_count': len(index.word_index),
                'ngram_count': len(index.ngram_index)
            }
        return stats
    
    def _add_to_history(self, query: str, data_types: Optional[List[str]], filters: Optional[Dict[str, Any]]):
        """Add search to history."""
        entry = {
            'query': query,
            'data_types': data_types,
            'filters': filters,
            'timestamp': datetime.now()
        }
        
        # Remove duplicate if exists
        self.search_history = [h for h in self.search_history if h['query'] != query]
        
        # Add to end
        self.search_history.append(entry)
        
        # Limit history size
        if len(self.search_history) > self.max_history:
            self.search_history = self.search_history[-self.max_history:]
        
        # Save to disk
        self._save_history()
    
    def _passes_filters(self, doc: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> bool:
        """Check if document passes filters."""
        if not filters:
            return True
        
        for key, value in filters.items():
            if key in doc['metadata']:
                if doc['metadata'][key] != value:
                    return False
            elif key == 'date_range':
                # Handle date range filtering
                doc_date = doc.get('indexed_date', datetime.min)
                start_date = value.get('start')
                end_date = value.get('end')
                if start_date and doc_date < start_date:
                    return False
                if end_date and doc_date > end_date:
                    return False
        
        return True
    
    def _find_highlights(self, query: str, text: str) -> List[Tuple[int, int]]:
        """Find positions to highlight in text."""
        highlights = []
        query_words = re.findall(r'\w+', query.lower())
        text_lower = text.lower()
        
        for word in query_words:
            start = 0
            while True:
                pos = text_lower.find(word, start)
                if pos == -1:
                    break
                highlights.append((pos, pos + len(word)))
                start = pos + 1
        
        # Merge overlapping highlights
        if highlights:
            highlights.sort()
            merged = [highlights[0]]
            for start, end in highlights[1:]:
                if start <= merged[-1][1]:
                    merged[-1] = (merged[-1][0], max(merged[-1][1], end))
                else:
                    merged.append((start, end))
            highlights = merged
        
        return highlights
    
    def _save_index(self, data_type: str, index: SearchIndex):
        """Save index to disk."""
        try:
            index_file = os.path.join(self.index_path, f"{data_type}_index.json")
            data = {
                'documents': {}
            }
            
            # Convert documents to serializable format
            for doc_id, doc in index.documents.items():
                doc_copy = doc.copy()
                doc_copy['indexed_date'] = doc['indexed_date'].isoformat()
                data['documents'][doc_id] = doc_copy
            
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save index for {data_type}: {e}")
    
    def _load_indices(self):
        """Load indices from disk."""
        try:
            if not os.path.exists(self.index_path):
                return
            
            for filename in os.listdir(self.index_path):
                if filename.endswith('_index.json'):
                    data_type = filename[:-11]  # Remove '_index.json'
                    index_file = os.path.join(self.index_path, filename)
                    
                    try:
                        with open(index_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Recreate index
                        index = SearchIndex(data_type)
                        for doc_id, doc in data.get('documents', {}).items():
                            doc['indexed_date'] = datetime.fromisoformat(doc['indexed_date'])
                            index.documents[doc_id] = doc
                            # Rebuild search indices
                            index._index_text(doc_id, doc['title'] + " " + doc['content'])
                        
                        self.indices[data_type] = index
                        self.logger.info(f"Loaded search index for {data_type}: {index.get_document_count()} documents")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to load index for {data_type}: {e}")
            
            # Load search history
            self._load_history()
            
        except Exception as e:
            self.logger.error(f"Failed to load search indices: {e}")
    
    def _save_history(self):
        """Save search history to disk."""
        try:
            history_file = os.path.join(self.index_path, "search_history.json")
            data = []
            for entry in self.search_history:
                entry_copy = entry.copy()
                entry_copy['timestamp'] = entry['timestamp'].isoformat()
                data.append(entry_copy)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save search history: {e}")
    
    def _load_history(self):
        """Load search history from disk."""
        try:
            history_file = os.path.join(self.index_path, "search_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.search_history = []
                for entry in data:
                    entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
                    self.search_history.append(entry)
                
                self.logger.info(f"Loaded search history: {len(self.search_history)} entries")
                
        except Exception as e:
            self.logger.error(f"Failed to load search history: {e}")