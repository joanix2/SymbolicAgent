from tkinter import ttk


class ActionPanel(ttk.Frame):
    """Panneau droit : boutons d'actions et aide contextuelle."""

    def __init__(self, parent, kernel):
        super().__init__(parent, width=220, padding=10)
        self.grid_propagate(False)
        self._build(kernel)

    def _build(self, kernel):
        ttk.Label(self, text="Actions", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

        callbacks = [
            ("Capturer zone", kernel.start_capture),
            ("Charger image", kernel.load_image),
            ("Crop", kernel.open_crop),
            ("Inverser couleurs", kernel.invert_colors),
            ("Masque tout vider", kernel.clear_mask),
            ("Masque tout remplir", kernel.fill_mask),
            ("Sauvegarder image", kernel.save_image),
            ("Sauvegarder masque", kernel.save_mask),
        ]

        for text, command in callbacks:
            ttk.Button(self, text=text, command=command).pack(fill="x", pady=4)

        ttk.Separator(self).pack(fill="x", pady=12)

        ttk.Label(
            self,
            text=(
                "Usage\n\n"
                "• Brush : ajoute au masque\n"
                "• Erase : retire du masque\n"
                "• Bucket add : remplit une zone proche\n"
                "• Bucket remove : retire une zone proche"
            ),
            justify="left",
            wraplength=200,
        ).pack(anchor="w")
