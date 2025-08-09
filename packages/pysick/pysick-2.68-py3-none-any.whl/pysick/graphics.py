"""
PySick drawing utilities for shapes and screen manipulation.
"""
class SickError(Exception):
    def __init__(self ,message = 'error'):
        super().__init__(message)


def _color_to_hex(color):
    """
    Convert (R,G,B) or (R,G,B,A) tuple to #RRGGBB hex string for tkinter.

    Args:
        color: A string (e.g. "red") or tuple like (R, G, B) or (R, G, B, A).

    Returns:
        A tkinter-compatible color string like "#ff00cc".
    """
    if isinstance(color, tuple):
        if len(color) == 3:
            r, g, b = color
        elif len(color) == 4:
            r, g, b, _ = color  # Ignore alpha for now
        else:
            raise ValueError("Color tuple must be RGB or RGBA.")
        return f'#{r:02x}{g:02x}{b:02x}'
    elif isinstance(color, str):
        return color  # Already a color name or hex
    else:
        raise ValueError("Color must be a tuple or a string.")



class Rect:
    """
    Rectangle shape.
    """
    def __init__(self, x, y, width, height, fill):
        self._shape_type = "rect"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill = fill

class Oval:
    """
    Oval shape.
    """
    def __init__(self, x, y, width, height, fill):
        self._shape_type = "oval"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill = fill

class Circle:
    """
    Circle shape.
    """
    def __init__(self, x, y, radius, fill):
        self._shape_type = "circle"
        self.x = x
        self.y = y
        self.radius = radius
        self.fill = fill

class Line:
    """
    Line shape.
    """
    def __init__(self, x1, y1, x2, y2, fill):
        self._shape_type = "line"
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fill = fill

def fill_screen( fill):
    """
    Fill the entire screen with a solid color.
    """
    import pysick
    master = pysick.ingine
    canvas = master._get_canvas()
    canvas.delete("all")
    fill_color = _color_to_hex(fill)
    canvas.create_rectangle(
        0, 0,
        master.width,
        master.height,
        fill=fill_color
    )

def draw( shape):
    """
    Draw any shape object.

    Parameters:
        master (InGine): The engine window.
        shape: A shape instance from graphics class.
    """
    import pysick
    master = pysick.ingine
    canvas = master._get_canvas()

    try:
        shape_type = getattr(shape, "_shape_type", None)

        fill_color = _color_to_hex(shape.fill)

        if shape_type == "rect":
            x2 = shape.x + shape.width
            y2 = shape.y + shape.height
            canvas.create_rectangle(shape.x, shape.y, x2, y2, fill=fill_color)

        elif shape_type == "oval":
            x2 = shape.x + shape.width
            y2 = shape.y + shape.height
            canvas.create_oval(shape.x, shape.y, x2, y2, fill=fill_color)

        elif shape_type == "circle":
            r = shape.radius
            canvas.create_oval(
                shape.x - r,
                shape.y - r,
                shape.x + r,
                shape.y + r,
                fill=fill_color
            )

        elif shape_type == "line":
            canvas.create_line(
                shape.x1, shape.y1,
                shape.x2, shape.y2,
                fill=fill_color
            )

        else:
            raise SickError("Invalid shape object passed to graphics.draw().")

    except Exception as ex:
        raise SickError(str(ex))


def draw_polygon(points, fill, master=None):
    """
    Draw a polygon shape.

    Parameters:
        points (list of tuples): [(x1, y1), (x2, y2), ...]
        fill (str or tuple): Color
        master (InGine): Optional engine instance.
    """
    import pysick
    canvas = master._get_canvas() if master else pysick.ingine._get_canvas()
    fill = _color_to_hex(fill)
    coords = []
    for x, y in points:
        coords.extend([x, y])
    canvas.create_polygon(coords, fill=fill)


def draw_text(x, y, text, font=("Arial", 16), fill=(0, 0, 0), anchor="nw", master=None):
    """
    Draw text on the canvas.

    Parameters:
        x (int)
        y (int)
        text (str)
        font (tuple)
        fill (str or tuple)
        anchor (str)
        master (InGine)
    """
    import pysick
    canvas = master._get_canvas() if master else pysick.ingine._get_canvas()
    fill = _color_to_hex(fill)
    canvas.create_text(x, y, text=text, font=font, fill=fill, anchor=anchor)
