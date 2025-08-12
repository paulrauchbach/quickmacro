"""
Base UI styling and components for PyQt6.
"""

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QPushButton,
    QLabel,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QSplitter,
    QStatusBar,
    QMenuBar,
    QToolBar,
    QGroupBox,
    QGridLayout,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QAction
import logging

logger = logging.getLogger(__name__)


class ModernStyle:
    """Modern PyQt6 styling constants and utilities."""

    # Modern color scheme (Windows 11 inspired but cleaner)
    COLORS = {
        # Background colors
        "bg_primary": "#fafafa",  # Main background
        "bg_secondary": "#ffffff",  # Card/panel background
        "bg_tertiary": "#f5f5f5",  # Elevated surfaces
        "bg_hover": "#f0f0f0",  # Hover states
        "bg_pressed": "#e8e8e8",  # Pressed states
        "bg_selected": "#0078d4",  # Selection blue
        "bg_disabled": "#f9f9f9",  # Disabled background
        # Text colors
        "text_primary": "#202020",  # Primary text
        "text_secondary": "#616161",  # Secondary text
        "text_tertiary": "#757575",  # Muted text
        "text_accent": "#0078d4",  # Accent text
        "text_on_accent": "#ffffff",  # Text on accent backgrounds
        "text_disabled": "#9e9e9e",  # Disabled text
        # Border colors
        "border_light": "#e0e0e0",  # Light borders
        "border_medium": "#d0d0d0",  # Medium borders
        "border_focus": "#0078d4",  # Focus borders
        # Status colors
        "success": "#0d7377",  # Success green
        "warning": "#f57c00",  # Warning orange
        "error": "#d32f2f",  # Error red
        "info": "#1976d2",  # Info blue
    }

    # Modern fonts
    FONTS = {
        "default": QFont("Segoe UI", 9),
        "large": QFont("Segoe UI", 11),
        "small": QFont("Segoe UI", 8),
        "title": QFont("Segoe UI", 12, QFont.Weight.DemiBold),
        "monospace": QFont("Consolas", 9),
    }

    # Spacing system
    SPACING = {
        "xs": 4,
        "sm": 8,
        "md": 16,
        "lg": 24,
        "xl": 32,
    }

    @staticmethod
    def get_stylesheet():
        """Get the main application stylesheet."""
        return f"""
        /* Main application styling */
        QMainWindow {{
            background-color: {ModernStyle.COLORS["bg_primary"]};
            color: {ModernStyle.COLORS["text_primary"]};
            margin: 0px;
            padding: 0px;
        }}
        
        /* Remove global widget styling that interferes with text colors */
        
        /* Panels and cards */
        QFrame[frameStyle="panel"] {{
            background-color: {ModernStyle.COLORS["bg_secondary"]};
            border: 1px solid {ModernStyle.COLORS["border_light"]};
            border-radius: 6px;
            padding: 8px;
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {ModernStyle.COLORS["bg_secondary"]};
            border: 1px solid {ModernStyle.COLORS["border_medium"]};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 9pt;
            color: {ModernStyle.COLORS["text_primary"]};
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background-color: {ModernStyle.COLORS["bg_hover"]};
            border-color: {ModernStyle.COLORS["border_focus"]};
        }}
        
        QPushButton:pressed {{
            background-color: {ModernStyle.COLORS["bg_pressed"]};
        }}
        
        QPushButton:disabled {{
            background-color: {ModernStyle.COLORS["bg_disabled"]};
            color: {ModernStyle.COLORS["text_disabled"]};
            border-color: {ModernStyle.COLORS["border_light"]};
        }}
        
        /* Primary button variant */
        QPushButton[buttonStyle="primary"] {{
            background-color: {ModernStyle.COLORS["bg_selected"]};
            color: {ModernStyle.COLORS["text_on_accent"]};
            border: 1px solid {ModernStyle.COLORS["bg_selected"]};
        }}
        
        QPushButton[buttonStyle="primary"]:hover {{
            background-color: #106ebe;
            border-color: #106ebe;
        }}
        
        /* Tab widget */
        QTabWidget::pane {{
            border: 1px solid {ModernStyle.COLORS["border_light"]};
            background-color: {ModernStyle.COLORS["bg_secondary"]};
            border-radius: 4px;
        }}
        
        QTabWidget::tab-bar {{
            alignment: left;
        }}
        
        QTabBar::tab {{
            background-color: {ModernStyle.COLORS["bg_tertiary"]};
            color: {ModernStyle.COLORS["text_secondary"]};
            border: 1px solid {ModernStyle.COLORS["border_light"]};
            border-bottom: none;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {ModernStyle.COLORS["bg_secondary"]};
            color: {ModernStyle.COLORS["text_primary"]};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {ModernStyle.COLORS["bg_hover"]};
        }}
        
        /* Group boxes */
        QGroupBox {{
            font-weight: 500;
            color: {ModernStyle.COLORS["text_primary"]};
            border: 1px solid {ModernStyle.COLORS["border_light"]};
            border-radius: 6px;
            margin-top: 8px;
            padding-top: 8px;
            background-color: transparent;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px 0 4px;
            background-color: {ModernStyle.COLORS["bg_primary"]};
        }}
        
        /* Tree widget */
        QTreeWidget {{
            background-color: {ModernStyle.COLORS["bg_secondary"]};
            alternate-background-color: {ModernStyle.COLORS["bg_tertiary"]};
            border: 1px solid {ModernStyle.COLORS["border_light"]};
            border-radius: 4px;
            selection-background-color: {ModernStyle.COLORS["bg_selected"]};
            selection-color: {ModernStyle.COLORS["text_on_accent"]};
            color: {ModernStyle.COLORS["text_primary"]};
        }}
        
        QTreeWidget::item {{
            padding: 4px;
            border: none;
            color: {ModernStyle.COLORS["text_primary"]};
        }}
        
        QTreeWidget::item:hover {{
            background-color: {ModernStyle.COLORS["bg_hover"]};
        }}
        
        QHeaderView::section {{
            background-color: {ModernStyle.COLORS["bg_tertiary"]};
            border: 1px solid {ModernStyle.COLORS["border_light"]};
            padding: 6px 8px;
            font-weight: 500;
        }}
        
        /* Text edit */
        QTextEdit {{
            background-color: {ModernStyle.COLORS["bg_secondary"]};
            border: 1px solid {ModernStyle.COLORS["border_light"]};
            border-radius: 4px;
            padding: 8px;
            selection-background-color: {ModernStyle.COLORS["bg_selected"]};
            selection-color: {ModernStyle.COLORS["text_on_accent"]};
            color: {ModernStyle.COLORS["text_primary"]};
        }}
        
        /* Status bar */
        QStatusBar {{
            background-color: {ModernStyle.COLORS["bg_tertiary"]};
            border-top: 1px solid {ModernStyle.COLORS["border_light"]};
            padding: 4px 8px;
        }}
        
        /* Toolbar */
        QToolBar {{
            background-color: {ModernStyle.COLORS["bg_secondary"]};
            border-bottom: 1px solid {ModernStyle.COLORS["border_light"]};
            spacing: 4px;
            padding: 4px;
        }}
        
        QToolBar QPushButton {{
            border: none;
            border-radius: 3px;
            padding: 6px 12px;
            margin: 1px;
        }}
        
        /* Labels */
        QLabel {{
            color: {ModernStyle.COLORS["text_primary"]};
        }}
        
        QLabel[labelStyle="secondary"] {{
            color: {ModernStyle.COLORS["text_secondary"]};
        }}
        
        QLabel[labelStyle="muted"] {{
            color: {ModernStyle.COLORS["text_tertiary"]};
        }}
        """


