from . import _tkinter_pysick as tk
from . import _messagebox_pysick as messagebox

SickVersion = '2.68'

def about():
    """
    Show PySick about messagebox.

    Parameters:
        -
    """
    messagebox.showinfo(
        "",
        f"Hello, this is pysick(v.{SickVersion}), tk(-v{str(tk.TkVersion)}), Tcl(v-3.10)"
    )

if __name__ != "__main__":
    print(f"pysick (v.{SickVersion}) tk(-v{tk.TkVersion}) Tcl({tk.TclVersion})")