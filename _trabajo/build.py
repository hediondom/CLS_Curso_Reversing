# -*- coding: utf-8 -*-
"""Generador del paquete de estudio CLS.

Convierte los Markdown de _trabajo/src en HTML offline con navegacion comun.
No toca las fuentes del proyecto: solo escribe dentro de CLS_Guia.
"""
import html
import os
import re
import urllib.parse

GUIA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ = os.path.dirname(GUIA)
SRC = os.path.join(GUIA, "_trabajo", "src")

ORDEN = [
    ("00_EMPEZAR_AQUI.html", "Inicio"),
    ("guia/index.html", "Curso"),
    ("materiales.html", "Materiales"),
    ("fichas/index.html", "Fichas"),
    ("glosario.html", "Glosario"),
    ("preguntas_y_respuestas.html", "Repaso"),
    ("buscar.html", "Buscar"),
]


def esc(t):
    return html.escape(t, quote=False)


def _enlace(m):
    label, url = m.group(1), m.group(2)
    url = url.strip()
    externo = url.startswith(("http://", "https://", "mailto:"))
    attrs = ' rel="noopener" target="_blank"' if externo else ""
    return f'<a href="{html.escape(url)}"{attrs}>{label}</a>'


def inline(text):
    piezas = []

    def guardar(m):
        piezas.append("<code>" + esc(m.group(1)) + "</code>")
        return f"\x00{len(piezas)-1}\x00"

    text = re.sub(r"`([^`]+)`", guardar, text)
    text = esc(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _enlace, text)

    def restaurar(m):
        return piezas[int(m.group(1))]

    return re.sub("\x00(\\d+)\x00", restaurar, text)


def expandir_fuentes(text, fuera):
    """{{src:RUTA|ETIQUETA}} -> enlace relativo al proyecto desde CLS_Guia."""

    def rep(m):
        cuerpo = m.group(1)
        if "|" in cuerpo:
            ruta, label = cuerpo.split("|", 1)
        else:
            ruta, label = cuerpo, os.path.basename(cuerpo.replace("\\", "/"))
        ruta = ruta.strip().replace("\\", "/")
        url = urllib.parse.quote(ruta, safe="/")
        return f'<a class="fuente" href="{fuera}{url}">{esc(label.strip())}</a>'

    return re.sub(r"\{\{src:([^}]+)\}\}", rep, text)


def tabla(block):
    lineas = [l.strip() for l in block.strip().split("\n") if l.strip()]
    if len(lineas) < 2:
        return None
    cab = [c.strip() for c in lineas[0].strip("|").split("|")]
    filas = [l for l in lineas[1:] if not re.match(r"^[\s:|-]+$", l.strip("|"))]
    salida = ['<div class="tabla"><table>', "<thead><tr>"]
    salida += [f"<th>{inline(c)}</th>" for c in cab]
    salida.append("</tr></thead><tbody>")
    for f in filas:
        celdas = [c.strip() for c in f.strip("|").split("|")]
        salida.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in celdas) + "</tr>")
    salida.append("</tbody></table></div>")
    return "\n".join(salida)


