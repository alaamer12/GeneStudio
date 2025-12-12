# GeneStudio Pro - Core Utilities Reference

## 📁 New Core Utilities (Milestone 1)

All new utilities are added to support essential functionality without overcomplicating the application.

---

## 1. 📂 **File Importer (ABC Pattern)**

### `utils/file_importer.py`

**Purpose:** Extensible file import system using Abstract Base Class pattern

**Components:**

```python
from abc import ABC, abstractmethod
from typing import List, Tuple

class FileImporter(ABC):
    """Abstract base class for all file importers."""
    
    @abstractmethod
    def can_import(self, filepath: str) -> bool:
        """Check if this importer can handle the file."""
        pass
    
    @abstractmethod
    def import_file(self, filepath: str) -> List[Tuple[str, str]]:
        """Import file and return list of (header, sequence) tuples."""
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """Return the format name (e.g., 'FASTA', 'GenBank')."""
        pass


class FASTAImporter(FileImporter):
    """FASTA file importer."""
    
    def can_import(self, filepath: str) -> bool:
        return filepath.lower().endswith(('.fasta', '.fa', '.fna'))
    
    def import_file(self, filepath: str) -> List[Tuple[str, str]]:
        # Use existing algorithms.read_fasta
        from algorithms import read_fasta
        return read_fasta(filepath)
    
    def get_format_name(self) -> str:
        return "FASTA"


# Future importers can be added easily:
# class GenBankImporter(FileImporter): ...
# class FASTQImporter(FileImporter): ...
# class GFFImporter(FileImporter): ...
```

**Usage:**
```python
from utils.file_importer import FASTAImporter

importer = FASTAImporter()
if importer.can_import("sequences.fasta"):
    sequences = importer.import_file("sequences.fasta")
```

**Benefits:**
- Easy to add new formats (just create new class)
- Consistent interface for all importers
- Auto-detection of file formats

---

## 2. ↩️ **Text History (Undo/Redo)**

### `utils/text_history.py`

**Purpose:** Simple undo/redo for text input widgets

**Components:**

```python
class TextHistory:
    """Simple undo/redo stack for text widgets."""
    
    def __init__(self, max_history: int = 50):
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = max_history
        self.current_text = ""
    
    def record_change(self, new_text: str):
        """Record a text change."""
        if new_text != self.current_text:
            self.undo_stack.append(self.current_text)
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
            self.redo_stack.clear()
            self.current_text = new_text
    
    def undo(self) -> str:
        """Undo last change and return previous text."""
        if self.undo_stack:
            self.redo_stack.append(self.current_text)
            self.current_text = self.undo_stack.pop()
        return self.current_text
    
    def redo(self) -> str:
        """Redo last undone change and return text."""
        if self.redo_stack:
            self.undo_stack.append(self.current_text)
            self.current_text = self.redo_stack.pop()
        return self.current_text
    
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0
```

**Usage:**
```python
from utils.text_history import TextHistory

# In your text editor widget
class SequenceEditor(ctk.CTkTextbox):
    def __init__(self, parent):
        super().__init__(parent)
        self.history = TextHistory()
        
        # Bind text changes
        self.bind("<KeyRelease>", self._on_text_change)
    
    def _on_text_change(self, event):
        text = self.get("1.0", "end-1c")
        self.history.record_change(text)
    
    def undo(self):
        if self.history.can_undo():
            text = self.history.undo()
            self.delete("1.0", "end")
            self.insert("1.0", text)
    
    def redo(self):
        if self.history.can_redo():
            text = self.history.redo()
            self.delete("1.0", "end")
            self.insert("1.0", text)
```

**Features:**
- Simple stack-based undo/redo
- Configurable history limit
- Works with any text widget

---

## 3. 💾 **State Manager (Keep State)**

### `services/state_manager.py`

**Purpose:** Save and restore application state on close/open

**Components:**

```python
import json
from pathlib import Path

class StateManager:
    """Manage application state persistence."""
    
    def __init__(self, state_file: str = "app_state.json"):
        self.state_file = Path(state_file)
        self.state = {}
    
    def save_state(self, state: dict):
        """Save application state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Failed to save state: {e}")
    
    def restore_state(self) -> dict:
        """Restore application state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to restore state: {e}")
        return {}
    
    def clear_state(self):
        """Clear saved state."""
        if self.state_file.exists():
            self.state_file.unlink()
```

**Usage:**
```python
from services.state_manager import StateManager

# In main_window.py
class MainWindowPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.state_manager = StateManager()
        
        # Restore state on startup
        self._restore_state()
        
        # Save state on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _restore_state(self):
        state = self.state_manager.restore_state()
        
        # Restore window position
        if "window_geometry" in state:
            self.geometry(state["window_geometry"])
        
        # Restore last open page
        if "last_page" in state:
            self.page_manager.show_page(state["last_page"])
        
        # Restore recent files
        if "recent_files" in state:
            self.recent_files = state["recent_files"]
    
    def _on_close(self):
        # Save current state
        state = {
            "window_geometry": self.geometry(),
            "last_page": self.page_manager.current_page,
            "recent_files": getattr(self, 'recent_files', []),
            "theme": ctk.get_appearance_mode()
        }
        self.state_manager.save_state(state)
        self.destroy()
```

