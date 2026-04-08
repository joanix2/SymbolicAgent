import os
from tkinter import filedialog, messagebox
from PIL import Image
import pyautogui


class ImageImport:
    """Mixin : capture écran et chargement d'image."""

    def start_capture(self):
        self.app.withdraw()
        self.app.update()
        try:
            # Utilise pyautogui pour garantir la même pipeline couleur que le template matching CLI
            screenshot = pyautogui.screenshot()
            self._load_img(screenshot.convert("RGB"))
        except Exception as exc:
            messagebox.showerror("Erreur capture", str(exc))
        finally:
            self.app.deiconify()
            self.app.lift()

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if not path:
            return
        try:
            self._load_img(Image.open(path).convert("RGB"))
        except Exception as exc:
            messagebox.showerror("Erreur chargement", str(exc))

    def _load_img(self, img):
        self.original_image = img.copy()
        self.image = img
        self.mask = Image.new("L", img.size, 0)
        self.update_preview()
