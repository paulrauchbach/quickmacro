"""
Lock screen action.
"""

import logging
from typing import Dict, Any

try:
    from utils.system_utils import SystemManager
    from .base_action import BaseAction
except ImportError:
    # Fallback for when running as standalone
    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from utils.system_utils import SystemManager
    from actions.base_action import BaseAction

logger = logging.getLogger(__name__)


class LockScreenAction(BaseAction):
    """Action to lock the screen."""

    @property
    def name(self) -> str:
        return "Lock Screen"

    @property
    def description(self) -> str:
        return "Lock the Windows screen"

    def execute(self, parameters: Dict[str, Any] = None) -> bool:
        """Execute the lock screen action."""
        try:
            system_manager = SystemManager()
            system_manager.lock_screen()
            logger.info("Screen locked")
            return True
        except Exception as e:
            logger.error(f"Error locking screen: {e}")
            return False
