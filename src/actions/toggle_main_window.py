"""
Toggle main window visibility action.
This action is handled specially in the main application.
"""

import logging
from typing import Dict, Any

try:
    from .base_action import BaseAction
except ImportError:
    # Fallback for when running as standalone
    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from actions.base_action import BaseAction

logger = logging.getLogger(__name__)


class ToggleMainWindowAction(BaseAction):
    """Action to toggle main window visibility."""

    @property
    def name(self) -> str:
        return "Toggle Main Window"

    @property
    def description(self) -> str:
        return "Show/hide the QuickMacro main window"

    def execute(self, parameters: Dict[str, Any] = None) -> bool:
        """Execute the toggle main window action."""
        # This action is handled specially by the main application
        # before it reaches the action manager, so this should not be called
        logger.warning("toggle_main_window action should be handled by main app")
        return False
