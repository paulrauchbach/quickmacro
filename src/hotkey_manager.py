import keyboard
import logging
import threading
from typing import Dict, Callable, Any, List

# Import the Hotkey model
try:
    from .models.hotkey import Hotkey
except ImportError:
    # Fallback for when running as standalone
    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), "."))
    from models.hotkey import Hotkey

logger = logging.getLogger(__name__)


class HotkeyManager:
    def __init__(self):
        self.hotkeys = {}
        self.callbacks = {}
        self.running = False
        self.listener_thread = None

    def register_hotkey(self, hotkey: str, callback: Callable, action_name: str = None):
        """Register a global hotkey with a callback function."""
        try:
            # Store the callback
            self.callbacks[hotkey] = {
                "callback": callback,
                "action_name": action_name or hotkey,
            }

            # Register with keyboard library
            keyboard.add_hotkey(hotkey, callback)
            self.hotkeys[hotkey] = True

            logger.info(f"Hotkey registered: {hotkey} -> {action_name}")
            return True

        except Exception as e:
            logger.error(f"Error registering hotkey {hotkey}: {e}")
            return False

    def unregister_hotkey(self, hotkey: str):
        """Unregister a hotkey."""
        try:
            if hotkey in self.hotkeys:
                keyboard.remove_hotkey(hotkey)
                del self.hotkeys[hotkey]
                del self.callbacks[hotkey]
                logger.info(f"Hotkey unregistered: {hotkey}")
                return True
        except Exception as e:
            logger.error(f"Error unregistering hotkey {hotkey}: {e}")
        return False

    def register_hotkeys_from_config(
        self, hotkey_config: Dict[str, str], action_callback: Callable
    ):
        """Register multiple hotkeys from configuration (backward compatibility)."""
        success_count = 0

        for hotkey, action_name in hotkey_config.items():
            # Create a callback that passes the action name
            callback = lambda action=action_name: action_callback(action)

            if self.register_hotkey(hotkey, callback, action_name):
                success_count += 1

        logger.info(f"Registered {success_count}/{len(hotkey_config)} hotkeys")
        return success_count

    def register_hotkeys_from_objects(
        self, hotkeys: List[Hotkey], action_callback: Callable
    ):
        """Register multiple hotkeys from Hotkey objects."""
        success_count = 0

        for hotkey_obj in hotkeys:
            if not hotkey_obj.enabled:
                logger.debug(f"Skipping disabled hotkey: {hotkey_obj.hotkey}")
                continue

            if not hotkey_obj.validate():
                logger.warning(f"Invalid hotkey configuration: {hotkey_obj}")
                continue

            # Create a callback that passes the action name
            callback = lambda action=hotkey_obj.action: action_callback(action)

            if self.register_hotkey(hotkey_obj.hotkey, callback, hotkey_obj.action):
                success_count += 1

        logger.info(f"Registered {success_count}/{len(hotkeys)} hotkeys from objects")
        return success_count

    def clear_all_hotkeys(self):
        """Clear all registered hotkeys."""
        try:
            for hotkey in list(self.hotkeys.keys()):
                self.unregister_hotkey(hotkey)
            logger.info("All hotkeys cleared")
        except Exception as e:
            logger.error(f"Error clearing hotkeys: {e}")

    def start_listener(self):
        """Start the hotkey listener in a separate thread."""
        if self.running:
            return

        self.running = True
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()
        logger.info("Hotkey listener started")

    def stop_listener(self):
        """Stop the hotkey listener."""
        if not self.running:
            return

        self.running = False
        try:
            # Clear all hotkeys to stop listening
            keyboard.unhook_all()
            logger.info("Hotkey listener stopped")
        except Exception as e:
            logger.error(f"Error stopping hotkey listener: {e}")

    def _listen_loop(self):
        """Main listening loop for hotkeys."""
        try:
            # Keep the thread alive while running
            # keyboard.wait(timeout=...) is not supported; use sleep loop
            import time

            while self.running:
                time.sleep(0.2)
        except Exception as e:
            logger.error(f"Error in hotkey listener loop: {e}")

    def get_registered_hotkeys(self) -> Dict[str, str]:
        """Get all currently registered hotkeys."""
        return {hotkey: info["action_name"] for hotkey, info in self.callbacks.items()}

    def is_hotkey_registered(self, hotkey: str) -> bool:
        """Check if a hotkey is registered."""
        return hotkey in self.hotkeys

    def reload_hotkeys(self, hotkey_config: Dict[str, str], action_callback: Callable):
        """Reload hotkeys from new configuration."""
        logger.info("Reloading hotkeys...")

        # Clear existing hotkeys
        self.clear_all_hotkeys()

        # Register new hotkeys
        return self.register_hotkeys_from_config(hotkey_config, action_callback)
