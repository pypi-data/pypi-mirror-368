# epp.py - Single-file EPP engine (numpy + PIL + tkinter)
# Created for PySick: fast numpy framebuffer, drawing API, input, and loop helpers.
# Requirements: pillow, numpy
# Save as epp.py and import in your games: from epp import *

from . import _tkinter_pysick as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import time
import os
try:
    import numpy as np
except ImportError:
    raise ImportError("You need to install numpy for fast graphics(epp)")
# === Key constants ===
eppKeyA = 'a'; eppKeyB = 'b'; eppKeyC = 'c'; eppKeyD = 'd'; eppKeyE = 'e'; eppKeyF = 'f'
eppKeyG = 'g'; eppKeyH = 'h'; eppKeyI = 'i'; eppKeyJ = 'j'; eppKeyK = 'k'; eppKeyL = 'l'
eppKeyM = 'm'; eppKeyN = 'n'; eppKeyO = 'o'; eppKeyP = 'p'; eppKeyQ = 'q'; eppKeyR = 'r'
eppKeyS = 's'; eppKeyT = 't'; eppKeyU = 'u'; eppKeyV = 'v'; eppKeyW = 'w'; eppKeyX = 'x'
eppKeyY = 'y'; eppKeyZ = 'z'

eppKeyLeft = 'Left'; eppKeyRight = 'Right'; eppKeyUp = 'Up'; eppKeyDown = 'Down'
eppKey0='0'; eppKey1='1'; eppKey2='2'; eppKey3='3'; eppKey4='4'; eppKey5='5'; eppKey6='6'
eppKey7='7'; eppKey8='8'; eppKey9='9'
eppKeyEscape='Escape'; eppKeyEnter='Return'; eppKeyBackspace='BackSpace'; eppKeyTab='Tab'
eppKeySpace='space'; eppKeyLShift='Shift_L'; eppKeyRShift='Shift_R'; eppKeyLControl='Control_L'
eppKeyRControl='Control_R'; eppKeyLAlt='Alt_L'; eppKeyRAlt='Alt_R'
eppKeyF1='F1'; eppKeyF2='F2'; eppKeyF3='F3'; eppKeyF4='F4'; eppKeyF5='F5'; eppKeyF6='F6'
eppKeyF7='F7'; eppKeyF8='F8'; eppKeyF9='F9'; eppKeyF10='F10'; eppKeyF11='F11'; eppKeyF12='F12'

# Mouse button constants
eppMouseLeft   = 1  # Left mouse button
eppMouseMiddle = 2  # Middle (scroll wheel) button
eppMouseRight  = 3  # Right mouse button

# === Globals ===
_epp_root = None
_epp_canvas = None
_epp_width = 800
_epp_height = 600
_epp_np = None            # numpy framebuffer: HxWx3 uint8
_epp_photo = None         # PhotoImage
_epp_img_id = None        # canvas image id
_epp_keys = set()
_epp_running = False
_epp_font = None

# === Init / Window ===
def eppWindowInit(width=800, height=600, title="EPP Window"):
    """Initialize window and framebuffer. Must be called before drawing."""
    global _epp_root, _epp_canvas, _epp_width, _epp_height, _epp_np, _epp_img_id, _epp_font, _epp_photo, _epp_running

    if _epp_root is not None:
        return  # already initialized

    _epp_width, _epp_height = int(width), int(height)
    _epp_np = np.zeros((_epp_height, _epp_width, 3), dtype=np.uint8)

    _epp_root = tk.Tk()
    _epp_root.title(title)
    _epp_root.protocol("WM_DELETE_WINDOW", _epp_on_close)
    _epp_root.resizable(False, False)

    _epp_canvas = tk.Canvas(_epp_root, width=_epp_width, height=_epp_height, highlightthickness=0)
    _epp_canvas.pack()
    # In eppWindowInit, after creating the canvas:
    _epp_canvas.bind("<Motion>", _on_mouse_move)
    _epp_canvas.bind("<ButtonPress>", _on_mouse_press)
    _epp_canvas.bind("<ButtonRelease>", _on_mouse_release)

    # initial blank image
    pil = Image.fromarray(_epp_np, 'RGB')
    _epp_photo = ImageTk.PhotoImage(pil, master=_epp_root)
    _epp_img_id = _epp_canvas.create_image(0, 0, anchor='nw', image=_epp_photo)

    # key bindings
    _epp_root.bind("<KeyPress>", lambda e: _epp_keys.add(e.keysym))
    _epp_root.bind("<KeyRelease>", lambda e: _epp_keys.discard(e.keysym))

    # default font
    try:
        _epp_font = ImageFont.load_default()
    except Exception:
        _epp_font = None

    _epp_running = True

