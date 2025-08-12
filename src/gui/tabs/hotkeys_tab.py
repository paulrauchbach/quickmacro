"""
Hotkeys tab component for PyQt6 with interactive editing capabilities.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from typing import Dict, Optional, Callable, List

from ..components.hotkey_manager import HotkeyManagerWidget


class HotkeysTab(QWidget):
    """Hotkeys tab with full hotkey management capabilities."""

    # Signals
    refresh_requested = pyqtSignal()
    hotkey_added = pyqtSignal(str, str)  # hotkey, action
    hotkey_modified = pyqtSignal(str, str, str)  # old_hotkey, new_hotkey, action
    hotkey_removed = pyqtSignal(str)  # hotkey

    def __init__(self, parent=None):
        super().__init__(parent)

        # Callbacks
        self.refresh_callback: Optional[Callable] = None
        self.add_hotkey_callback: Optional[Callable] = None
        self.modify_hotkey_callback: Optional[Callable] = None
        self.remove_hotkey_callback: Optional[Callable] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the hotkeys tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Use the new hotkey manager widget
        self.hotkey_manager = HotkeyManagerWidget()
        layout.addWidget(self.hotkey_manager)

    def _connect_signals(self):
        """Connect internal signals to callbacks."""
        # Forward signals from the hotkey manager
        self.hotkey_manager.refresh_requested.connect(self._on_refresh)
        self.hotkey_manager.hotkey_added.connect(self._on_hotkey_added)
        self.hotkey_manager.hotkey_modified.connect(self._on_hotkey_modified)
        self.hotkey_manager.hotkey_removed.connect(self._on_hotkey_removed)

    def _on_refresh(self):
        """Handle refresh signal."""
        if self.refresh_callback:
            self.refresh_callback()
        self.refresh_requested.emit()

    def _on_hotkey_added(self, hotkey: str, action: str):
        """Handle hotkey added signal."""
        if self.add_hotkey_callback:
            self.add_hotkey_callback(hotkey, action)
        self.hotkey_added.emit(hotkey, action)

    def _on_hotkey_modified(self, old_hotkey: str, new_hotkey: str, action: str):
        """Handle hotkey modified signal."""
        if self.modify_hotkey_callback:
            self.modify_hotkey_callback(old_hotkey, new_hotkey, action)
        self.hotkey_modified.emit(old_hotkey, new_hotkey, action)

    def _on_hotkey_removed(self, hotkey: str):
        """Handle hotkey removed signal."""
        if self.remove_hotkey_callback:
            self.remove_hotkey_callback(hotkey)
        self.hotkey_removed.emit(hotkey)

    def set_callbacks(
        self,
        refresh_callback: Optional[Callable] = None,
        add_hotkey_callback: Optional[Callable] = None,
        modify_hotkey_callback: Optional[Callable] = None,
        remove_hotkey_callback: Optional[Callable] = None,
    ):
        """Set callback functions."""
        self.refresh_callback = refresh_callback
        self.add_hotkey_callback = add_hotkey_callback
        self.modify_hotkey_callback = modify_hotkey_callback
        self.remove_hotkey_callback = remove_hotkey_callback

    def set_available_actions(self, actions: List[str]):
        """Set the list of available actions for the hotkey manager."""
        self.hotkey_manager.set_available_actions(actions)

    def set_action_manager(self, action_manager):
        """Set the action manager for parameter handling."""
        self.hotkey_manager.set_action_manager(action_manager)

    def update_hotkeys(self, hotkeys: Dict[str, str]):
        """Update the hotkeys display."""
        self.hotkey_manager.update_hotkeys(hotkeys)
