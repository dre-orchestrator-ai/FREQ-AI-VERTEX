"""
FREQ AI Design Tokens

Token-based design system inspired by IBM Carbon and Microsoft Fluent.
Provides consistent styling primitives for the FREQ AI Command Center.

Reference:
- IBM Carbon: https://carbondesignsystem.com/
- Microsoft Fluent 2: https://fluent2.microsoft.design/
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from enum import Enum


class ColorRole(Enum):
    """Semantic color roles."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    NEUTRAL = "neutral"


@dataclass
class ColorPalette:
    """
    FREQ AI Color Palette

    Designed for enterprise maritime operations with high contrast
    and accessibility compliance (WCAG 2.1 AA minimum).
    """

    # Primary - FREQ Blue (Maritime/Professional)
    primary_100: str = "#E8F4FE"
    primary_200: str = "#B8DCFC"
    primary_300: str = "#78BAF7"
    primary_400: str = "#4598E8"
    primary_500: str = "#0F62FE"  # Primary action color (Carbon Blue 60)
    primary_600: str = "#0043CE"
    primary_700: str = "#002D9C"

    # Secondary - Teal (Intelligence/Analytics)
    secondary_100: str = "#D9FBFB"
    secondary_200: str = "#9EF0F0"
    secondary_300: str = "#3DDBD9"
    secondary_400: str = "#08BDBA"
    secondary_500: str = "#009D9A"  # Secondary actions
    secondary_600: str = "#007D79"
    secondary_700: str = "#005D5D"

    # Accent - Purple (AI/Cognition)
    accent_100: str = "#F6F2FF"
    accent_200: str = "#E8DAFF"
    accent_300: str = "#D4BBFF"
    accent_400: str = "#BE95FF"
    accent_500: str = "#A56EFF"  # AI/Lattice indicators
    accent_600: str = "#8A3FFC"
    accent_700: str = "#6929C4"

    # Success - Green
    success_100: str = "#DEFBE6"
    success_200: str = "#A7F0BA"
    success_300: str = "#6FDC8C"
    success_400: str = "#42BE65"
    success_500: str = "#24A148"  # FREQ compliance passed
    success_600: str = "#198038"
    success_700: str = "#0E6027"

    # Warning - Yellow/Gold
    warning_100: str = "#FFF8E1"
    warning_200: str = "#FFE082"
    warning_300: str = "#FFD54F"
    warning_400: str = "#FFCA28"
    warning_500: str = "#F1C21B"  # Degraded status
    warning_600: str = "#D2A106"
    warning_700: str = "#8E6A00"

    # Danger - Red
    danger_100: str = "#FFF1F1"
    danger_200: str = "#FFD7D9"
    danger_300: str = "#FFB3B8"
    danger_400: str = "#FF8389"
    danger_500: str = "#FA4D56"  # VETO/Critical
    danger_600: str = "#DA1E28"
    danger_700: str = "#A2191F"

    # Info - Cyan
    info_100: str = "#E5F6FF"
    info_200: str = "#BAE6FF"
    info_300: str = "#82CFFF"
    info_400: str = "#33B1FF"
    info_500: str = "#1192E8"  # Informational
    info_600: str = "#0072C3"
    info_700: str = "#00539A"

    # Neutral - Gray scale
    neutral_100: str = "#F4F4F4"
    neutral_200: str = "#E0E0E0"
    neutral_300: str = "#C6C6C6"
    neutral_400: str = "#A8A8A8"
    neutral_500: str = "#8D8D8D"
    neutral_600: str = "#6F6F6F"
    neutral_700: str = "#525252"
    neutral_800: str = "#393939"
    neutral_900: str = "#262626"
    neutral_1000: str = "#161616"  # Dark mode background

    # Semantic aliases
    background_light: str = "#FFFFFF"
    background_dark: str = "#161616"
    surface_light: str = "#F4F4F4"
    surface_dark: str = "#262626"
    text_primary_light: str = "#161616"
    text_primary_dark: str = "#F4F4F4"
    text_secondary_light: str = "#525252"
    text_secondary_dark: str = "#A8A8A8"
    border_light: str = "#E0E0E0"
    border_dark: str = "#393939"


@dataclass
class Typography:
    """
    FREQ AI Typography Scale

    Uses IBM Plex Sans for body and IBM Plex Mono for code/data.
    """

    # Font families
    font_family_sans: str = "'IBM Plex Sans', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"
    font_family_mono: str = "'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace"
    font_family_display: str = "'IBM Plex Sans', 'Segoe UI Variable Display', sans-serif"

    # Font weights
    weight_light: int = 300
    weight_regular: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700

    # Type scale (rem units, base 16px)
    # Caption/Small
    size_xs: str = "0.75rem"    # 12px
    size_sm: str = "0.875rem"   # 14px
    # Body
    size_md: str = "1rem"       # 16px (base)
    size_lg: str = "1.125rem"   # 18px
    # Headings
    size_xl: str = "1.25rem"    # 20px
    size_2xl: str = "1.5rem"    # 24px
    size_3xl: str = "1.75rem"   # 28px
    size_4xl: str = "2rem"      # 32px
    size_5xl: str = "2.625rem"  # 42px

    # Line heights
    line_height_tight: str = "1.25"
    line_height_normal: str = "1.5"
    line_height_relaxed: str = "1.75"

    # Letter spacing
    letter_spacing_tight: str = "-0.02em"
    letter_spacing_normal: str = "0"
    letter_spacing_wide: str = "0.025em"


