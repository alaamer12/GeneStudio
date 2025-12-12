# GeneStudio Pro - Technical Architecture & Specifications

## 🏗️ System Architecture

### Current Architecture (Scaffold)
```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Views (12 Pages + Components)                   │  │
│  │  - Dashboard, Projects, Workspace, Analysis...   │  │
│  │  - Navigation, Header, Footer, Buttons, Cards... │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
                    ⚠️ DISCONNECTED ⚠️
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ViewModels (Minimal)                            │  │
│  │  - MainViewModel only                            │  │
│  │  - No page-specific ViewModels                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      DATA LAYER                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Models + Algorithms                             │  │
│  │  - SequenceData, MatchResult, GraphData          │  │
│  │  - 8 algorithm modules                           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Target Architecture (Full Implementation)
```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Views (12 Pages + Components)                           │  │
│  │  • Event Handlers → ViewModels                           │  │
│  │  • Data Binding ← ViewModels                             │  │
│  │  • UI Updates via Observer Pattern                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Events & Data Binding
┌────────────────────────────▼────────────────────────────────────┐
│                    VIEWMODEL LAYER (NEW)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Page ViewModels (12 classes)                            │  │
│  │  • DashboardViewModel    • ProjectViewModel              │  │
│  │  • WorkspaceViewModel    • AnalysisViewModel             │  │
│  │  • PatternMatchingVM     • GraphAnalysisVM               │  │
│  │  • VisualizationVM       • SequenceManagementVM          │  │
│  │  • ReportsViewModel      • ExportViewModel               │  │
│  │  • SettingsViewModel     • HelpViewModel                 │  │
│  │                                                           │  │
│  │  Responsibilities:                                        │  │
│  │  - State management                                       │  │
│  │  - Event handling                                         │  │
│  │  - Data transformation                                    │  │
│  │  - Validation                                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Business Logic Calls
┌────────────────────────────▼────────────────────────────────────┐
│                     SERVICE LAYER (NEW)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Business Services (7 classes)                           │  │
│  │  • ProjectService        - Project lifecycle management  │  │
│  │  • SequenceService       - Sequence operations           │  │
│  │  • AnalysisService       - Analysis orchestration        │  │
│  │  • ReportService         - Report generation             │  │
│  │  • ExportService         - Data export                   │  │
│  │  • SettingsService       - Settings management           │  │
│  │  • NotificationService   - Notifications                 │  │
│  │                                                           │  │
│  │  Responsibilities:                                        │  │
│  │  - Business logic                                         │  │
│  │  - Workflow orchestration                                 │  │
│  │  - Transaction management                                 │  │
│  │  - Async task coordination                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Data Access
┌────────────────────────────▼────────────────────────────────────┐
│                   REPOSITORY LAYER (NEW)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Repositories (4 classes)                           │  │
│  │  • ProjectRepository     - CRUD for projects             │  │
│  │  • SequenceRepository    - CRUD for sequences            │  │
│  │  • AnalysisRepository    - CRUD for analyses             │  │
│  │  • SettingsRepository    - CRUD for settings             │  │
│  │                                                           │  │
│  │  Responsibilities:                                        │  │
│  │  - Database operations                                    │  │
│  │  - Query optimization                                     │  │
│  │  - Data mapping                                           │  │
│  │  - Cache management                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Persistence
┌────────────────────────────▼────────────────────────────────────┐
│                    PERSISTENCE LAYER (NEW)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Database Manager                                         │  │
│  │  • SQLite for structured data                            │  │
│  │  • JSON for configurations                               │  │
│  │  • File system for sequences                             │  │
│  │                                                           │  │
│  │  Schema:                                                  │  │
│  │  - projects (id, name, type, created, modified)          │  │
│  │  - sequences (id, project_id, header, sequence, ...)     │  │
│  │  - analyses (id, project_id, type, params, results, ...) │  │
│  │  - settings (key, value, type)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      CORE LAYER (EXISTING)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Models                                                   │  │
│  │  • SequenceData, MatchResult, GraphData                  │  │
│  │  • Project, Analysis, Report (NEW)                       │  │
│  │                                                           │  │
│  │  Algorithms (8 modules)                                   │  │
│  │  • fasta_reader      • sequence_ops                      │  │
│  │  • translation       • boyer_moore                       │  │
│  │  • suffix_array      • overlap_graph                     │  │
│  │  • approximate_match                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    UTILITY LAYER (NEW)                           │
│  • AsyncExecutor      - Threading/async operations              │
│  • CacheManager       - Caching strategy                        │
│  • FileManager        - File operations                         │
│  • ExportManager      - Export utilities                        │
│  • SearchEngine       - Search indexing                         │
│  • ThemeManager       - Theme switching                         │
│  • NotificationMgr    - Notification handling                   │
│  • Logger             - Logging                                 │
│  • Validators         - Input validation                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema

