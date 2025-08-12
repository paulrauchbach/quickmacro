"""
Base action class for QuickMacro application.
All actions should inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ActionParameter:
    """Represents a configurable parameter for an action."""

    name: str
    type: str  # 'string', 'number', 'boolean', 'choice', 'app_list'
    label: str
    description: str = ""
    required: bool = True
    default_value: Any = None
    choices: List[str] = field(default_factory=list)  # For 'choice' type
    min_value: Optional[float] = None  # For 'number' type
    max_value: Optional[float] = None  # For 'number' type


class BaseAction(ABC):
    """Base class for all actions."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the action."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this action does."""
        pass

    @property
    def parameters(self) -> List[ActionParameter]:
        """List of configurable parameters for this action."""
        return []

    @abstractmethod
    def execute(self, parameters: Dict[str, Any] = None) -> bool:
        """Execute the action with given parameters."""
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """Validate the provided parameters."""
        if parameters is None:
            parameters = {}

        for param in self.parameters:
            if param.required and param.name not in parameters:
                return False, f"Required parameter '{param.name}' is missing"

            if param.name in parameters:
                value = parameters[param.name]

                # Type validation
                if param.type == "number":
                    if not isinstance(value, (int, float)):
                        return False, f"Parameter '{param.name}' must be a number"
                    if param.min_value is not None and value < param.min_value:
                        return (
                            False,
                            f"Parameter '{param.name}' must be >= {param.min_value}",
                        )
                    if param.max_value is not None and value > param.max_value:
                        return (
                            False,
                            f"Parameter '{param.name}' must be <= {param.max_value}",
                        )

                elif param.type == "boolean":
                    if not isinstance(value, bool):
                        return False, f"Parameter '{param.name}' must be a boolean"

                elif param.type == "choice":
                    if value not in param.choices:
                        return (
                            False,
                            f"Parameter '{param.name}' must be one of: {param.choices}",
                        )

                elif param.type == "string":
                    if not isinstance(value, str):
                        return False, f"Parameter '{param.name}' must be a string"

        return True, ""

    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameter values."""
        defaults = {}
        for param in self.parameters:
            if param.default_value is not None:
                defaults[param.name] = param.default_value
        return defaults

    def create_parameter_widgets(self, parent_widget=None) -> Dict[str, Any]:
        """Create UI widgets for action parameters.

        Returns:
            Dict mapping parameter names to widget objects
        """
        from PyQt6.QtWidgets import (
            QLineEdit,
            QSpinBox,
            QDoubleSpinBox,
            QCheckBox,
            QComboBox,
        )

        widgets = {}

        for param in self.parameters:
            if param.type == "string":
                widget = QLineEdit(parent_widget)
                if param.default_value:
                    widget.setText(str(param.default_value))
                widgets[param.name] = widget

            elif param.type == "number":
                if param.min_value is not None and param.max_value is not None:
                    # Use appropriate spin box based on whether we have decimals
                    if (
                        isinstance(param.default_value, float)
                        or (param.min_value != int(param.min_value))
                        or (param.max_value != int(param.max_value))
                    ):
                        widget = QDoubleSpinBox(parent_widget)
                        widget.setDecimals(2)
                    else:
                        widget = QSpinBox(parent_widget)

                    widget.setMinimum(param.min_value)
                    widget.setMaximum(param.max_value)
                else:
                    widget = QDoubleSpinBox(parent_widget)
                    widget.setDecimals(2)
                    widget.setMinimum(-999999)
                    widget.setMaximum(999999)

                if param.default_value is not None:
                    widget.setValue(param.default_value)
                widgets[param.name] = widget

            elif param.type == "boolean":
                widget = QCheckBox(parent_widget)
                if param.default_value is not None:
                    widget.setChecked(param.default_value)
                widgets[param.name] = widget

            elif param.type == "choice":
                widget = QComboBox(parent_widget)
                for choice in param.choices:
                    widget.addItem(choice)
                if param.default_value and param.default_value in param.choices:
                    widget.setCurrentText(param.default_value)
                widgets[param.name] = widget

        return widgets

    def extract_parameter_values(self, widgets: Dict[str, Any]) -> Dict[str, Any]:
        """Extract values from parameter widgets.

        Args:
            widgets: Dict mapping parameter names to widget objects

        Returns:
            Dict mapping parameter names to their values
        """
        from PyQt6.QtWidgets import (
            QLineEdit,
            QSpinBox,
            QDoubleSpinBox,
            QCheckBox,
            QComboBox,
        )

        values = {}

        for param in self.parameters:
            if param.name not in widgets:
                continue

            widget = widgets[param.name]

            if param.type == "string":
                values[param.name] = widget.text()
            elif param.type == "number":
                values[param.name] = widget.value()
            elif param.type == "boolean":
                values[param.name] = widget.isChecked()
            elif param.type == "choice":
                values[param.name] = widget.currentText()

        return values
