"""
Actions package for QuickMacro application.
Each action is implemented as a separate module with an Action class.
"""

import logging
from typing import Dict, Any
import importlib
import pkgutil
from .base_action import BaseAction

logger = logging.getLogger(__name__)


class ActionRegistry:
    """Registry for dynamically loading and managing actions."""

    def __init__(self):
        self.actions: Dict[str, BaseAction] = {}
        self._load_actions()

    def _load_actions(self):
        """Load all action modules from the actions package.

        Uses import-based discovery so it works in both source and PyInstaller builds.
        """
        excluded_modules = {"__init__", "base_action"}

        discovered_any = False
        try:
            for _finder, module_name, _is_pkg in pkgutil.iter_modules(__path__):  # type: ignore[name-defined]
                if module_name in excluded_modules:
                    continue
                full_name = f"{__name__}.{module_name}"
                try:
                    module = importlib.import_module(full_name)
                    self._register_actions_from_module(module_name, module)
                    discovered_any = True
                except Exception as import_error:
                    logger.error(
                        f"Error importing action module '{full_name}': {import_error}"
                    )
        except Exception as discovery_error:
            # Fallback: try eager imports of known modules if discovery fails entirely
            logger.warning(
                f"Action discovery failed: {discovery_error}. Falling back to explicit imports."
            )

        # If nothing discovered (common in PyInstaller onefile), use explicit list
        if not discovered_any and not self.actions:
            for module_name in [
                "lock_screen",
                "mute_app",
                "set_app_volume",
                "toggle_active_app_mute",
                "toggle_main_window",
                "toggle_system_mute",
            ]:
                try:
                    module = importlib.import_module(f"{__name__}.{module_name}")
                    self._register_actions_from_module(module_name, module)
                except Exception as import_error:
                    logger.error(
                        f"Error importing fallback action module '{module_name}': {import_error}"
                    )

    def _register_actions_from_module(self, action_name: str, module: Any) -> None:
        """Find and register a concrete BaseAction subclass from a module."""
        action_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseAction)
                and attr is not BaseAction
            ):
                action_class = attr
                break

        if action_class:
            action_instance = action_class()
            self.actions[action_name] = action_instance
            logger.debug(f"Loaded action: {action_name} ({action_instance.name})")
        else:
            logger.warning(f"Action module {action_name} missing Action class")

    def get_action(self, action_name: str) -> BaseAction:
        """Get an action by name."""
        return self.actions.get(action_name)

    def list_actions(self) -> Dict[str, BaseAction]:
        """Get all available actions."""
        return self.actions.copy()

    def get_action_names(self) -> list:
        """Get list of all available action names."""
        return list(self.actions.keys())

    def execute_action(
        self, action_name: str, parameters: Dict[str, Any] = None
    ) -> bool:
        """Execute an action by name with parameters."""
        action = self.get_action(action_name)
        if action is None:
            logger.error(f"Unknown action: {action_name}")
            return False

        # Validate parameters
        valid, error_msg = action.validate_parameters(parameters)
        if not valid:
            logger.error(f"Parameter validation failed for {action_name}: {error_msg}")
            return False

        # Execute the action
        return action.execute(parameters)

    def reload_actions(self):
        """Reload all actions (useful for development)."""
        self.actions.clear()
        self._load_actions()


# Global action registry instance
action_registry = ActionRegistry()
