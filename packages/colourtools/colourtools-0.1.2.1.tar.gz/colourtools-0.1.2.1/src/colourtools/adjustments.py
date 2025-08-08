from logging import getLogger

from .converters import rgb_to_hsl, hsl_to_rgb

logger = getLogger(__name__)

def brightness_hsl(hsl: tuple[float, float, float], factor: float = 1.0) -> tuple[float, float, float]:
    """Returns a new HSL tuple with adjusted brightness.
    Parameters:
    -----------
        hsl : tuple
            HSL values (hue, saturation, lightness).
        factor : float
            Brightness factor (1.0 = no change, <1.0 = darker, >1.0 = lighter).
    """
    h, s, l = hsl
    new_l = l * factor
    if new_l > 100.0:
        logger.warning(f"Lightness {new_l} exceeds 100%, clamping to 100%")
        new_l = 100.0
    elif new_l < 0.0:
        logger.warning(f"Lightness {new_l} exceeds below 0%, clamping to 0%")
        new_l = 0.0

    return (h, s, new_l)


def brightness_rgb(rgb: tuple[int, int, int], factor: float = 1.0) -> tuple[int, int, int]:
    """Returns a new RGB tuple with adjusted brightness.

    Parameters:
    -----------
        rgb : tuple
            RGB values (red, green, blue).
        factor : float
            Brightness factor (1.0 = no change, <1.0 = darker, >1.0 = lighter).
    """
    hsl = rgb_to_hsl(rgb)

    return hsl_to_rgb(brightness_hsl(hsl, factor))


def saturation_hsl(hsl: tuple[float, float, float], factor: float = 1.0) -> tuple[float, float, float]:
    """Returns a new HSL tuple with adjusted saturation.

    Parameters:
    -----------
        hsl : tuple
            HSL values (hue, saturation, lightness).
        factor : float
            Saturation factor (1.0 = no change, <1.0 = less saturated/muted, >1.0 = more saturated, richer).
    """
    h, s, l = hsl
    new_s = s * factor
    if new_s > 100:
        logger.warning(f"Saturation {new_s} exceeds 100%, clamping to 100%")
        new_s = 100
    elif new_s < 0.0:
        logger.warning(f"Saturation {new_s} exceeds below 0%, clamping to 0%")
        new_s = 0.0

    return (h, new_s, l)


def saturation_rgb(rgb: tuple[int, int, int], factor: float = 1.0) -> tuple[int, int, int]:
    """Returns a new RGB tuple with adjusted saturation.

    Parameters:
    -----------
        rgb : tuple
            RGB values (red, green, blue).
        factor : float
            Saturation factor (1.0 = no change, <1.0 = less saturated/muted, >1.0 = more saturated, richer).
    """
    hsl = rgb_to_hsl(rgb)

    return hsl_to_rgb(saturation_hsl(hsl, factor))


def adjust_hue(hsl: tuple[float, float, float], degrees: float = 180) -> tuple[float, float, float]:
    """Returns a new HSL tuple with adjusted hue.

    Parameters:
    -----------
        hsl : tuple
            HSL values (hue, saturation, lightness).
        degrees : float, optional
            Degrees to adjust hue by (positive = clockwise, negative = counter-clockwise). Default is 180.
            which generates a complementary color of the original.

    Returns:
    --------
        tuple
            New HSL values with adjusted hue.
    """
    h, s, l = hsl
    new_h = (h + degrees) % 360.0
    return (new_h, s, l)

def complement_hsl(hsl: tuple[float, float, float]) -> tuple[float, float, float]:
    """Returns a new HSL tuple that is the complementary color of the input.

    Parameters:
    -----------
        hsl : tuple
            HSL values (hue, saturation, lightness).

    Returns:
    --------
        tuple
            New HSL values that are the complement of the input.
    """
    return adjust_hue(hsl, 180)

def complement_rgb(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    """Returns a new RGB tuple that is the complementary color of the input.

    Parameters:
    -----------
        rgb : tuple
            RGB values (red, green, blue).

    Returns:
    --------
        tuple
            New RGB values that are the complement of the input.
    """
    hsl = rgb_to_hsl(rgb)
    comp_hsl = complement_hsl(hsl)
    return hsl_to_rgb(comp_hsl)
