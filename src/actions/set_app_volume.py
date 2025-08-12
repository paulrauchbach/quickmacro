"""
Set volume for specific application action.
"""

import logging
from typing import Dict, Any, List

try:
    from utils.audio_utils import AudioManager
    from .base_action import BaseAction, ActionParameter
except ImportError:
    # Fallback for when running as standalone
    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from utils.audio_utils import AudioManager
    from actions.base_action import BaseAction, ActionParameter

logger = logging.getLogger(__name__)


class SetAppVolumeAction(BaseAction):
    """Action to set volume for a specific application."""

    @property
    def name(self) -> str:
        return "Set App Volume"

    @property
    def description(self) -> str:
        return "Set the volume level for a specific application"

    @property
    def parameters(self) -> List[ActionParameter]:
        return [
            ActionParameter(
                name="app_name",
                type="string",
                label="Application Name",
                description="Name of the application (e.g., chrome.exe, spotify.exe)",
                required=True,
            ),
            ActionParameter(
                name="volume",
                type="number",
                label="Volume Level",
                description="Volume level from 0.0 (silent) to 1.0 (maximum)",
                required=True,
                default_value=0.5,
                min_value=0.0,
                max_value=1.0,
            ),
        ]

    def execute(self, parameters: Dict[str, Any] = None) -> bool:
        """Execute the set app volume action."""
        if parameters is None:
            parameters = {}

        app_name = parameters.get("app_name", "").strip()
        volume = parameters.get("volume", 0.5)

        if not app_name:
            logger.error("App name is required for set app volume action")
            return False

        try:
            audio_manager = AudioManager()
            success = audio_manager.set_app_volume(app_name, volume)

            if success:
                logger.info(f"Set volume for {app_name} to {volume:.1%}")
            else:
                logger.warning(f"Failed to set volume for {app_name}")

            return success

        except Exception as e:
            logger.error(f"Error setting volume for app {app_name}: {e}")
            return False
