import _tkinter as tk
import pysick


def show(engine, image_path, x=0, y=0, anchor="nw"):
    """
    Displays an image on the engine's canvas.

    Parameters:
        engine     : InGine instance from pysick
        image_path : Path to the image file (.png, .jpg, etc.)
        x       : Position on canvas
        y       : Position on the canvas
        anchor     : Anchor point (default: "nw" = top-left)
    """

    import os

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"[pysick.photo] Image file not found: {image_path}")

    img = tk.PhotoImage(file=image_path)

    engine._canvas.create_image(x, y, image=img, anchor=anchor)
    engine._canvas.image = img  # prevent garbage collection

    print(f"[pysick.photo] Displayed: {image_path}")


def extract_frames(video_path, output_folder, size):

    import os

    os.makedirs(output_folder, exist_ok=True)
    w, h = size
    cmd = f'ffmpeg -i "{video_path}" -vf scale={w}:{h} "{output_folder}/frame_%04d.png"'
    os.system(cmd)


def cleanup_frames(folder):

    import os

    for f in os.listdir(folder):

        os.remove(os.path.join(folder, f))

    os.rmdir(folder)



def play(video_path, resolution=(320, 240), fps=24, cleanup=True):

    """
    Public method to play a video on a given engine (InGine instance).

    Parameters:
        video_path  : Path to video file (.mp4)
        resolution  : Tuple (width, height)
        fps         : Frames per second
        cleanup     : Whether to delete frames after playback
    """
    import os
    import pysick
    engine = pysick.ingine
    canvas = engine._canvas

    _root = canvas.winfo_toplevel()

    frame_folder = "_video_frames"

    video_path = os.path.abspath(video_path)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"[pysick.video] Video not found: {video_path}")

    extract_frames(video_path, frame_folder, resolution)

    frames = sorted(f for f in os.listdir(frame_folder) if f.endswith(".png"))

    if not frames:
        raise RuntimeError("[pysick.video] No frames extracted. ffmpeg may have failed.")

    index = 0

    tk_img = tk.PhotoImage(file=os.path.join(frame_folder, frames[0]))
    img_id = canvas.create_image(0, 0, anchor="nw", image=tk_img)

    def advance():

        nonlocal index, tk_img

        if index < len(frames):

            frame_path = os.path.join(frame_folder, frames[index])
            tk_img = tk.PhotoImage(file=frame_path)

            canvas.itemconfig(img_id, image=tk_img)
            canvas.image = tk_img  # avoid garbage collection

            index += 1

            _root.after(int(1000 / fps), advance)

        else:

            if cleanup:
                cleanup_frames(frame_folder)

            print("[pysick.video] Video playback finished.")

    advance()