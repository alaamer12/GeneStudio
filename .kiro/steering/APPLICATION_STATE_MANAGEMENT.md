# GeneStudio Pro - Application State Management

This document describes the application state management features implemented in GeneStudio Pro, including window state persistence, platform-specific data storage, and user interface enhancements.

## Window State Management

### Features

- **Automatic State Persistence**: Window size, position, and maximization state are automatically saved
- **Minimum Dimensions**: Enforced minimum window size of 1200x700 pixels
- **Smart Restoration**: Window state is restored on application startup
- **Cross-Session Memory**: Last active page is remembered between sessions
- **Screen Boundary Validation**: Ensures windows remain visible on screen

### Implementation

The `WindowStateManager` class handles all window state operations:

```python
from utils.window_state_manager import WindowStateManager

# Initialize in main window
self.window_state_manager = WindowStateManager()

# Restore previous state
self.window_state_manager.restore_window_state(self)

# Set up automatic saving
self.window_state_manager.setup_window_callbacks(self)
```

### Configuration File

Window state is stored in: `~/.genestudio/<user>/window_state.json`

```json
{
  "geometry": "1400x900+100+50",
  "maximized": false,
  "minimized": false,
  "last_page": "dashboard",
  "last_saved": "2024-12-12T10:30:00"
}
```

## Platform Directory Management

### Directory Structure

GeneStudio Pro uses the standard `platformdirs` library for cross-platform directory management:

```
# Windows Example:
%APPDATA%/GeneStudio/<username>/     # User data
%LOCALAPPDATA%/GeneStudio/<username>/ # Cache
%APPDATA%/GeneStudio/<username>/     # Config

# macOS/Linux Example:
~/.local/share/GeneStudio/<username>/  # User data
~/.cache/GeneStudio/<username>/        # Cache
~/.config/GeneStudio/<username>/       # Config

# Structure within each:
├── <username>/          # Named user profile
│   ├── database/        # Database files
│   ├── projects/        # User projects
│   ├── exports/         # Exported data
│   └── temp/            # Temporary files
└── temp/                # Anonymous user data
```

### User Profile Detection

- **Named Users**: Uses system username (`getpass.getuser()`)
- **Anonymous Users**: Falls back to `temp/` directory
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Directory Functions

```python
from utils.platform_dirs import (
    get_app_data_dir,
    get_database_dir,
    get_config_dir,
    get_projects_dir
)

# Get user-specific directories
db_dir = get_database_dir()  # ~/.genestudio/<user>/database/
config_dir = get_config_dir()  # ~/.genestudio/<user>/config/
```

### Automatic Cleanup

- Temporary files older than 7 days are automatically cleaned
- Cache files are managed to prevent excessive disk usage
- Log rotation prevents log files from growing too large

## Toast Notification System

### Enhanced Design

The toast notification system has been redesigned with theme-aligned styling for better user experience:

#### Visual Improvements

- **Theme-Aligned Styling**: Subtle colors that match the dark theme instead of bright colors
- **Circular Colored Icons**: Icons are displayed in circular containers with state-specific colors
- **Professional Appearance**: Clean, modern design that fits the enterprise aesthetic
- **Better Positioning**: Always appears in bottom-right corner with proper spacing
- **Responsive Layout**: Adapts to window size and prevents cut-off

#### Positioning Logic

```python
# Bottom-right positioning with upward stacking
x = container_width - toast_width - margin
y = container_height - margin - toast_height - (stack_index * spacing)

# Boundary validation
x = max(margin, min(x, container_width - toast_width - margin))
y = max(margin, min(y, container_height - toast_height - margin))
```

#### Toast Types

- **Success**: Green with checkmark icon
- **Error**: Red with X icon  
- **Info**: Blue with info icon
- **Warning**: Orange with warning icon

### Usage

```python
from views.components.toast_notifications import show_success, show_error

# Show notifications
show_success("Operation completed successfully!")
show_error("Failed to save file. Please try again.")
show_info("Loading data...", duration=5000)
show_warning("Large dataset detected.")
```

## Application Lifecycle

### Startup Sequence

1. **Initialize Platform Directories**: Create user-specific folders
2. **Restore Window State**: Apply saved geometry and position
3. **Set Minimum Dimensions**: Enforce 1200x700 minimum size
4. **Load Last Page**: Navigate to previously active page
5. **Set Up Auto-Save**: Configure periodic state saving

### Shutdown Sequence

1. **Save Window State**: Store current geometry and maximization
2. **Save Last Page**: Remember active page for next session
3. **Cleanup Temp Files**: Remove old temporary files
4. **Close Database Connections**: Properly close all DB connections

### Periodic Maintenance

- **Auto-Save**: Window state saved every 30 seconds
- **Temp Cleanup**: Old files cleaned on startup
- **Log Rotation**: Logs rotated when they exceed size limits

## Configuration Options

### Window Behavior

```python
# Minimum dimensions (can be customized)
min_width = 1200
min_height = 700

# Auto-save interval (milliseconds)
auto_save_interval = 30000

# Default window size for new installations
default_geometry = "1400x900"
```

### Directory Customization

```python
# Custom user profile
custom_profile = "my_profile"
app_dir = get_app_data_dir(custom_profile)

# Directory information
info = get_directory_info()
print(f"User: {info['user_profile']}")
print(f"Database: {info['directories']['database']['path']}")
```

## Error Handling

### Graceful Degradation

- **State Loading Failures**: Falls back to default window state
- **Directory Creation Errors**: Uses fallback locations
- **Permission Issues**: Handles read-only directories gracefully

### Logging

All state management operations are logged for debugging:

```
INFO: Window state restored: 1400x900+100+50
WARNING: Failed to create config directory, using fallback
ERROR: Cannot save window state: Permission denied
```

## Security Considerations

### Data Privacy

- **User Isolation**: Each user's data is stored separately
- **Anonymous Mode**: Temporary directory for privacy-conscious users
- **No Sensitive Data**: Window state contains no sensitive information

### File Permissions

- **Restricted Access**: User directories have appropriate permissions
- **Temp File Cleanup**: Automatic cleanup prevents data accumulation
- **Safe Defaults**: Fallback to safe locations if primary directories fail

## Performance Optimization

### Efficient State Management

- **Debounced Saving**: Rapid window changes don't trigger excessive saves
- **Lazy Directory Creation**: Directories created only when needed
- **Connection Pooling**: Database connections reused per thread

### Memory Management

- **Periodic Cleanup**: Automatic removal of old temporary files
- **Cache Limits**: Configurable cache size limits
- **Resource Monitoring**: Track directory sizes and file counts

## Troubleshooting

### Common Issues

1. **Window Not Restoring**: Check permissions on config directory
2. **Toast Cut-Off**: Ensure minimum window dimensions are met
3. **State Not Saving**: Verify write permissions to user directory

### Debug Information

```python
from utils.platform_dirs import get_directory_info

# Get comprehensive directory information
info = get_directory_info()
print(json.dumps(info, indent=2))
```

### Reset to Defaults

To reset application state:

1. Close GeneStudio Pro
2. Delete `~/.genestudio/<user>/window_state.json`
3. Restart application (will use defaults)

## Future Enhancements

### Planned Features

- **Multi-Monitor Support**: Better handling of multi-monitor setups
- **Theme Persistence**: Remember user's preferred theme
- **Layout Customization**: Save custom panel layouts
- **Backup/Restore**: Export/import application state

### Configuration UI

A future settings page will allow users to:

- Configure auto-save intervals
- Set custom directory locations
- Manage cleanup policies
- View storage usage statistics