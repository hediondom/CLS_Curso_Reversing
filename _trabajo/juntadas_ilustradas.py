# -*- coding: utf-8 -*-
"""Arma "juntadas ilustradas": por cada sesión larga de reversing grabada en Telegram,
muestrea un fotograma cada ~N segundos y lo pega con la transcripción de ese tramo.

NO es un tutorial redactado: es una sesión EN VIVO transcripta AUTOMÁTICAMENTE (voz sin
atribuir, con muletillas) + fotogramas del propio video. Sirve para escanear una sesión
de varias horas de un vistazo y saltar al minuto que interesa en el video original.

Salida: CLS_Guia/juntadas/<slug>.html  (+ img/<slug>/*.jpg) y CLS_Guia/juntadas/index.html
Uso:  py -3 juntadas_ilustradas.py [--top 5] [--cadencia 180] [--solo <slug>]
"""
import csv
import glob
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
GUIA = os.path.join(RAIZ, "CLS_Guia")
DEST = os.path.join(GUIA, "juntadas")
IMGDIR = os.path.join(DEST, "img")
TDIR = os.path.join(RAIZ, "CLS_resultados_intermedios", "transcripciones", "telegram_videos")
FFBIN = r"C:\Users\agust\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
# ffmpeg/ffprobe: los del PATH; si no están, la instalación de winget con la que se generaron las juntadas.
FFMPEG = shutil.which("ffmpeg") or os.path.join(FFBIN, "ffmpeg.exe")
FFPROBE = shutil.which("ffprobe") or os.path.join(FFBIN, "ffprobe.exe")

MAX_FRAMES = 80
CAD_MIN = 150  # segundos mínimos entre fotogramas


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s.strip().lower()).strip("-")
    return s[:50] or "sesion"


def srt_sec(t):
    h, m, rest = t.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_srt(path):
    out = []
    bloques = re.split(r"\n\s*\n", open(path, encoding="utf-8", errors="ignore").read())
    for b in bloques:
        m = re.search(r"(\d\d:\d\d:\d\d,\d+)\s*-->\s*(\d\d:\d\d:\d\d,\d+)(.*)", b, re.S)
        if m:
            texto = " ".join(l.strip() for l in m.group(3).splitlines() if l.strip())
            if texto:
                out.append((srt_sec(m.group(1)), srt_sec(m.group(2)), texto))
    return out


def duracion(mp4):
    try:
        r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", mp4], capture_output=True, text=True)
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def frame(mp4, t, destino):
    subprocess.run([FFMPEG, "-y", "-ss", str(int(t)), "-i", mp4, "-frames:v", "1",
                    "-vf", "scale=960:-1", "-q:v", "4", destino],
                   capture_output=True)
    return os.path.exists(destino)


def hhmm(seg):
    seg = int(seg)
    h, m, s = seg // 3600, (seg % 3600) // 60, seg % 60
    return (f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}")


def hallar_mp4(label):
    """mp4 cuyo nombre es exactamente la etiqueta (tolerando espacios finales)."""
    lab = label.strip().lower()
    for p in glob.glob(os.path.join(RAIZ, "telegram", "**", "*.mp4"), recursive=True):
        if os.path.splitext(os.path.basename(p))[0].strip().lower() == lab:
            return p
    return None


def rel_desde_pagina(target):
    rel = os.path.relpath(target, DEST).replace("\\", "/")
    from urllib.parse import quote
    return "/".join(quote(p) for p in rel.split("/"))


