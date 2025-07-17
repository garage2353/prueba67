import random
import threading
import re
import tkinter as tk
from ttkbootstrap import ttk, Style
from tkinter import messagebox, StringVar
from voz import reproducir_palabra, reproducir_texto_con_pronunciacion, detectar_voz, iniciar_motor_voz, detener_voz
from utilidades import normalizar_texto
from base_datos import conectar_bd
from PIL import Image, ImageTk

class PantallaTutorial:
    def __init__(self, frame_padre, usuario_id, volver_callback, finalizar_callback):
        self.frame = ttk.Frame(frame_padre, style="CustomWhite.TFrame")

        try:
            self.fondo_original = Image.open("fondo.png")
            self.fondo_tk = ImageTk.PhotoImage(self.fondo_original)
            self.label_fondo = tk.Label(self.frame, image=self.fondo_tk)
            self.label_fondo.place(relwidth=1, relheight=1)
            self.frame.bind("<Configure>", self.redimensionar_fondo)
        except Exception as e:
            print(f"No se pudo cargar la imagen de fondo: {e}")
            self.fondo_original = None

        self.usuario_id = usuario_id
        self.volver_callback = volver_callback
        self.finalizar_callback = finalizar_callback
        self.engine = iniciar_motor_voz()

        self.frame_intro1 = ttk.Frame(self.frame, style="CustomWhite.TFrame")
        self.frame_intro2 = ttk.Frame(self.frame, style="CustomWhite.TFrame")
        self.frame_teoria = ttk.Frame(self.frame, style="CustomWhite.TFrame")
        self.frame_ejercicios = ttk.Frame(self.frame, style="CustomWhite.TFrame")

        self.frame_intro1.place(relx=0.5, rely=0.5, anchor="center", width=1000, height=300)

        self.palabras = []
        self.leccion_contenido = ""

        self.ejercicios = []
        self.ejercicio_actual = -1

        self._crear_interfaz_intro1()

    def redimensionar_fondo(self, event):
        if self.fondo_original:
            nuevo_ancho = event.width
            nuevo_alto = event.height
            imagen_redim = self.fondo_original.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            self.fondo_tk = ImageTk.PhotoImage(imagen_redim)
            self.label_fondo.config(image=self.fondo_tk)

    def _crear_interfaz_intro1(self):
        for w in self.frame_intro1.winfo_children():
            w.destroy()

        ttk.Label(
            self.frame_intro1,
            text="¡Bienvenido al tutorial!",
            font=("Helvetica", 20, "bold"),
            background="white",
            foreground="#5a3d1e"
        ).pack(pady=30)

        ttk.Label(
            self.frame_intro1,
            text="Aquí aprenderás algunas palabras en náhuat y harás ejercicios simples.",
            font=("Helvetica", 14),
            background="white",
            foreground="#5a3d1e"
        ).pack(pady=10)

        ttk.Button(
            self.frame_intro1,
            text="Siguiente",
            style="Mi.TButton",
            command=self._mostrar_intro2
        ).pack(pady=30)

    def _mostrar_intro2(self):
        self.frame_intro1.place_forget()
        self.frame_intro2.place(relx=0.5, rely=0.5, anchor="center", width=1000, height=400)

        for w in self.frame_intro2.winfo_children():
            w.destroy()

        ttk.Label(
            self.frame_intro2,
            text="¿Qué harás en este tutorial?",
            font=("Helvetica", 18, "bold"),
            background="white",
            foreground="#5a3d1e"
        ).pack(pady=30)

        ttk.Label(
            self.frame_intro2,
            text="Primero leerás una pequeña lección con algunas palabras.",
            font=("Helvetica", 14),
            background="white",
            foreground="#5a3d1e"
        ).pack(pady=10)

        ttk.Label(
            self.frame_intro2,
            text="Luego harás ejercicios para practicar lo que aprendiste, incluso con tu voz.",
            font=("Helvetica", 14),
            background="white",
            foreground="#5a3d1e"
        ).pack(pady=10)

        ttk.Button(
            self.frame_intro2,
            text="Comenzar lección",
            style="Mi.TButton",
            command=self._iniciar_teoria
        ).pack(pady=30)

    def _iniciar_teoria(self):
        self.frame_intro2.place_forget()
        self.frame_teoria.place(relx=0.5, rely=0.5, anchor="center")
        self._crear_interfaz_teoria()

    def _crear_interfaz_teoria(self):
        for w in self.frame_teoria.winfo_children():
            w.destroy()

        marco_scroll = ttk.Frame(self.frame_teoria, width=400, height=300)
        marco_scroll.pack(padx=20, pady=20)
        marco_scroll.pack_propagate(False)

        self.texto_teoria = tk.Text(
            marco_scroll,
            font=("Helvetica", 13),
            wrap="word",
            bg="white",
            fg="#5a3d1e",
            width=40,
            height=15
        )
        self.texto_teoria.pack(fill="both", expand=True)

        botones = ttk.Frame(self.frame_teoria, style="CustomWhite.TFrame")
        botones.pack(pady=10)

        self.boton_leer = ttk.Button(
            botones,
            text="🔊 Leer palabras",
            command=self._leer_palabras,
            style="Mi.TButton"
        )
        self.boton_leer.pack(side="left", padx=10)

        self.boton_detener = ttk.Button(
            botones,
            text="■ Detener",
            command=self._detener_lectura,
            style="Mi.TButton",
            state="disabled"
        )
        self.boton_detener.pack(side="left", padx=10)

        self.btn_siguiente = ttk.Button(
            botones,
            text="Siguiente",
            command=self._iniciar_ejercicios,
            style="Mi.TButton"
        )
        self.btn_siguiente.pack(side="right", padx=10)

        self._cargar_palabras()

    def _leer_palabras(self):
        self.boton_leer.config(state="disabled")
        self.boton_detener.config(state="normal")
        texto = self.leccion_contenido
        for _, nawat, tts in self.palabras:
            if nawat and tts:
                texto = re.sub(rf"\b{re.escape(nawat)}\b", tts, texto, flags=re.IGNORECASE)
        threading.Thread(
            target=reproducir_texto_con_pronunciacion,
            args=(texto, self),
            daemon=True
        ).start()

    def _detener_lectura(self):
        self.boton_leer.config(state="normal")
        self.boton_detener.config(state="disabled")
        detener_voz()

    def _cargar_palabras(self):
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("""
            SELECT palabra_es, palabra_nawat, pronunciacion_tts
            FROM traducciones
            WHERE palabra_es IS NOT NULL AND palabra_nawat IS NOT NULL
            ORDER BY RANDOM() LIMIT 5
        """)
        self.palabras = cur.fetchall()
        conn.close()

        texto = "\n".join(f"{i}. {esp} – {nawat}" for i, (esp, nawat, _) in enumerate(self.palabras, 1))
        self.texto_teoria.delete("1.0", "end")
        self.texto_teoria.insert("1.0", texto)
        self.leccion_contenido = texto

    def _iniciar_ejercicios(self):
        self.frame_teoria.place_forget()
        self.frame_ejercicios.place(relx=0.5, rely=0.5, anchor="center")

        self.ejercicios = [(esp, naw) for esp, naw, _ in self.palabras]
        self.ejercicio_actual = -1
        self._mostrar_siguiente()

    def _mostrar_siguiente(self):
        for w in self.frame_ejercicios.winfo_children():
            w.destroy()

        self.ejercicio_actual += 1
        if self.ejercicio_actual >= len(self.ejercicios):
            return self._finalizar_tutorial()

        esp, naw = self.ejercicios[self.ejercicio_actual]

        marco = ttk.Frame(self.frame_ejercicios, width=800, height=200)
        marco.pack(pady=20)
        marco.pack_propagate(False)

        ttk.Label(
            marco,
            text=f"Traduce al náhuat: {esp}",
            font=("Helvetica", 16, "bold"),
            background="white",
            foreground="#5a3d1e"
        ).pack(pady=20)

        self.resp_var = StringVar()
        ttk.Entry(
            marco,
            textvariable=self.resp_var,
            font=("Helvetica", 14),
            width=30
        ).pack(pady=10)

        ttk.Button(
            marco,
            text="Verificar",
            style="Mi.TButton",
            command=lambda: self._validar_respuesta(naw)
        ).pack(pady=10)

    def _validar_respuesta(self, correcta):
        entrada = normalizar_texto(self.resp_var.get())
        esperada = normalizar_texto(correcta)

        if entrada == esperada:
            messagebox.showinfo("Correcto", "¡Respuesta correcta!")
        else:
            messagebox.showwarning("Incorrecto", f"Respuesta esperada: {correcta}")

        self._mostrar_siguiente()

    def _finalizar_tutorial(self):
        for w in self.frame_ejercicios.winfo_children():
            w.destroy()

        ttk.Label(
            self.frame_ejercicios,
            text="¡Tutorial finalizado!",
            font=("Helvetica", 16, "bold"),
            foreground="#5a3d1e",
            background="white"
        ).pack(pady=30)

        ttk.Button(
            self.frame_ejercicios,
            text="Ir al menú principal",
            style="Mi.TButton",
            command=self._guardar_estado_tutorial
        ).pack(pady=20)

    def _guardar_estado_tutorial(self):
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET tutorial_completado=1 WHERE id=?", (self.usuario_id,))
        conn.commit()
        conn.close()

        self.finalizar_callback()
