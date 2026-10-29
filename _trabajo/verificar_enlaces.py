# -*- coding: utf-8 -*-
"""Verifica que los enlaces relativos de las paginas y las rutas de los CSV existan."""
import csv
import os
import re
import urllib.parse

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
GUIA = os.path.join(RAIZ, "CLS_Guia")

roto = []
total = 0
for root, _dirs, files in os.walk(GUIA):
    if "_backup" in root or "_trabajo" in root:
        continue
    for name in files:
        if not name.endswith(".html"):
            continue
        path = os.path.join(root, name)
        with open(path, encoding="utf-8") as f:
            html = f.read()
        for m in re.finditer(r'(?:href|src)="([^"]+)"', html):
            url = m.group(1)
            if url.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            total += 1
            limpio = urllib.parse.unquote(url.split("#")[0])
            destino = os.path.normpath(os.path.join(root, limpio.replace("/", os.sep)))
            if not os.path.exists(destino):
                roto.append((os.path.relpath(path, GUIA), url, os.path.relpath(destino, RAIZ)))

print(f"Enlaces relativos revisados: {total}")
print(f"Rotas: {len(roto)}")
for p, u, d in roto[:80]:
    print(f"  {p} -> {u}  (resuelve a {d})")

# Rutas del mapa de cobertura
mapa = os.path.join(GUIA, "mapa_de_cobertura.csv")
faltan_csv = []
with open(mapa, encoding="utf-8-sig") as f:
    for fila in csv.DictReader(f, delimiter=";"):
        ruta = fila["ruta_relativa"]
        if ruta and ruta != "n/a":
            if not os.path.exists(os.path.join(RAIZ, ruta.replace("/", os.sep))):
                faltan_csv.append(ruta)
print(f"Rutas del mapa faltantes: {len(faltan_csv)}")
for r in faltan_csv:
    print("  ", r)
