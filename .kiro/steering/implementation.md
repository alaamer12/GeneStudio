# GeneStudio Pro - Implementation Guidelines

## Current Status & Implementation Priority

### ✅ Completed (Enterprise UI Scaffold)
- **Complete 12-page enterprise GUI** with professional navigation
- **Core bioinformatics algorithms** (8 modules) implemented from scratch
- **Reusable component library** (buttons, cards, tables, modals, plots)
- **Page management system** with routing and navigation history
- **Professional design system** with dark/light themes

### ⚠️ Critical Gap: UI-Backend Disconnection
- **All UI is placeholder-based** - buttons don't perform real actions
- **No data persistence** - no database, file management, or state saving
- **No integration layer** - UI and algorithms are completely separate
- **No error handling** - no validation, logging, or user feedback systems

## Implementation Milestones

### Milestone 1: Foundation & Core Integration (Priority 1)
**Goal:** Connect UI to algorithms with proper data flow and persistence

#### Core Architecture Implementation
```python
# Service Layer - Business logic
services/
├── project_service.py      # Project lifecycle management
├── sequence_service.py     # Sequence operations and validation
├── analysis_service.py     # Analysis orchestration and execution
├── settings_service.py     # Settings persistence and management
└── state_manager.py        # Application state persistence

# Repository Layer - Data access
repositories/
├── project_repository.py   # Project CRUD operations
├── sequence_repository.py  # Sequence storage and retrieval
├── analysis_repository.py  # Analysis results storage
└── settings_repository.py  # Settings storage

# Database Layer
database/
├── db_manager.py          # DuckDB connection management
├── schema.sql             # Database schema definition
└── migrations/            # Schema migration scripts
```

#### ViewModel Expansion (12 files needed)
```python
# Page-specific ViewModels for proper MVVM
viewmodels/
├── dashboard_viewmodel.py        # Dashboard stats and activity
├── projects_viewmodel.py         # Project management logic
├── workspace_viewmodel.py        # File browser and editor logic
├── analysis_viewmodel.py         # Analysis execution logic
├── pattern_matching_viewmodel.py # Pattern search logic
├── graph_analysis_viewmodel.py   # Graph construction logic
├── visualization_viewmodel.py    # Data visualization logic
├── sequence_management_viewmodel.py # Sequence library logic
├── reports_viewmodel.py          # Report generation logic
├── export_viewmodel.py           # Data export logic
├── settings_viewmodel.py         # Settings management logic
└── help_viewmodel.py             # Help system logic
```

#### UX Components (Professional User Experience)
```python
# Essential UX components for enterprise feel
views/components/
├── skeleton_loader.py      # Loading placeholders with shimmer
├── loading_indicators.py   # Progress bars and spinners
├── toast_notifications.py  # Success/error/info messages
├── error_boundary.py       # Error handling with retry
├── empty_states.py         # Helpful empty state messages
└── confirmation_dialog.py  # Confirmation for destructive actions
```

#### Core Utilities (Essential Functionality)
```python
# Utilities for professional application behavior
utils/
├── file_importer.py        # ABC pattern for extensible file imports
├── text_history.py         # Undo/redo for text editors
├── async_executor.py       # Threading for long operations
├── validators.py           # Input validation utilities
└── logger.py               # Simple logging with rotation
```

### Milestone 2: Advanced Features & Integration (Priority 2)
**Goal:** Implement search, visualization, and advanced analysis features

#### Search System Implementation
```python
# Global search across all data
utils/search_engine.py      # Full-text search with indexing
# Integration in header search bar
# Filter and sort capabilities
# Search history and suggestions
```

#### Visualization Integration
```python
# Connect real data to existing plot components
# Interactive controls (zoom, pan, rotate for 3D)
# Export visualizations as images
# Multiple data source binding
```

#### Pattern Matching Enhancement
```python
# Real-time search with highlighting
# Match statistics and performance metrics
# Export match results in multiple formats
# Visual representation of matches
```

