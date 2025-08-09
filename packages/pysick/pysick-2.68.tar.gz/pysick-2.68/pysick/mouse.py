# pysick/py


"""
PySick Mouse Input Handler
"""
import pysick

# Internal state
_buttons = {
    "LEFT": False,
    "MIDDLE": False,
    "RIGHT": False,
}

LEFT = "LEFT"
MIDDLE = "MIDDLE"
RIGHT = "RIGHT"

_position = (0, 0)
_wheel_delta = 0

def init():
    """
    Initialize mouse bindings.
    Should be called once after creating the window.
    """
    import pysick
    root = pysick.ingine._root

    # Mouse button events
    root.bind("<ButtonPress-1>", lambda e: _set_button("LEFT", True))
    root.bind("<ButtonRelease-1>", lambda e: _set_button("LEFT", False))

    root.bind("<ButtonPress-2>", lambda e: _set_button("MIDDLE", True))
    root.bind("<ButtonRelease-2>", lambda e: _set_button("MIDDLE", False))

    root.bind("<ButtonPress-3>", lambda e: _set_button("RIGHT", True))
    root.bind("<ButtonRelease-3>", lambda e: _set_button("RIGHT", False))

    # Mouse motion
    root.bind("<Motion>", _on_motion)

    # Mouse wheel
    root.bind("<MouseWheel>", _on_wheel)


def _set_button(button, state):
    _buttons[button] = state


def _on_motion(event):
    _position = (event.x, event.y)


def _on_wheel(event):
    _wheel_delta = event.delta


def is_pressed(button):
    """
    Check if a mouse button is pressed.

    Parameters:
        button (str): "LEFT", "MIDDLE", or "RIGHT"

    Returns:
        bool
    """
    return _buttons.get(button, False)


def get_pos():
    """
    Get current mouse position.

    Returns:
        (x, y) tuple
    """
    return _position


def get_wheel_delta():
    """
    Get last wheel delta.

    Returns:
        int
    """
    return _wheel_delta