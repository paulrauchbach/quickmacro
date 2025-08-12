"""
Demo component showing how to use the ShortcutRecorderWidget.
This can be used as a reference or for testing the shortcut recorder.
"""

import logging
from typing import List
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import pyqtSignal

from .base import ModernStyle, ModernButton
from .shortcut_recorder import ShortcutRecorderCard

# Import utilities with absolute import fallback
try:
    from ...utils.shortcut_utils import (
        qt_to_keyboard,
        keyboard_to_qt,
        format_shortcut,
        validate_shortcut,
    )
except ImportError:
    # Fallback for when running as standalone
    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from utils.shortcut_utils import (
        qt_to_keyboard,
        keyboard_to_qt,
        format_shortcut,
        validate_shortcut,
    )

logger = logging.getLogger(__name__)


class ShortcutRecorderDemo(QWidget):
    """
    Demo widget showing the shortcut recorder in action.
    Similar to the React example provided.
    """

    # Signal emitted when shortcut is confirmed
    shortcut_confirmed = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_shortcut = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the demo UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
        )
        layout.setSpacing(ModernStyle.SPACING["lg"])

        # Title
        title = QLabel("Shortcut Recorder Demo")
        title.setFont(ModernStyle.FONTS["title"])
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "This demo shows the shortcut recorder component in action. "
            "Click in the input field to start recording a keyboard shortcut."
        )
        desc.setProperty("labelStyle", "secondary")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Shortcut recorder with configuration similar to React example
        self.recorder_card = ShortcutRecorderCard(
            title="Enter Shortcut",
            label_text="Shortcut:",
            excluded_keys=["A", "B"],  # KeyA, KeyB equivalent
            excluded_shortcuts=[
                ["Alt", "M"],  # Alt + M
                ["Meta", "["],  # Meta + BracketLeft equivalent
            ],
            excluded_mod_keys=["Ctrl"],  # Control key excluded
            max_mod_keys=3,
            min_mod_keys=1,
            on_change=self._on_shortcut_change,
        )
        layout.addWidget(self.recorder_card)

        # Status display
        self.status_label = QLabel("No shortcut recorded")
        self.status_label.setProperty("labelStyle", "secondary")
        layout.addWidget(self.status_label)

        # Conversion display
        self.conversion_text = QTextEdit()
        self.conversion_text.setMaximumHeight(120)
        self.conversion_text.setPlaceholderText(
            "Shortcut conversion info will appear here..."
        )
        self.conversion_text.setFont(ModernStyle.FONTS["small"])
        layout.addWidget(self.conversion_text)

        # Demo buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(ModernStyle.SPACING["sm"])

        # Set example shortcut
        example_btn = ModernButton("Set Example (Shift+F1)")
        example_btn.clicked.connect(self._set_example_shortcut)
        button_layout.addWidget(example_btn)

        # Clear shortcut
        clear_btn = ModernButton("Clear")
        clear_btn.clicked.connect(self._clear_shortcut)
        button_layout.addWidget(clear_btn)

        # Confirm shortcut
        confirm_btn = ModernButton("Confirm Shortcut", style="primary")
        confirm_btn.clicked.connect(self._confirm_shortcut)
        button_layout.addWidget(confirm_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Connect signals
        self._connect_signals()

    def _connect_signals(self):
        """Connect component signals."""
        recorder = self.recorder_card.get_recorder()
        recorder.shortcut_changed.connect(self._on_shortcut_changed)
        recorder.recording_started.connect(self._on_recording_started)
        recorder.recording_stopped.connect(self._on_recording_stopped)
        recorder.error_occurred.connect(self._on_error_occurred)

    def _on_shortcut_change(self, shortcut: List[str]):
        """Callback function for shortcut changes."""
        logger.info(f"Shortcut changed: {shortcut}")

    def _on_shortcut_changed(self, shortcut: List[str]):
        """Handle shortcut changed signal."""
        self.current_shortcut = shortcut
        if shortcut:
            formatted = format_shortcut(shortcut)
            self.status_label.setText(f"Current shortcut: {formatted}")
            self._update_conversion_display(shortcut)
        else:
            self.status_label.setText("No shortcut recorded")
            self.conversion_text.clear()

    def _on_recording_started(self):
        """Handle recording started signal."""
        self.status_label.setText("Recording shortcut...")
        logger.debug("Recording started")

    def _on_recording_stopped(self):
        """Handle recording stopped signal."""
        logger.debug("Recording stopped")

    def _on_error_occurred(self, error: str):
        """Handle error signal."""
        logger.warning(f"Shortcut recorder error: {error}")

    def _set_example_shortcut(self):
        """Set an example shortcut."""
        example_shortcut = ["Shift", "F1"]
        recorder = self.recorder_card.get_recorder()
        recorder.set_shortcut(example_shortcut)

    def _clear_shortcut(self):
        """Clear the current shortcut."""
        recorder = self.recorder_card.get_recorder()
        recorder.clear_recording()

    def _confirm_shortcut(self):
        """Confirm the current shortcut."""
        if self.current_shortcut:
            self.shortcut_confirmed.emit(self.current_shortcut)
            logger.info(f"Shortcut confirmed: {' + '.join(self.current_shortcut)}")
        else:
            logger.warning("No shortcut to confirm")

    def _update_conversion_display(self, shortcut: List[str]):
        """Update the conversion display with shortcut info."""
        lines = []

        # Original format
        lines.append(f"Qt/Recorder format: {shortcut}")

        # Formatted display
        formatted = format_shortcut(shortcut)
        lines.append(f"Formatted display: {formatted}")

        # Keyboard library format
        keyboard_format = qt_to_keyboard(shortcut)
        if keyboard_format:
            lines.append(f"Keyboard library format: {keyboard_format}")
        else:
            lines.append("Keyboard library format: (conversion failed)")

        # Validation
        validation = validate_shortcut(shortcut)
        lines.append(f"Valid: {validation['valid']}")

        if validation["errors"]:
            lines.append(f"Errors: {', '.join(validation['errors'])}")

        if validation["warnings"]:
            lines.append(f"Warnings: {', '.join(validation['warnings'])}")

        # Test conversion back
        if keyboard_format:
            back_converted = keyboard_to_qt(keyboard_format)
            if back_converted:
                lines.append(f"Round-trip test: {back_converted}")
            else:
                lines.append("Round-trip test: (failed)")

        self.conversion_text.setPlainText("\n".join(lines))

    def get_current_shortcut(self) -> List[str]:
        """Get the current shortcut."""
        return self.current_shortcut.copy()
