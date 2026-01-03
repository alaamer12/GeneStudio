"""Enhanced visualization page with interactive plots and real-time data binding."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton, InteractivePlotCanvas, PieChart, DonutChart, AreaChart, Enhanced3DVisualization
from viewmodels.visualization_viewmodel import VisualizationViewModel
import numpy as np
from typing import Optional, Dict, Any, List


class VisualizationPage(ctk.CTkFrame):
    """Enhanced visualization hub with interactive plots and real-time capabilities."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Initialize ViewModel
        self.viewmodel = VisualizationViewModel()
        self.viewmodel.add_observer(self._on_viewmodel_update)
        
        # Current state
        self.current_plot_id = None
        self.current_plot_type = "line"
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI components
        self._create_header()
        self._create_sidebar()
        self._create_plot_area()
        
        # Load initial data
        self._load_initial_data()
    
    def _create_header(self):
        """Create the header section."""
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="Data Visualization",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            header,
            text="Ready",
            font=("Arial", 12),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=(20, 0))
        
        # Action buttons
        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.pack(side="right")
        
        self.real_time_btn = SecondaryButton(
            button_frame,
            text="📡 Real-time",
            width=100,
            command=self._toggle_real_time
        )
        self.real_time_btn.pack(side="right", padx=5)
        
        self.export_btn = SecondaryButton(
            button_frame,
            text="💾 Export",
            width=100,
            command=self._export_plot,
            state="disabled"
        )
        self.export_btn.pack(side="right", padx=5)
        
        self.create_btn = PrimaryButton(
            button_frame,
            text="➕ Create Plot",
            width=120,
            command=self._create_new_plot
        )
        self.create_btn.pack(side="right", padx=5)
    
    def _create_sidebar(self):
        """Create the sidebar with controls."""
        sidebar = ctk.CTkFrame(self, width=280)
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        sidebar.grid_propagate(False)
        
        # Active plots section
        ctk.CTkLabel(
            sidebar,
            text="Active Plots",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=(15, 10), anchor="w")
        
        # Scrollable frame for active plots
        self.plots_frame = ctk.CTkScrollableFrame(sidebar, height=120)
        self.plots_frame.pack(fill="x", padx=15, pady=5)
        
        # Plot types section
        ctk.CTkLabel(
            sidebar,
            text="Plot Types",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=(20, 10), anchor="w")
        
        plot_types = [
            ("📈 Line Plot", "line"),
            ("📊 Bar Chart", "bar"),
            ("🔵 Scatter Plot", "scatter"),
            ("🟦 Heatmap", "heatmap"),
            ("🥧 Pie Chart", "pie"),
            ("🍩 Donut Chart", "donut"),
            ("📉 Area Chart", "area"),
            ("📐 3D Surface", "3d_surface"),
            ("🕸️ 3D Graph", "3d_graph")
        ]
        
        self.plot_type_buttons = {}
        for display_name, plot_id in plot_types:
            btn = ctk.CTkButton(
                sidebar,
                text=display_name,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda pid=plot_id: self._select_plot_type(pid)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.plot_type_buttons[plot_id] = btn
        
        # Data sources section
        ctk.CTkLabel(
            sidebar,
            text="Data Sources",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=(20, 10), anchor="w")
        
        # Data source selector
        self.data_source_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.data_source_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            self.data_source_frame,
            text="Source Type:",
            font=("Arial", 10)
        ).pack(anchor="w")
        
        self.source_type_selector = ctk.CTkOptionMenu(
            self.data_source_frame,
            values=["Sequence Data", "Analysis Results", "Project Summary", "Custom Data"],
            width=240,
            command=self._on_source_type_changed
        )
        self.source_type_selector.pack(anchor="w", pady=2)
        
        # Source item selector
        ctk.CTkLabel(
            self.data_source_frame,
            text="Data Item:",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(10, 0))
        
        self.source_item_selector = ctk.CTkOptionMenu(
            self.data_source_frame,
            values=["Select source type first..."],
            width=240
        )
        self.source_item_selector.pack(anchor="w", pady=2)
        
        # Plot configuration section
        ctk.CTkLabel(
            sidebar,
            text="Configuration",
            font=("Arial", 14, "bold")
        ).pack(padx=15, pady=(20, 10), anchor="w")
        
        config_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        config_frame.pack(fill="x", padx=15, pady=5)
        
        # Title entry
        ctk.CTkLabel(
            config_frame,
            text="Plot Title:",
            font=("Arial", 10)
        ).pack(anchor="w")
        
        self.title_entry = ctk.CTkEntry(
            config_frame,
            placeholder_text="Enter plot title...",
            width=240
        )
        self.title_entry.pack(anchor="w", pady=2)
        
        # Interactive controls
        self.interactive_var = ctk.BooleanVar(value=True)
        self.interactive_checkbox = ctk.CTkCheckBox(
            config_frame,
            text="Interactive controls",
            variable=self.interactive_var,
            font=("Arial", 10)
        )
        self.interactive_checkbox.pack(anchor="w", pady=(10, 2))
        
        # Real-time updates
        self.realtime_var = ctk.BooleanVar(value=False)
        self.realtime_checkbox = ctk.CTkCheckBox(
            config_frame,
            text="Real-time updates",
            variable=self.realtime_var,
            font=("Arial", 10)
        )
        self.realtime_checkbox.pack(anchor="w", pady=2)
    
    def _create_plot_area(self):
        """Create the main plot area."""
        plot_frame = ctk.CTkFrame(self)
        plot_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        
        # Container for different plot types
        self.plot_container = ctk.CTkFrame(plot_frame, fg_color="transparent")
        self.plot_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create enhanced plot components
        self.plot_canvas_2d = InteractivePlotCanvas(self.plot_container)
        self.pie_chart = PieChart(self.plot_container)
        self.donut_chart = DonutChart(self.plot_container)
        self.area_chart = AreaChart(self.plot_container)
        self.viz_3d = Enhanced3DVisualization(self.plot_container)
        
        # Set up callbacks
        self.plot_canvas_2d.set_selection_callback(self._on_plot_selection)
        self.plot_canvas_2d.set_update_callback(self._on_plot_update)
        self.viz_3d.set_selection_callback(self._on_3d_selection)
        
        # Initially hide all plots
        self._hide_all_plots()
        
        # Show welcome message
        self.welcome_label = ctk.CTkLabel(
            self.plot_container,
            text="Create a new plot to get started",
            font=("Arial", 16),
            text_color="gray"
        )
        self.welcome_label.pack(expand=True)
    
    def _load_initial_data(self):
        """Load initial data and populate UI."""
        # Load available data sources
        self.viewmodel.load_available_data_sources()
        
        # Set default source type
        self.source_type_selector.set("Sequence Data")
        self._on_source_type_changed("Sequence Data")
    
    def _hide_all_plots(self):
        """Hide all plot components."""
        self.plot_canvas_2d.pack_forget()
        self.pie_chart.pack_forget()
        self.donut_chart.pack_forget()
        self.area_chart.pack_forget()
        self.viz_3d.pack_forget()
        
        if hasattr(self, 'welcome_label'):
            self.welcome_label.pack_forget()
    
    def _select_plot_type(self, plot_type: str):
        """Select a plot type for creation."""
        # Reset button colors
        for btn in self.plot_type_buttons.values():
            btn.configure(fg_color="transparent")
        
        # Highlight selected button
        if plot_type in self.plot_type_buttons:
            self.plot_type_buttons[plot_type].configure(fg_color=("gray75", "gray25"))
        
        self.current_plot_type = plot_type
    
    def _on_source_type_changed(self, source_type: str):
        """Handle data source type change."""
        # Update available items based on source type
        if source_type == "Sequence Data":
            items = ["Demo Sequence 1", "Demo Sequence 2", "Demo Sequence 3"]
        elif source_type == "Analysis Results":
            items = ["GC Content Analysis", "Pattern Match Results", "Translation Results"]
        elif source_type == "Project Summary":
            items = ["Project Statistics", "Sequence Lengths", "Analysis Summary"]
        elif source_type == "Custom Data":
            items = ["Random Data", "Sine Wave", "Sample Dataset"]
        else:
            items = ["No items available"]
        
        self.source_item_selector.configure(values=items)
        if items and items[0] != "No items available":
            self.source_item_selector.set(items[0])
    
    def _create_new_plot(self):
        """Create a new plot with current configuration."""
        try:
            # Get configuration
            plot_type = self.current_plot_type
            title = self.title_entry.get() or f"{plot_type.title()} Plot"
            source_type = self.source_type_selector.get()
            source_item = self.source_item_selector.get()
            
            # Create data source configuration
            data_sources = [{
                'type': 'custom',
                'source_id': f"{source_type}_{source_item}",
                'data_type': self._get_data_type_for_plot(plot_type),
                'generator': 'demo'
            }]
            
            # Create plot configuration
            config = {
                'title': title,
                'interactive': self.interactive_var.get(),
                'real_time': self.realtime_var.get()
            }
            
            # Create plot through ViewModel
            self.viewmodel.create_plot(plot_type, data_sources, config)
            
        except Exception as e:
            self._show_status(f"Error creating plot: {e}", "error")
    
    def _get_data_type_for_plot(self, plot_type: str) -> str:
        """Get appropriate data type for plot type."""
        if plot_type in ['pie', 'donut', 'bar']:
            return 'categorical'
        elif plot_type in ['line', 'area', 'scatter']:
            return 'continuous'
        elif plot_type == 'heatmap':
            return 'matrix'
        elif plot_type.startswith('3d'):
            return '3d'
        else:
            return 'continuous'
    
    def _show_plot(self, plot_id: str):
        """Show a specific plot."""
        self.current_plot_id = plot_id
        self.viewmodel.select_plot(plot_id)
    
    def _update_active_plots_display(self):
        """Update the active plots list."""
        # Clear existing widgets
        for widget in self.plots_frame.winfo_children():
            widget.destroy()
        
        active_plots = self.viewmodel.get_state('active_plots', {})
        
        if not active_plots:
            no_plots_label = ctk.CTkLabel(
                self.plots_frame,
                text="No active plots",
                font=("Arial", 10),
                text_color="gray"
            )
            no_plots_label.pack(pady=10)
            return
        
        for plot_id, plot_info in active_plots.items():
            plot_frame = ctk.CTkFrame(self.plots_frame, fg_color="transparent")
            plot_frame.pack(fill="x", pady=2)
            
            # Plot info button
            plot_btn = ctk.CTkButton(
                plot_frame,
                text=f"{plot_info['type'].title()}: {plot_info.get('config', {}).get('title', 'Untitled')}",
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda pid=plot_id: self._show_plot(pid),
                font=("Arial", 10)
            )
            plot_btn.pack(side="left", fill="x", expand=True)
            
            # Remove button
            remove_btn = ctk.CTkButton(
                plot_frame,
                text="✕",
                width=25,
                height=25,
                command=lambda pid=plot_id: self._remove_plot(pid),
                fg_color="red",
                hover_color="darkred"
            )
            remove_btn.pack(side="right", padx=(5, 0))
    
    def _remove_plot(self, plot_id: str):
        """Remove a plot."""
        self.viewmodel.remove_plot(plot_id)
    
    def _toggle_real_time(self):
        """Toggle real-time updates for current plot."""
        if self.current_plot_id:
            self.viewmodel.enable_real_time_updates(self.current_plot_id)
    
    def _export_plot(self):
        """Export the current plot."""
        if not self.current_plot_id:
            self._show_status("No plot selected for export", "error")
            return
        
        from tkinter import filedialog
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("SVG files", "*.svg"),
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                format_type = filename.split('.')[-1].lower()
                self.viewmodel.export_plot(self.current_plot_id, format_type, filename)
                
        except Exception as e:
            self._show_status(f"Export error: {e}", "error")
    
    def _show_status(self, message: str, status_type: str = "info"):
        """Show status message."""
        colors = {
            "info": "gray",
            "success": "green",
            "error": "red",
            "warning": "orange"
        }
        
        self.status_label.configure(
            text=message,
            text_color=colors.get(status_type, "gray")
        )
        
        # Auto-clear status after 5 seconds for non-error messages
        if status_type != "error":
            self.after(5000, lambda: self.status_label.configure(text="Ready", text_color="gray"))
    
    def _on_plot_selection(self, selection_info: Dict[str, Any]):
        """Handle plot element selection."""
        # Could show selection details in a panel
        pass
    
    def _on_plot_update(self, plot_data: Dict[str, Any]):
        """Handle plot data updates."""
        # Could trigger additional processing
        pass
    
    def _on_3d_selection(self, selection_info: Dict[str, Any]):
        """Handle 3D plot element selection."""
        # Could show 3D selection details
        pass
    
    def _on_viewmodel_update(self, key: str, value: Any):
        """Handle ViewModel state updates."""
        if key == 'active_plots':
            self._update_active_plots_display()
        elif key == 'current_plot_id':
            self._update_current_plot_display(value)
        elif key == 'plot_data_updated':
            self._handle_plot_data_update(value)
        elif key == 'available_data_sources':
            self._update_data_sources_display(value)
        elif key == 'error':
            if value:
                self._show_status(value, "error")
        elif key == 'loading':
            if value:
                self._show_status("Loading...", "info")
    
    def _update_current_plot_display(self, plot_id: Optional[str]):
        """Update the display for the current plot."""
        if not plot_id:
            self._hide_all_plots()
            self.welcome_label.pack(expand=True)
            self.export_btn.configure(state="disabled")
            return
        
        # Get plot data
        plot_data = self.viewmodel.get_current_plot_data()
        if not plot_data:
            return
        
        # Hide all plots first
        self._hide_all_plots()
        
        # Show appropriate plot component
        plot_type = plot_data.get('type', 'line')
        
        if plot_type in ['line', 'bar', 'scatter', 'heatmap']:
            self.plot_canvas_2d.pack(fill="both", expand=True)
            self.plot_canvas_2d.update_data(plot_data)
        elif plot_type == 'pie':
            self.pie_chart.pack(fill="both", expand=True)
            if 'labels' in plot_data and 'values' in plot_data:
                self.pie_chart.plot(plot_data['labels'], plot_data['values'], plot_data.get('title', ''))
        elif plot_type == 'donut':
            self.donut_chart.pack(fill="both", expand=True)
            if 'labels' in plot_data and 'values' in plot_data:
                self.donut_chart.plot(plot_data['labels'], plot_data['values'], plot_data.get('title', ''))
        elif plot_type == 'area':
            self.area_chart.pack(fill="both", expand=True)
            if 'x_data' in plot_data and 'y_data' in plot_data:
                self.area_chart.plot(plot_data['x_data'], plot_data['y_data'], 
                                   plot_data.get('title', ''), 
                                   plot_data.get('xlabel', ''), 
                                   plot_data.get('ylabel', ''))
        elif plot_type.startswith('3d'):
            self.viz_3d.pack(fill="both", expand=True)
            self.viz_3d.update_3d_data(plot_data)
        
        self.export_btn.configure(state="normal")
    
    def _handle_plot_data_update(self, update_info: Dict[str, Any]):
        """Handle real-time plot data updates."""
        plot_id = update_info.get('plot_id')
        if plot_id == self.current_plot_id:
            self._update_current_plot_display(plot_id)
    
    def _update_data_sources_display(self, data_sources: List[Dict[str, Any]]):
        """Update available data sources."""
        # This could populate the data source selectors with real data
        pass