**State Saved:**
- Window position and size
- Last active page
- Recent files list
- Theme preference
- Open tabs
- Any other app preferences

---

## 4. 📝 **Simple Logger**

### `utils/logger.py`

**Purpose:** Simple logging system with file rotation

**Components:**

```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(
    name: str = "genestudio",
    log_file: str = "genestudio.log",
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 3
) -> logging.Logger:
    """Setup simple logger with file rotation."""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create logs directory if needed
    log_path = Path("logs") / log_file
    log_path.parent.mkdir(exist_ok=True)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Convenience functions
_logger = None

def get_logger():
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger

def log_info(message: str):
    get_logger().info(message)

def log_error(message: str, exc_info=False):
    get_logger().error(message, exc_info=exc_info)

def log_warning(message: str):
    get_logger().warning(message)

def log_debug(message: str):
    get_logger().debug(message)
```

**Usage:**
```python
from utils.logger import log_info, log_error, log_warning

# In your code
log_info("Application started")
log_info(f"Loaded {len(sequences)} sequences")

try:
    # Some operation
    pass
except Exception as e:
    log_error(f"Failed to load file: {e}", exc_info=True)

log_warning("Large file detected, this may take a while")
```

**Features:**
- Automatic log file rotation (10MB max, 3 backups)
- Logs to both file and console
- Simple API (log_info, log_error, etc.)
- Logs stored in `logs/` directory

---

## 5. 🔄 **Update Service**

### `services/update_service.py`

**Purpose:** Simple update checker for GitHub releases

**Components:**

```python
import requests
from typing import Optional, Dict

class UpdateService:
    """Simple update checker for GitHub releases."""
    
    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        current_version: str
    ):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    def check_for_updates(self) -> Optional[Dict]:
        """Check if a new version is available."""
        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").lstrip("v")
                
                if self._is_newer_version(latest_version):
                    return {
                        "version": latest_version,
                        "url": data.get("html_url"),
                        "notes": data.get("body", ""),
                        "published_at": data.get("published_at")
                    }
        except Exception as e:
            print(f"Failed to check for updates: {e}")
        
        return None
    
    def _is_newer_version(self, latest: str) -> bool:
        """Compare version strings (simple comparison)."""
        try:
            current_parts = [int(x) for x in self.current_version.split(".")]
            latest_parts = [int(x) for x in latest.split(".")]
            return latest_parts > current_parts
        except:
            return False
    
    def notify_update_available(self, update_info: Dict):
        """Show update notification (to be implemented with toast)."""
        from views.components.toast_notifications import show_info
        message = f"New version {update_info['version']} is available!"
        show_info(message)
```

**Usage:**
```python
from services.update_service import UpdateService

# In main.py or main_window.py
class MainWindowPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Check for updates on startup (async)
        self.after(2000, self._check_updates)  # Check after 2 seconds
    
    def _check_updates(self):
        update_service = UpdateService(
            repo_owner="yourusername",
            repo_name="genestudio",
            current_version="1.0.0"
        )
        
        update_info = update_service.check_for_updates()
        if update_info:
            update_service.notify_update_available(update_info)
```

**Features:**
- Checks GitHub releases API
- Simple version comparison
- Non-blocking (runs in background)
- Shows toast notification if update available
- No auto-download (just notification)

---

## 📋 **Implementation Checklist**

### Milestone 1 - Core Utilities

- [ ] **File Importer**
  - [ ] FileImporter ABC
  - [ ] FASTAImporter implementation
  - [ ] Auto-detection logic
  - [ ] Integration with workspace

- [ ] **Text History**
  - [ ] TextHistory class
  - [ ] Undo/redo methods
  - [ ] Integration with sequence editor
  - [ ] Button handlers (Ctrl+Z, Ctrl+Y optional)

- [ ] **State Manager**
  - [ ] StateManager class
  - [ ] Save state on close
  - [ ] Restore state on open
  - [ ] Window geometry persistence
  - [ ] Recent files persistence

- [ ] **Logger**
  - [ ] setup_logger function
  - [ ] File rotation
  - [ ] Convenience functions
  - [ ] Integration throughout app

- [ ] **Update Service**
  - [ ] UpdateService class
  - [ ] GitHub API integration
  - [ ] Version comparison
  - [ ] Toast notification
  - [ ] Background check on startup

---

## 💡 **Design Principles**

1. **Keep It Simple** - No over-engineering
2. **Extensible** - Easy to add new features (e.g., new file formats)
3. **Non-Intrusive** - Utilities don't block main functionality
4. **Fail Gracefully** - Errors in utilities don't crash the app
5. **Well-Documented** - Clear docstrings and examples

---

## 🎯 **Benefits**

✅ **File Importer ABC** - Future-proof for new formats
✅ **Text History** - Professional editor experience
✅ **State Manager** - Seamless user experience
✅ **Simple Logger** - Easy debugging and support
✅ **Update Service** - Keep users informed

**All utilities are simple, focused, and add real value without complexity!** 🚀
