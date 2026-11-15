"""Take a series of screenshots at a fixed interval.

Requires: pip install pillow
"""
import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

from PIL import ImageGrab


class App:
    def __init__(self, root):
        self.root = root
        root.title("Screenshot Series")
        root.resizable(False, False)
        self.running = False
        self.closed = False
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        tk.Label(root, text="Number of screenshots:").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.count = tk.Entry(root, width=10)
        self.count.insert(0, "5")
        self.count.grid(row=0, column=1, sticky="w", padx=8)

        tk.Label(root, text="Delay (seconds):").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.delay = tk.Entry(root, width=10)
        self.delay.insert(0, "2")
        self.delay.grid(row=1, column=1, sticky="w", padx=8)

        tk.Label(root, text="Save to:").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.folder = tk.StringVar(value=os.path.expanduser("~"))
        tk.Entry(root, textvariable=self.folder, width=35).grid(row=2, column=1, padx=8)
        tk.Button(root, text="Browse...", command=self.browse).grid(row=2, column=2, padx=8)

        self.stop_event = threading.Event()
        buttons = tk.Frame(root)
        buttons.grid(row=3, column=0, columnspan=3, pady=8)
        self.start_btn = tk.Button(buttons, text="Start", width=12, command=self.start)
        self.start_btn.pack(side="left", padx=4)
        self.stop_btn = tk.Button(buttons, text="Stop", width=12, command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=4)

        self.status = tk.Label(root, text="Ready")
        self.status.grid(row=4, column=0, columnspan=3, pady=(0, 8))

    def browse(self):
        path = filedialog.askdirectory(initialdir=self.folder.get())
        if path:
            self.folder.set(path)

    def start(self):
        try:
            count = int(self.count.get())
            delay = float(self.delay.get())
            if count < 1 or delay < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input", "Enter a whole number >= 1 and a delay >= 0.")
            return

        folder = self.folder.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Invalid folder", f"Folder does not exist:\n{folder}")
            return

        self.running = True
        self.stop_event.clear()
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.root.iconify()  # minimize so the window isn't in the shots
        # daemon=False: Python waits for the capture to finish before exiting
        threading.Thread(target=self.capture, args=(count, delay, folder), daemon=False).start()

    def stop(self):
        self.stop_event.set()
        self.stop_btn.config(state="disabled")
        self.status.config(text="Stopping...")

    def on_close(self):
        if self.running:
            # Hide instead of quitting; capture keeps going, then the app exits
            self.closed = True
            self.root.withdraw()
        else:
            self.root.destroy()

    def capture(self, count, delay, folder):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved = 0
        # Event.wait() acts like sleep() but returns early when Stop is pressed
        if not self.stop_event.wait(1):  # give the window time to minimize
            for i in range(1, count + 1):
                path = os.path.join(folder, f"screenshot_{stamp}_{i:03d}.png")
                ImageGrab.grab(all_screens=True).save(path)
                saved = i
                self.root.after(0, self.status.config, {"text": f"Saved {i}/{count}"})
                if i < count and self.stop_event.wait(delay):
                    break
        self.root.after(0, self.done, saved, count, folder)

    def done(self, saved, count, folder):
        self.running = False
        if self.closed:
            self.root.destroy()  # user closed the window earlier; just exit
            return
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.root.deiconify()
        word = "Stopped" if saved < count else "Done"
        self.status.config(text=f"{word}: {saved}/{count} screenshots saved")
        messagebox.showinfo(word, f"Saved {saved} of {count} screenshots to:\n{folder}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
