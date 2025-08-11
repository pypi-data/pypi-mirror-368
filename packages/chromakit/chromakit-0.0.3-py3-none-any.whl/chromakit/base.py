from typing import Literal as _Literal
from math import floor as _floor

class ColorError(Exception):
    pass

class Color:
    def __init__(self, color: tuple, color_format: _Literal["rgb", "rgba", "hsl"] = "rgb"):
        if len(color) != len(color_format):
            raise ColorError("tuple not matching with format")
        wrong_types = {type(obj).__name__ for obj in color if not isinstance(obj, (int, float))}
        if wrong_types:
            raise IndexError(f"wrong values in color: {', '.join(wrong_types)}")
        if color_format == "hsl":
            h, s, l = color
            if not (0 <= h <= 360 and 0 <= s <= 1 and 0 <= l <= 1):
                raise ColorError("color not matching with hsl")
        elif color_format in ["rgb", "rgba"]:
            for i, num in enumerate(color):
                if i == 3:
                    if not (0 <= num <= 1):
                        raise ColorError(f"tuple not matching with {color_format}")
                else:
                    if not (0 <= num <= 255):
                        raise ColorError(f"tuple not matching with {color_format}")
        if color_format in ("rgb", "rgba"):
            self.r, self.g, self.b = color[0], color[1], color[2]
            if color_format == "rgba":
                self.alpha = color[3]
        else:
            self.h, self.s, self.l = color
        self.format = color_format

    def __str__(self):
        if self.format == "rgb":
            return f"rgb({self.r}, {self.g}, {self.b})"
        elif self.format == "rgba":
            return f"rgba({self.r}, {self.g}, {self.b}, {self.alpha})"
        elif self.format == "hsl":
            return f"hsl({self.h}, {self.s}, {self.l})"

    def __repr__(self):
        return f"<Color {self}>"

    def _hsl_to_rgb_values(self):
        c = (1 - abs(2 * self.l - 1)) * self.s
        h_prime = self.h / 60
        x = c * (1 - abs(h_prime % 2 - 1))
        m = self.l - c / 2
        if 0 <= self.h < 60:
            r1, g1, b1 = c, x, 0
        elif 60 <= self.h < 120:
            r1, g1, b1 = x, c, 0
        elif 120 <= self.h < 180:
            r1, g1, b1 = 0, c, x
        elif 180 <= self.h < 240:
            r1, g1, b1 = 0, x, c
        elif 240 <= self.h < 300:
            r1, g1, b1 = x, 0, c
        else:
            r1, g1, b1 = c, 0, x
        r = _floor((r1 + m) * 255)
        g = _floor((g1 + m) * 255)
        b = _floor((b1 + m) * 255)
        return r, g, b

    def to_rgb(self, *, inplace: bool = False, **kw):
        if self.format == "rgb":
            return self if not inplace else None
        elif self.format == "rgba":
            if inplace:
                del self.alpha
                self.format = "rgb"
            else:
                return Color((self.r, self.g, self.b), "rgb")
        elif self.format == "hsl":
            r, g, b = self._hsl_to_rgb_values()
            if inplace:
                self.r, self.g, self.b = r, g, b
                self.format = "rgb"
                del self.h, self.s, self.l
            else:
                return Color((r, g, b), "rgb")

    def to_rgba(self, *, inplace: bool = False, **kw):
        if self.format == "rgba":
            return self if not inplace else None
        elif self.format == "rgb":
            if inplace:
                self.alpha = 1.0
                self.format = "rgba"
            else:
                return Color((self.r, self.g, self.b, 1.0), "rgba")
        elif self.format == "hsl":
            r, g, b = self._hsl_to_rgb_values()
            if inplace:
                self.r, self.g, self.b, self.alpha = r, g, b, 1.0
                self.format = "rgba"
                del self.h, self.s, self.l
            else:
                return Color((r, g, b, 1.0), "rgba")

    def to_hsl(self, *, inplace: bool = False, **kw):
        if self.format == "hsl":
            return self if not inplace else None
        r1 = self.r / 255
        g1 = self.g / 255
        b1 = self.b / 255
        cmax = max(r1, g1, b1)
        cmin = min(r1, g1, b1)
        delta = cmax - cmin

        if delta == 0:
            h = 0
        elif cmax == r1:
            h = (g1 - b1) / delta % 6
        elif cmax == g1:
            h = (b1 - r1) / delta + 2
        else:
            h = (r1 - g1) / delta + 4
        h *= 60

        l = (cmax + cmin) / 2
        s = 0 if delta == 0 else delta / (1 - abs(2 * l - 1))

        if inplace:
            self.h, self.s, self.l = h, s, l
            del self.r, self.g, self.b
            if self.format == "rgba":
                del self.alpha
            self.format = "hsl"
        else:
            return Color((h, s, l), "hsl")
