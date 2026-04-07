from tkinter import ttk


class ActionPanel(ttk.Frame):
    """Panneau droit : boutons d'actions et aide contextuelle."""

    def __init__(self, parent, *, callbacks, panel_width):
        super().__init__(parent, width=panel_width, padding=10)
        self.grid_propagate(False)
        self._panel_width = panel_width
        self._build(callbacks)

    def _build(self, callbacks):
        ttk.Label(self, text="Actions", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

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
            wraplength=self._panel_width - 20,
        ).pack(anchor="w")
