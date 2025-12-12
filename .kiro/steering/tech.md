# GeneStudio Pro - Technical Stack & Build System

## Tech Stack

### Core Framework
- **Python 3.10+** - Primary language
- **CustomTkinter 5.2.0+** - Modern GUI framework with dark/light themes
- **Matplotlib 3.8.0+** - Data visualization and plotting

### Architecture Pattern
- **MVVM (Model-View-ViewModel)** - Clean separation of concerns
- **Repository Pattern** - Data access abstraction
- **Service Layer** - Business logic encapsulation

### Current Dependencies
```
customtkinter>=5.2.0
matplotlib>=3.8.0
```

### Planned Dependencies (Implementation Phase)
```
duckdb>=0.9.0             # Fast analytical database
reportlab>=4.0.0          # PDF generation
openpyxl>=3.1.0           # Excel export
pillow>=10.0.0            # Image processing
numpy>=1.24.0             # Numerical operations
pandas>=2.0.0             # Data manipulation
requests>=2.31.0          # HTTP requests
```

## Project Structure

### Current Architecture
```
algorithms/          # Core bioinformatics algorithms (implemented)
models/             # Data models (basic implementation)
views/              # UI layer - complete enterprise GUI
  ├── components/   # Reusable UI components
  ├── pages/        # 12 application pages
  └── main_window.py
viewmodels/         # Presentation logic (minimal - needs expansion)
data/               # Sample FASTA files
```

### Target Architecture (Full Implementation)
```
algorithms/          # Core algorithms (existing)
models/             # Enhanced data models
views/              # UI layer (existing)
viewmodels/         # Page-specific ViewModels (expand)
services/           # Business logic layer (new)
repositories/       # Data access layer (new)
database/           # Database schema and management (new)
utils/              # Utility functions (new)
config/             # Configuration files (new)
```

## Build & Development Commands

### Setup
```bash
# Clone and setup
git clone <repository-url>
cd GeneStudio
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Run Application
```bash
python main.py
```

### Development Workflow
```bash
# Install development dependencies (when added)
pip install -r requirements-dev.txt

# Run tests (when implemented)
python -m pytest tests/

# Code formatting (when configured)
black .
isort .

# Type checking (when configured)
mypy .
```

## Algorithm Implementation Philosophy

- **From Scratch Implementation** - All algorithms implemented without external bioinformatics libraries
- **Educational Focus** - Code is readable and well-documented for learning
- **Performance Conscious** - Efficient implementations suitable for real-world use
- **Modular Design** - Each algorithm in separate module for easy testing and maintenance

## Current Implementation Status

### ✅ Completed
- Core algorithm implementations (8 modules)
- Complete enterprise GUI (12 pages, components)
- Basic data models
- FASTA file reading
- Main application structure

### ⚠️ In Progress / Needs Implementation
- ViewModel layer expansion (12 page-specific ViewModels needed)
- Service layer (business logic)
- Repository layer (data persistence)
- Database integration
- File management system
- Settings persistence
- Error handling and validation

### 🔄 Architecture Patterns to Follow

#### Async Operations
```python
# Use threading for long-running operations
def run_analysis_async(self, analysis_func, callback):
    def worker():
        result = analysis_func()
        self.after(0, lambda: callback(result))
    thread = threading.Thread(target=worker)
    thread.start()
```

#### Error Handling
```python
# Consistent error handling pattern
try:
    result = operation()
    return True, result
except Exception as e:
    return False, f"Error: {str(e)}"
```

#### Data Validation
```python
# Input validation before processing
def validate_sequence(sequence: str) -> tuple[bool, str]:
    if not sequence:
        return False, "Sequence cannot be empty"
    valid_chars = set('ATCG')
    if not all(c.upper() in valid_chars for c in sequence):
        return False, "Invalid DNA characters"
    return True, ""
```

## UX/UI Implementation Guidelines

### Loading States & User Feedback
- **Always show loading states** - Use skeleton screens and progress indicators
- **Optimistic UI updates** - Update UI immediately, rollback on error
- **Toast notifications** - Provide immediate feedback for user actions
- **Error boundaries** - Gracefully handle and display errors with retry options

### Component Library Standards
```python
# UX Components to implement (Milestone 1)
views/components/
├── skeleton_loader.py      # Animated loading placeholders
├── loading_indicators.py   # Progress bars and spinners  
├── toast_notifications.py  # Success/error/info messages
├── error_boundary.py       # Error handling with retry
├── empty_states.py         # Helpful empty state messages
└── confirmation_dialog.py  # Confirmation for destructive actions
```

### Core Utilities Pattern
```python
# Essential utilities for professional application
utils/
├── file_importer.py        # ABC pattern for extensible file imports
├── text_history.py         # Undo/redo for text editors
├── logger.py               # Simple logging with rotation
services/
├── state_manager.py        # Application state persistence
└── update_service.py       # GitHub release update checker
```

### Database Strategy
- **DuckDB for analytics** - Fast queries for dashboard stats and reports
- **JSON for configuration** - Settings, themes, and simple data
- **File system for sequences** - Large sequence data stored as files
- **Hybrid approach** - Metadata in database, content in files

### Performance Patterns
```python
# Lazy loading for pages
def show_page(self, name: str):
    if name not in self.pages:
        self.pages[name] = self.page_constructors[name](self.parent)

# Caching for expensive operations
@lru_cache(maxsize=128)
def get_sequence_stats(sequence_id):
    return calculate_stats(sequence_id)

# Pagination for large datasets
class PaginatedTable:
    def __init__(self, data, page_size=50):
        self.page_size = page_size
        # Implementation...
```