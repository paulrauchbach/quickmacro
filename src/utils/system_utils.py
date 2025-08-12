import subprocess
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SystemManager:
    @staticmethod
    def lock_screen():
        """Lock the Windows screen."""
        try:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
            logger.info("Screen locked")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error locking screen: {e}")

    @staticmethod
    def sleep_system():
        """Put the system to sleep."""
        try:
            subprocess.run(
                ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True
            )
            logger.info("System put to sleep")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error putting system to sleep: {e}")

    @staticmethod
    def shutdown_system(force: bool = False):
        """Shutdown the system."""
        try:
            cmd = ["shutdown", "/s", "/t", "0"]
            if force:
                cmd.append("/f")
            subprocess.run(cmd, check=True)
            logger.info("System shutdown initiated")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error shutting down system: {e}")

    @staticmethod
    def restart_system(force: bool = False):
        """Restart the system."""
        try:
            cmd = ["shutdown", "/r", "/t", "0"]
            if force:
                cmd.append("/f")
            subprocess.run(cmd, check=True)
            logger.info("System restart initiated")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error restarting system: {e}")

    @staticmethod
    def run_script(script_path: str, args: Optional[list] = None):
        """Run a script or executable."""
        try:
            if not os.path.exists(script_path):
                logger.error(f"Script not found: {script_path}")
                return False

            cmd = [script_path]
            if args:
                cmd.extend(args)

            subprocess.Popen(cmd, shell=True)
            logger.info(f"Script executed: {script_path}")
            return True
        except Exception as e:
            logger.error(f"Error running script {script_path}: {e}")
            return False

    @staticmethod
    def open_application(app_path: str):
        """Open an application."""
        try:
            subprocess.Popen(app_path, shell=True)
            logger.info(f"Application opened: {app_path}")
            return True
        except Exception as e:
            logger.error(f"Error opening application {app_path}: {e}")
            return False

    @staticmethod
    def minimize_all_windows():
        """Minimize all open windows."""
        try:
            import win32gui
            import win32con

            def enum_handler(hwnd, lParam):
                if win32gui.IsWindowVisible(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                return True

            win32gui.EnumWindows(enum_handler, None)
            logger.info("All windows minimized")
        except Exception as e:
            logger.error(f"Error minimizing windows: {e}")

    @staticmethod
    def get_active_window_title() -> str:
        """Get the title of the active window."""
        try:
            import win32gui

            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
        except Exception as e:
            logger.error(f"Error getting active window title: {e}")
            return ""

    @staticmethod
    def show_notification(title: str, message: str, duration: int = 3000):
        """Show a Windows notification."""
        try:
            import win32gui
            import win32con

            # This is a simple implementation
            # For more advanced notifications, consider using plyer or win10toast
            print(f"Notification: {title} - {message}")
            logger.info(f"Notification shown: {title} - {message}")
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
