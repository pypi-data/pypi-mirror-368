import random
import numpy as np

class MeganR:
    def __init__(self):
        self.nombre = "MeganR Nucleus X13"
        self.version = "0.0.1"
        self.palabras_base = [
            "hola", "adiós", "mundo", "python", "inteligencia",
            "algoritmo", "dato", "nube", "entrenar", "aprender",
            "consola", "proyecto", "función", "variable", "random",
            "vector", "matriz", "código", "número", "tiempo",
            "texto", "simulación", "red", "modelo", "bot"
        ]

    def saludar(self):
        return f"Hola, soy {self.nombre} v{self.version}"

    def palabra_aleatoria(self):
        return random.choice(self.palabras_base)

    def sumar_vectores(self, a, b):
        return np.add(a, b)

    def multiplicar_matrices(self, a, b):
        return np.dot(a, b)

    def entrenar(self):
        print("Entrenando modelo con datos ficticios...")
        for _ in range(3):
            print(f"Aprendí la palabra: {self.palabra_aleatoria()}")
        print("Entrenamiento básico completado.")
