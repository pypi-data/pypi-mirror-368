# megarnucleusx13/megan_beta.py
import re
import os
import json
import random
import datetime
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # package root
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")
VOCAB_FILE = os.path.join(DATA_DIR, "vocab.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def _now_ts():
    return datetime.datetime.utcnow().isoformat() + "Z"

class MeganRBeta:
    def __init__(self, persist_vocab=True):
        self.nombre = "MeganR Nucleus X13"
        self.version = "0.0.2.5b0"
        self.persist_vocab = persist_vocab

        # vocab inicial (más grande)
        self.vocabulario = set([
            "hola","adiós","mundo","python","inteligencia","algoritmo","dato",
            "nube","entrenar","aprender","consola","proyecto","función","variable",
            "random","vector","matriz","código","número","tiempo","texto","simulación",
            "red","modelo","bot","ayuda","cómo","quién","qué","por","gracias","bien",
            "mal","sí","no","claro","ok","genial","increíble","estás","megan","saludos",
            "buenos","días","noches","pregunta","respuesta","ejemplo","prueba","debug",
            "error","problema","solución","lista","array","matriz","suma","resta"
        ])

        # cargar vocab persistido si existe
        if self.persist_vocab and os.path.exists(VOCAB_FILE):
            try:
                with open(VOCAB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.vocabulario.update(data.get("vocab", []))
            except Exception:
                # si falla la carga, continuar con vocab por defecto
                pass

        # respuestas fijas con patterns (regex) para ser más flexibles
        self.patrones_respuesta = [
            (r"\b(hola|buenos días|buenas|saludos)\b", "Hola, ¿cómo estás?"),
            (r"\b(adiós|chao|hasta luego)\b", "Adiós, ¡hasta pronto!"),
            (r"\b(cómo (estás|vas))\b", "Estoy bien, gracias por preguntar."),
            (r"\b(quién (eres|so s))\b", f"Soy {self.nombre}, una IA en desarrollo."),
            (r"\b(qué sabes hacer|qué puedes hacer)\b", "Puedo responder preguntas simples, hacer cálculos y aprender nuevas palabras con /teach."),
            (r"\b(gracias|muchas gracias)\b", "De nada, ¡a la orden!"),
            (r"\b(ayuda|help)\b", "Escribe preguntas simples o usa /teach <palabra> para enseñarme, /save para guardar vocab, /stats para ver estadísticas."),
        ]

        # estadísticas simples
        self.stats = {"total_queries": 0, "fixed_matches": 0, "known_word_matches": 0, "fallbacks": 0}
        self.log_file = os.path.join(LOG_DIR, f"conversation_{_now_ts().replace(':','_')}.log")

    # Tokenizador robusto: captura palabras unicode y números, ignora puntuación
    def tokenizar(self, texto):
        if not isinstance(texto, str):
            return []
        # encuentra palabras (letras, dígitos, guiones bajos, apóstrofes) — maneja 'hola;' 'hola!' etc.
        tokens = re.findall(r"\b[\w']+\b", texto.lower(), flags=re.UNICODE)
        return tokens

    def _log(self, user_text, response_text):
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{_now_ts()} | USER: {user_text}\n")
                f.write(f"{_now_ts()} | MEGAN: {response_text}\n\n")
        except Exception:
            # no bloquear por errores de logging
            pass

    def _match_fixed(self, texto):
        for pattern, respuesta in self.patrones_respuesta:
            if re.search(pattern, texto, flags=re.IGNORECASE):
                return respuesta
        return None

    def responder(self, texto):
        self.stats["total_queries"] += 1
        try:
            if not isinstance(texto, str) or texto.strip() == "":
                return "No recibí nada. Dime algo."

            texto_clean = texto.strip()
            # 1) respuesta fija por patrón
            fixed = self._match_fixed(texto_clean)
            if fixed:
                self.stats["fixed_matches"] += 1
                self._log(texto_clean, fixed)
                return fixed

            # 2) detectar si contiene palabra conocida
            tokens = self.tokenizar(texto_clean)
            for t in tokens:
                if t in self.vocabulario:
                    self.stats["known_word_matches"] += 1
                    resp = f"Conozco la palabra '{t}', pero no tengo una respuesta fija aún."
                    self._log(texto_clean, resp)
                    return resp

            # 3) fallback: palabra aleatoria + mensaje
            aleatoria = random.choice(list(self.vocabulario))
            self.stats["fallbacks"] += 1
            resp = f"No entendí eso, pero aquí está una respuesta aleatoria: {aleatoria}"
            self._log(texto_clean, resp)
            return resp

        except Exception as e:
            # seguridad: devolver mensaje de error genérico sin romper la sesión
            return "Ocurrió un error al procesar tu mensaje."

    # Funciones tipo numpy con comprobaciones
    def sumar_vectores(self, a, b):
        try:
            a_arr = np.asarray(a)
            b_arr = np.asarray(b)
            return np.add(a_arr, b_arr)
        except Exception as e:
            raise ValueError("Entradas inválidas para sumar_vectores. Deben ser listas o arrays compatibles.") from e

    def multiplicar_matrices(self, a, b):
        try:
            a_arr = np.asarray(a)
            b_arr = np.asarray(b)
            return np.dot(a_arr, b_arr)
        except Exception as e:
            raise ValueError("Entradas inválidas para multiplicar_matrices. Asegura dimensiones compatibles.") from e

    # persistencia de vocab
    def teach(self, palabra):
        palabra = palabra.strip().lower()
        if not palabra:
            return False
        self.vocabulario.add(palabra)
        return True

    def save_vocab(self):
        if not self.persist_vocab:
            return False
        try:
            with open(VOCAB_FILE, "w", encoding="utf-8") as f:
                json.dump({"vocab": sorted(list(self.vocabulario))}, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def get_stats(self):
        return dict(self.stats)