### DuckDB Database: `genestudio.db`

**Why DuckDB?**
- Fast analytical queries (10-100x faster than SQLite for aggregations)
- PostgreSQL-compatible SQL syntax
- Excellent Python integration
- Perfect for read-heavy workloads (dashboard stats, reports)
- Handles large datasets efficiently

#### Table: `projects`
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'sequence_analysis', 'genome_assembly', 'comparative'
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',  -- 'active', 'archived', 'completed'
    metadata JSON  -- Additional project-specific data
);
```

#### Table: `sequences`
```sql
CREATE TABLE sequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    header TEXT NOT NULL,
    sequence TEXT NOT NULL,
    sequence_type TEXT DEFAULT 'dna',  -- 'dna', 'rna', 'protein'
    length INTEGER,
    gc_percentage REAL,
    notes TEXT,
    tags TEXT,  -- Comma-separated tags
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_sequences_project ON sequences(project_id);
CREATE INDEX idx_sequences_header ON sequences(header);
```

#### Table: `analyses`
```sql
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    sequence_id INTEGER,
    analysis_type TEXT NOT NULL,  -- 'gc_content', 'pattern_match', etc.
    parameters JSON,  -- Analysis parameters
    results JSON,  -- Analysis results
    status TEXT DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'
    error_message TEXT,
    execution_time REAL,  -- Seconds
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (sequence_id) REFERENCES sequences(id) ON DELETE CASCADE
);

CREATE INDEX idx_analyses_project ON analyses(project_id);
CREATE INDEX idx_analyses_type ON analyses(analysis_type);
```

#### Table: `reports`
```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    name TEXT NOT NULL,
    template TEXT NOT NULL,  -- 'analysis_summary', 'sequence_comparison', etc.
    format TEXT NOT NULL,  -- 'pdf', 'excel', 'html', 'csv', 'json'
    file_path TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_reports_project ON reports(project_id);
```

#### Table: `settings`
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    value_type TEXT DEFAULT 'string',  -- 'string', 'int', 'float', 'bool', 'json'
    category TEXT  -- 'appearance', 'preferences', 'advanced'
);
```

#### Table: `activity_log`
```sql
CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,  -- 'project_created', 'analysis_run', etc.
    entity_type TEXT,  -- 'project', 'sequence', 'analysis'
    entity_id INTEGER,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_timestamp ON activity_log(timestamp DESC);
```

---

## 🗂️ File System Structure

### Project Storage
```
data/
├── projects/
│   ├── project_1/
│   │   ├── config.json          # Project configuration
│   │   ├── sequences/
│   │   │   ├── seq_001.fasta
│   │   │   ├── seq_002.fasta
│   │   │   └── ...
│   │   ├── analyses/
│   │   │   ├── analysis_001.json
│   │   │   ├── analysis_002.json
│   │   │   └── ...
│   │   └── reports/
│   │       ├── report_001.pdf
│   │       ├── report_002.xlsx
│   │       └── ...
│   ├── project_2/
│   │   └── ...
│   └── ...
├── cache/                       # Cached data
│   ├── search_index.json
│   ├── sequence_stats.json
│   └── ...
├── exports/                     # Exported files
│   ├── export_001.csv
│   ├── export_002.xlsx
│   └── ...
└── genestudio.db               # DuckDB database
```

### Configuration Files
```
config/
├── default_settings.json       # Default application settings
├── themes/
│   ├── dark.json
│   ├── light.json
│   └── custom.json
└── report_templates/
    ├── analysis_summary.json
    ├── sequence_comparison.json
    └── project_overview.json
```

---

## 🔄 Data Flow Examples

### Example 1: Loading a FASTA File
```
User clicks "Load FASTA" button
    ↓
WorkspacePage.on_load_fasta_clicked()
    ↓
WorkspaceViewModel.load_fasta(filepath)
    ↓
SequenceService.import_fasta(filepath, project_id)
    ↓
1. Read file using algorithms.read_fasta()
2. Validate sequences
3. Calculate metadata (length, GC%)
    ↓
SequenceRepository.create_sequence(sequence_data)
    ↓
Database: INSERT INTO sequences
    ↓
SequenceRepository returns Sequence object
    ↓
SequenceService returns success
    ↓
WorkspaceViewModel updates state
    ↓
WorkspacePage updates UI (add to list, show in editor)
```

