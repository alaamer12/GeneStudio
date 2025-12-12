# GeneStudio Pro - UX Components Reference

## 📁 Component Structure

All UX components are located in: `views/components/`

```
views/components/
├── buttons.py              # ✅ Existing
├── cards.py                # ✅ Existing
├── tables.py               # ✅ Existing
├── modals.py               # ✅ Existing
├── plots.py                # ✅ Existing
├── charts.py               # ✅ Existing
├── navigation.py           # ✅ Existing
├── header.py               # ✅ Existing
├── footer.py               # ✅ Existing
├── skeleton_loader.py      # ❌ NEW - Milestone 1
├── loading_indicators.py   # ❌ NEW - Milestone 1
├── toast_notifications.py  # ❌ NEW - Milestone 1
├── error_boundary.py       # ❌ NEW - Milestone 1
├── empty_states.py         # ❌ NEW - Milestone 1
└── confirmation_dialog.py  # ❌ NEW - Milestone 1
```

---

## 🎨 New UX Components to Build

### 1. `skeleton_loader.py` - Loading Skeletons

**Purpose:** Show animated placeholders while data loads

**Components:**
```python
class SkeletonCard(ctk.CTkFrame):
    """Animated card placeholder with shimmer effect."""
    
class SkeletonTable(ctk.CTkFrame):
    """Table row placeholders."""
    
class SkeletonText(ctk.CTkFrame):
    """Text block placeholders."""
    
class SkeletonChart(ctk.CTkFrame):
    """Chart placeholders."""
```

**Usage Example:**
```python
# In dashboard_page.py
if self.loading:
    SkeletonCard(self.stats_frame).grid(row=0, column=0)
else:
    StatCard(self.stats_frame, title="Total Sequences", value="42").grid(row=0, column=0)
```

**Features:**
- Animated shimmer effect
- Matches actual component size
- Smooth transition to real content

---

### 2. `loading_indicators.py` - Progress Indicators

**Purpose:** Show progress for operations

**Components:**
```python
class LinearProgress(ctk.CTkProgressBar):
    """Linear progress bar (determinate/indeterminate)."""
    
class CircularProgress(ctk.CTkFrame):
    """Circular spinner."""
    
class LoadingOverlay(ctk.CTkFrame):
    """Full-page loading overlay with message."""
```

**Usage Example:**
```python
# For file upload
progress = LinearProgress(self, mode="determinate")
progress.set(0.5)  # 50%

# For unknown duration
spinner = CircularProgress(self, mode="indeterminate")
spinner.start()

# Full page loading
overlay = LoadingOverlay(self, message="Loading sequences...")
overlay.show()
```

---

### 3. `toast_notifications.py` - Toast System

**Purpose:** Show temporary feedback messages

**Components:**
```python
class ToastManager:
    """Singleton manager for all toasts."""
    
class Toast(ctk.CTkFrame):
    """Individual toast notification."""
    
# Helper functions
def show_success(message: str, duration: int = 3000):
    """Show success toast (green, auto-dismiss)."""
    
def show_error(message: str):
    """Show error toast (red, manual dismiss)."""
    
def show_info(message: str, duration: int = 5000):
    """Show info toast (blue, auto-dismiss)."""
    
def show_warning(message: str):
    """Show warning toast (orange, manual dismiss)."""
```

**Usage Example:**
```python
# After saving project
from views.components.toast_notifications import show_success
show_success("Project saved successfully!")

# After error
from views.components.toast_notifications import show_error
show_error("Failed to load file. Please try again.")
```

**Features:**
- Auto-dismiss for success/info
- Manual dismiss for errors/warnings
- Stack vertically (bottom-right)
- Smooth slide-in animation

---

### 4. `error_boundary.py` - Error Handling

**Purpose:** Gracefully handle and display errors

**Components:**
```python
class ErrorBoundary:
    """Wrapper that catches errors in child components."""
    
class ErrorFallback(ctk.CTkFrame):
    """Error display with retry option."""
    
class RetryButton(ctk.CTkButton):
    """Retry action button."""
```

**Usage Example:**
```python
# Wrap page in error boundary
class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Wrap content in error boundary
        boundary = ErrorBoundary(
            self,
            content=self._render_content,
            fallback=ErrorFallback
        )
        boundary.pack(fill="both", expand=True)
    
    def _render_content(self):
        # Your page content
        # If error occurs, shows ErrorFallback instead
        pass
```

**Features:**
- Catch all exceptions
- Show friendly error message
- Retry button
- Log error details

---

### 5. `empty_states.py` - Empty States

**Purpose:** Show helpful messages when no data exists

