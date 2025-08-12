"""
Shortcut recorder component for PyQt6 - similar to React useShortcutRecorder.
"""

import logging
from typing import List, Optional, Callable, Set, Tuple
import threading
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QFocusEvent

from utils.shortcut_utils import ShortcutConverter

from .base import ModernStyle, ModernButton

try:
    import keyboard  # Global keyboard hook library
except Exception:  # pragma: no cover - safety if not available at runtime
    keyboard = None

logger = logging.getLogger(__name__)


class ShortcutRecorderWidget(QWidget):
    """
    A widget for recording keyboard shortcuts, similar to the React useShortcutRecorder.

    Features:
    - Records key combinations with modifiers
    - Validates shortcuts against excluded keys/shortcuts
    - Provides visual feedback during recording
    - Emits signals when shortcut changes
    """

    # Signals
    shortcut_changed = pyqtSignal(list)  # Emits the new shortcut as a list
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str)  # Emits error message
    # Internal: update current combo from global hook thread
    global_combo_updated = pyqtSignal(list)

    def __init__(
        self,
        parent=None,
        label_text: str = "Enter Shortcut:",
        excluded_keys: Optional[List[str]] = None,
        excluded_shortcuts: Optional[List[List[str]]] = None,
        excluded_mod_keys: Optional[List[str]] = None,
        max_mod_keys: int = 3,
        min_mod_keys: int = 1,
        on_change: Optional[Callable] = None,
    ):
        super().__init__(parent)

        # Configuration
        self.label_text = label_text
        self.excluded_keys = set(excluded_keys or [])
        self.excluded_shortcuts = [
            set(shortcut) for shortcut in (excluded_shortcuts or [])
        ]
        self.excluded_mod_keys = set(excluded_mod_keys or [])
        self.max_mod_keys = max_mod_keys
        self.min_mod_keys = min_mod_keys
        self.on_change_callback = on_change

        # State
        self.is_recording = False
        self.current_shortcut: List[str] = []
        self.saved_shortcut: List[str] = []
        self.current_error: Optional[str] = None
        self.pressed_keys: Set[int] = set()

        # Only support multiple-key chord recording

        # Global hook state
        self._press_hook = None
        self._release_hook = None
        self._pressed_keyboard_names: Set[str] = set()

        # Timer to detect when user finishes recording
        self.finish_timer = QTimer()
        self.finish_timer.setSingleShot(True)
        self.finish_timer.timeout.connect(self._finish_recording)

        # Key mappings
        self._init_key_mappings()

        # UI setup
        self._setup_ui()
        self._connect_signals()
        self.global_combo_updated.connect(self._on_global_combo_updated)

    def _init_key_mappings(self):
        """Initialize key code to string mappings."""
        # Modifier keys
        self.modifier_keys = {
            Qt.Key.Key_Control: "Ctrl",
            Qt.Key.Key_Shift: "Shift",
            Qt.Key.Key_Alt: "Alt",
            Qt.Key.Key_Meta: "Meta",  # Windows key
        }

        # Common keys
        self.key_names = {
            Qt.Key.Key_Space: "Space",
            Qt.Key.Key_Tab: "Tab",
            Qt.Key.Key_Return: "Enter",
            Qt.Key.Key_Enter: "Enter",
            Qt.Key.Key_Escape: "Escape",
            Qt.Key.Key_Backspace: "Backspace",
            Qt.Key.Key_Delete: "Delete",
            Qt.Key.Key_Home: "Home",
            Qt.Key.Key_End: "End",
            Qt.Key.Key_PageUp: "PageUp",
            Qt.Key.Key_PageDown: "PageDown",
            Qt.Key.Key_Up: "ArrowUp",
            Qt.Key.Key_Down: "ArrowDown",
            Qt.Key.Key_Left: "ArrowLeft",
            Qt.Key.Key_Right: "ArrowRight",
            Qt.Key.Key_Insert: "Insert",
            Qt.Key.Key_Pause: "Pause",
            Qt.Key.Key_Print: "PrintScreen",
            Qt.Key.Key_ScrollLock: "ScrollLock",
            Qt.Key.Key_CapsLock: "CapsLock",
            Qt.Key.Key_NumLock: "NumLock",
        }

        # Function keys
        for i in range(1, 25):
            self.key_names[getattr(Qt.Key, f"Key_F{i}")] = f"F{i}"

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(ModernStyle.SPACING["sm"])

        # Label
        if self.label_text:
            self.label = QLabel(self.label_text)
            self.label.setFont(ModernStyle.FONTS["default"])
            layout.addWidget(self.label)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setReadOnly(True)
        self.input_field.setPlaceholderText("Click to Record Shortcut...")
        self.input_field.setFont(ModernStyle.FONTS["default"])
        self.input_field.setMinimumHeight(36)

        # Input field with reset button in horizontal layout
        input_layout = QHBoxLayout()
        input_layout.setSpacing(ModernStyle.SPACING["sm"])
        input_layout.addWidget(self.input_field)

        # Reset button next to input
        self.reset_button = ModernButton("Reset")
        self.reset_button.clicked.connect(self.clear_recording)
        self.reset_button.setFixedWidth(80)  # Keep button compact
        self.reset_button.setEnabled(False)  # Initially disabled
        input_layout.addWidget(self.reset_button)

        layout.addLayout(input_layout)

        # Error display
        self.error_label = QLabel()
        self.error_label.setProperty("labelStyle", "muted")
        self.error_label.setStyleSheet(f"color: {ModernStyle.COLORS['error']};")
        self.error_label.hide()
        layout.addWidget(self.error_label)

    def _connect_signals(self):
        """Connect internal signals."""
        self.input_field.mousePressEvent = self._on_input_click
        # Remove auto-start on focus - only start on click
        # self.input_field.focusInEvent = self._on_input_focus
        self.input_field.focusOutEvent = self._on_input_blur

        # Connect external signals
        self.shortcut_changed.connect(self._on_shortcut_changed)

        # No mode/tap controls in multiple-only recorder

    def _on_input_click(self, event):
        """Handle input field click."""
        self.start_recording()

    def _on_input_focus(self, event: QFocusEvent):
        """Handle input field focus."""
        self.start_recording()

    def _on_input_blur(self, event: QFocusEvent):
        """Handle input field blur."""
        self.stop_recording()

    # Removed single/tap-related handlers

    def _on_shortcut_changed(self, shortcut: List[str]):
        """Handle shortcut change signal."""
        if self.on_change_callback:
            self.on_change_callback(shortcut)

    def start_recording(self):
        """Start recording a shortcut."""
        if self.is_recording:
            return

        self.is_recording = True
        self.current_shortcut = []
        self.pressed_keys = set()
        self.current_error = None

        self.input_field.setPlaceholderText("Key Recording Started...")
        self.input_field.setFocus()  # Need focus for key events
        self._clear_error()

        # Install event filter to capture key events (local, when available)
        self.input_field.installEventFilter(self)

        # Use only local Qt key events for composing the combination

        self.recording_started.emit()
        logger.debug("Shortcut recording started")

    def stop_recording(self):
        """Stop recording a shortcut."""
        if not self.is_recording:
            return

        self.is_recording = False
        self.finish_timer.stop()

        # Remove event filter
        self.input_field.removeEventFilter(self)

        # No global keyboard hook used

        # Validate and save the shortcut
        validation_error = self._validate_shortcut(self.current_shortcut)
        if self.current_shortcut and validation_error is None:
            self.saved_shortcut = self.current_shortcut.copy()
            self.shortcut_changed.emit(self.saved_shortcut)
        elif self.current_shortcut and validation_error:
            # Show error but still display what was recorded
            self._show_error(validation_error)

        self.input_field.setPlaceholderText("Click to Record Shortcut...")
        self._update_input_display()
        self._update_reset_button_state()

        self.recording_stopped.emit()
        logger.debug("Shortcut recording stopped")

    def clear_recording(self):
        """Clear the current recording and saved shortcut."""
        self.current_shortcut = []
        self.saved_shortcut = []
        self.pressed_keys = set()
        self._clear_error()

        if self.is_recording:
            self.stop_recording()
        else:
            self._update_input_display()
            self._update_reset_button_state()

        self.shortcut_changed.emit([])
        logger.debug("Shortcut recording cleared")

    def _finish_recording(self):
        """Finish recording after a short delay."""
        if self.is_recording:
            self.stop_recording()

    def eventFilter(self, obj, event):
        """Filter key events during recording."""
        if obj == self.input_field and self.is_recording:
            if event.type() == event.Type.KeyPress:
                self._handle_key_press(event)
                return True
            elif event.type() == event.Type.KeyRelease:
                self._handle_key_release(event)
                return True

        return super().eventFilter(obj, event)

    def _handle_key_press(self, event: QKeyEvent):
        """Handle key press during recording."""
        key_code = event.key()

        # Ignore already pressed keys
        if key_code in self.pressed_keys:
            return

        self.pressed_keys.add(key_code)

        # Convert key to string
        key_str = self._key_to_string(key_code, event.text())

        if key_str:
            # Add to current shortcut if not already present
            if key_str not in self.current_shortcut:
                self.current_shortcut.append(key_str)
                self._update_input_display()

                # Validate as we build
                error = self._validate_shortcut(self.current_shortcut, partial=True)
                if error:
                    self._show_error(error)
                else:
                    self._clear_error()

        # Reset finish timer
        self.finish_timer.stop()
        self.finish_timer.start(500)  # 500ms delay

    def _handle_key_release(self, event: QKeyEvent):
        """Handle key release during recording."""
        key_code = event.key()
        self.pressed_keys.discard(key_code)

    def _key_to_string(self, key_code: int, text: str) -> Optional[str]:
        """Convert Qt key code to string representation."""
        # Check modifier keys first
        if key_code in self.modifier_keys:
            return self.modifier_keys[key_code]

        # Check named keys
        if key_code in self.key_names:
            return self.key_names[key_code]

        # Handle letter keys directly by key code (more reliable)
        if Qt.Key.Key_A <= key_code <= Qt.Key.Key_Z:
            return chr(key_code)  # This gives us A-Z directly

        # Handle number keys by key code
        if Qt.Key.Key_0 <= key_code <= Qt.Key.Key_9:
            return chr(key_code)  # This gives us 0-9 directly

        # Handle special keys by key code
        special_keys = {
            Qt.Key.Key_Minus: "-",
            Qt.Key.Key_Equal: "=",
            Qt.Key.Key_BracketLeft: "[",
            Qt.Key.Key_BracketRight: "]",
            Qt.Key.Key_Backslash: "\\",
            Qt.Key.Key_Semicolon: ";",
            Qt.Key.Key_Apostrophe: "'",
            Qt.Key.Key_Comma: ",",
            Qt.Key.Key_Period: ".",
            Qt.Key.Key_Slash: "/",
            Qt.Key.Key_Grave: "`",
        }

        if key_code in special_keys:
            return special_keys[key_code]

        # Fallback to text if it's a single printable character
        if text and text.isprintable() and len(text) == 1:
            if text.isalpha():
                return text.upper()
            elif text.isdigit() or text in "!@#$%^&*()_+-=[]{}|;':\",./<>?`~":
                return text

        return None

    # ===== Global keyboard hook support =====
    def _start_global_hook(self):
        """Start global keyboard hooks using the keyboard library (if available)."""
        if keyboard is None:
            logger.warning("keyboard library not available; global capture disabled")
            return
        try:
            # Clear any previous state
            self._pressed_keyboard_names.clear()
            # Register press and release hooks
            self._press_hook = keyboard.on_press(
                self._on_keyboard_press, suppress=False
            )
            self._release_hook = keyboard.on_release(
                self._on_keyboard_release, suppress=False
            )
            logger.debug("Global keyboard hooks started for recording")
        except Exception as e:
            logger.error(f"Failed to start global keyboard hooks: {e}")

    def _stop_global_hook(self):
        """Stop global keyboard hooks if running."""
        if keyboard is None:
            return
        try:
            if self._press_hook is not None:
                keyboard.unhook(self._press_hook)
                self._press_hook = None
            else:
                # Fallback by callback reference
                try:
                    keyboard.unhook(self._on_keyboard_press)
                except Exception:
                    pass

            if self._release_hook is not None:
                keyboard.unhook(self._release_hook)
                self._release_hook = None
            else:
                try:
                    keyboard.unhook(self._on_keyboard_release)
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Failed to stop global keyboard hooks: {e}")

    def _on_keyboard_press(self, event):
        if not self.is_recording:
            return
        name = self._normalize_keyboard_name(getattr(event, "name", ""))
        if not name:
            return
        if name not in self._pressed_keyboard_names:
            self._pressed_keyboard_names.add(name)
            self._emit_combo_update_from_pressed()

        # Reset finish timer on any activity
        self.finish_timer.stop()
        self.finish_timer.start(500)

    def _on_keyboard_release(self, event):
        if not self.is_recording:
            return
        name = self._normalize_keyboard_name(getattr(event, "name", ""))
        if not name:
            return
        if name in self._pressed_keyboard_names:
            self._pressed_keyboard_names.discard(name)
            self._emit_combo_update_from_pressed()

        # Reset finish timer to allow graceful finish after release
        self.finish_timer.stop()
        self.finish_timer.start(500)

    def _emit_combo_update_from_pressed(self):
        """Compose a keyboard-format combo from pressed names and emit to UI thread."""
        if not self._pressed_keyboard_names:
            # Nothing pressed; clear current shortcut for live view
            self.global_combo_updated.emit([])
            return

        try:
            mod_order = ["ctrl", "alt", "shift", "windows"]
            modifiers = [m for m in mod_order if m in self._pressed_keyboard_names]
            regulars = [
                k for k in sorted(self._pressed_keyboard_names) if k not in mod_order
            ]
            keyboard_combo = "+".join(modifiers + regulars)
            qt_list = ShortcutConverter.keyboard_to_qt(keyboard_combo) or []
            self.global_combo_updated.emit(qt_list)
        except Exception as e:
            logger.error(f"Error composing global combo: {e}")

    def _normalize_keyboard_name(self, name: str) -> Optional[str]:
        if not name:
            return None
        n = name.strip().lower()
        # Normalize left/right variants and common aliases
        alias_map = {
            "left ctrl": "ctrl",
            "right ctrl": "ctrl",
            "ctrl": "ctrl",
            "left shift": "shift",
            "right shift": "shift",
            "shift": "shift",
            "left alt": "alt",
            "right alt": "alt",
            "alt gr": "alt",
            "alt": "alt",
            "left windows": "windows",
            "right windows": "windows",
            "windows": "windows",
            "win": "windows",
            "return": "enter",
        }
        if n in alias_map:
            return alias_map[n]
        # Single characters (letters, digits, symbols)
        if len(n) == 1 and n.isprintable():
            return n
        # Keep common special keys as-is (keyboard lib normalized names)
        return n

    def _on_global_combo_updated(self, qt_list: List[str]):
        """Update current shortcut from global hook (executed on UI thread)."""
        if not self.is_recording:
            return
        # Update current shortcut live for display and validation
        self.current_shortcut = qt_list.copy()
        # Validate as we build
        error = self._validate_shortcut(self.current_shortcut, partial=True)
        if error:
            self._show_error(error)
        else:
            self._clear_error()
        self._update_input_display()

    def _validate_shortcut(
        self, shortcut: List[str], partial: bool = False
    ) -> Optional[str]:
        """
        Validate a shortcut against the configured rules.
        Returns error message if invalid, None if valid.
        """
        if not shortcut:
            return None if partial else "Empty shortcut"

        # Check excluded keys
        for key in shortcut:
            if key in self.excluded_keys:
                return f"Key '{key}' is not allowed"

        # Count modifiers
        modifiers = [key for key in shortcut if key in self.modifier_keys.values()]
        regular_keys = [
            key for key in shortcut if key not in self.modifier_keys.values()
        ]

        # Check excluded modifier keys
        for mod in modifiers:
            if mod in self.excluded_mod_keys:
                return f"Modifier '{mod}' is not allowed"

        if not partial:
            # Multiple mode rules
            if len(modifiers) < self.min_mod_keys:
                return f"At least {self.min_mod_keys} modifier key(s) required"
            if len(modifiers) > self.max_mod_keys:
                return f"Maximum {self.max_mod_keys} modifier key(s) allowed"

            # Must have at least one regular key
            if not regular_keys:
                return "At least one non-modifier key required"

        # Check excluded shortcuts
        shortcut_set = set(shortcut)
        for excluded_set in self.excluded_shortcuts:
            if shortcut_set == excluded_set:
                return "This shortcut combination is not allowed"

        return None

    def _update_input_display(self):
        """Update the input field display."""
        if self.is_recording and self.current_shortcut:
            # Sort: modifiers first, then regular keys
            modifiers = [
                key
                for key in self.current_shortcut
                if key in self.modifier_keys.values()
            ]
            regular_keys = [
                key
                for key in self.current_shortcut
                if key not in self.modifier_keys.values()
            ]
            # Sort modifiers in preferred order
            modifier_order = ["Ctrl", "Alt", "Shift", "Meta"]
            sorted_modifiers = []
            for mod in modifier_order:
                if mod in modifiers:
                    sorted_modifiers.append(mod)

            sorted_shortcut = sorted_modifiers + regular_keys
            self.input_field.setText(" + ".join(sorted_shortcut))
        elif not self.is_recording and self.saved_shortcut:
            # Sort saved shortcut for display
            modifiers = [
                key for key in self.saved_shortcut if key in self.modifier_keys.values()
            ]
            regular_keys = [
                key
                for key in self.saved_shortcut
                if key not in self.modifier_keys.values()
            ]
            # Sort modifiers in preferred order
            modifier_order = ["Ctrl", "Alt", "Shift", "Meta"]
            sorted_modifiers = []
            for mod in modifier_order:
                if mod in modifiers:
                    sorted_modifiers.append(mod)

            sorted_shortcut = sorted_modifiers + regular_keys
            self.input_field.setText(" + ".join(sorted_shortcut))
        elif not self.is_recording and self.current_shortcut:
            # Show current shortcut even if not saved (for immediate feedback)
            modifiers = [
                key
                for key in self.current_shortcut
                if key in self.modifier_keys.values()
            ]
            regular_keys = [
                key
                for key in self.current_shortcut
                if key not in self.modifier_keys.values()
            ]
            modifier_order = ["Ctrl", "Alt", "Shift", "Meta"]
            sorted_modifiers = []
            for mod in modifier_order:
                if mod in modifiers:
                    sorted_modifiers.append(mod)

            sorted_shortcut = sorted_modifiers + regular_keys
            self.input_field.setText(" + ".join(sorted_shortcut))
        else:
            self.input_field.setText("")

    def _update_reset_button_state(self):
        """Update the reset button enabled state based on whether there's a saved shortcut."""
        has_shortcut = bool(self.saved_shortcut)
        self.reset_button.setEnabled(has_shortcut)

    def _show_error(self, message: str):
        """Show an error message."""
        self.current_error = message
        self.error_label.setText(message)
        self.error_label.show()
        self.error_occurred.emit(message)

    def _clear_error(self):
        """Clear the error message."""
        self.current_error = None
        self.error_label.hide()

    # Public API methods
    def get_shortcut(self) -> List[str]:
        """Get the current saved shortcut."""
        return self.saved_shortcut.copy()

    def get_current_shortcut(self) -> List[str]:
        """Get the shortcut being recorded."""
        return self.current_shortcut.copy()

    def set_shortcut(self, shortcut: List[str]):
        """Set the shortcut programmatically."""
        if self._validate_shortcut(shortcut):
            self.saved_shortcut = shortcut.copy()
            self._update_input_display()
            self._update_reset_button_state()
            self.shortcut_changed.emit(self.saved_shortcut)

    # Removed mode/tap APIs for multiple-only behavior

    def get_error(self) -> Optional[str]:
        """Get the current error message."""
        return self.current_error

    def is_recording_active(self) -> bool:
        """Check if recording is active."""
        return self.is_recording


