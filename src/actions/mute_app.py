"""
Mute specific application action.
This action allows muting/unmuting a specific application by name.
"""

import logging
from typing import Dict, Any, List
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout
from gui.components.base import ModernCard

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


class MuteAppAction(BaseAction):
    """Action to mute/unmute a specific application."""

    @property
    def name(self) -> str:
        return "Mute Specific App"

    @property
    def description(self) -> str:
        return "Mute or unmute a specific application by name"

    @property
    def parameters(self) -> List[ActionParameter]:
        return [
            ActionParameter(
                name="app_name",
                type="string",
                label="Application Name",
                description="Name of the application to mute (e.g., chrome.exe, spotify.exe)",
                required=True,
            ),
            ActionParameter(
                name="action",
                type="choice",
                label="Action",
                description="Whether to mute, unmute, or toggle",
                required=True,
                default_value="toggle",
                choices=["mute", "unmute", "toggle"],
            ),
        ]

    def select_parameters(self) -> QWidget:
        """Create and return a widget with parameter selection UI."""
        # Create main container
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Add a title/description
        title_label = QLabel("Configure Mute App Action")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)

        # Create parameter widgets using the built-in method
        widgets = self.create_parameter_widgets(container)

        # Organize widgets in a form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        for param in self.parameters:
            if param.name in widgets:
                label = QLabel(param.label + ("*" if param.required else ""))
                label.setToolTip(param.description)
                form_layout.addRow(label, widgets[param.name])

        layout.addLayout(form_layout)

        # Store widgets for later value extraction
        container.parameter_widgets = widgets

        return container

    def execute(self, parameters: Dict[str, Any] = None) -> bool:
        """Execute the mute app action."""
        if parameters is None:
            parameters = {}

        app_name = parameters.get("app_name", "").strip()
        action = parameters.get("action", "toggle")

        if not app_name:
            logger.error("App name is required for mute app action")
            return False

        try:
            audio_manager = AudioManager()

            if action == "mute":
                success = audio_manager.mute_app(app_name)
                logger.info(f"Muted app: {app_name}")
            elif action == "unmute":
                success = audio_manager.unmute_app(app_name)
                logger.info(f"Unmuted app: {app_name}")
            else:  # toggle
                success = audio_manager.toggle_app_mute(app_name)
                logger.info(f"Toggled mute for app: {app_name}")

            return success

        except Exception as e:
            logger.error(f"Error controlling mute for app {app_name}: {e}")
            return False
