import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
import os
from PIL import Image, ImageTk
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)


class Windows11Style:
    """Windows 11 Fluent Design styling constants and utilities."""

    # Windows 11 Color System
    COLORS = {
        # Light theme (Windows 11 default)
        "bg_primary": "#f3f3f3",  # System background
        "bg_secondary": "#ffffff",  # Card/surface background
        "bg_tertiary": "#fafafa",  # Elevated surfaces
        "bg_hover": "#f6f6f6",  # Hover states
        "bg_pressed": "#ebebeb",  # Pressed states
        # Windows 11 Accent colors (blue by default)
        "accent": "#0078d4",  # System accent
        "accent_light": "#106ebe",  # Light accent
        "accent_hover": "#005a9e",  # Hover accent
        "accent_disabled": "#c7e0f4",  # Disabled accent
        # Text colors
        "text_primary": "#323130",  # Primary text
        "text_secondary": "#605e5c",  # Secondary text
        "text_tertiary": "#8a8886",  # Tertiary/muted text
        "text_accent": "#0078d4",  # Accent text
        "text_on_accent": "#ffffff",  # Text on accent backgrounds
        # Border and stroke
        "stroke_primary": "#d1d1d1",  # Primary borders
        "stroke_secondary": "#e1dfdd",  # Secondary borders
        "stroke_accent": "#0078d4",  # Accent borders
        "stroke_focus": "#0078d4",  # Focus indicators
        # Status colors
        "success": "#107c10",  # Success green
        "warning": "#faa81a",  # Warning amber
        "error": "#d83b01",  # Error red
        "info": "#0078d4",  # Info blue
        # Card shadows and effects
        "shadow_light": "rgba(0, 0, 0, 0.05)",
        "shadow_medium": "rgba(0, 0, 0, 0.1)",
    }

    # Windows 11 Typography (Segoe UI Variable)
    FONTS = {
        "display": ("Segoe UI Variable Display", 28, "normal"),
        "title_large": ("Segoe UI Variable Display", 22, "normal"),
        "title": ("Segoe UI Variable Display", 18, "normal"),
        "subtitle": ("Segoe UI Variable Text", 16, "normal"),
        "body_large": ("Segoe UI Variable Text", 14, "normal"),
        "body": ("Segoe UI Variable Text", 13, "normal"),
        "body_small": ("Segoe UI Variable Text", 12, "normal"),
        "caption": ("Segoe UI Variable Text", 11, "normal"),
        "code": ("Cascadia Code", 12, "normal"),  # Windows Terminal font
    }

    # Windows 11 Spacing (8px grid system)
    SPACING = {
        "xs": 4,  # 0.5 units
        "sm": 8,  # 1 unit
        "md": 16,  # 2 units
        "lg": 24,  # 3 units
        "xl": 32,  # 4 units
        "xxl": 48,  # 6 units
    }

    # Border radius for rounded corners
    RADIUS = {"small": 4, "medium": 8, "large": 12}

    @staticmethod
    def configure_styles():
        """Configure TTK styles for Windows 11 look."""
        style = ttk.Style()

        # Use modern theme as base
        style.theme_use("vista" if "vista" in style.theme_names() else "clam")

        # Configure main containers
        style.configure(
            "Win11.TFrame",
            background=Windows11Style.COLORS["bg_primary"],
            relief="flat",
            borderwidth=0,
        )

        style.configure(
            "Win11Card.TFrame",
            background=Windows11Style.COLORS["bg_secondary"],
            relief="flat",
            borderwidth=1,
        )

        # Notebook (Tab control) styling
        style.configure(
            "Win11.TNotebook",
            background=Windows11Style.COLORS["bg_primary"],
            borderwidth=0,
            tabmargins=[0, 0, 0, 0],
        )

        style.configure(
            "Win11.TNotebook.Tab",
            background=Windows11Style.COLORS["bg_tertiary"],
            foreground=Windows11Style.COLORS["text_secondary"],
            padding=[16, 12, 16, 12],
            borderwidth=0,
            focuscolor="none",
            font=Windows11Style.FONTS["body"],
        )

        style.map(
            "Win11.TNotebook.Tab",
            background=[
                ("selected", Windows11Style.COLORS["bg_secondary"]),
                ("active", Windows11Style.COLORS["bg_hover"]),
            ],
            foreground=[
                ("selected", Windows11Style.COLORS["text_primary"]),
                ("active", Windows11Style.COLORS["text_primary"]),
            ],
        )

        # Labels
        style.configure(
            "Win11Title.TLabel",
            background=Windows11Style.COLORS["bg_secondary"],
            foreground=Windows11Style.COLORS["text_primary"],
            font=Windows11Style.FONTS["title"],
        )

        style.configure(
            "Win11Subtitle.TLabel",
            background=Windows11Style.COLORS["bg_secondary"],
            foreground=Windows11Style.COLORS["text_secondary"],
            font=Windows11Style.FONTS["subtitle"],
        )

        style.configure(
            "Win11Body.TLabel",
            background=Windows11Style.COLORS["bg_secondary"],
            foreground=Windows11Style.COLORS["text_primary"],
            font=Windows11Style.FONTS["body"],
        )

        style.configure(
            "Win11Caption.TLabel",
            background=Windows11Style.COLORS["bg_secondary"],
            foreground=Windows11Style.COLORS["text_tertiary"],
            font=Windows11Style.FONTS["caption"],
        )

        # Status labels
        style.configure(
            "Win11Success.TLabel",
            background=Windows11Style.COLORS["bg_secondary"],
            foreground=Windows11Style.COLORS["success"],
            font=Windows11Style.FONTS["body"],
        )

        style.configure(
            "Win11Warning.TLabel",
            background=Windows11Style.COLORS["bg_secondary"],
            foreground=Windows11Style.COLORS["warning"],
            font=Windows11Style.FONTS["body"],
        )

        style.configure(
            "Win11Error.TLabel",
            background=Windows11Style.COLORS["bg_secondary"],
            foreground=Windows11Style.COLORS["error"],
            font=Windows11Style.FONTS["body"],
        )

        # Buttons
        style.configure(
            "Win11.TButton",
            background=Windows11Style.COLORS["bg_secondary"],
            foreground=Windows11Style.COLORS["text_primary"],
            borderwidth=1,
            relief="flat",
            focuscolor="none",
            padding=[16, 8, 16, 8],
            font=Windows11Style.FONTS["body"],
        )

        style.map(
            "Win11.TButton",
            background=[
                ("active", Windows11Style.COLORS["bg_hover"]),
                ("pressed", Windows11Style.COLORS["bg_pressed"]),
            ],
        )

        style.configure(
            "Win11Accent.TButton",
            background=Windows11Style.COLORS["accent"],
            foreground=Windows11Style.COLORS["text_on_accent"],
            borderwidth=0,
            relief="flat",
            focuscolor="none",
            padding=[16, 8, 16, 8],
            font=Windows11Style.FONTS["body"],
        )

        style.map(
            "Win11Accent.TButton",
            background=[
                ("active", Windows11Style.COLORS["accent_hover"]),
                ("pressed", Windows11Style.COLORS["accent_light"]),
            ],
        )

        # LabelFrame
        style.configure(
            "Win11.TLabelframe",
            background=Windows11Style.COLORS["bg_secondary"],
            borderwidth=1,
            relief="flat",
        )

        style.configure(
            "Win11.TLabelframe.Label",
            background=Windows11Style.COLORS["bg_secondary"],
            foreground=Windows11Style.COLORS["text_secondary"],
            font=Windows11Style.FONTS["body_large"],
        )

        # Treeview
        style.configure(
            "Win11.Treeview",
            background=Windows11Style.COLORS["bg_secondary"],
            foreground=Windows11Style.COLORS["text_primary"],
            fieldbackground=Windows11Style.COLORS["bg_secondary"],
            borderwidth=1,
            relief="flat",
            font=Windows11Style.FONTS["body"],
        )

        style.configure(
            "Win11.Treeview.Heading",
            background=Windows11Style.COLORS["bg_tertiary"],
            foreground=Windows11Style.COLORS["text_secondary"],
            borderwidth=0,
            relief="flat",
            font=Windows11Style.FONTS["body_large"],
        )

        style.map(
            "Win11.Treeview",
            background=[("selected", Windows11Style.COLORS["accent_disabled"])],
            foreground=[("selected", Windows11Style.COLORS["text_primary"])],
        )


