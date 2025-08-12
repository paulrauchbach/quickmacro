"""
Classic Windows frame components.
"""

import tkinter as tk
from tkinter import ttk
from .base import ClassicWindowsStyle


class ClassicFrame(tk.Frame):
    """A Windows 7-style frame."""

    def __init__(self, parent, style="flat", **kwargs):
        # Set default Windows 7 styling based on style
        if style == "raised":
            relief = "raised"
            borderwidth = 1
            bg_color = ClassicWindowsStyle.COLORS["bg_dialog"]
        elif style == "sunken":
            relief = "sunken"
            borderwidth = 1
            bg_color = ClassicWindowsStyle.COLORS["bg_window"]
        else:  # flat
            relief = "flat"
            borderwidth = 0
            bg_color = ClassicWindowsStyle.COLORS["bg_window"]

        default_config = {
            "bg": bg_color,
            "relief": relief,
            "borderwidth": borderwidth,
        }

        # Override with any user-specified kwargs
        default_config.update(kwargs)

        super().__init__(parent, **default_config)


class ClassicLabelFrame(tk.LabelFrame):
    """A Windows 7-style label frame (group box)."""

    def __init__(self, parent, text: str = "", **kwargs):
        # Set default Windows 7 styling
        default_config = {
            "text": text,
            "bg": ClassicWindowsStyle.COLORS["bg_window"],
            "fg": ClassicWindowsStyle.COLORS["text_normal"],
            "font": ClassicWindowsStyle.FONTS["default"],
            "relief": "solid",
            "borderwidth": 1,
            "padx": ClassicWindowsStyle.SPACING["md"],
            "pady": ClassicWindowsStyle.SPACING["sm"],
        }

        # Override with any user-specified kwargs
        default_config.update(kwargs)

        super().__init__(parent, **default_config)


class ClassicPanedWindow(tk.PanedWindow):
    """A classic Windows-style paned window."""

    def __init__(self, parent, orient=tk.HORIZONTAL, **kwargs):
        # Set default classic styling
        default_config = {
            "orient": orient,
            "bg": ClassicWindowsStyle.COLORS["bg_window"],
            "relief": "sunken",
            "borderwidth": 1,
            "sashrelief": "raised",
            "sashwidth": 4,
        }

        # Override with any user-specified kwargs
        default_config.update(kwargs)

        super().__init__(parent, **default_config)


class StatusBar(ClassicFrame):
    """A classic Windows-style status bar."""

    def __init__(self, parent, **kwargs):
        # Status bar specific styling
        default_config = {
            "relief": "sunken",
            "borderwidth": 1,
            "height": 24,
        }
        default_config.update(kwargs)

        super().__init__(parent, **default_config)

        # Create status label
        self.status_label = tk.Label(
            self,
            text="Ready",
            bg=ClassicWindowsStyle.COLORS["bg_window"],
            fg=ClassicWindowsStyle.COLORS["text_normal"],
            font=ClassicWindowsStyle.FONTS["small"],
            anchor="w",
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=1)

    def set_text(self, text: str):
        """Set the status bar text."""
        self.status_label.config(text=text)
