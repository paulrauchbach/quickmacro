"""
Toggle active application audio mute action.
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


class ToggleActiveAppMuteAction(BaseAction):
    """Action to toggle active application audio mute."""

    @property
    def name(self) -> str:
        return "Toggle Active App Audio Mute"

    @property
    def description(self) -> str:
        return "Toggle the audio mute state of the currently active application"

    def execute(self, parameters: Dict[str, Any] = None) -> bool:
        """Execute the toggle active app mute action."""
        try:
            audio_manager = AudioManager()
            audio_manager.toggle_app_mute()
            logger.info("Active app mute toggled")
            return True
        except Exception as e:
            logger.error(f"Error toggling active app mute: {e}")
            return False
