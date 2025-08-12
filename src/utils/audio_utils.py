import psutil
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
from ctypes import cast, POINTER
import logging
import atexit

logger = logging.getLogger(__name__)


class AudioManager:
    def __init__(self):
        # Initialize COM
        try:
            CoInitialize()
            # Register cleanup on exit
            atexit.register(self._cleanup_com)
            logger.info("COM initialized successfully")
        except Exception as e:
            logger.warning(f"COM initialization warning: {e}")

        try:
            self.devices = AudioUtilities.GetSpeakers()
            self.interface = self.devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
            logger.info("Audio system initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing audio system: {e}")
            self.devices = None
            self.interface = None
            self.volume = None

    def _cleanup_com(self):
        """Cleanup COM on exit."""
        try:
            CoUninitialize()
            logger.info("COM cleaned up")
        except Exception as e:
            logger.debug(f"COM cleanup warning: {e}")

    def get_system_volume(self) -> float:
        """Get system volume level (0.0 to 1.0)."""
        try:
            if not self.volume:
                logger.error("Audio system not initialized")
                return 0.0
            return self.volume.GetMasterVolumeLevelScalar()
        except Exception as e:
            logger.error(f"Error getting system volume: {e}")
            return 0.0

    def set_system_volume(self, level: float):
        """Set system volume level (0.0 to 1.0)."""
        try:
            if not self.volume:
                logger.error("Audio system not initialized")
                return
            self.volume.SetMasterVolumeLevelScalar(level, None)
        except Exception as e:
            logger.error(f"Error setting system volume: {e}")

    def is_system_muted(self) -> bool:
        """Check if system is muted."""
        try:
            if not self.volume:
                logger.error("Audio system not initialized")
                return False
            return bool(self.volume.GetMute())
        except Exception as e:
            logger.error(f"Error checking system mute: {e}")
            return False

    def toggle_system_mute(self):
        """Toggle system mute."""
        try:
            if not self.volume:
                logger.error("Audio system not initialized")
                return
            current_mute = self.volume.GetMute()
            self.volume.SetMute(not current_mute, None)
            logger.info(f"System mute toggled: {not current_mute}")
        except Exception as e:
            logger.error(f"Error toggling system mute: {e}")

    def get_active_window_process(self) -> str:
        """Get the process name of the active window."""
        try:
            import win32gui
            import win32process

            # Get the active window
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                # Get process ID
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                # Get process name
                process = psutil.Process(pid)
                return process.name()
        except Exception as e:
            logger.error(f"Error getting active window process: {e}")
        return None

    def list_audio_sessions(self):
        """List all available audio sessions for debugging."""
        try:
            # Ensure COM is initialized for this thread
            try:
                CoInitialize()
            except:
                pass  # Already initialized

            sessions = AudioUtilities.GetAllSessions()
            logger.info("Available audio sessions:")
            for i, session in enumerate(sessions):
                try:
                    if session.Process:
                        process_name = session.Process.name()
                        pid = session.Process.pid
                        is_muted = (
                            session.SimpleAudioVolume.GetMute()
                            if session.SimpleAudioVolume
                            else "Unknown"
                        )
                        volume = (
                            f"{session.SimpleAudioVolume.GetMasterVolume():.2f}"
                            if session.SimpleAudioVolume
                            else "Unknown"
                        )
                        logger.info(
                            f"  {i+1}. {process_name} (PID: {pid}) - Muted: {is_muted}, Volume: {volume}"
                        )
                    else:
                        logger.info(f"  {i+1}. System session (no process)")
                except Exception as e:
                    logger.info(f"  {i+1}. Error reading session: {e}")
        except Exception as e:
            logger.error(f"Error listing audio sessions: {e}")

    def toggle_app_mute(self, app_name: str = None):
        """Toggle mute for a specific app or the active app."""
        try:
            # Ensure COM is initialized for this thread
            try:
                CoInitialize()
            except:
                pass  # Already initialized

            if app_name is None:
                app_name = self.get_active_window_process()

            if not app_name:
                logger.warning("No active application found")
                return False

            sessions = AudioUtilities.GetAllSessions()
            app_found = False
            muted_sessions = 0

            logger.info(f"Looking for audio sessions for app: {app_name}")

            for session in sessions:
                try:
                    if session.Process:
                        process_name = session.Process.name()
                        logger.debug(f"Found audio session for: {process_name}")

                        # Check for exact match or partial match (for .exe files)
                        if (
                            process_name == app_name
                            or process_name.lower() == app_name.lower()
                            or process_name.lower().replace(".exe", "")
                            == app_name.lower().replace(".exe", "")
                        ):

                            volume = session.SimpleAudioVolume
                            if volume:
                                current_mute = volume.GetMute()
                                volume.SetMute(not current_mute, None)
                                logger.info(
                                    f"App {process_name} mute toggled: {not current_mute}"
                                )
                                app_found = True
                                muted_sessions += 1
                except Exception as session_error:
                    logger.debug(f"Error processing session: {session_error}")
                    continue

            if not app_found:
                # Try to find sessions by listing all available
                logger.info("App not found, listing all available audio sessions:")
                for session in sessions:
                    try:
                        if session.Process:
                            logger.info(f"  - {session.Process.name()}")
                    except:
                        logger.info(f"  - Unknown process")

                logger.warning(f"Audio session for '{app_name}' not found")
                return False
            else:
                logger.info(
                    f"Successfully toggled mute for {muted_sessions} sessions of {app_name}"
                )
                return True

        except Exception as e:
            logger.error(f"Error toggling app mute: {e}")
            return False

    def get_app_volume(self, app_name: str) -> float:
        """Get volume level for a specific app."""
        try:
            # Ensure COM is initialized for this thread
            try:
                CoInitialize()
            except:
                pass  # Already initialized

            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.Process.name() == app_name:
                    return session.SimpleAudioVolume.GetMasterVolume()
        except Exception as e:
            logger.error(f"Error getting app volume: {e}")
        return 0.0

    def set_app_volume(self, app_name: str, level: float):
        """Set volume level for a specific app."""
        try:
            # Ensure COM is initialized for this thread
            try:
                CoInitialize()
            except:
                pass  # Already initialized

            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.Process.name() == app_name:
                    session.SimpleAudioVolume.SetMasterVolume(level, None)
                    logger.info(f"App {app_name} volume set to {level}")
                    break
        except Exception as e:
            logger.error(f"Error setting app volume: {e}")