@dataclass
class Spacing:
    """
    FREQ AI Spacing Scale

    Based on 4px grid system for consistent layouts.
    """

    # Base unit
    base: int = 4  # pixels

    # Spacing scale (multiples of base)
    space_0: str = "0"
    space_1: str = "0.25rem"   # 4px
    space_2: str = "0.5rem"    # 8px
    space_3: str = "0.75rem"   # 12px
    space_4: str = "1rem"      # 16px
    space_5: str = "1.25rem"   # 20px
    space_6: str = "1.5rem"    # 24px
    space_7: str = "2rem"      # 32px
    space_8: str = "2.5rem"    # 40px
    space_9: str = "3rem"      # 48px
    space_10: str = "4rem"     # 64px

    # Component-specific
    container_padding: str = "1.5rem"  # 24px
    card_padding: str = "1rem"         # 16px
    button_padding_x: str = "1rem"     # 16px
    button_padding_y: str = "0.5rem"   # 8px
    input_padding: str = "0.75rem"     # 12px
    table_cell_padding: str = "0.75rem"

    # Layout widths
    sidebar_width: str = "256px"
    sidebar_collapsed: str = "64px"
    container_max: str = "1440px"
    content_max: str = "1200px"


@dataclass
class BorderRadius:
    """Border radius tokens."""
    none: str = "0"
    sm: str = "2px"
    md: str = "4px"
    lg: str = "8px"
    xl: str = "12px"
    full: str = "9999px"


@dataclass
class Shadow:
    """Shadow tokens for depth/elevation."""
    sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    xl: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

    # Dark mode shadows with subtle glow
    sm_dark: str = "0 1px 3px 0 rgba(0, 0, 0, 0.3)"
    md_dark: str = "0 4px 6px -1px rgba(0, 0, 0, 0.4)"
    lg_dark: str = "0 10px 15px -3px rgba(0, 0, 0, 0.5)"


@dataclass
class Transition:
    """Animation/transition tokens."""
    duration_fast: str = "100ms"
    duration_normal: str = "200ms"
    duration_slow: str = "300ms"
    duration_slower: str = "500ms"

    easing_default: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    easing_ease_in: str = "cubic-bezier(0.4, 0, 1, 1)"
    easing_ease_out: str = "cubic-bezier(0, 0, 0.2, 1)"
    easing_ease_in_out: str = "cubic-bezier(0.4, 0, 0.2, 1)"

    # Fluent-inspired productive motion
    easing_productive: str = "cubic-bezier(0.2, 0, 0.38, 0.9)"
    easing_expressive: str = "cubic-bezier(0.4, 0.14, 0.3, 1)"


@dataclass
class DesignTokens:
    """
    Complete FREQ AI Design Token Set

    Combines all token categories into a single configuration.
    """

    colors: ColorPalette = field(default_factory=ColorPalette)
    typography: Typography = field(default_factory=Typography)
    spacing: Spacing = field(default_factory=Spacing)
    border_radius: BorderRadius = field(default_factory=BorderRadius)
    shadow: Shadow = field(default_factory=Shadow)
    transition: Transition = field(default_factory=Transition)

    def to_css_variables(self, prefix: str = "freq") -> Dict[str, str]:
        """
        Export tokens as CSS custom properties.

        Returns a dict that can be used to generate CSS like:
        :root { --freq-primary-500: #0F62FE; ... }
        """
        css_vars = {}

        # Colors
        for field_name, value in vars(self.colors).items():
            if not field_name.startswith("_"):
                css_vars[f"--{prefix}-color-{field_name.replace('_', '-')}"] = value

        # Typography
        for field_name, value in vars(self.typography).items():
            if not field_name.startswith("_"):
                css_vars[f"--{prefix}-{field_name.replace('_', '-')}"] = str(value)

        # Spacing
        for field_name, value in vars(self.spacing).items():
            if not field_name.startswith("_") and isinstance(value, str):
                css_vars[f"--{prefix}-{field_name.replace('_', '-')}"] = value

        return css_vars

    def to_dict(self) -> Dict[str, Any]:
        """Export all tokens as a dictionary."""
        return {
            "colors": vars(self.colors),
            "typography": vars(self.typography),
            "spacing": vars(self.spacing),
            "borderRadius": vars(self.border_radius),
            "shadow": vars(self.shadow),
            "transition": vars(self.transition),
        }


# Default token instance
DESIGN_TOKENS = DesignTokens()