class StatusCard(tk.Frame):
    """A Windows 11 style status card with icon and information."""

    def __init__(
        self,
        parent,
        title: str,
        value: str = "--",
        status: str = "neutral",
        icon: str = "",
    ):
        super().__init__(
            parent,
            bg=Windows11Style.COLORS["bg_secondary"],
            relief="flat",
            bd=1,
            highlightthickness=0,
        )

        self.title = title
        self.value = value
        self.status = status
        self.icon = icon

        # Configure card styling
        self.configure(highlightbackground=Windows11Style.COLORS["stroke_secondary"])

        self._create_widgets()

    def _create_widgets(self):
        """Create the status card widgets."""
        # Main container with padding
        container = tk.Frame(self, bg=Windows11Style.COLORS["bg_secondary"])
        container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=Windows11Style.SPACING["md"],
            pady=Windows11Style.SPACING["md"],
        )

        # Header with icon and title
        header = tk.Frame(container, bg=Windows11Style.COLORS["bg_secondary"])
        header.pack(fill=tk.X, pady=(0, Windows11Style.SPACING["sm"]))

        # Icon
        if self.icon:
            icon_label = tk.Label(
                header,
                text=self.icon,
                bg=Windows11Style.COLORS["bg_secondary"],
                fg=Windows11Style.COLORS["text_secondary"],
                font=("Segoe UI Emoji", 16),
            )
            icon_label.pack(side=tk.LEFT, padx=(0, Windows11Style.SPACING["sm"]))

        # Title
        title_label = tk.Label(
            header,
            text=self.title,
            bg=Windows11Style.COLORS["bg_secondary"],
            fg=Windows11Style.COLORS["text_secondary"],
            font=Windows11Style.FONTS["caption"],
            anchor="w",
        )
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Status indicator (small circle)
        self.status_indicator = tk.Label(
            header,
            text="●",
            bg=Windows11Style.COLORS["bg_secondary"],
            fg=Windows11Style.COLORS["text_tertiary"],
            font=("Segoe UI", 8),
        )
        self.status_indicator.pack(side=tk.RIGHT)

        # Value
        self.value_label = tk.Label(
            container,
            text=self.value,
            bg=Windows11Style.COLORS["bg_secondary"],
            fg=Windows11Style.COLORS["text_primary"],
            font=Windows11Style.FONTS["body_large"],
            anchor="w",
        )
        self.value_label.pack(fill=tk.X)

    def update_status(self, value: str, status: str = "neutral"):
        """Update the status card."""
        self.value = value
        self.status = status

        # Update value text
        self.value_label.config(text=value)

        # Update status indicator color
        colors = {
            "success": Windows11Style.COLORS["success"],
            "warning": Windows11Style.COLORS["warning"],
            "error": Windows11Style.COLORS["error"],
            "info": Windows11Style.COLORS["info"],
            "neutral": Windows11Style.COLORS["text_tertiary"],
        }
        self.status_indicator.config(fg=colors.get(status, colors["neutral"]))


