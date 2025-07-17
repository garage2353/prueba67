import os
import json
import sqlite3
from tkinter import messagebox
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Label

class PantallaPerfil(ttk.Frame):
    def __init__(self, master, cambiar_pantalla):
        super().__init__(master, style="Custom.TFrame")
        self.cambiar_pantalla = cambiar_pantalla
        self.pack_propagate(False)

        # Estilos base
        style = ttk.Style()
        style.configure("Custom.TFrame", background="white")
        style.configure("Custom.TLabel", background="white", foreground="#5a3d1e")
        style.configure("Mi.TButton",
                        font=("Helvetica", 12),
                        background="#7a5331",
                        foreground="white",
                        borderwidth=0)
        style.map("Mi.TButton",
                  background=[("active", "#7a5331"), ("pressed", "#3e2b17")],
                  foreground=[("disabled", "#ccc")])

        # Fondo opcional
        try:
            self.fondo_original = Image.open("fondo2.png")
            self.fondo_label = Label(self)
            self.fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bind("<Configure>", self.redimensionar_fondo)
        except:
            self.fondo_original = None

        # Contenedor donde pintaremos el perfil
        self.frame_perfil = ttk.Frame(self, style="Custom.TFrame", padding=30)
        self.frame_perfil.place(relx=0.5, rely=0.5, anchor="center")

    def redimensionar_fondo(self, event):
        if not self.fondo_original:
            return
        ancho, alto = max(1, event.width), max(1, event.height)
        img = self.fondo_original.resize((ancho, alto), Image.Resampling.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        self.fondo_label.configure(image=foto)
        self.fondo_label.image = foto

    def mostrar_perfil(self):
        # Limpiar datos anteriores
        for w in self.frame_perfil.winfo_children():
            w.destroy()

        # Cargar usuario
        if not os.path.exists("usuario.json"):
            messagebox.showerror("Error", "No se encontró la información del usuario.")
            self.cambiar_pantalla("inicio")
            return

        with open("usuario.json", "r", encoding="utf-8") as f:
            usuario = json.load(f)
        nombre = usuario.get("nombre", "Desconocido")
        correo = usuario.get("correo", "Desconocido")

        # Consultas BD
        conexion = sqlite3.connect("traductor.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE correo=?", (correo,))
        res = cursor.fetchone()
        usuario_id = res[0] if res else None

        total = cursor.execute("SELECT COUNT(*) FROM lecciones").fetchone()[0] if usuario_id else 0
        comp = cursor.execute(
            "SELECT COUNT(*) FROM progreso WHERE usuario_id=? AND completada=1",
            (usuario_id,)
        ).fetchone()[0] if usuario_id else 0
        conexion.close()
        pend = total - comp

        if comp == 0:
            nivel = "Principiante"
        elif comp < 24:
            nivel = "Básico"
        elif comp < 48:
            nivel = "Intermedio"
        else:
            nivel = "Avanzado"

        # Mostrar datos
        ttk.Label(self.frame_perfil, text="Mi Perfil", font=("Helvetica", 24, "bold"), style="Custom.TLabel").pack(pady=10)
        ttk.Label(self.frame_perfil, text=f"Nombre: {nombre}", font=("Helvetica", 16), style="Custom.TLabel").pack(pady=5)
        ttk.Label(self.frame_perfil, text=f"Correo: {correo}", font=("Helvetica", 16), style="Custom.TLabel").pack(pady=5)
        ttk.Label(self.frame_perfil, text=f"Lecciones completadas: {comp}", font=("Helvetica", 16), style="Custom.TLabel").pack(pady=5)
        ttk.Label(self.frame_perfil, text=f"Lecciones pendientes: {pend}", font=("Helvetica", 16), style="Custom.TLabel").pack(pady=5)
        ttk.Label(self.frame_perfil, text=f"Nivel de aprendizaje: {nivel}", font=("Helvetica", 16, "italic"), style="Custom.TLabel").pack(pady=10)

        ttk.Button(
            self.frame_perfil, text="Volver",
            command=lambda: self.cambiar_pantalla("menu"),
            style="Mi.TButton"
        ).pack(pady=20)

        ttk.Button(
            self.frame_perfil, text="Cerrar sesión",
            command=self._cerrar_sesion,
            style="Mi.TButton"
        ).pack(pady=5)

    def _cerrar_sesion(self):
        try:
            os.remove("usuario.json")
        except FileNotFoundError:
            pass
        messagebox.showinfo("Cerrar sesión", "Has cerrado sesión correctamente.")
        self.cambiar_pantalla("inicio")
