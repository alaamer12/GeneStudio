# GeneStudio Pro - UX Patterns & Guidelines

ALWAYS RUN FROM `.venv`. ie. `.venv\scripts\python <command>`
IF YOU ARE GOING TO RUN THE GUI [ie. main.py] just compile it or RUN IT with time off to terminate if it passed without errors

## Loading States & User Feedback

### Always Show Loading States
- **Never leave users wondering** - Show immediate feedback for all actions
- **Use skeleton screens** for known layouts (cards, tables, text blocks)
- **Show progress indicators** for operations with known duration
- **Provide cancellation** for long-running operations where possible

### Loading Component Hierarchy
```python
# 1. Skeleton screens (preferred for known layouts)
SkeletonCard(parent)  # Matches actual card size with shimmer
SkeletonTable(parent, rows=5)  # Table row placeholders
SkeletonText(parent, lines=3)  # Text block placeholders

# 2. Progress indicators (for operations with progress)
LinearProgress(parent, mode="determinate")  # 0-100% progress
LinearProgress(parent, mode="indeterminate")  # Unknown duration
CircularProgress(parent)  # Compact spinner

# 3. Loading overlays (for full-page loading)
LoadingOverlay(parent, message="Loading sequences...")
```

### Timing Guidelines
- **Show skeleton after 200ms delay** - Avoid flash for fast operations
- **Switch to progress bar after 2s** - For longer operations
- **Provide cancellation after 5s** - For very long operations

## Error Handling & Recovery

### Error Boundary Pattern
```python
# Wrap all pages in error boundaries
class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.boundary = ErrorBoundary(
            self,
            content=self._render_content,
            fallback=ErrorFallback,
            on_retry=self._retry_load
        )
        self.boundary.pack(fill="both", expand=True)
```

### Error Message Guidelines
- **Be specific** - "File not found: sequences.fasta" not "Error occurred"
- **Provide solutions** - "Check file path and permissions"
- **Offer retry** - Always provide retry button for recoverable errors
- **Log details** - Log full error for debugging, show friendly message to user

### Error Types & Handling
```python
# File errors
try:
    sequences = read_fasta(filepath)
except FileNotFoundError:
    show_error("File not found. Please check the file path.")
except PermissionError:
    show_error("Permission denied. Please check file permissions.")
except ValueError as e:
    show_error(f"Invalid file format: {str(e)}")

# Network errors (for update checker)
try:
    update_info = check_for_updates()
except requests.ConnectionError:
    # Fail silently for non-critical features
    log_warning("Could not check for updates - no internet connection")
```

## Toast Notification System

### Notification Types & Usage
```python
from views.components.toast_notifications import show_success, show_error, show_info, show_warning

# Success (green, auto-dismiss 3s)
show_success("Project saved successfully!")
show_success("Analysis completed in 2.3 seconds")

# Error (red, manual dismiss)
show_error("Failed to load file. Please try again.")
show_error("Invalid sequence format detected.")

# Info (blue, auto-dismiss 5s)
show_info("Loading large file, this may take a moment...")
show_info("New version 1.2.0 is available!")

# Warning (orange, manual dismiss)
show_warning("Large dataset detected. Consider using pagination.")
show_warning("Unsaved changes will be lost.")
```

### Toast Positioning & Behavior
- **Position**: Bottom-right corner of main window
- **Stacking**: Stack vertically, newest on top
- **Animation**: Slide in from right, fade out
- **Max visible**: 5 toasts maximum, older ones auto-dismiss

## Empty States & First-Time Experience

### Empty State Guidelines
- **Use large, friendly icons** - Emoji or simple graphics
- **Provide clear next steps** - "Create your first project"
- **Include primary action** - Large, prominent button
- **Add helpful context** - Brief explanation of the feature

### Empty State Components
```python
# Generic empty state
EmptyState(
    parent,
    icon="📁",
    title="No projects yet",
    message="Create your first project to get started with sequence analysis.",
    action_text="Create Project",
    action_callback=self.on_create_project
)

# Specific empty states
EmptyDashboard(parent)  # Welcome message with quick start
EmptyProjects(parent)   # Project templates
EmptySequences(parent)  # Import instructions
EmptyResults(parent)    # Analysis suggestions
```

### Onboarding Flow
1. **Welcome screen** - Brief app overview on first launch
2. **Sample data option** - "Load sample project" for exploration
3. **Contextual help** - Tooltips and hints for key features
4. **Progressive disclosure** - Show advanced features after basic usage

