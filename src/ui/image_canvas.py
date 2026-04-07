import tkinter as tk
from PIL import Image, ImageTk
import numpy as np


class ImageCanvas(tk.Canvas):
    """Composant Canvas pour afficher et éditer les images avec support du crop."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#1e1e1e", highlightthickness=0, **kwargs)
        
        self.image = None
        self.display_scale = 1.0
        self.display_offset_x = 0
        self.display_offset_y = 0
        self.tk_preview = None
        
        # Mode crop
        self.crop_mode = False
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_current_x = None
        self.crop_current_y = None
        self.crop_rect_id = None

    def set_image(self, image):
        """Définir l'image à afficher."""
        self.image = image
        self.update_display()

    def update_display(self):
        """Mettre à jour l'affichage de l'image."""
        self.delete("all")

        if self.image is None:
            return

        canvas_w = max(self.winfo_width(), 100)
        canvas_h = max(self.winfo_height(), 100)

        # Supprimer la limite de 1.0 pour permettre le zoom sur les petites images
        scale = min(canvas_w / self.image.width, canvas_h / self.image.height)
        self.display_scale = scale

        disp_w = max(1, int(self.image.width * scale))
        disp_h = max(1, int(self.image.height * scale))

        if scale != 1.0:
            display_image = self.image.resize((disp_w, disp_h), Image.Resampling.NEAREST)
        else:
            display_image = self.image

        self.display_offset_x = max(0, (canvas_w - disp_w) // 2)
        self.display_offset_y = max(0, (canvas_h - disp_h) // 2)

        self.tk_preview = ImageTk.PhotoImage(display_image)
        self.create_image(
            self.display_offset_x,
            self.display_offset_y,
            anchor="nw",
            image=self.tk_preview,
        )

    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """Convertir les coordonnées canvas en coordonnées image."""
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

    def start_crop(self, canvas_x, canvas_y):
        """Débuter une sélection de crop."""
        pos = self.canvas_to_image_coords(canvas_x, canvas_y)
        if pos is None:
            return False
        self.crop_start_x, self.crop_start_y = pos
        self.crop_current_x, self.crop_current_y = pos
        if self.crop_rect_id:
            self.delete(self.crop_rect_id)
        return True

    def update_crop(self, canvas_x, canvas_y):
        """Mettre à jour la sélection de crop."""
        if self.crop_start_x is None:
            return
        
        pos = self.canvas_to_image_coords(canvas_x, canvas_y)
        if pos is None:
            return
        self.crop_current_x, self.crop_current_y = pos
        
        x1 = min(self.crop_start_x, self.crop_current_x)
        y1 = min(self.crop_start_y, self.crop_current_y)
        x2 = max(self.crop_start_x, self.crop_current_x)
        y2 = max(self.crop_start_y, self.crop_current_y)
        
        # Convertir en coordonnées canvas
        cx1 = x1 * self.display_scale + self.display_offset_x
        cy1 = y1 * self.display_scale + self.display_offset_y
        cx2 = x2 * self.display_scale + self.display_offset_x
        cy2 = y2 * self.display_scale + self.display_offset_y
        
        if self.crop_rect_id:
            self.coords(self.crop_rect_id, cx1, cy1, cx2, cy2)
        else:
            self.crop_rect_id = self.create_rectangle(
                cx1, cy1, cx2, cy2,
                outline="yellow",
                width=2
            )

    def get_crop_box(self):
        """Récupérer la boîte de crop sélectionnée."""
        if self.crop_start_x is None:
            return None
        
        x1 = min(self.crop_start_x, self.crop_current_x)
        y1 = min(self.crop_start_y, self.crop_current_y)
        x2 = max(self.crop_start_x, self.crop_current_x)
        y2 = max(self.crop_start_y, self.crop_current_y)
        
        return (x1, y1, x2, y2)

    def clear_crop(self):
        """Effacer la sélection de crop."""
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_current_x = None
        self.crop_current_y = None
        if self.crop_rect_id:
            self.delete(self.crop_rect_id)
            self.crop_rect_id = None
