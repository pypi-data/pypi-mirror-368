"""
PySick messagebox utility class.
"""
from . import _messagebox_pysick as messagebox


def ask_question(title, text):
    """
    Show a question dialog.

    Parameters:
        title (str)
        text (str)
    """
    return messagebox.askquestion(title, text)



def show_info(title, text):
    """
    Show an informational dialog.

    Parameters:
        title (str)
        text (str)
    """
    messagebox.showinfo(title, text)



def show_warning(title, text):
    """
    Show a warning dialog.

    Parameters:
        title (str)
        text (str)
    """
    messagebox.showwarning(title, text)



def show_error(title, text):
    """
    Show an error dialog.

    Parameters:
        title (str)
        text (str)
    """
    messagebox.showerror(title, text)



def about(title, text):
    """
    Show an about dialog.

    Parameters:
        title (str)
        text (str)
    """
    messagebox.showinfo(title, text)