"""
Status tab component for PyQt6.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any, Optional, Callable

from ..components.base import ModernStyle, ModernButton, ModernCard
from ..components.status_card import StatusCard


class StatusTab(QWidget):
    """Status tab for displaying system information and quick actions."""

    # Signals
    refresh_requested = pyqtSignal()
    action_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Status cards
        self.status_cards = {}

        # Callbacks
        self.refresh_callback: Optional[Callable] = None
        self.quick_action_callback: Optional[Callable] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the status tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
        )
        layout.setSpacing(ModernStyle.SPACING["lg"])

        # System status section
        self._create_status_section(layout)

        # Quick actions section removed

        # Stretch to push everything up
        layout.addStretch()

    def _create_status_section(self, parent_layout):
        """Create the system status section."""
        status_group = QGroupBox("System Status")
        status_group.setFont(ModernStyle.FONTS["default"])
        parent_layout.addWidget(status_group)

        layout = QVBoxLayout(status_group)
        layout.setSpacing(ModernStyle.SPACING["md"])

        # Header with refresh button
        header_layout = QHBoxLayout()
        header_layout.addStretch()

        self.refresh_btn = ModernButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Status cards
        cards_layout = QVBoxLayout()
        cards_layout.setSpacing(ModernStyle.SPACING["sm"])

        # Create status cards
        self.status_cards["volume"] = StatusCard(
            title="System Volume", value="--", status="normal"
        )
        cards_layout.addWidget(self.status_cards["volume"])

        self.status_cards["muted"] = StatusCard(
            title="Audio Status", value="--", status="normal"
        )
        cards_layout.addWidget(self.status_cards["muted"])

        self.status_cards["active_window"] = StatusCard(
            title="Active Window", value="--", status="normal"
        )
        cards_layout.addWidget(self.status_cards["active_window"])

        layout.addLayout(cards_layout)

    def _connect_signals(self):
        """Connect internal signals to callbacks."""
        self.refresh_requested.connect(self._on_refresh)
        self.action_requested.connect(self._on_action)

    def _on_refresh(self):
        """Handle refresh signal."""
        if self.refresh_callback:
            self.refresh_callback()

    def _on_action(self, action_name: str):
        """Handle action signal."""
        if self.quick_action_callback:
            self.quick_action_callback(action_name)

    def set_callbacks(
        self,
        refresh_callback: Optional[Callable] = None,
        quick_action_callback: Optional[Callable] = None,
    ):
        """Set callback functions."""
        self.refresh_callback = refresh_callback
        self.quick_action_callback = quick_action_callback

    def update_status(self, status: Dict[str, Any]):
        """Update the status display."""
        if self.status_cards:
            # Volume card
            volume = status.get("system_volume", 0)
            volume_text = f"{volume:.0%}"
            volume_status = "success" if volume > 0 else "warning"
            self.status_cards["volume"].update_status(volume_text, volume_status)

            # Muted card
            muted = status.get("system_muted", False)
            muted_text = "Muted" if muted else "Unmuted"
            muted_status = "warning" if muted else "success"
            self.status_cards["muted"].update_status(muted_text, muted_status)

            # Active window card
            active_window = status.get("active_window", "Unknown")
            if len(active_window) > 50:
                active_window = active_window[:47] + "..."
            self.status_cards["active_window"].update_status(active_window, "info")