def md(texto):
    texto = texto.replace("\r\n", "\n")
    lineas = texto.split("\n")
    out, i = [], 0
    parrafo = []

    def cerrar():
        if parrafo:
            out.append("<p>" + inline(" ".join(parrafo)) + "</p>")
            parrafo.clear()

    while i < len(lineas):
        s = lineas[i].strip()

        if s.startswith("```"):
            cerrar()
            lang = s[3:].strip()
            bloque = []
            i += 1
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                bloque.append(lineas[i])
                i += 1
            i += 1
            clase = f' class="lenguaje-{esc(lang)}"' if lang else ""
            out.append(f"<pre><code{clase}>" + esc("\n".join(bloque)) + "</code></pre>")
            continue

        if s.startswith(":::"):
            cerrar()
            cab = s[3:].strip().split(" ", 1)
            tipo = (cab[0] or "nota").strip("{}")
            titulo = cab[1] if len(cab) > 1 else ""
            cuerpo = []
            i += 1
            while i < len(lineas) and not lineas[i].strip().startswith(":::"):
                cuerpo.append(lineas[i])
                i += 1
            i += 1
            h = f'<p class="callout-titulo">{inline(titulo)}</p>' if titulo else ""
            out.append(f'<aside class="callout {esc(tipo)}">{h}{md(chr(10).join(cuerpo))}</aside>')
            continue

        if s.startswith("#"):
            cerrar()
            nivel = min(len(s) - len(s.lstrip("#")), 6)
            titulo = s[nivel:].strip()
            anchor = re.sub(r"[^a-z0-9áéíóúñü]+", "-", titulo.lower()).strip("-")
            out.append(f'<h{nivel} id="{esc(anchor)}">{inline(titulo)}</h{nivel}>')
            i += 1
            continue

        if s.startswith("?? "):
            cerrar()
            pregunta = s[3:].strip()
            i += 1
            respuesta = []
            if i < len(lineas) and lineas[i].strip().startswith("!! "):
                respuesta.append(lineas[i].strip()[3:].strip())
                i += 1
                while i < len(lineas) and lineas[i].strip() and not lineas[i].strip().startswith(("?? ", ":::", "#")):
                    respuesta.append(lineas[i].strip())
                    i += 1
            out.append(
                f'<details class="qa"><summary>{inline(pregunta)}</summary>'
                f'<div class="respuesta">{md(" ".join(respuesta))}</div></details>'
            )
            continue

        if s.startswith("|") and "|" in s:
            cerrar()
            bloque = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                bloque.append(lineas[i])
                i += 1
            t = tabla("\n".join(bloque))
            if t:
                out.append(t)
            continue

        if re.match(r"^[-*] ", s):
            cerrar()
            items = []
            while i < len(lineas) and re.match(r"^[-*] ", lineas[i].strip()):
                items.append(re.sub(r"^[-*] ", "", lineas[i].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue

        if re.match(r"^\d+\. ", s):
            cerrar()
            items = []
            while i < len(lineas) and re.match(r"^\d+\. ", lineas[i].strip()):
                items.append(re.sub(r"^\d+\. ", "", lineas[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
            continue

        if s.startswith(">"):
            cerrar()
            cita = []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                cita.append(lineas[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + md("\n".join(cita)) + "</blockquote>")
            continue

        if s in ("---", "***"):
            cerrar()
            out.append("<hr>")
            i += 1
            continue

        if not s:
            cerrar()
            i += 1
            continue

        parrafo.append(s)
        i += 1

    cerrar()
    return "\n".join(out)


PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descripcion}">
<link rel="stylesheet" href="{css}">
</head>
<body>
<a class="salto" href="#contenido">Saltar al contenido</a>
<header class="cabecera">
  <div class="marca"><a href="{home}">CLS · Curso de reversing</a> <span class="edicion">edición 5 · 27/10/2026</span></div>
  <nav class="principal" aria-label="Navegación principal">
{nav}
  </nav>
</header>
<main id="contenido">
{contenido}
</main>
<footer class="pie">
  <p>Material educativo y defensivo. Las prácticas se limitan a programas propios, software abierto o crackmes diseñados para aprender. No se enseña a eludir licencias, DRM ni controles de acceso.</p>
  <p><a href="{home}">Inicio</a> · <a href="{etapas}">Etapas</a> · <a href="{fuentes}">Fuentes y límites</a> · <a href="{registro}">Registro de cobertura</a></p>
</footer>
</body>
</html>
"""


def prefijo(destino):
    rel = os.path.relpath(destino, GUIA).replace("\\", "/")
    return "../" * rel.count("/")


def construir(destino, titulo, descripcion, cuerpo):
    pre = prefijo(destino)
    fuera = "../" * (pre.count("../") + 1)
    nav = "\n".join(f'    <a href="{pre}{href}">{label}</a>' for href, label in ORDEN)
    home = pre + "00_EMPEZAR_AQUI.html"
    html_final = PLANTILLA.format(
        titulo=esc(titulo), descripcion=esc(descripcion), css=pre + "guia/estilo.css",
        home=home, nav=nav, contenido=cuerpo,
        etapas=pre + "guia/etapa-0.html", fuentes=pre + "fuentes_y_limites.html",
        registro=pre + "registro_de_cobertura.csv",
    )
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(html_final)
    return destino


def migas(items):
    partes = ['<nav class="migas" aria-label="Ubicación">']
    for i, (href, label) in enumerate(items):
        partes.append(f'<a href="{href}">{esc(label)}</a>' if href else f"<span>{esc(label)}</span>")
        if i < len(items) - 1:
            partes.append('<span aria-hidden="true">›</span>')
    partes.append("</nav>")
    return "".join(partes)


def proceso():
    if not os.path.isdir(SRC):
        print("No existe", SRC)
        return
    for root, _dirs, files in os.walk(SRC):
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            src = os.path.join(root, name)
            rel = os.path.relpath(src, SRC).replace("\\", "/")
            destino = os.path.join(GUIA, rel[:-3] + ".html")
            with open(src, encoding="utf-8") as f:
                crudo = f.read()
            meta, cuerpo = {}, crudo
            if crudo.startswith("---\n"):
                fin = crudo.find("\n---\n", 4)
                cabecera = crudo[4:fin].strip()
                for linea in cabecera.split("\n"):
                    if ":" in linea:
                        k, v = linea.split(":", 1)
                        meta[k.strip()] = v.strip().strip('"').strip("'")
                cuerpo = crudo[fin + 5:]
            destino = os.path.normpath(destino)
            pre = prefijo(destino)
            fuera = "../" * (pre.count("../") + 1)
            cuerpo_html = md(cuerpo)
            cuerpo_html = expandir_fuentes(cuerpo_html, fuera)
            if meta.get("etapa"):
                cuerpo_html = migas([
                    (pre + "00_EMPEZAR_AQUI.html", "Inicio"),
                    (pre + "guia/index.html", "Curso"),
                    (None, meta["etapa"]),
                ]) + cuerpo_html
            construir(destino, meta.get("title", name[:-3]), meta.get("description", ""), cuerpo_html)
            print("ok", os.path.relpath(destino, GUIA))

    fuentes_md = os.path.join(GUIA, "FUENTES_Y_LIMITES.md")
    if os.path.exists(fuentes_md):
        with open(fuentes_md, encoding="utf-8") as f:
            texto = f.read()
        construir(
            os.path.join(GUIA, "fuentes_y_limites.html"),
            "Fuentes y límites",
            "Criterios, cobertura, exclusiones y limitaciones de esta edición.",
            md(texto),
        )
        print("ok fuentes_y_limites.html")


if __name__ == "__main__":
    proceso()
