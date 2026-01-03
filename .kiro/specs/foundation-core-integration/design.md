# Design Document

## Overview

The Foundation & Core Integration milestone transforms GeneStudio Pro from a UI prototype into a functional bioinformatics application by establishing a robust data architecture and connecting the existing enterprise UI to the comprehensive algorithm library. This design implements a layered architecture following MVVM patterns with DuckDB for fast analytical queries, comprehensive error handling, and professional UX components.

The system architecture consists of five primary layers: Presentation (existing UI), ViewModel (new presentation logic), Service (new business logic), Repository (new data access), and Persistence (new database layer). This design ensures separation of concerns, maintainability, and extensibility while providing immediate user feedback through loading states, error boundaries, and toast notifications.

## Architecture

### System Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Views (12 Pages + Components) - EXISTING                │  │
│  │  • Event Handlers → ViewModels                           │  │
│  │  • Data Binding ← ViewModels                             │  │
│  │  • UI Updates via Observer Pattern                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Events & Data Binding
┌────────────────────────────▼────────────────────────────────────┐
│                    VIEWMODEL LAYER (NEW)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Page ViewModels (4 core classes)                        │  │
│  │  • DashboardViewModel    • ProjectViewModel              │  │
│  │  • WorkspaceViewModel    • AnalysisViewModel             │  │
│  │                                                           │  │
│  │  Responsibilities:                                        │  │
│  │  - State management with observer pattern                │  │
│  │  - Event handling and validation                         │  │
│  │  - Async operation coordination                          │  │
│  │  - UI feedback orchestration                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Business Logic Calls
┌────────────────────────────▼────────────────────────────────────┐
│                     SERVICE LAYER (NEW)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Business Services (4 core classes)                      │  │
│  │  • ProjectService        - Project lifecycle management  │  │
│  │  • SequenceService       - Sequence operations           │  │
│  │  • AnalysisService       - Analysis orchestration        │  │
│  │  • SettingsService       - Settings management           │  │
│  │                                                           │  │
│  │  Responsibilities:                                        │  │
│  │  - Business logic and validation                         │  │
│  │  - Algorithm integration                                  │  │
│  │  - Transaction coordination                               │  │
│  │  - Error handling and logging                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Data Access
┌────────────────────────────▼────────────────────────────────────┐
│                   REPOSITORY LAYER (NEW)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Repositories (4 core classes)                      │  │
│  │  • ProjectRepository     - CRUD for projects             │  │
│  │  • SequenceRepository    - CRUD for sequences            │  │
│  │  • AnalysisRepository    - CRUD for analyses             │  │
│  │  • SettingsRepository    - CRUD for settings             │  │
│  │                                                           │  │
│  │  Responsibilities:                                        │  │
│  │  - Database operations with error handling               │  │
│  │  - Query optimization and indexing                       │  │
│  │  - Data mapping and validation                           │  │
│  │  - Transaction management                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Persistence
┌────────────────────────────▼────────────────────────────────────┐
│                    PERSISTENCE LAYER (NEW)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Database Manager                                         │  │
│  │  • DuckDB for structured data (10-100x faster queries)   │  │
│  │  • JSON for configurations and settings                  │  │
│  │  • File system for large sequence data                   │  │
│  │  • Hybrid approach: metadata in DB, content in files     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Pattern

The system implements a unidirectional data flow with async operations:

1. **User Action** → View captures event
2. **Event Handler** → View delegates to ViewModel
3. **ViewModel** → Validates input, calls Service
4. **Service** → Implements business logic, calls Repository
5. **Repository** → Performs database operations
6. **Response** → Flows back through layers with error handling
7. **UI Update** → ViewModel notifies observers, View updates

### Async Execution Strategy

All long-running operations use the AsyncExecutor pattern to prevent UI blocking:
- File I/O operations (FASTA import/export)
- Database queries for large datasets
- Algorithm execution for complex analyses
- Network operations for update checking

## Components and Interfaces

### Core Components

