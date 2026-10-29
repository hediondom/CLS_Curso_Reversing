# -*- coding: utf-8 -*-
"""Genera CLS_Guia/practicas.html: el "Banco de prácticas".

Lista los binarios del corpus que el inventario marcó como «practica (solo VM)»
(crackmes y targets didácticos), con su tamaño, SHA-256 y enlace, un protocolo de
seguridad fuerte y el mapeo de los que el curso usa a su tute/lección.

NO afirma que los binarios sean seguros: se ejecutan SOLO en VM aislada, bajo
responsabilidad de quien los corre. Excluye por completo lo marcado cuarentena/excluido.
"""
import csv
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
GUIA = os.path.join(RAIZ, "CLS_Guia")
INV = os.path.join(RAIZ, "CLS_resultados_intermedios", "inventario_limpio", "CLS_inventario_limpio.csv")
ESTADO_OK = "practica (solo VM)"

# Crackmes que el Curso usa, mapeados a su tute/lección (por nombre de archivo en el corpus).
MAPEO = {
    "crackme_cruehead 1.0.exe": (
        "El crackme clásico de **Cruehead**, el mismo que reversea el Curso IDA.",
        '[tutes 3](ida_tutes/3.html), [4](ida_tutes/4.html), [10](ida_tutes/10.html) y [19](ida_tutes/19.html) · lecciones [IDA](guia/02-ida.html) y [Debugger](guia/02-debugger.html)',
    ),
}


def rel(rutaabs):
    r = os.path.relpath(rutaabs, GUIA).replace("\\", "/")
    return "/".join(quote(p) for p in r.split("/"))


def main():
    rows = [r for r in csv.DictReader(open(INV, encoding="utf-8-sig"), delimiter=";")
            if r["estado"] == ESTADO_OK]
    # dedup por sha256
    vist, uniq = set(), []
    for r in rows:
        h = r.get("sha256", "")
        if h and h in vist:
            continue
        vist.add(h)
        uniq.append(r)
    exes = sorted([r for r in uniq if r["archivo"].lower().endswith(".exe")], key=lambda r: r["archivo"].lower())
    packs = sorted([r for r in uniq if r["archivo"].lower().endswith((".zip", ".rar", ".7z"))], key=lambda r: r["archivo"].lower())

    H = []
    H.append('<p class="migas"><a href="00_EMPEZAR_AQUI.html">← Inicio</a></p>')
    H.append("<h1>Banco de prácticas</h1>")
    H.append(f'<p class="meta-tute"><strong>🧪 {len(exes)} crackmes listos</strong> + {len(packs)} targets empacados · '
             "todos marcados «práctica (solo VM)» en el inventario</p>")
    H.append(
        '<aside class="callout peligro"><p class="callout-titulo">Antes de ejecutar NADA de acá</p>'
        "<p>Estos binarios están en el corpus y el inventario los marcó como material de práctica, pero "
        "<strong>no verificamos que sean seguros</strong>. Ejecutalos <strong>solo</strong> así:</p>"
        "<ul>"
        "<li><strong>VM aislada</strong> (sin carpetas compartidas ni red), con un <strong>snapshot</strong> previo para revertir.</li>"
        "<li><strong>Nunca</strong> en tu máquina real ni en una VM con datos tuyos.</li>"
        "<li>Verificá el <strong>SHA-256</strong> antes de usarlos (está al lado de cada uno) para confirmar que son los mismos que acá.</li>"
        "<li>Son <strong>crackmes</strong> —programas hechos para practicar reversing—, no software ajeno: el objetivo es entenderlos, no eludir licencias reales.</li>"
        "</ul><p>Corré bajo tu responsabilidad.</p></aside>"
    )

    # Mapeo al curso
    H.append("<h2>Los que usa el curso</h2>")
    hay_mapa = False
    for r in exes:
        key = r["archivo"].lower()
        if key in MAPEO:
            hay_mapa = True
            desc, refs = MAPEO[key]
            sha = r.get("sha256", "")[:16]
            H.append(f'<p><strong><a class="fuente" href="{rel(os.path.join(RAIZ, r["ruta"]))}">{build.esc(r["archivo"])}</a></strong> '
                     f"({r['MB']} MB · <code>{sha}…</code>)<br>{build.esc(desc)}<br><em>Se usa en:</em> {refs}.</p>")
    if not hay_mapa:
        H.append("<p>(No se encontró el binario mapeado en esta corrida.)</p>")
    H.append(
        '<aside class="callout nota"><p class="callout-titulo">Qué NO está</p>'
        "<p>Varios targets que el Curso IDA nombra (los `HOLA_REVERSER.exe`, `TEST_REVERSER.exe`, `IDA1`–`IDA3.exe`) "
        "<strong>no están</strong> como archivo en el corpus, o están en <strong>cuarentena</strong> (por eso no aparecen). "
        "Igual podés practicar lo mismo con cualquiera de los crackmes de abajo.</p></aside>"
    )

    # Práctica libre
    H.append("<h2>Práctica libre (crackmes listos)</h2>")
    H.append("<p>Crackmes para analizar con el método del curso (strings → <code>main</code> → xrefs → renombrar → confirmar en el debugger). De menor a mayor dificultad, a ojo por tamaño:</p>")
    H.append("<ul>")
    for r in exes:
        if r["archivo"].lower() in MAPEO:
            continue
        sha = r.get("sha256", "")[:16]
        H.append(f'<li><a class="fuente" href="{rel(os.path.join(RAIZ, r["ruta"]))}">{build.esc(r["archivo"])}</a> '
                 f"— {r['MB']} MB · <code>{sha}…</code></li>")
    H.append("</ul>")

    # Empacados
    if packs:
        H.append("<h2>Targets empacados (avanzado, fuera del recorrido base)</h2>")
        H.append("<p>Para practicar <strong>desempaquetado</strong> (UPX, ASPack, etc.). El unpacking de protectores queda fuera del recorrido base de esta guía; se listan por completitud.</p>")
        H.append("<ul>")
        for r in packs:
            sha = r.get("sha256", "")[:16]
            H.append(f'<li><a class="fuente" href="{rel(os.path.join(RAIZ, r["ruta"]))}">{build.esc(r["archivo"])}</a> '
                     f"— {r['MB']} MB · <code>{sha}…</code></li>")
        H.append("</ul>")

    H.append('<p class="migas"><a href="materiales.html">← Todos los materiales</a> · <a href="00_EMPEZAR_AQUI.html">Inicio</a></p>')

    build.construir(os.path.join(GUIA, "practicas.html"), "Banco de prácticas (CLS)",
                    "Crackmes y targets didácticos del corpus para practicar en VM, con hash y mapeo al curso.",
                    "\n".join(H))
    print(f"practicas.html -> {len(exes)} exe + {len(packs)} empacados")


if __name__ == "__main__":
    main()
