"""
Hotkey management component with interactive editing capabilities.
"""

import logging
from typing import Dict, List, Optional, Callable
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QComboBox,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal

from .base import ModernStyle, ModernButton, ModernCard
from .shortcut_recorder import ShortcutRecorderWidget

# Import utilities with fallback for different execution contexts
try:
    from ...utils.shortcut_utils import qt_to_keyboard, keyboard_to_qt, format_shortcut
except ImportError:
    # Fallback for when running as main module
    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from utils.shortcut_utils import qt_to_keyboard, keyboard_to_qt, format_shortcut

logger = logging.getLogger(__name__)


class HotkeyEntryCard(ModernCard):
    """A card representing a single hotkey entry with edit/delete capabilities."""

    # Signals
    hotkey_changed = pyqtSignal(str, str, str)  # old_hotkey, new_hotkey, action
    hotkey_deleted = pyqtSignal(str)  # hotkey
    edit_requested = pyqtSignal(str, str)  # hotkey, action

    def __init__(self, hotkey: str, action: str, parent=None):
        super().__init__("", parent)

        self.hotkey = hotkey
        self.action = action

        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI for the hotkey entry."""
        # Main layout (horizontal)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(ModernStyle.SPACING["md"])

        # Hotkey display
        hotkey_layout = QVBoxLayout()
        hotkey_layout.setSpacing(ModernStyle.SPACING["xs"])

        # Convert keyboard format to display format
        qt_shortcut = keyboard_to_qt(self.hotkey)
        display_shortcut = format_shortcut(qt_shortcut) if qt_shortcut else self.hotkey

        self.hotkey_label = QLabel(display_shortcut)
        self.hotkey_label.setFont(ModernStyle.FONTS["large"])
        self.hotkey_label.setStyleSheet(
            f"color: {ModernStyle.COLORS['text_accent']}; font-weight: 500;"
        )
        hotkey_layout.addWidget(self.hotkey_label)

        hotkey_sublabel = QLabel("Hotkey")
        hotkey_sublabel.setProperty("labelStyle", "muted")
        hotkey_sublabel.setFont(ModernStyle.FONTS["small"])
        hotkey_layout.addWidget(hotkey_sublabel)

        main_layout.addLayout(hotkey_layout)

        # Action
        info_layout = QVBoxLayout()
        info_layout.setSpacing(ModernStyle.SPACING["xs"])

        self.action_label = QLabel(self.action.replace("_", " ").title())
        self.action_label.setFont(ModernStyle.FONTS["default"])
        info_layout.addWidget(self.action_label)

        main_layout.addLayout(info_layout)
        main_layout.addStretch()

        # Action buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(ModernStyle.SPACING["xs"])

        self.edit_btn = ModernButton("✏️ Edit")
        self.edit_btn.setMaximumWidth(80)
        self.edit_btn.clicked.connect(self._on_edit)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = ModernButton("🗑️ Delete")
        self.delete_btn.setMaximumWidth(80)
        self.delete_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ModernStyle.COLORS['error']};
                color: white;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #b71c1c;
            }}
        """
        )
        self.delete_btn.clicked.connect(self._on_delete)
        button_layout.addWidget(self.delete_btn)

        main_layout.addLayout(button_layout)

        self.add_layout(main_layout)

    def _on_edit(self):
        """Handle edit button click."""
        self.edit_requested.emit(self.hotkey, self.action)

    def _on_delete(self):
        """Handle delete button click."""
        reply = QMessageBox.question(
            self,
            "Delete Hotkey",
            f"Are you sure you want to delete the hotkey '{self.hotkey}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.hotkey_deleted.emit(self.hotkey)

    def update_hotkey(self, new_hotkey: str):
        """Update the hotkey display."""
        self.hotkey = new_hotkey
        qt_shortcut = keyboard_to_qt(new_hotkey)
        display_shortcut = format_shortcut(qt_shortcut) if qt_shortcut else new_hotkey
        self.hotkey_label.setText(display_shortcut)


class HotkeyEditDialog(QDialog):
    """Dialog for editing or creating hotkeys."""

    def __init__(
        self,
        hotkey: str = "",
        action: str = "",
        available_actions: List[str] = None,
        action_manager=None,  # Action manager reference (optional)
        parent=None,
    ):
        super().__init__(parent)

        self.hotkey = hotkey
        self.action = action
        self.available_actions = available_actions or []
        self.action_manager = action_manager
        # Parameters removed: keep references minimal

        self.setWindowTitle("Edit Hotkey" if hotkey else "Add New Hotkey")
        self.setMinimumSize(420, 380)
        self.setModal(True)

        # Apply modern styling
        self.setStyleSheet(ModernStyle.get_stylesheet())

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING["lg"])

        # Title
        title = QLabel("Edit Hotkey" if self.hotkey else "Add New Hotkey")
        title.setFont(ModernStyle.FONTS["title"])
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Form layout
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(ModernStyle.SPACING["md"])

        # Shortcut recorder (multiple-keys chord only)
        self.shortcut_recorder = ShortcutRecorderWidget(
            label_text="Hotkey Combination:",
            min_mod_keys=0,  # Allow shortcuts without modifiers if desired
            max_mod_keys=3,
            on_change=self._on_shortcut_change,
        )

        # Set existing shortcut if editing
        if self.hotkey:
            qt_shortcut = keyboard_to_qt(self.hotkey)
            if qt_shortcut:
                self.shortcut_recorder.set_shortcut(qt_shortcut)

        form_layout.addRow("Hotkey:", self.shortcut_recorder)

        # Action selection with user-friendly names
        self.action_combo = QComboBox()

        # Add actions - self.available_actions now contains action metadata
        for action_data in self.available_actions:
            if isinstance(action_data, dict):
                # New format: action data with name and id
                action_id = action_data.get("id", "")
                display_name = action_data.get("name", action_id)
                self.action_combo.addItem(display_name, action_id)
            else:
                # Fallback for old format (just action_id strings)
                action_id = action_data
                self.action_combo.addItem(action_id, action_id)

        # Set current action if editing
        if self.action:
            for i in range(self.action_combo.count()):
                if self.action_combo.itemData(i) == self.action:
                    self.action_combo.setCurrentIndex(i)
                    break

        form_layout.addRow("Action:", self.action_combo)

        # Description removed

        layout.addWidget(form_widget)

        # Parameters removed

        # Validation status
        self.status_label = QLabel()
        self.status_label.setProperty("labelStyle", "secondary")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)

        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Save Hotkey")
        self.ok_button.setEnabled(False)  # Disabled until valid shortcut

        layout.addWidget(button_box)

        # Connect signals
        self.shortcut_recorder.shortcut_changed.connect(self._validate_form)
        self.shortcut_recorder.error_occurred.connect(self._on_recorder_error)

        # Initial validation
        self._validate_form()

    def _on_shortcut_change(self, shortcut: List[str]):
        """Handle shortcut change from recorder."""
        if shortcut:
            keyboard_format = qt_to_keyboard(shortcut)
            self.status_label.setText(f"Keyboard format: {keyboard_format}")
        else:
            self.status_label.setText("")

    def _validate_form(self):
        """Validate the form and enable/disable OK button."""
        shortcut = self.shortcut_recorder.get_shortcut()
        action = self.action_combo.currentData()  # Use action ID, not display text

        valid = bool(shortcut and action)
        error_message = ""

        if not shortcut:
            error_message = "Please record a hotkey combination"
            valid = False
        elif not action:
            error_message = "Please select an action"
            valid = False
        else:
            # No parameters to validate
            pass

        self.ok_button.setEnabled(valid)

        if error_message:
            self.status_label.setText(f"❌ {error_message}")
            self.status_label.setStyleSheet(f"color: {ModernStyle.COLORS['error']};")
        else:
            keyboard_format = qt_to_keyboard(shortcut)
            action_name = self.action_combo.currentText()
            self.status_label.setText(
                f"✅ Ready to save: {keyboard_format} → {action_name}"
            )
            self.status_label.setStyleSheet("")

    def _on_recorder_error(self, error: str):
        """Handle recorder errors."""
        self.status_label.setText(f"Error: {error}")
        self.status_label.setStyleSheet(f"color: {ModernStyle.COLORS['error']};")

    def _on_action_changed(self):
        """Handle action selection change."""
        self._validate_form()

    # Parameters UI removed

    # No parameter widgets to clear

    # No parameter widget signals

    # No parameter values to load

    def _on_accept(self):
        """Handle OK button click."""
        shortcut = self.shortcut_recorder.get_shortcut()
        action = self.action_combo.currentData()  # Get action ID, not display text

        if shortcut and action:
            self.accept()
        else:
            QMessageBox.warning(
                self, "Invalid Input", "Please fill in all required fields."
            )

    def get_result(self):
        """Get the dialog result."""
        shortcut = self.shortcut_recorder.get_shortcut()
        if not shortcut:
            return None, None

        keyboard_format = qt_to_keyboard(shortcut)
        action = self.action_combo.currentData()  # Get action ID, not display text
        return keyboard_format, action