#### 1. Database Manager
```python
class DatabaseManager:
    """Manages DuckDB connections and schema operations."""
    
    def get_connection(self) -> duckdb.DuckDBPyConnection
    def execute_query(self, query: str, params: tuple) -> List[Dict]
    def execute_transaction(self, operations: List[Callable]) -> bool
    def initialize_schema(self) -> None
    def backup_database(self, filepath: str) -> bool
```

#### 2. Base Repository
```python
class BaseRepository:
    """Abstract base class for all repositories."""
    
    def create(self, entity: Any) -> Any
    def get_by_id(self, entity_id: int) -> Optional[Any]
    def update(self, entity: Any) -> bool
    def delete(self, entity_id: int) -> bool
    def list(self, filters: Dict = None) -> List[Any]
```

#### 3. Base Service
```python
class BaseService:
    """Abstract base class for all services."""
    
    def __init__(self, repository: BaseRepository)
    def execute_with_logging(self, operation: Callable) -> Tuple[bool, Any]
    def validate_input(self, data: Any) -> Tuple[bool, str]
```

#### 4. Base ViewModel
```python
class BaseViewModel:
    """Abstract base class for all ViewModels."""
    
    def add_observer(self, callback: Callable) -> None
    def notify_observers(self) -> None
    def update_state(self, key: str, value: Any) -> None
    def get_state(self, key: str) -> Any
```

#### 5. AsyncExecutor
```python
class AsyncExecutor:
    """Executes long-running operations asynchronously."""
    
    @staticmethod
    def run_async(task: Callable, on_complete: Callable, on_error: Callable) -> Thread
    @staticmethod
    def run_with_progress(task: Callable, progress_callback: Callable) -> Thread
```

#### 6. Theme Manager
```python
class ThemeManager:
    """Centralized theme management with caching and observer pattern."""
    
    def get_font(self, font_type: str = "default") -> tuple
    def get_color(self, color_type: str) -> str
    def update_font_settings(self, font_family: str, font_size: int) -> None
    def add_observer(self, callback: Callable) -> None
    def refresh_theme(self) -> None
    def clear_cache(self) -> None
```

#### 7. Themed Components
```python
class ThemedComponent:
    """Mixin class for components that need theme support."""
    
    def _apply_theme(self) -> None
    def _update_fonts(self) -> None
    def _update_colors(self) -> None
    def _on_theme_changed(self, event: str, data: Any) -> None

class ThemedLabel(ThemedComponent, ctk.CTkLabel):
    """Themed label with automatic font management."""
    
class ThemedButton(ThemedComponent, ctk.CTkButton):
    """Themed button with automatic font management."""
    
class ThemedEntry(ThemedComponent, ctk.CTkEntry):
    """Themed entry with automatic font management."""
```

#### 8. Tooltip System
```python
class ThemedTooltip:
    """Themed tooltip wrapper with consistent styling."""
    
    def __init__(self, widget, message: str, delay: float = 0.5)
    def update_theme(self) -> None
    def show(self) -> None
    def hide(self) -> None

def create_tooltip(widget, message: str, delay: float = 0.5) -> ThemedTooltip
def create_help_tooltip(widget, help_text: str) -> ThemedTooltip
def create_validation_tooltip(widget, validation_msg: str) -> ThemedTooltip
```

### UX Components

#### 1. Skeleton Loader Components
```python
class SkeletonCard(ctk.CTkFrame):
    """Animated card placeholder with shimmer effect."""
    
class SkeletonTable(ctk.CTkFrame):
    """Table row placeholders matching actual table structure."""
    
class SkeletonText(ctk.CTkFrame):
    """Text block placeholders with configurable line count."""
```

#### 2. Loading Indicators
```python
class LinearProgress(ctk.CTkProgressBar):
    """Progress bar for determinate and indeterminate operations."""
    
class LoadingOverlay(ctk.CTkFrame):
    """Full-page loading overlay with cancellation support."""
```

#### 3. Toast Notification System
```python
class ToastManager:
    """Singleton manager for toast notifications."""
    
def show_success(message: str, duration: int = 3000) -> None
def show_error(message: str) -> None
def show_info(message: str, duration: int = 5000) -> None
def show_warning(message: str) -> None
```