def _epp_on_close():
    global _epp_running, _epp_root
    _epp_running = False
    try:
        if _epp_root:
            _epp_root.destroy()
    except Exception:
        pass
    _epp_root = None

def eppInput(key):
    """Return True if key currently pressed (keys are raw tkinter keysym strings)."""
    return key in _epp_keys

# === Low-level helpers ===
def _clamp_rect(x, y, w, h):
    x0 = max(0, int(x)); y0 = max(0, int(y))
    x1 = min(_epp_width, int(x + max(0, w))); y1 = min(_epp_height, int(y + max(0, h)))
    return x0, y0, x1, y1

# === Drawing primitives (numpy pixel ops) ===
def eppFillColor(r, g, b):
    """Fast fill entire screen color using numpy buffer."""
    global _epp_np
    if _epp_np is None:
        return
    _epp_np[:, :] = [int(r) & 255, int(g) & 255, int(b) & 255]

def eppDrawRect(x, y, w, h, color):
    """Fast filled rect (numpy slice)."""
    global _epp_np
    if _epp_np is None: return
    x0, y0, x1, y1 = _clamp_rect(x, y, w, h)
    _epp_np[y0:y1, x0:x1] = color

def eppDrawPoint(x, y, color):
    global _epp_np
    if _epp_np is None: return
    x = int(x); y = int(y)
    if 0 <= x < _epp_width and 0 <= y < _epp_height:
        _epp_np[y, x] = color

def eppDrawCircle(cx, cy, r, color):
    """Draw filled circle using numpy mask (fast)."""
    global _epp_np
    if _epp_np is None: return
    cx = int(cx); cy = int(cy); r = int(r)
    if r <= 0: return
    y, x = np.ogrid[0:_epp_height, 0:_epp_width]
    mask = (x - cx) ** 2 + (y - cy) ** 2 <= r * r
    _epp_np[mask] = color

def eppDrawOval(x, y, w, h, color):
    """Draw filled ellipse by creating mask scaled to bounding box."""
    global _epp_np
    if _epp_np is None: return
    x, y, w, h = int(x), int(y), int(w), int(h)
    if w <= 0 or h <= 0: return
    yy, xx = np.ogrid[0:_epp_height, 0:_epp_width]
    cx = x + w / 2.0; cy = y + h / 2.0
    rx = w / 2.0; ry = h / 2.0
    mask = ((xx - cx) / (rx if rx else 1)) ** 2 + ((yy - cy) / (ry if ry else 1)) ** 2 <= 1.0
    # clip mask to bbox for speed
    bbox_x0, bbox_y0, bbox_x1, bbox_y1 = _clamp_rect(x, y, w, h)
    sub = mask[bbox_y0:bbox_y1, bbox_x0:bbox_x1]
    _epp_np[bbox_y0:bbox_y1, bbox_x0:bbox_x1][sub] = color

# For lines, polygons, text, and images we use a temporary PIL draw onto the numpy array and blit back.
def _pil_draw_draw(fn):
    """Helper: create PIL image from buffer, call fn(ImageDraw.Draw), write back to numpy buffer."""
    global _epp_np
    pil = Image.fromarray(_epp_np, 'RGB')
    draw = ImageDraw.Draw(pil)
    fn(draw)
    _epp_np[:] = np.asarray(pil)

def eppDrawLine(x1, y1, x2, y2, color, width=1):
    global _epp_np
    if _epp_np is None: return
    def _fn(draw):
        draw.line([x1, y1, x2, y2], fill=tuple(color), width=int(width))
    _pil_draw_draw(_fn)

def eppDrawPolygon(points, color):
    global _epp_np
    if _epp_np is None: return
    def _fn(draw):
        draw.polygon(points, fill=tuple(color))
    _pil_draw_draw(_fn)

def eppDrawText(x, y, text, color, font=None):
    global _epp_np, _epp_font
    if _epp_np is None: return
    def _fn(draw):
        f = _epp_font if font is None else font
        draw.text((x, y), str(text), fill=tuple(color), font=f)
    _pil_draw_draw(_fn)

def eppDrawImage(x, y, src):
    """Paste a PIL image or path onto buffer at integer coords."""
    global _epp_np
    if _epp_np is None: return
    if isinstance(src, str):
        if not os.path.exists(src):
            return
        src_img = Image.open(src).convert('RGB')
    elif isinstance(src, Image.Image):
        src_img = src.convert('RGB')
    else:
        return
    w, h = src_img.size
    pil = Image.fromarray(_epp_np, 'RGB')
    pil.paste(src_img, (int(x), int(y)))
    _epp_np[:] = np.asarray(pil)