class HotkeyManagerWidget(QWidget):
    """Main hotkey management widget with full CRUD capabilities."""

    # Signals
    hotkey_added = pyqtSignal(str, str)  # hotkey, action
    hotkey_modified = pyqtSignal(str, str, str)  # old_hotkey, new_hotkey, action
    hotkey_removed = pyqtSignal(str)  # hotkey
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.hotkey_cards = {}  # hotkey -> HotkeyEntryCard
        # Available actions will be set by the main application
        self.available_actions = []
        self.action_manager = None  # Will be set by main application

        # Callbacks
        self.refresh_callback: Optional[Callable] = None

        self._setup_ui()

    def set_action_manager(self, action_manager):
        """Set the action manager for parameter handling."""
        self.action_manager = action_manager

    def _setup_ui(self):
        """Setup the main UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
            ModernStyle.SPACING["lg"],
        )
        layout.setSpacing(ModernStyle.SPACING["lg"])

        # Header section
        header_layout = QHBoxLayout()

        title = QLabel("Hotkey Configuration")
        title.setFont(ModernStyle.FONTS["title"])
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Action buttons
        self.add_btn = ModernButton("➕ Add Hotkey", style="primary")
        self.add_btn.clicked.connect(self._on_add_hotkey)
        header_layout.addWidget(self.add_btn)

        self.refresh_btn = ModernButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Info text
        info_text = QLabel(
            "Manage your application hotkeys. Click 'Add Hotkey' to create new shortcuts, "
            "or edit existing ones by clicking the edit button on each entry."
        )
        info_text.setProperty("labelStyle", "secondary")
        info_text.setWordWrap(True)
        layout.addWidget(info_text)

        # Scrollable area for hotkey cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # Remove frame
        scroll_area.setStyleSheet(
            f"QScrollArea {{ background-color: {ModernStyle.COLORS['bg_primary']}; }}"
        )

        # Container widget for cards
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet(
            f"QWidget {{ background-color: {ModernStyle.COLORS['bg_primary']}; }}"
        )
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(ModernStyle.SPACING["md"])
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.addStretch()  # Push cards to top

        scroll_area.setWidget(self.cards_container)
        layout.addWidget(scroll_area)

    def set_available_actions(self, actions: List[str]):
        """Set the list of available actions."""
        self.available_actions = actions

    def set_callbacks(self, refresh_callback: Optional[Callable] = None):
        """Set callback functions."""
        self.refresh_callback = refresh_callback

    def update_hotkeys(self, hotkeys: Dict[str, str]):
        """Update the displayed hotkeys."""
        # Clear existing cards
        for card in self.hotkey_cards.values():
            card.setParent(None)
            card.deleteLater()
        self.hotkey_cards.clear()

        # Create new cards
        for hotkey, action in hotkeys.items():
            self._add_hotkey_card(hotkey, action)

        # Add empty state if no hotkeys
        if not hotkeys:
            self._show_empty_state()

    def _add_hotkey_card(self, hotkey: str, action: str):
        """Add a hotkey card to the display."""
        card = HotkeyEntryCard(hotkey, action)
        card.edit_requested.connect(self._on_edit_hotkey)
        card.hotkey_deleted.connect(self._on_delete_hotkey)

        # Insert before the stretch
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        self.hotkey_cards[hotkey] = card

    def _show_empty_state(self):
        """Show empty state when no hotkeys exist."""
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_label = QLabel("No hotkeys configured")
        empty_label.setFont(ModernStyle.FONTS["large"])
        empty_label.setProperty("labelStyle", "muted")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_label)

        empty_sublabel = QLabel("Click 'Add Hotkey' to create your first shortcut")
        empty_sublabel.setProperty("labelStyle", "secondary")
        empty_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_sublabel)

        self.cards_layout.insertWidget(self.cards_layout.count() - 1, empty_widget)

    def _on_add_hotkey(self):
        """Handle add hotkey button."""
        dialog = HotkeyEditDialog(
            hotkey="",
            action="",
            available_actions=self.available_actions,
            action_manager=self.action_manager,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            hotkey, action = dialog.get_result()
            if hotkey and action:
                self.hotkey_added.emit(hotkey, action)

    def _on_edit_hotkey(self, hotkey: str, action: str):
        """Handle edit hotkey request."""
        dialog = HotkeyEditDialog(
            hotkey=hotkey,
            action=action,
            available_actions=self.available_actions,
            action_manager=self.action_manager,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_hotkey, new_action = dialog.get_result()
            if new_hotkey and new_action:
                self.hotkey_modified.emit(hotkey, new_hotkey, new_action)

    def _on_delete_hotkey(self, hotkey: str):
        """Handle delete hotkey request."""
        self.hotkey_removed.emit(hotkey)

        # Remove the card
        if hotkey in self.hotkey_cards:
            card = self.hotkey_cards[hotkey]
            card.setParent(None)
            card.deleteLater()
            del self.hotkey_cards[hotkey]
