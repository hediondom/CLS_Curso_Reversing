# -*- coding: utf-8 -*-
"""Busca una expresion regular en las transcripciones y devuelve citas verificables.

Uso:
  python buscar.py "patron" [--dir RUTA] [--max 40] [--ctx 2]

Para archivos .srt devuelve el timestamp del cue. Para .txt devuelve el numero de linea.
No modifica ningun archivo fuente.
"""
import argparse
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
BASE = os.path.join(RAIZ, "CLS_resultados_intermedios", "transcripciones")


def cues_srt(path):
    """Devuelve [(inicio, texto)] de un SRT."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read().replace("\r\n", "\n")
    out = []
    for block in raw.split("\n\n"):
        lines = [l for l in block.split("\n") if l.strip()]
        if len(lines) >= 3 and "-->" in lines[1]:
            t = lines[1].split("-->")[0].strip()
            out.append((t, " ".join(lines[2:])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("patron")
    ap.add_argument("--dir", default=BASE)
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--ctx", type=int, default=1)
    ap.add_argument("--ignore-case", action="store_true", default=True)
    a = ap.parse_args()
    rx = re.compile(a.patron, re.I if a.ignore_case else 0)
    hits = 0
    for root, _dirs, files in os.walk(a.dir):
        for name in sorted(files):
            if not name.lower().endswith((".srt", ".txt")):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, a.dir)
            if name.lower().endswith(".srt"):
                for t, text in cues_srt(path):
                    if rx.search(text):
                        print(f"{rel}\t{t}\t{text.strip()[:300]}")
                        hits += 1
                        if hits >= a.max:
                            return
            else:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.read().replace("\r\n", "\n").split("\n")
                for i, line in enumerate(lines):
                    if rx.search(line):
                        print(f"{rel}\tL{i+1}\t{line.strip()[:300]}")
                        hits += 1
                        if hits >= a.max:
                            return


if __name__ == "__main__":
    main()
