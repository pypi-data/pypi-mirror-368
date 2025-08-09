# NUMPTY PATH for colormath
from typing import Any

import numpy as np
from colorblind import colorblind
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
from pbi_core.ruff.base_rule import BaseRule, RuleResult
from pbi_core.static_files.file_classes.theme import Theme


def patch_asscalar(a: Any) -> Any:
    return a.item()


np.asscalar = patch_asscalar
MIN_COLOR_DISTANCE = 3


def hex_to_rbg(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


class ThemeColors(BaseRule):
    id = "THM-001"
    name = "Theme Colors"
    description = """
        All colors used in the report should be defined in the theme.
        This helps to maintain consistency and makes it easier to change colors later.
    """

    @classmethod
    def check(cls, themes: dict[str, Theme]) -> list[RuleResult]:
        if not themes and cls:
            return []
        return []


class ThemeColorsProtanopia(ThemeColors):
    id = "THM-002"
    name = "Theme Colors Protanopia"
    description = """
        All data colors should be clearly distinguishable for color vision deficiency.
        This rule is specifically for Protanopia color vision deficiency.
    """

    @classmethod
    def check(cls, themes: dict[str, Theme]) -> list[RuleResult]:
        all_colors = set()
        for theme in themes.values():
            all_colors.update(theme.dataColors)
        colors = [[hex_to_rbg(color)] for color in all_colors]
        protanopia = colorblind.simulate_colorblindness(colors, colorblind_type="protanopia")
        protanopia_tuples: list[tuple[int, int, int]] = [
            convert_color(sRGBColor(*color[0]), LabColor) for color in protanopia
        ]

        conflicting_colors = []
        for c1 in protanopia_tuples:
            for c2 in protanopia_tuples:
                if c1 == c2:
                    continue
                if delta_e_cie2000(c1, c2) < MIN_COLOR_DISTANCE:
                    conflicting_colors.append((c1, c2))
        print(conflicting_colors)
        return []


class ThemeColorsDeuteranopia(ThemeColors):
    id = "THM-002"
    name = "Theme Colors Deuteranopia"
    description: str = """
        All data colors should be clearly distinguishable for color vision deficiency.
        This rule is specifically for Deuteranopia color vision deficiency.
    """

    @classmethod
    def check(cls, themes: dict[str, Theme]) -> list[RuleResult]:
        if not themes and cls:
            return []
        return []


class ThemeColorsTritanopia(ThemeColors):
    id = "THM-003"
    name = "Theme Colors Tritanopia"
    description = """
        All data colors should be clearly distinguishable for color vision deficiency.
        This rule is specifically for Tritanopia color vision deficiency.
    """

    @classmethod
    def check(cls, themes: dict[str, Theme]) -> list[RuleResult]:
        if not themes and cls:
            return []
        return []


# colorblind
