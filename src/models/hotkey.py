"""
Hotkey model class for QuickMacro application.
"""

from dataclasses import dataclass, fields, asdict
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class Hotkey:
    """Represents a hotkey configuration with automatic serialization support."""

    hotkey: str
    action: str
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert hotkey to dictionary for config storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hotkey":
        """Create hotkey from dictionary data.

        Extra fields in the input are ignored for backward compatibility.
        """
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)

    def validate(self) -> bool:
        """Validate the hotkey configuration."""
        if not self.hotkey or not self.hotkey.strip():
            logger.warning("Hotkey configuration missing hotkey combination")
            return False

        if not self.action or not self.action.strip():
            logger.warning("Hotkey configuration missing action")
            return False

        return True

    def __str__(self) -> str:
        """String representation of the hotkey."""
        return f"Hotkey('{self.hotkey}' -> '{self.action}'{' (disabled)' if not self.enabled else ''})"

    def __repr__(self) -> str:
        """Detailed representation of the hotkey."""
        return f"Hotkey(hotkey='{self.hotkey}', action='{self.action}', enabled={self.enabled})"
