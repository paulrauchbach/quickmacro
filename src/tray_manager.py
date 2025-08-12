import pystray
import logging
import threading
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class TrayManager:
    def __init__(self, app_name: str = "QuickMacro"):
        self.app_name = app_name
        self.icon = None
        self.running = False
        self.tray_thread = None

        # Callbacks for menu actions
        self.on_open_callback = None
        self.on_settings_callback = None
        self.on_exit_callback = None
        self.on_left_click_callback = None

    def set_callbacks(
        self,
        on_open: Optional[Callable] = None,
        on_settings: Optional[Callable] = None,
        on_exit: Optional[Callable] = None,
        on_left_click: Optional[Callable] = None,
    ):
        """Set callback functions for tray menu actions."""
        self.on_open_callback = on_open
        self.on_settings_callback = on_settings
        self.on_exit_callback = on_exit
        self.on_left_click_callback = on_left_click

    def _execute_callback_on_main_thread(self, callback):
        """Execute callback on the main thread using QMetaObject.invokeMethod."""
        logger.info("Attempting to execute callback on main thread")

        try:
            from PyQt6.QtCore import QMetaObject, Qt, QObject, pyqtSlot
            from PyQt6.QtWidgets import QApplication

            # Get the QApplication instance
            app = QApplication.instance()
            if app is None:
                logger.warning(
                    "No QApplication instance found, executing callback directly"
                )
                callback()
                return

            # Create a helper object in the main thread to receive the invocation
            class CallbackInvoker(QObject):
                def __init__(self):
                    super().__init__()
                    # Move this object to the main thread
                    self.moveToThread(app.thread())

                @pyqtSlot()
                def invoke_callback(self):
                    logger.info("Executing callback on main thread via QMetaObject")
                    try:
                        callback()
                        logger.info("Callback executed successfully on main thread")
                    except Exception as e:
                        logger.error(f"Error in callback execution: {e}")

            # Create the invoker and invoke the method on the main thread
            invoker = CallbackInvoker()
            QMetaObject.invokeMethod(
                invoker, "invoke_callback", Qt.ConnectionType.QueuedConnection
            )
            logger.info("Callback invocation scheduled via QMetaObject")

        except ImportError:
            logger.warning("PyQt6 not available, executing callback directly")
            callback()
        except Exception as e:
            logger.error(f"Error scheduling callback on main thread: {e}")
            # Fallback to direct execution
            logger.info("Falling back to direct callback execution")
            callback()

    def load_icon_image(self, size: int = 64) -> Image.Image:
        """Load icon image from assets folder, fallback to Windows 11 style creation."""
        # Try to load from assets folder first
        icon_paths = [
            os.path.join("assets", "icon.png"),
            os.path.join("assets", "icon.ico"),
            # Also try relative to the script location
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png"
            ),
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "assets", "icon.ico"
            ),
        ]

        for icon_path in icon_paths:
            try:
                if os.path.exists(icon_path):
                    image = Image.open(icon_path)
                    # Convert to RGBA if needed
                    if image.mode != "RGBA":
                        image = image.convert("RGBA")
                    # Resize to requested size
                    if image.size != (size, size):
                        image = image.resize((size, size), Image.Resampling.LANCZOS)
                    logger.info(f"Loaded icon from: {icon_path}")
                    return image
            except Exception as e:
                logger.warning(f"Failed to load icon from {icon_path}: {e}")
                continue

        # Fallback to Windows 11 style creation
        logger.info("Creating Windows 11 style tray icon")
        return self.create_windows11_icon(size)

    def create_windows11_icon(self, size: int = 64) -> Image.Image:
        """Create a Windows 11 Fluent Design style icon."""
        # Create image with transparency
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Windows 11 color scheme
        bg_color = (0, 120, 212, 255)  # Windows 11 accent blue
        secondary_color = (16, 110, 190, 255)  # Darker blue
        white = (255, 255, 255, 255)  # White for contrast
        shadow = (0, 0, 0, 32)  # Subtle shadow

        # Calculate dimensions with Windows 11 padding
        padding = max(4, size // 8)
        icon_size = size - (padding * 2)
        center = size // 2

        # Draw subtle shadow (Windows 11 depth)
        shadow_offset = max(1, size // 24)
        shadow_rect = [
            padding + shadow_offset,
            padding + shadow_offset,
            size - padding + shadow_offset,
            size - padding + shadow_offset,
        ]
        draw.rounded_rectangle(shadow_rect, radius=size // 8, fill=shadow)

        # Draw main background with rounded corners (Windows 11 style)
        main_rect = [padding, padding, size - padding, size - padding]
        draw.rounded_rectangle(main_rect, radius=size // 8, fill=bg_color)

        # Draw inner accent area
        inner_padding = padding + max(2, size // 16)
        inner_rect = [
            inner_padding,
            inner_padding,
            size - inner_padding,
            size - inner_padding,
        ]
        draw.rounded_rectangle(inner_rect, radius=size // 12, fill=secondary_color)

        # Draw the main symbol - simplified keyboard/hotkey representation
        if size >= 24:
            self._draw_windows11_symbol(draw, size, white, center)
        else:
            # Very small size - just a dot
            dot_size = max(2, size // 12)
            draw.ellipse(
                [
                    center - dot_size,
                    center - dot_size,
                    center + dot_size,
                    center + dot_size,
                ],
                fill=white,
            )

        # Add subtle highlight (Windows 11 lighting effect)
        highlight_size = max(3, size // 12)
        highlight_x = center - icon_size // 4
        highlight_y = center - icon_size // 4

        # Create gradient-like highlight
        for i in range(3):
            alpha = 80 - (i * 20)
            highlight_color = (255, 255, 255, alpha)
            draw.ellipse(
                [
                    highlight_x + i,
                    highlight_y + i,
                    highlight_x + highlight_size - i,
                    highlight_y + highlight_size - i,
                ],
                fill=highlight_color,
            )

        return image

    def _draw_windows11_symbol(
        self, draw: ImageDraw.Draw, size: int, color: tuple, center: int
    ):
        """Draw a Windows 11 style keyboard/hotkey symbol."""
        # Modern, minimalist design
        symbol_width = size // 3
        symbol_height = size // 4

        # Key representation - three rounded rectangles
        key_height = max(2, size // 20)
        key_spacing = max(3, size // 12)

        # Calculate starting position
        start_y = center - symbol_height // 2
        start_x = center - symbol_width // 2

        # Draw three "keys" representing hotkey combinations
        for i in range(3):
            y_pos = start_y + (i * key_spacing)

            # Vary the width slightly for visual interest
            if i == 0:  # Top key (shortest - like Ctrl)
                key_width = int(symbol_width * 0.6)
                x_offset = (symbol_width - key_width) // 2
            elif i == 1:  # Middle key (medium - like Shift)
                key_width = int(symbol_width * 0.8)
                x_offset = (symbol_width - key_width) // 2
            else:  # Bottom key (longest - like letter key)
                key_width = symbol_width
                x_offset = 0

            # Draw rounded rectangle for each key
            key_rect = [
                start_x + x_offset,
                y_pos,
                start_x + x_offset + key_width,
                y_pos + key_height,
            ]

            # Small radius for modern look
            radius = max(1, key_height // 2)
            draw.rounded_rectangle(key_rect, radius=radius, fill=color)

        # Add small indicator dots below (function keys indicator)
        dot_y = start_y + (3 * key_spacing) + key_height + max(2, size // 16)
        dot_size = max(1, size // 32)

        for i in range(3):
            dot_x = start_x + (i * symbol_width // 3) + (symbol_width // 6)
            draw.ellipse(
                [
                    dot_x - dot_size,
                    dot_y - dot_size,
                    dot_x + dot_size,
                    dot_y + dot_size,
                ],
                fill=color,
            )

    def create_menu(self):
        """Create the Windows 11 style context menu."""
        menu_items = []

        if self.on_open_callback:
            # Mark as default so double-click on tray icon triggers this action
            menu_items.append(
                pystray.MenuItem("Open QuickMacro", self._on_open, default=True)
            )

        if self.on_settings_callback:
            menu_items.append(pystray.MenuItem("Settings", self._on_settings))

        # Add separator
        if menu_items:
            menu_items.append(pystray.Menu.SEPARATOR)

        # Always add exit option
        menu_items.append(pystray.MenuItem("Exit", self._on_exit))

        return pystray.Menu(*menu_items)

    def _on_open(self, icon, item):
        """Handle open menu item."""
        logger.info("Tray menu: Open clicked")
        if self.on_open_callback:
            try:
                self._execute_callback_on_main_thread(self.on_open_callback)
                logger.info("Open callback scheduled successfully")
            except Exception as e:
                logger.error(f"Error in open callback: {e}")
        else:
            logger.warning("No open callback set")

    def _on_settings(self, icon, item):
        """Handle settings menu item."""
        logger.info("Tray menu: Settings clicked")
        if self.on_settings_callback:
            try:
                self._execute_callback_on_main_thread(self.on_settings_callback)
                logger.info("Settings callback scheduled successfully")
            except Exception as e:
                logger.error(f"Error in settings callback: {e}")
        else:
            logger.warning("No settings callback set")

    def _on_exit(self, icon, item):
        """Handle exit menu item."""
        logger.info("Tray menu: Exit clicked")
        if self.on_exit_callback:
            try:
                self._execute_callback_on_main_thread(self.on_exit_callback)
                logger.info("Exit callback scheduled successfully")
            except Exception as e:
                logger.error(f"Error in exit callback: {e}")
        else:
            logger.warning("No exit callback set")
        # Note: Don't call self.stop() here as it should be handled by the callback

    def _on_left_click(self, icon):
        """Handle left click on tray icon."""
        logger.info("Tray icon: Left click")
        if self.on_left_click_callback:
            try:
                self._execute_callback_on_main_thread(self.on_left_click_callback)
                logger.info("Left click callback scheduled successfully")
            except Exception as e:
                logger.error(f"Error in left click callback: {e}")
        else:
            logger.warning("No left click callback set")

    def start(self):
        """Start the Windows 11 style system tray icon."""
        if self.running:
            return

        try:
            # Create Windows 11 style icon image
            icon_image = self.load_icon_image()

            # Create the tray icon
            self.icon = pystray.Icon(
                self.app_name, icon_image, title=self.app_name, menu=self.create_menu()
            )

            # Rely on default menu item for double-click behavior on Windows

            self.running = True

            # Start the tray icon in a separate thread
            self.tray_thread = threading.Thread(target=self._run_tray, daemon=True)
            self.tray_thread.start()

            logger.info("Windows 11 style system tray icon started")

        except Exception as e:
            logger.error(f"Error starting tray icon: {e}")
            self.running = False

    def _run_tray(self):
        """Run the tray icon (blocking call)."""
        try:
            self.icon.run()
        except Exception as e:
            logger.error(f"Error running tray icon: {e}")
        finally:
            self.running = False

    def stop(self):
        """Stop the system tray icon."""
        if not self.running:
            return

        try:
            if self.icon:
                self.icon.stop()
            self.running = False
            logger.info("System tray icon stopped")
        except Exception as e:
            logger.error(f"Error stopping tray icon: {e}")

    def update_icon(self, new_image: Image.Image):
        """Update the tray icon image."""
        if self.icon and self.running:
            try:
                self.icon.icon = new_image
                logger.info("Tray icon updated")
            except Exception as e:
                logger.error(f"Error updating tray icon: {e}")

    def update_title(self, new_title: str):
        """Update the tray icon tooltip."""
        if self.icon and self.running:
            try:
                self.icon.title = new_title
                logger.info(f"Tray icon title updated: {new_title}")
            except Exception as e:
                logger.error(f"Error updating tray icon title: {e}")

    def show_notification(self, title: str, message: str):
        """Show a Windows 11 style notification."""
        if self.icon and self.running:
            try:
                self.icon.notify(message, title)
                logger.info(f"Notification shown: {title} - {message}")
            except Exception as e:
                logger.error(f"Error showing notification: {e}")

    def is_running(self) -> bool:
        """Check if the tray icon is running."""
        return self.running

    def get_icon_path(self) -> str:
        """Get the path to the icon file."""
        icon_paths = [
            os.path.join("assets", "icon.ico"),
            os.path.join("assets", "icon.png"),
            # Also try relative to the script location
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "assets", "icon.ico"
            ),
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png"
            ),
        ]

        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                return icon_path

        return None

    # Legacy method for compatibility
    def create_modern_icon(self, size: int = 64) -> Image.Image:
        """Legacy method - redirects to Windows 11 style."""
        return self.create_windows11_icon(size)

    def create_fallback_icon(self, size: int = 64) -> Image.Image:
        """Legacy method - redirects to Windows 11 style."""
        return self.create_windows11_icon(size)
