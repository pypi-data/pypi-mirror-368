from .base import Color, ColorError
from math import sqrt

def average(num1: int, num2: int):
    return (num1 + num2) / 2

def mix(color1: Color, color2: Color):
    if color1.format != color2.format:
        color1 = color1.to_rgb()
        color2 = color2.to_rgb()
    if color1.format == "rgb":
        return Color((average(color1.r, color2.r), average(color1.g, color2.g), average(color1.b, color2.b)))
    elif color1.format == "rgba":
        return Color(
            (average(color1.r, color2.r), average(color1.g, color2.g), average(color1.b, color2.b), max(color1.alpha, color2.alpha)),
            "rgba"
        )
    else:
        return mix(color1.to_rgb(), color2.to_rgb())

def invert(color: Color):
    if color.format == "rgb":
        return Color((255 - color.r, 255 - color.g, 255 - color.b))
    elif color.format == "rgba":
        return Color((255 - color.r, 255 - color.g, 255 - color.b, color.alpha), "rgba")
    else:
        return invert(color.to_rgb())

def put_ratio(color: Color, ratio: float):
    if color.format == "rgb":
        color.r = min(255, color.r * ratio)
        color.g = min(255, color.g * ratio)
        color.b = min(255, color.b * ratio)
        return color
    elif color.format == "rgba":
        new_rgb = put_ratio(color.to_rgb(), ratio)
        new_rgb.to_rgba(inplace=True)
        new_rgb.alpha = color.alpha
        return new_rgb
    else:
        return put_ratio(color.to_rgb(), ratio)

def adjust(c):
    c = c / 255  # normalize
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def is_dark(color: Color):
    color = color.to_rgb() if color.format != "rgb" else color
    newr, newg, newb = adjust(color.r), adjust(color.g), adjust(color.b)
    return (0.2126 * newr + 0.7152 * newg + 0.0722 * newb) < 0.5

def is_light(color: Color):
    return not is_dark(color)

def distance(color1: Color, color2: Color):
    color1 = color1.to_rgb() if color1.format != "rgb" else color1
    color2 = color2.to_rgb() if color2.format != "rgb" else color2
    return sqrt((color1.r - color2.r) ** 2 + (color1.g - color2.g) ** 2 + (color1.b - color2.b) ** 2)