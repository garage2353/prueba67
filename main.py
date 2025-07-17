import os
import json
import threading
import tkinter.messagebox as mb
import ttkbootstrap as ttk
from tkinter import Label
from iniciosesion import PantallaInicioSesion
from menu import PantallaMenu
from perfil import PantallaPerfil
from tutorial import PantallaTutorial
from clasificacion import PantallaClasificacion
from ayuda import PantallaAyuda
from tkinter import PhotoImage
from PIL import Image, ImageTk
import pyttsx3
from base_datos import conectar_bd

class Aplicacion(ttk.Window):
    def __init__(self):
        super().__init__(title="Timumachtikan", themename="flatly", size=(800, 600))
        self.state("zoomed")

        # Icono de la app
        icon_path = "logo.png"
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            self.icono = ImageTk.PhotoImage(img)
            self.iconphoto(False, self.icono)

        # Contenedor principal
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Motor de voz
        self.engine = pyttsx3.init()

        # Cargar usuario si existe
        self.usuario_id = None
        self.tutorial_ok = True
        if os.path.exists("usuario.json"):
            with open("usuario.json","r") as f:
                data = json.load(f)
            self.usuario_id = data.get("id")
            self._actualizar_tutorial_ok()

        # Crear pantallas
        self.frames = {}
        mappings = [
            ("inicio", PantallaInicioSesion),
            ("tutorial", PantallaTutorial),
            ("menu", PantallaMenu),
            ("perfil", PantallaPerfil),
            ("ayuda", PantallaAyuda),  # <-- Pantalla de ayuda reintegrada
        ]

        for name, cls in mappings:
            if name == "inicio":
                inst = cls(
                    self.container,
                    self.mostrar_pantalla,
                    self.actualizar_usuario
                )
                widget = inst
            elif name == "tutorial":
                inst = cls(
                    self.container,
                    self.usuario_id,
                    self.mostrar_pantalla,
                    self.finalizar_tutorial
                )
                widget = inst.frame
            else:
                # Para menu, perfil y ayuda
                widget = cls(self.container, self.mostrar_pantalla)
            widget.grid(row=0, column=0, sticky="nsew")
            self.frames[name] = widget

        # Determinar pantalla inicial
        if not os.path.exists("usuario.json"):
            inicial = "inicio"
        else:
            inicial = "menu" if self.tutorial_ok else "tutorial"
        self.mostrar_pantalla(inicial)

        # Bienvenida de voz en login
        if inicial == "inicio":
            threading.Thread(target=self.reproducir_bienvenida, daemon=True).start()

    def reproducir_bienvenida(self):
        self.engine.say("Bienvenido a Timumachtikan")
        self.engine.runAndWait()

    def mostrar_pantalla(self, nombre):
        # Redirige al tutorial si no completado
        if nombre == "menu" and hasattr(self, "tutorial_ok") and not self.tutorial_ok:
            nombre = "tutorial"

        # Clases dinámicas
        if nombre == "clases":
            if not os.path.exists("usuario.json"):
                mb.showwarning("Sin sesión", "Debes iniciar sesión antes de entrar a Clases.")
                nombre = "inicio"
            else:
                if "clases" not in self.frames:
                    from clases_lecciones import PantallaClases
                    frm = PantallaClases(self.container, self.usuario_id, self.mostrar_pantalla)
                    frm.grid(row=0, column=0, sticky="nsew")
                    self.frames["clases"] = frm

        # Clasificación dinámica
        if nombre == "clasificacion":
            if "clasificacion" not in self.frames:
                frm = PantallaClasificacion(self.container, self.mostrar_pantalla)
                frm.grid(row=0, column=0, sticky="nsew")
                self.frames["clasificacion"] = frm

        # Ayuda dinámica
        if nombre == "ayuda":
            if not os.path.exists("usuario.json"):
                mb.showwarning("Sin sesión", "Debes iniciar sesión antes de entrar a la ayuda.")
                nombre = "inicio"
            else:
                if "ayuda" not in self.frames:
                    frm = PantallaAyuda(self.container, self.mostrar_pantalla)
                    frm.grid(row=0, column=0, sticky="nsew")
                    self.frames["ayuda"] = frm

        frame = self.frames.get(nombre)
        if not frame:
            return

        if nombre == "perfil":
            frame.mostrar_perfil()
        frame.tkraise()

    def actualizar_usuario(self, usuario_id):
        self.usuario_id = usuario_id
        self._actualizar_tutorial_ok()
        for clave in ["clases", "clasificacion", "ayuda"]:  # <-- Reemplazado 'tienda'
            if clave in self.frames:
                self.frames[clave].destroy()
                del self.frames[clave]

    def _actualizar_tutorial_ok(self):
        if not self.usuario_id:
            self.tutorial_ok = False
            return
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("SELECT tutorial_completado FROM usuarios WHERE id=?", (self.usuario_id,))
        row = cur.fetchone()
        conn.close()
        self.tutorial_ok = bool(row and row[0])

    def finalizar_tutorial(self):
        if self.usuario_id:
            conn = conectar_bd()
            cur = conn.cursor()
            cur.execute("UPDATE usuarios SET tutorial_completado = 1 WHERE id = ?", (self.usuario_id,))
            conn.commit()
            conn.close()
        self.tutorial_ok = True
        self.mostrar_pantalla("menu")


        # PantallaMenu con integración de "Ayuda"
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

        # Botón Ayuda redirige a "ayuda"
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


if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()    