class FluentButton(tk.Button):
    """A Windows 11 Fluent Design button with proper styling."""

    def __init__(
        self,
        parent,
        text: str,
        command: Callable,
        style: str = "default",
        icon: str = "",
    ):

        if style == "accent":
            bg = Windows11Style.COLORS["accent"]
            fg = Windows11Style.COLORS["text_on_accent"]
            hover_bg = Windows11Style.COLORS["accent_hover"]
            border_color = Windows11Style.COLORS["accent"]
        else:
            bg = Windows11Style.COLORS["bg_secondary"]
            fg = Windows11Style.COLORS["text_primary"]
            hover_bg = Windows11Style.COLORS["bg_hover"]
            border_color = Windows11Style.COLORS["stroke_primary"]

        # Add icon to text if provided
        display_text = f"{icon} {text}" if icon else text

        super().__init__(
            parent,
            text=display_text,
            command=command,
            bg=bg,
            fg=fg,
            font=Windows11Style.FONTS["body"],
            relief="flat",
            borderwidth=1,
            cursor="hand2",
            padx=Windows11Style.SPACING["md"],
            pady=Windows11Style.SPACING["sm"],
            highlightthickness=0,
            bd=1,
        )

        # Configure border
        self.configure(highlightbackground=border_color, highlightcolor=border_color)

        self.default_bg = bg
        self.hover_bg = hover_bg
        self.border_color = border_color

        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        """Handle mouse enter."""
        self.config(bg=self.hover_bg)

    def _on_leave(self, event):
        """Handle mouse leave."""
        self.config(bg=self.default_bg)


