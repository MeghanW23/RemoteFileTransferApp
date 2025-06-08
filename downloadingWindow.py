
import random
import sys
import tkinter as tk
from PIL import Image, ImageTk
from itertools import count, cycle

import settings

#TODO show progressbar 
class GifLabel(tk.Label):
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        frames = []

        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)

class DownloadWindow:
    def __init__(self):
        pass

    def start(self):
        self.root = tk.Tk()
        self.root.title("Remote File Transfer")
        self.root.resizable(False, False)
        self.root.geometry(f"+{settings.window_location['x']}+{settings.window_location['y']}")
        lbl = GifLabel(self.root)
        lbl.pack()
        lbl.load(random.choice(settings.gifs))
        self.title_label = tk.Label(master=self.root, text="Sending Files ...", font=("Helvetica", 20, "bold")).pack(padx=20, pady=20)
        self.root.mainloop()
    
    def update_from_transfer_progress(self, action: str):
        if action == "done":
            print("Transfer is Done")
            # clear window
            for widget in self.root.winfo_children():
                if widget.winfo_exists:
                    widget.destroy()

            self.ending_label = tk.Label(master=self.root, text="Transfer Finished! Exiting.", font=("Helvetica", 20, "bold")).pack(padx=20, pady=20)

            self.root.after(1000, self.root.destroy)

            sys.exit(0)
