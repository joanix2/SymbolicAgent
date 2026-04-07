from tkinter import ttk

PANEL_WIDTH = 280


class ToolbarPanel(ttk.Frame):
    """Panneau gauche : sélection d'outil, paramètres, nom du symbole, informations."""

    def __init__(self, parent, kernel):
        super().__init__(parent, width=PANEL_WIDTH, padding=10)
        self.grid_propagate(False)
        self._k = kernel
        self._build()

    def _build(self):
        k = self._k
        ttk.Label(self, text="Outils", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

        tools_frame = ttk.LabelFrame(self, text="Sélection")
        tools_frame.pack(fill="x", pady=(0, 10))

        for label, value in [
            ("Brush", "brush"),
            ("Erase", "erase"),
            ("Bucket add", "bucket_add"),
            ("Bucket remove", "bucket_remove"),
        ]:
            ttk.Radiobutton(
                tools_frame,
                text=label,
                value=value,
                variable=k.current_tool,
            ).pack(anchor="w", padx=8, pady=2)

        params_frame = ttk.LabelFrame(self, text="Paramètres")
        params_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(params_frame, text="Taille brush").pack(anchor="w", padx=8, pady=(8, 2))
        ttk.Spinbox(
            params_frame, from_=1, to=200, textvariable=k.brush_size, width=10
        ).pack(anchor="w", padx=8, pady=(0, 8))

        ttk.Label(params_frame, text="Tolérance seau").pack(anchor="w", padx=8, pady=(0, 2))
        ttk.Spinbox(
            params_frame, from_=0, to=255, textvariable=k.bucket_tolerance, width=10
        ).pack(anchor="w", padx=8, pady=(0, 8))

        ttk.Checkbutton(
            params_frame,
            text="Afficher overlay masque",
            variable=k.show_mask_overlay,
            command=k.update_preview,
        ).pack(anchor="w", padx=8, pady=(0, 8))

        meta_frame = ttk.LabelFrame(self, text="Symbole")
        meta_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(meta_frame, text="Nom").pack(anchor="w", padx=8, pady=(8, 2))
        ttk.Entry(meta_frame, textvariable=k.base_name).pack(fill="x", padx=8, pady=(0, 8))

        info_frame = ttk.LabelFrame(self, text="Informations")
        info_frame.pack(fill="both", expand=True)

        ttk.Label(
            info_frame,
            textvariable=k.dimensions_var,
            justify="left",
            wraplength=PANEL_WIDTH - 40,
        ).pack(anchor="w", padx=8, pady=(8, 4))

        ttk.Label(
            info_frame,
            textvariable=k.zoom_var,
            justify="left",
            wraplength=PANEL_WIDTH - 40,
        ).pack(anchor="w", padx=8, pady=(0, 4))

        ttk.Separator(info_frame).pack(fill="x", padx=8, pady=8)

        ttk.Label(
            info_frame,
            textvariable=k.info_var,
            justify="left",
            wraplength=PANEL_WIDTH - 40,
        ).pack(anchor="w", padx=8, pady=(0, 8))
