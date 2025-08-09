

"""
PySick GUI class with static methods for adding widgets
to the pysick.ingine window.
"""

import pysick
import _tkinter_pysick as tk
_widgets = []


def add_label(text, x, y, font=("Arial", 14), color="black"):
    root = pysick.ingine._root
    label = tk.Label(root, text=text, font=font, fg=color)
    label.place(x=x, y=y)
    _widgets.append(label)
    return label


def add_button(text, x, y, func, width=10, height=2):
    root = pysick.ingine._root
    button = tk.Button(root, text=text, command=func, width=width, height=height)
    button.place(x=x, y=y)
    _widgets.append(button)
    return button


def add_entry(x, y, width=20):
    root = pysick.ingine._root
    entry = tk.Entry(root, width=width)
    entry.place(x=x, y=y)
    _widgets.append(entry)
    return entry


def add_checkbutton(text, x, y, variable=None):
    """
    Add a checkbox.

    Parameters:
        text (str): Label text.
        x, y (int): Position.
        variable (tk.BooleanVar): Optional external variable.

    Returns:
        tk.Checkbutton, tk.BooleanVar
    """
    root = pysick.ingine._root
    var = variable or tk.BooleanVar()
    check = tk.Checkbutton(root, text=text, variable=var)
    check.place(x=x, y=y)
    _widgets.append(check)
    return check, var


def add_radiobutton(text, x, y, variable, value):
    """
    Add a radiobutton.

    Parameters:
        text (str): Button text.
        x, y (int): Position.
        variable (tk.Variable): The shared variable for all radio buttons.
        value (any): The value assigned if selected.

    Returns:
        tk.Radiobutton
    """
    root = pysick.ingine._root
    radio = tk.Radiobutton(root, text=text, variable=variable, value=value)
    radio.place(x=x, y=y)
    _widgets.append(radio)
    return radio


def add_scale(x, y, from_=0, to=100, orient='horizontal', length=200):
    """
    Add a slider (scale).

    Parameters:
        x, y (int): Position.
        from_, to (int): Min and max values.
        orient (str): 'horizontal' or 'vertical'.
        length (int): Pixel length.

    Returns:
        tk.Scale
    """
    root = pysick.ingine._root
    scale = tk.Scale(root, from_=from_, to=to, orient=orient, length=length)
    scale.place(x=x, y=y)
    _widgets.append(scale)
    return scale

def add_textbox(x, y, width=40, height=5):
    """
    Add a multi-line text box.

    Parameters:
        x, y (int): Position.
        width (int): Character width.
        height (int): Number of lines.

    Returns:
        tk.Text
    """
    root = pysick.ingine._root
    textbox = tk.Text(root, width=width, height=height)
    textbox.place(x=x, y=y)
    _widgets.append(textbox)
    return textbox


def clear():
    """
    Destroy all widgets created via gui class.
    """
    for widget in _widgets:
        widget.destroy()
    _widgets.clear()