class ShortcutRecorderCard(QFrame):
    """A card wrapper for the shortcut recorder with modern styling."""

    # Forward signals
    shortcut_changed = pyqtSignal(list)
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(
        self, title: str = "Shortcut Recorder", parent=None, **recorder_kwargs
    ):
        super().__init__(parent)

        # Set frame style for modern card appearance
        self.setProperty("frameStyle", "panel")

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            ModernStyle.SPACING["md"],
            ModernStyle.SPACING["md"],
            ModernStyle.SPACING["md"],
            ModernStyle.SPACING["md"],
        )
        layout.setSpacing(ModernStyle.SPACING["sm"])

        # Title
        if title:
            title_label = QLabel(title)
            title_label.setFont(ModernStyle.FONTS["title"])
            layout.addWidget(title_label)

        # Shortcut recorder
        self.recorder = ShortcutRecorderWidget(parent=self, **recorder_kwargs)
        layout.addWidget(self.recorder)

        # Forward signals
        self.recorder.shortcut_changed.connect(self.shortcut_changed.emit)
        self.recorder.recording_started.connect(self.recording_started.emit)
        self.recorder.recording_stopped.connect(self.recording_stopped.emit)
        self.recorder.error_occurred.connect(self.error_occurred.emit)

    def get_recorder(self) -> ShortcutRecorderWidget:
        """Get the underlying recorder widget."""
        return self.recorder
