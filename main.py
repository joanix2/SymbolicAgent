import sys
from tkinter import messagebox
from PIL import Image

from src.mask_editor_app import MaskEditorApp


def main():
    app = MaskEditorApp()

    # Lire le chemin de l'image depuis stdin (pipe bash)
    if not sys.stdin.isatty():
        image_path = sys.stdin.readline().strip()
        if image_path:
            try:
                img = Image.open(image_path).convert("RGB")
                app.original_image = img.copy()
                app.image = img
                app.mask = Image.new("L", app.image.size, 0)
                app.after(100, app.update_preview)
            except Exception as exc:
                messagebox.showerror("Erreur chargement image", str(exc))

    app.mainloop()


if __name__ == "__main__":
    main()
