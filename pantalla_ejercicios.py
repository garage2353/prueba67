import re
import random
import threading
import tkinter as tk
from tkinter import StringVar, messagebox
from datetime import datetime, timedelta
from ttkbootstrap import ttk, Style
from utilidades import normalizar_texto
from voz import reproducir_palabra, detectar_voz, detener_voz
from base_datos import conectar_bd
from cronometro import cronocmetro

style = Style()
style.configure("CustomWhite.TFrame", background="white")

# Factores de velocidad y tiempos por nivel
LEVEL_FACTORS = {'básico': 1.0, 'intermedio': 1.2, 'avanzado': 1.5}
LEVEL_TIEMPOS  = {'básico': 15,  'intermedio': 12,  'avanzado': 10}

class PantallaEjercicios:
    def __init__(self, frame_padre, usuario_id, volver_callback):
        self.frame = ttk.Frame(frame_padre, style="CustomWhite.TFrame", padding=50)
        self.frame.pack(fill="both", expand=True)
        self.frame.config(width=800, height=400)
        self.frame.pack_propagate(False)

        self.btn_volver = ttk.Button(
            frame_padre,
            text="Volver a lecciones",
            style="Mi.TButton",
            command=volver_callback
        )

        self.usuario_id = usuario_id
        self.volver_callback = volver_callback
        self.ejercicios = []
        self.ejercicio_actual = -1
        self.puntos = 0
        self.errores = 0
        self.total = 0
        self.leccion_id = None
        self.respuestas = []

        # Parámetros: 2 intentos por lección, 3 vidas por intento
        self.intentos_restantes = 2
        self.vidas_restantes = 3

        self.cronometro = None
        self.factor_velocidad = 1.0
        self.tiempo_por_ejercicio = 0

    def cargar_ejercicios(self, leccion_id, conexion):
        self.leccion_id = leccion_id
        self.ejercicios.clear()
        self.puntos = self.errores = 0
        self.ejercicio_actual = -1
        self.vidas_restantes = 3

        cur = conexion.cursor()
        # Verificar intentos previos y bloqueo
        cur.execute(
            "SELECT total_fallos, fecha_ultimo_intento FROM intentos_fallidos"
            " WHERE usuario_id=? AND leccion_id=?",
            (self.usuario_id, leccion_id)
        )
        row = cur.fetchone()
        if row:
            total_fallos, fecha_ultimo = row
            self.intentos_restantes = max(0, 2 - total_fallos)
            fecha_ultimo = datetime.fromisoformat(fecha_ultimo)
            if total_fallos >= 2:
                espera = timedelta(hours=6)
                if datetime.now() - fecha_ultimo < espera:
                    restante = espera - (datetime.now() - fecha_ultimo)
                    horas, minutos = divmod(restante.seconds // 60, 60)
                    messagebox.showwarning(
                        "Lección bloqueada",
                        f"Has agotado tus intentos. Intenta de nuevo en {horas}h {minutos}m."
                    )
                    self.volver_callback()
                    return
                else:
                    self.intentos_restantes = 2
                    cur.execute(
                        "DELETE FROM intentos_fallidos WHERE usuario_id=? AND leccion_id=?",
                        (self.usuario_id, leccion_id)
                    )
                    conexion.commit()
            else:
                messagebox.showinfo(
                    "Intentos disponibles",
                    f"Tienes {self.intentos_restantes} de 2 intentos restantes."
                )
        else:
            messagebox.showinfo(
                "Intentos disponibles",
                "Tienes 2 de 2 intentos disponibles."
            )

        # Cargar nivel y ejercicios
        cur.execute("SELECT nivel FROM lecciones WHERE id=?", (leccion_id,))
        nivel = cur.fetchone()[0]
        self.factor_velocidad = LEVEL_FACTORS.get(nivel, 1.0)
        self.tiempo_por_ejercicio = LEVEL_TIEMPOS.get(nivel, 15)

        cur.execute(
            "SELECT e.id, e.tipo, e.pregunta FROM ejercicios e WHERE e.leccion_id=?",
            (leccion_id,)
        )
        for eid, tipo, pregunta in cur.fetchall():
            cur.execute(
                "SELECT t.palabra_es, t.palabra_nawat FROM traducciones t"
                " JOIN ejercicio_traducciones et ON t.id=et.traduccion_id"
                " WHERE et.ejercicio_id=? ORDER BY et.rowid",
                (eid,)
            )
            trads = cur.fetchall()
            self.ejercicios.append((eid, tipo, pregunta, trads))

        random.shuffle(self.ejercicios)
        self.total = len(self.ejercicios)

    def limpiar_frame(self):
        if self.cronometro:
            self.cronometro.detener()
        for w in self.frame.winfo_children():
            w.destroy()

    def mostrar_siguiente(self, conexion):
        detener_voz()
        self.limpiar_frame()
        self.ejercicio_actual += 1
        if self.ejercicio_actual >= self.total:
            return self.finalizar(conexion)

        eid, tipo, pregunta, trads = self.ejercicios[self.ejercicio_actual]
        # Preparar respuesta
        if tipo == "traduccion":
            p = pregunta.lower()
            if "al español" in p or "oración" in p:
                resp = [normalizar_texto(" ".join(t[0] for t in trads))]
            else:
                resp = [normalizar_texto(" ".join(t[1] for t in trads))]
        else:
            resp = [" ".join(normalizar_texto(t[1]) for t in trads)]
        self.respuestas = resp

        cont = ttk.Frame(self.frame, style="CustomWhite.TFrame")
        cont.pack(fill="both", expand=True)

        # Mostrar intentos y corazones
        hearts = ''.join('♥' for _ in range(self.vidas_restantes)) + ''.join('♡' for _ in range(3-self.vidas_restantes))
        ttk.Label(
            cont,
            text=f"Intentos: {self.intentos_restantes}/2   Vidas: {hearts}",
            font=("Helvetica", 12, "italic"),
            foreground="#7a5331", background="white"
        ).pack(pady=(0,5))

        # Cronómetro
        self.lbl_cron = ttk.Label(cont, font=("Helvetica",12), foreground="#7a5331", background="white")
        self.lbl_cron.pack(pady=(0,10))
        self.cronometro = cronocmetro(
            parent=cont,
            tiempo_inicial=self.tiempo_por_ejercicio,
            interval_ms=int(1000/self.factor_velocidad),
            on_tick=lambda s: self.lbl_cron.config(text=f"Tiempo: {s}s"),
            on_timeout=lambda: self.validar_texto("", self.respuestas, conexion)
        )
        self.cronometro.iniciar()

        # Pregunta y entrada
        ttk.Label(
            cont,
            text=f"Ejercicio {self.ejercicio_actual+1}/{self.total}: {tipo.title()}",
            font=("Helvetica",14,"bold"), foreground="#7a5331", background="white"
        ).pack(pady=(5,5))
        ttk.Label(
            cont,
            text=pregunta, font=("Helvetica",14),
            foreground="#7a5331", background="white"
        ).pack(pady=(0,10))

        if tipo in ("completar","traduccion"):
            self.resp_var = StringVar()
            entry = ttk.Entry(cont, textvariable=self.resp_var, font=("Helvetica",14), width=30)
            entry.pack(pady=10); entry.focus_set()
            entry.bind("<Return>", lambda e: self.validar_texto(self.resp_var.get(), self.respuestas, conexion))
            ttk.Button(cont, text="Siguiente", style="Mi.TButton",
                       command=lambda: self.validar_texto(self.resp_var.get(), self.respuestas, conexion)
            ).pack(pady=5)
        else:
            frase = self.respuestas[0]
            cur = conectar_bd().cursor()
            cur.execute("SELECT palabra_nawat, pronunciacion_tts FROM traducciones")
            dic = {p:t for p,t in cur.fetchall() if p and t}
            pron = frase
            for p,t in dic.items():
                pron = re.sub(rf"\b{re.escape(p)}\b", t, pron, flags=re.IGNORECASE)
            ttk.Button(cont, text="Escuchar", style="Mi.TButton",
                       command=lambda: threading.Thread(target=reproducir_palabra,
                                                      kwargs=dict(palabra=frase, pronunciacion=pron), daemon=True).start()
            ).pack(pady=5)
            ttk.Button(cont, text="Grabar Pronunciación", style="Mi.TButton",
                       command=lambda: self.validar_pronunciacion(conexion)
            ).pack(pady=5)

    def validar_texto(self, entrada, respuestas, conexion):
        if self.cronometro: self.cronometro.detener()
        usr = normalizar_texto(entrada)

        if usr in respuestas:
            self.puntos += 1
            messagebox.showinfo("Resultado", "¡Correcto!")
        else:
            self.errores += 1
            if self.vidas_restantes > 0:
                self.vidas_restantes -= 1
                messagebox.showwarning("Resultado", f"Incorrecto. Vidas restantes: {self.vidas_restantes}/3")
            else:
                messagebox.showerror("Lección fallada", "Has cometido un error sin corazones. Volviendo a lecciones.")
                self.registrar_fallo(conexion)
                self.volver_callback()
                return

        self.mostrar_siguiente(conexion)

    def validar_pronunciacion(self, conexion):
        if self.cronometro: self.cronometro.detener()

        for w in self.frame.winfo_children():
            for c in w.winfo_children():
                if isinstance(c, ttk.Button): c.config(state="disabled")
        self.frame.update_idletasks()
        try:
            if detectar_voz():
                threading.Thread(target=reproducir_palabra, kwargs=dict(palabra="escuchado"), daemon=True).start()
                messagebox.showinfo("Resultado", "¡Se detectó tu voz!")
                self.puntos += 1
            else:
                self.errores += 1
                if self.vidas_restantes > 0:
                    self.vidas_restantes -= 1
                    messagebox.showwarning("Resultado", f"No se detectó voz. Vidas restantes: {self.vidas_restantes}/3")
                else:
                    messagebox.showerror("Lección fallada", "Has cometido un error sin corazones. Volviendo a lecciones.")
                    self.registrar_fallo(conexion)
                    self.volver_callback()
                    return
            self.frame.after(500, lambda: self.mostrar_siguiente(conexion))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def guardar_nota_leccion(self, conexion):
        nota_final = int((self.puntos / self.total) * 100) if self.total > 0 else 0
        cur = conexion.cursor()
        try:
            cur.execute(
                "UPDATE notas_lecciones SET nota=?, fecha=CURRENT_TIMESTAMP WHERE usuario_id=? AND leccion_id=?",
                (nota_final, self.usuario_id, self.leccion_id)
            )
            if cur.rowcount == 0:
                cur.execute(
                    "INSERT INTO notas_lecciones (usuario_id, leccion_id, nota) VALUES (?, ?, ?)",
                    (self.usuario_id, self.leccion_id, nota_final)
                )
            conexion.commit()
        except Exception as e:
            messagebox.showerror("Error al guardar nota de lección", str(e))

    def registrar_fallo(self, conexion):
        ahora = datetime.now().isoformat()
        cur = conexion.cursor()
        cur.execute("SELECT total_fallos FROM intentos_fallidos WHERE usuario_id=? AND leccion_id=?",
                    (self.usuario_id, self.leccion_id))
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE intentos_fallidos SET total_fallos=total_fallos+1, fecha_ultimo_intento=?"
                " WHERE usuario_id=? AND leccion_id=?",
                (ahora, self.usuario_id, self.leccion_id)
            )
        else:
            cur.execute(
                "INSERT INTO intentos_fallidos(usuario_id, leccion_id, fecha_ultimo_intento, total_fallos)"
                " VALUES(?,?,?,1)",
                (self.usuario_id, self.leccion_id, ahora)
            )
        conexion.commit()

    def finalizar(self, conexion):
        self.limpiar_frame()
        total = len(self.ejercicios)
        ttk.Label(
            self.frame,
            text=f"Lección finalizada. Puntos: {self.puntos}/{total} | Errores: {self.errores}",
            font=("Helvetica",16,"bold"), foreground="#7a5331", background="white"
        ).pack(pady=20)

        # Guardar nota final de la lección
        self.guardar_nota_leccion(conexion)

        self.btn_volver.pack(pady=10)
        try:
            cur = conexion.cursor()
            cur.execute("SELECT id FROM progreso WHERE usuario_id=? AND leccion_id=?",
                        (self.usuario_id, self.leccion_id))
            res = cur.fetchone()
            if res:
                cur.execute("UPDATE progreso SET completada=1 WHERE id=?", (res[0],))
            else:
                cur.execute(
                    "INSERT INTO progreso(usuario_id,leccion_id,completada) VALUES(?,?,1)",
                    (self.usuario_id, self.leccion_id)
                )
            # Resetear intentos fallidos
            cur.execute(
                "DELETE FROM intentos_fallidos WHERE usuario_id=? AND leccion_id=?",
                (self.usuario_id, self.leccion_id)
            )
            conexion.commit()
        except Exception as e:
            messagebox.showerror("Error al guardar progreso", str(e))