## Tooltips & Contextual Help

### Tooltip Implementation
Install tooltip support: `.venv\scripts\pip install tkinter-tooltip`

```python
import time
import tkinter as tk
import tkinter.ttk as ttk
from tktooltip import ToolTip

# Professional Usage Examples

# 1. Basic static tooltip
button = ctk.CTkButton(parent, text="Analyze")
ToolTip(button, msg="Run sequence analysis with current parameters")

# 2. Dynamic tooltip with function (NOTE: pass function itself, not return value)
status_label = ctk.CTkLabel(parent, text="Status")
ToolTip(status_label, msg=time.asctime, delay=0)  # Shows current time

# 3. Advanced tooltip with theme styling
entry_field = ctk.CTkEntry(parent)
ToolTip(
    widget=entry_field,
    msg="Enter DNA sequence (A, T, G, C only)\nCase insensitive, spaces ignored",
    delay=0.5,  # 500ms delay
    follow=True,  # Follow mouse cursor
    parent_kwargs={"bg": "#2b2b2b", "padx": 8, "pady": 4},
    fg="#ffffff",
    bg="#2b2b2b",
    font=("Arial", 10)
)

# 4. Multi-line tooltip for complex explanations
algorithm_menu = ctk.CTkOptionMenu(parent, values=["Boyer-Moore", "KMP"])
ToolTip(
    algorithm_menu,
    msg="Boyer-Moore: Fast exact pattern matching algorithm\n"
        "• Best for long patterns and large texts\n"
        "• Preprocessing time: O(m + σ)\n"
        "• Search time: O(n) average case",
    delay=0.5,
    parent_kwargs={"bg": "#2b2b2b", "padx": 10, "pady": 6}
)

# 5. Validation tooltip for input fields
sequence_entry = ctk.CTkEntry(parent, placeholder_text="Enter sequence...")
ToolTip(
    sequence_entry,
    msg="Valid DNA characters: A, T, G, C, N\n"
        "• Case insensitive\n"
        "• Spaces and line breaks ignored\n"
        "• Minimum length: 1 nucleotide",
    delay=0.3
)

# 6. Status tooltip with dynamic content
def get_analysis_status():
    return f"Analysis progress: {get_current_progress()}%\nEstimated time remaining: {get_eta()}"

progress_icon = ctk.CTkLabel(parent, text="⚙️")
ToolTip(progress_icon, msg=get_analysis_status, delay=0.2)
```

### When to Use Tooltips
- **Complex controls** - Explain non-obvious functionality
- **Technical terms** - Define bioinformatics terminology
- **Input validation** - Show format requirements
- **Keyboard shortcuts** - Display available shortcuts
- **Status indicators** - Explain icon meanings
- **Disabled controls** - Explain why something is disabled

### Tooltip Guidelines
- **Keep it concise** - Maximum 1-2 sentences
- **Be helpful** - Provide actionable information
- **Use consistent delay** - 500ms standard delay
- **Match theme** - Use application colors and fonts
- **Avoid redundancy** - Don't repeat obvious button text

### Tooltip Categories & Implementation Patterns