**Components:**
```python
class EmptyState(ctk.CTkFrame):
    """Generic empty state with icon, message, and action."""
    
class EmptyDashboard(EmptyState):
    """Empty dashboard state."""
    
class EmptyProjects(EmptyState):
    """Empty projects list."""
    
class EmptySequences(EmptyState):
    """Empty sequences library."""
```

**Usage Example:**
```python
# In projects page
if len(self.projects) == 0:
    EmptyProjects(
        self,
        message="No projects yet. Create your first project!",
        action_text="Create Project",
        action_callback=self.on_create_project
    ).pack(fill="both", expand=True)
else:
    # Show projects table
    pass
```

**Features:**
- Large icon (emoji or custom)
- Helpful message
- Primary action button
- Optional secondary actions

---

### 6. `confirmation_dialog.py` - Confirmation Dialogs

**Purpose:** Confirm destructive actions

**Components:**
```python
class ConfirmDialog(ctk.CTkToplevel):
    """Generic confirmation dialog."""
    
class DestructiveActionDialog(ConfirmDialog):
    """Confirmation for delete/destructive actions (red button)."""
```

**Usage Example:**
```python
# Before deleting project
def on_delete_project(self, project_id):
    dialog = DestructiveActionDialog(
        self,
        title="Delete Project?",
        message=f"Are you sure you want to delete '{project.name}'? This cannot be undone.",
        confirm_text="Delete",
        on_confirm=lambda: self._delete_project(project_id)
    )
    dialog.show()
```

**Features:**
- Modal dialog
- Clear consequences
- Confirm/Cancel buttons
- Red button for destructive actions

---

## 🔄 Integration Pattern

### How to Use in Pages

```python
# Example: Dashboard Page with all UX components

from views.components.skeleton_loader import SkeletonCard
from views.components.loading_indicators import LinearProgress
from views.components.toast_notifications import show_success, show_error
from views.components.error_boundary import ErrorBoundary, ErrorFallback
from views.components.empty_states import EmptyDashboard
from views.components.confirmation_dialog import DestructiveActionDialog

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # State
        self.loading = True
        self.error = None
        self.data = None
        
        # Wrap in error boundary
        self.boundary = ErrorBoundary(
            self,
            content=self._render,
            fallback=ErrorFallback
        )
        self.boundary.pack(fill="both", expand=True)
        
        # Load data
        self.load_data()
    
    def _render(self):
        """Render page content."""
        if self.loading:
            # Show skeletons
            for i in range(4):
                SkeletonCard(self).grid(row=0, column=i)
        
        elif self.data is None or len(self.data) == 0:
            # Show empty state
            EmptyDashboard(
                self,
                message="Welcome! Create your first project to get started.",
                action_text="Create Project",
                action_callback=self.on_create_project
            ).pack(fill="both", expand=True)
        
        else:
            # Show actual data
            for i, stat in enumerate(self.data):
                StatCard(self, **stat).grid(row=0, column=i)
    
    def load_data(self):
        """Load dashboard data asynchronously."""
        def task():
            # Simulate loading
            import time
            time.sleep(2)
            return [
                {"title": "Projects", "value": "5"},
                {"title": "Sequences", "value": "42"},
                # ...
            ]
        
        def on_success(data):
            self.loading = False
            self.data = data
            self._render()
            show_success("Dashboard loaded!")
        
        def on_error(error):
            self.loading = False
            self.error = error
            show_error(f"Failed to load dashboard: {error}")
        
        # Run async
        AsyncExecutor.run_async(task, on_success, on_error)
```

---

## 🎨 Design Guidelines

### Colors
- **Success**: Green (#2fa572)
- **Error**: Red (#d42f2f)
- **Info**: Blue (#1f6aa5)
- **Warning**: Orange (#ffa500)
- **Skeleton**: Gray (light: #e0e0e0, dark: #2b2b2b)

### Animations
- **Shimmer**: 1.5s ease-in-out infinite
- **Slide-in**: 0.3s ease-out
- **Fade**: 0.2s ease-in-out

### Timing
- **Success toast**: 3s auto-dismiss
- **Info toast**: 5s auto-dismiss
- **Error/Warning**: Manual dismiss
- **Skeleton**: Show after 200ms delay (avoid flash)

---

## 💡 Best Practices

1. **Always show loading state** - Never leave users wondering
2. **Use skeletons for known layouts** - Match actual component size
3. **Provide retry options** - Don't dead-end users
4. **Be specific in error messages** - "File not found" not "Error"
5. **Celebrate success** - Positive feedback for completed actions
6. **Prevent accidental deletion** - Always confirm destructive actions
7. **Guide empty states** - Tell users what to do next

---

**All UX components should be reusable, well-documented, and follow CustomTkinter patterns!** 🚀
