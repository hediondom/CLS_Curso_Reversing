# -*- coding: utf-8 -*-
"""Valida mapa_de_cobertura.csv contra el disco y, si se pide, lo normaliza.

El CSV es la única fuente del mapa. Este script ya no lo regenera desde una
lista fija: antes lo hacía, y volver a correrlo borraba las filas agregadas a
mano (2D, Etapa 6 y las ampliaciones de 2B/2C/4.1). Para agregar o corregir un
tema, editá el CSV y corré este script para comprobarlo.

Uso:
    python mapa.py                  # solo valida; sale con código 1 si hay errores
    python mapa.py --normalizar     # valida y reescribe el CSV en formato canónico
    python mapa.py --normalizar --salida OTRO.csv   # escribe en otro archivo

Comprueba: encabezado, 8 columnas por fila, etapa y estado conocidos, que la
lección exista como Markdown en _trabajo/src, que la ruta_relativa exista bajo
la raíz del proyecto (salvo "n/a" o estado "excluido") y que no haya filas
repetidas. Las rutas se calculan desde la ubicación de este archivo, así que
funciona aunque el proyecto cambie de disco o de carpeta.
"""
import argparse
import csv
import io
import os
import sys

TRABAJO = os.path.dirname(os.path.abspath(__file__))
GUIA = os.path.dirname(TRABAJO)
RAIZ = os.path.dirname(GUIA)
MAPA = os.path.join(GUIA, "mapa_de_cobertura.csv")
SRC = os.path.join(TRABAJO, "src")

ENCABEZADO = ["tema", "etapa", "leccion", "recurso", "ruta_relativa", "capitulo_o_marca", "estado", "evidencia"]
ETAPAS = {"0", "1", "2", "2D", "2D optativa", "3", "4", "5", "6"}
ESTADOS = {"observado", "sintesis", "externo", "externo/ilustrativo", "pendiente", "excluido", "fuera de alcance"}


def lecciones():
    nombres = set()
    for base, _, archivos in os.walk(SRC):
        nombres.update(a[:-3] for a in archivos if a.endswith(".md"))
    return nombres


def validar(filas):
    errores, avisos = [], []
    if not filas or filas[0] != ENCABEZADO:
        errores.append(f"encabezado inesperado: {filas[0] if filas else '(vacío)'}")
        return errores, avisos
    existentes = lecciones()
    vistas = set()
    for n, fila in enumerate(filas[1:], start=2):
        if len(fila) != len(ENCABEZADO):
            errores.append(f"línea {n}: {len(fila)} columnas en lugar de {len(ENCABEZADO)}")
            continue
        tema, etapa, leccion, _, ruta, _, estado, _ = fila
        if etapa not in ETAPAS:
            errores.append(f"línea {n} ({tema}): etapa desconocida {etapa!r}")
        if estado not in ESTADOS:
            errores.append(f"línea {n} ({tema}): estado desconocido {estado!r}")
        if leccion not in existentes:
            errores.append(f"línea {n} ({tema}): no existe la lección {leccion}.md")
        if ruta != "n/a" and not os.path.exists(os.path.join(RAIZ, ruta.replace("/", os.sep))):
            if estado == "excluido":
                avisos.append(f"línea {n} ({tema}): recurso excluido ausente en disco: {ruta}")
            else:
                errores.append(f"línea {n} ({tema}): no existe {ruta}")
        clave = (tema, leccion, ruta)
        if clave in vistas:
            errores.append(f"línea {n}: fila repetida {clave}")
        vistas.add(clave)
    return errores, avisos


def canonico(filas):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", lineterminator="\n")
    w.writerows(filas)
    return "﻿" + buf.getvalue()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--normalizar", action="store_true", help="reescribir el CSV en formato canónico")
    ap.add_argument("--salida", default=MAPA, help="destino de --normalizar (por defecto, el mismo CSV)")
    args = ap.parse_args()

    with open(MAPA, encoding="utf-8-sig", newline="") as f:
        filas = list(csv.reader(f, delimiter=";"))
    errores, avisos = validar(filas)
    for a in avisos:
        print("aviso:", a)
    for e in errores:
        print("ERROR:", e)
    print(f"{len(filas) - 1} filas en {MAPA} | errores: {len(errores)} | avisos: {len(avisos)}")
    if errores:
        sys.exit(1)

    if args.normalizar:
        nuevo = canonico(filas)
        actual = open(MAPA, encoding="utf-8", newline="").read()
        with open(args.salida, "w", encoding="utf-8", newline="") as f:
            f.write(nuevo)
        print("sin cambios de formato" if nuevo == actual else "formato normalizado", "->", args.salida)


if __name__ == "__main__":
    main()
