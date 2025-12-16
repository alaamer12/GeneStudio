"""Pagination and lazy loading utilities for large datasets."""

from typing import List, Dict, Any, Optional, Callable, TypeVar, Generic
from dataclasses import dataclass
import threading
import time
from utils.logger import get_logger

T = TypeVar('T')


@dataclass
class PageInfo:
    """Information about a page in paginated results."""
    page_number: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool
    start_index: int
    end_index: int


class PaginatedResult(Generic[T]):
    """Container for paginated results."""
    
    def __init__(self, items: List[T], page_info: PageInfo):
        self.items = items
        self.page_info = page_info
    
    def __len__(self) -> int:
        return len(self.items)
    
    def __iter__(self):
        return iter(self.items)
    
    def __getitem__(self, index):
        return self.items[index]


class LazyLoader(Generic[T]):
    """Lazy loader for large datasets with caching."""
    
    def __init__(self, 
                 data_loader: Callable[[int, int], List[T]],
                 total_count_loader: Callable[[], int],
                 page_size: int = 50,
                 cache_size: int = 5):
        """
        Initialize lazy loader.
        
        Args:
            data_loader: Function that loads data for a page (offset, limit)
            total_count_loader: Function that returns total item count
            page_size: Number of items per page
            cache_size: Number of pages to cache
        """
        self.data_loader = data_loader
        self.total_count_loader = total_count_loader
        self.page_size = page_size
        self.cache_size = cache_size
        
        self._cache = {}
        self._cache_order = []
        self._total_count = None
        self._lock = threading.Lock()
        self.logger = get_logger(self.__class__.__name__)
    
    def get_page(self, page_number: int) -> PaginatedResult[T]:
        """Get a specific page of data."""
        with self._lock:
            # Validate page number
            total_count = self._get_total_count()
            total_pages = (total_count + self.page_size - 1) // self.page_size
            
            if page_number < 0 or (total_pages > 0 and page_number >= total_pages):
                raise ValueError(f"Page {page_number} out of range (0-{total_pages-1})")
            
            # Check cache first
            if page_number in self._cache:
                self._update_cache_order(page_number)
                items = self._cache[page_number]
            else:
                # Load data
                offset = page_number * self.page_size
                items = self.data_loader(offset, self.page_size)
                
                # Cache the result
                self._add_to_cache(page_number, items)
            
            # Create page info
            page_info = PageInfo(
                page_number=page_number,
                page_size=self.page_size,
                total_items=total_count,
                total_pages=total_pages,
                has_previous=page_number > 0,
                has_next=page_number < total_pages - 1,
                start_index=page_number * self.page_size,
                end_index=min((page_number + 1) * self.page_size, total_count)
            )
            
            return PaginatedResult(items, page_info)
    
    def get_items(self, start_index: int, count: int) -> List[T]:
        """Get items by index range (may span multiple pages)."""
        items = []
        current_index = start_index
        remaining_count = count
        
        while remaining_count > 0:
            page_number = current_index // self.page_size
            page_offset = current_index % self.page_size
            
            try:
                page_result = self.get_page(page_number)
                page_items = page_result.items[page_offset:]
                
                # Take only what we need
                items_to_take = min(len(page_items), remaining_count)
                items.extend(page_items[:items_to_take])
                
                current_index += items_to_take
                remaining_count -= items_to_take
                
                # If we didn't get enough items from this page, we're at the end
                if len(page_items) < self.page_size - page_offset:
                    break
                    
            except ValueError:
                # Page out of range
                break
        
        return items
    
    def search_pages(self, 
                    search_func: Callable[[List[T]], List[T]], 
                    max_pages: Optional[int] = None) -> List[T]:
        """Search across pages using a search function."""
        results = []
        total_count = self._get_total_count()
        total_pages = (total_count + self.page_size - 1) // self.page_size
        
        pages_to_search = min(max_pages or total_pages, total_pages)
        
        for page_num in range(pages_to_search):
            try:
                page_result = self.get_page(page_num)
                page_matches = search_func(page_result.items)
                results.extend(page_matches)
            except Exception as e:
                self.logger.warning(f"Error searching page {page_num}: {e}")
                continue
        
        return results
    
    def invalidate_cache(self):
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
            self._cache_order.clear()
            self._total_count = None
    
    def preload_pages(self, page_numbers: List[int]):
        """Preload specific pages into cache."""
        for page_num in page_numbers:
            try:
                self.get_page(page_num)
            except Exception as e:
                self.logger.warning(f"Failed to preload page {page_num}: {e}")
    
    def _get_total_count(self) -> int:
        """Get total count with caching."""
        if self._total_count is None:
            self._total_count = self.total_count_loader()
        return self._total_count
    
    def _add_to_cache(self, page_number: int, items: List[T]):
        """Add page to cache with LRU eviction."""
        # Remove oldest pages if cache is full
        while len(self._cache) >= self.cache_size:
            oldest_page = self._cache_order.pop(0)
            del self._cache[oldest_page]
        
        self._cache[page_number] = items
        self._cache_order.append(page_number)
    
    def _update_cache_order(self, page_number: int):
        """Update cache order for LRU."""
        if page_number in self._cache_order:
            self._cache_order.remove(page_number)
            self._cache_order.append(page_number)


