import tkinter as tk
from tkinter import ttk

from ..kernel.editor_kernel import EditorKernel
from .image_canvas import ImageCanvas
from .toolbar_panel import ToolbarPanel
from .action_panel import ActionPanel


class MaskEditorApp(tk.Tk):
    LEFT_PANEL_WIDTH = 280
    RIGHT_PANEL_WIDTH = 220

    def __init__(self):
        super().__init__()
        self.title("Mask Editor")
        self.geometry("1500x900")
        self.minsize(1100, 700)

        self.fullscreen_mode = False
        self.kernel = EditorKernel(self)

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)

        self.left_panel = ToolbarPanel(self, self.kernel)
        self.left_panel.grid(row=0, column=0, sticky="nsw")

        self.center_panel = ttk.Frame(self, padding=(0, 8, 0, 8))
        self.center_panel.grid(row=0, column=1, sticky="nsew")

        self.right_panel = ActionPanel(self, self.kernel)
        self.right_panel.grid(row=0, column=2, sticky="nse")

        self._build_center_panel()

    def _build_center_panel(self):
        self.header = ttk.Frame(self.center_panel)
        self.header.pack(fill="x", padx=8, pady=(0, 8))

        ttk.Label(self.header, text="Image", font=("Arial", 12, "bold")).pack(side="left")
        ttk.Label(self.header, textvariable=self.kernel.dimensions_var).pack(side="right")

        self.canvas_frame = ttk.Frame(self.center_panel)
        self.canvas_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.canvas = ImageCanvas(self.canvas_frame)
        self.canvas.pack(fill="both", expand=True)

    def _bind_events(self):
        k = self.kernel
        self.canvas.bind("<ButtonPress-1>", k.on_canvas_press)
        self.canvas.bind("<B1-Motion>", k.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", k.on_canvas_release)
        self.canvas.bind("<Configure>", lambda e: k.update_preview())
        self.bind("<Return>", lambda e: k.confirm_crop() if k.crop_mode else None)
        self.bind("<Escape>", self._on_escape_press)

    def _on_escape_press(self, event):
        if self.kernel.crop_mode:
            self.kernel.cancel_crop()
        elif self.kernel.image and self.fullscreen_mode:
            self._toggle_panels()

    def _toggle_panels(self):
        """Bascule entre le mode plein écran (image) et le mode édition (panneaux visibles)."""
        self.fullscreen_mode = not self.fullscreen_mode
        if self.fullscreen_mode:
            self.left_panel.grid_remove()
            self.right_panel.grid_remove()
            self.header.pack_forget()
            self.canvas_frame.pack_forget()
            self.canvas_frame.pack(fill="both", expand=True, padx=0, pady=0)
        else:
            self.left_panel.grid()
            self.right_panel.grid()
            self.canvas_frame.pack_forget()
            self.header.pack(fill="x", padx=8, pady=(0, 8))
            self.canvas_frame.pack(fill="both", expand=True, padx=8, pady=8)


