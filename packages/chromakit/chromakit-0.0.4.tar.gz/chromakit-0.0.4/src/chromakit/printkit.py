from typing import Literal
from .base import Color
from tkinter import Tk
from colorama import init

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"

def color_text(
    text: str,
    color: Color,
    *,
    mode: Literal["text", "print"] = "text",
    allowed_formats: list[str] = ["rgb", "rgba", "hsl"],
    **kw
):
    init()
    # Validate allowed formats
    for fmt in allowed_formats:
        if fmt not in ["rgb", "rgba", "hsl"]:
            raise ValueError(f"wrong format '{fmt}'")
    if color.format not in allowed_formats:
        raise ValueError(f"wrong format '{color.format}'")

    rgb_color = color.to_rgb()
    r, g, b = rgb_color.r, rgb_color.g, rgb_color.b
    gentext = f"\033[38;2;{r};{g};{b}m{text}\033[0m"

    if mode == "text":
        return gentext
    elif mode == "print":
        print(gentext)

def display(
    color: Color,
    *,
    allowed_formats: list[str] = ["rgb", "rgba", "hsl"],
    **kw
):
    # Validate allowed formats
    for fmt in allowed_formats:
        if fmt not in ["rgb", "rgba", "hsl"]:
            raise ValueError(f"wrong format '{fmt}'")
    if color.format not in allowed_formats:
        raise ValueError(f"wrong format '{color.format}'")

    if color.format == "rgb":
        root = Tk()
        root.configure(bg=rgb_to_hex(color.r, color.g, color.b))
        root.mainloop()
    elif color.format == "rgba":
        root = Tk()
        root.configure(bg=rgb_to_hex(color.r, color.g, color.b))
        root.attributes("-alpha", color.alpha)
        root.mainloop()
    elif color.format == "hsl":
        display(color.to_rgb())