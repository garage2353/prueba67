import unicodedata
import difflib

def normalizar_texto(texto):
    texto = texto.strip().casefold()
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def es_similar(a, b, umbral=0.75):
    return difflib.SequenceMatcher(None, a, b).ratio() >= umbral
