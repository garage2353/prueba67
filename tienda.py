import tkinter as tk
from ttkbootstrap import ttk
from base_datos import conectar_bd
from PIL import Image, ImageTk
import tkinter.messagebox as mb

class PantallaTienda(ttk.Frame):
    def __init__(self, master, usuario_id, volver_callback):
        super().__init__(master, style="CustomWhite.TFrame")
        self.usuario_id = usuario_id
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
        self.contenedor = ttk.Frame(self, width=800, height=700, style="CustomWhite.TFrame")
        self.contenedor.place(relx=0.5, rely=0.5, anchor="center")
        self.contenedor.pack_propagate(False)

        self.label_saldo = ttk.Label(
            self.contenedor, font=("Helvetica", 16, "bold"),
            foreground="#4b3621", background="white"
        )
        self.label_saldo.pack(pady=10)

        ttk.Label(
            self.contenedor,
            text="🛒 Tienda",
            font=("Helvetica", 20, "bold"),
            background="white",
            foreground="#5a3d1e"
        ).pack(pady=10)

        self.marco_items = ttk.Frame(self.contenedor)
        self.marco_items.pack(pady=20)

        # Botón volver
        ttk.Button(
            self.contenedor,
            text="Volver",
            style="Mi.TButton",
            command=lambda: self.volver_callback("menu")
        ).pack(pady=10)

        self._cargar_saldo()
        self._mostrar_items()

    def _redimensionar_fondo(self, event):
        if self.fondo_original:
            redim = self.fondo_original.resize((event.width, event.height), Image.Resampling.LANCZOS)
            self.fondo_tk = ImageTk.PhotoImage(redim)
            self.label_fondo.config(image=self.fondo_tk)

    def _cargar_saldo(self):
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("SELECT saldo FROM usuarios WHERE id = ?", (self.usuario_id,))
        saldo = cur.fetchone()[0]
        conn.close()
        self.saldo_actual = saldo
        self.label_saldo.config(text=f"💰 Tumin disponibles: {saldo}")

    def _mostrar_items(self):
        # Puedes definir aquí tus productos
        productos = [
            {"nombre": "Tema oscuro", "costo": 30},
            {"nombre": "Avatar jaguar", "costo": 50},
            {"nombre": "Nuevo fondo", "costo": 40}
        ]

        for producto in productos:
            frame = ttk.Frame(self.marco_items)
            frame.pack(pady=5)

            ttk.Label(frame, text=producto["nombre"], font=("Helvetica", 14), background="white").pack(side="left", padx=20)
            ttk.Label(frame, text=f"{producto['costo']} 🪙", font=("Helvetica", 12), foreground="#4b3621", background="white").pack(side="left")

            ttk.Button(frame, text="Comprar", style="Mi.TButton", command=lambda p=producto: self._comprar(p)).pack(side="right", padx=10)

    def _comprar(self, producto):
        if self.saldo_actual >= producto["costo"]:
            nuevo_saldo = self.saldo_actual - producto["costo"]
            conn = conectar_bd()
            cur = conn.cursor()
            cur.execute("UPDATE usuarios SET saldo = ? WHERE id = ?", (nuevo_saldo, self.usuario_id))
            conn.commit()
            conn.close()

            self.saldo_actual = nuevo_saldo
            self.label_saldo.config(text=f"💰 Tumin disponibles: {nuevo_saldo}")
            mb.showinfo("Compra realizada", f"Has comprado: {producto['nombre']} 🎉")
        else:
            mb.showwarning("Fondos insuficientes", "No tienes suficientes tumin para esta compra.")
