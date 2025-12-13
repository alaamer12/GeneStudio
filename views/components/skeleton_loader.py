"""Skeleton loading components with shimmer animations."""

import customtkinter as ctk
import threading
import time
from typing import Optional


class SkeletonBase(ctk.CTkFrame):
    """Base class for skeleton loading components with shimmer animation."""
    
    def __init__(self, parent, width: int = 200, height: int = 50, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        
        # Animation properties
        self.shimmer_active = True
        self.shimmer_position = 0.0
        self.shimmer_direction = 1
        self.animation_id = None
        
        # Colors for shimmer effect
        self.base_color = "#2b2b2b"
        self.shimmer_color = "#3b3b3b"
        
        # Completely disable shimmer animation to prevent threading issues
        # Animation disabled - no shimmer effects
        pass
    
    def start_shimmer(self):
        """Start the shimmer animation."""
        if self.animation_id is None:
            self.shimmer_active = True
            self._schedule_next_frame()
    
    def stop_shimmer(self):
        """Stop the shimmer animation."""
        self.shimmer_active = False
        if self.animation_id is not None:
            try:
                self.after_cancel(self.animation_id)
            except:
                pass
            self.animation_id = None
    
    def destroy(self):
        """Override destroy to ensure animation is stopped."""
        self.stop_shimmer()
        super().destroy()
    
    def __del__(self):
        """Ensure animation is stopped when object is deleted."""
        try:
            self.stop_shimmer()
        except:
            pass
    
    def _schedule_next_frame(self):
        """Schedule the next animation frame."""
        if self.shimmer_active:
            try:
                # Update shimmer position
                self.shimmer_position += 0.02 * self.shimmer_direction
                
                # Reverse direction at boundaries
                if self.shimmer_position >= 1.0:
                    self.shimmer_position = 1.0
                    self.shimmer_direction = -1
                elif self.shimmer_position <= 0.0:
                    self.shimmer_position = 0.0
                    self.shimmer_direction = 1
                
                # Update visual effect
                self._update_shimmer()
                
                # Schedule next frame
                self.animation_id = self.after(50, self._schedule_next_frame)
            except Exception:
                # Widget destroyed or error, stop animation
                self.stop_shimmer()
    
    def _update_shimmer(self):
        """Update the shimmer visual effect."""
        # Animation completely disabled to prevent widget destruction errors
        return
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb: tuple) -> str:
        """Convert RGB tuple to hex color."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def destroy(self):
        """Clean up animation when destroying component."""
        self.stop_shimmer()
        super().destroy()


class SkeletonCard(SkeletonBase):
    """Skeleton placeholder for card components."""
    
    def __init__(self, parent, width: int = 200, height: int = 120, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        
        # Configure card appearance
        self.configure(corner_radius=8)
        
        # Add skeleton elements
        self._create_skeleton_elements()
    
    def _create_skeleton_elements(self):
        """Create skeleton elements that match card structure."""
        # Title placeholder
        title_skeleton = ctk.CTkFrame(
            self,
            width=120,
            height=16,
            fg_color="#3b3b3b",
            corner_radius=4
        )
        title_skeleton.place(x=16, y=16)
        
        # Value placeholder
        value_skeleton = ctk.CTkFrame(
            self,
            width=80,
            height=24,
            fg_color="#3b3b3b",
            corner_radius=4
        )
        value_skeleton.place(x=16, y=45)
        
        # Icon placeholder
        icon_skeleton = ctk.CTkFrame(
            self,
            width=32,
            height=32,
            fg_color="#3b3b3b",
            corner_radius=16
        )
        icon_skeleton.place(x=150, y=20)


class SkeletonTable(SkeletonBase):
    """Skeleton placeholder for table components."""
    
    def __init__(self, parent, rows: int = 5, width: int = 600, height: int = 300, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        
        self.rows = rows
        
        # Configure table appearance
        self.configure(corner_radius=8)
        
        # Add skeleton rows
        self._create_skeleton_rows()
    
    def _create_skeleton_rows(self):
        """Create skeleton rows that match table structure."""
        row_height = 40
        header_height = 35
        
        # Header row
        header_frame = ctk.CTkFrame(
            self,
            width=self.cget("width") - 20,
            height=header_height,
            fg_color="#3b3b3b",
            corner_radius=4
        )
        header_frame.place(x=10, y=10)
        
        # Data rows
        for i in range(self.rows):
            y_pos = 10 + header_height + 5 + (i * (row_height + 5))
            
            row_frame = ctk.CTkFrame(
                self,
                width=self.cget("width") - 20,
                height=row_height,
                fg_color="#2b2b2b",
                corner_radius=4
            )
            row_frame.place(x=10, y=y_pos)
            
            # Add column placeholders
            col_widths = [100, 150, 80, 120]  # Typical column widths
            x_offset = 10
            
            for width in col_widths:
                col_skeleton = ctk.CTkFrame(
                    row_frame,
                    width=width,
                    height=20,
                    fg_color="#3b3b3b",
                    corner_radius=3
                )
                col_skeleton.place(x=x_offset, y=10)
                x_offset += width + 15


class SkeletonText(SkeletonBase):
    """Skeleton placeholder for text blocks."""
    
    def __init__(self, parent, lines: int = 3, width: int = 400, **kwargs):
        line_height = 20
        line_spacing = 8
        total_height = (lines * line_height) + ((lines - 1) * line_spacing) + 20
        
        super().__init__(parent, width=width, height=total_height, **kwargs)
        
        self.lines = lines
        
        # Configure text appearance
        self.configure(corner_radius=8)
        
        # Add skeleton lines
        self._create_skeleton_lines()
    
    def _create_skeleton_lines(self):
        """Create skeleton lines that match text structure."""
        line_height = 20
        line_spacing = 8
        
        for i in range(self.lines):
            y_pos = 10 + (i * (line_height + line_spacing))
            
            # Vary line widths to look more natural
            if i == self.lines - 1:  # Last line is shorter
                line_width = int(self.cget("width") * 0.6)
            else:
                line_width = int(self.cget("width") * 0.9)
            
            line_skeleton = ctk.CTkFrame(
                self,
                width=line_width,
                height=line_height,
                fg_color="#3b3b3b",
                corner_radius=4
            )
            line_skeleton.place(x=10, y=y_pos)


class SkeletonList(SkeletonBase):
    """Skeleton placeholder for list components."""
    
    def __init__(self, parent, items: int = 4, width: int = 300, **kwargs):
        item_height = 50
        item_spacing = 5
        total_height = (items * item_height) + ((items - 1) * item_spacing) + 20
        
        super().__init__(parent, width=width, height=total_height, **kwargs)
        
        self.items = items
        
        # Configure list appearance
        self.configure(corner_radius=8)
        
        # Add skeleton items
        self._create_skeleton_items()
    
    def _create_skeleton_items(self):
        """Create skeleton items that match list structure."""
        item_height = 50
        item_spacing = 5
        
        for i in range(self.items):
            y_pos = 10 + (i * (item_height + item_spacing))
            
            item_frame = ctk.CTkFrame(
                self,
                width=self.cget("width") - 20,
                height=item_height,
                fg_color="#2b2b2b",
                corner_radius=6
            )
            item_frame.place(x=10, y=y_pos)
            
            # Add item content placeholders
            # Icon placeholder
            icon_skeleton = ctk.CTkFrame(
                item_frame,
                width=24,
                height=24,
                fg_color="#3b3b3b",
                corner_radius=12
            )
            icon_skeleton.place(x=15, y=13)
            
            # Title placeholder
            title_skeleton = ctk.CTkFrame(
                item_frame,
                width=120,
                height=14,
                fg_color="#3b3b3b",
                corner_radius=3
            )
            title_skeleton.place(x=50, y=10)
            
            # Subtitle placeholder
            subtitle_skeleton = ctk.CTkFrame(
                item_frame,
                width=80,
                height=12,
                fg_color="#3b3b3b",
                corner_radius=3
            )
            subtitle_skeleton.place(x=50, y=28)