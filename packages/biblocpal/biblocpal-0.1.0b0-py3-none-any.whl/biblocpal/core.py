from .data import VOCABULARIO, RESPUESTAS_PREFIJAS
from .reasoning import razonamiento_basico

class Biblocpal:
    def __init__(self):
        self.vocabulario = VOCABULARIO
        self.respuestas_fijas = RESPUESTAS_PREFIJAS

    def obtener_significado(self, palabra):
        return self.vocabulario.get(palabra.lower(), "No tengo significado para esa palabra.")

    def obtener_respuesta_fija(self, texto):
        return self.respuestas_fijas.get(texto.lower())

    def pensar(self, palabra):
        return razonamiento_basico(palabra)