class VirtualScrollManager:
    """Manages virtual scrolling for large lists."""
    
    def __init__(self, 
                 total_items: int,
                 visible_items: int = 20,
                 buffer_items: int = 10):
        """
        Initialize virtual scroll manager.
        
        Args:
            total_items: Total number of items in the list
            visible_items: Number of items visible at once
            buffer_items: Number of items to buffer above/below visible area
        """
        self.total_items = total_items
        self.visible_items = visible_items
        self.buffer_items = buffer_items
        
        self.scroll_position = 0
        self.item_height = 25  # Default item height in pixels
        
    def get_visible_range(self) -> tuple[int, int]:
        """Get the range of items that should be rendered."""
        # Calculate which items are visible based on scroll position
        first_visible = max(0, self.scroll_position // self.item_height)
        last_visible = min(self.total_items - 1, 
                          first_visible + self.visible_items - 1)
        
        # Add buffer
        start_index = max(0, first_visible - self.buffer_items)
        end_index = min(self.total_items - 1, 
                       last_visible + self.buffer_items)
        
        return start_index, end_index + 1
    
    def update_scroll_position(self, scroll_y: int):
        """Update scroll position and return if visible range changed."""
        old_range = self.get_visible_range()
        self.scroll_position = max(0, scroll_y)
        new_range = self.get_visible_range()
        
        return old_range != new_range
    
    def get_total_height(self) -> int:
        """Get total height of the virtual list."""
        return self.total_items * self.item_height
    
    def get_offset_for_index(self, index: int) -> int:
        """Get scroll offset for a specific item index."""
        return index * self.item_height


class ChunkedProcessor:
    """Processes large datasets in chunks to avoid memory issues."""
    
    def __init__(self, chunk_size: int = 1000):
        """
        Initialize chunked processor.
        
        Args:
            chunk_size: Number of items to process in each chunk
        """
        self.chunk_size = chunk_size
        self.logger = get_logger(self.__class__.__name__)
    
    def process_in_chunks(self, 
                         data_source: Callable[[int, int], List[T]],
                         processor: Callable[[List[T]], Any],
                         total_count: int,
                         progress_callback: Optional[Callable[[float], None]] = None) -> List[Any]:
        """
        Process data in chunks.
        
        Args:
            data_source: Function to get data chunk (offset, limit)
            processor: Function to process each chunk
            total_count: Total number of items to process
            progress_callback: Optional progress callback
            
        Returns:
            List of results from processing each chunk
        """
        results = []
        processed_count = 0
        
        while processed_count < total_count:
            # Calculate chunk size for this iteration
            current_chunk_size = min(self.chunk_size, total_count - processed_count)
            
            try:
                # Get chunk data
                chunk_data = data_source(processed_count, current_chunk_size)
                
                if not chunk_data:
                    break
                
                # Process chunk
                chunk_result = processor(chunk_data)
                results.append(chunk_result)
                
                processed_count += len(chunk_data)
                
                # Update progress
                if progress_callback:
                    progress = processed_count / total_count
                    progress_callback(progress)
                
                # Log progress
                if processed_count % (self.chunk_size * 10) == 0:
                    self.logger.info(f"Processed {processed_count}/{total_count} items")
                
            except Exception as e:
                self.logger.error(f"Error processing chunk at offset {processed_count}: {e}")
                # Continue with next chunk or break based on error handling strategy
                processed_count += current_chunk_size
                continue
        
        return results
    
    def stream_process(self,
                      data_source: Callable[[int, int], List[T]],
                      processor: Callable[[T], Any],
                      total_count: int,
                      progress_callback: Optional[Callable[[float], None]] = None):
        """
        Stream process items one by one (generator).
        
        Args:
            data_source: Function to get data chunk (offset, limit)
            processor: Function to process each item
            total_count: Total number of items to process
            progress_callback: Optional progress callback
            
        Yields:
            Processed items
        """
        processed_count = 0
        
        while processed_count < total_count:
            current_chunk_size = min(self.chunk_size, total_count - processed_count)
            
            try:
                chunk_data = data_source(processed_count, current_chunk_size)
                
                if not chunk_data:
                    break
                
                for item in chunk_data:
                    try:
                        result = processor(item)
                        yield result
                        
                        processed_count += 1
                        
                        # Update progress periodically
                        if progress_callback and processed_count % 100 == 0:
                            progress = processed_count / total_count
                            progress_callback(progress)
                            
                    except Exception as e:
                        self.logger.warning(f"Error processing item: {e}")
                        processed_count += 1
                        continue
                
            except Exception as e:
                self.logger.error(f"Error loading chunk at offset {processed_count}: {e}")
                processed_count += current_chunk_size
                continue


class DebounceManager:
    """Manages debounced operations to prevent excessive calls."""
    
    def __init__(self):
        self._timers = {}
        self._lock = threading.Lock()
    
    def debounce(self, 
                key: str, 
                func: Callable, 
                delay: float = 0.3,
                *args, **kwargs):
        """
        Debounce a function call.
        
        Args:
            key: Unique key for the operation
            func: Function to call
            delay: Delay in seconds
            *args, **kwargs: Arguments for the function
        """
        with self._lock:
            # Cancel existing timer for this key
            if key in self._timers:
                self._timers[key].cancel()
            
            # Create new timer
            timer = threading.Timer(delay, func, args, kwargs)
            self._timers[key] = timer
            timer.start()
    
    def cancel(self, key: str):
        """Cancel a debounced operation."""
        with self._lock:
            if key in self._timers:
                self._timers[key].cancel()
                del self._timers[key]
    
    def cancel_all(self):
        """Cancel all debounced operations."""
        with self._lock:
            for timer in self._timers.values():
                timer.cancel()
            self._timers.clear()


# Global debounce manager instance
_debounce_manager = DebounceManager()


def debounce_call(key: str, func: Callable, delay: float = 0.3, *args, **kwargs):
    """Convenience function for debouncing calls."""
    _debounce_manager.debounce(key, func, delay, *args, **kwargs)


def cancel_debounced_call(key: str):
    """Cancel a specific debounced call."""
    _debounce_manager.cancel(key)