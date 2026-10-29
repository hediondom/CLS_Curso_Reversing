# -*- coding: utf-8 -*-
"""Convierte los .docx del «Curso IDA desde cero» en páginas-tutorial legibles:
texto + las capturas originales intercaladas en su lugar + tiempo de lectura.

Por cada tute escribe CLS_Guia/ida_tutes/<n>.html (mismo encabezado/CSS del curso) y
guarda sus imágenes en CLS_Guia/ida_tutes/img/<n>/. No es contenido inventado: es el
.docx original, solo presentado como tutorial (y las imágenes grandes se achican para
que cargue, sin perder legibilidad del texto de IDA).

Uso:  py -3 tutes_ida_ilustrados.py [--solo 1-28]
"""
import io
import os
import re
import sys

from docx import Document
from docx.oxml.ns import qn
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # plantilla/encabezado del curso
import gen_materiales as gm  # temas curados y grupos

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
TUTES = os.path.join(RAIZ, "CLS_fuentes_externas", "github", "apuromafo_Crackslatinos",
                     "IDA DESDE CERO", "CURSO DE IDA TUTES")
DEST = os.path.join(RAIZ, "CLS_Guia", "ida_tutes")
IMGDIR = os.path.join(DEST, "img")
MAXW = 1366  # ancho máx.: recorta solo las capturas sobredimensionadas, mantiene legible el texto de IDA

# Heurística de código/asm: dirección hex al inicio, o línea con mnemónico típico.
MNEM = ("mov", "push", "pop", "call", "jmp", "je", "jne", "jz", "jnz", "cmp", "test",
        "add", "sub", "xor", "and", "or", "lea", "ret", "nop", "inc", "dec", "int3",
        "jg", "jl", "jge", "jle", "ja", "jb", "dword", "ptr", "eax", "ebx", "ecx", "edx")
RE_ADDR = re.compile(r"^(?:[0-9A-Fa-f]{6,16}|\.text:[0-9A-Fa-f]+)\b")


def es_codigo(linea):
    s = linea.strip()
    if not s or len(s) > 160:
        return False
    if RE_ADDR.match(s):
        return True
    toks = re.split(r"\s+", s.lower())
    return len(toks) <= 8 and bool(toks) and toks[0] in MNEM


def grupo_de(n):
    for a, b, titulo, nota, lecciones in gm.IDA_GRUPOS:
        if a <= n <= b:
            return titulo, nota, lecciones
    return "", "", []


def achicar(blob, ext):
    """Devuelve (bytes, ext_final). Achica si es muy ancha; si falla, deja el original."""
    try:
        im = Image.open(io.BytesIO(blob))
        if im.width > MAXW:
            h = int(im.height * MAXW / im.width)
            im = im.resize((MAXW, h), Image.LANCZOS)
        out = io.BytesIO()
        fmt = "PNG" if ext.lower() in (".png", ".bmp", ".gif") else "JPEG"
        if fmt == "JPEG" and im.mode in ("RGBA", "P"):
            im = im.convert("RGB")
        if fmt == "JPEG":
            im.save(out, "JPEG", optimize=True, quality=82)
            return out.getvalue(), ".jpg"
        im.save(out, "PNG", optimize=True)
        return out.getvalue(), ".png"
    except Exception:
        return blob, ext


def bloques(doc):
    """Recorre el cuerpo en orden: lista de ('texto', str) | ('img', blob, ext)."""
    out = []
    partes = doc.part.related_parts
    for child in doc.element.body.iterchildren():
        if child.tag in (qn("w:p"), qn("w:tbl")):
            texto = "".join(t.text for t in child.iter(qn("w:t")) if t.text)
            if texto.strip():
                out.append(("texto", texto.strip()))
            for blip in child.iter(qn("a:blip")):
                rid = blip.get(qn("r:embed")) or blip.get(qn("r:link"))
                if not rid or rid not in partes:
                    continue
                part = partes[rid]
                ext = os.path.splitext(part.partname)[1] or ".png"
                out.append(("img", part.blob, ext))
    return out


