import json
import os
from pathlib import Path
from typing import Dict, Any, List
import logging

# Import the Hotkey model
try:
    from ..models.hotkey import Hotkey
except ImportError:
    # Fallback for when running as standalone
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from models.hotkey import Hotkey

logger = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / "AppData" / "Local" / "QuickMacro"
        self.config_file = self.config_dir / "config.json"
        self.default_config_file = Path(__file__).parent / "default_config.json"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file, creating default if needed."""
        if not self.config_file.exists():
            # Copy default config if user config doesn't exist
            with open(self.default_config_file, "r") as f:
                default_config = json.load(f)
            # Migrate default config to new format
            default_config = self._migrate_config(default_config)
            self.save_config(default_config)
            return default_config

        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                # Migrate config to new format if needed
                return self._migrate_config(config)
        except (json.JSONDecodeError, FileNotFoundError):
            # If config is corrupted, use default
            with open(self.default_config_file, "r") as f:
                default_config = json.load(f)
                return self._migrate_config(default_config)

    def _migrate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate old config format to new hotkey object format."""
        # Check if migration is needed (old format has hotkeys as dict)
        if "hotkeys" in config and isinstance(config["hotkeys"], dict):
            # Old format: {"hotkeys": {"ctrl+alt+m": "toggle_system_mute", ...}}
            old_hotkeys = config["hotkeys"]
            new_hotkeys = []

            # Convert old hotkeys to new format
            for hotkey_combination, action in old_hotkeys.items():
                new_hotkey = Hotkey(
                    hotkey=hotkey_combination,
                    action=action,
                    enabled=True,
                )
                new_hotkeys.append(new_hotkey.to_dict())

            config["hotkeys"] = new_hotkeys

            # Remove actions section as requested
            if "actions" in config:
                del config["actions"]

            logger.info(f"Migrated {len(new_hotkeys)} hotkeys to new format")

        return config

    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file."""
        if config is None:
            config = self.config

        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def get_hotkeys(self) -> List[Hotkey]:
        """Get hotkey objects."""
        hotkey_data = self.config.get("hotkeys", [])
        hotkeys = []

        for data in hotkey_data:
            try:
                hotkey = Hotkey.from_dict(data)
                if hotkey.validate():
                    hotkeys.append(hotkey)
                else:
                    logger.warning(f"Invalid hotkey configuration: {data}")
            except Exception as e:
                logger.error(f"Error loading hotkey from config: {data}, error: {e}")

        return hotkeys

    def get_hotkeys_dict(self) -> Dict[str, str]:
        """Get hotkey mappings as dict (for backward compatibility)."""
        hotkeys = self.get_hotkeys()
        return {hk.hotkey: hk.action for hk in hotkeys if hk.enabled}

    def get_settings(self) -> Dict[str, Any]:
        """Get application settings."""
        return self.config.get("settings", {})

    def add_hotkey(self, hotkey: Hotkey):
        """Add a new hotkey."""
        if not hotkey.validate():
            raise ValueError("Invalid hotkey configuration")

        # Remove existing hotkey with same combination if it exists
        self.remove_hotkey(hotkey.hotkey)

        # Add new hotkey
        if "hotkeys" not in self.config:
            self.config["hotkeys"] = []

        self.config["hotkeys"].append(hotkey.to_dict())
        self.save_config()
        logger.info(f"Added hotkey: {hotkey}")

    def update_hotkey(self, old_hotkey: str, new_hotkey: Hotkey):
        """Update an existing hotkey."""
        if not new_hotkey.validate():
            raise ValueError("Invalid hotkey configuration")

        # Remove old hotkey
        self.remove_hotkey(old_hotkey)

        # Add updated hotkey
        self.add_hotkey(new_hotkey)
        logger.info(f"Updated hotkey: {old_hotkey} -> {new_hotkey}")

    def remove_hotkey(self, hotkey_combination: str):
        """Remove a hotkey by combination."""
        if "hotkeys" not in self.config:
            return

        # Filter out the hotkey to remove
        original_count = len(self.config["hotkeys"])
        self.config["hotkeys"] = [
            hk
            for hk in self.config["hotkeys"]
            if hk.get("hotkey") != hotkey_combination
        ]

        if len(self.config["hotkeys"]) < original_count:
            self.save_config()
            logger.info(f"Removed hotkey: {hotkey_combination}")

    def update_setting(self, key: str, value: Any):
        """Update a setting value."""
        if "settings" not in self.config:
            self.config["settings"] = {}
        self.config["settings"][key] = value
        self.save_config()

    def reload_config(self):
        """Reload configuration from file."""
        self.config = self._load_config()
