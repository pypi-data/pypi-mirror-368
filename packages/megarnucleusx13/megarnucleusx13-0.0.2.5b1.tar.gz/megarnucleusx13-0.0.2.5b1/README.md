# MeganR Nucleus X13
MeganR Nucleus X13 es una IA experimental desarrollada en Python.  
Actualmente en fase beta pero con mas estabilidad y menos margen de errores en eata nueva version a cambiado mucho (`0.0.2.5b1`), con un sistema de tokenización básico, respuestas predefinidas y vocabulario expandido.

## Instalación
```bash
pip install megarnucleusx13

# usos de ejemplo
ejecutar una conversacio directamente en la consola python clip_beta1.py a conrinuacion pruebaw y comandos

# Pruebas y comandos:



hola → respuesta fija extendida.

hola; o hola! → tokenizador debe limpiar y dar la misma respuesta.

😀 o 😊 → primer uso emoji produce mensaje especial.

/teach unicornio → añade unicornio al vocab y guarda.

/def unicornio → crea/retorna definición automática.

/read abc → devuelve [1,2,3] (lectura beta).

/stats → ver estadísticas
