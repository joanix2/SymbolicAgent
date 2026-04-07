import tkinter as tk

from .image_import import ImageImport
from .edition import Edition
from .export import Export


class EditorKernel(ImageImport, Edition, Export):
    """Noyau applicatif : agrège Import, Edition et Export via héritage mixin."""

    def __init__(self, app):
        self.app = app

        # --- État image ---
        self.original_image = None
        self.image = None
        self.mask = None

        # --- État dessin ---
        self.is_drawing = False
        self.last_px = None
        self.crop_mode = False

        # --- Variables tk ---
        self.current_tool = tk.StringVar(value="brush")
        self.brush_size = tk.IntVar(value=8)
        self.bucket_tolerance = tk.IntVar(value=25)
        self.show_mask_overlay = tk.BooleanVar(value=True)
        self.base_name = tk.StringVar(value="spotify_icon")

        self.info_var = tk.StringVar(value="Aucune image")
        self.dimensions_var = tk.StringVar(value="Dimensions : -")
        self.zoom_var = tk.StringVar(value="Zoom : -")

    @property
    def canvas(self):
        return self.app.canvas