```python
# 1. Implicit Tooltips (hover over existing controls)
# Action tooltips for buttons
save_button = ctk.CTkButton(parent, text="Save Project")
ToolTip(save_button, msg="Save project (Ctrl+S)")

analyze_button = ctk.CTkButton(parent, text="Run Analysis")
ToolTip(analyze_button, msg="Execute selected algorithm on current sequence")

# Input validation tooltips
sequence_entry = ctk.CTkEntry(parent)
ToolTip(sequence_entry, msg="Valid DNA: A, T, G, C, N (case insensitive)")

# Status indicator tooltips
status_icon = ctk.CTkLabel(parent, text="⚠️")
ToolTip(status_icon, msg=lambda: f"Analysis running - {get_progress()}% complete")

# 2. Explicit Tooltips (dedicated info buttons)
def create_help_button_with_tooltip(parent, help_text):
    """Create an explicit (i) info button with tooltip."""
    info_button = ctk.CTkButton(
        parent, 
        text="ℹ️", 
        width=20, 
        height=20,
        font=("Arial", 12)
    )
    ToolTip(
        info_button,
        msg=help_text,
        delay=0.1,  # Faster for explicit help
        parent_kwargs={"bg": "#2b2b2b", "padx": 10, "pady": 8}
    )
    return info_button

# Usage of explicit help buttons
gc_label = ctk.CTkLabel(parent, text="GC Content:")
gc_help = create_help_button_with_tooltip(
    parent,
    "GC Content: Percentage of Guanine (G) and Cytosine (C) nucleotides\n\n"
    "• Important for DNA stability and melting temperature\n"
    "• Typical range: 30-70% in most organisms\n"
    "• Higher GC content = higher melting temperature"
)

# Layout: Label + Help button
gc_frame = ctk.CTkFrame(parent)
gc_label.pack(side="left")
gc_help.pack(side="left", padx=(5, 0))

# 3. Technical term tooltips
algorithm_label = ctk.CTkLabel(parent, text="Boyer-Moore Algorithm")
ToolTip(
    algorithm_label,
    msg="Boyer-Moore: Efficient string searching algorithm\n\n"
        "Key Features:\n"
        "• Bad character rule: Skip characters not in pattern\n"
        "• Good suffix rule: Skip based on pattern suffixes\n"
        "• Time complexity: O(n/m) best case, O(nm) worst case\n"
        "• Preprocessing: O(m + σ) where σ is alphabet size"
)

# 4. Disabled control explanations
disabled_button = ctk.CTkButton(parent, text="Export Results", state="disabled")
ToolTip(
    disabled_button,
    msg="Export not available: No analysis results to export\n"
        "Run an analysis first to enable export functionality"
)
```

### Tooltip Best Practices

```python
# ✅ DO: Use functions for dynamic content
def get_file_info():
    return f"File: {current_file}\nSize: {file_size}\nLast modified: {mod_time}"

ToolTip(file_label, msg=get_file_info)

# ❌ DON'T: Use return values (will be static)
ToolTip(file_label, msg=get_file_info())  # Wrong - evaluates once

# ✅ DO: Keep tooltips concise but informative
ToolTip(button, msg="Save current project (Ctrl+S)")

# ❌ DON'T: Write novels in tooltips
ToolTip(button, msg="This button will save your current project to the database...")

# ✅ DO: Use consistent delays
TOOLTIP_DELAYS = {
    "action": 0.5,      # Standard for buttons/actions
    "validation": 0.3,   # Faster for input fields
    "help": 0.1,        # Immediate for explicit help buttons
    "status": 0.2       # Quick for status indicators
}

# ✅ DO: Match application theme
def create_themed_tooltip(widget, message, delay=0.5):
    """Create tooltip with consistent theme styling."""
    return ToolTip(
        widget,
        msg=message,
        delay=delay,
        parent_kwargs={
            "bg": "#2b2b2b",  # Match dark theme
            "padx": 8,
            "pady": 4
        },
        fg="#ffffff",
        bg="#2b2b2b",
        font=("Arial", 10)
    )
```

## Confirmation Dialogs

### When to Use Confirmations
- **Destructive actions** - Delete project, clear data, reset settings
- **Irreversible operations** - Export with overwrite, permanent changes
- **Bulk operations** - Delete multiple items, batch processing
- **Data loss risk** - Close without saving, navigate away from unsaved work

### Confirmation Dialog Types
```python
# Standard confirmation
ConfirmDialog(
    parent,
    title="Save Changes?",
    message="You have unsaved changes. Save before closing?",
    confirm_text="Save",
    cancel_text="Don't Save",
    on_confirm=self.save_and_close,
    on_cancel=self.close_without_saving
)

# Destructive action (red button)
DestructiveActionDialog(
    parent,
    title="Delete Project?",
    message="Are you sure you want to delete 'My Project'? This cannot be undone.",
    confirm_text="Delete",
    on_confirm=lambda: self.delete_project(project_id)
)
```

### Dialog Guidelines
- **Clear consequences** - Explain what will happen
- **Specific details** - Include item names, counts, etc.
- **Appropriate button colors** - Red for destructive, blue for safe
- **Keyboard support** - Enter for confirm, Escape for cancel

## Optimistic UI Updates

### Pattern Implementation
```python
# Update UI immediately, rollback on error
def delete_sequence(self, sequence_id):
    # 1. Optimistically update UI
    self.remove_sequence_from_table(sequence_id)
    
    # 2. Perform actual operation
    def task():
        return self.sequence_service.delete(sequence_id)
    
    def on_success(result):
        show_success("Sequence deleted")
    
    def on_error(error):
        # Rollback UI change
        self.restore_sequence_to_table(sequence_id)
        show_error(f"Failed to delete sequence: {error}")
    
    AsyncExecutor.run_async(task, on_success, on_error)
```

