# megarnucleusx13/megan_beta1.py
import re
import os
import json
import random
import datetime
import difflib
import numpy as np

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
VOCAB_FILE = os.path.join(DATA_DIR, "vocab.json")
DEFS_FILE = os.path.join(DATA_DIR, "defs.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

os.makedirs(DATA_DIR, exist_ok=True)

def _now_ts():
    return datetime.datetime.utcnow().isoformat() + "Z"

class MeganRBeta1:
    def __init__(self, persist=True, history_len=8):
        self.nombre = "MeganR Nucleus X13"
        self.version = "0.0.2.5b1"
        self.persist = persist
        self.history_len = history_len

        # vocab base ampliado (añade lo que quieras)
        base_vocab = [
            "hola","adiós","mundo","python","inteligencia","algoritmo","dato","nube",
            "entrenar","aprender","consola","proyecto","función","variable","random",
            "vector","matriz","código","número","tiempo","texto","simulación","red",
            "modelo","bot","ayuda","cómo","quién","qué","por","gracias","bien","mal",
            "sí","no","claro","ok","genial","increíble","estás","megan","saludos",
            "buenos","días","noches","pregunta","respuesta","ejemplo","prueba","debug",
            "error","problema","solución","lista","array","suma","resta","multiplica",
            "dividir","operación","emocion","emoji","leer","definir","definición",
            "leerletras","convertir","mapa","alfabeto"
        ]
        self.vocabulario = set(base_vocab)

        # cargar vocab persistente si existe
        if self.persist and os.path.exists(VOCAB_FILE):
            try:
                with open(VOCAB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.vocabulario.update(data.get("vocab", []))
            except Exception:
                pass

        # respuestas fijas (más largas)
        self.patrones_respuesta = [
            (r"\b(hola|buenas|buenos días|buenas noches|saludos)\b",
             "Hola — soy Megan. Estoy en versión beta1. Puedo conversar, hacer operaciones matemáticas básicas, y aprender palabras que me enseñes con /teach <palabra>. ¿En qué puedo ayudarte hoy?"),
            (r"\b(adiós|chao|nos vemos|hasta luego)\b",
             "Adiós. Fue un gusto conversar. ¡Vuelve cuando quieras!"),
            (r"\b(cómo (estás|te sientes))\b",
             "Estoy bien, gracias. Soy una IA de desarrollo; siempre lista para aprender y mejorar."),
            (r"\b(quién (eres|eres tú)|quien eres)\b",
             f"Soy {self.nombre} (v{self.version}), un bot en desarrollo. Puedo responder preguntas simples, ejecutar sumas o convertir texto a números."),
            (r"\b(qué sabes hacer|qué puedes hacer)\b",
             "Puedo responder preguntas simples, realizar operaciones con vectores/matrices (ver funciones), enseñar nuevas palabras con /teach, y convertir texto a secuencias numéricas (modo lectura)."),
            (r"\b(gracias|muchas gracias)\b",
             "¡De nada! Me alegra poder ayudar."),
            (r"\b(ayuda|help)\b",
             "Comandos: /teach <palabra>, /save, /stats, /def <palabra>, /read <texto>, /exit")
        ]

        # definiciones (cargar si existe)
        self.defs = {}
        if self.persist and os.path.exists(DEFS_FILE):
            try:
                with open(DEFS_FILE, "r", encoding="utf-8") as f:
                    self.defs = json.load(f)
            except Exception:
                self.defs = {}

        # stats e historial
        self.stats = {"queries": 0, "fixed": 0, "known_word": 0, "fallback": 0}
        self.history = []
        if self.persist and os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f).get("history", [])
            except Exception:
                self.history = []

        # emoji primer uso tracker
        self._seen_emojis = set()

    # tokenizador robusto (quita puntuación, separa palabras, mantiene emoji tokens)
    def tokenizar(self, texto):
        if not isinstance(texto, str):
            return []
        # extraer emojis (básico unicode range) y palabras alfanuméricas
        # nota: esto es simple, no cubre todos los emojis
        emoji_pattern = re.compile(
            "[" 
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\u2600-\u26FF\u2700-\u27BF"
            "]+", flags=re.UNICODE)
        emojis = emoji_pattern.findall(texto)
        # palabras: letras, dígitos, apostrófos
        words = re.findall(r"\b[\w']+\b", texto.lower(), flags=re.UNICODE)
        return words + emojis

    # autocorrección básica: devuelve palabra corregida o None
    def autocorrect(self, palabra, cutoff=0.8):
        if not palabra:
            return None
        # solo para palabras no-numéricas y sin emojis
        if re.match(r"^[a-zA-Z]+$", palabra):
            candidates = difflib.get_close_matches(palabra.lower(), self.vocabulario, n=1, cutoff=cutoff)
            return candidates[0] if candidates else None
        return None

    # convertir texto a números a=1..z=26, ignora otros chars, devuelve lista de ints por palabra
    def texto_a_numeros(self, texto):
        mapping = {chr(i + 96): i for i in range(1, 27)}  # a:1 ... z:26
        resultados = []
        for ch in texto.lower():
            if ch in mapping:
                resultados.append(mapping[ch])
            # separar palabras con espacios si quieres listas por palabra; aquí es secuencia continua
        return resultados

    def _match_fixed(self, texto):
        for pattern, respuesta in self.patrones_respuesta:
            if re.search(pattern, texto, flags=re.IGNORECASE):
                return respuesta
        return None

    def _save_all(self):
        if not self.persist:
            return
        try:
            with open(VOCAB_FILE, "w", encoding="utf-8") as f:
                json.dump({"vocab": sorted(list(self.vocabulario))}, f, ensure_ascii=False, indent=2)
            with open(DEFS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.defs, f, ensure_ascii=False, indent=2)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({"history": self.history[-self.history_len:]}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def responder(self, texto, user_id=None):
        self.stats["queries"] += 1

        if not texto or not isinstance(texto, str) or texto.strip() == "":
            return "No recibí nada. Escribe algo para conversar."

        texto_clean = texto.strip()
        # guardar al historial (simple)
        self.history.append({"ts": _now_ts(), "user": user_id or "local", "text": texto_clean})
        self.history = self.history[-(self.history_len * 2):]  # mantener algo de contexto

        # detectar emojis y primer uso
        emojis = [t for t in self.tokenizar(texto_clean) if re.match(r'[\U0001F300-\U0001F6FF\u2600-\u27BF]', t)]
        if emojis:
            for em in emojis:
                if em not in self._seen_emojis:
                    self._seen_emojis.add(em)
                    msg = f"Veo que usaste {em} — me gusta ver emojis 😊. (nota: aún manejo emojis de forma básica)"
                    self._save_all()
                    self.stats["fixed"] += 1
                    return msg

        # 1) respuesta fija por patrón
        fixed = self._match_fixed(texto_clean)
        if fixed:
            self.stats["fixed"] += 1
            self._save_all()
            return fixed

        # 2) tokenizar y buscar palabras conocidas (con autocorrect)
        tokens = self.tokenizar(texto_clean)
        for t in tokens:
            # intento autocorrect si no está exactamente
            if t in self.vocabulario:
                self.stats["known_word"] += 1
                return f"Conozco la palabra '{t}'. ¿Quieres que la defina? Usa /def {t}"
            else:
                cor = self.autocorrect(t, cutoff=0.82)
                if cor:
                    # sugerir autocorrección y usarla como respuesta conocida
                    self.vocabulario.add(cor)  # opcional: añadir autosugerida
                    self.stats["known_word"] += 1
                    return f"¿Quisiste decir '{cor}'? Conozco esa palabra. Usa /def {cor} para una definición."
        # 3) fallback: fallback mejorado con palabra aleatoria y conversión numérica
        aleatoria = random.choice(list(self.vocabulario))
        numeros = self.texto_a_numeros(aleatoria)
        resp = (f"No entendí exactamente eso. Aquí una palabra de mi vocabulario: '{aleatoria}'. "
                f"Modo lectura (beta): {numeros} — (a=1,b=2,...).")
        self.stats["fallback"] += 1
        self._save_all()
        return resp

    # funciones tipo numpy con validación
    def sumar_vectores(self, a, b):
        try:
            return np.add(np.asarray(a), np.asarray(b)).tolist()
        except Exception:
            raise ValueError("Entradas inválidas para sumar_vectores. Usa listas/arrays compatibles.")

    def multiplicar_matrices(self, a, b):
        try:
            return np.dot(np.asarray(a), np.asarray(b)).tolist()
        except Exception:
            raise ValueError("Entradas inválidas para multiplicar_matrices. Asegura dimensiones compatibles.")

    # teach, save, def
    def teach(self, palabra):
        palabra = palabra.strip().lower()
        if not palabra:
            return False
        self.vocabulario.add(palabra)
        self._save_all()
        return True

    def define(self, palabra):
        palabra = palabra.strip().lower()
        if not palabra:
            return None
        if palabra in self.defs:
            return self.defs[palabra]
        # si no existe, intento una definición simple automática
        simple = f"'{palabra}' es una palabra aprendida por Megan. (definición básica automática en beta)"
        # guardarlo para futuras referencias
        self.defs[palabra] = simple
        self._save_all()
        return simple

    def get_stats(self):
        return dict(self.stats)
