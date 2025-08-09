# ABOUTME: Miscellaneous utilities - color generation and helper functions
"""Miscellaneous utility functions for repomap."""

import colorsys
import random


def get_random_color() -> str:
    """Generate a random color in hex format."""
    hue = random.random()
    r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, 1, 0.75)]
    res = f"#{r:02x}{g:02x}{b:02x}"
    return res