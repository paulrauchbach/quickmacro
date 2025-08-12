"""
Utility functions for working with keyboard shortcuts.
Provides conversion between different shortcut formats.
"""

from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class ShortcutConverter:
    """Converts between different shortcut formats."""

    # Mapping from PyQt/recorder format to keyboard library format
    QT_TO_KEYBOARD_MAP = {
        # Modifiers
        "Ctrl": "ctrl",
        "Shift": "shift",
        "Alt": "alt",
        "Meta": "windows",  # Windows key
        # Special keys
        "Space": "space",
        "Tab": "tab",
        "Enter": "enter",
        "Escape": "esc",
        "Backspace": "backspace",
        "Delete": "delete",
        "Home": "home",
        "End": "end",
        "PageUp": "page up",
        "PageDown": "page down",
        "ArrowUp": "up",
        "ArrowDown": "down",
        "ArrowLeft": "left",
        "ArrowRight": "right",
        "Insert": "insert",
        "Pause": "pause",
        "PrintScreen": "print screen",
        "ScrollLock": "scroll lock",
        "CapsLock": "caps lock",
        "NumLock": "num lock",
    }

    # Reverse mapping for converting back
    KEYBOARD_TO_QT_MAP = {v: k for k, v in QT_TO_KEYBOARD_MAP.items()}

    @classmethod
    def qt_to_keyboard(cls, qt_shortcut: List[str]) -> Optional[str]:
        """
        Convert a Qt/recorder shortcut format to keyboard library format.

        Args:
            qt_shortcut: List of keys like ["Ctrl", "Shift", "A"]

        Returns:
            String in keyboard library format like "ctrl+shift+a" or None if conversion fails
        """
        if not qt_shortcut:
            return None

        try:
            converted_keys = []

            for key in qt_shortcut:
                if key in cls.QT_TO_KEYBOARD_MAP:
                    converted_keys.append(cls.QT_TO_KEYBOARD_MAP[key])
                elif len(key) == 1:
                    # Single character keys (letters, numbers, symbols)
                    converted_keys.append(key.lower())
                elif key.startswith("F") and key[1:].isdigit():
                    # Function keys (F1, F2, etc.)
                    converted_keys.append(key.lower())
                else:
                    logger.warning(f"Unknown key in shortcut conversion: {key}")
                    return None

            return "+".join(converted_keys)

        except Exception as e:
            logger.error(
                f"Error converting Qt shortcut {qt_shortcut} to keyboard format: {e}"
            )
            return None

    @classmethod
    def keyboard_to_qt(cls, keyboard_shortcut: str) -> Optional[List[str]]:
        """
        Convert a keyboard library shortcut format to Qt/recorder format.

        Args:
            keyboard_shortcut: String like "ctrl+shift+a"

        Returns:
            List of keys like ["Ctrl", "Shift", "A"] or None if conversion fails
        """
        if not keyboard_shortcut:
            return None

        try:
            keys = keyboard_shortcut.split("+")
            converted_keys = []

            for key in keys:
                key = key.strip()
                if key in cls.KEYBOARD_TO_QT_MAP:
                    converted_keys.append(cls.KEYBOARD_TO_QT_MAP[key])
                elif len(key) == 1:
                    # Single character keys
                    converted_keys.append(key.upper())
                elif key.lower().startswith("f") and key[1:].isdigit():
                    # Function keys
                    converted_keys.append(key.upper())
                else:
                    # Try to handle other special cases
                    if key.lower() == "windows":
                        converted_keys.append("Meta")
                    else:
                        logger.warning(
                            f"Unknown key in keyboard shortcut conversion: {key}"
                        )
                        return None

            return converted_keys

        except Exception as e:
            logger.error(
                f"Error converting keyboard shortcut {keyboard_shortcut} to Qt format: {e}"
            )
            return None

    @classmethod
    def format_for_display(cls, qt_shortcut: List[str]) -> str:
        """
        Format a Qt shortcut for display purposes.
        Ensures modifiers come first and proper separator.

        Args:
            qt_shortcut: List of keys like ["A", "Ctrl", "Shift"]

        Returns:
            Formatted string like "Ctrl + Shift + A"
        """
        if not qt_shortcut:
            return ""

        # Separate modifiers from regular keys
        modifiers = []
        regular_keys = []

        modifier_order = ["Ctrl", "Alt", "Shift", "Meta"]  # Preferred order

        for key in qt_shortcut:
            if key in modifier_order:
                modifiers.append(key)
            else:
                regular_keys.append(key)

        # Sort modifiers by preferred order
        sorted_modifiers = []
        for mod in modifier_order:
            if mod in modifiers:
                sorted_modifiers.append(mod)

        # Combine and format
        all_keys = sorted_modifiers + regular_keys
        return " + ".join(all_keys)

    @classmethod
    def validate_shortcut(cls, shortcut: List[str]) -> Dict[str, any]:
        """
        Validate a shortcut and return validation info.

        Args:
            shortcut: List of keys to validate

        Returns:
            Dict with validation results: {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'keyboard_format': str or None
            }
        """
        result = {"valid": True, "errors": [], "warnings": [], "keyboard_format": None}

        if not shortcut:
            result["valid"] = False
            result["errors"].append("Empty shortcut")
            return result

        # Check for duplicates
        if len(shortcut) != len(set(shortcut)):
            result["valid"] = False
            result["errors"].append("Duplicate keys in shortcut")

        # Try to convert to keyboard format
        keyboard_format = cls.qt_to_keyboard(shortcut)
        if keyboard_format is None:
            result["valid"] = False
            result["errors"].append("Cannot convert to keyboard library format")
        else:
            result["keyboard_format"] = keyboard_format

        # Check for common issues
        modifiers = [key for key in shortcut if key in ["Ctrl", "Alt", "Shift", "Meta"]]
        regular_keys = [key for key in shortcut if key not in modifiers]

        if not regular_keys:
            result["warnings"].append("Shortcut contains only modifier keys")

        if len(modifiers) == 0:
            result["warnings"].append(
                "Shortcut has no modifier keys (may conflict with normal typing)"
            )

        return result


# Convenience functions
def qt_to_keyboard(qt_shortcut: List[str]) -> Optional[str]:
    """Convenience function for converting Qt shortcut to keyboard format."""
    return ShortcutConverter.qt_to_keyboard(qt_shortcut)


def keyboard_to_qt(keyboard_shortcut: str) -> Optional[List[str]]:
    """Convenience function for converting keyboard shortcut to Qt format."""
    return ShortcutConverter.keyboard_to_qt(keyboard_shortcut)


def format_shortcut(qt_shortcut: List[str]) -> str:
    """Convenience function for formatting shortcut for display."""
    return ShortcutConverter.format_for_display(qt_shortcut)


def validate_shortcut(shortcut: List[str]) -> Dict[str, any]:
    """Convenience function for validating shortcut."""
    return ShortcutConverter.validate_shortcut(shortcut)