### When to Use Optimistic Updates
- **Fast operations** - Save settings, toggle preferences
- **High success rate** - Operations that rarely fail
- **Immediate feedback needed** - User expects instant response
- **Easy to rollback** - UI changes can be easily reversed

## Accessibility & Keyboard Support

### Keyboard Navigation
- **Tab order** - Logical tab navigation through all interactive elements
- **Focus indicators** - Clear visual focus states
- **Keyboard shortcuts** - Common shortcuts (Ctrl+S, Ctrl+N, Ctrl+F)
- **Escape handling** - Close dialogs, cancel operations

### Common Shortcuts
```python
# Bind keyboard shortcuts in main window
self.bind("<Control-s>", lambda e: self.save_current())
self.bind("<Control-n>", lambda e: self.create_new_project())
self.bind("<Control-o>", lambda e: self.open_project())
self.bind("<Control-f>", lambda e: self.focus_search())
self.bind("<F5>", lambda e: self.refresh_current_page())
```

### Visual Feedback
- **Hover states** - All interactive elements show hover feedback
- **Active states** - Button press feedback
- **Disabled states** - Clear visual indication when controls are disabled
- **Loading states** - Visual indication during processing

## Performance & Responsiveness

### Lazy Loading Strategy
```python
# Load pages only when accessed
class PageManager:
    def show_page(self, name: str):
        if name not in self.loaded_pages:
            self.loaded_pages[name] = self.page_constructors[name](self.parent)
        # Show page
        self.loaded_pages[name].pack(fill="both", expand=True)
```

### Data Pagination
```python
# Handle large datasets with pagination
class PaginatedTable:
    def __init__(self, data, page_size=50):
        self.data = data
        self.page_size = page_size
        self.current_page = 0
    
    def get_current_page_data(self):
        start = self.current_page * self.page_size
        end = start + self.page_size
        return self.data[start:end]
```

### Memory Management
- **Clear matplotlib figures** - Prevent memory leaks in visualizations
- **Limit cache size** - Use LRU cache with reasonable limits
- **Stream large files** - Don't load entire files into memory
- **Cleanup on page switch** - Release resources when navigating away

## Design System

### Color Palette
```python
COLORS = {
    "primary": "#1f6aa5",      # Blue - primary actions
    "secondary": "#144870",    # Dark blue - secondary actions
    "success": "#2fa572",      # Green - success states
    "danger": "#d42f2f",       # Red - destructive actions
    "warning": "#ffa500",      # Orange - warnings
    "info": "#1f6aa5",         # Blue - informational
    "background": "#1a1a1a",   # Dark background
    "surface": "#2b2b2b",      # Card/component background
    "text": "#ffffff",         # Primary text
    "text_secondary": "#a0a0a0" # Secondary text
}
```

### Typography Scale
- **Header**: 24px - Page titles
- **Subheader**: 16px - Section titles
- **Body**: 12px - Regular text
- **Caption**: 10px - Helper text
- **Monospace**: Courier New - Code/sequences

### Spacing System
- **xs**: 4px - Tight spacing
- **sm**: 8px - Small spacing
- **md**: 16px - Medium spacing (default)
- **lg**: 24px - Large spacing
- **xl**: 32px - Extra large spacing

### Animation Guidelines
- **Duration**: 200-300ms for UI transitions
- **Easing**: ease-out for entrances, ease-in for exits
- **Shimmer**: 1.5s ease-in-out infinite for skeleton loading
- **Hover**: 150ms ease-out for interactive feedback

## Implementation Checklist

### UX Components (Milestone 1)
- [ ] Skeleton loading screens for all data-heavy pages
- [ ] Toast notification system with proper positioning
- [ ] Error boundaries on all pages with retry functionality
- [ ] Empty states for all data views with helpful actions
- [ ] Confirmation dialogs for all destructive actions
- [ ] Loading indicators for all async operations

### User Experience Features
- [ ] Optimistic UI updates for fast operations
- [ ] Keyboard shortcuts for common actions
- [ ] Focus management and tab navigation
- [ ] Hover/active/disabled states for all interactive elements
- [ ] Consistent error messaging with actionable solutions
- [ ] Progressive loading for large datasets

### Performance Optimizations
- [ ] Lazy loading for pages and components
- [ ] Pagination for large data tables
- [ ] Memory cleanup on page navigation
- [ ] Caching for expensive operations
- [ ] Async operations for long-running tasks