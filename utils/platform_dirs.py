"""Platform-specific directory management for GeneStudio Pro using platformdirs."""

import getpass
from pathlib import Path
from typing import Optional
from platformdirs import user_data_dir, user_config_dir, user_cache_dir, user_log_dir


def get_user_profile() -> str:
    """Get current user profile name."""
    try:
        return getpass.getuser()
    except Exception:
        return "anonymous"


def get_app_data_dir(user_profile: Optional[str] = None) -> Path:
    """
    Get application data directory based on user profile.
    
    Structure:
    - Uses platformdirs for cross-platform compatibility
    - For named users: <user_data_dir>/GeneStudio/<username>/
    - For anonymous users: <user_data_dir>/GeneStudio/temp/
    
    Args:
        user_profile: Optional user profile name. If None, uses current user.
        
    Returns:
        Path to application data directory
    """
    if user_profile is None:
        user_profile = get_user_profile()
    
    # Use anonymous temp directory for unknown users
    if user_profile in ("anonymous", "unknown", "", None):
        user_profile = "temp"
    
    # Get platform-specific user data directory
    base_dir = Path(user_data_dir("GeneStudio", "GeneStudio"))
    app_dir = base_dir / user_profile
    
    # Ensure directory exists
    app_dir.mkdir(parents=True, exist_ok=True)
    
    return app_dir


def get_database_dir(user_profile: Optional[str] = None) -> Path:
    """Get database directory for user profile."""
    app_dir = get_app_data_dir(user_profile)
    db_dir = app_dir / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir


def get_config_dir(user_profile: Optional[str] = None) -> Path:
    """Get configuration directory for user profile."""
    if user_profile is None:
        user_profile = get_user_profile()
    
    if user_profile in ("anonymous", "unknown", "", None):
        user_profile = "temp"
    
    # Use platformdirs for config directory
    base_dir = Path(user_config_dir("GeneStudio", "GeneStudio"))
    config_dir = base_dir / user_profile
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_cache_dir(user_profile: Optional[str] = None) -> Path:
    """Get cache directory for user profile."""
    if user_profile is None:
        user_profile = get_user_profile()
    
    if user_profile in ("anonymous", "unknown", "", None):
        user_profile = "temp"
    
    # Use platformdirs for cache directory
    base_dir = Path(user_cache_dir("GeneStudio", "GeneStudio"))
    cache_dir = base_dir / user_profile
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_logs_dir(user_profile: Optional[str] = None) -> Path:
    """Get logs directory for user profile."""
    if user_profile is None:
        user_profile = get_user_profile()
    
    if user_profile in ("anonymous", "unknown", "", None):
        user_profile = "temp"
    
    # Use platformdirs for logs directory
    base_dir = Path(user_log_dir("GeneStudio", "GeneStudio"))
    logs_dir = base_dir / user_profile
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_projects_dir(user_profile: Optional[str] = None) -> Path:
    """Get projects directory for user profile."""
    app_dir = get_app_data_dir(user_profile)
    projects_dir = app_dir / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    return projects_dir


def get_exports_dir(user_profile: Optional[str] = None) -> Path:
    """Get exports directory for user profile."""
    app_dir = get_app_data_dir(user_profile)
    exports_dir = app_dir / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir


def get_temp_dir(user_profile: Optional[str] = None) -> Path:
    """Get temporary directory for user profile."""
    app_dir = get_app_data_dir(user_profile)
    temp_dir = app_dir / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def cleanup_temp_files(user_profile: Optional[str] = None, max_age_days: int = 7) -> None:
    """
    Clean up temporary files older than specified days.
    
    Args:
        user_profile: User profile name
        max_age_days: Maximum age of files to keep in days
    """
    import time
    
    temp_dir = get_temp_dir(user_profile)
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60
    
    try:
        for file_path in temp_dir.rglob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                    except OSError:
                        pass  # Ignore files that can't be deleted
    except Exception:
        pass  # Ignore cleanup errors


def get_directory_info(user_profile: Optional[str] = None) -> dict:
    """
    Get information about all application directories.
    
    Returns:
        Dictionary with directory paths and sizes
    """
    if user_profile is None:
        user_profile = get_user_profile()
    
    directories = {
        "app_data": get_app_data_dir(user_profile),
        "database": get_database_dir(user_profile),
        "config": get_config_dir(user_profile),
        "cache": get_cache_dir(user_profile),
        "logs": get_logs_dir(user_profile),
        "projects": get_projects_dir(user_profile),
        "exports": get_exports_dir(user_profile),
        "temp": get_temp_dir(user_profile)
    }
    
    info = {
        "user_profile": user_profile,
        "directories": {}
    }
    
    for name, path in directories.items():
        try:
            size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
            file_count = len([f for f in path.rglob("*") if f.is_file()])
            
            info["directories"][name] = {
                "path": str(path),
                "exists": path.exists(),
                "size_bytes": size,
                "file_count": file_count
            }
        except Exception:
            info["directories"][name] = {
                "path": str(path),
                "exists": path.exists(),
                "size_bytes": 0,
                "file_count": 0
            }
    
    return info


# Initialize directories on import
def initialize_directories(user_profile: Optional[str] = None) -> None:
    """Initialize all application directories."""
    get_app_data_dir(user_profile)
    get_database_dir(user_profile)
    get_config_dir(user_profile)
    get_cache_dir(user_profile)
    get_logs_dir(user_profile)
    get_projects_dir(user_profile)
    get_exports_dir(user_profile)
    get_temp_dir(user_profile)


# Auto-initialize on import
initialize_directories()