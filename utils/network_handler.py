"""Network error handling for non-critical operations with silent failures."""

import requests
import time
import threading
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from urllib.parse import urlparse

from utils.error_handling import NetworkError, ErrorContext, handle_error


class NetworkOperationType(Enum):
    """Types of network operations."""
    UPDATE_CHECK = "update_check"
    TELEMETRY = "telemetry"
    FEEDBACK = "feedback"
    DOCUMENTATION = "documentation"
    EXTERNAL_API = "external_api"


@dataclass
class NetworkConfig:
    """Network configuration settings."""
    timeout: float = 10.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    silent_failure: bool = True
    user_agent: str = "GeneStudio/1.0"


@dataclass
class NetworkRequest:
    """Network request definition."""
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, Any]] = None
    json_data: Optional[Dict[str, Any]] = None
    operation_type: NetworkOperationType = NetworkOperationType.EXTERNAL_API
    config: Optional[NetworkConfig] = None


class NetworkResult:
    """Result of network operation."""
    
    def __init__(self, success: bool = False, data: Any = None, 
                 error: Optional[Exception] = None, status_code: Optional[int] = None):
        self.success = success
        self.data = data
        self.error = error
        self.status_code = status_code
        self.response_time = 0.0
        self.retries_used = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'data': self.data,
            'error': str(self.error) if self.error else None,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'retries_used': self.retries_used
        }


