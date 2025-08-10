import numpy as np
import random

class MeganRBeta:
    def __init__(self):
        self.nombre = "MeganR Nucleus X13"
        self.version = "0.0.2b0"
        self.vocabulario = set([
            "hola", "adiós", "mundo", "python", "inteligencia", "algoritmo",
            "dato", "nube", "entrenar", "aprender", "consola", "proyecto",
            "función", "variable", "random", "vector", "matriz", "código",
            "número", "tiempo", "texto", "simulación", "red", "modelo", "bot",
            "ayuda", "cómo", "quién", "qué", "por", "gracias", "bien", "mal",
            "sí", "no", "claro", "ok", "genial", "increíble", "estás", "megan"
        ])
        self.respuestas_fijas = {
            "hola": "Hola, ¿cómo estás?",
            "adiós": "Adiós, ¡hasta pronto!",
            "cómo estás": "Estoy bien, gracias por preguntar.",
            "quién eres": f"Soy {self.nombre}, una IA en desarrollo.",
            "qué sabes hacer": "Puedo responder preguntas simples y hacer cálculos básicos.",
        }

    def tokenizar(self, texto):
        return texto.lower().strip().split()

    def responder(self, texto):
        tokens = self.tokenizar(texto)
        frase = " ".join(tokens)

        # Respuesta fija si existe
        if frase in self.respuestas_fijas:
            return self.respuestas_fijas[frase]

        # Buscar palabras que conozca
        for palabra in tokens:
            if palabra in self.vocabulario:
                return f"Conozco la palabra '{palabra}', pero no tengo respuesta fija aún."

        # Si no encuentra nada, devuelve palabra aleatoria
        aleatoria = random.choice(list(self.vocabulario))
        return f"No entendí eso, pero aquí está una respuesta aleatoria: {aleatoria}"

    # Mejoras NumPy básicas
    def sumar_vectores(self, a, b):
        return np.add(a, b)

    def multiplicar_matrices(self, a, b):
        return np.dot(a, b)
