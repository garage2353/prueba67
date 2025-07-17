from tkinter import messagebox
from utilidades import normalizar_texto

def validar_respuesta_entrada(user_input, respuestas, puntos):
    user = normalizar_texto(user_input)
    correcto = user in respuestas
    if correcto:
        puntos += 1
        messagebox.showinfo("Resultado", "¡Correcto!")
    else:
        messagebox.showwarning("Resultado", "Incorrecto.\n" + "\n".join(respuestas))
    return puntos

def validar_respuesta_voz(respuestas, reconocer_func, puntos):
    try:
        escuchado = reconocer_func()
        norm = normalizar_texto(escuchado)
        if norm in respuestas:
            puntos += 1
            messagebox.showinfo("Resultado", f"¡Correcto! Escuché: {escuchado}")
        else:
            messagebox.showwarning(
                "Resultado",
                f"Incorrecto.\nEscuché: {escuchado}\nEsperado:\n" + "\n".join(respuestas)
            )
    except Exception as e:
        messagebox.showerror("Error", str(e))
    return puntos
