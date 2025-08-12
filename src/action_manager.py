import logging
from typing import Dict, Any, List

try:
    # Try bundled imports first (for PyInstaller)
    from utils.audio_utils import AudioManager
    from utils.system_utils import SystemManager
    from actions import action_registry
except ImportError:
    # Fallback to relative imports (for development)
    from .utils.audio_utils import AudioManager
    from .utils.system_utils import SystemManager
    from .actions import action_registry

logger = logging.getLogger(__name__)


class ActionManager:
    """Manages execution of actions using the plugin-based action system."""

    def __init__(self):
        self.audio_manager = AudioManager()
        self.system_manager = SystemManager()

    def execute_action(self, action_name: str, parameters: Dict[str, Any] = None):
        """Execute an action by name using the action registry."""
        try:
            return action_registry.execute_action(action_name, parameters)
        except Exception as e:
            logger.error(f"Error executing action {action_name}: {e}")
            return False

    def get_available_actions(self) -> list:
        """Get list of all available action names."""
        return action_registry.get_action_names()

    def get_all_actions(self) -> Dict[str, Any]:
        """Get all available actions with their metadata."""
        actions = {}
        for action_name, action_instance in action_registry.list_actions().items():
            actions[action_name] = {
                "name": action_instance.name,
                "description": action_instance.description,
                "parameters": [
                    {
                        "name": param.name,
                        "type": param.type,
                        "label": param.label,
                        "description": param.description,
                        "required": param.required,
                        "default_value": param.default_value,
                        "choices": param.choices,
                        "min_value": param.min_value,
                        "max_value": param.max_value,
                    }
                    for param in action_instance.parameters
                ],
            }
        return actions

    def get_action_parameters(self, action_name: str) -> List[Dict[str, Any]]:
        """Get parameters for a specific action."""
        action = action_registry.get_action(action_name)
        if action is None:
            return []

        return [
            {
                "name": param.name,
                "type": param.type,
                "label": param.label,
                "description": param.description,
                "required": param.required,
                "default_value": param.default_value,
                "choices": param.choices,
                "min_value": param.min_value,
                "max_value": param.max_value,
            }
            for param in action.parameters
        ]

    def reload_actions(self):
        """Reload all actions (useful for development)."""
        action_registry.reload_actions()

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status for display."""
        try:
            return {
                "system_volume": self.audio_manager.get_system_volume(),
                "system_muted": self.audio_manager.is_system_muted(),
                "active_window": self.system_manager.get_active_window_title(),
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {}
