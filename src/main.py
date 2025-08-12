#!/usr/bin/env python3
"""
QuickMacro - Windows Background App
Main application entry point
"""

import sys
import os
import logging
import threading
import time
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import PyQt6 for the application
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

try:
    # Try bundled imports first (for PyInstaller)
    from config.settings import ConfigManager
    from tray_manager import TrayManager
    from hotkey_manager import HotkeyManager
    from action_manager import ActionManager
    from gui.main_window import MainWindow
except ImportError:
    # Fallback to relative imports (for development)
    from .config.settings import ConfigManager
    from .tray_manager import TrayManager
    from .hotkey_manager import HotkeyManager
    from .action_manager import ActionManager
    from .gui.main_window import MainWindow

# Configure logging to Roaming AppData (e.g., %APPDATA%\QuickMacro)
appdata_roaming = Path(os.getenv("APPDATA") or (Path.home() / "AppData" / "Roaming"))
log_dir = appdata_roaming / "QuickMacro"
log_dir.mkdir(parents=True, exist_ok=True)
log_file_path = log_dir / "quickmacro.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class QuickMacroApp:
    def __init__(self):
        # Create QApplication first
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("QuickMacro")
        self.app.setApplicationVersion("1.0")

        self.config_manager = ConfigManager()
        self.tray_manager = TrayManager("QuickMacro")
        self.hotkey_manager = HotkeyManager()
        self.action_manager = ActionManager()
        self.main_window = MainWindow("QuickMacro")

        self.running = False
        self.status_update_thread = None
        self.status_timer = None

        # Setup callbacks
        self._setup_callbacks()

        logger.info("QuickMacro PyQt6 application initialized")

    def _setup_callbacks(self):
        """Setup callbacks between components."""
        # Tray manager callbacks
        self.tray_manager.set_callbacks(
            on_open=self._on_tray_open,
            on_settings=self._on_tray_settings,
            on_exit=self._on_tray_exit,
            on_left_click=self._on_tray_left_click,
        )

        # Main window callbacks
        self.main_window.set_callbacks(
            on_close=self._on_window_close,
            refresh_status=self._refresh_status,
            refresh_hotkeys=self._refresh_hotkeys,
            quick_action=self._execute_quick_action,
            add_hotkey=self._add_hotkey,
            modify_hotkey=self._modify_hotkey,
            remove_hotkey=self._remove_hotkey,
        )

    def _on_tray_open(self):
        """Handle tray 'Open' action."""
        logger.info("Tray: Open clicked - CALLBACK EXECUTING")
        try:
            logger.info("About to show and focus main window")
            self.main_window.show()
            # Ensure window is restored, raised, and focused
            try:
                self.main_window.raise_()
                self.main_window.activateWindow()
            except Exception:
                pass
            logger.info("Main window brought to foreground")
            logger.info(f"Window visible: {self.main_window.isVisible()}")
        except Exception as e:
            logger.error(f"Error in _on_tray_open: {e}")
            raise

    def _on_tray_settings(self):
        """Handle tray 'Settings' action."""
        logger.info("Tray: Settings clicked")
        self.main_window.show()
        # TODO: Switch to settings tab or open settings dialog

    def _on_tray_exit(self):
        """Handle tray 'Exit' action."""
        logger.info("Tray: Exit clicked - CALLBACK EXECUTING")
        try:
            logger.info("About to call shutdown()")
            self.shutdown()
            logger.info("shutdown() completed")
        except Exception as e:
            logger.error(f"Error in _on_tray_exit: {e}")
            raise

    def _on_tray_left_click(self):
        """Handle tray left click."""
        logger.info("Tray: Left double-click (default action) -> Open window")
        # Treat default action (double-click) as 'open': show and focus window
        try:
            self.main_window.show()
            try:
                self.main_window.raise_()
                self.main_window.activateWindow()
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Error handling tray double-click: {e}")

    def _on_window_close(self):
        """Handle main window close."""
        logger.info("Window: Close requested")
        self.main_window.hide()

    def _refresh_status(self):
        """Refresh system status."""
        try:
            status = self.action_manager.get_system_status()
            self.main_window.update_status(status)
            logger.info("Status refreshed")
        except Exception as e:
            logger.error(f"Error refreshing status: {e}")

    def _refresh_hotkeys(self):
        """Refresh hotkeys display."""
        try:
            hotkeys = self.hotkey_manager.get_registered_hotkeys()
            self.main_window.update_hotkeys(hotkeys)
            logger.info("Hotkeys refreshed")
        except Exception as e:
            logger.error(f"Error refreshing hotkeys: {e}")

    def _execute_quick_action(self, action_name: str):
        """Execute a quick action from the UI."""
        try:
            # Actions are now handled directly by action name
            success = self.action_manager.execute_action(action_name)

            if success:
                self.main_window.add_log_message(f"Action executed: {action_name}")
                self.tray_manager.show_notification(
                    "QuickMacro", f"Executed: {action_name}"
                )
            else:
                self.main_window.add_log_message(f"Action failed: {action_name}")
        except Exception as e:
            logger.error(f"Error executing quick action {action_name}: {e}")

    def _add_hotkey(self, hotkey: str, action: str):
        """Add a new hotkey."""
        try:
            from models.hotkey import Hotkey

            new_hotkey = Hotkey(hotkey=hotkey, action=action, enabled=True)

            self.config_manager.add_hotkey(new_hotkey)

            # Re-register all hotkeys
            self.hotkey_manager.clear_all_hotkeys()
            hotkeys = self.config_manager.get_hotkeys()
            self.hotkey_manager.register_hotkeys_from_objects(
                hotkeys, self._on_hotkey_pressed
            )

            # Refresh UI
            self._refresh_hotkeys()

            logger.info(f"Added hotkey: {hotkey} -> {action}")
            self.main_window.add_log_message(f"Added hotkey: {hotkey} -> {action}")

        except Exception as e:
            logger.error(f"Error adding hotkey: {e}")
            self.main_window.add_log_message(f"Error adding hotkey: {e}")

    def _modify_hotkey(self, old_hotkey: str, new_hotkey: str, action: str):
        """Modify an existing hotkey."""
        try:
            from models.hotkey import Hotkey

            new_hotkey_obj = Hotkey(hotkey=new_hotkey, action=action, enabled=True)

            self.config_manager.update_hotkey(old_hotkey, new_hotkey_obj)

            # Re-register all hotkeys
            self.hotkey_manager.clear_all_hotkeys()
            hotkeys = self.config_manager.get_hotkeys()
            self.hotkey_manager.register_hotkeys_from_objects(
                hotkeys, self._on_hotkey_pressed
            )

            # Refresh UI
            self._refresh_hotkeys()

            logger.info(f"Modified hotkey: {old_hotkey} -> {new_hotkey} ({action})")
            self.main_window.add_log_message(
                f"Modified hotkey: {old_hotkey} -> {new_hotkey}"
            )

        except Exception as e:
            logger.error(f"Error modifying hotkey: {e}")
            self.main_window.add_log_message(f"Error modifying hotkey: {e}")

    def _remove_hotkey(self, hotkey: str):
        """Remove a hotkey."""
        try:
            self.config_manager.remove_hotkey(hotkey)

            # Re-register all hotkeys
            self.hotkey_manager.clear_all_hotkeys()
            hotkeys = self.config_manager.get_hotkeys()
            self.hotkey_manager.register_hotkeys_from_objects(
                hotkeys, self._on_hotkey_pressed
            )

            # Refresh UI
            self._refresh_hotkeys()

            logger.info(f"Removed hotkey: {hotkey}")
            self.main_window.add_log_message(f"Removed hotkey: {hotkey}")

        except Exception as e:
            logger.error(f"Error removing hotkey: {e}")
            self.main_window.add_log_message(f"Error removing hotkey: {e}")

    def _on_hotkey_pressed(self, action_name: str):
        """Handle hotkey press."""
        try:
            logger.info(f"Hotkey pressed: {action_name}")

            if action_name == "toggle_main_window":
                self.main_window.toggle_visibility()
                return

            # Execute action (no parameters stored per hotkey)
            success = self.action_manager.execute_action(action_name)

            if success:
                self.main_window.add_log_message(f"Hotkey action: {action_name}")
                if self.config_manager.get_settings().get("show_notifications", True):
                    self.tray_manager.show_notification(
                        "QuickMacro", f"Hotkey: {action_name}"
                    )
            else:
                self.main_window.add_log_message(f"Hotkey action failed: {action_name}")

        except Exception as e:
            logger.error(f"Error handling hotkey {action_name}: {e}")

    def _update_status(self):
        """Update system status (called by QTimer)."""
        try:
            if self.main_window.is_visible():
                self._refresh_status()
        except Exception as e:
            logger.error(f"Error updating status: {e}")

    def start(self):
        """Start the application."""
        if self.running:
            return

        try:
            logger.info("Starting QuickMacro...")

            # Load configuration
            hotkeys = self.config_manager.get_hotkeys()  # Now returns List[Hotkey]
            settings = self.config_manager.get_settings()

            print(settings)

            # Register hotkeys using new object-based method
            self.hotkey_manager.register_hotkeys_from_objects(
                hotkeys, self._on_hotkey_pressed
            )
            self.hotkey_manager.start_listener()

            # Start tray icon
            self.tray_manager.start()

            # Main window is already created in __init__ for PyQt6
            # No need to call create_window()

            # Set available actions for the hotkey manager
            all_actions = self.action_manager.get_all_actions()
            # Convert to format expected by UI
            available_actions = [
                {"id": action_id, "name": action_data["name"]}
                for action_id, action_data in all_actions.items()
            ]
            self.main_window.set_available_actions(available_actions)

            # Set action manager for parameter handling
            self.main_window.set_action_manager(self.action_manager)

            # Show window if not set to start minimized
            if not settings.get("start_minimized", True):
                self.main_window.show()

            # Start status update timer
            self.running = True
            self.status_timer = QTimer()
            self.status_timer.timeout.connect(self._update_status)
            self.status_timer.start(5000)  # Update every 5 seconds

            # Initial status refresh
            self._refresh_status()
            self._refresh_hotkeys()

            logger.info("QuickMacro started successfully")

            # Show startup notification
            if settings.get("show_notifications", True):
                self.tray_manager.show_notification("QuickMacro", "Application started")

        except Exception as e:
            logger.error(f"Error starting application: {e}")
            raise

    def shutdown(self):
        """Shutdown the application."""
        if not self.running:
            return

        try:
            logger.info("Shutting down QuickMacro...")

            self.running = False

            # Use QTimer to ensure shutdown happens on main thread
            QTimer.singleShot(0, self._do_shutdown)

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def _do_shutdown(self):
        """Perform the actual shutdown on the main thread."""
        try:
            # Stop status timer
            if self.status_timer:
                self.status_timer.stop()

            # Stop components
            self.hotkey_manager.stop_listener()
            self.tray_manager.stop()

            # Close main window
            self.main_window.close()

            # Quit the PyQt application
            self.app.quit()

            logger.info("QuickMacro shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def run(self):
        """Run the application main loop."""
        try:
            self.start()

            # Run the PyQt event loop
            return self.app.exec()

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.shutdown()


def main():
    """Main entry point."""
    try:
        app = QuickMacroApp()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
