import tkinter as tk
from ttkbootstrap import ttk
from base_datos import conectar_bd
from PIL import Image, ImageTk

class PantallaClasificacion(ttk.Frame):  # Puedes renombrarla a PantallaRanking si prefieres
    def __init__(self, master, volver_callback):
        super().__init__(master, style="CustomWhite.TFrame")
        self.volver_callback = volver_callback

        # Fondo de pantalla
        try:
            self.fondo_original = Image.open("fondo2.png")
            self.fondo_tk = ImageTk.PhotoImage(self.fondo_original)
            self.label_fondo = tk.Label(self, image=self.fondo_tk)
            self.label_fondo.place(relwidth=1, relheight=1)
            self.bind("<Configure>", self._redimensionar_fondo)
        except Exception as e:
            print("No se pudo cargar fondo2.png:", e)

        # Contenedor principal
        self.contenedor = ttk.Frame(self, width=800, height=700, style="CustomWhite.TFrame")
        self.contenedor.place(relx=0.5, rely=0.5, anchor="center")
        self.contenedor.pack_propagate(False)

        ttk.Label(
            self.contenedor,
            text="🏆 Clasificación de Usuarios",
            font=("Helvetica", 20, "bold"),
            background="white",
            foreground="#5a3d1e"
        ).pack(pady=10)

        # Tabla con scroll
        tabla_frame = ttk.Frame(self.contenedor)
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(tabla_frame, columns=("Puesto", "Usuario", "Lecciones Completadas"), show="headings", height=15)
        self.tree.heading("Puesto", text="Puesto")
        self.tree.heading("Usuario", text="Usuario")
        self.tree.heading("Lecciones Completadas", text="Lecciones Completadas")
        self.tree.column("Puesto", width=80, anchor="center")
        self.tree.column("Usuario", width=250, anchor="center")
        self.tree.column("Lecciones Completadas", width=150, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Botón volver
        ttk.Button(
            self.contenedor,
            text="Volver",
            style="Mi.TButton",
            command=lambda: self.volver_callback("menu")
        ).pack(pady=10)

        self._cargar_ranking()

    def _redimensionar_fondo(self, event):
        if self.fondo_original:
            redim = self.fondo_original.resize((event.width, event.height), Image.Resampling.LANCZOS)
            self.fondo_tk = ImageTk.PhotoImage(redim)
            self.label_fondo.config(image=self.fondo_tk)

    def _cargar_ranking(self):
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute('''
            SELECT u.nombre, COUNT(p.leccion_id) as total
            FROM usuarios u
            JOIN progreso p ON p.usuario_id = u.id
            WHERE p.completada = 1
            GROUP BY u.id
            ORDER BY total DESC
        ''')
        resultados = cur.fetchall()
        conn.close()

        for i, (nombre, total) in enumerate(resultados, start=1):
            self.tree.insert("", "end", values=(f"{i}°", nombre, total))
