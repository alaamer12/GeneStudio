# GeneStudio Pro - Product Overview

ALWAYS RUN FROM `.venv`. ie. `.venv\scripts\python <command>`
IF YOU ARE GOING TO RUN THE GUI [ie. main.py] just compile it or RUN IT with time off to terminate if it passed without errors

## What is GeneStudio?

GeneStudio is a modern desktop GUI application for DNA sequence analysis and bioinformatics algorithms. It's designed as an educational yet powerful tool that brings classical string-matching algorithms and biological sequence operations into a clean, intuitive interface.

## Target Users

- **Students** learning bioinformatics and computational biology
- **Researchers** needing quick sequence analysis without heavy bioinformatics software
- **Developers** exploring algorithm implementations in biological contexts

## Core Value Proposition

GeneStudio demonstrates how classical computer science algorithms (Boyer-Moore, suffix arrays, dynamic programming) can be applied to real biological sequences, making complex bioinformatics accessible without requiring deep domain knowledge.

## Key Features

### Sequence Processing
- FASTA file loading and parsing
- Basic sequence operations (reverse, complement, reverse-complement)
- GC content calculation
- DNA to amino acid translation

### Pattern Matching Algorithms
- Boyer-Moore (bad character and good suffix rules)
- Suffix array construction and search
- Approximate matching (Hamming distance, edit distance)

### Graph Analysis
- Overlap graph construction from multiple sequences
- Visualization and analysis of sequence relationships

### Professional Interface
- Multi-page enterprise-grade GUI
- Project management and workspace organization
- Visualization and reporting capabilities
- Export functionality for results and reports

## Technical Philosophy

All core algorithms are implemented from scratch without external bioinformatics libraries, making the codebase educational and transparent while maintaining professional-grade performance and usability.

## Enterprise Features

### Multi-Page Architecture
- **12 distinct application pages** with professional navigation
- **Page manager with routing** and navigation history
- **Collapsible sidebar** with organized sections and icons
- **Breadcrumb navigation** and real-time status updates

### Professional UI Components
- **Reusable component library** (buttons, cards, tables, modals)
- **Advanced visualizations** (2D plots, charts, 3D graphics)
- **Interactive data tables** with sorting and filtering
- **Theme system** with dark/light modes

### User Experience Focus
- **Loading states** with skeleton screens and progress indicators
- **Error handling** with user-friendly messages and retry options
- **Empty states** that guide users on next actions
- **Toast notifications** for immediate feedback
- **Confirmation dialogs** for destructive actions

### Data Management
- **Project-based workflow** with templates and organization
- **Sequence library** with metadata and search capabilities
- **Analysis history** and result persistence
- **Multiple export formats** (PDF, Excel, CSV, HTML, JSON)

## Development Milestones

### Current Status: UI Complete, Backend Integration Needed
- ✅ **Complete enterprise GUI** (12 pages, navigation, components)
- ✅ **Core algorithms implemented** (8 bioinformatics modules)
- ⚠️ **UI and backend disconnected** - needs integration layer
- ❌ **No data persistence** - needs database and file management
- ❌ **No user settings** - needs configuration system

### Implementation Priority
1. **Foundation & Core Integration** - Connect UI to algorithms with proper data flow
2. **Advanced Analysis & Visualization** - Real data binding and interactive features  
3. **Reports, Export & User Experience** - Professional reporting and settings
4. **Performance & Polish** - Optimization and final refinements