class MainWindow:
    def __init__(self, title: str = "QuickMacro"):
        self.title = title
        self.root = None
        self.visible = False

        # Callbacks
        self.on_close_callback = None
        self.on_minimize_callback = None

        # UI Components
        self.status_frame = None
        self.hotkey_frame = None
        self.log_frame = None
        self.status_cards = {}
        self.hotkey_tree = None
        self.log_text = None

        # Data
        self.hotkeys = {}
        self.system_status = {}

        # Icon
        self.icon_image = None

    def load_icon(self) -> bool:
        """Load icon from assets folder."""
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
                    if icon_path.endswith(".ico"):
                        self.icon_image = icon_path
                        logger.info(f"Loaded icon from: {icon_path}")
                        return True
                    else:
                        image = Image.open(icon_path)
                        image = image.resize((32, 32), Image.Resampling.LANCZOS)
                        self.icon_image = ImageTk.PhotoImage(image)
                        logger.info(f"Loaded icon from: {icon_path}")
                        return True
            except Exception as e:
                logger.warning(f"Failed to load icon from {icon_path}: {e}")
                continue

        logger.warning("No icon found in assets folder")
        return False

    def create_window(self):
        """Create the main window with Windows 11 styling."""
        if self.root is not None:
            return

        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Configure Windows 11 styling
        Windows11Style.configure_styles()

        # Set window background to Windows 11 system color
        self.root.configure(bg=Windows11Style.COLORS["bg_primary"])

        # Load and set icon
        if self.load_icon():
            try:
                if isinstance(self.icon_image, str):
                    self.root.iconbitmap(self.icon_image)
                else:
                    self.root.iconphoto(True, self.icon_image)
            except Exception as e:
                logger.warning(f"Failed to set window icon: {e}")

        # Configure window close behavior
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Hide window initially
        self.root.withdraw()

        # Create UI components
        self._create_title_bar()
        self._create_content()

        # Show welcome message
        self._show_welcome_message()

        logger.info("Windows 11 style main window created")

    def _create_title_bar(self):
        """Create the custom title bar area."""
        title_bar = tk.Frame(
            self.root, bg=Windows11Style.COLORS["bg_secondary"], height=60
        )
        title_bar.pack(fill=tk.X, padx=0, pady=0)
        title_bar.pack_propagate(False)

        # Add a subtle border at bottom
        border = tk.Frame(
            title_bar, bg=Windows11Style.COLORS["stroke_secondary"], height=1
        )
        border.pack(side=tk.BOTTOM, fill=tk.X)

        # Title bar content
        title_content = tk.Frame(title_bar, bg=Windows11Style.COLORS["bg_secondary"])
        title_content.pack(
            fill=tk.BOTH,
            expand=True,
            padx=Windows11Style.SPACING["lg"],
            pady=Windows11Style.SPACING["md"],
        )

        # App icon and title
        app_info = tk.Frame(title_content, bg=Windows11Style.COLORS["bg_secondary"])
        app_info.pack(side=tk.LEFT, fill=tk.Y)

        # App title
        title_label = tk.Label(
            app_info,
            text="QuickMacro",
            bg=Windows11Style.COLORS["bg_secondary"],
            fg=Windows11Style.COLORS["text_primary"],
            font=Windows11Style.FONTS["title"],
        )
        title_label.pack(anchor="w")

        # Subtitle
        subtitle_label = tk.Label(
            app_info,
            text="Global hotkeys and system actions",
            bg=Windows11Style.COLORS["bg_secondary"],
            fg=Windows11Style.COLORS["text_secondary"],
            font=Windows11Style.FONTS["caption"],
        )
        subtitle_label.pack(anchor="w")

        # Action buttons
        actions = tk.Frame(title_content, bg=Windows11Style.COLORS["bg_secondary"])
        actions.pack(side=tk.RIGHT, fill=tk.Y)

        # Settings button
        settings_btn = FluentButton(
            actions, "Settings", self._show_settings, "default", "⚙️"
        )
        settings_btn.pack(side=tk.RIGHT, padx=(Windows11Style.SPACING["sm"], 0))

        # Hide button
        hide_btn = FluentButton(actions, "Hide to tray", self.hide, "default", "🔽")
        hide_btn.pack(side=tk.RIGHT, padx=(Windows11Style.SPACING["sm"], 0))

    def _create_content(self):
        """Create the main content area."""
        # Content container with Windows 11 padding
        content_frame = tk.Frame(self.root, bg=Windows11Style.COLORS["bg_primary"])
        content_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=Windows11Style.SPACING["lg"],
            pady=Windows11Style.SPACING["lg"],
        )

        # Create notebook for tabs
        self.notebook = ttk.Notebook(content_frame, style="Win11.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self._create_status_tab(self.notebook)
        self._create_hotkeys_tab(self.notebook)
        self._create_logs_tab(self.notebook)

    def _create_status_tab(self, parent):
        """Create the Windows 11 style status tab."""
        self.status_frame = ttk.Frame(parent, style="Win11.TFrame")
        parent.add(self.status_frame, text="Status")

        # Main container
        main_container = tk.Frame(
            self.status_frame, bg=Windows11Style.COLORS["bg_primary"]
        )
        main_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=Windows11Style.SPACING["md"],
            pady=Windows11Style.SPACING["md"],
        )

        # Status cards section
        status_section = tk.Frame(
            main_container, bg=Windows11Style.COLORS["bg_secondary"]
        )
        status_section.pack(fill=tk.X, pady=(0, Windows11Style.SPACING["lg"]))

        # Add subtle border
        status_section.configure(
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground=Windows11Style.COLORS["stroke_secondary"],
        )

        # Section header
        header = tk.Frame(status_section, bg=Windows11Style.COLORS["bg_secondary"])
        header.pack(
            fill=tk.X,
            padx=Windows11Style.SPACING["lg"],
            pady=(Windows11Style.SPACING["lg"], Windows11Style.SPACING["md"]),
        )

        tk.Label(
            header,
            text="System status",
            bg=Windows11Style.COLORS["bg_secondary"],
            fg=Windows11Style.COLORS["text_primary"],
            font=Windows11Style.FONTS["body_large"],
        ).pack(side=tk.LEFT)

        # Refresh button
        refresh_btn = FluentButton(
            header, "Refresh", self._refresh_status, "default", "🔄"
        )
        refresh_btn.pack(side=tk.RIGHT)

        # Status cards grid
        cards_frame = tk.Frame(status_section, bg=Windows11Style.COLORS["bg_secondary"])
        cards_frame.pack(
            fill=tk.X,
            padx=Windows11Style.SPACING["lg"],
            pady=(0, Windows11Style.SPACING["lg"]),
        )

        # Create status cards
        self.status_cards["volume"] = StatusCard(
            cards_frame, "System volume", "--", "neutral", "🔊"
        )
        self.status_cards["volume"].pack(
            fill=tk.X, pady=(0, Windows11Style.SPACING["sm"])
        )

        self.status_cards["muted"] = StatusCard(
            cards_frame, "Audio status", "--", "neutral", "🔇"
        )
        self.status_cards["muted"].pack(
            fill=tk.X, pady=(0, Windows11Style.SPACING["sm"])
        )

        self.status_cards["active_window"] = StatusCard(
            cards_frame, "Active window", "--", "neutral", "🪟"
        )
        self.status_cards["active_window"].pack(fill=tk.X)

        # Quick actions section
        actions_section = tk.Frame(
            main_container, bg=Windows11Style.COLORS["bg_secondary"]
        )
        actions_section.pack(fill=tk.X)

        # Add subtle border
        actions_section.configure(
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground=Windows11Style.COLORS["stroke_secondary"],
        )

        # Section header
        actions_header = tk.Frame(
            actions_section, bg=Windows11Style.COLORS["bg_secondary"]
        )
        actions_header.pack(
            fill=tk.X,
            padx=Windows11Style.SPACING["lg"],
            pady=(Windows11Style.SPACING["lg"], Windows11Style.SPACING["md"]),
        )

        tk.Label(
            actions_header,
            text="Quick actions",
            bg=Windows11Style.COLORS["bg_secondary"],
            fg=Windows11Style.COLORS["text_primary"],
            font=Windows11Style.FONTS["body_large"],
        ).pack(side=tk.LEFT)

        # Action buttons
        actions_container = tk.Frame(
            actions_section, bg=Windows11Style.COLORS["bg_secondary"]
        )
        actions_container.pack(
            fill=tk.X,
            padx=Windows11Style.SPACING["lg"],
            pady=(0, Windows11Style.SPACING["lg"]),
        )

        # Primary actions row
        primary_actions = tk.Frame(
            actions_container, bg=Windows11Style.COLORS["bg_secondary"]
        )
        primary_actions.pack(fill=tk.X, pady=(0, Windows11Style.SPACING["sm"]))

        FluentButton(
            primary_actions,
            "Toggle system mute",
            lambda: self._quick_action("toggle_system_mute"),
            "accent",
            "🔇",
        ).pack(side=tk.LEFT, padx=(0, Windows11Style.SPACING["sm"]))

        FluentButton(
            primary_actions,
            "Toggle app mute",
            lambda: self._quick_action("toggle_active_app_mute"),
            "default",
            "🎵",
        ).pack(side=tk.LEFT, padx=(0, Windows11Style.SPACING["sm"]))

        FluentButton(
            primary_actions,
            "Lock screen",
            lambda: self._quick_action("lock_screen"),
            "default",
            "🔒",
        ).pack(side=tk.LEFT)

        # Secondary actions
        secondary_actions = tk.Frame(
            actions_container, bg=Windows11Style.COLORS["bg_secondary"]
        )
        secondary_actions.pack(fill=tk.X)

        FluentButton(
            secondary_actions,
            "List audio sessions",
            lambda: self._quick_action("list_audio_sessions"),
            "default",
            "📋",
        ).pack(side=tk.LEFT)

    def _create_hotkeys_tab(self, parent):
        """Create the Windows 11 style hotkeys tab."""
        self.hotkey_frame = ttk.Frame(parent, style="Win11.TFrame")
        parent.add(self.hotkey_frame, text="Hotkeys")

        # Main container
        main_container = tk.Frame(
            self.hotkey_frame, bg=Windows11Style.COLORS["bg_primary"]
        )
        main_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=Windows11Style.SPACING["md"],
            pady=Windows11Style.SPACING["md"],
        )

        # Section
        hotkeys_section = tk.Frame(
            main_container, bg=Windows11Style.COLORS["bg_secondary"]
        )
        hotkeys_section.pack(fill=tk.BOTH, expand=True)

        # Add subtle border
        hotkeys_section.configure(
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground=Windows11Style.COLORS["stroke_secondary"],
        )

        # Section header
        header = tk.Frame(hotkeys_section, bg=Windows11Style.COLORS["bg_secondary"])
        header.pack(
            fill=tk.X,
            padx=Windows11Style.SPACING["lg"],
            pady=(Windows11Style.SPACING["lg"], Windows11Style.SPACING["md"]),
        )

        tk.Label(
            header,
            text="Registered hotkeys",
            bg=Windows11Style.COLORS["bg_secondary"],
            fg=Windows11Style.COLORS["text_primary"],
            font=Windows11Style.FONTS["body_large"],
        ).pack(side=tk.LEFT)

        # Refresh button
        refresh_btn = FluentButton(
            header, "Refresh", self._refresh_hotkeys, "default", "🔄"
        )
        refresh_btn.pack(side=tk.RIGHT)

        # Hotkeys list container
        list_container = tk.Frame(
            hotkeys_section, bg=Windows11Style.COLORS["bg_secondary"]
        )
        list_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=Windows11Style.SPACING["lg"],
            pady=(0, Windows11Style.SPACING["lg"]),
        )

        # Create treeview with Windows 11 styling
        columns = ("Hotkey", "Action", "Description")
        self.hotkey_tree = ttk.Treeview(
            list_container,
            columns=columns,
            show="headings",
            style="Win11.Treeview",
            height=15,
        )

        # Define column headings and widths
        self.hotkey_tree.heading("Hotkey", text="Hotkey combination")
        self.hotkey_tree.heading("Action", text="Action")
        self.hotkey_tree.heading("Description", text="Description")

        self.hotkey_tree.column("Hotkey", width=200, minwidth=150)
        self.hotkey_tree.column("Action", width=200, minwidth=150)
        self.hotkey_tree.column("Description", width=350, minwidth=250)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_container, orient=tk.VERTICAL, command=self.hotkey_tree.yview
        )
        self.hotkey_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.hotkey_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_logs_tab(self, parent):
        """Create the Windows 11 style logs tab."""
        self.log_frame = ttk.Frame(parent, style="Win11.TFrame")
        parent.add(self.log_frame, text="Logs")

        # Main container
        main_container = tk.Frame(
            self.log_frame, bg=Windows11Style.COLORS["bg_primary"]
        )
        main_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=Windows11Style.SPACING["md"],
            pady=Windows11Style.SPACING["md"],
        )

        # Log section
        log_section = tk.Frame(main_container, bg=Windows11Style.COLORS["bg_secondary"])
        log_section.pack(fill=tk.BOTH, expand=True)

        # Add subtle border
        log_section.configure(
            relief="flat",
            bd=1,
            highlightthickness=1,
            highlightbackground=Windows11Style.COLORS["stroke_secondary"],
        )

        # Section header
        header = tk.Frame(log_section, bg=Windows11Style.COLORS["bg_secondary"])
        header.pack(
            fill=tk.X,
            padx=Windows11Style.SPACING["lg"],
            pady=(Windows11Style.SPACING["lg"], Windows11Style.SPACING["md"]),
        )

        tk.Label(
            header,
            text="Application logs",
            bg=Windows11Style.COLORS["bg_secondary"],
            fg=Windows11Style.COLORS["text_primary"],
            font=Windows11Style.FONTS["body_large"],
        ).pack(side=tk.LEFT)

        # Log controls
        controls = tk.Frame(header, bg=Windows11Style.COLORS["bg_secondary"])
        controls.pack(side=tk.RIGHT)

        FluentButton(controls, "Clear", self._clear_log, "default", "🗑️").pack(
            side=tk.RIGHT, padx=(Windows11Style.SPACING["sm"], 0)
        )
        FluentButton(controls, "Refresh", self._refresh_log, "default", "🔄").pack(
            side=tk.RIGHT
        )

        # Log text area container
        log_container = tk.Frame(log_section, bg=Windows11Style.COLORS["bg_secondary"])
        log_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=Windows11Style.SPACING["lg"],
            pady=(0, Windows11Style.SPACING["lg"]),
        )

        # Log text area with Windows 11 styling
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            bg=Windows11Style.COLORS["bg_tertiary"],
            fg=Windows11Style.COLORS["text_primary"],
            font=Windows11Style.FONTS["code"],
            relief="flat",
            borderwidth=1,
            selectbackground=Windows11Style.COLORS["accent_disabled"],
            selectforeground=Windows11Style.COLORS["text_primary"],
            wrap=tk.WORD,
            highlightthickness=1,
            highlightbackground=Windows11Style.COLORS["stroke_secondary"],
            insertbackground=Windows11Style.COLORS["text_primary"],
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _show_welcome_message(self):
        """Show Windows 11 style welcome message."""
        if self.root:
            self.root.after(1000, self._display_welcome)

    def _display_welcome(self):
        """Display the welcome message."""
        # Add welcome messages to log
        self.add_log_message("Welcome to QuickMacro!")
        self.add_log_message("Your hotkey manager is running in the background")
        self.add_log_message("Use Ctrl+Shift+H to show/hide this window")
        self.add_log_message("Check the status tab for system information")

    def _on_close(self):
        """Handle window close event."""
        if self.on_close_callback:
            self.on_close_callback()
        else:
            self.hide()

    def _show_settings(self):
        """Show settings dialog."""
        messagebox.showinfo(
            "Settings",
            "Settings dialog would open here.\nThis feature will be implemented in the settings window.",
        )

    def _refresh_status(self):
        """Refresh system status display."""
        if hasattr(self, "refresh_status_callback") and self.refresh_status_callback:
            self.refresh_status_callback()

    def _refresh_hotkeys(self):
        """Refresh hotkeys display."""
        if hasattr(self, "refresh_hotkeys_callback") and self.refresh_hotkeys_callback:
            self.refresh_hotkeys_callback()

    def _refresh_log(self):
        """Refresh log display."""
        self.add_log_message("Log refreshed")

    def _clear_log(self):
        """Clear the log display."""
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
            self.add_log_message("Log cleared")

    def _quick_action(self, action_name: str):
        """Execute a quick action."""
        if hasattr(self, "quick_action_callback") and self.quick_action_callback:
            self.quick_action_callback(action_name)

    def show(self):
        """Show the window."""
        if self.root is None:
            self.create_window()
        self.root.after_idle(self._show_window)

    def _show_window(self):
        """Internal method to show window on main thread."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.visible = True
        logger.info("Main window shown")

    def hide(self):
        """Hide the window."""
        if self.root:
            self.root.after_idle(self._hide_window)

    def _hide_window(self):
        """Internal method to hide window on main thread."""
        self.root.withdraw()
        self.visible = False
        logger.info("Main window hidden")

    def toggle_visibility(self):
        """Toggle window visibility."""
        if self.root:
            self.root.after_idle(self._toggle_visibility)

    def _toggle_visibility(self):
        """Internal method to toggle visibility on main thread."""
        if self.visible:
            self._hide_window()
        else:
            self._show_window()

    def update_status(self, status: Dict[str, Any]):
        """Update the status display."""
        self.system_status = status
        if self.root and self.status_cards:
            self.root.after_idle(self._update_status_display, status)

    def _update_status_display(self, status: Dict[str, Any]):
        """Internal method to update status display on main thread."""
        if self.status_cards:
            # Volume card
            volume = status.get("system_volume", 0)
            volume_text = f"{volume:.0%}"
            volume_status = "success" if volume > 0 else "warning"
            self.status_cards["volume"].update_status(volume_text, volume_status)

            # Muted card
            muted = status.get("system_muted", False)
            muted_text = "Muted" if muted else "Unmuted"
            muted_status = "warning" if muted else "success"
            self.status_cards["muted"].update_status(muted_text, muted_status)

            # Active window card
            active_window = status.get("active_window", "Unknown")
            if len(active_window) > 60:
                active_window = active_window[:57] + "..."
            self.status_cards["active_window"].update_status(active_window, "info")

    def update_hotkeys(self, hotkeys: Dict[str, str]):
        """Update the hotkeys display."""
        self.hotkeys = hotkeys
        if self.root and self.hotkey_tree:
            self.root.after_idle(self._update_hotkeys_display, hotkeys)

    def _update_hotkeys_display(self, hotkeys: Dict[str, str]):
        """Internal method to update hotkeys display on main thread."""
        if self.hotkey_tree:
            # Clear existing items
            for item in self.hotkey_tree.get_children():
                self.hotkey_tree.delete(item)

            # Action descriptions
            action_descriptions = {
                "toggle_system_mute": "Toggle system-wide audio mute",
                "toggle_active_app_mute": "Toggle active application audio mute",
                "lock_screen": "Lock the Windows screen",
                "toggle_main_window": "Show/hide QuickMacro window",
            }

            # Add new items with descriptions
            for hotkey, action in hotkeys.items():
                description = action_descriptions.get(action, "Custom action")
                self.hotkey_tree.insert(
                    "", tk.END, values=(hotkey, action, description)
                )

    def add_log_message(self, message: str):
        """Add a message to the log display."""
        if self.root and self.log_text:
            self.root.after_idle(self._add_log_message_display, message)

    def _add_log_message_display(self, message: str):
        """Internal method to add log message on main thread."""
        if self.log_text:
            # Add timestamp
            import datetime

            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"

            self.log_text.insert(tk.END, formatted_message)
            self.log_text.see(tk.END)

            # Limit log size (keep last 1000 lines)
            lines = self.log_text.get(1.0, tk.END).split("\n")
            if len(lines) > 1000:
                self.log_text.delete(1.0, f"{len(lines) - 1000}.0")

    def set_callbacks(
        self,
        on_close: Optional[Callable] = None,
        refresh_status: Optional[Callable] = None,
        refresh_hotkeys: Optional[Callable] = None,
        quick_action: Optional[Callable] = None,
    ):
        """Set callback functions."""
        self.on_close_callback = on_close
        self.refresh_status_callback = refresh_status
        self.refresh_hotkeys_callback = refresh_hotkeys
        self.quick_action_callback = quick_action

    def is_visible(self) -> bool:
        """Check if window is visible."""
        return self.visible

    def destroy(self):
        """Destroy the window."""
        if self.root:
            self.root.destroy()
            self.root = None
            self.visible = False
            logger.info("Main window destroyed")
