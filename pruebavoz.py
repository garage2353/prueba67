import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 140)
engine.setProperty("volume", 9.0)

while True:
    texto = input("Escribe algo para que lo lea (o 'salir' para terminar):\n> ")
    if texto.lower() in ("salir", "exit", "quit"):
        break
    engine.say(texto)
    engine.runAndWait()