### Example 2: Running an Analysis
```
User selects "GC Content" and clicks "Run Analysis"
    ↓
AnalysisPage.on_run_analysis_clicked()
    ↓
AnalysisViewModel.run_analysis(type, params)
    ↓
AnalysisService.execute_analysis(sequence_id, type, params)
    ↓
1. Create analysis record (status='running')
2. AnalysisRepository.create(analysis)
    ↓
AsyncExecutor.run_async(analysis_function)
    ↓
In background thread:
    1. Get sequence from SequenceRepository
    2. Call algorithms.gc_percentage(sequence)
    3. Format results
    4. Update analysis record (status='completed', results=...)
    ↓
Callback to main thread
    ↓
AnalysisViewModel.on_analysis_complete(results)
    ↓
AnalysisPage updates UI with results
```

### Example 3: Generating a Report
```
User selects template and clicks "Generate Report"
    ↓
ReportsPage.on_generate_report_clicked()
    ↓
ReportsViewModel.generate_report(template, format)
    ↓
ReportService.generate(project_id, template, format)
    ↓
1. Get project data from ProjectRepository
2. Get sequences from SequenceRepository
3. Get analyses from AnalysisRepository
4. Aggregate data
    ↓
ExportService.export_to_format(data, format)
    ↓
If format == 'pdf':
    PDFGenerator.generate(data, template)
        ↓
    reportlab creates PDF
        ↓
    Save to file system
        ↓
    ReportRepository.create(report_record)
        ↓
    Return file path
    ↓
ReportsViewModel updates state
    ↓
ReportsPage shows success message + download link
```

---

## 🧩 Component Specifications

### ViewModel Base Class
```python
class BaseViewModel:
    """Base class for all ViewModels."""
    
    def __init__(self):
        self._observers = []
        self._state = {}
    
    def add_observer(self, callback):
        """Add observer for state changes."""
        self._observers.append(callback)
    
    def notify_observers(self):
        """Notify all observers of state change."""
        for callback in self._observers:
            callback(self._state)
    
    def update_state(self, key, value):
        """Update state and notify observers."""
        self._state[key] = value
        self.notify_observers()
```

### Service Base Class
```python
class BaseService:
    """Base class for all Services."""
    
    def __init__(self, repository):
        self.repository = repository
        self.logger = Logger(__name__)
    
    def execute_with_logging(self, func, *args, **kwargs):
        """Execute function with logging and error handling."""
        try:
            self.logger.info(f"Executing {func.__name__}")
            result = func(*args, **kwargs)
            self.logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"{func.__name__} failed: {str(e)}")
            raise
```

### Repository Base Class
```python
class BaseRepository:
    """Base class for all Repositories."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create(self, entity):
        """Create new entity."""
        raise NotImplementedError
    
    def get_by_id(self, entity_id):
        """Get entity by ID."""
        raise NotImplementedError
    
    def update(self, entity):
        """Update existing entity."""
        raise NotImplementedError
    
    def delete(self, entity_id):
        """Delete entity."""
        raise NotImplementedError
    
    def list(self, filters=None):
        """List entities with optional filters."""
        raise NotImplementedError
```

---

## ⚡ Async Execution Pattern

### AsyncExecutor Utility
```python
import threading
from typing import Callable, Any

class AsyncExecutor:
    """Execute long-running tasks asynchronously."""
    
    @staticmethod
    def run_async(task: Callable, 
                   on_complete: Callable[[Any], None],
                   on_error: Callable[[Exception], None] = None):
        """
        Run task in background thread.
        
        Args:
            task: Function to execute
            on_complete: Callback for successful completion
            on_error: Callback for errors
        """
        def worker():
            try:
                result = task()
                on_complete(result)
            except Exception as e:
                if on_error:
                    on_error(e)
                else:
                    raise
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
```

### Usage Example
```python
# In ViewModel
def run_analysis(self):
    """Run analysis asynchronously."""
    
    def task():
        # Long-running operation
        return self.service.execute_analysis(...)
    
    def on_complete(result):
        # Update UI (must be on main thread)
        self.update_state('result', result)
        self.update_state('status', 'completed')
    
    def on_error(error):
        # Handle error
        self.update_state('error', str(error))
        self.update_state('status', 'failed')
    
    self.update_state('status', 'running')
    AsyncExecutor.run_async(task, on_complete, on_error)
```

