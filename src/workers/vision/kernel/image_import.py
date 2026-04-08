import subprocess
import tempfile
import os
from tkinter import filedialog, messagebox
from PIL import Image


class ImageImport:
    """Mixin : capture écran et chargement d'image."""

    def start_capture(self):
        screenshot_path = os.path.join(tempfile.gettempdir(), "screenshot_symbol_editor.png")
        self.app.withdraw()
        self.app.update()
        try:
            subprocess.run(
                ["gnome-screenshot", "-a", "-f", screenshot_path],
                check=True,
            )
            if not os.path.isfile(screenshot_path) or os.path.getsize(screenshot_path) == 0:
                raise RuntimeError("Fichier capture vide ou absent.")
            self._load_img(Image.open(screenshot_path).convert("RGB"))
        except subprocess.CalledProcessError:
            pass
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
