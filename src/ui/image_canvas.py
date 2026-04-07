import tkinter as tk
from PIL import Image, ImageTk

HANDLE_HALF = 6  # rayon de hit-test des poignées en pixels canvas


class ImageCanvas(tk.Canvas):
    """Canvas image avec sélection crop déplaçable et redimensionnable."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#1e1e1e", highlightthickness=0, **kwargs)

        self.image = None
        self.display_scale = 1.0
        self.display_offset_x = 0
        self.display_offset_y = 0
        self.tk_preview = None

        # Mode crop
        self.crop_mode = False
        self._cx1 = None  # coordonnées image (toujours normalisées après drag)
        self._cy1 = None
        self._cx2 = None
        self._cy2 = None

        self._action = None          # "draw" | "move" | "resize"
        self._resize_handle = None   # "nw"|"n"|"ne"|"w"|"e"|"sw"|"s"|"se"
        self._drag_start = None      # (canvas_x, canvas_y) au moment du press
        self._box_snapshot = None    # (x1,y1,x2,y2) image au moment du press

        self.crop_rect_id = None
        self._handle_ids = []

        self.bind("<Motion>", self._on_motion)

    # ------------------------------------------------------------------
    # Affichage
    # ------------------------------------------------------------------

    def update_display(self):
        self.delete("all")
        self._handle_ids = []
        self.crop_rect_id = None

        if self.image is None:
            return

        canvas_w = max(self.winfo_width(), 100)
        canvas_h = max(self.winfo_height(), 100)

        scale = min(canvas_w / self.image.width, canvas_h / self.image.height)
        self.display_scale = scale

        disp_w = max(1, int(self.image.width * scale))
        disp_h = max(1, int(self.image.height * scale))

        display_image = (
            self.image.resize((disp_w, disp_h), Image.Resampling.NEAREST)
            if scale != 1.0
            else self.image
        )

        self.display_offset_x = max(0, (canvas_w - disp_w) // 2)
        self.display_offset_y = max(0, (canvas_h - disp_h) // 2)

        self.tk_preview = ImageTk.PhotoImage(display_image)
        self.create_image(
            self.display_offset_x, self.display_offset_y,
            anchor="nw", image=self.tk_preview,
        )

        # Redessiner l'overlay crop si sélection active
        if self._cx1 is not None:
            self._draw_crop_overlay()

    # ------------------------------------------------------------------
    # Conversion de coordonnées
    # ------------------------------------------------------------------

    def canvas_to_image_coords(self, canvas_x, canvas_y):
        if self.image is None:
            return None
        x = canvas_x - self.display_offset_x
        y = canvas_y - self.display_offset_y
        if x < 0 or y < 0:
            return None
        img_x = int(x / self.display_scale)
        img_y = int(y / self.display_scale)
        if 0 <= img_x < self.image.width and 0 <= img_y < self.image.height:
            return img_x, img_y
        return None

    def _img_to_canvas(self, ix, iy):
        return (
            ix * self.display_scale + self.display_offset_x,
            iy * self.display_scale + self.display_offset_y,
        )

    def _clamp_img(self, x, y):
        if self.image is None:
            return x, y
        return (
            max(0, min(x, self.image.width)),
            max(0, min(y, self.image.height)),
        )

    # ------------------------------------------------------------------
    # Poignées
    # ------------------------------------------------------------------

    def _get_handles(self):
        """Retourne dict nom → (cx, cy) en coordonnées canvas."""
        if self._cx1 is None:
            return {}
        x1c, y1c = self._img_to_canvas(self._cx1, self._cy1)
        x2c, y2c = self._img_to_canvas(self._cx2, self._cy2)
        mx, my = (x1c + x2c) / 2, (y1c + y2c) / 2
        return {
            "nw": (x1c, y1c), "n": (mx, y1c), "ne": (x2c, y1c),
            "w":  (x1c, my),                   "e":  (x2c, my),
            "sw": (x1c, y2c), "s": (mx, y2c),  "se": (x2c, y2c),
        }

    def _hit_handle(self, canvas_x, canvas_y):
        for name, (hx, hy) in self._get_handles().items():
            if abs(canvas_x - hx) <= HANDLE_HALF and abs(canvas_y - hy) <= HANDLE_HALF:
                return name
        return None

    def _inside_selection(self, canvas_x, canvas_y):
        if self._cx1 is None:
            return False
        x1c, y1c = self._img_to_canvas(self._cx1, self._cy1)
        x2c, y2c = self._img_to_canvas(self._cx2, self._cy2)
        return x1c < canvas_x < x2c and y1c < canvas_y < y2c

    # ------------------------------------------------------------------
    # Dessin de l'overlay
    # ------------------------------------------------------------------

    def _draw_crop_overlay(self):
        if self.crop_rect_id:
            self.delete(self.crop_rect_id)
        for hid in self._handle_ids:
            self.delete(hid)
        self._handle_ids = []

        x1c, y1c = self._img_to_canvas(self._cx1, self._cy1)
        x2c, y2c = self._img_to_canvas(self._cx2, self._cy2)

        self.crop_rect_id = self.create_rectangle(
            x1c, y1c, x2c, y2c, outline="yellow", width=2
        )

        for hx, hy in self._get_handles().values():
            hid = self.create_rectangle(
                hx - HANDLE_HALF, hy - HANDLE_HALF,
                hx + HANDLE_HALF, hy + HANDLE_HALF,
                fill="yellow", outline="white", width=1,
            )
            self._handle_ids.append(hid)

    # ------------------------------------------------------------------
    # API publique crop
    # ------------------------------------------------------------------

    def start_crop(self, canvas_x, canvas_y):
        if self._cx1 is not None:
            handle = self._hit_handle(canvas_x, canvas_y)
            if handle:
                self._action = "resize"
                self._resize_handle = handle
                self._drag_start = (canvas_x, canvas_y)
                self._box_snapshot = (self._cx1, self._cy1, self._cx2, self._cy2)
                return True
            if self._inside_selection(canvas_x, canvas_y):
                self._action = "move"
                self._drag_start = (canvas_x, canvas_y)
                self._box_snapshot = (self._cx1, self._cy1, self._cx2, self._cy2)
                return True

        # Nouvelle sélection
        pos = self.canvas_to_image_coords(canvas_x, canvas_y)
        if pos is None:
            return False
        self._cx1, self._cy1 = int(pos[0]), int(pos[1])
        self._cx2, self._cy2 = self._cx1, self._cy1
        self._action = "draw"
        self._drag_start = (canvas_x, canvas_y)
        self._draw_crop_overlay()
        return True

    def update_crop(self, canvas_x, canvas_y):
        if self._action == "draw":
            pos = self.canvas_to_image_coords(canvas_x, canvas_y)
            if pos:
                self._cx2, self._cy2 = int(pos[0]), int(pos[1])
        elif self._action == "move":
            self._do_move(canvas_x, canvas_y)
        elif self._action == "resize":
            self._do_resize(canvas_x, canvas_y)
        self._draw_crop_overlay()

    def _do_move(self, canvas_x, canvas_y):
        dx = round((canvas_x - self._drag_start[0]) / self.display_scale)
        dy = round((canvas_y - self._drag_start[1]) / self.display_scale)
        ox1, oy1, ox2, oy2 = self._box_snapshot
        bw, bh = ox2 - ox1, oy2 - oy1
        iw, ih = self.image.width, self.image.height
        new_x1 = max(0, min(ox1 + dx, iw - bw))
        new_y1 = max(0, min(oy1 + dy, ih - bh))
        self._cx1, self._cy1 = new_x1, new_y1
        self._cx2, self._cy2 = new_x1 + bw, new_y1 + bh

    def _do_resize(self, canvas_x, canvas_y):
        dx = round((canvas_x - self._drag_start[0]) / self.display_scale)
        dy = round((canvas_y - self._drag_start[1]) / self.display_scale)
        ox1, oy1, ox2, oy2 = self._box_snapshot
        x1, y1, x2, y2 = ox1, oy1, ox2, oy2
        h = self._resize_handle
        iw, ih = self.image.width, self.image.height
        if "w" in h: x1 = max(0, min(ox1 + dx, ox2 - 1))
        if "e" in h: x2 = max(ox1 + 1, min(ox2 + dx, iw))
        if "n" in h: y1 = max(0, min(oy1 + dy, oy2 - 1))
        if "s" in h: y2 = max(oy1 + 1, min(oy2 + dy, ih))
        self._cx1, self._cy1, self._cx2, self._cy2 = x1, y1, x2, y2

    def get_crop_box(self):
        if self._cx1 is None:
            return None
        return (
            int(min(self._cx1, self._cx2)), int(min(self._cy1, self._cy2)),
            int(max(self._cx1, self._cx2)), int(max(self._cy1, self._cy2)),
        )

    def clear_crop(self):
        self._cx1 = self._cy1 = self._cx2 = self._cy2 = None
        self._action = None
        self._resize_handle = None
        self._drag_start = None
        self._box_snapshot = None
        if self.crop_rect_id:
            self.delete(self.crop_rect_id)
            self.crop_rect_id = None
        for hid in self._handle_ids:
            self.delete(hid)
        self._handle_ids = []

    # ------------------------------------------------------------------
    # Curseur adaptatif
    # ------------------------------------------------------------------

    _HANDLE_CURSORS = {
        "nw": "top_left_corner",  "ne": "top_right_corner",
        "sw": "bottom_left_corner", "se": "bottom_right_corner",
        "n": "top_side", "s": "bottom_side",
        "w": "left_side", "e": "right_side",
    }

    def _on_motion(self, event):
        if not self.crop_mode or self._cx1 is None:
            self.config(cursor="")
            return
        handle = self._hit_handle(event.x, event.y)
        if handle:
            self.config(cursor=self._HANDLE_CURSORS[handle])
        elif self._inside_selection(event.x, event.y):
            self.config(cursor="fleur")
        else:
            self.config(cursor="crosshair")

