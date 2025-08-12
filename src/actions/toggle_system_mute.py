"""
Toggle system-wide audio mute action.
"""

import logging
from typing import Dict, Any

try:
    from utils.audio_utils import AudioManager
    from .base_action import BaseAction
except ImportError:
    # Fallback for when running as standalone
    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from utils.audio_utils import AudioManager
    from actions.base_action import BaseAction

logger = logging.getLogger(__name__)


class ToggleSystemMuteAction(BaseAction):
    """Action to toggle system-wide audio mute."""

    @property
    def name(self) -> str:
        return "Toggle System Audio Mute"

    @property
    def description(self) -> str:
        return "Toggle the system-wide audio mute state"

    def execute(self, parameters: Dict[str, Any] = None) -> bool:
        """Execute the toggle system mute action."""
        try:
            audio_manager = AudioManager()
            audio_manager.toggle_system_mute()
            logger.info("System mute toggled")
            return True
        except Exception as e:
            logger.error(f"Error toggling system mute: {e}")
            return False
