from tkinter import ttk


class ToolbarPanel(ttk.Frame):
    """Panneau gauche : sélection d'outil, paramètres, nom du symbole, informations."""

    def __init__(
        self,
        parent,
        *,
        current_tool,
        brush_size,
        bucket_tolerance,
        show_mask_overlay,
        base_name,
        dimensions_var,
        zoom_var,
        info_var,
        on_overlay_toggle,
        panel_width,
    ):
        super().__init__(parent, width=panel_width, padding=10)
        self.grid_propagate(False)
        self._panel_width = panel_width
        self._current_tool = current_tool
        self._brush_size = brush_size
        self._bucket_tolerance = bucket_tolerance
        self._show_mask_overlay = show_mask_overlay
        self._base_name = base_name
        self._dimensions_var = dimensions_var
        self._zoom_var = zoom_var
        self._info_var = info_var
        self._on_overlay_toggle = on_overlay_toggle
        self._build()

    def _build(self):
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
                variable=self._current_tool,
            ).pack(anchor="w", padx=8, pady=2)

        params_frame = ttk.LabelFrame(self, text="Paramètres")
        params_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(params_frame, text="Taille brush").pack(anchor="w", padx=8, pady=(8, 2))
        ttk.Spinbox(
            params_frame, from_=1, to=200, textvariable=self._brush_size, width=10
        ).pack(anchor="w", padx=8, pady=(0, 8))

        ttk.Label(params_frame, text="Tolérance seau").pack(anchor="w", padx=8, pady=(0, 2))
        ttk.Spinbox(
            params_frame, from_=0, to=255, textvariable=self._bucket_tolerance, width=10
        ).pack(anchor="w", padx=8, pady=(0, 8))

        ttk.Checkbutton(
            params_frame,
            text="Afficher overlay masque",
            variable=self._show_mask_overlay,
            command=self._on_overlay_toggle,
        ).pack(anchor="w", padx=8, pady=(0, 8))

        meta_frame = ttk.LabelFrame(self, text="Symbole")
        meta_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(meta_frame, text="Nom").pack(anchor="w", padx=8, pady=(8, 2))
        ttk.Entry(meta_frame, textvariable=self._base_name).pack(fill="x", padx=8, pady=(0, 8))

        info_frame = ttk.LabelFrame(self, text="Informations")
        info_frame.pack(fill="both", expand=True)

        ttk.Label(
            info_frame,
            textvariable=self._dimensions_var,
            justify="left",
            wraplength=self._panel_width - 40,
        ).pack(anchor="w", padx=8, pady=(8, 4))

        ttk.Label(
            info_frame,
            textvariable=self._zoom_var,
            justify="left",
            wraplength=self._panel_width - 40,
        ).pack(anchor="w", padx=8, pady=(0, 4))

        ttk.Separator(info_frame).pack(fill="x", padx=8, pady=8)

        ttk.Label(
            info_frame,
            textvariable=self._info_var,
            justify="left",
            wraplength=self._panel_width - 40,
        ).pack(anchor="w", padx=8, pady=(0, 8))
