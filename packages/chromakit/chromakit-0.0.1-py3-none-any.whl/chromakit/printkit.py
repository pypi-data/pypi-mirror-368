from typing import Literal
from .base import Color
from tkinter import Tk, Canvas

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def color_text(text: str, color: Color, *, mode = "text": Literal["text", "print"], allowed_formats = ["rgb", "rgba", "hsl"]: list, **kw):
    for format_check in allowed_formats:
        if format_check not in ["rgb", "rgba", "hsl"]:
            raise ValueError(f"wrong format '{format_check}'")
    if color.format not in allowed_formats:
        raise ValueError(f"wrong format '{color.format}'")
    r = color.to_rgb().r
    g = color.to_rgb().g
    b = color.to_rgb().b
    gentext = f"\033[38;2;{r};{g};{b}m{text}\033[0m"
    if mode == "text":
        return gentext
    elif mode == "print":
        print(gentext)

def display(color, *, allowed_formats = ["rgb", "rgba", "hsl"]: list, **kw):
    for format_check in allowed_formats:
        if format_check not in ["rgb", "rgba", "hsl"]:
            raise ValueError(f"wrong format '{format_check}'")
    if color.format not in allowed_formats:
        raise ValueError(f"wrong format '{color.format}'")
    if color.format == "rgb":
        root = Tk()
        root.configure(bg = rgb_to_hex(color.r, color.g, color.b))
        root.mainloop()
    elif color.format == "rgba":
        root = Tk()
        root.configure(bg = rgb_to_hex(color.r, color.g, color.b))
        root.arributes("-alpha", color.alpha)
        root.mainloop()
    elif color.format == "hsl":
        display(color.to_rgb())