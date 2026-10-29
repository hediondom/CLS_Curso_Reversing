# -*- coding: utf-8 -*-
"""Extrae el texto de los 69 tutoriales .docx de «Curso IDA desde cero» y arma un índice por tema.

- Guarda el texto de cada tute en _trabajo/extraido_ida/<n>.txt (para leer/citar después).
- Escribe CLS_Guia/ida_tutes_indice.csv: numero;archivo;palabras;resumen (primeras líneas con tema).
No toca los originales.
"""
import csv
import os
import re

from docx import Document

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
TUTES = os.path.join(RAIZ, "CLS_fuentes_externas", "github", "apuromafo_Crackslatinos",
                     "IDA DESDE CERO", "CURSO DE IDA TUTES")
EXTRA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extraido_ida")
SALIDA_CSV = os.path.join(RAIZ, "CLS_Guia", "ida_tutes_indice.csv")

RUIDO = re.compile(r"^(p[aá]gina|http|www\.|\d+\s*$)", re.I)


def texto(path):
    doc = Document(path)
    out = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            out.append(t)
    return out


def resumen(parrafos):
    """Primeras líneas con sustancia (saltea títulos repetidos y ruido)."""
    utiles = []
    for t in parrafos:
        low = t.lower()
        if RUIDO.match(t) or "introduccion al reversing con ida" in low or len(t) < 15:
            continue
        utiles.append(t)
        if len(" ".join(utiles)) > 300:
            break
    s = " ".join(utiles)[:360].replace(";", ",").replace("\n", " ")
    return s if s else " ".join(parrafos[:2])[:360].replace(";", ",")


def num(nombre):
    m = re.match(r"\s*(\d+)", nombre)
    return int(m.group(1)) if m else 9999


def main():
    os.makedirs(EXTRA, exist_ok=True)
    docs = [f for f in os.listdir(TUTES) if f.lower().endswith(".docx")]
    docs.sort(key=num)
    filas = []
    for f in docs:
        full = os.path.join(TUTES, f)
        try:
            parrafos = texto(full)
        except Exception as e:
            filas.append((num(f), f, 0, f"(no se pudo leer: {e})"))
            continue
        palabras = sum(len(p.split()) for p in parrafos)
        with open(os.path.join(EXTRA, f[:-5] + ".txt"), "w", encoding="utf-8") as g:
            g.write("\n".join(parrafos))
        filas.append((num(f), f, palabras, resumen(parrafos)))
        print(f"  {num(f):3d}  {palabras:5d} palabras  {f[:45]}")

    with open(SALIDA_CSV, "w", encoding="utf-8-sig", newline="") as g:
        w = csv.writer(g, delimiter=";")
        w.writerow(["numero", "archivo", "palabras", "resumen_primeras_lineas"])
        for n, f, p, s in filas:
            w.writerow([n, f, p, s])
    tot = sum(p for _, _, p, _ in filas)
    print(f"\n{len(filas)} tutes, {tot} palabras en total -> {SALIDA_CSV}")
    print(f"Textos extraídos en {EXTRA}")


if __name__ == "__main__":
    main()
