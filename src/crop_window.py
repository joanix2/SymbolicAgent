import tkinter as tk
from tkinter import ttk
from PIL import ImageTk


class CropWindow(tk.Toplevel):
    def __init__(self, parent, image, callback):
        super().__init__(parent)
        self.title("Crop")
        self.callback = callback
        self.image = image
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.crop_box = None

        self.tk_img = ImageTk.PhotoImage(self.image)
        self.canvas = tk.Canvas(
            self,
            width=self.image.width,
            height=self.image.height,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(bar, text="Valider", command=self.confirm).pack(side="left", padx=4)
        ttk.Button(bar, text="Annuler", command=self.destroy).pack(side="left", padx=4)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="lime",
            width=2,
        )

    def on_drag(self, event):
        if self.rect_id:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        self.crop_box = (
            min(self.start_x, event.x),
            min(self.start_y, event.y),
            max(self.start_x, event.x),
            max(self.start_y, event.y),
        )

    def confirm(self):
        if not self.crop_box:
            return
        x1, y1, x2, y2 = self.crop_box
        if x2 - x1 < 2 or y2 - y1 < 2:
            return
        self.callback(self.crop_box)
        self.destroy()
