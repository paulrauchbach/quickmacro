"""
Main application window with modern PyQt6 styling.
"""

import os
import logging
from typing import Dict, Any, Callable, Optional

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QMenuBar,
    QMenu,
    QStatusBar,
    QToolBar,
    QMessageBox,
    QPushButton,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QPixmap

from .components.base import BaseWindow, ModernStyle, ModernButton
from .tabs.status_tab import StatusTab
from .tabs.hotkeys_tab import HotkeysTab
from .tabs.logs_tab import LogsTab

logger = logging.getLogger(__name__)


class MainWindow(BaseWindow):
    """Main application window with modern PyQt6 styling."""

    # Signals
    window_closed = pyqtSignal()

    def __init__(self, title: str = "QuickMacro"):
        super().__init__(title, 900, 700)

        # Callbacks
        self.on_close_callback = None
        self.refresh_status_callback = None
        self.refresh_hotkeys_callback = None
        self.quick_action_callback = None
        self.add_hotkey_callback = None
        self.modify_hotkey_callback = None
        self.remove_hotkey_callback = None

        # Tab components
        self.status_tab = None
        self.hotkeys_tab = None
        self.logs_tab = None

        # UI components
        self.stacked_widget = None
        self.status_bar = None
        self.tab_buttons = []

        # Data
        self.hotkeys = {}
        self.system_status = {}

        # Setup UI
        self._setup_ui()
        self._setup_signals()

        # Show welcome message after a short delay
        QTimer.singleShot(1000, self._show_welcome_message)

        logger.info("PyQt6 modern main window created")

    def load_icon(self) -> bool:
        """Load application icon."""
        icon_paths = [
            os.path.join("assets", "icon.ico"),
            os.path.join("assets", "icon.png"),
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "assets",
                "icon.ico",
            ),
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "assets",
                "icon.png",
            ),
        ]

        for icon_path in icon_paths:
            try:
                if os.path.exists(icon_path):
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.setWindowIcon(icon)
                        logger.info(f"Loaded icon from: {icon_path}")
                        return True
            except Exception as e:
                logger.warning(f"Failed to load icon from {icon_path}: {e}")
                continue

        logger.warning("No icon found in assets folder")
        return False

    def _setup_ui(self):
        """Setup the main UI."""
        # Load icon
        self.load_icon()

        # Create menu bar
        self._create_menu_bar()
        # Hide menu bar to eliminate gap
        self.menuBar().hide()

        # Create main content
        self._create_content()

        # Create status bar
        self._create_status_bar()

    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        settings_action = QAction("&Settings...", self)
        settings_action.setStatusTip("Open application settings")
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        hide_action = QAction("&Hide to tray", self)
        hide_action.setStatusTip("Hide window to system tray")
        hide_action.triggered.connect(self.hide)
        file_menu.addAction(hide_action)

        exit_action = QAction("E&xit", self)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self._on_close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        refresh_status_action = QAction("Refresh &Status", self)
        refresh_status_action.triggered.connect(self._refresh_status)
        view_menu.addAction(refresh_status_action)

        refresh_hotkeys_action = QAction("Refresh &Hotkeys", self)
        refresh_hotkeys_action.triggered.connect(self._refresh_hotkeys)
        view_menu.addAction(refresh_hotkeys_action)

        view_menu.addSeparator()

        clear_logs_action = QAction("&Clear Logs", self)
        clear_logs_action.triggered.connect(self._clear_logs)
        view_menu.addAction(clear_logs_action)

        # Actions menu
        actions_menu = menubar.addMenu("&Actions")

        mute_action = QAction("Toggle System &Mute", self)
        mute_action.triggered.connect(lambda: self._quick_action("toggle_system_mute"))
        actions_menu.addAction(mute_action)

        app_mute_action = QAction("Toggle &App Mute", self)
        app_mute_action.triggered.connect(
            lambda: self._quick_action("toggle_active_app_mute")
        )
        actions_menu.addAction(app_mute_action)

        lock_action = QAction("&Lock Screen", self)
        lock_action.triggered.connect(lambda: self._quick_action("lock_screen"))
        actions_menu.addAction(lock_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About...", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_content(self):
        """Create the main content area."""
        # Use the existing central widget from BaseWindow
        main_container = self.central_widget
        main_container.setContentsMargins(0, 0, 0, 0)

        # Create main layout
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create header with tabs and icon buttons
        self._create_header(main_layout)

        # Create divider
        self._create_divider(main_layout)

        # Create stacked widget for tab content
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)

        # Create tabs
        self._create_tabs()

    def _create_header(self, main_layout):
        """Create the header with custom tabs and icon buttons."""
        # Create header container
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(8)

        # Create tab buttons container
        tab_container = QWidget()
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(2)

        # Create tab buttons
        self.tab_buttons = []
        tab_names = ["📊 Status", "⌨️ Hotkeys", "📝 Logs"]
        for i, tab_name in enumerate(tab_names):
            tab_btn = QPushButton(tab_name)
            tab_btn.setCheckable(True)
            tab_btn.clicked.connect(lambda checked, idx=i: self._switch_tab(idx))
            tab_btn.setStyleSheet(self._get_tab_button_style())
            self.tab_buttons.append(tab_btn)
            tab_layout.addWidget(tab_btn)

        # Set first tab as active
        if self.tab_buttons:
            self.tab_buttons[0].setChecked(True)

        # Add spacer to push icon buttons to the right
        tab_layout.addStretch()

        header_layout.addWidget(tab_container)

        # Create icon buttons container
        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(4)

        # Settings icon button
        settings_btn = QPushButton("⚙️")
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(self._show_settings)
        settings_btn.setStyleSheet(self._get_icon_button_style())
        icon_layout.addWidget(settings_btn)

        # Exit icon button
        exit_btn = QPushButton("❌")
        exit_btn.setToolTip("Exit Application")
        exit_btn.clicked.connect(self._exit_app)
        exit_btn.setStyleSheet(self._get_icon_button_style())
        icon_layout.addWidget(exit_btn)

        # Hide icon button
        hide_btn = QPushButton("🔽")
        hide_btn.setToolTip("Hide to Tray")
        hide_btn.clicked.connect(self.hide)
        hide_btn.setStyleSheet(self._get_icon_button_style())
        icon_layout.addWidget(hide_btn)

        header_layout.addWidget(icon_container)

        # Style the header
        header_widget.setStyleSheet(
            f"""
            QWidget {{
                background-color: {ModernStyle.COLORS["bg_secondary"]};
                margin: 0px;
                padding: 0px;
            }}
        """
        )

        main_layout.addWidget(header_widget)

    def _create_divider(self, main_layout):
        """Create a visual divider between header and content."""
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet(
            f"""
            QWidget {{
                background-color: {ModernStyle.COLORS["border_light"]};
            }}
        """
        )
        main_layout.addWidget(divider)

    def _get_tab_button_style(self):
        """Get the style for tab buttons."""
        return f"""
            QPushButton {{
                background-color: {ModernStyle.COLORS["bg_tertiary"]};
                color: {ModernStyle.COLORS["text_secondary"]};
                border: 1px solid {ModernStyle.COLORS["border_light"]};
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 9pt;
                min-width: 100px;
                margin-right: 2px;
            }}
            
            QPushButton:hover:!checked {{
                background-color: {ModernStyle.COLORS["bg_hover"]};
            }}
            
            QPushButton:checked {{
                background-color: {ModernStyle.COLORS["bg_selected"]};
                color: {ModernStyle.COLORS["text_on_accent"]};
                border-color: {ModernStyle.COLORS["bg_selected"]};
            }}
        """

    def _get_icon_button_style(self):
        """Get the style for icon buttons."""
        return f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 2px;
                font-size: 12px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }}
            
            QPushButton:hover {{
                background-color: {ModernStyle.COLORS["bg_hover"]};
                border-color: {ModernStyle.COLORS["border_light"]};
            }}
            
            QPushButton:pressed {{
                background-color: {ModernStyle.COLORS["bg_pressed"]};
            }}
        """

    def _switch_tab(self, index):
        """Switch to the specified tab."""
        # Update tab button states
        for i, btn in enumerate(self.tab_buttons):
            btn.setChecked(i == index)

        # Switch the actual tab content
        self.stacked_widget.setCurrentIndex(index)

    def _create_tabs(self):
        """Create the tab components."""
        # Status tab
        self.status_tab = StatusTab()
        self.stacked_widget.addWidget(self.status_tab)

        # Hotkeys tab
        self.hotkeys_tab = HotkeysTab()
        self.stacked_widget.addWidget(self.hotkeys_tab)

        # Logs tab
        self.logs_tab = LogsTab()
        self.stacked_widget.addWidget(self.logs_tab)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - QuickMacro is running")

    def _setup_signals(self):
        """Setup signal connections."""
        # Connect tab signals if tabs exist
        if self.status_tab:
            self.status_tab.refresh_requested.connect(self._refresh_status)
            self.status_tab.action_requested.connect(self._quick_action)

        if self.hotkeys_tab:
            self.hotkeys_tab.refresh_requested.connect(self._refresh_hotkeys)
            self.hotkeys_tab.hotkey_added.connect(self._on_hotkey_added)
            self.hotkeys_tab.hotkey_modified.connect(self._on_hotkey_modified)
            self.hotkeys_tab.hotkey_removed.connect(self._on_hotkey_removed)

    def _show_welcome_message(self):
        """Show welcome message in logs."""
        self.add_log_message("Welcome to QuickMacro!")
        self.add_log_message("Modern PyQt6 interface is running")
        self.add_log_message("Use Ctrl+Shift+H to show/hide this window")
        self.add_log_message("Check the status tab for system information")

    def _on_close(self):
        """Handle window close event."""
        if self.on_close_callback:
            self.on_close_callback()
        else:
            self.hide()

    def _exit_app(self):
        """Exit the application completely."""
        QApplication.quit()

    def _show_settings(self):
        """Show settings dialog."""
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog would open here.\nThis feature will be implemented in a future version.",
        )

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About QuickMacro",
            "QuickMacro v1.0\n\nA modern hotkey manager for Windows.\n\nBuilt with PyQt6 for a beautiful, native interface.",
        )

    def _refresh_all(self):
        """Refresh all data."""
        self._refresh_status()
        self._refresh_hotkeys()
        self.status_bar.showMessage("Refreshed all data")

    def _refresh_status(self):
        """Refresh system status display."""
        if self.refresh_status_callback:
            self.refresh_status_callback()
        self.status_bar.showMessage("Status refreshed")

    def _refresh_hotkeys(self):
        """Refresh hotkeys display."""
        if self.refresh_hotkeys_callback:
            self.refresh_hotkeys_callback()
        self.status_bar.showMessage("Hotkeys refreshed")

    def _clear_logs(self):
        """Clear the logs."""
        if self.logs_tab:
            self.logs_tab._clear_log()

    def _quick_action(self, action_name: str):
        """Execute a quick action."""
        if self.quick_action_callback:
            self.quick_action_callback(action_name)
        self.status_bar.showMessage(f"Executed action: {action_name}")

    def closeEvent(self, event):
        """Override close event."""
        self.window_closed.emit()
        if self.on_close_callback:
            self.on_close_callback()
            event.ignore()  # Don't actually close, let the callback handle it
        else:
            self.hide()
            event.ignore()

    def update_status(self, status: Dict[str, Any]):
        """Update the status display."""
        self.system_status = status
        if self.status_tab:
            self.status_tab.update_status(status)

        # Update status bar with key info
        volume = status.get("system_volume", 0)
        muted = status.get("system_muted", False)
        status_text = f"Volume: {volume:.0%}" + (" (Muted)" if muted else "")
        self.status_bar.showMessage(status_text)

    def update_hotkeys(self, hotkeys: Dict[str, str]):
        """Update the hotkeys display."""
        self.hotkeys = hotkeys
        if self.hotkeys_tab:
            self.hotkeys_tab.update_hotkeys(hotkeys)

    def add_log_message(self, message: str):
        """Add a message to the log display."""
        if self.logs_tab:
            self.logs_tab.add_log_message(message)

    def set_callbacks(
        self,
        on_close: Optional[Callable] = None,
        refresh_status: Optional[Callable] = None,
        refresh_hotkeys: Optional[Callable] = None,
        quick_action: Optional[Callable] = None,
        add_hotkey: Optional[Callable] = None,
        modify_hotkey: Optional[Callable] = None,
        remove_hotkey: Optional[Callable] = None,
    ):
        """Set callback functions."""
        self.on_close_callback = on_close
        self.refresh_status_callback = refresh_status
        self.refresh_hotkeys_callback = refresh_hotkeys
        self.quick_action_callback = quick_action
        self.add_hotkey_callback = add_hotkey
        self.modify_hotkey_callback = modify_hotkey
        self.remove_hotkey_callback = remove_hotkey

        # Set callbacks for tab components
        if self.status_tab:
            self.status_tab.set_callbacks(refresh_status, quick_action)
        if self.hotkeys_tab:
            self.hotkeys_tab.set_callbacks(
                refresh_callback=refresh_hotkeys,
                add_hotkey_callback=add_hotkey,
                modify_hotkey_callback=modify_hotkey,
                remove_hotkey_callback=remove_hotkey,
            )

    def toggle_visibility(self):
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def is_visible(self) -> bool:
        """Check if window is visible."""
        return self.isVisible()

    def set_available_actions(self, actions):
        """Set available actions for hotkey management."""
        if self.hotkeys_tab:
            self.hotkeys_tab.set_available_actions(actions)

    def set_action_manager(self, action_manager):
        """Set action manager for parameter handling."""
        if self.hotkeys_tab:
            self.hotkeys_tab.set_action_manager(action_manager)

    def _on_hotkey_added(self, hotkey: str, action: str):
        """Handle hotkey added from UI."""
        if self.add_hotkey_callback:
            self.add_hotkey_callback(hotkey, action)

        # Log the action
        self.add_log_message(f"Hotkey added: {hotkey} → {action}")

    def _on_hotkey_modified(self, old_hotkey: str, new_hotkey: str, action: str):
        """Handle hotkey modified from UI."""
        if self.modify_hotkey_callback:
            self.modify_hotkey_callback(old_hotkey, new_hotkey, action)

        # Log the action
        self.add_log_message(f"Hotkey modified: {old_hotkey} → {new_hotkey} ({action})")

    def _on_hotkey_removed(self, hotkey: str):
        """Handle hotkey removed from UI."""
        if self.remove_hotkey_callback:
            self.remove_hotkey_callback(hotkey)

        # Log the action
        self.add_log_message(f"Hotkey removed: {hotkey}")
