"""Settings page."""

import customtkinter as ctk
from views.components import PrimaryButton, SecondaryButton
from utils.themed_tooltips import (
    create_tooltip, create_validation_tooltip, create_info_button_tooltip,
    create_info_button_with_tooltip, TooltipTemplates, create_status_tooltip
)


class SettingsPage(ctk.CTkFrame):
    """Application settings page."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        # Title with info button
        title_container = ctk.CTkFrame(header, fg_color="transparent")
        title_container.pack(side="left", fill="x", expand=True)
        
        title_label = ctk.CTkLabel(
            title_container,
            text="Settings",
            font=("Arial", 24, "bold")
        )
        title_label.pack(side="left")
        
        # Info button for settings
        settings_info_button, settings_info_tooltip = create_info_button_with_tooltip(
            title_container,
            "Application Settings\n\n"
            "Customize GeneStudio Pro to your preferences:\n\n"
            "• Appearance: Theme, colors, and visual settings\n"
            "• Preferences: Workflow and behavior options\n"
            "• Advanced: Performance and debugging settings\n\n"
            "Settings are automatically saved and applied across sessions. "
            "Use Reset to restore default values for any category."
        )
        settings_info_button.pack(side="left", padx=(10, 0))
        
        save_button = PrimaryButton(
            header,
            text="💾 Save Settings",
            width=140
        )
        save_button.pack(side="right", padx=5)
        
        reset_button = SecondaryButton(
            header,
            text="↩️ Reset",
            width=100
        )
        reset_button.pack(side="right", padx=5)
        
        # Add tooltips to header buttons
        create_tooltip(
            save_button,
            TooltipTemplates.keyboard_shortcut(
                "Save all settings changes and apply them immediately",
                "Ctrl+S"
            )
        )
        
        create_tooltip(
            reset_button,
            "Reset all settings in the current tab to their default values. "
            "This action requires confirmation and cannot be undone."
        )
        
        # Settings tabs
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Appearance tab
        appearance_tab = tabview.add("Appearance")
        
        # Theme section
        theme_label = ctk.CTkLabel(
            appearance_tab,
            text="Theme",
            font=("Arial", 12, "bold")
        )
        theme_label.pack(padx=20, pady=(20, 10), anchor="w")
        
        theme_menu = ctk.CTkOptionMenu(
            appearance_tab,
            values=["Dark", "Light", "System"],
            width=200
        )
        theme_menu.pack(padx=20, pady=(0, 20), anchor="w")
        
        # Color scheme section
        color_label = ctk.CTkLabel(
            appearance_tab,
            text="Color Scheme",
            font=("Arial", 12, "bold")
        )
        color_label.pack(padx=20, pady=(10, 10), anchor="w")
        
        color_menu = ctk.CTkOptionMenu(
            appearance_tab,
            values=["Blue", "Green", "Purple", "Red"],
            width=200
        )
        color_menu.pack(padx=20, pady=(0, 20), anchor="w")
        
        # Font size section
        font_label = ctk.CTkLabel(
            appearance_tab,
            text="Font Size",
            font=("Arial", 12, "bold")
        )
        font_label.pack(padx=20, pady=(10, 10), anchor="w")
        
        font_slider = ctk.CTkSlider(
            appearance_tab,
            from_=10,
            to=20,
            number_of_steps=10
        )
        font_slider.pack(padx=20, pady=(0, 20), anchor="w", fill="x")
        
        # Add tooltips to appearance settings
        create_tooltip(
            theme_menu,
            "Application Theme\n\n"
            "Choose the overall appearance mode:\n"
            "• Dark: Dark background with light text (recommended for long sessions)\n"
            "• Light: Light background with dark text (better for printing)\n"
            "• System: Follow your operating system's theme setting"
        )
        
        create_tooltip(
            color_menu,
            "Color Scheme\n\n"
            "Select the accent color for buttons, highlights, and interactive elements:\n"
            "• Blue: Default professional appearance\n"
            "• Green: Nature-inspired, good for biological themes\n"
            "• Purple: Creative and modern look\n"
            "• Red: High contrast, attention-grabbing"
        )
        
        create_tooltip(
            font_slider,
            "Font Size\n\n"
            "Adjust the base font size for all text in the application.\n"
            "Range: 10-20 points\n"
            "• Smaller fonts fit more content on screen\n"
            "• Larger fonts improve readability\n"
            "• Changes apply to all UI elements proportionally"
        )
        
        # Preferences tab
        prefs_tab = tabview.add("Preferences")
        
        autosave_cb = ctk.CTkCheckBox(
            prefs_tab,
            text="Auto-save projects"
        )
        autosave_cb.pack(padx=20, pady=10, anchor="w")
        
        line_numbers_cb = ctk.CTkCheckBox(
            prefs_tab,
            text="Show line numbers in editor"
        )
        line_numbers_cb.pack(padx=20, pady=10, anchor="w")
        
        syntax_highlighting_cb = ctk.CTkCheckBox(
            prefs_tab,
            text="Enable syntax highlighting"
        )
        syntax_highlighting_cb.pack(padx=20, pady=10, anchor="w")
        
        confirm_delete_cb = ctk.CTkCheckBox(
            prefs_tab,
            text="Confirm before deleting"
        )
        confirm_delete_cb.pack(padx=20, pady=10, anchor="w")
        
        show_tooltips_cb = ctk.CTkCheckBox(
            prefs_tab,
            text="Show tooltips"
        )
        show_tooltips_cb.pack(padx=20, pady=10, anchor="w")
        
        # Add tooltips to preference checkboxes
        create_tooltip(
            autosave_cb,
            "Auto-save Projects\n\n"
            "Automatically save project changes at regular intervals.\n"
            "• Prevents data loss from unexpected crashes\n"
            "• Saves every 5 minutes when changes are detected\n"
            "• Does not replace manual saving for important milestones"
        )
        
        create_tooltip(
            line_numbers_cb,
            "Show Line Numbers in Editor\n\n"
            "Display line numbers in the sequence editor for easier navigation.\n"
            "• Helpful for referencing specific positions\n"
            "• Useful when working with large sequences\n"
            "• Makes error reporting more precise"
        )
        
        create_tooltip(
            syntax_highlighting_cb,
            "Enable Syntax Highlighting\n\n"
            "Color-code different nucleotides and sequence elements.\n"
            "• A, T, G, C displayed in different colors\n"
            "• FASTA headers highlighted distinctly\n"
            "• Improves sequence readability and error detection"
        )
        
        create_tooltip(
            confirm_delete_cb,
            "Confirm Before Deleting\n\n"
            "Show confirmation dialogs before permanent deletions.\n"
            "• Prevents accidental data loss\n"
            "• Applies to projects, sequences, and analyses\n"
            "• Recommended for important research data"
        )
        
        create_tooltip(
            show_tooltips_cb,
            "Show Tooltips\n\n"
            "Display helpful tooltips when hovering over UI elements.\n"
            "• Provides context-sensitive help\n"
            "• Explains bioinformatics terminology\n"
            "• Can be disabled to reduce visual clutter"
        )
        
        # Advanced tab
        advanced_tab = tabview.add("Advanced")
        
        # Performance section with info button
        perf_header_container = ctk.CTkFrame(advanced_tab, fg_color="transparent")
        perf_header_container.pack(padx=20, pady=(20, 10), anchor="w", fill="x")
        
        perf_label = ctk.CTkLabel(
            perf_header_container,
            text="Performance",
            font=("Arial", 12, "bold")
        )
        perf_label.pack(side="left", anchor="w")
        
        # Info button for performance settings
        perf_info_button, perf_info_tooltip = create_info_button_with_tooltip(
            perf_header_container,
            "Performance Settings\n\n"
            "Configure computational performance parameters:\n\n"
            "• Max Threads: Number of CPU cores to use for parallel processing\n"
            "• Cache Size: Memory allocated for storing computed results\n\n"
            "Higher values improve performance but use more system resources. "
            "Adjust based on your computer's capabilities and other running applications."
        )
        perf_info_button.pack(side="left", padx=(10, 0))
        
        # Max threads
        threads_label = ctk.CTkLabel(
            advanced_tab,
            text="Max threads:",
            font=("Arial", 10)
        )
        threads_label.pack(padx=20, pady=(5, 2), anchor="w")
        
        threads_entry = ctk.CTkEntry(
            advanced_tab,
            placeholder_text="4",
            width=100
        )
        threads_entry.pack(padx=20, pady=(0, 15), anchor="w")
        
        # Cache size
        cache_label = ctk.CTkLabel(
            advanced_tab,
            text="Cache size (MB):",
            font=("Arial", 10)
        )
        cache_label.pack(padx=20, pady=(5, 2), anchor="w")
        
        cache_entry = ctk.CTkEntry(
            advanced_tab,
            placeholder_text="512",
            width=100
        )
        cache_entry.pack(padx=20, pady=(0, 15), anchor="w")
        
        # Debug options
        debug_cb = ctk.CTkCheckBox(
            advanced_tab,
            text="Enable debug mode"
        )
        debug_cb.pack(padx=20, pady=10, anchor="w")
        
        logging_cb = ctk.CTkCheckBox(
            advanced_tab,
            text="Log all operations"
        )
        logging_cb.pack(padx=20, pady=10, anchor="w")
        
        # Add tooltips to advanced settings
        create_validation_tooltip(
            threads_entry,
            TooltipTemplates.validation_format(
                "Maximum Threads",
                "Number of CPU cores to use (1-16)",
                "4 (recommended for most systems)"
            ) + "\n\nMore threads = faster processing but higher CPU usage"
        )
        
        create_validation_tooltip(
            cache_entry,
            TooltipTemplates.validation_format(
                "Cache Size",
                "Memory for caching results in MB (64-2048)",
                "512 (recommended for most systems)"
            ) + "\n\nLarger cache = faster repeated operations but more RAM usage"
        )
        
        create_tooltip(
            debug_cb,
            "Enable Debug Mode\n\n"
            "Activate detailed debugging information and developer tools.\n"
            "• Shows additional error details\n"
            "• Enables performance profiling\n"
            "• Useful for troubleshooting issues\n"
            "• May impact application performance"
        )
        
        create_tooltip(
            logging_cb,
            "Log All Operations\n\n"
            "Record detailed logs of all application activities.\n"
            "• Tracks user actions and system events\n"
            "• Helpful for debugging and support\n"
            "• Creates larger log files\n"
            "• May slightly impact performance"
        )
