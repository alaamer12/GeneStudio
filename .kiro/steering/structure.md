# GeneStudio Pro - Project Structure & Organization

ALWAYS RUN FROM `.venv`. ie. `.venv\scripts\python <command>`
IF YOU ARE GOING TO RUN THE GUI [ie. main.py] just compile it or RUN IT with time off to terminate if it passed without errors

## Directory Structure

### Current Implementation
```
GeneStudio/
├── algorithms/              # ✅ Core bioinformatics algorithms
│   ├── fasta_reader.py     # FASTA file parsing
│   ├── sequence_ops.py     # Basic sequence operations (GC%, reverse, complement)
│   ├── translation.py      # DNA to amino acid translation
│   ├── boyer_moore.py      # Boyer-Moore pattern matching variants
│   ├── suffix_array.py     # Suffix array construction and search
│   ├── approximate_match.py # Hamming distance and edit distance
│   ├── overlap_graph.py    # Overlap graph construction
│   └── __init__.py         # Algorithm exports
├── models/                 # ✅ Data models (basic)
│   ├── sequence_model.py   # SequenceData, MatchResult, GraphData
│   └── __init__.py
├── views/                  # ✅ Complete enterprise GUI
│   ├── main_window.py      # Main application window
│   ├── page_manager.py     # Page navigation system
│   ├── components/         # Reusable UI components
│   │   ├── buttons.py      # Custom button components
│   │   ├── cards.py        # Card layouts
│   │   ├── tables.py       # Data tables
│   │   ├── modals.py       # Modal dialogs
│   │   ├── plots.py        # Plot components
│   │   ├── charts.py       # Chart components
│   │   ├── navigation.py   # Navigation components
│   │   ├── header.py       # Header component
│   │   ├── footer.py       # Footer component
│   │   └── visualization_3d.py # 3D visualization
│   └── pages/              # 12 application pages
│       ├── dashboard_page.py        # Main dashboard
│       ├── projects_page.py         # Project management
│       ├── workspace_page.py        # File browser & sequence editor
│       ├── analysis_page.py         # Analysis tools
│       ├── pattern_matching_page.py # Pattern matching algorithms
│       ├── graph_analysis_page.py   # Overlap graph analysis
│       ├── visualization_page.py    # Data visualization
│       ├── sequence_management_page.py # Sequence library
│       ├── reports_page.py          # Report generation
│       ├── export_page.py           # Data export
│       ├── settings_page.py         # Application settings
│       └── help_page.py             # Help and documentation
├── viewmodels/             # ⚠️ Minimal implementation - needs expansion
│   ├── main_viewmodel.py   # Basic business logic
│   └── __init__.py
├── data/                   # ✅ Sample data
│   └── sample.fasta        # Sample FASTA file
├── main.py                 # ✅ Application entry point
├── requirements.txt        # ✅ Dependencies
└── README.md              # ✅ Documentation
```

### Target Structure (Full Implementation)
```
GeneStudio/
├── algorithms/             # ✅ Existing - Core algorithms
├── models/                 # ⚠️ Enhance existing models
├── views/                  # ✅ Existing - Complete UI
├── viewmodels/             # ❌ Expand - Add 12 page ViewModels
├── services/               # ❌ New - Business logic layer
│   ├── project_service.py
│   ├── sequence_service.py
│   ├── analysis_service.py
│   ├── report_service.py
│   ├── export_service.py
│   ├── settings_service.py
│   └── notification_service.py
├── repositories/           # ❌ New - Data access layer
│   ├── project_repository.py
│   ├── sequence_repository.py
│   ├── analysis_repository.py
│   └── settings_repository.py
├── database/               # ❌ New - Database management
│   ├── schema.sql
│   ├── db_manager.py
│   └── migrations/
├── utils/                  # ❌ New - Utility functions
│   ├── async_executor.py
│   ├── cache_manager.py
│   ├── file_manager.py
│   ├── export_manager.py
│   ├── search_engine.py
│   ├── theme_manager.py
│   ├── notification_manager.py
│   └── validators.py
├── config/                 # ❌ New - Configuration
│   ├── default_settings.json
│   └── themes/
└── tests/                  # ❌ New - Unit tests
```

## Architecture Layers

### 1. Presentation Layer (views/)
- **Complete Implementation** - All 12 pages with professional UI
- **Components** - Reusable UI widgets and layouts
- **Navigation** - Page management and routing system
- **Responsibility** - User interface and user interaction

### 2. Presentation Logic (viewmodels/)
- **Current Status** - Only main_viewmodel.py with basic functionality
- **Needs** - 12 page-specific ViewModels for proper MVVM pattern
- **Responsibility** - UI state management, event handling, data binding

### 3. Business Logic (services/)
- **Current Status** - Not implemented
- **Needs** - Service layer for business operations
- **Responsibility** - Business rules, workflow orchestration, validation

### 4. Data Access (repositories/)
- **Current Status** - Not implemented  
- **Needs** - Repository pattern for data persistence
- **Responsibility** - CRUD operations, data mapping, query optimization

### 5. Core Domain (models/ + algorithms/)
- **Current Status** - Basic models, complete algorithms
- **Responsibility** - Domain entities, business logic, algorithm implementations

## File Naming Conventions