# === Presenting frame ===
def eppSlap():
    """Blit current numpy buffer to tkinter canvas. Safe if called each frame."""
    global _epp_photo, _epp_img_id, _epp_canvas, _epp_root, _epp_np, _epp_running
    if _epp_root is None:
        return False
    try:
        pil = Image.fromarray(_epp_np, 'RGB')
        _epp_photo = ImageTk.PhotoImage(pil, master=_epp_root)
        # update existing canvas image
        if _epp_img_id is None:
            _epp_img_id = _epp_canvas.create_image(0, 0, anchor='nw', image=_epp_photo)
        else:
            _epp_canvas.itemconfig(_epp_img_id, image=_epp_photo)
            # keep reference to avoid GC
            _epp_canvas.image = _epp_photo
        _epp_root.update_idletasks()
        _epp_root.update()
        return True
    except tk.TclError:
        # window closed
        _epp_running = False
        return False

# === Utilities ===
def eppClear():
    eppFillColor(0,0,0)

def eppRun(update_fn=None, fps=60):
    """High-level loop: calls update_fn each frame then eppSlap. Returns when window closed."""
    global _epp_running
    if _epp_root is None:
        eppWindowInit(_epp_width, _epp_height)
    delay = 1.0 / fps
    _epp_running = True
    last = time.time()
    while _epp_running:
        start = time.time()
        if update_fn:
            update_fn()
        ok = eppSlap()
        if not ok:
            break
        # simple fps limiter
        elapsed = time.time() - start
        to_sleep = delay - elapsed
        if to_sleep > 0:
            time.sleep(to_sleep)
    return

def eppQuit():
    _epp_on_close()
# --- Mouse constants ---
eppMouseLeft = 1
eppMouseMiddle = 2
eppMouseRight = 3

# --- Mouse state ---
epp_mouse_buttons = {eppMouseLeft: False, eppMouseMiddle: False, eppMouseRight: False}
epp_mouse_x, epp_mouse_y = 0, 0

def eppMousePos():
    """Return current mouse position as (x, y)."""
    global epp_mouse_x, epp_mouse_y
    return epp_mouse_x, epp_mouse_y

def eppMouseButton(button):
    """Return True if given mouse button is pressed."""
    return epp_mouse_buttons.get(button, False)

# --- Bind mouse events ---
def _on_mouse_move(event):
    global epp_mouse_x, epp_mouse_y
    epp_mouse_x, epp_mouse_y = event.x, event.y

def _on_mouse_press(event):
    if event.num in epp_mouse_buttons:
        epp_mouse_buttons[event.num] = True

def _on_mouse_release(event):
    if event.num in epp_mouse_buttons:
        epp_mouse_buttons[event.num] = False

_widgets = []
_epp_root = None


def _get_root():
    global _epp_root
    if _epp_root is None:
        raise RuntimeError("EPP GUI: Root window not set. Call eppGuiSetRoot(root) after eppWindowInit.")
    return _epp_root


def eppGuiSetRoot(root):
    """Set the Tk root for GUI widgets (call this right after eppWindowInit)."""
    global _epp_root
    _epp_root = root


def eppGuiLabel(text, x, y, font=("Arial", 14), color="black"):
    root = _get_root()
    label = tk.Label(root, text=text, font=font, fg=color)
    label.place(x=x, y=y)
    _widgets.append(label)
    return label


def eppGuiButton(text, x, y, func, width=10, height=2):
    root = _get_root()
    button = tk.Button(root, text=text, command=func, width=width, height=height)
    button.place(x=x, y=y)
    _widgets.append(button)
    return button


def eppGuiEntry(x, y, width=20):
    root = _get_root()
    entry = tk.Entry(root, width=width)
    entry.place(x=x, y=y)
    _widgets.append(entry)
    return entry


def eppGuiCheckButton(text, x, y, variable=None):
    root = _get_root()
    var = variable or tk.BooleanVar()
    check = tk.Checkbutton(root, text=text, variable=var)
    check.place(x=x, y=y)
    _widgets.append(check)
    return check, var


def eppGuiRadioButton(text, x, y, variable, value):
    root = _get_root()
    radio = tk.Radiobutton(root, text=text, variable=variable, value=value)
    radio.place(x=x, y=y)
    _widgets.append(radio)
    return radio


def eppGuiSlider(x, y, from_=0, to=100, orient='horizontal', length=200):
    root = _get_root()
    scale = tk.Scale(root, from_=from_, to=to, orient=orient, length=length)
    scale.place(x=x, y=y)
    _widgets.append(scale)
    return scale


def eppGuiTextBox(x, y, width=40, height=5):
    root = _get_root()
    textbox = tk.Text(root, width=width, height=height)
    textbox.place(x=x, y=y)
    _widgets.append(textbox)
    return textbox


def eppGuiClear():
    """Destroy all GUI widgets."""
    for widget in _widgets:
        widget.destroy()
    _widgets.clear()



# ---- end of epp.py ----
