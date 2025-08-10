# megarnucleusx13/definicion.py
def definicion_basica(palabra):
    if not palabra:
        return "No se proporcionó palabra."
    palabra = palabra.lower().strip()
    definiciones = {
        "hola": "saludo informal usado para iniciar una conversación.",
        "python": "lenguaje de programación interpretado, usado para scripts y prototipos rápidos.",
        "vector": "lista ordenada de números; estructura matemática.",
        "matriz": "arreglo bidimensional de números.",
        "algoritmo": "conjunto de pasos para resolver un problema."
    }
    return definiciones.get(palabra, f"No tengo una definición preparada para '{palabra}'. Puedes enseñarme con /teach y añadir una definición en defs.json.")

