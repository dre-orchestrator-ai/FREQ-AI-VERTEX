"""
FREQ AI Theme System

Light and Dark mode themes with semantic color mappings.
Inspired by IBM Carbon and Microsoft Fluent design systems.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional

from .tokens import ColorPalette, DesignTokens, DESIGN_TOKENS


class ThemeMode(Enum):
    """Theme mode selection."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"  # Follow OS preference


@dataclass
class SemanticColors:
    """Semantic color assignments for a theme."""

    # Background layers
    background: str = ""
    background_secondary: str = ""
    background_tertiary: str = ""

    # Surface (cards, panels)
    surface: str = ""
    surface_hover: str = ""
    surface_selected: str = ""

    # Text
    text_primary: str = ""
    text_secondary: str = ""
    text_disabled: str = ""
    text_inverse: str = ""

    # Interactive
    interactive: str = ""
    interactive_hover: str = ""
    interactive_active: str = ""
    interactive_disabled: str = ""

    # Status indicators
    status_success: str = ""
    status_success_bg: str = ""
    status_warning: str = ""
    status_warning_bg: str = ""
    status_danger: str = ""
    status_danger_bg: str = ""
    status_info: str = ""
    status_info_bg: str = ""

    # Borders
    border: str = ""
    border_strong: str = ""
    border_interactive: str = ""

    # Focus
    focus: str = ""
    focus_inset: str = ""

    # Overlay
    overlay: str = ""


@dataclass
class Theme:
    """
    Complete theme configuration.

    Combines design tokens with semantic color mappings.
    """

    name: str
    mode: ThemeMode
    tokens: DesignTokens = field(default_factory=DesignTokens)
    semantic: SemanticColors = field(default_factory=SemanticColors)

    def to_css_variables(self) -> Dict[str, str]:
        """Export theme as CSS custom properties."""
        css_vars = self.tokens.to_css_variables()

        # Add semantic colors
        for field_name, value in vars(self.semantic).items():
            if not field_name.startswith("_") and value:
                css_key = f"--freq-{field_name.replace('_', '-')}"
                css_vars[css_key] = value

        return css_vars

    def to_dict(self) -> Dict[str, Any]:
        """Export theme as dictionary."""
        return {
            "name": self.name,
            "mode": self.mode.value,
            "tokens": self.tokens.to_dict(),
            "semantic": vars(self.semantic),
        }


def create_light_theme(tokens: Optional[DesignTokens] = None) -> Theme:
    """Create the FREQ AI light theme."""
    t = tokens or DESIGN_TOKENS
    colors = t.colors

    return Theme(
        name="FREQ Light",
        mode=ThemeMode.LIGHT,
        tokens=t,
        semantic=SemanticColors(
            # Backgrounds
            background=colors.background_light,
            background_secondary=colors.neutral_100,
            background_tertiary=colors.neutral_200,

            # Surfaces
            surface="#FFFFFF",
            surface_hover=colors.neutral_100,
            surface_selected=colors.primary_100,

            # Text
            text_primary=colors.text_primary_light,
            text_secondary=colors.text_secondary_light,
            text_disabled=colors.neutral_400,
            text_inverse=colors.text_primary_dark,

            # Interactive
            interactive=colors.primary_500,
            interactive_hover=colors.primary_600,
            interactive_active=colors.primary_700,
            interactive_disabled=colors.neutral_300,

            # Status
            status_success=colors.success_500,
            status_success_bg=colors.success_100,
            status_warning=colors.warning_600,
            status_warning_bg=colors.warning_100,
            status_danger=colors.danger_600,
            status_danger_bg=colors.danger_100,
            status_info=colors.info_500,
            status_info_bg=colors.info_100,

            # Borders
            border=colors.border_light,
            border_strong=colors.neutral_400,
            border_interactive=colors.primary_500,

            # Focus
            focus=colors.primary_500,
            focus_inset="#FFFFFF",

            # Overlay
            overlay="rgba(22, 22, 22, 0.5)",
        ),
    )


def create_dark_theme(tokens: Optional[DesignTokens] = None) -> Theme:
    """Create the FREQ AI dark theme."""
    t = tokens or DESIGN_TOKENS
    colors = t.colors

    return Theme(
        name="FREQ Dark",
        mode=ThemeMode.DARK,
        tokens=t,
        semantic=SemanticColors(
            # Backgrounds
            background=colors.background_dark,
            background_secondary=colors.neutral_900,
            background_tertiary=colors.neutral_800,

            # Surfaces
            surface=colors.neutral_900,
            surface_hover=colors.neutral_800,
            surface_selected=colors.primary_700,

            # Text
            text_primary=colors.text_primary_dark,
            text_secondary=colors.text_secondary_dark,
            text_disabled=colors.neutral_600,
            text_inverse=colors.text_primary_light,

            # Interactive (brighter for dark mode)
            interactive=colors.primary_400,
            interactive_hover=colors.primary_300,
            interactive_active=colors.primary_500,
            interactive_disabled=colors.neutral_700,

            # Status (adjusted for dark backgrounds)
            status_success=colors.success_400,
            status_success_bg=colors.success_700,
            status_warning=colors.warning_400,
            status_warning_bg=colors.warning_700,
            status_danger=colors.danger_400,
            status_danger_bg=colors.danger_700,
            status_info=colors.info_400,
            status_info_bg=colors.info_700,

            # Borders
            border=colors.border_dark,
            border_strong=colors.neutral_600,
            border_interactive=colors.primary_400,

            # Focus
            focus=colors.primary_400,
            focus_inset=colors.neutral_900,

            # Overlay
            overlay="rgba(0, 0, 0, 0.7)",
        ),
    )


# Pre-built theme instances
LIGHT_THEME = create_light_theme()
DARK_THEME = create_dark_theme()


def get_theme(mode: ThemeMode = ThemeMode.DARK) -> Theme:
    """
    Get a theme by mode.

    Default is dark mode for enterprise dashboards (reduces eye strain).
    """
    if mode == ThemeMode.LIGHT:
        return LIGHT_THEME
    return DARK_THEME


@dataclass
class ThemeContext:
    """
    Runtime theme context for application state.

    Manages current theme and provides switching capability.
    """

    current_theme: Theme = field(default_factory=lambda: DARK_THEME)
    user_preference: ThemeMode = ThemeMode.SYSTEM

    def set_mode(self, mode: ThemeMode) -> None:
        """Set the theme mode."""
        self.user_preference = mode
        self.current_theme = get_theme(mode)

    def toggle(self) -> ThemeMode:
        """Toggle between light and dark modes."""
        if self.current_theme.mode == ThemeMode.LIGHT:
            self.set_mode(ThemeMode.DARK)
        else:
            self.set_mode(ThemeMode.LIGHT)
        return self.current_theme.mode

    def get_css_class(self) -> str:
        """Get the CSS class for the current theme."""
        return f"freq-theme-{self.current_theme.mode.value}"
