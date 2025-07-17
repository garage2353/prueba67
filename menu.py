import os
import json
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from tkinter import Label

class PantallaMenu(ttk.Frame):
    def __init__(self, master, cambiar_pantalla):
        super().__init__(master)
        self.cambiar_pantalla = cambiar_pantalla
        self.pack_propagate(False)

        # Fondo redimensionable
        try:
            self.fondo_original = Image.open("fondo2.png")
            self.fondo_label = Label(self)
            self.fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bind("<Configure>", self.redimensionar_fondo)
        except Exception as e:
            print("⚠️ Error al cargar fondo2.png:", e)

        # Estilos
        style = ttk.Style()
        color_cafe = "#5a3d1e"
        style.configure("Cafe.TFrame", background=color_cafe)
        style.configure("Cafe.TButton",
                        background=color_cafe,
                        foreground="white",
                        font=("Helvetica", 14, "bold"),
                        borderwidth=0)
        style.map("Cafe.TButton",
                  background=[("active", "#7a5331"), ("pressed", "#3e2b17")],
                  foreground=[("disabled", "#ccc")])

        # Contenido principal
        main_frame = ttk.Frame(self, style="Cafe.TFrame", padding=30)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            main_frame,
            text="Timumachtikan",
            font=("Helvetica", 32, "bold"),
            foreground="#FFD700",
            background=color_cafe,
            anchor="center",
            bootstyle="inverse"
        ).pack(pady=(0, 40))

        ttk.Button(
            main_frame, text="Iniciar Clase", width=25, style="Cafe.TButton",
            command=lambda: self.cambiar_pantalla("clases")
        ).pack(pady=10)

        ttk.Button(
            main_frame, text="Clasificación", width=25, style="Cafe.TButton",
            command=lambda: self.cambiar_pantalla("clasificacion")
        ).pack(pady=10)

        ttk.Button(
            main_frame, text="Perfil", width=25, style="Cafe.TButton",
            command=lambda: self.cambiar_pantalla("perfil")
        ).pack(pady=10)

        ttk.Button(
            main_frame, text="Ayuda", width=25, style="Cafe.TButton",
            command=lambda: self.cambiar_pantalla("ayuda")
        ).pack(pady=10)


    def redimensionar_fondo(self, event):
        if not getattr(self, "fondo_original", None):
            return
        nuevo_ancho = max(1, event.width)
        nuevo_alto = max(1, event.height)
        redim = self.fondo_original.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
        foto = ImageTk.PhotoImage(redim)
        self.fondo_label.configure(image=foto)
        self.fondo_label.image = foto
