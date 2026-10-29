# -*- coding: utf-8 -*-
"""Arma copias autocontenidas y livianas de los 69 tutes IDA ilustrados, para el celular.

Cada copia es un .html único con el CSS y las imágenes embebidas (reescaladas a ~900px,
JPEG, para que pese poco en el teléfono). Incluye navegación anterior/siguiente e índice.
Todo se empaqueta en un ZIP: se descomprime una vez y se abre cualquier tute offline.

Salida: <SCRATCH>/tutes_celular/*.html  y  <SCRATCH>/CLS_tutes_ilustrados_celular.zip
(SCRATCH = variable de entorno CLS_SCRATCH, o %TEMP%/CLS_copias_celular)
Uso:  py -3 copias_celular.py
"""
import base64
import io
import os
import re
import sys
import tempfile
import zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_materiales as gm

GUIA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDAT = os.path.join(GUIA, "ida_tutes")
# Carpeta de salida temporal: CLS_SCRATCH si está definida; si no, una carpeta en el temporal del sistema.
SCRATCH = os.environ.get("CLS_SCRATCH") or os.path.join(tempfile.gettempdir(), "CLS_copias_celular")
OUT = os.path.join(SCRATCH, "tutes_celular")
MAXW = 900

CSS = open(os.path.join(GUIA, "guia", "estilo.css"), encoding="utf-8").read()
BANNER = ('<p style="background:#fffae6;border:1px solid #e0c200;padding:.6rem;border-radius:6px;'
          'font-size:.9rem;margin:.4rem 0 1rem">📱 Copia para celular (imágenes embebidas, reescaladas). '
          'Navegá con los enlaces de arriba/abajo. Los enlaces a videos y lecciones del curso no abren en esta copia suelta.</p>')


def data_uri(path):
    try:
        im = Image.open(path)
        if im.mode in ("RGBA", "P", "LA"):
            im = im.convert("RGB")
        if im.width > MAXW:
            im = im.resize((MAXW, int(im.height * MAXW / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", optimize=True, quality=72)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        b = open(path, "rb").read()
        return "data:image/jpeg;base64," + base64.b64encode(b).decode()


def nav(n, nums):
    i = nums.index(n)
    ant = f'<a href="{nums[i-1]}.html">← Tute {nums[i-1]}</a>' if i > 0 else "<span></span>"
    sig = f'<a href="{nums[i+1]}.html">Tute {nums[i+1]} →</a>' if i < len(nums) - 1 else "<span></span>"
    return (f'<nav class="migas" style="display:flex;justify-content:space-between;gap:1rem">'
            f'{ant}<a href="index.html">Índice</a>{sig}</nav>')


def una_copia(n, nums):
    h = open(os.path.join(IDAT, f"{n}.html"), encoding="utf-8").read()
    h = re.sub(r'<link rel="stylesheet"[^>]*>', "<style>\n" + CSS + "\n</style>", h)
    # imágenes -> data URI reescalado
    def repl(m):
        p = os.path.normpath(os.path.join(IDAT, m.group(1)))
        return 'src="' + data_uri(p) + '"' if os.path.isfile(p) else m.group(0)
    h = re.sub(r'src="(img/[^"]+)"', repl, h)
    # índice interno del bundle + nav + banner
    h = h.replace('<p class="migas"><a href="../ida-tutes.html">← Índice de los 69 tutes de IDA</a></p>',
                  nav(n, nums))
    h = h.replace('<main id="contenido">', "<main id=\"contenido\">" + nav(n, nums) + BANNER)
    # al final del main, otra barra de navegación
    h = h.replace("</main>", nav(n, nums) + "</main>")
    return h


def indice(nums):
    L = ["<style>\n" + CSS + "\n</style>", '<main id="contenido">',
         "<h1>Curso IDA · 69 tutes ilustrados (copia celular)</h1>",
         "<p>Copia offline para el teléfono. Tocá un tute para abrirlo; adentro tenés "
         "navegación anterior/siguiente.</p>"]
    for a, b, titulo, nota, lecciones in gm.IDA_GRUPOS:
        L.append(f"<h2>Tutes {a}–{b} · {titulo}</h2>")
        L.append("<ul>")
        for n in range(a, b + 1):
            tema = gm.IDA_TUTES.get(n, ("", "", ""))[0]
            if n in nums:
                L.append(f'<li><a href="{n}.html"><strong>{n}</strong> · {tema}</a></li>')
        L.append("</ul>")
    L.append("</main>")
    return ("<!doctype html><html lang='es'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>Curso IDA · copia celular</title></head><body>" + "\n".join(L) + "</body></html>")


def main():
    os.makedirs(OUT, exist_ok=True)
    nums = sorted(int(re.match(r"(\d+)\.html", f).group(1))
                  for f in os.listdir(IDAT) if re.match(r"\d+\.html$", f))
    for n in nums:
        open(os.path.join(OUT, f"{n}.html"), "w", encoding="utf-8").write(una_copia(n, nums))
        print(f"  tute {n}")
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(indice(nums))
    # ZIP
    zip_path = os.path.join(SCRATCH, "CLS_tutes_ilustrados_celular.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(OUT, "index.html"), "index.html")
        for n in nums:
            z.write(os.path.join(OUT, f"{n}.html"), f"{n}.html")
    mb_html = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)) / 1e6
    print(f"\n{len(nums)} copias ({mb_html:.0f} MB sin comprimir) -> ZIP {os.path.getsize(zip_path)/1e6:.0f} MB")
    print("ZIP:", zip_path)


if __name__ == "__main__":
    main()
