import pyttsx3
import speech_recognition as sr
import threading
import re
import tkinter as tk
from tkinter import messagebox

_detener_voz = False
_hilo_voz = None

def iniciar_motor_voz():
    """
    Retorna una nueva instancia del motor TTS configurado para usar Microsoft Helena.
    Si no encuentra 'Helena', avisa al usuario y cae a una voz genérica en español.
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    # Intentamos la voz Helena
    helena = next((v for v in voices if 'helena' in v.name.lower()), None)
    if helena:
        engine.setProperty('voice', helena.id)
    else:
        # Mensaje en consola
        print("[WARNING] La voz 'Microsoft Helena' no está instalada.")
        # Mensaje GUI si hay un root de tkinter
        try:
            root = tk._default_root or tk.Tk()
            root.withdraw()
            messagebox.showwarning(
                "Voz no encontrada",
                ("La voz 'Microsoft Helena' no está instalada en tu sistema.\n"
                 "Por favor ve a Configuración de Windows → Hora e idioma → Voz → "
                 "Agregar voces y busca 'Helena' en español.")
            )
        except Exception:
            pass

        # Caer a primera voz española que encuentre
        esp = next((v for v in voices if 'spanish' in v.name.lower()), None)
        if esp:
            engine.setProperty('voice', esp.id)

    return engine

def reproducir_palabra(palabra: str = '', pronunciacion: str = None):
    """
    Reproduce una palabra o su pronunciación usando un motor TTS nuevo.
    """
    engine = iniciar_motor_voz()
    texto = pronunciacion or palabra
    print(f"[DEBUG] Reproduciendo: {texto}")
    engine.say(texto)
    engine.runAndWait()
    engine.stop()

def reproducir_texto_con_pronunciacion(texto: str, pantalla):
    """
    Lee un bloque de texto con pronunciaciones usando un hilo nuevo y motor limpio.
    """
    global _detener_voz, _hilo_voz

    if _hilo_voz and _hilo_voz.is_alive():
        detener_voz()

    def hilo_hablar():
        global _detener_voz
        engine = iniciar_motor_voz()
        _detener_voz = False
        frases = re.split(r'(?<=[.!?])\s+', texto.strip())
        for frase in frases:
            if _detener_voz:
                break
            print(f"[DEBUG] Reproduciendo frase: {frase}")
            engine.say(frase)
            engine.runAndWait()
        engine.stop()
        pantalla.boton_leer.config(state="normal")
        pantalla.boton_detener.config(state="disabled")

    _hilo_voz = threading.Thread(target=hilo_hablar, daemon=True)
    _hilo_voz.start()

def detener_voz():
    """
    Señala que se debe detener la reproducción de voz.
    """
    global _detener_voz
    _detener_voz = True

def detectar_voz() -> bool:
    """
    Usa el micrófono para detectar si el usuario habló.
    """
    recog = sr.Recognizer()
    mic = sr.Microphone()
    with mic as fuente:
        recog.adjust_for_ambient_noise(fuente, duration=0.5)
        try:
            print("[DEBUG] Escuchando...")
            audio = recog.listen(fuente, timeout=2, phrase_time_limit=3)
            if audio.frame_data:
                print("[DEBUG] Voz detectada.")
                return True
            else:
                print("[DEBUG] Silencio detectado.")
                return False
        except sr.WaitTimeoutError:
            print("[DEBUG] Tiempo agotado sin detectar voz.")
            return False
        except Exception as e:
            print(f"[DEBUG] Error en la detección de voz: {e}")
            return False
