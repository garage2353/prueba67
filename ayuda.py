import tkinter as tk
from ttkbootstrap import ttk
from PIL import Image, ImageTk

class PantallaAyuda(ttk.Frame):
    def __init__(self, master, volver_callback):
        super().__init__(master, style="CustomWhite.TFrame")
        self.volver_callback = volver_callback

        # Fondo
        try:
            self.fondo_original = Image.open("fondo2.png")
            self.fondo_tk = ImageTk.PhotoImage(self.fondo_original)
            self.label_fondo = tk.Label(self, image=self.fondo_tk)
            self.label_fondo.place(relwidth=1, relheight=1)
            self.bind("<Configure>", self._redimensionar_fondo)
        except Exception as e:
            print("No se pudo cargar fondo2.png:", e)

        # Contenedor
        self.contenedor = ttk.Frame(self, width=1000, height=800, style="CustomWhite.TFrame")
        self.contenedor.place(relx=0.5, rely=0.5, anchor="center")
        self.contenedor.pack_propagate(False)

        ttk.Label(
            self.contenedor,
            text="❓ Ayuda",
            font=("Helvetica", 20, "bold"),
            background="white",
            foreground="#5a3d1e"
        ).pack(pady=10)

        texto_ayuda = (
            "Bienvenido a la sección de ayuda.\n\n"
            "Aquí puedes encontrar información útil sobre cómo usar la aplicación.\n\n"
            "Si tienes dudas, contacta con soporte o revisa el manual de usuario."
        )

        ttk.Label(
            self.contenedor,
            text=texto_ayuda,
            font=("Helvetica", 14),
            background="white",
            foreground="#4b3621",
            wraplength=700,
            justify="left"
        ).pack(pady=20)

        # Botón volver
        ttk.Button(
            self.contenedor,
            text="Volver",
            style="Mi.TButton",
            command=lambda: self.volver_callback("menu")
        ).pack(pady=10)

    def _redimensionar_fondo(self, event):
        if self.fondo_original:
            redim = self.fondo_original.resize((event.width, event.height), Image.Resampling.LANCZOS)
            self.fondo_tk = ImageTk.PhotoImage(redim)
            self.label_fondo.config(image=self.fondo_tk)