---

## 🎨 Theme Management

### Theme Structure
```json
{
  "name": "Dark",
  "colors": {
    "primary": "#1f6aa5",
    "secondary": "#144870",
    "success": "#2fa572",
    "danger": "#d42f2f",
    "warning": "#ffa500",
    "background": "#1a1a1a",
    "surface": "#2b2b2b",
    "text": "#ffffff",
    "text_secondary": "#a0a0a0"
  },
  "fonts": {
    "primary": "Arial",
    "monospace": "Courier New",
    "size_base": 12,
    "size_header": 24,
    "size_subheader": 16
  }
}
```

### ThemeManager
```python
class ThemeManager:
    """Manage application themes."""
    
    def __init__(self):
        self.current_theme = self.load_theme('dark')
    
    def load_theme(self, theme_name):
        """Load theme from JSON file."""
        with open(f'config/themes/{theme_name}.json') as f:
            return json.load(f)
    
    def apply_theme(self, app):
        """Apply theme to application."""
        ctk.set_appearance_mode(self.current_theme['name'].lower())
        # Apply custom colors, fonts, etc.
```

---

## 📈 Performance Optimization Strategies

### 1. Lazy Loading
```python
class PageManager:
    def show_page(self, name: str):
        # Only create page when first accessed
        if name not in self.pages:
            self.pages[name] = self.page_constructors[name](self.parent)
        # Show page
        self.pages[name].pack(fill="both", expand=True)
```

### 2. Caching
```python
class CacheManager:
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
```

### 3. Pagination
```python
class PaginatedDataTable:
    def __init__(self, data, page_size=50):
        self.data = data
        self.page_size = page_size
        self.current_page = 0
    
    def get_page_data(self):
        start = self.current_page * self.page_size
        end = start + self.page_size
        return self.data[start:end]
    
    def next_page(self):
        if (self.current_page + 1) * self.page_size < len(self.data):
            self.current_page += 1
            return True
        return False
```

### 4. Streaming Large Files
```python
def read_large_fasta(filepath, chunk_size=1000):
    """Read FASTA file in chunks."""
    with open(filepath, 'r') as f:
        sequences = []
        for header, seq in read_fasta_stream(f):
            sequences.append((header, seq))
            if len(sequences) >= chunk_size:
                yield sequences
                sequences = []
        if sequences:
            yield sequences
```

---

## 🔒 Error Handling Strategy

### Error Handler Utility
```python
class ErrorHandler:
    """Centralized error handling."""
    
    @staticmethod
    def handle_error(error: Exception, context: str = ""):
        """Handle error with logging and user notification."""
        logger.error(f"{context}: {str(error)}", exc_info=True)
        
        # User-friendly error messages
        error_messages = {
            FileNotFoundError: "File not found. Please check the file path.",
            PermissionError: "Permission denied. Please check file permissions.",
            ValueError: "Invalid input. Please check your data.",
            # Add more...
        }
        
        message = error_messages.get(type(error), f"An error occurred: {str(error)}")
        return message
```

---

## 📝 Validation Strategy

### Validator Utility
```python
class Validators:
    """Input validation utilities."""
    
    @staticmethod
    def validate_sequence(sequence: str) -> tuple[bool, str]:
        """Validate DNA sequence."""
        if not sequence:
            return False, "Sequence cannot be empty"
        
        valid_chars = set('ATCG')
        if not all(c.upper() in valid_chars for c in sequence):
            return False, "Sequence contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_project_name(name: str) -> tuple[bool, str]:
        """Validate project name."""
        if not name or len(name.strip()) == 0:
            return False, "Project name cannot be empty"
        
        if len(name) > 100:
            return False, "Project name too long (max 100 characters)"
        
        return True, ""
```

---

## 🎯 Summary

This technical specification provides:
1. **Complete architecture** - From UI to database
2. **Database schema** - All tables and relationships
3. **File system structure** - How data is organized
4. **Data flow examples** - How operations work end-to-end
5. **Component specifications** - Base classes and patterns
6. **Performance strategies** - Optimization techniques
7. **Error handling** - Centralized error management
8. **Validation** - Input validation patterns

**Next Step:** Begin implementation with Milestone 1 (Foundation & Data Layer)