#### 4. Error Boundary
```python
class ErrorBoundary:
    """Catches and handles component errors gracefully."""
    
    def __init__(self, parent, content_func: Callable, fallback_func: Callable)
    def handle_error(self, error: Exception) -> None
```

#### 5. Empty States
```python
class EmptyState(ctk.CTkFrame):
    """Generic empty state with icon, message, and action."""
    
class EmptyDashboard(EmptyState):
    """Dashboard-specific empty state with project creation guidance."""
```

## Data Models

### Enhanced Data Models

#### Project Model
```python
@dataclass
class Project:
    id: Optional[int] = None
    name: str = ""
    type: str = "sequence_analysis"  # sequence_analysis, genome_assembly, comparative
    description: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, archived, completed
    sequence_count: int = 0
    analysis_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### Enhanced Sequence Model
```python
@dataclass
class Sequence:
    id: Optional[int] = None
    project_id: int = 0
    header: str = ""
    sequence: str = ""
    sequence_type: str = "dna"  # dna, rna, protein
    length: int = 0
    gc_percentage: float = 0.0
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)
    file_path: Optional[str] = None  # For large sequences stored as files
```

#### Analysis Model
```python
@dataclass
class Analysis:
    id: Optional[int] = None
    project_id: int = 0
    sequence_id: int = 0
    analysis_type: str = ""  # gc_content, pattern_match, translation, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    error_message: Optional[str] = None
    execution_time: float = 0.0
    created_date: datetime = field(default_factory=datetime.now)
```

#### Settings Model
```python
@dataclass
class Setting:
    key: str = ""
    value: str = ""
    value_type: str = "string"  # string, int, float, bool, json
    category: str = "general"  # appearance, preferences, advanced
```

### Database Schema

#### DuckDB Tables
```sql
-- Projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'sequence_analysis',
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    sequence_count INTEGER DEFAULT 0,
    analysis_count INTEGER DEFAULT 0,
    metadata JSON
);

-- Sequences table
CREATE TABLE sequences (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    header TEXT NOT NULL,
    sequence TEXT,
    sequence_type TEXT DEFAULT 'dna',
    length INTEGER,
    gc_percentage REAL,
    notes TEXT,
    tags TEXT,
    file_path TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analyses table
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    sequence_id INTEGER REFERENCES sequences(id) ON DELETE CASCADE,
    analysis_type TEXT NOT NULL,
    parameters JSON,
    results JSON,
    status TEXT DEFAULT 'pending',
    error_message TEXT,
    execution_time REAL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Settings table
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    value_type TEXT DEFAULT 'string',
    category TEXT DEFAULT 'general'
);

-- Activity log for dashboard
CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### File System Organization
```
data/
├── projects/
│   ├── project_1/
│   │   ├── sequences/           # Large sequence files
│   │   ├── analyses/            # Analysis result files
│   │   └── config.json          # Project configuration
│   └── project_2/
├── cache/                       # Cached computations
├── exports/                     # Exported files
└── genestudio.db               # DuckDB database
```
## Cor
rectness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, several properties can be consolidated to eliminate redundancy:

- Properties for project CRUD operations (create, load, delete, update) can be combined into comprehensive project lifecycle properties
- Properties for error handling across different operation types can be consolidated into general error handling properties
- Properties for UI feedback (loading states, toasts, empty states) can be combined into comprehensive UI feedback properties
- Properties for data persistence across different entity types can be consolidated into general persistence properties

### Core Properties

**Property 1: Project lifecycle management**
*For any* valid project data, creating a project should result in the project being stored in the database and displayed in the projects list, and selecting that project should load all associated sequences and analyses correctly
**Validates: Requirements 1.2, 1.3**

**Property 2: Project deletion confirmation**
*For any* existing project, attempting deletion should display a confirmation dialog, and the project should only be deleted after explicit confirmation
**Validates: Requirements 1.4**

**Property 3: Project data persistence**
*For any* project modifications, changes should be persisted to the database and survive application restarts
**Validates: Requirements 1.5, 5.1**

