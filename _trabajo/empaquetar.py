# -*- coding: utf-8 -*-
"""Arma los ZIP para compartir el curso, sin seleccionar carpetas a mano.

- curso_solo.zip        : solo CLS_Guia (liviano). El curso funciona; los enlaces
                          a videos/transcripciones no abren hasta tener esas carpetas al lado.
- curso_con_videos.zip  : la carpeta portable (CLS_curso_portable) entera, que ya trae la guía
                          + SOLO los materiales que las citas referencian (videos del curso,
                          juntadas y audios de Telegram, transcripciones), con la estructura de
                          carpetas lista para que todos los enlaces relativos abran al descomprimir.

Uso:
    py -3 empaquetar.py            # arma solo el liviano (rápido)
    py -3 empaquetar.py --con-videos   # arma también el grande (varios GB, tarda)

No modifica nada del proyecto: solo lee y escribe los .zip en CLS_proyecto/paquetes/.
"""
import os
import sys
import time
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
SALIDA = os.path.join(RAIZ, "paquetes")

# Carpetas de CLS_Guia que NO se comparten (generadores, perfiles, backups).
EXCLUIR_EN_GUIA = {"_trabajo"}
EXCLUIR_PREFIJO = ("_backup_",)

# Para el paquete grande: la carpeta portable ya curada (guía + solo lo citado).
PORTABLE = os.path.join(RAIZ, "CLS_curso_portable")


def _saltar_dir(nombre):
    return nombre in EXCLUIR_EN_GUIA or nombre.startswith(EXCLUIR_PREFIJO)


def agregar_carpeta(zf, carpeta_abs, arc_base, saltar_guia=False):
    """Agrega una carpeta al zip; arc_base es el nombre con que entra (p. ej. 'CLS_Guia')."""
    n, bytes_tot = 0, 0
    for root, dirs, files in os.walk(carpeta_abs):
        if saltar_guia:
            dirs[:] = [d for d in dirs if not _saltar_dir(d)]
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, carpeta_abs)
            arc = os.path.join(arc_base, rel).replace("\\", "/")
            try:
                zf.write(full, arc)
                n += 1
                bytes_tot += os.path.getsize(full)
            except (PermissionError, FileNotFoundError, OSError) as e:
                print("  (omitido)", arc, "->", e)
    return n, bytes_tot


def humano(b):
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"


def hacer_solo():
    os.makedirs(SALIDA, exist_ok=True)
    destino = os.path.join(SALIDA, "curso_solo.zip")
    print("Armando", destino, "(solo CLS_Guia, comprimido)...")
    t0 = time.time()
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        n, b = agregar_carpeta(zf, os.path.join(RAIZ, "CLS_Guia"), "CLS_Guia", saltar_guia=True)
    print(f"  {n} archivos, {humano(b)} sin comprimir -> {humano(os.path.getsize(destino))} en el zip ({time.time()-t0:.0f}s)")
    print(f"  Al descomprimir: abrir CLS_Guia/00_EMPEZAR_AQUI.html")


def hacer_con_videos():
    os.makedirs(SALIDA, exist_ok=True)
    if not os.path.isdir(PORTABLE):
        print("  No existe", PORTABLE, "- armala antes con armar_curso_portable.py.")
        return
    destino = os.path.join(SALIDA, "curso_con_videos.zip")
    print("Armando", destino, "(carpeta portable entera, SIN recomprimir)...")
    print("  Esto puede tardar y pesar varios GB. No cierres hasta que diga LISTO.")
    t0 = time.time()
    # ZIP_STORED: los .mp4/.ogg ya están comprimidos; recomprimir no sirve y es lento.
    # Se empaqueta el contenido de CLS_curso_portable en la raíz del zip (CLS_Guia y las
    # carpetas de materiales quedan como hermanas, igual que en el proyecto).
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_STORED, allowZip64=True) as zf:
        n, b = agregar_carpeta(zf, PORTABLE, "")
    print(f"  LISTO: {n} archivos, {humano(os.path.getsize(destino))} en el zip ({time.time()-t0:.0f}s)")
    print(f"  Al descomprimir (en una carpeta vacía): abrir CLS_Guia/00_EMPEZAR_AQUI.html; todo abre por ruta relativa.")


def main():
    hacer_solo()
    if "--con-videos" in sys.argv:
        hacer_con_videos()
    else:
        print("\n(Para el paquete grande con videos: py -3 empaquetar.py --con-videos)")


if __name__ == "__main__":
    main()
