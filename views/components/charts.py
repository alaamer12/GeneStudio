"""Chart components for data visualization."""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PieChart(ctk.CTkFrame):
    """Pie chart component."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.figure = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def plot(self, labels, values, title=""):
        """Create pie chart."""
        self.ax.clear()
        self.ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        self.ax.set_title(title)
        self.canvas.draw()


class DonutChart(ctk.CTkFrame):
    """Donut chart component."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.figure = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def plot(self, labels, values, title=""):
        """Create donut chart."""
        self.ax.clear()
        wedges, texts, autotexts = self.ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(width=0.5)
        )
        self.ax.set_title(title)
        self.canvas.draw()


class AreaChart(ctk.CTkFrame):
    """Area chart component."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def plot(self, x_data, y_data, title="", xlabel="", ylabel=""):
        """Create area chart."""
        self.ax.clear()
        self.ax.fill_between(x_data, y_data, alpha=0.5, color='#3B8ED0')
        self.ax.plot(x_data, y_data, color='#1F6AA5', linewidth=2)
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