**Property 4: FASTA import processing**
*For any* valid FASTA file, importing should correctly parse all sequences, calculate accurate metadata (length, GC percentage), and store sequences in the current project
**Validates: Requirements 2.2, 2.3**

**Property 5: Invalid data error handling**
*For any* invalid input data (FASTA files, analysis parameters, etc.), the system should display specific error messages and provide recovery options without crashing
**Validates: Requirements 2.4, 3.4, 6.1, 6.3**

**Property 6: Asynchronous operation management**
*For any* long-running operation (file import, analysis execution), the operation should execute asynchronously with progress indicators and not block the UI
**Validates: Requirements 2.5, 3.2, 7.4**

**Property 7: Analysis execution and storage**
*For any* valid analysis request, the system should execute the corresponding algorithm, store results in the database, and display formatted results
**Validates: Requirements 3.3**

**Property 8: Concurrent operation handling**
*For any* set of concurrent operations, the system should manage all operations independently with individual status tracking
**Validates: Requirements 3.5**

**Property 9: UI feedback consistency**
*For any* user action, the system should provide appropriate feedback through loading states for data operations, success toasts for completed actions, and error toasts for failures
**Validates: Requirements 4.1, 4.2, 4.3**

**Property 10: Error boundary protection**
*For any* unexpected error condition, the system should display error boundaries with retry options rather than crashing the application
**Validates: Requirements 4.4**

**Property 11: Empty state guidance**
*For any* empty data collection, the system should display helpful empty state messages with guidance on next actions
**Validates: Requirements 4.5**

**Property 12: Session state persistence**
*For any* application session, closing and reopening the application should restore the previous session state including open projects and window configuration
**Validates: Requirements 5.2**

**Property 13: Settings persistence**
*For any* application setting modification, changes should persist across application restarts and be applied in subsequent sessions
**Validates: Requirements 5.3**

**Property 14: Database error recovery**
*For any* database operation failure, the system should log detailed error information, display user-friendly messages, and attempt recovery procedures where possible
**Validates: Requirements 5.4, 6.2**

**Property 15: Resource management**
*For any* large dataset or memory-intensive operation, the system should implement appropriate resource management strategies and warn users about limitations
**Validates: Requirements 6.5**

**Property 16: Network failure handling**
*For any* network operation failure during non-critical features, the system should fail silently and log warnings for debugging
**Validates: Requirements 6.4**

**Property 17: Dashboard statistics accuracy**
*For any* data state, the dashboard should display accurate current statistics (project count, sequence count, analysis count) and update in real-time when data changes
**Validates: Requirements 8.1, 8.2**

**Property 18: Activity feed tracking**
*For any* user action that modifies data, the action should appear in the activity feed with accurate timestamps and relevant details
**Validates: Requirements 8.3**

**Property 19: Dashboard loading states**
*For any* dashboard data loading operation, skeleton loading screens should be displayed before actual statistics are shown
**Validates: Requirements 8.4**

**Property 20: Dynamic theme application**
*For any* font setting change, all UI components should immediately update to use the new font configuration without requiring application restart
**Validates: Requirements 9.1, 9.2**

**Property 21: Automatic theme inheritance**
*For any* newly created UI component, the component should automatically inherit the current theme configuration without requiring manual font specification
**Validates: Requirements 9.3**

**Property 22: Theme fallback handling**
*For any* invalid or missing font settings, the system should fall back to default font configuration and continue functioning normally
**Validates: Requirements 9.4**

**Property 23: Font type differentiation**
*For any* UI element type (default, heading, code, small), the appropriate font configuration should be applied based on the element's semantic purpose
**Validates: Requirements 9.5**

**Property 24: Contextual tooltip display**
*For any* UI control with tooltip support, hovering for the specified delay should display relevant contextual information
**Validates: Requirements 10.1, 10.2, 10.3, 10.4**

**Property 25: Tooltip theme consistency**
*For any* tooltip displayed in the application, the styling should match the current application theme and remain readable in all appearance modes
**Validates: Requirements 10.5**

