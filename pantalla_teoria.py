import unicodedata
import re
import tkinter as tk
from ttkbootstrap import ttk, Style
import threading
from voz import (
    reproducir_palabra,
    reproducir_texto_con_pronunciacion,
    detener_voz,
    iniciar_motor_voz
)
from base_datos import conectar_bd

# === Configurar estilo blanco global ===
style = Style()
style.configure("CustomWhite.TFrame", background="white")
style.configure("CustomWhite.TLabel", background="white", foreground="#5a3d1e")

def normalizar_palabra(palabra: str) -> str:
    palabra = palabra.strip()
    palabra = re.sub(r"[^\wáéíóúñÁÉÍÓÚÑ]", "", palabra)
    return unicodedata.normalize('NFC', palabra)

def buscar_traduccion_insensible(dic, palabra):
    cf = palabra.casefold()
    return next((v for k, v in dic.items() if k.casefold() == cf), None)

class PantallaTeoria:
    def __init__(
        self, frame_teoria, volver_a_lecciones_callback, mostrar_ejercicios_callback
    ):
        self.frame = frame_teoria
        self.frame.configure(style="CustomWhite.TFrame")
        self.frame.pack_propagate(True)

        self.volver_a_lecciones_callback = volver_a_lecciones_callback
        self.mostrar_ejercicios_callback = mostrar_ejercicios_callback

        # Título y descripción
        self.label_titulo = ttk.Label(
            self.frame,
            text="",
            font=("Helvetica", 18, "bold"),
            style="CustomWhite.TLabel",
            wraplength=1000,
            justify="center"
        )
        self.label_titulo.pack(pady=(20, 10))

        self.label_descripcion = ttk.Label(
            self.frame,
            text="",
            font=("Helvetica", 13, "italic"),
            style="CustomWhite.TLabel",
            wraplength=800,
            justify="center"
        )
        self.label_descripcion.pack(pady=(0, 10))

        # Contenedor para Text + Scrollbar
        self.text_frame = ttk.Frame(self.frame, style="CustomWhite.TFrame")
        self.text_frame.pack(fill="both", expand=True, padx=40, pady=(0, 60))

        self.scrollbar = tk.Scrollbar(
            self.text_frame,
            orient="vertical",
            bg="white",
            troughcolor="white",
            activebackground="white",
            highlightthickness=0,
            width=16
        )
        self.scrollbar.pack(side="right", fill="y")

        self.texto_teoria = tk.Text(
            self.text_frame,
            font=("Helvetica", 13),
            wrap="word",
            bg="white",
            fg="#5a3d1e",
            relief="flat",
            borderwidth=0,
            yscrollcommand=self.scrollbar.set
        )
        self.texto_teoria.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.texto_teoria.yview)

        self.texto_teoria.config(state="disabled")
        self.texto_teoria.tag_configure("palabra", foreground="#5a3d1e")
        self.texto_teoria.tag_bind("palabra", "<Button-1>", self.on_click_palabra)

        # Botones inferiores
        self.frame_botones_inferiores = ttk.Frame(
            self.frame, style="CustomWhite.TFrame", padding=5
        )
        self.frame_botones_inferiores.place(relx=0.5, rely=1.0, y=-10, anchor="s")

        self.boton_leer = ttk.Button(
            self.frame_botones_inferiores,
            text="🔊 Leer",
            style="Mi.TButton",
            command=self.leer_teoria
        )
        self.boton_leer.pack(side="left", padx=10)

        self.boton_detener = ttk.Button(
            self.frame_botones_inferiores,
            text="⏸️ Detener",
            style="Mi.TButton",
            command=detener_voz,
            state="disabled"
        )
        self.boton_detener.pack(side="left", padx=10)

        self.boton_volver = ttk.Button(
            self.frame_botones_inferiores,
            text="Volver a lecciones",
            style="Mi.TButton",
            command=self.volver_a_lecciones_callback
        )
        self.boton_volver.pack(side="left", padx=10)

        self.boton_ejercicios = ttk.Button(
            self.frame_botones_inferiores,
            text="Empezar ejercicios",
            style="Mi.TButton",
            command=self.mostrar_ejercicios_callback
        )
        self.boton_ejercicios.pack(side="left", padx=10)

        self.traducciones_dic = {}
        self.palabras_detectadas = set()

    def mostrar(self, titulo, descripcion, contenido):
        self.label_titulo.config(text=titulo)
        self.label_descripcion.config(text=descripcion or "")

        self.texto_teoria.config(state="normal")
        self.texto_teoria.delete("1.0", "end")
        self.texto_teoria.insert("1.0", contenido)

        self.texto_teoria.tag_remove("palabra", "1.0", "end")
        self.palabras_detectadas.clear()
        for m in re.finditer(r'\b[\wáéíóúñÁÉÍÓÚÑ]+\b', contenido):
            palabra = m.group(0)
            if palabra not in self.palabras_detectadas:
                self.palabras_detectadas.add(palabra)
                start = f"1.0+{m.start()}c"
                end = f"1.0+{m.end()}c"
                self.texto_teoria.tag_add("palabra", start, end)

        self.texto_teoria.config(state="disabled")
        self.leccion_contenido = contenido

        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("SELECT palabra_nawat, pronunciacion_tts FROM traducciones")
        self.traducciones_dic = {p: t for p, t in cur.fetchall() if p and t}
        conn.close()

    def leer_teoria(self):
        # Detener posible lectura anterior
        detener_voz()
        self.boton_leer.config(state="disabled")
        self.boton_detener.config(state="normal")
        texto = self.leccion_contenido
        for palabra, tts in self.traducciones_dic.items():
            texto = re.sub(
                rf'\b{re.escape(palabra)}\b', tts,
                texto, flags=re.IGNORECASE
            )
        threading.Thread(
            target=reproducir_texto_con_pronunciacion,
            args=(texto, self),
            daemon=True
        ).start()

    def on_click_palabra(self, event):
        idx = self.texto_teoria.index(f"@{event.x},{event.y}")
        rng = self.texto_teoria.tag_prevrange("palabra", idx)
        if not rng:
            return
        pal = self.texto_teoria.get(rng[0], rng[1])
        pal_norm = normalizar_palabra(pal)
        pron = buscar_traduccion_insensible(self.traducciones_dic, pal_norm) or pal
        engine = iniciar_motor_voz()
        detener_voz()
        threading.Thread(
            target=reproducir_palabra,
            args=(engine, pal, pron),
            daemon=True
        ).start()
