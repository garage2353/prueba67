import os
import json
import sqlite3
import hashlib
from tkinter import messagebox, Label
import ttkbootstrap as ttk
from PIL import Image, ImageTk

# Base de datos
conexion = sqlite3.connect("traductor.db")
cursor = conexion.cursor()
conexion.commit()

class PantallaInicioSesion(ttk.Frame):
    def __init__(self, master, cambiar_pantalla, actualizar_usuario):
        super().__init__(master, style="Custom.TFrame")
        self.cambiar_pantalla = cambiar_pantalla
        self.actualizar_usuario = actualizar_usuario
        self.pack_propagate(False)

        # Imagen de fondo
        try:
            self.fondo_original = Image.open("fondo.png")
            self.fondo_label = Label(self)
            self.fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bind("<Configure>", self.redimensionar_fondo)
        except:
            self.fondo_original = None

        # Estilos
        style = ttk.Style()
        style.configure("Custom.TFrame", background="white")
        style.configure("Custom.TLabel", background="white", foreground="#5a3d1e")
        style.configure("Mi.TButton", font=("Helvetica", 12), background="#7a5331", foreground="white", borderwidth=0)
        style.map("Mi.TButton", background=[("active", "#7a5331"), ("pressed", "#3e2b17")], foreground=[("disabled", "#ccc")])
        style.configure("Titulo.TLabel", font=("Helvetica", 32, "bold"), foreground="#FFD700", background="#FFFFFF")

        self.frame_login = ttk.Frame(self, style="Custom.TFrame", width=500, padding=30)
        self.frame_login.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(self.frame_login, text="Timumachtikan", style="Titulo.TLabel").pack(fill="x", pady=(0, 40))
        ttk.Label(self.frame_login, text="Inicio de sesión", font=("Helvetica", 18, "bold"), style="Custom.TLabel").pack(pady=10)

        ttk.Label(self.frame_login, text="Correo:", style="Custom.TLabel").pack()
        self.correo_entry = ttk.Entry(self.frame_login, width=40)
        self.correo_entry.pack()

        ttk.Label(self.frame_login, text="Contraseña:", style="Custom.TLabel").pack()
        self.contrasena_entry = ttk.Entry(self.frame_login, show="*", width=40)
        self.contrasena_entry.pack()

        ttk.Button(self.frame_login, text="Iniciar sesión", command=self.iniciar_sesion, style="Mi.TButton").pack(pady=10)
        ttk.Button(self.frame_login, text="Crear cuenta", command=self.mostrar_registro, style="Mi.TButton").pack()

        self.frame_register = ttk.Frame(self, style="Custom.TFrame", width=500, padding=30)

        ttk.Label(self.frame_register, text="Timumachtikan", style="Titulo.TLabel").pack(fill="x", pady=(0, 40))
        ttk.Label(self.frame_register, text="Registro de usuario", font=("Helvetica", 18, "bold"), style="Custom.TLabel").pack(pady=10)

        ttk.Label(self.frame_register, text="Nombre:", style="Custom.TLabel").pack()
        self.nombre_entry = ttk.Entry(self.frame_register, width=40)
        self.nombre_entry.pack()

        ttk.Label(self.frame_register, text="Correo:", style="Custom.TLabel").pack()
        self.correo_reg_entry = ttk.Entry(self.frame_register, width=40)
        self.correo_reg_entry.pack()

        ttk.Label(self.frame_register, text="Contraseña:", style="Custom.TLabel").pack()
        self.contrasena_reg_entry = ttk.Entry(self.frame_register, show="*", width=40)
        self.contrasena_reg_entry.pack()

        ttk.Button(self.frame_register, text="Registrar usuario", command=self.registrar_usuario, style="Mi.TButton").pack(pady=10)
        ttk.Button(self.frame_register, text="Volver a inicio de sesión", command=self.mostrar_login, style="Mi.TButton").pack()

    def redimensionar_fondo(self, event):
        if self.fondo_original and event.width > 10 and event.height > 10:
            nueva_img = self.fondo_original.resize((event.width, event.height), Image.Resampling.LANCZOS)
            nueva_foto = ImageTk.PhotoImage(nueva_img)
            self.fondo_label.configure(image=nueva_foto)
            self.fondo_label.image = nueva_foto

    def mostrar_login(self):
        self.frame_register.place_forget()
        self.frame_login.place(relx=0.5, rely=0.5, anchor="center")

    def mostrar_registro(self):
        self.frame_login.place_forget()
        self.frame_register.place(relx=0.5, rely=0.5, anchor="center")

    def hashear_contrasena(self, contrasena):
        return hashlib.sha256(contrasena.encode()).hexdigest()

    def iniciar_sesion(self):
        correo = self.correo_entry.get().strip()
        contrasena = self.hashear_contrasena(self.contrasena_entry.get().strip())

        if not correo or not contrasena:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        cursor.execute("SELECT id, nombre, correo FROM usuarios WHERE correo=? AND contrasena=?", (correo, contrasena))
        usuario = cursor.fetchone()

        if usuario:
            with open("usuario.json", "w") as f:
                json.dump({
                    "id": usuario[0],
                    "nombre": usuario[1],
                    "correo": usuario[2]
                }, f)

            self.actualizar_usuario(usuario[0])  # <- ¡Clave para actualizar tutorial_ok!
            messagebox.showinfo("Inicio de sesión", "Has iniciado sesión correctamente.")
            self.cambiar_pantalla("menu")
        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")

    def registrar_usuario(self):
        nombre = self.nombre_entry.get().strip()
        correo = self.correo_reg_entry.get().strip()
        contrasena = self.hashear_contrasena(self.contrasena_reg_entry.get().strip())

        if not nombre or not correo or not contrasena:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            cursor.execute("INSERT INTO usuarios (nombre, correo, contrasena) VALUES (?, ?, ?)", (nombre, correo, contrasena))
            conexion.commit()

            cursor.execute("SELECT id FROM usuarios WHERE correo=?", (correo,))
            usuario_id = cursor.fetchone()[0]

            with open("usuario.json", "w") as f:
                json.dump({
                    "id": usuario_id,
                    "nombre": nombre,
                    "correo": correo
                }, f)

            self.actualizar_usuario(usuario_id)  # <- También al registrar
            messagebox.showinfo("Registro exitoso", "Tu cuenta ha sido creada.")
            self.mostrar_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El correo ya está registrado.")
