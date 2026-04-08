from tkinter import messagebox
from PIL import Image, ImageDraw
import numpy as np
from collections import deque


class Edition:
    """Mixin : crop, peinture du masque, bucket fill, rendu."""

    # ------------------------------------------------------------------
    # Crop
    # ------------------------------------------------------------------

    def open_crop(self):
        if self.image is None:
            messagebox.showwarning("Crop", "Aucune image chargée.")
            return
        self.crop_mode = True
        self.canvas.crop_mode = True
        self.canvas.config(cursor="crosshair")

    def confirm_crop(self):
        if not self.crop_mode:
            return
        crop_box = self.canvas.get_crop_box()
        if crop_box is None:
            messagebox.showwarning("Crop", "Aucune sélection.")
            return
        x1, y1, x2, y2 = crop_box
        if x2 - x1 < 2 or y2 - y1 < 2:
            messagebox.showwarning("Crop", "Sélection trop petite.")
            return
        self._apply_crop(crop_box)
        self.cancel_crop()

    def cancel_crop(self):
        self.crop_mode = False
        self.canvas.crop_mode = False
        self.canvas.clear_crop()
        self.update_preview()

    def _apply_crop(self, crop_box):
        x1, y1, x2, y2 = crop_box
        self.image = self.image.crop((x1, y1, x2, y2))
        if self.original_image is not None:
            self.original_image = self.original_image.crop((x1, y1, x2, y2))
        self.mask = self.mask.crop((x1, y1, x2, y2))
        messagebox.showinfo("Crop", "Image recadrée avec succès.")
        self.update_preview()

    # ------------------------------------------------------------------
    # Masque
    # ------------------------------------------------------------------

    def invert_colors(self):
        if self.image is None:
            return
        arr = np.array(self.image)
        self.image = Image.fromarray((255 - arr).astype(np.uint8), "RGB")
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

    # ------------------------------------------------------------------
    # Rendu
    # ------------------------------------------------------------------

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
        if self.image is None:
            self.dimensions_var.set("Dimensions : -")
            self.zoom_var.set("Zoom : -")
            self.info_var.set("Aucune image")
            return

        preview = self.compose_preview()
        self.canvas.image = preview
        self.canvas.update_display()

        w, h = self.image.size
        mask_np = np.array(self.mask)
        selected = int((mask_np > 0).sum())
        total = int(mask_np.size)
        percent = (selected / total * 100) if total else 0.0

        self.dimensions_var.set(f"Dimensions : {w} x {h}")
        self.zoom_var.set(f"Zoom : {self.canvas.display_scale * 100:.1f}%")
        self.info_var.set(
            f"Outil : {self.current_tool.get()}\n"
            f"Brush : {self.brush_size.get()}\n"
            f"Tolérance : {self.bucket_tolerance.get()}\n"
            f"Pixels masqués : {selected} / {total} ({percent:.1f}%)"
        )

    # ------------------------------------------------------------------
    # Événements canvas
    # ------------------------------------------------------------------

    def on_canvas_press(self, event):
        if self.image is None:
            return
        if self.crop_mode:
            self.canvas.start_crop(event.x, event.y)
            return
        pos = self.canvas.canvas_to_image_coords(event.x, event.y)
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
        if self.crop_mode:
            self.canvas.update_crop(event.x, event.y)
            return
        if not self.is_drawing or self.image is None:
            return
        pos = self.canvas.canvas_to_image_coords(event.x, event.y)
        if pos is None:
            return
        tool = self.current_tool.get()
        self.paint_line(self.last_px, pos, add=(tool == "brush"))
        self.last_px = pos

    def on_canvas_release(self, event):
        self.is_drawing = False
        self.last_px = None

    # ------------------------------------------------------------------
    # Dessin sur masque
    # ------------------------------------------------------------------

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
            return int(np.abs(pixel.astype(np.int16) - target).sum()) <= tol * 3

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