class NetworkHandler:
    """Handler for network operations with error handling and retry logic."""
    
    def __init__(self, default_config: Optional[NetworkConfig] = None):
        self.default_config = default_config or NetworkConfig()
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self._setup_session()
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'silent_failures': 0,
            'operation_stats': {}
        }
    
    def _setup_session(self):
        """Setup requests session with default headers."""
        self.session.headers.update({
            'User-Agent': self.default_config.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def make_request(self, request: NetworkRequest) -> NetworkResult:
        """Make a network request with error handling and retries."""
        config = request.config or self.default_config
        result = NetworkResult()
        
        # Update statistics
        self.stats['total_requests'] += 1
        op_type = request.operation_type.value
        if op_type not in self.stats['operation_stats']:
            self.stats['operation_stats'][op_type] = {'total': 0, 'success': 0, 'failed': 0}
        self.stats['operation_stats'][op_type]['total'] += 1
        
        start_time = time.time()
        
        for attempt in range(config.max_retries + 1):
            try:
                result.retries_used = attempt
                
                # Prepare request
                headers = request.headers or {}
                headers.update(self.session.headers)
                
                # Make request
                response = self.session.request(
                    method=request.method,
                    url=request.url,
                    headers=headers,
                    data=request.data,
                    json=request.json_data,
                    timeout=config.timeout
                )
                
                result.status_code = response.status_code
                result.response_time = time.time() - start_time
                
                # Check if request was successful
                if response.ok:
                    try:
                        # Try to parse JSON
                        result.data = response.json()
                    except ValueError:
                        # Not JSON, return text
                        result.data = response.text
                    
                    result.success = True
                    self.stats['successful_requests'] += 1
                    self.stats['operation_stats'][op_type]['success'] += 1
                    
                    self.logger.debug(f"Network request successful: {request.method} {request.url}")
                    return result
                
                else:
                    # HTTP error
                    error = NetworkError(
                        f"HTTP {response.status_code}: {response.reason}",
                        url=request.url,
                        status_code=response.status_code
                    )
                    result.error = error
                    
                    # Don't retry on client errors (4xx)
                    if 400 <= response.status_code < 500:
                        break
            
            except requests.exceptions.Timeout as e:
                result.error = NetworkError(
                    f"Request timeout after {config.timeout}s",
                    url=request.url,
                    cause=e
                )
            
            except requests.exceptions.ConnectionError as e:
                result.error = NetworkError(
                    f"Connection error: {e}",
                    url=request.url,
                    cause=e
                )
            
            except requests.exceptions.RequestException as e:
                result.error = NetworkError(
                    f"Request error: {e}",
                    url=request.url,
                    cause=e
                )
            
            except Exception as e:
                result.error = NetworkError(
                    f"Unexpected error: {e}",
                    url=request.url,
                    cause=e
                )
            
            # Wait before retry (except on last attempt)
            if attempt < config.max_retries:
                delay = config.retry_delay * (config.retry_backoff ** attempt)
                self.logger.debug(f"Retrying request in {delay:.1f}s (attempt {attempt + 1}/{config.max_retries})")
                time.sleep(delay)
        
        # All attempts failed
        result.response_time = time.time() - start_time
        self.stats['failed_requests'] += 1
        self.stats['operation_stats'][op_type]['failed'] += 1
        
        # Handle error based on configuration
        if config.silent_failure:
            self.stats['silent_failures'] += 1
            self.logger.debug(f"Network request failed silently: {request.method} {request.url} - {result.error}")
        else:
            context = ErrorContext(
                operation="network_request",
                component="network_handler",
                additional_data={
                    'url': request.url,
                    'method': request.method,
                    'operation_type': request.operation_type.value
                }
            )
            handle_error(result.error, context, suppress=False)
        
        return result
    
    def get(self, url: str, operation_type: NetworkOperationType = NetworkOperationType.EXTERNAL_API,
            **kwargs) -> NetworkResult:
        """Make GET request."""
        request = NetworkRequest(
            url=url,
            method="GET",
            operation_type=operation_type,
            **kwargs
        )
        return self.make_request(request)
    
    def post(self, url: str, data: Optional[Dict[str, Any]] = None,
             json_data: Optional[Dict[str, Any]] = None,
             operation_type: NetworkOperationType = NetworkOperationType.EXTERNAL_API,
             **kwargs) -> NetworkResult:
        """Make POST request."""
        request = NetworkRequest(
            url=url,
            method="POST",
            data=data,
            json_data=json_data,
            operation_type=operation_type,
            **kwargs
        )
        return self.make_request(request)
    
    def put(self, url: str, data: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            operation_type: NetworkOperationType = NetworkOperationType.EXTERNAL_API,
            **kwargs) -> NetworkResult:
        """Make PUT request."""
        request = NetworkRequest(
            url=url,
            method="PUT",
            data=data,
            json_data=json_data,
            operation_type=operation_type,
            **kwargs
        )
        return self.make_request(request)
    
    def delete(self, url: str, operation_type: NetworkOperationType = NetworkOperationType.EXTERNAL_API,
               **kwargs) -> NetworkResult:
        """Make DELETE request."""
        request = NetworkRequest(
            url=url,
            method="DELETE",
            operation_type=operation_type,
            **kwargs
        )
        return self.make_request(request)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get network operation statistics."""
        return self.stats.copy()
    
    def reset_statistics(self):
        """Reset network statistics."""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'silent_failures': 0,
            'operation_stats': {}
        }
    
    def close(self):
        """Close the session."""
        self.session.close()


class UpdateChecker:
    """Check for application updates from GitHub releases."""
    
    def __init__(self, repo_owner: str, repo_name: str, current_version: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.network_handler = NetworkHandler(NetworkConfig(silent_failure=True))
        self.logger = logging.getLogger(__name__)
    
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """Check for updates from GitHub releases."""
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        
        result = self.network_handler.get(
            url,
            operation_type=NetworkOperationType.UPDATE_CHECK
        )
        
        if not result.success:
            self.logger.debug("Update check failed - no internet connection or GitHub unavailable")
            return None
        
        try:
            release_data = result.data
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            if self._is_newer_version(latest_version, self.current_version):
                return {
                    'version': latest_version,
                    'name': release_data.get('name', ''),
                    'body': release_data.get('body', ''),
                    'html_url': release_data.get('html_url', ''),
                    'published_at': release_data.get('published_at', ''),
                    'assets': release_data.get('assets', [])
                }
            
            return None  # No update available
            
        except Exception as e:
            self.logger.debug(f"Error parsing update information: {e}")
            return None
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings."""
        try:
            # Simple version comparison (assumes semantic versioning)
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return latest_parts > current_parts
            
        except ValueError:
            # Fallback to string comparison
            return latest > current
    
    def check_for_updates_async(self, callback: Callable[[Optional[Dict[str, Any]]], None]):
        """Check for updates asynchronously."""
        def check_task():
            update_info = self.check_for_updates()
            callback(update_info)
        
        thread = threading.Thread(target=check_task, daemon=True)
        thread.start()


class TelemetryCollector:
    """Collect and send anonymous usage telemetry."""
    
    def __init__(self, endpoint_url: str, app_version: str):
        self.endpoint_url = endpoint_url
        self.app_version = app_version
        self.network_handler = NetworkHandler(NetworkConfig(silent_failure=True))
        self.logger = logging.getLogger(__name__)
        self.enabled = False  # Disabled by default
    
    def enable_telemetry(self):
        """Enable telemetry collection."""
        self.enabled = True
        self.logger.info("Telemetry collection enabled")
    
    def disable_telemetry(self):
        """Disable telemetry collection."""
        self.enabled = False
        self.logger.info("Telemetry collection disabled")
    
    def send_event(self, event_type: str, data: Dict[str, Any]):
        """Send telemetry event."""
        if not self.enabled:
            return
        
        telemetry_data = {
            'event_type': event_type,
            'app_version': self.app_version,
            'timestamp': time.time(),
            'data': data
        }
        
        result = self.network_handler.post(
            self.endpoint_url,
            json_data=telemetry_data,
            operation_type=NetworkOperationType.TELEMETRY
        )
        
        if result.success:
            self.logger.debug(f"Telemetry event sent: {event_type}")
        else:
            self.logger.debug(f"Telemetry event failed: {event_type}")
    
    def send_event_async(self, event_type: str, data: Dict[str, Any]):
        """Send telemetry event asynchronously."""
        def send_task():
            self.send_event(event_type, data)
        
        thread = threading.Thread(target=send_task, daemon=True)
        thread.start()


class DocumentationFetcher:
    """Fetch documentation and help content from remote sources."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.network_handler = NetworkHandler(NetworkConfig(silent_failure=True))
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour
    
    def get_help_content(self, topic: str) -> Optional[str]:
        """Get help content for a topic."""
        # Check cache first
        cache_key = f"help_{topic}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return cached_data
        
        url = f"{self.base_url}/help/{topic}.md"
        result = self.network_handler.get(
            url,
            operation_type=NetworkOperationType.DOCUMENTATION
        )
        
        if result.success and isinstance(result.data, str):
            # Cache the result
            self.cache[cache_key] = (result.data, time.time())
            return result.data
        
        return None
    
    def get_changelog(self) -> Optional[str]:
        """Get application changelog."""
        cache_key = "changelog"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return cached_data
        
        url = f"{self.base_url}/CHANGELOG.md"
        result = self.network_handler.get(
            url,
            operation_type=NetworkOperationType.DOCUMENTATION
        )
        
        if result.success and isinstance(result.data, str):
            self.cache[cache_key] = (result.data, time.time())
            return result.data
        
        return None
    
    def clear_cache(self):
        """Clear documentation cache."""
        self.cache.clear()


# Global network handler instance
_network_handler = None


def get_network_handler() -> NetworkHandler:
    """Get the global network handler instance."""
    global _network_handler
    if _network_handler is None:
        _network_handler = NetworkHandler()
    return _network_handler


def make_safe_request(url: str, method: str = "GET", **kwargs) -> NetworkResult:
    """Make a safe network request that fails silently."""
    handler = get_network_handler()
    
    request = NetworkRequest(
        url=url,
        method=method,
        config=NetworkConfig(silent_failure=True),
        **kwargs
    )
    
    return handler.make_request(request)


def check_internet_connectivity() -> bool:
    """Check if internet connectivity is available."""
    test_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://httpbin.org/get"
    ]
    
    handler = NetworkHandler(NetworkConfig(
        timeout=5.0,
        max_retries=1,
        silent_failure=True
    ))
    
    for url in test_urls:
        result = handler.get(url, operation_type=NetworkOperationType.EXTERNAL_API)
        if result.success:
            return True
    
    return False


def validate_url(url: str) -> bool:
    """Validate URL format and accessibility."""
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return False
        
        # Quick connectivity check
        handler = NetworkHandler(NetworkConfig(
            timeout=3.0,
            max_retries=1,
            silent_failure=True
        ))
        
        result = handler.get(url, operation_type=NetworkOperationType.EXTERNAL_API)
        return result.success
        
    except Exception:
        return False


def download_file_safe(url: str, filepath: str, chunk_size: int = 8192) -> bool:
    """Safely download a file with error handling."""
    try:
        handler = get_network_handler()
        
        # Stream download
        response = handler.session.get(url, stream=True, timeout=30.0)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        
        return True
        
    except Exception as e:
        # Silent failure for downloads
        logging.getLogger(__name__).debug(f"File download failed: {e}")
        return False