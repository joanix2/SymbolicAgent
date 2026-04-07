import subprocess
import tempfile
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from collections import deque
from datetime import datetime

from .crop_window import CropWindow
from .toolbar_panel import ToolbarPanel
from .action_panel import ActionPanel


class MaskEditorApp(tk.Tk):
    LEFT_PANEL_WIDTH = 280
    RIGHT_PANEL_WIDTH = 220

    def __init__(self):
        super().__init__()
        self.title("Mask Editor")
        self.geometry("1500x900")
        self.minsize(1100, 700)

        self.original_image = None
        self.image = None
        self.mask = None

        self.display_scale = 1.0
        self.display_offset_x = 0
        self.display_offset_y = 0
        self.tk_preview = None

        self.current_tool = tk.StringVar(value="brush")
        self.brush_size = tk.IntVar(value=8)
        self.bucket_tolerance = tk.IntVar(value=25)
        self.show_mask_overlay = tk.BooleanVar(value=True)
        self.base_name = tk.StringVar(value="spotify_icon")

        self.info_var = tk.StringVar(value="Aucune image")
        self.dimensions_var = tk.StringVar(value="Dimensions : -")
        self.zoom_var = tk.StringVar(value="Zoom : -")

        self.is_drawing = False
        self.last_px = None

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)

        self.left_panel = ToolbarPanel(
            self,
            current_tool=self.current_tool,
            brush_size=self.brush_size,
            bucket_tolerance=self.bucket_tolerance,
            show_mask_overlay=self.show_mask_overlay,
            base_name=self.base_name,
            dimensions_var=self.dimensions_var,
            zoom_var=self.zoom_var,
            info_var=self.info_var,
            on_overlay_toggle=self.update_preview,
            panel_width=self.LEFT_PANEL_WIDTH,
        )
        self.left_panel.grid(row=0, column=0, sticky="nsw")

        self.center_panel = ttk.Frame(self, padding=(0, 8, 0, 8))
        self.center_panel.grid(row=0, column=1, sticky="nsew")

        self.right_panel = ActionPanel(
            self,
            callbacks=[
                ("Capturer zone", self.start_capture),
                ("Charger image", self.load_image),
                ("Crop", self.open_crop),
                ("Inverser couleurs", self.invert_colors),
                ("Masque tout vider", self.clear_mask),
                ("Masque tout remplir", self.fill_mask),
                ("Sauvegarder image", self.save_image),
                ("Sauvegarder masque", self.save_mask),
            ],
            panel_width=self.RIGHT_PANEL_WIDTH,
        )
        self.right_panel.grid(row=0, column=2, sticky="nse")

        self._build_center_panel()

    def _build_center_panel(self):
        header = ttk.Frame(self.center_panel)
        header.pack(fill="x", padx=8, pady=(0, 8))

        ttk.Label(header, text="Image", font=("Arial", 12, "bold")).pack(side="left")
        ttk.Label(header, textvariable=self.dimensions_var).pack(side="right")

        canvas_frame = ttk.Frame(self.center_panel)
        canvas_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.canvas = tk.Canvas(canvas_frame, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def _bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Configure>", lambda e: self.update_preview())

    def start_capture(self):
        screenshot_path = os.path.join(tempfile.gettempdir(), "screenshot_symbol_editor.png")
        self.withdraw()
        self.update()
        try:
            result = subprocess.run(
                ["gnome-screenshot", "-a", "-f", screenshot_path],
                check=True,
            )
            if not os.path.isfile(screenshot_path) or os.path.getsize(screenshot_path) == 0:
                raise RuntimeError("Fichier capture vide ou absent.")
            img = Image.open(screenshot_path).convert("RGB")
            self.original_image = img.copy()
            self.image = img
            self.mask = Image.new("L", self.image.size, 0)
            self.update_preview()
        except subprocess.CalledProcessError:
            pass  # capture annulée par l'utilisateur
        except Exception as exc:
            messagebox.showerror("Erreur capture", str(exc))
        finally:
            self.deiconify()
            self.lift()

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if not path:
            return

        try:
            img = Image.open(path).convert("RGB")
            self.original_image = img.copy()
            self.image = img
            self.mask = Image.new("L", self.image.size, 0)
            self.update_preview()
        except Exception as exc:
            messagebox.showerror("Erreur chargement", str(exc))

    def open_crop(self):
        if self.image is None:
            messagebox.showwarning("Crop", "Aucune image chargée.")
            return
        CropWindow(self, self.image, self.apply_crop)

    def apply_crop(self, crop_box):
        x1, y1, x2, y2 = crop_box
        self.image = self.image.crop((x1, y1, x2, y2))
        if self.original_image is not None:
            self.original_image = self.original_image.crop((x1, y1, x2, y2))
        self.mask = self.mask.crop((x1, y1, x2, y2))
        self.update_preview()

    def invert_colors(self):
        if self.image is None:
            return
        arr = np.array(self.image)
        arr = 255 - arr
        self.image = Image.fromarray(arr.astype(np.uint8), "RGB")
        self.update_preview()

    def clear_mask(self):
        if self.image is None:
            return
        self.mask = Image.new("L", self.image.size, 0)
        self.update_preview()

    def fill_mask(self):
        if self.image is None:
            return
        self.mask = Image.new("L", self.image.size, 255)
        self.update_preview()

    def compose_preview(self):
        base = self.image.convert("RGBA")
        if not self.show_mask_overlay.get():
            return base

        mask_np = np.array(self.mask)
        overlay = np.zeros((self.image.height, self.image.width, 4), dtype=np.uint8)
        overlay[mask_np > 0] = [255, 0, 0, 110]
        overlay_img = Image.fromarray(overlay, "RGBA")
        return Image.alpha_composite(base, overlay_img)

    def update_preview(self):
        self.canvas.delete("all")

        if self.image is None:
            self.dimensions_var.set("Dimensions : -")
            self.zoom_var.set("Zoom : -")
            self.info_var.set("Aucune image")
            return

        preview = self.compose_preview()
        canvas_w = max(self.canvas.winfo_width(), 100)
        canvas_h = max(self.canvas.winfo_height(), 100)

        scale = min(canvas_w / preview.width, canvas_h / preview.height, 1.0)
        self.display_scale = scale

        disp_w = max(1, int(preview.width * scale))
        disp_h = max(1, int(preview.height * scale))

        if scale != 1.0:
            display_image = preview.resize((disp_w, disp_h), Image.Resampling.NEAREST)
        else:
            display_image = preview

        self.display_offset_x = max(0, (canvas_w - disp_w) // 2)
        self.display_offset_y = max(0, (canvas_h - disp_h) // 2)

        self.tk_preview = ImageTk.PhotoImage(display_image)
        self.canvas.create_image(
            self.display_offset_x,
            self.display_offset_y,
            anchor="nw",
            image=self.tk_preview,
        )

        w, h = self.image.size
        mask_np = np.array(self.mask)
        selected = int((mask_np > 0).sum())
        total = int(mask_np.size)
        percent = (selected / total * 100) if total else 0.0

        self.dimensions_var.set(f"Dimensions : {w} x {h}")
        self.zoom_var.set(f"Zoom : {scale * 100:.1f}%")
        self.info_var.set(
            f"Outil : {self.current_tool.get()}\n"
            f"Brush : {self.brush_size.get()}\n"
            f"Tolérance : {self.bucket_tolerance.get()}\n"
            f"Pixels masqués : {selected} / {total} ({percent:.1f}%)"
        )

    def canvas_to_image_coords(self, event):
        if self.image is None:
            return None

        x = event.x - self.display_offset_x
        y = event.y - self.display_offset_y

        if x < 0 or y < 0:
            return None

        img_x = int(x / self.display_scale)
        img_y = int(y / self.display_scale)

        if 0 <= img_x < self.image.width and 0 <= img_y < self.image.height:
            return img_x, img_y
        return None

    def on_canvas_press(self, event):
        if self.image is None:
            return

        pos = self.canvas_to_image_coords(event)
        if pos is None:
            return

        tool = self.current_tool.get()

        if tool in ("brush", "erase"):
            self.is_drawing = True
            self.last_px = pos
            self.paint_mask(pos, add=(tool == "brush"))
        elif tool in ("bucket_add", "bucket_remove"):
            self.bucket_fill(pos, add=(tool == "bucket_add"))

    def on_canvas_drag(self, event):
        if not self.is_drawing or self.image is None:
            return

        pos = self.canvas_to_image_coords(event)
        if pos is None:
            return

        tool = self.current_tool.get()
        self.paint_line(self.last_px, pos, add=(tool == "brush"))
        self.last_px = pos

    def on_canvas_release(self, event):
        self.is_drawing = False
        self.last_px = None

    def paint_mask(self, pos, add=True):
        radius = max(1, int(self.brush_size.get()))
        draw = ImageDraw.Draw(self.mask)
        x, y = pos
        fill = 255 if add else 0
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)
        self.update_preview()

    def paint_line(self, start, end, add=True):
        radius = max(1, int(self.brush_size.get()))
        draw = ImageDraw.Draw(self.mask)
        fill = 255 if add else 0
        draw.line([start, end], fill=fill, width=radius * 2)
        x, y = end
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)
        self.update_preview()

    def bucket_fill(self, start_pos, add=True):
        arr = np.array(self.image.convert("RGB"))
        mask_arr = np.array(self.mask)

        h, w, _ = arr.shape
        sx, sy = start_pos
        target = arr[sy, sx].astype(np.int16)
        tol = int(self.bucket_tolerance.get())

        visited = np.zeros((h, w), dtype=bool)
        queue = deque([(sx, sy)])
        visited[sy, sx] = True

        def close_enough(pixel):
            diff = np.abs(pixel.astype(np.int16) - target)
            return int(diff.sum()) <= tol * 3

        fill_value = 255 if add else 0

        while queue:
            x, y = queue.popleft()
            if not close_enough(arr[y, x]):
                continue

            mask_arr[y, x] = fill_value

            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and not visited[ny, nx]:
                    visited[ny, nx] = True
                    queue.append((nx, ny))

        self.mask = Image.fromarray(mask_arr.astype(np.uint8), mode="L")
        self.update_preview()

    def save_image(self):
        if self.image is None:
            return

        name = self.base_name.get().strip() or "icon"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=f"{name}_{ts}.png",
            filetypes=[("PNG", "*.png")],
        )
        if not path:
            return

        try:
            self.image.save(path)
        except Exception as exc:
            messagebox.showerror("Erreur sauvegarde", str(exc))

    def save_mask(self):
        if self.mask is None:
            return

        name = self.base_name.get().strip() or "icon"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=f"{name}_mask_{ts}.png",
            filetypes=[("PNG", "*.png")],
        )
        if not path:
            return

        try:
            self.mask.save(path)
        except Exception as exc:
            messagebox.showerror("Erreur sauvegarde", str(exc))
