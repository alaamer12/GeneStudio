"""Analysis page - comprehensive analysis tools with parameter configuration and async execution."""

import customtkinter as ctk
from typing import Optional, Any, List, Dict
from views.components import (
    PrimaryButton, SecondaryButton, DataTable, LinearProgress,
    EmptyAnalyses, SkeletonText, show_success, show_error
)
from viewmodels.analysis_viewmodel import AnalysisViewModel


class AnalysisPage(ctk.CTkFrame):
    """Analysis tools page with real parameter configuration and execution."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Initialize ViewModel
        self.viewmodel = AnalysisViewModel()
        self.viewmodel.add_observer(self._on_state_changed)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create UI components
        self._create_sidebar()
        self._create_main_area()
        
        # Load initial data
        self.after(100, self._initialize_analysis)
    
    def _create_sidebar(self):
        """Create analysis types sidebar."""
        self.sidebar = ctk.CTkFrame(self, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Header
        ctk.CTkLabel(
            self.sidebar,
            text="Analysis Types",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=15, anchor="w")
        
        # Analysis type buttons (will be populated from ViewModel)
        self.analysis_buttons_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.analysis_buttons_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Initially show loading
        self._show_sidebar_loading()
    
    def _create_main_area(self):
        """Create main analysis configuration and results area."""
        self.main_area = ctk.CTkFrame(self)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Initially show empty state
        self._show_empty_analysis_state()
    
    def _show_sidebar_loading(self):
        """Show loading state in sidebar."""
        for widget in self.analysis_buttons_frame.winfo_children():
            widget.destroy()
        
        # Show skeleton text for loading
        for i in range(6):
            skeleton = SkeletonText(self.analysis_buttons_frame, lines=1, width=180)
            skeleton.pack(fill="x", pady=2)
    
    def _show_empty_analysis_state(self):
        """Show empty state when no analysis is selected."""
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()
        
        # Show empty analyses state
        EmptyAnalyses(
            self.main_area,
            on_run_analysis=self._handle_select_first_analysis,
            on_view_templates=self._handle_view_templates
        ).pack(fill="both", expand=True)
    
    def _initialize_analysis(self):
        """Initialize analysis page with available types."""
        # This would typically load available analysis types
        # For now, we'll use the types from ViewModel
        analysis_types = self.viewmodel.get_state('analysis_types', [])
        self._update_analysis_types(analysis_types)
    
    def _on_state_changed(self, key: Optional[str], value: Any):
        """Handle ViewModel state changes."""
        if key == 'analysis_types':
            self._update_analysis_types(value)
        elif key == 'selected_analysis_type':
            self._update_selected_analysis(value)
        elif key == 'analysis_parameters':
            self._update_parameter_display()
        elif key == 'parameter_errors':
            self._update_parameter_errors(value)
        elif key == 'running_analyses':
            self._update_running_analyses(value)
        elif key == 'current_results':
            self._update_results_display(value)
        elif key == 'loading':
            self._update_loading_state(value)
    
    def _update_analysis_types(self, analysis_types: List[Dict]):
        """Update sidebar with available analysis types."""
        # Clear current buttons
        for widget in self.analysis_buttons_frame.winfo_children():
            widget.destroy()
        
        if not analysis_types:
            return
        
        # Create buttons for each analysis type
        for analysis_type in analysis_types:
            button = ctk.CTkButton(
                self.analysis_buttons_frame,
                text=f"{analysis_type.get('icon', '🔬')} {analysis_type['name']}",
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda at=analysis_type: self._select_analysis_type(at)
            )
            button.pack(fill="x", pady=2)
    
    def _select_analysis_type(self, analysis_type: Dict):
        """Select an analysis type."""
        self.viewmodel.select_analysis_type(analysis_type['id'])
    
    def _update_selected_analysis(self, analysis_type: Optional[Dict]):
        """Update main area with selected analysis configuration."""
        if analysis_type is None:
            self._show_empty_analysis_state()
            return
        
        # Clear main area
        for widget in self.main_area.winfo_children():
            widget.destroy()
        
        # Create analysis configuration interface
        self._create_analysis_interface(analysis_type)
    
    def _create_analysis_interface(self, analysis_type: Dict):
        """Create interface for configuring and running analysis."""
        # Header
        header_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        # Analysis title and description
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"{analysis_type.get('icon', '🔬')} {analysis_type['name']}",
            font=("Arial", 20, "bold")
        )
        title_label.pack(side="left")
        
        # Run button
        self.run_button = PrimaryButton(
            header_frame,
            text="▶️ Run Analysis",
            width=150,
            command=self._handle_run_analysis
        )
        self.run_button.pack(side="right")
        
        # Description
        if analysis_type.get('description'):
            desc_label = ctk.CTkLabel(
                self.main_area,
                text=analysis_type['description'],
                font=("Arial", 12),
                text_color="gray",
                wraplength=600,
                justify="left"
            )
            desc_label.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Sequence selection
        self._create_sequence_selection()
        
        # Parameter configuration
        self._create_parameter_configuration(analysis_type)
        
        # Results area
        self._create_results_area()
    
    def _create_sequence_selection(self):
        """Create sequence selection interface."""
        seq_frame = ctk.CTkFrame(self.main_area)
        seq_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            seq_frame,
            text="Sequence Selection",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        # Available sequences (would be populated from ViewModel)
        available_sequences = self.viewmodel.get_state('available_sequences', [])
        
        if not available_sequences:
            # Show message about no sequences
            no_seq_label = ctk.CTkLabel(
                seq_frame,
                text="No sequences available. Please load sequences first.",
                text_color="gray"
            )
            no_seq_label.pack(padx=20, pady=(0, 15))
        else:
            # Create sequence selection interface
            seq_scroll = ctk.CTkScrollableFrame(seq_frame, height=100)
            seq_scroll.pack(fill="x", padx=20, pady=(0, 15))
            
            for sequence in available_sequences:
                seq_checkbox = ctk.CTkCheckBox(
                    seq_scroll,
                    text=f"{sequence.header} ({len(sequence.sequence)} bp)",
                    command=lambda s=sequence: self._toggle_sequence_selection(s)
                )
                seq_checkbox.pack(anchor="w", pady=2)
    
    def _create_parameter_configuration(self, analysis_type: Dict):
        """Create parameter configuration interface."""
        params_frame = ctk.CTkFrame(self.main_area)
        params_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            params_frame,
            text="Parameters",
            font=("Arial", 14, "bold")
        ).pack(padx=20, pady=(15, 10), anchor="w")
        
        # Parameter widgets
        self.parameter_widgets = {}
        parameters = analysis_type.get('parameters', [])
        
        for param in parameters:
            self._create_parameter_widget(params_frame, param)
    
    def _create_parameter_widget(self, parent, param: Dict):
        """Create a widget for a single parameter."""
        param_frame = ctk.CTkFrame(parent, fg_color="transparent")
        param_frame.pack(fill="x", padx=20, pady=5)
        
        # Parameter label
        label_text = param['label']
        if param.get('required', False):
            label_text += " *"
        
        param_label = ctk.CTkLabel(
            param_frame,
            text=label_text,
            font=("Arial", 11)
        )
        param_label.pack(anchor="w", pady=(0, 2))
        
        # Parameter widget based on type
        param_type = param.get('type', 'string')
        param_name = param['name']
        
        if param_type == 'string':
            widget = ctk.CTkEntry(
                param_frame,
                placeholder_text=param.get('description', ''),
                height=30
            )
            if param.get('default'):
                widget.insert(0, str(param['default']))
        
        elif param_type == 'integer':
            widget = ctk.CTkEntry(
                param_frame,
                placeholder_text=f"Default: {param.get('default', '')}",
                height=30
            )
            if param.get('default') is not None:
                widget.insert(0, str(param['default']))
        
        elif param_type == 'boolean':
            widget = ctk.CTkCheckBox(
                param_frame,
                text=param.get('description', ''),
                command=lambda: self._update_parameter(param_name, widget.get())
            )
            if param.get('default', False):
                widget.select()
        
        elif param_type == 'choice':
            choices = param.get('choices', [])
            widget = ctk.CTkOptionMenu(
                param_frame,
                values=[str(choice) for choice in choices],
                command=lambda value: self._update_parameter(param_name, value)
            )
            if param.get('default') is not None:
                widget.set(str(param['default']))
        
        else:
            # Default to string entry
            widget = ctk.CTkEntry(
                param_frame,
                placeholder_text=param.get('description', ''),
                height=30
            )
        
        widget.pack(fill="x", pady=(0, 5))
        
        # Bind change events for non-checkbox widgets
        if param_type != 'boolean' and param_type != 'choice':
            widget.bind("<KeyRelease>", lambda e: self._update_parameter(param_name, widget.get()))
        
        # Store widget reference
        self.parameter_widgets[param_name] = widget
        
        # Description
        if param.get('description') and param_type != 'boolean':
            desc_label = ctk.CTkLabel(
                param_frame,
                text=param['description'],
                font=("Arial", 9),
                text_color="gray"
            )
            desc_label.pack(anchor="w", pady=(0, 5))
    
    def _create_results_area(self):
        """Create results display area."""
        self.results_frame = ctk.CTkFrame(self.main_area)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Results header
        results_header = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        results_header.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            results_header,
            text="Results",
            font=("Arial", 14, "bold")
        ).pack(side="left")
        
        # Progress bar (initially hidden)
        self.progress_bar = LinearProgress(
            results_header,
            mode="indeterminate"
        )
        
        # Results content
        self.results_text = ctk.CTkTextbox(
            self.results_frame,
            font=("Courier", 11),
            state="disabled"
        )
        self.results_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Initial message
        self._update_results_text("Results will appear here after running analysis...")
    
    def _toggle_sequence_selection(self, sequence):
        """Toggle sequence selection."""
        selected_sequences = self.viewmodel.get_state('selected_sequences', [])
        
        if sequence.id in [s.id for s in selected_sequences]:
            # Remove from selection
            selected_sequences = [s for s in selected_sequences if s.id != sequence.id]
        else:
            # Add to selection
            selected_sequences.append(sequence)
        
        self.viewmodel.update_state('selected_sequences', selected_sequences)
    
    def _update_parameter(self, param_name: str, value: Any):
        """Update parameter value in ViewModel."""
        current_params = self.viewmodel.get_state('analysis_parameters', {})
        current_params[param_name] = value
        self.viewmodel.update_state('analysis_parameters', current_params)
    
    def _update_parameter_display(self):
        """Update parameter widgets with current values."""
        parameters = self.viewmodel.get_state('analysis_parameters', {})
        
        for param_name, widget in self.parameter_widgets.items():
            if param_name in parameters:
                value = parameters[param_name]
                
                if isinstance(widget, ctk.CTkEntry):
                    current_value = widget.get()
                    if current_value != str(value):
                        widget.delete(0, "end")
                        widget.insert(0, str(value))
                elif isinstance(widget, ctk.CTkCheckBox):
                    if value != widget.get():
                        if value:
                            widget.select()
                        else:
                            widget.deselect()
                elif isinstance(widget, ctk.CTkOptionMenu):
                    widget.set(str(value))
    
    def _update_parameter_errors(self, errors: Dict[str, str]):
        """Update parameter error display."""
        # This would highlight parameters with errors
        # For now, we'll just show error messages
        if errors:
            error_messages = []
            for param, error in errors.items():
                error_messages.append(f"{param}: {error}")
            
            show_error("Parameter errors:\n" + "\n".join(error_messages))
    
    def _update_running_analyses(self, running_analyses: List):
        """Update display of running analyses."""
        if running_analyses:
            # Show progress bar
            self.progress_bar.pack(side="right", padx=(10, 0))
            self.progress_bar.start_indeterminate()
            
            # Update run button
            if hasattr(self, 'run_button'):
                self.run_button.configure(text="⏳ Running...", state="disabled")
        else:
            # Hide progress bar
            self.progress_bar.pack_forget()
            self.progress_bar.stop_indeterminate()
            
            # Update run button
            if hasattr(self, 'run_button'):
                self.run_button.configure(text="▶️ Run Analysis", state="normal")
    
    def _update_results_display(self, results: Optional[Dict]):
        """Update results display."""
        if results is None:
            self._update_results_text("Results will appear here after running analysis...")
        else:
            # Format and display results
            formatted_results = self._format_results(results)
            self._update_results_text(formatted_results)
    
    def _update_results_text(self, text: str):
        """Update results text widget."""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", text)
        self.results_text.configure(state="disabled")
    
    def _format_results(self, results: Dict) -> str:
        """Format analysis results for display."""
        formatted = "Analysis Results\n"
        formatted += "=" * 50 + "\n\n"
        
        for key, value in results.items():
            if isinstance(value, dict):
                formatted += f"{key.title()}:\n"
                for sub_key, sub_value in value.items():
                    formatted += f"  {sub_key}: {sub_value}\n"
                formatted += "\n"
            elif isinstance(value, list):
                formatted += f"{key.title()}:\n"
                for i, item in enumerate(value, 1):
                    formatted += f"  {i}. {item}\n"
                formatted += "\n"
            else:
                formatted += f"{key.title()}: {value}\n"
        
        return formatted
    
    def _update_loading_state(self, loading: bool):
        """Update loading state display."""
        # This would show/hide loading indicators
        pass
    
    # Event handlers
    def _handle_select_first_analysis(self):
        """Handle selecting the first available analysis type."""
        analysis_types = self.viewmodel.get_state('analysis_types', [])
        if analysis_types:
            self._select_analysis_type(analysis_types[0])
    
    def _handle_view_templates(self):
        """Handle view analysis templates action."""
        show_success("Analysis templates would be shown here")
    
    def _handle_run_analysis(self):
        """Handle run analysis button click."""
        # Validate that sequences are selected
        selected_sequences = self.viewmodel.get_state('selected_sequences', [])
        if not selected_sequences:
            show_error("Please select at least one sequence for analysis")
            return
        
        # Validate parameters
        analysis_type = self.viewmodel.get_state('selected_analysis_type')
        parameters = self.viewmodel.get_state('analysis_parameters', {})
        
        if analysis_type:
            # Run analysis through ViewModel
            self.viewmodel.run_analysis(
                analysis_type['id'],
                selected_sequences,
                parameters
            )
    
    def set_current_project(self, project_id: int):
        """Set the current project for analysis operations."""
        self.viewmodel.set_current_project(project_id)
    
    def cleanup(self):
        """Cleanup resources when page is destroyed."""
        if hasattr(self, 'viewmodel'):
            self.viewmodel.cleanup()
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass
