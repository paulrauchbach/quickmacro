"""
Logs tab component for PyQt6.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QTextEdit,
    QPushButton,
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QTextCursor
from typing import Optional, Callable

from ..components.base import ModernStyle, ModernButton


class LogsTab(QWidget):
    """Logs tab for displaying application logs."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # UI components
        self.log_text = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup the logs tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
        )
        layout.setSpacing(ModernStyle.SPACING["lg"])

        # Logs section
        logs_group = QGroupBox("Application Logs")
        logs_group.setFont(ModernStyle.FONTS["default"])
        layout.addWidget(logs_group)

        group_layout = QVBoxLayout(logs_group)
        group_layout.setSpacing(ModernStyle.SPACING["md"])

        # Header with controls
        header_layout = QHBoxLayout()
        header_layout.addStretch()

        self.clear_btn = ModernButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self._clear_log)
        header_layout.addWidget(self.clear_btn)

        self.refresh_btn = ModernButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._refresh_log)
        header_layout.addWidget(self.refresh_btn)

        group_layout.addLayout(header_layout)

        # Log text area
        self._create_log_text(group_layout)

    def _create_log_text(self, parent_layout):
        """Create the log text widget."""
        self.log_text = QTextEdit()
        self.log_text.setFont(ModernStyle.FONTS["monospace"])
        self.log_text.setReadOnly(True)

        # Set minimum height
        self.log_text.setMinimumHeight(300)

        parent_layout.addWidget(self.log_text)

    def _refresh_log(self):
        """Refresh log display."""
        self.add_log_message("Log refreshed")

    def _clear_log(self):
        """Clear the log display."""
        if self.log_text:
            self.log_text.clear()
            self.add_log_message("Log cleared")

    def add_log_message(self, message: str):
        """Add a message to the log display."""
        if self.log_text:
            # Add timestamp
            timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
            formatted_message = f"[{timestamp}] {message}"

            # Add message
            self.log_text.append(formatted_message)

            # Scroll to bottom
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)

            # Limit log size (keep last 1000 lines)
            text = self.log_text.toPlainText()
            lines = text.split("\n")
            if len(lines) > 1000:
                # Keep only the last 1000 lines
                self.log_text.setPlainText("\n".join(lines[-1000:]))

                # Scroll to bottom again
                cursor = self.log_text.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.log_text.setTextCursor(cursor)