### Milestone 3: Reports & Export System (Priority 3)
**Goal:** Professional reporting and data export capabilities

#### Report Generation System
```python
services/report_service.py   # Report generation logic
utils/pdf_generator.py       # PDF creation with reportlab
utils/excel_generator.py     # Excel export with openpyxl
templates/report_templates/  # Report template definitions
```

#### Export System Enhancement
```python
# Multiple format support (PDF, Excel, CSV, HTML, JSON)
# Batch export capabilities
# Format-specific options and validation
# Export history and management
```

### Milestone 4: Performance & Polish (Priority 4)
**Goal:** Optimize performance and finalize user experience

#### Performance Optimizations
```python
utils/cache_manager.py       # Caching for expensive operations
utils/file_streamer.py       # Streaming for large files
# Lazy loading implementation
# Memory management improvements
# Async operation optimization
```

## Database Architecture (DuckDB + Hybrid Approach)

### Why DuckDB?
- **10-100x faster than SQLite** for analytical queries (dashboard stats, reports)
- **PostgreSQL-compatible SQL** syntax for complex queries
- **Excellent Python integration** with pandas support
- **Perfect for read-heavy workloads** (dashboard, search, reporting)

### Hybrid Storage Strategy
```sql
-- DuckDB for structured metadata (fast queries)
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sequence_count INTEGER DEFAULT 0,
    analysis_count INTEGER DEFAULT 0
);

CREATE TABLE sequences (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    header TEXT NOT NULL,
    length INTEGER,
    gc_percentage REAL,
    file_path TEXT,  -- Points to actual sequence file
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analyses (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    sequence_id INTEGER REFERENCES sequences(id),
    analysis_type TEXT NOT NULL,
    parameters JSON,
    results JSON,
    execution_time REAL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### File System Organization
```
data/
├── projects/
│   ├── project_1/
│   │   ├── sequences/           # Large sequence files
│   │   │   ├── seq_001.fasta
│   │   │   └── seq_002.fasta
│   │   ├── analyses/            # Analysis result files
│   │   │   ├── analysis_001.json
│   │   │   └── analysis_002.json
│   │   └── reports/             # Generated reports
│   │       ├── report_001.pdf
│   │       └── report_002.xlsx
│   └── project_2/
├── cache/                       # Cached computations
└── genestudio.db               # DuckDB database
```

## MVVM Data Flow Implementation

### Standard Data Flow Pattern
```python
# 1. User Action (View)
def on_load_fasta_clicked(self):
    filepath = self.show_file_dialog()
    if filepath:
        self.viewmodel.load_fasta_file(filepath)

# 2. ViewModel (Presentation Logic)
class WorkspaceViewModel:
    def load_fasta_file(self, filepath: str):
        # Show loading state
        self.update_state("loading", True)
        
        # Async operation
        def task():
            return self.sequence_service.import_fasta(filepath)
        
        def on_success(sequences):
            self.update_state("loading", False)
            self.update_state("sequences", sequences)
            show_success(f"Loaded {len(sequences)} sequences")
        
        def on_error(error):
            self.update_state("loading", False)
            show_error(f"Failed to load file: {error}")
        
        AsyncExecutor.run_async(task, on_success, on_error)

# 3. Service (Business Logic)
class SequenceService:
    def import_fasta(self, filepath: str) -> List[SequenceData]:
        # Validate file
        if not self.validator.validate_fasta_file(filepath):
            raise ValueError("Invalid FASTA file format")
        
        # Import sequences
        sequences = self.file_importer.import_file(filepath)
        
        # Save to repository
        saved_sequences = []
        for header, seq in sequences:
            sequence_data = SequenceData(header=header, sequence=seq)
            saved = self.repository.create(sequence_data)
            saved_sequences.append(saved)
        
        return saved_sequences

