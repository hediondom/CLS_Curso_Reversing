# -*- coding: utf-8 -*-
"""Genera src/videos.md: índice de videotutoriales con enlace y ruta absoluta en Windows.

Escanea CLS_videos_extraidos y lista cada video (.mp4) con:
- un enlace relativo para abrirlo desde el HTML ({{src:...}} lo resuelve),
- la ruta absoluta en Windows (texto copiable, útil en el PDF).
No copia ningún video: solo los enlaza en su ubicación actual.
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
GUIA = os.path.join(RAIZ, "CLS_Guia")
VID = os.path.join(RAIZ, "CLS_videos_extraidos")
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "videos.md")

# (título de sección, subcarpeta base donde viven los capítulos, descripción)
CURSOS = [
    ("Reversing desde cero (Ricardo y Solid)",
     "Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero",
     "El tronco del curso. Cada capítulo que la guía cita como «Reversing desde cero, cap. NN» es uno de estos videos."),
    ("Videos y material adicional (MASM32 y OllyDbg)",
     "Videos y material adicional Ingenieria Inversa/Videos",
     "Los videos que la guía cita como «Videos y material adicional, Video NN» (curso de MASM32 y de OllyDbg de Cayetano de Juan Úbeda)."),
    ("Reverse engineering con Ricardo Narvaja",
     "Reverse engineering con Ricardo Narvaja",
     "Video suelto (entrevista/stream). Contexto vocacional, no es un tutorial técnico."),
]


def entradas(base_rel):
    base = os.path.join(VID, base_rel)
    out = []
    for root, _dirs, files in os.walk(base):
        for f in files:
            if not f.lower().endswith(".mp4"):
                continue
            full = os.path.join(root, f)
            partes = os.path.relpath(full, base).split(os.sep)
            chap = partes[0] if len(partes) > 1 else os.path.splitext(f)[0]
            titulo = chap if len(partes) <= 2 else f"{chap} — {partes[-2]}"
            m = re.search(r"(\d+)([a-z]?)", chap)
            clave = (int(m.group(1)) if m else 9999, m.group(2) if m else "", chap.lower())
            rel = os.path.relpath(full, RAIZ).replace("\\", "/")        # para {{src}} (desde la raíz del proyecto)
            rel_guia = os.path.relpath(full, GUIA).replace("/", "\\")   # ruta portable, relativa a CLS_Guia
            out.append((clave, titulo, rel, rel_guia))
    out.sort(key=lambda t: t[0])
    return out


def main():
    L = [
        "---",
        'title: "Índice de videotutoriales"',
        'description: "Dónde está en Windows cada video que menciona el curso, con enlace para abrirlo y ruta absoluta."',
        "---",
        "",
        "# Dónde están los videotutoriales",
        "",
        ":::{nota} Cómo usar esta página",
        "Cuando una lección menciona un video (por ejemplo, «Reversing desde cero, cap. 03»), buscalo acá por su número o título. Tenés el **enlace para abrirlo** (▶) y la **ruta relativa** para encontrarlo en el Explorador. Los videos **no** se copian al paquete: se enlazan en su ubicación.",
        ":::",
        "",
        ":::{nota} Enlaces portables: funciona en cualquier PC",
        "Los enlaces de esta página son **relativos**, no dependen de tu usuario ni de la letra de unidad. Abren en cualquier máquina **siempre que la carpeta del curso (`CLS_Guia`) quede al lado de la carpeta `CLS_videos_extraidos`** (las dos dentro de `CLS_proyecto`, como están ahora). La ruta que se muestra, `..\\CLS_videos_extraidos\\...`, es relativa a `CLS_Guia` y vale igual en cualquier equipo.",
        "",
        "**Para compartir todo y que se abra solo:** comprimí la carpeta `CLS_proyecto` completa (o, como mínimo, `CLS_Guia` + `CLS_videos_extraidos` + `CLS_resultados_intermedios`) **manteniendo esa estructura**. Quien la reciba la descomprime donde quiera y abre `CLS_Guia/00_EMPEZAR_AQUI.html`: todos los enlaces resuelven.",
        "",
        "**Aviso de tamaño:** los videos pesan mucho (decenas de GB). Si solo querés compartir el **curso** (liviano), comprimí únicamente `CLS_Guia`: el material funciona, pero los enlaces a videos y transcripciones no van a abrir hasta que esas carpetas estén al lado.",
        ":::",
        "",
        ":::{aviso} Si un enlace no abre el video",
        "Según el navegador, un `.mp4` local puede abrirse, descargarse o pedir permiso. Si no abre, usá la **ruta relativa** que figura al lado, partiendo de la carpeta `CLS_Guia`.",
        ":::",
        "",
    ]
    total = 0
    for titulo_sec, base_rel, desc in CURSOS:
        vids = entradas(base_rel)
        total += len(vids)
        L.append(f"## {titulo_sec}")
        L.append("")
        L.append(f"{desc} ({len(vids)} videos.)")
        L.append("")
        for _k, t, rel, rel_guia in vids:
            L.append(f"- **{t}** — {{{{src:{rel}|▶ abrir}}}} · ruta: `{rel_guia}`")
        L.append("")

    L += [
        "## Python ISO video tutes (lógica de programación · Flash .swf)",
        "",
        "Este material enseña **lógica, no Python** (ver la lección de C y Python). Son archivos **Flash `.swf`**, no `.mp4`: hoy necesitás un reproductor como **Ruffle** para verlos. Están (relativo a `CLS_Guia`) en:",
        "",
        "- `..\\CLS_videos_extraidos\\Python ISO video tutes\\Videotutoriales\\`",
        "",
        "Cada tema está en su subcarpeta (`Algoritmos\\Algoritmos.swf`, `Arreglos1\\Arreglos1.swf`, etc.). Las **transcripciones** en texto de estos videos sí están disponibles y son más cómodas de leer; se enlazan desde la lección de C y Python y desde su ficha.",
        "",
        ":::{nota} Transcripciones en texto",
        f"Además de los {total} videos `.mp4`, cada uno tiene su **transcripción** (`.txt`/`.srt`) en `..\\CLS_resultados_intermedios\\transcripciones\\extraidos\\` (relativo a `CLS_Guia`). Las lecciones citan esas transcripciones (texto), que se leen más rápido que ver el video entero.",
        ":::",
        "",
    ]

    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(L).rstrip() + "\n")
    print(f"{total} videos .mp4 -> {SALIDA}")


if __name__ == "__main__":
    main()