## Error Handling

### Error Handling Strategy

The system implements a layered error handling approach with specific error types and recovery mechanisms:

#### 1. Input Validation Errors
- **File Format Errors**: Invalid FASTA files, corrupted data
- **Parameter Errors**: Invalid analysis parameters, missing required fields
- **Data Type Errors**: Incorrect sequence types, malformed input
- **Recovery**: Display specific error messages with correction guidance

#### 2. System Errors
- **Database Errors**: Connection failures, query errors, constraint violations
- **File System Errors**: Permission denied, disk full, file not found
- **Memory Errors**: Out of memory, resource exhaustion
- **Recovery**: Log detailed errors, display user-friendly messages, attempt automatic recovery

#### 3. Algorithm Errors
- **Execution Errors**: Algorithm failures, invalid input for algorithms
- **Timeout Errors**: Long-running operations that exceed time limits
- **Resource Errors**: Insufficient resources for computation
- **Recovery**: Validate inputs before execution, provide parameter correction guidance

#### 4. Network Errors
- **Connection Errors**: Network unavailable, server unreachable
- **Timeout Errors**: Request timeouts, slow responses
- **Authentication Errors**: Invalid credentials, expired tokens
- **Recovery**: Fail silently for non-critical features, retry with exponential backoff

### Error Boundary Implementation

Error boundaries wrap UI components to catch and handle unexpected errors:

```python
class ErrorBoundary:
    def __init__(self, parent, content_func, fallback_func):
        self.parent = parent
        self.content_func = content_func
        self.fallback_func = fallback_func
        
    def render(self):
        try:
            return self.content_func()
        except Exception as e:
            self.log_error(e)
            return self.fallback_func(e)
```

### Error Logging

Comprehensive error logging with structured information:
- **Error Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Context Information**: User action, component, timestamp
- **Stack Traces**: Full stack traces for debugging
- **User Impact**: Description of user-visible effects

## Testing Strategy

### Dual Testing Approach

The system requires both unit testing and property-based testing to ensure comprehensive coverage:

#### Unit Testing
Unit tests verify specific examples, edge cases, and integration points:
- **Component Integration**: Test ViewModel-Service-Repository interactions
- **Error Conditions**: Test specific error scenarios and recovery
- **Edge Cases**: Test boundary conditions and special cases
- **UI Components**: Test component rendering and event handling

#### Property-Based Testing
Property-based tests verify universal properties across all inputs using **Hypothesis** for Python:
- **Minimum 100 iterations** per property test for thorough coverage
- **Random data generation** for comprehensive input space exploration
- **Property test tagging** with explicit references to design properties

Each property-based test must be tagged with this exact format:
```python
# **Feature: foundation-core-integration, Property 1: Project lifecycle management**
def test_project_lifecycle_property():
    # Test implementation
```

#### Testing Requirements
- Each correctness property must be implemented by a single property-based test
- Property-based tests must be placed as close to implementation as possible
- Tests must catch errors early in the development process
- Both unit and property tests are complementary and required

### Test Coverage Strategy

#### Core Functionality Testing
- **Project Management**: Create, read, update, delete operations
- **Sequence Import**: FASTA parsing, validation, metadata calculation
- **Analysis Execution**: Algorithm integration, async execution, result storage
- **Data Persistence**: Database operations, session state, settings

#### UX Component Testing
- **Loading States**: Skeleton screens, progress indicators
- **Error Handling**: Error boundaries, toast notifications
- **Empty States**: Guidance messages, action buttons
- **User Feedback**: Success notifications, error messages

#### Integration Testing
- **End-to-End Workflows**: Complete user scenarios from UI to database
- **Cross-Component Communication**: ViewModel-Service-Repository interactions
- **Async Operation Coordination**: Multiple concurrent operations
- **Error Recovery**: System behavior under various failure conditions

### Performance Testing
- **Large File Handling**: FASTA files with thousands of sequences
- **Concurrent Operations**: Multiple analyses running simultaneously
- **Memory Usage**: Resource consumption under load
- **Database Performance**: Query optimization and indexing effectiveness