def una(base, label, cad_min=CAD_MIN):
    srt = os.path.join(TDIR, base + ".srt")
    if not os.path.exists(srt):
        return None
    mp4 = hallar_mp4(label)
    if not mp4:
        print(f"   (sin mp4 para «{label}»)")
        return None
    subs = parse_srt(srt)
    dur = duracion(mp4) or (subs[-1][1] if subs else 0)
    cad = max(cad_min, dur / MAX_FRAMES)
    slug = slugify(label)
    outimg = os.path.join(IMGDIR, slug)
    os.makedirs(outimg, exist_ok=True)

    H = []
    H.append('<p class="migas"><a href="index.html">← Juntadas ilustradas</a> · '
             '<a href="../telegram.html">Transcripciones de Telegram</a></p>')
    H.append(f"<h1>{build.esc(label.strip())}</h1>")
    palabras = sum(len(s[2].split()) for s in subs)
    H.append(f'<p class="meta-tute"><strong>🎞 sesión de {hhmm(dur)}</strong> · {palabras:,} palabras transcriptas · '
             f"un fotograma cada ~{int(cad//60)} min</p>".replace(",", "."))
    H.append('<aside class="callout peligro"><p class="callout-titulo">Qué es y qué no</p>'
             "<p>Es una <strong>sesión de práctica EN VIVO</strong> grabada en los grupos, con la "
             "<strong>transcripción automática</strong> (puede tener errores) y <strong>fotogramas</strong> del propio video. "
             "<strong>No es un tutorial redactado ni material verificado</strong>, y la voz no está atribuida con certeza. "
             "Sirve para escanear la sesión y saltar al minuto que te interese en el video.</p></aside>")
    mp4rel = rel_desde_pagina(mp4)
    H.append(f'<p>▶ <a class="fuente" href="{mp4rel}">Reproducir el video original</a> '
             f'({hhmm(dur)}) · <a class="fuente" href="{rel_desde_pagina(srt)}">transcripción .srt</a></p>')
    H.append("<hr>")

    # Muestreo
    t = 0.0
    k = 0
    i = 0
    while t < dur and k < MAX_FRAMES:
        k += 1
        fn = f"{k}.jpg"
        ok = frame(mp4, t, os.path.join(outimg, fn))
        # texto del tramo [t, t+cad)
        trozo = []
        while i < len(subs) and subs[i][0] < t + cad:
            if subs[i][0] >= t - 1:
                trozo.append(subs[i][2])
            i += 1
        H.append('<section class="tramo">')
        if ok:
            H.append(f'<figure><figcaption>{hhmm(t)}</figcaption>'
                     f'<img loading="lazy" src="img/{slug}/{fn}" alt="Fotograma a {hhmm(t)}"></figure>')
        if trozo:
            H.append(f"<p>{build.esc(' '.join(trozo))}</p>")
        H.append("</section>")
        t += cad

    destino = os.path.join(DEST, slug + ".html")
    build.construir(destino, f"{label.strip()} — Juntada ilustrada (CLS)",
                    f"Sesión de práctica de reversing «{label.strip()}»: fotogramas + transcripción automática.",
                    "\n".join(H))
    return slug, label.strip(), dur, palabras, k


def gen_index(hechas):
    H = ['<h1>Juntadas ilustradas</h1>',
         '<aside class="callout aviso"><p class="callout-titulo">Material automático, no verificado</p>'
         "<p>Sesiones de práctica EN VIVO de los grupos, con transcripción automática y fotogramas del video. "
         "No son tutoriales redactados. Se eligieron las más largas marcadas como reversing/técnico en el "
         '<a href="../telegram.html">tamizado de Telegram</a>.</p></aside>',
         "<ul>"]
    for slug, label, dur, pal, k in hechas:
        H.append(f'<li><a href="{slug}.html"><strong>{build.esc(label)}</strong></a> — '
                 f"{hhmm(dur)}, {k} fotogramas, {pal:,} palabras</li>".replace(",", "."))
    H.append("</ul>")
    build.construir(os.path.join(DEST, "index.html"), "Juntadas ilustradas (CLS)",
                    "Sesiones de práctica de reversing de Telegram con fotogramas + transcripción.",
                    "\n".join(H))


def main():
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 5
    cad = int(sys.argv[sys.argv.index("--cadencia") + 1]) if "--cadencia" in sys.argv else CAD_MIN
    solo = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None
    os.makedirs(IMGDIR, exist_ok=True)

    rows = list(csv.DictReader(open(os.path.join(GUIA, "telegram_indice.csv"), encoding="utf-8-sig"), delimiter=";"))
    rev = [r for r in rows if r["tipo"] == "video" and r["clase"].startswith("reversing")]
    rev.sort(key=lambda r: -int(r["palabras"]))
    sel = rev[:top]

    hechas = []
    for r in sel:
        base = r["archivo"]
        label = base.split("_", 2)[-1]
        if solo and slugify(label) != solo:
            continue
        print(f"-> {label.strip()[:50]} ({r['palabras']} pal)")
        res = una(base, label, cad)
        if res:
            hechas.append(res)
            print(f"   OK {res[4]} fotogramas")
    if hechas:
        gen_index(hechas)
    tam = sum(os.path.getsize(os.path.join(root, x)) for root, _, fs in os.walk(DEST) for x in fs)
    print(f"\n{len(hechas)} juntadas -> {DEST}  ({tam/1e6:.0f} MB)")


if __name__ == "__main__":
    main()