### Python Files
- **snake_case** for all Python files and modules
- **Descriptive names** that indicate purpose
- **Consistent suffixes** for similar file types:
  - `*_page.py` for UI pages
  - `*_viewmodel.py` for ViewModels  
  - `*_service.py` for business services
  - `*_repository.py` for data repositories
  - `*_manager.py` for utility managers

### Class Naming
- **PascalCase** for class names
- **Descriptive names** that indicate responsibility
- **Consistent suffixes**:
  - `*Page` for UI pages
  - `*ViewModel` for ViewModels
  - `*Service` for services
  - `*Repository` for repositories
  - `*Manager` for managers

## Import Organization

### Standard Import Order
```python
# 1. Standard library imports
import os
import threading
from typing import Optional, List, Tuple

# 2. Third-party imports
import customtkinter as ctk
import matplotlib.pyplot as plt

# 3. Local application imports
from models.sequence_model import SequenceData
from algorithms import fasta_reader
from utils.validators import validate_sequence
```

### Relative vs Absolute Imports
- **Prefer absolute imports** from project root
- **Use relative imports** only within same package
- **Avoid deep relative imports** (../../)

## Data Flow Patterns

### MVVM Data Flow
```
User Action (View) 
    ↓
Event Handler (View)
    ↓  
ViewModel Method
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Model/Database
    ↓
Repository Returns Data
    ↓
Service Processes Data
    ↓
ViewModel Updates State
    ↓
View Updates UI
```

### Error Handling Flow
```python
# Consistent error handling pattern across layers
def service_method(self) -> tuple[bool, str]:
    try:
        result = self.repository.get_data()
        processed = self.process_data(result)
        return True, processed
    except Exception as e:
        self.logger.error(f"Service error: {str(e)}")
        return False, f"Operation failed: {str(e)}"
```

## Configuration Management

### Settings Hierarchy
1. **Default settings** - `config/default_settings.json`
2. **User settings** - Stored in database
3. **Session settings** - Runtime overrides

### Theme Management
- **Theme files** - `config/themes/*.json`
- **Dynamic switching** - Runtime theme changes
- **Custom themes** - User-defined color schemes

## Testing Structure (Planned)

```
tests/
├── unit/                   # Unit tests
│   ├── test_algorithms/
│   ├── test_models/
│   ├── test_services/
│   └── test_repositories/
├── integration/            # Integration tests
│   ├── test_workflows/
│   └── test_data_flow/
└── fixtures/               # Test data
    ├── sample_sequences/
    └── test_configs/
```

## Development Guidelines

### Code Organization
- **Single Responsibility** - Each class/module has one clear purpose
- **Dependency Injection** - Pass dependencies rather than creating them
- **Interface Segregation** - Small, focused interfaces
- **Separation of Concerns** - Clear layer boundaries

### Performance Considerations
- **Lazy Loading** - Load data only when needed
- **Async Operations** - Use threading for long-running tasks
- **Caching** - Cache frequently accessed data
- **Pagination** - Handle large datasets efficiently

### Error Handling
- **Graceful Degradation** - Application continues working when possible
- **User-Friendly Messages** - Clear, actionable error messages
- **Logging** - Comprehensive error logging for debugging
- **Recovery** - Provide retry mechanisms where appropriate

## UX Component Integration

### Required UX Components (Milestone 1)
```python
# New components to implement for professional UX
views/components/
├── skeleton_loader.py      # SkeletonCard, SkeletonTable, SkeletonText
├── loading_indicators.py   # LinearProgress, CircularProgress, LoadingOverlay
├── toast_notifications.py  # ToastManager, show_success/error/info/warning
├── error_boundary.py       # ErrorBoundary, ErrorFallback, RetryButton
├── empty_states.py         # EmptyState, EmptyDashboard, EmptyProjects
└── confirmation_dialog.py  # ConfirmDialog, DestructiveActionDialog
```

### Core Utilities Implementation
```python
# Essential utilities for enterprise functionality
utils/
├── file_importer.py        # ABC pattern: FileImporter, FASTAImporter
├── text_history.py         # TextHistory with undo/redo for editors
├── logger.py               # Simple logging with file rotation
services/
├── state_manager.py        # Save/restore app state (window, tabs, files)
└── update_service.py       # GitHub release checker with notifications
```

### Database Architecture
- **DuckDB** - Fast analytical queries for dashboard stats and reports
- **JSON files** - Configuration, settings, and themes
- **File system** - Large sequence data and analysis results
- **Hybrid approach** - Metadata in database, content as files

### Implementation Patterns

#### Loading States
```python
# Always show loading state
if self.loading:
    SkeletonCard(self.stats_frame).grid(row=0, column=0)
else:
    StatCard(self.stats_frame, **data).grid(row=0, column=0)
```

#### Error Boundaries
```python
# Wrap pages in error boundaries
boundary = ErrorBoundary(
    self,
    content=self._render_content,
    fallback=ErrorFallback
)
```

#### Toast Notifications
```python
# Immediate user feedback
from views.components.toast_notifications import show_success, show_error
show_success("Project saved successfully!")
show_error("Failed to load file. Please try again.")
```

#### State Persistence
```python
# Save application state on close
state = {
    "window_geometry": self.geometry(),
    "last_page": self.page_manager.current_page,
    "recent_files": self.recent_files,
    "theme": ctk.get_appearance_mode()
}
self.state_manager.save_state(state)
```