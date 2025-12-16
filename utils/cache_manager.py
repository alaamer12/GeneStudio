"""Cache manager for complex analyses and computations."""

import hashlib
import json
import pickle
import time
from typing import Any, Dict, Optional, Callable, TypeVar, Generic
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
from utils.logger import get_logger

T = TypeVar('T')


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl_seconds is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl_seconds)
    
    def touch(self):
        """Update last accessed time and increment access count."""
        self.last_accessed = datetime.now()
        self.access_count += 1


class MemoryCache(Generic[T]):
    """In-memory LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 100, default_ttl: Optional[int] = None):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self.logger = get_logger(self.__class__.__name__)
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, key: str) -> Optional[T]:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self.misses += 1
                return None
            
            # Update access info
            entry.touch()
            self.hits += 1
            
            return entry.value
    
    def put(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """Put value in cache."""
        with self._lock:
            # Calculate size (rough estimate)
            try:
                size_bytes = len(pickle.dumps(value))
            except Exception:
                size_bytes = 1024  # Default estimate
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                size_bytes=size_bytes,
                ttl_seconds=ttl or self.default_ttl
            )
            
            # Remove existing entry if present
            if key in self._cache:
                del self._cache[key]
            
            # Evict entries if necessary
            self._evict_if_necessary()
            
            # Add new entry
            self._cache[key] = entry
    
    def remove(self, key: str) -> bool:
        """Remove entry from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0
            self.evictions = 0
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            
            total_size = sum(entry.size_bytes for entry in self._cache.values())
            
            return {
                'entries': len(self._cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate': hit_rate,
                'total_size_bytes': total_size,
                'average_size_bytes': total_size / len(self._cache) if self._cache else 0
            }
    
    def _evict_if_necessary(self):
        """Evict entries if cache is full."""
        while len(self._cache) >= self.max_size:
            # Find least recently used entry
            lru_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].last_accessed
            )
            
            del self._cache[lru_key]
            self.evictions += 1


