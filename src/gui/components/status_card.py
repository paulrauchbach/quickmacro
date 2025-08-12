"""
Modern status card component for PyQt6.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from .base import ModernStyle, StatusIndicator


class StatusCard(QFrame):
    """A modern status card for displaying system information."""

    def __init__(
        self, title: str, value: str = "--", status: str = "normal", parent=None
    ):
        super().__init__(parent)

        self.title = title
        self.value = value
        self.status = status

        # Set frame styling
        self.setProperty("frameStyle", "panel")

        self._setup_ui()

    def _setup_ui(self):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            ModernStyle.SPACING["md"],
            ModernStyle.SPACING["sm"],
            ModernStyle.SPACING["md"],
            ModernStyle.SPACING["sm"],
        )
        layout.setSpacing(ModernStyle.SPACING["xs"])

        # Header with title and status indicator
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setProperty("labelStyle", "secondary")
        self.title_label.setFont(ModernStyle.FONTS["small"])
        header_layout.addWidget(self.title_label)

        # Status indicator
        self.status_indicator = StatusIndicator(self.status)
        header_layout.addWidget(
            self.status_indicator, alignment=Qt.AlignmentFlag.AlignRight
        )

        layout.addLayout(header_layout)

        # Value
        self.value_label = QLabel(self.value)
        self.value_label.setFont(ModernStyle.FONTS["large"])
        layout.addWidget(self.value_label)

    def update_status(self, value: str, status: str = "normal"):
        """Update the card status and value."""
        self.value = value
        self.status = status

        self.value_label.setText(value)
        self.status_indicator.update_status(status)
