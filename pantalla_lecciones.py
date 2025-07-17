import subprocess
from ttkbootstrap import ttk, Style
from tkinter import messagebox

style = Style()
style.configure("CustomWhite.TFrame", background="white")
style.configure("Treeview", fieldbackground="white", background="white", foreground="#5a3d1e")

class PantallaLecciones:
    def __init__(self, frame_padre, usuario_id, conexion, callback_abrir_leccion):
        self.frame = frame_padre
        self.frame.configure(style="CustomWhite.TFrame")
        self.usuario_id = usuario_id
        self.conn = conexion
        self.callback_abrir_leccion = callback_abrir_leccion

        # Título
        ttk.Label(
            self.frame,
            text="Lecciones",
            font=("Helvetica", 28, "bold"),
            foreground="#7a5331",
            background="white"
        ).pack(pady=20)

        # Árbol de lecciones
        self.tree = ttk.Treeview(
            self.frame,
            show="tree",
            height=10
        )
        self.tree.column("#0", anchor="w", width=600)
        self.tree.pack(pady=10, fill="x")

        self.tree.bind("<Double-1>", self.abrir_leccion)

        # Mostrar contenido inicial
        self.recargar_lecciones()

        self.frame.pack(fill="both", expand=True)

    def recargar_lecciones(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        cur = self.conn.cursor()

        # Obtener correo del usuario
        cur.execute("SELECT correo FROM usuarios WHERE id = ?", (self.usuario_id,))
        resultado = cur.fetchone()
        correo_usuario = resultado[0].strip().lower() if resultado and resultado[0] else ""

        # Obtener progreso completado
        cur.execute(
            "SELECT leccion_id FROM progreso WHERE usuario_id=? AND completada=1",
            (self.usuario_id,)
        )
        self.completadas = {r[0] for r in cur.fetchall()}
        self.desbloqueadas = set()

        # Obtener lista ordenada de lecciones
        cur.execute("SELECT id, titulo FROM lecciones ORDER BY orden")
        lecciones = cur.fetchall()

        if correo_usuario == "prueba":
            self.desbloqueadas = {lid for lid, _ in lecciones}
        else:
            desbloquear = True
            for lid, _ in lecciones:
                if desbloquear:
                    self.desbloqueadas.add(lid)
                else:
                    break
                if lid not in self.completadas:
                    desbloquear = False

        for i, (lid, titulo) in enumerate(lecciones):
            numero = i + 1
            if lid in self.desbloqueadas:
                display = f"{numero}. {titulo}"
            else:
                display = f"{numero}. {titulo} (🔒 Bloqueada)"
            self.tree.insert('', 'end', iid=str(lid), text=display)

    def abrir_leccion(self, event):
        sel = self.tree.focus()
        if sel:
            try:
                lid = int(sel)
            except ValueError:
                return
            if lid not in self.desbloqueadas:
                messagebox.showwarning(
                    "Lección bloqueada",
                    "Debes completar la lección anterior para acceder a esta."
                )
                return
            self.callback_abrir_leccion(lid)

    def volver_al_menu(self):
        self.frame.winfo_toplevel().destroy()
        subprocess.Popen(["python", "menu.py"])