class DiskCache:
    """Persistent disk-based cache."""
    
    def __init__(self, cache_dir: str = "data/cache", max_size_mb: int = 500):
        """
        Initialize disk cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_size_mb: Maximum cache size in MB
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._lock = threading.RLock()
        self.logger = get_logger(self.__class__.__name__)
        
        # Metadata file
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self._load_metadata()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache."""
        with self._lock:
            cache_file = self._get_cache_file(key)
            
            if not cache_file.exists():
                return None
            
            try:
                # Check metadata for TTL
                if key in self.metadata:
                    entry_meta = self.metadata[key]
                    if self._is_expired(entry_meta):
                        self.remove(key)
                        return None
                    
                    # Update access info
                    entry_meta['last_accessed'] = datetime.now().isoformat()
                    entry_meta['access_count'] = entry_meta.get('access_count', 0) + 1
                    self._save_metadata()
                
                # Load value
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
                    
            except Exception as e:
                self.logger.warning(f"Failed to load cache entry {key}: {e}")
                self.remove(key)
                return None
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Put value in disk cache."""
        with self._lock:
            try:
                cache_file = self._get_cache_file(key)
                
                # Save value to file
                with open(cache_file, 'wb') as f:
                    pickle.dump(value, f)
                
                # Update metadata
                file_size = cache_file.stat().st_size
                self.metadata[key] = {
                    'created_at': datetime.now().isoformat(),
                    'last_accessed': datetime.now().isoformat(),
                    'access_count': 1,
                    'size_bytes': file_size,
                    'ttl_seconds': ttl,
                    'file_path': str(cache_file)
                }
                
                self._save_metadata()
                
                # Clean up if necessary
                self._cleanup_if_necessary()
                
            except Exception as e:
                self.logger.error(f"Failed to save cache entry {key}: {e}")
    
    def remove(self, key: str) -> bool:
        """Remove entry from disk cache."""
        with self._lock:
            try:
                cache_file = self._get_cache_file(key)
                
                if cache_file.exists():
                    cache_file.unlink()
                
                if key in self.metadata:
                    del self.metadata[key]
                    self._save_metadata()
                
                return True
                
            except Exception as e:
                self.logger.warning(f"Failed to remove cache entry {key}: {e}")
                return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            try:
                # Remove all cache files
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                
                # Clear metadata
                self.metadata.clear()
                self._save_metadata()
                
            except Exception as e:
                self.logger.error(f"Failed to clear cache: {e}")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        with self._lock:
            expired_keys = []
            
            for key, entry_meta in self.metadata.items():
                if self._is_expired(entry_meta):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.remove(key)
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_size = sum(
                entry.get('size_bytes', 0) 
                for entry in self.metadata.values()
            )
            
            return {
                'entries': len(self.metadata),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'max_size_mb': self.max_size_bytes / (1024 * 1024),
                'cache_dir': str(self.cache_dir)
            }
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key."""
        # Create safe filename from key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.cache"
    
    def _load_metadata(self):
        """Load cache metadata from disk."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}
        except Exception as e:
            self.logger.warning(f"Failed to load cache metadata: {e}")
            self.metadata = {}
    
    def _save_metadata(self):
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save cache metadata: {e}")
    
    def _is_expired(self, entry_meta: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        ttl_seconds = entry_meta.get('ttl_seconds')
        if ttl_seconds is None:
            return False
        
        created_at = datetime.fromisoformat(entry_meta['created_at'])
        return datetime.now() > created_at + timedelta(seconds=ttl_seconds)
    
    def _cleanup_if_necessary(self):
        """Clean up cache if it exceeds size limit."""
        total_size = sum(
            entry.get('size_bytes', 0) 
            for entry in self.metadata.values()
        )
        
        if total_size <= self.max_size_bytes:
            return
        
        # Sort by last accessed time (LRU)
        sorted_entries = sorted(
            self.metadata.items(),
            key=lambda x: x[1].get('last_accessed', '1970-01-01')
        )
        
        # Remove oldest entries until under limit
        for key, entry_meta in sorted_entries:
            if total_size <= self.max_size_bytes:
                break
            
            self.remove(key)
            total_size -= entry_meta.get('size_bytes', 0)


class CacheManager:
    """Manages multiple cache layers (memory + disk)."""
    
    def __init__(self, 
                 memory_cache_size: int = 100,
                 disk_cache_size_mb: int = 500,
                 default_ttl: Optional[int] = None):
        """
        Initialize cache manager.
        
        Args:
            memory_cache_size: Maximum entries in memory cache
            disk_cache_size_mb: Maximum disk cache size in MB
            default_ttl: Default time-to-live in seconds
        """
        self.memory_cache = MemoryCache(memory_cache_size, default_ttl)
        self.disk_cache = DiskCache(max_size_mb=disk_cache_size_mb)
        self.logger = get_logger(self.__class__.__name__)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (memory first, then disk)."""
        # Try memory cache first
        value = self.memory_cache.get(key)
        if value is not None:
            return value
        
        # Try disk cache
        value = self.disk_cache.get(key)
        if value is not None:
            # Promote to memory cache
            self.memory_cache.put(key, value)
            return value
        
        return None
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None, 
            memory_only: bool = False) -> None:
        """Put value in cache."""
        # Always put in memory cache
        self.memory_cache.put(key, value, ttl)
        
        # Put in disk cache unless memory_only is True
        if not memory_only:
            self.disk_cache.put(key, value, ttl)
    
    def remove(self, key: str) -> bool:
        """Remove from both caches."""
        memory_removed = self.memory_cache.remove(key)
        disk_removed = self.disk_cache.remove(key)
        return memory_removed or disk_removed
    
    def clear(self) -> None:
        """Clear both caches."""
        self.memory_cache.clear()
        self.disk_cache.clear()
    
    def cleanup_expired(self) -> Dict[str, int]:
        """Clean up expired entries in both caches."""
        memory_cleaned = self.memory_cache.cleanup_expired()
        disk_cleaned = self.disk_cache.cleanup_expired()
        
        return {
            'memory_cleaned': memory_cleaned,
            'disk_cleaned': disk_cleaned,
            'total_cleaned': memory_cleaned + disk_cleaned
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return {
            'memory_cache': self.memory_cache.get_stats(),
            'disk_cache': self.disk_cache.get_stats()
        }


class CachedFunction:
    """Decorator for caching function results."""
    
    def __init__(self, 
                 cache_manager: CacheManager,
                 ttl: Optional[int] = None,
                 key_func: Optional[Callable] = None,
                 memory_only: bool = False):
        """
        Initialize cached function decorator.
        
        Args:
            cache_manager: Cache manager to use
            ttl: Time-to-live for cached results
            key_func: Function to generate cache key from arguments
            memory_only: Whether to use memory cache only
        """
        self.cache_manager = cache_manager
        self.ttl = ttl
        self.key_func = key_func or self._default_key_func
        self.memory_only = memory_only
    
    def __call__(self, func: Callable) -> Callable:
        """Decorate function with caching."""
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = self.key_func(func.__name__, args, kwargs)
            
            # Try to get from cache
            result = self.cache_manager.get(cache_key)
            if result is not None:
                return result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            self.cache_manager.put(cache_key, result, self.ttl, self.memory_only)
            
            return result
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.cache_clear = lambda: self._clear_function_cache(func.__name__)
        
        return wrapper
    
    def _default_key_func(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate default cache key."""
        key_data = {
            'function': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _clear_function_cache(self, func_name: str):
        """Clear cache entries for a specific function."""
        # This is a simplified implementation
        # In practice, you'd need to track which keys belong to which functions
        pass


# Global cache manager instance
_global_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    return _global_cache_manager


def cached(ttl: Optional[int] = None, 
          key_func: Optional[Callable] = None,
          memory_only: bool = False):
    """Decorator for caching function results."""
    cache_manager = get_cache_manager()
    return CachedFunction(cache_manager, ttl, key_func, memory_only)