"""
pysick: A beginner-friendly graphics module with future-ready video & canvas features.
"""


from . import clock
from . import graphics
from . import keys
from . import message_box
from . import version

__all__ = [graphics, keys, message_box, clock, version]

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

from tkinter import TclVersion


class SickError(Exception):
    """
    Custom error for PySick module.

    Parameters:
        message (str): Optional error message.
    """

    def __init__(self, message="A SickError occurred!"):
        super().__init__(message)

try:
    from . import _tkinter_pysick as tk
except Exception as e:
    error = e
    raise SickError('ImportError: _tkinter_pysick.py not found')
try:
    from . import _messagebox_pysick as messagebox
except Exception as e:
    error = e
    raise SickError('ImportError: _messagebox_pysick.py not found')



try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1+
except Exception:
    try:
        windll.user32.SetProcessDPIAware()    # Windows Vista+
    except Exception:
        pass



QUIT = False

class ingine:
    """
    PySick InGine class for managing the Tkinter window and canvas.

    Parameters:
        width (int): Window width in pixels.
        height (int): Window height in pixels.
    """

    _root = None
    _canvas = None
    width = 0
    height = 0

    @classmethod
    def init(cls, width, height):
        """
        Initialize the engine window and canvas.
        """
        print(f"[pysick] Window Initialized with {width}x{height}")

        cls._root = tk.Tk()
        cls._root.title("pysick graphics")


        cls.width = width
        cls.height = height
        cls._root.geometry(f"{width}x{height}")

        cls._root.protocol("WM_DELETE_WINDOW", cls.on_close)

        cls._canvas = tk.Canvas(cls._root, width=width, height=height)
        cls._canvas.pack()

        try:
            import os
            import sys
            py_icon_path = os.path.join(os.path.dirname(sys.executable), 'DLLs', 'pyc.ico')
            try:
                cls._root.iconbitmap(py_icon_path)
            except Exception:
                pass
        except Exception as ex:
            raise SickError(str(ex))



    @classmethod
    def on_close(cls):
        global QUIT
        QUIT = True
        cls._root.destroy()



    @classmethod
    def _get_canvas(cls):
        import inspect
        caller = inspect.stack()[1].frame.f_globals["__name__"]
        if not caller.startswith("pysick."):
            raise SickError(f"Unauthorized access from {caller}")
        return cls._canvas

    @classmethod
    def run(cls):
        """
        Run the Tkinter main loop.
        """
        cls._root.mainloop()
    @classmethod
    def slap(cls):
        """Update"""
        cls._root.update()
        cls._root.update_idletasks()

    @classmethod
    def set_title(cls, title):
        """
        Set the window title.

        Parameters:
            title (str): New title for the window.
        """
        cls._root.title(title)



    @classmethod
    def add_label(cls, text, x, y, font=("Arial", 14), color="black"):
        """
        Add a text label to the window.
        """
        label = tk.Label(cls._root, text=text, font=font, fg=color)
        label.place(x=x, y=y)
        return label

    @classmethod
    def add_button(cls, text, x, y, func, width=10, height=2):
        """
        Add a clickable button.
        """
        button = tk.Button(
            cls._root,
            text=text,
            command=func,
            width=width,
            height=height
        )
        button.place(x=x, y=y)
        return button



    @classmethod
    def quit(cls):
        """
        Destroy the window and quit the program.
        """
        cls._root.destroy()



