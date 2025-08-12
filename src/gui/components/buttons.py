"""
Classic Windows button components.
"""

import tkinter as tk
from typing import Callable, Optional
from .base import ClassicWindowsStyle


class ClassicButton(tk.Button):
    """A Windows 7-style button."""

    def __init__(self, parent, text: str, command: Optional[Callable] = None, **kwargs):
        # Set default Windows 7 styling
        default_config = {
            "text": text,
            "command": command,
            "bg": ClassicWindowsStyle.COLORS["bg_button"],
            "fg": ClassicWindowsStyle.COLORS["text_normal"],
            "font": ClassicWindowsStyle.FONTS["default"],
            "relief": "flat",
            "borderwidth": 1,
            "padx": 12,
            "pady": 6,
            "cursor": "hand2",
        }

        # Override with any user-specified kwargs
        default_config.update(kwargs)

        super().__init__(parent, **default_config)

        # Bind hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, event):
        """Handle mouse enter."""
        if self["state"] != "disabled":
            self.config(bg=ClassicWindowsStyle.COLORS["bg_hover"])

    def _on_leave(self, event):
        """Handle mouse leave."""
        if self["state"] != "disabled":
            self.config(bg=ClassicWindowsStyle.COLORS["bg_button"])

    def _on_press(self, event):
        """Handle button press."""
        if self["state"] != "disabled":
            self.config(relief="sunken", bg=ClassicWindowsStyle.COLORS["bg_pressed"])

    def _on_release(self, event):
        """Handle button release."""
        if self["state"] != "disabled":
            self.config(relief="flat", bg=ClassicWindowsStyle.COLORS["bg_hover"])


class ClassicCheckButton(tk.Checkbutton):
    """A classic Windows-style checkbutton."""

    def __init__(
        self, parent, text: str, variable: Optional[tk.Variable] = None, **kwargs
    ):
        # Set default classic styling
        default_config = {
            "text": text,
            "variable": variable,
            "bg": ClassicWindowsStyle.COLORS["bg_window"],
            "fg": ClassicWindowsStyle.COLORS["text_normal"],
            "font": ClassicWindowsStyle.FONTS["default"],
            "relief": "flat",
            "borderwidth": 0,
            "highlightthickness": 0,
            "selectcolor": ClassicWindowsStyle.COLORS["bg_window"],
        }

        # Override with any user-specified kwargs
        default_config.update(kwargs)

        super().__init__(parent, **default_config)


class ClassicRadioButton(tk.Radiobutton):
    """A classic Windows-style radiobutton."""

    def __init__(
        self,
        parent,
        text: str,
        variable: Optional[tk.Variable] = None,
        value=None,
        **kwargs
    ):
        # Set default classic styling
        default_config = {
            "text": text,
            "variable": variable,
            "value": value,
            "bg": ClassicWindowsStyle.COLORS["bg_window"],
            "fg": ClassicWindowsStyle.COLORS["text_normal"],
            "font": ClassicWindowsStyle.FONTS["default"],
            "relief": "flat",
            "borderwidth": 0,
            "highlightthickness": 0,
            "selectcolor": ClassicWindowsStyle.COLORS["bg_window"],
        }

        # Override with any user-specified kwargs
        default_config.update(kwargs)

        super().__init__(parent, **default_config)
