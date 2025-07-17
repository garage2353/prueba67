import sqlite3
import json
import os

def obtener_usuario_id():
    if not os.path.exists("usuario.json"):
        raise FileNotFoundError("No se encontró 'usuario.json'")
    with open("usuario.json", "r", encoding="utf-8") as f:
        usuario = json.load(f)
    conn = sqlite3.connect("traductor.db")
    resultado = conn.execute("SELECT id FROM usuarios WHERE correo=?", (usuario['correo'],)).fetchone()
    conn.close()
    if resultado:
        return resultado[0]
    raise ValueError("Usuario no encontrado en la base de datos.")

def conectar_bd():
    conn = sqlite3.connect("traductor.db")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