# 4. Repository (Data Access)
class SequenceRepository:
    def create(self, sequence_data: SequenceData) -> SequenceData:
        # Save metadata to database
        sequence_id = self.db.execute(
            "INSERT INTO sequences (header, length, gc_percentage) VALUES (?, ?, ?)",
            (sequence_data.header, len(sequence_data.sequence), 
             calculate_gc_percentage(sequence_data.sequence))
        )
        
        # Save sequence to file
        file_path = f"data/sequences/seq_{sequence_id}.fasta"
        with open(file_path, 'w') as f:
            f.write(f">{sequence_data.header}\n{sequence_data.sequence}\n")
        
        # Update file path in database
        self.db.execute(
            "UPDATE sequences SET file_path = ? WHERE id = ?",
            (file_path, sequence_id)
        )
        
        sequence_data.id = sequence_id
        return sequence_data
```

## Error Handling Strategy

### Layered Error Handling
```python
# 1. Repository Layer - Data errors
class SequenceRepository:
    def get_by_id(self, sequence_id: int) -> SequenceData:
        try:
            result = self.db.execute("SELECT * FROM sequences WHERE id = ?", (sequence_id,))
            if not result:
                raise SequenceNotFoundError(f"Sequence {sequence_id} not found")
            return self._map_to_sequence_data(result[0])
        except DatabaseError as e:
            log_error(f"Database error in get_by_id: {e}")
            raise RepositoryError("Failed to retrieve sequence from database")

# 2. Service Layer - Business logic errors
class SequenceService:
    def get_sequence(self, sequence_id: int) -> tuple[bool, SequenceData | str]:
        try:
            sequence = self.repository.get_by_id(sequence_id)
            return True, sequence
        except SequenceNotFoundError as e:
            return False, "Sequence not found. It may have been deleted."
        except RepositoryError as e:
            return False, "Database error. Please try again later."
        except Exception as e:
            log_error(f"Unexpected error in get_sequence: {e}", exc_info=True)
            return False, "An unexpected error occurred. Please contact support."

# 3. ViewModel Layer - UI error handling
class SequenceManagementViewModel:
    def load_sequence(self, sequence_id: int):
        success, result = self.sequence_service.get_sequence(sequence_id)
        if success:
            self.update_state("current_sequence", result)
        else:
            show_error(result)  # User-friendly error message

# 4. View Layer - Error boundaries
class SequenceManagementPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Wrap in error boundary
        self.boundary = ErrorBoundary(
            self,
            content=self._render_content,
            fallback=ErrorFallback,
            on_retry=self._retry_load
        )
```

## Performance Optimization Patterns

### Async Operations
```python
# Use AsyncExecutor for all long-running operations
class AsyncExecutor:
    @staticmethod
    def run_async(task: Callable, on_complete: Callable, on_error: Callable = None):
        def worker():
            try:
                result = task()
                # Schedule callback on main thread
                threading.Timer(0, lambda: on_complete(result)).start()
            except Exception as e:
                if on_error:
                    threading.Timer(0, lambda: on_error(e)).start()
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
```

### Caching Strategy
```python
# Cache expensive computations
from functools import lru_cache

class AnalysisService:
    @lru_cache(maxsize=128)
    def calculate_gc_content(self, sequence: str) -> float:
        # Expensive computation cached
        return algorithms.gc_percentage(sequence)
    
    def clear_cache(self):
        self.calculate_gc_content.cache_clear()
```

### Lazy Loading
```python
# Load pages only when accessed
class PageManager:
    def __init__(self):
        self.pages = {}
        self.page_constructors = {
            "dashboard": DashboardPage,
            "projects": ProjectsPage,
            # ... other pages
        }
    
    def show_page(self, name: str):
        if name not in self.pages:
            # Create page on first access
            self.pages[name] = self.page_constructors[name](self.parent)
        
        # Hide current page
        if self.current_page:
            self.current_page.pack_forget()
        
        # Show requested page
        self.pages[name].pack(fill="both", expand=True)
        self.current_page = self.pages[name]
```