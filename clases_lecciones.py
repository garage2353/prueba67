import ttkbootstrap as ttk
from tkinter import Label
from PIL import Image, ImageTk
from base_datos import conectar_bd
from voz import iniciar_motor_voz
from pantalla_lecciones import PantallaLecciones
from pantalla_teoria import PantallaTeoria
from pantalla_ejercicios import PantallaEjercicios

class PantallaClases(ttk.Frame):
    def __init__(self, master, usuario_id, cambiar_pantalla):
        super().__init__(master)
        self.cambiar_pantalla = cambiar_pantalla
        self.usuario_id = usuario_id
        self.conn = conectar_bd()
        self.engine = iniciar_motor_voz()

        # Fondo
        try:
            self.fondo_original = Image.open("fondo2.png")
            self.fondo_tk = ImageTk.PhotoImage(self.fondo_original)
            self.label_fondo = Label(self, image=self.fondo_tk)
            self.label_fondo.place(relwidth=1, relheight=1)
            self.label_fondo.lower()
            self.bind("<Configure>", self._redimensionar_fondo)
        except Exception as e:
            print("⚠️ No se pudo cargar fondo2.png:", e)
            self.fondo_original = None
            self.label_fondo = None

        # Estilo blanco
        style = ttk.Style()
        style.configure("White.TFrame", background="white")

        # Tamaños personalizados por frame
        self.ancho_lecciones, self.alto_lecciones = 800, 600
        self.ancho_ejercicios, self.alto_ejercicios = 900, 750

        # Contenedor principal
        self.contenedor = ttk.Frame(self, style="White.TFrame")
        self.contenedor.pack(pady=20, padx=20, expand=True)
        self.contenedor.pack_propagate(False)

        # === FRAMES ===
        self.frame_lecciones = ttk.Frame(self.contenedor, style="White.TFrame", padding=10)
        self.frame_lecciones.config(width=self.ancho_lecciones, height=self.alto_lecciones)
        self.frame_lecciones.pack(side="top", fill="none", anchor="center")

        self.frame_teoria = ttk.Frame(self.contenedor, style="White.TFrame", padding=10)
        self.frame_ejercicios = ttk.Frame(self.contenedor, style="White.TFrame", padding=10)

        # Botón volver en lecciones
        ttk.Button(
            self.frame_lecciones,
            text="Volver",
            command=lambda: self.cambiar_pantalla("menu"),
            style="Mi.TButton"
        ).pack(anchor="nw", pady=(0, 10))

        # Pantallas internas
        self.pantalla_lecciones = PantallaLecciones(
            self.frame_lecciones, self.usuario_id, self.conn, self.abrir_leccion
        )
        self.pantalla_teoria = PantallaTeoria(
            self.frame_teoria,
            volver_a_lecciones_callback=self.volver_a_lecciones,
            mostrar_ejercicios_callback=self.mostrar_ejercicios
        )
        self.pantalla_ejercicios = PantallaEjercicios(
            self.frame_ejercicios, self.usuario_id, self.volver_a_lecciones
        )

        # Mostrar solo lecciones al inicio
        self.frame_lecciones.pack()
        self.ajustar_contenedor(self.ancho_lecciones, self.alto_lecciones)

    def _redimensionar_fondo(self, event):
        if not self.fondo_original or not self.label_fondo:
            return
        w, h = max(1, event.width), max(1, event.height)
        img = self.fondo_original.resize((w, h), Image.Resampling.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        self.label_fondo.configure(image=foto)
        self.label_fondo.image = foto

    def ajustar_contenedor(self, ancho, alto):
        """ Método para asegurar que el contenedor mantenga el tamaño adecuado """
        self.contenedor.config(width=ancho, height=alto)
        self.contenedor.pack_propagate(False)

    def abrir_leccion(self, leccion_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT titulo, descripcion, contenido FROM lecciones WHERE id=?",
            (leccion_id,)
        )
        fila = cur.fetchone()
        if not fila:
            return
        titulo, descripcion, contenido = fila
        self.pantalla_teoria.mostrar(titulo, descripcion, contenido)

        # Ocultar frames no usados y mostrar teoría
        self.frame_lecciones.pack_forget()
        self.frame_ejercicios.pack_forget()
        self.frame_teoria.pack()
        self.ajustar_contenedor(self.ancho_lecciones, self.alto_lecciones)

        self.pantalla_ejercicios.cargar_ejercicios(leccion_id, self.conn)

    def mostrar_ejercicios(self):
        self.frame_teoria.pack_forget()
        self.frame_ejercicios.pack()
        self.ajustar_contenedor(self.ancho_ejercicios, self.alto_ejercicios)
        self.pantalla_ejercicios.mostrar_siguiente(self.conn)

    def volver_a_lecciones(self):
        self.frame_teoria.pack_forget()
        self.frame_ejercicios.pack_forget()
        self.frame_lecciones.pack()
        self.ajustar_contenedor(self.ancho_lecciones, self.alto_lecciones)

        # 🔄 ACTUALIZADO: recargar lecciones para reflejar progreso nuevo
        self.pantalla_lecciones.recargar_lecciones()