class BaseWindow(QMainWindow):
    """Base window class with modern PyQt6 styling."""

    def __init__(self, title="Application", width=800, height=600):
        super().__init__()

        self.setWindowTitle(title)
        self.setMinimumSize(QSize(640, 480))
        self.resize(width, height)

        # Apply modern styling
        self.setStyleSheet(ModernStyle.get_stylesheet())

        # Set font
        self.setFont(ModernStyle.FONTS["default"])

        # Central widget
        self.central_widget = QWidget()
        self.central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.central_widget)

        logger.info(f"PyQt6 modern window created: {title}")


class ModernCard(QFrame):
    """A modern card-style container."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)

        # Set frame style for styling
        self.setProperty("frameStyle", "panel")

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            ModernStyle.SPACING["md"],
            ModernStyle.SPACING["md"],
            ModernStyle.SPACING["md"],
            ModernStyle.SPACING["md"],
        )
        layout.setSpacing(ModernStyle.SPACING["sm"])

        # Title if provided
        if title:
            title_label = QLabel(title)
            title_label.setFont(ModernStyle.FONTS["title"])
            layout.addWidget(title_label)

        # Content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(ModernStyle.SPACING["sm"])
        layout.addLayout(self.content_layout)

    def add_widget(self, widget):
        """Add a widget to the card content."""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """Add a layout to the card content."""
        self.content_layout.addLayout(layout)


class ModernButton(QPushButton):
    """A modern styled button."""

    def __init__(self, text: str, style: str = "default", parent=None):
        super().__init__(text, parent)

        if style == "primary":
            self.setProperty("buttonStyle", "primary")

        self.setFont(ModernStyle.FONTS["default"])


class StatusIndicator(QLabel):
    """A status indicator with colored dot."""

    def __init__(self, status: str = "normal", parent=None):
        super().__init__(parent)
        self.status = status
        self.update_status(status)

    def update_status(self, status: str):
        """Update the status indicator."""
        self.status = status

        colors = {
            "success": ModernStyle.COLORS["success"],
            "warning": ModernStyle.COLORS["warning"],
            "error": ModernStyle.COLORS["error"],
            "info": ModernStyle.COLORS["info"],
            "normal": ModernStyle.COLORS["text_tertiary"],
        }

        color = colors.get(status, colors["normal"])
        self.setText("●")
        self.setStyleSheet(f"color: {color}; font-size: 12px;")
        self.setToolTip(f"Status: {status.title()}")
