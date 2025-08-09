

"""
PySick keys input handler.

Usage:
    init()
    if KEY_W:
        # do something
"""

# Class-level dictionary to track key states
__state = {}

# Mapping from readable constants → actual characters
# Letters
KEY_A = "A"
KEY_B = "B"
KEY_C = "C"
KEY_D = "D"
KEY_E = "E"
KEY_F = "F"
KEY_G = "G"
KEY_H = "H"
KEY_I = "I"
KEY_J = "J"
KEY_K = "K"
KEY_L = "L"
KEY_M = "M"
KEY_N = "N"
KEY_O = "O"
KEY_P = "P"
KEY_Q = "Q"
KEY_R = "R"
KEY_S = "S"
KEY_T = "T"
KEY_U = "U"
KEY_V = "V"
KEY_W = "W"
KEY_X = "X"
KEY_Y = "Y"
KEY_Z = "Z"

# Digits
KEY_0 = "0"
KEY_1 = "1"
KEY_2 = "2"
KEY_3 = "3"
KEY_4 = "4"
KEY_5 = "5"
KEY_6 = "6"
KEY_7 = "7"
KEY_8 = "8"
KEY_9 = "9"

# Arrow keys
KEY_LEFT = "Left"
KEY_RIGHT = "Right"
KEY_UP = "Up"
KEY_DOWN = "Down"

# Modifier keys
KEY_SHIFT_L = "Shift_L"
KEY_SHIFT_R = "Shift_R"
KEY_CONTROL_L = "Control_L"
KEY_CONTROL_R = "Control_R"
KEY_ALT_L = "Alt_L"
KEY_ALT_R = "Alt_R"
KEY_CAPS_LOCK = "Caps_Lock"

# Space and enter
KEY_SPACE = "space"
KEY_RETURN = "Return"
KEY_TAB = "Tab"
KEY_BACKSPACE = "BackSpace"
KEY_ESCAPE = "Escape"

# Symbols / punctuation
KEY_EXCLAMATION = "exclam"
KEY_AT = "at"
KEY_HASH = "numbersign"
KEY_DOLLAR = "dollar"
KEY_PERCENT = "percent"
KEY_CARET = "asciicircum"
KEY_AMPERSAND = "ampersand"
KEY_ASTERISK = "asterisk"
KEY_LEFT_PAREN = "parenleft"
KEY_RIGHT_PAREN = "parenright"
KEY_MINUS = "minus"
KEY_UNDERSCORE = "underscore"
KEY_EQUALS = "equal"
KEY_PLUS = "plus"
KEY_LEFT_BRACE = "braceleft"
KEY_RIGHT_BRACE = "braceright"
KEY_LEFT_BRACKET = "bracketleft"
KEY_RIGHT_BRACKET = "bracketright"
KEY_SEMICOLON = "semicolon"
KEY_COLON = "colon"
KEY_QUOTE = "quoteright"
KEY_DOUBLE_QUOTE = "quotedbl"
KEY_COMMA = "comma"
KEY_PERIOD = "period"
KEY_SLASH = "slash"
KEY_BACKSLASH = "backslash"
KEY_PIPE = "bar"
KEY_LESS = "less"
KEY_GREATER = "greater"
KEY_QUESTION = "question"

# Function keys
KEY_F1 = "F1"
KEY_F2 = "F2"
KEY_F3 = "F3"
KEY_F4 = "F4"
KEY_F5 = "F5"
KEY_F6 = "F6"
KEY_F7 = "F7"
KEY_F8 = "F8"
KEY_F9 = "F9"
KEY_F10 = "F10"
KEY_F11 = "F11"
KEY_F12 = "F12"

# --- Internal storage ---
_pressed = {}
_pressed_once = set()

def init():
    """
    Initialize key tracking on the Tk root window.
    Should be called AFTER pysick.ingine.init().
    """
    from pysick import ingine

    root = ingine._root

    def on_press(event):
        k = _normalize(event.keysym)
        _pressed[k] = True

    def on_release(event):
        k = _normalize(event.keysym)
        if _pressed.get(k, False):
            _pressed_once.add(k)
        _pressed[k] = False

    root.bind("<KeyPress>", on_press)
    root.bind("<KeyRelease>", on_release)


def is_pressed(key):
    """
    Check if the given key is currently held down.

    Parameters:
        key (str): One of the key constants above.

    Returns:
        bool: True if held down, else False.
    """
    return _pressed.get(key, False)


def was_pressed(key):
    """
    Check if the given key was pressed and released since last check.
    Good for one-shot triggers.

    Parameters:
        key (str)

    Returns:
        bool
    """
    if key in _pressed_once:
        _pressed_once.remove(key)
        return True
    return False


def _normalize(name):
    """
    Normalize key names for consistent dictionary lookup.
    """
    return name.upper() if len(name) == 1 else name