def cuerpo_html(n, render, n_img, palabras):
    """render: lista de ('texto', s) | ('fig', html_figure)."""
    tema, sintesis, video = gm.IDA_TUTES.get(n, ("", "", ""))
    gtitulo, gnota, lecciones = grupo_de(n)
    minutos = max(1, round(palabras / 180))
    H = []
    H.append('<p class="migas"><a href="../ida-tutes.html">← Índice de los 69 tutes de IDA</a></p>')
    H.append(f"<h1>Tute {n} · {build.esc(tema)}</h1>")
    pal_fmt = f"{palabras:,}".replace(",", ".")
    H.append(f'<p class="meta-tute"><strong>⏱ {minutos} min de lectura</strong> · {pal_fmt} palabras · '
             f"{n_img} capturas · grupo: {build.esc(gtitulo)}</p>")
    if sintesis:
        H.append(f'<aside class="callout nota"><p class="callout-titulo">Qué enseña</p><p>{build.esc(sintesis)}</p></aside>')
    extras = []
    if video:
        extras.append(f'<em>▶ video afín (mismo autor, en x64dbg):</em> <a href="../videos.html">«{build.esc(video)}»</a>')
    if lecciones:
        enl = " · ".join(f'<a href="../guia/{slug}.html">{build.esc(lab)}</a>' for lab, slug in lecciones)
        extras.append(f"<em>se conecta con:</em> {enl}")
    if extras:
        H.append("<p>" + " · ".join(extras) + "</p>")
    H.append('<aside class="callout aviso"><p class="callout-titulo">Material observado, no reescrito</p>'
             "<p>Es el texto y las capturas del <code>.docx</code> original del curso, solo presentados como tutorial. "
             "Puede tener erratas de origen. El autor del curso es Ricardo Narvaja.</p></aside>")
    H.append("<hr>")

    buf = []

    def volcar():
        if buf:
            H.append("<pre class='asm'>" + build.esc("\n".join(buf)) + "</pre>")
            buf.clear()

    for tipo, val in render:
        if tipo == "texto":
            if es_codigo(val):
                buf.append(val)
            else:
                volcar()
                H.append(f"<p>{build.esc(val)}</p>")
        else:
            volcar()
            H.append(val)
    volcar()
    return "\n".join(H)


def una(path, n):
    doc = Document(path)
    blks = bloques(doc)
    outdir = os.path.join(IMGDIR, str(n))
    os.makedirs(outdir, exist_ok=True)
    palabras = sum(len(b[1].split()) for b in blks if b[0] == "texto")
    k = 0
    render = []
    for b in blks:
        if b[0] == "img":
            k += 1
            data, ext = achicar(b[1], b[2])
            fn = f"{k}{ext}"
            with open(os.path.join(outdir, fn), "wb") as f:
                f.write(data)
            render.append(("fig", f'<figure><img loading="lazy" src="img/{n}/{fn}" alt="Captura {k} del tute {n}"></figure>'))
        else:
            render.append(("texto", b[1]))
    cuerpo = cuerpo_html(n, render, k, palabras)
    tema = gm.IDA_TUTES.get(n, ("", "", ""))[0]
    destino = os.path.join(DEST, f"{n}.html")
    build.construir(destino, f"Tute {n} · {tema} — Curso IDA",
                    f"Tutorial ilustrado del tute {n} del Curso IDA desde cero: {tema}.", cuerpo)
    return k, palabras


def parse_solo(arg):
    m = re.match(r"(\d+)-(\d+)", arg)
    if m:
        return set(range(int(m.group(1)), int(m.group(2)) + 1))
    return {int(x) for x in arg.split(",")}


def main():
    solo = None
    if "--solo" in sys.argv:
        solo = parse_solo(sys.argv[sys.argv.index("--solo") + 1])
    os.makedirs(DEST, exist_ok=True)
    docs = [f for f in os.listdir(TUTES) if f.lower().endswith(".docx")]
    docs.sort(key=lambda f: int(re.match(r"(\d+)", f).group(1)))
    tot_img = 0
    hechos = []
    for f in docs:
        n = int(re.match(r"(\d+)", f).group(1))
        if solo and n not in solo:
            continue
        try:
            ki, pal = una(os.path.join(TUTES, f), n)
        except Exception as e:
            print(f"  {n:3d}  ERROR: {e}")
            continue
        tot_img += ki
        hechos.append(n)
        print(f"  {n:3d}  {ki:3d} capturas  {pal:5d} palabras")
    tam = 0
    for root, _, files in os.walk(DEST):
        tam += sum(os.path.getsize(os.path.join(root, x)) for x in files)
    print(f"\n{len(hechos)} tutes, {tot_img} capturas -> {DEST}  ({tam/1e6:.0f} MB)")


if __name__ == "__main__":
    main()
