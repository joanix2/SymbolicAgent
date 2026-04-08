from tkinter import filedialog, messagebox
from datetime import datetime


class Export:
    """Mixin : sauvegarde image et masque."""

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
