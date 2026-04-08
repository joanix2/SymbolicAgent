import tkinter as tk
from tkinter import messagebox, ttk

from ..kernel import parse
from ..kernel.correction import get_vocab, save_vocab


class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat — Analyse NLP")
        self.minsize(480, 320)
        self._build_ui()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        chat_frame = ttk.Frame(notebook, padding=12)
        notebook.add(chat_frame, text="  Chat  ")
        self._build_chat_tab(chat_frame)

        dict_frame = ttk.Frame(notebook, padding=12)
        notebook.add(dict_frame, text="  Dictionnaire  ")
        self._build_dict_tab(dict_frame)

    # ── Onglet Chat ───────────────────────────────────────────────────────────

    def _build_chat_tab(self, parent):
        ttk.Label(parent, text="Message :").pack(anchor=tk.W, pady=(0, 4))

        row = ttk.Frame(parent)
        row.pack(fill=tk.X)

        self._entry = ttk.Entry(row, width=50, font=("Helvetica", 12))
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._entry.bind("<Return>", self._on_send)
        self._entry.focus()

        ttk.Button(row, text="Envoyer", command=self._on_send).pack(
            side=tk.LEFT, padx=(8, 0)
        )

    def _on_send(self, _event=None):
        text = self._entry.get().strip()
        if not text:
            return
        result = parse(text)
        print("\n" + "=" * 50)
        print(result)
        print("=" * 50)
        self._entry.delete(0, tk.END)

    # ── Onglet Dictionnaire ───────────────────────────────────────────────────

    def _build_dict_tab(self, parent):
        ttk.Label(parent, text="Vocabulaire personnalisé (correcteur orthographique) :").pack(
            anchor=tk.W, pady=(0, 4)
        )

        # Liste + scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(list_frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._listbox = tk.Listbox(
            list_frame,
            yscrollcommand=sb.set,
            selectmode=tk.SINGLE,
            width=36,
            height=14,
            font=("Helvetica", 11),
        )
        self._listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self._listbox.yview)

        self._refresh_list()

        # Ligne ajout / suppression
        add_row = ttk.Frame(parent)
        add_row.pack(fill=tk.X, pady=(8, 0))

        self._new_word_var = tk.StringVar()
        entry = ttk.Entry(add_row, textvariable=self._new_word_var, width=28)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.bind("<Return>", self._on_add)

        ttk.Button(add_row, text="Ajouter", command=self._on_add).pack(
            side=tk.LEFT, padx=(4, 0)
        )
        ttk.Button(add_row, text="Supprimer", command=self._on_remove).pack(
            side=tk.LEFT, padx=(4, 0)
        )

    def _refresh_list(self):
        self._listbox.delete(0, tk.END)
        for word in sorted(get_vocab()):
            self._listbox.insert(tk.END, word)

    def _on_add(self, _event=None):
        word = self._new_word_var.get().strip().lower()
        if not word:
            return
        current = list(self._listbox.get(0, tk.END))
        if word in current:
            messagebox.showinfo("Doublon", f"« {word} » est déjà dans le dictionnaire.")
            return
        save_vocab(current + [word])
        self._refresh_list()
        self._new_word_var.set("")

    def _on_remove(self):
        sel = self._listbox.curselection()
        if not sel:
            return
        word = self._listbox.get(sel[0])
        if messagebox.askyesno("Confirmer", f"Supprimer « {word} » ?"):
            current = list(self._listbox.get(0, tk.END))
            current.remove(word)
            save_vocab(current)
            self._refresh_list()


def run():
    app = ChatApp()
    app.mainloop()
