# -*- coding: utf-8 -*-
"""Une los audios (notas de voz) técnicos de Telegram en hilos legibles por sesión.

Los audios vienen partidos (audio_10, audio_15… de un mismo día). Esto los agrupa por
FECHA de envío y arma una sola página con, por cada audio: la hora, un reproductor
inline del .ogg original y su transcripción. Así dejan de ser fragmentos sueltos.

NO es un tutorial: es transcripción AUTOMÁTICA de notas de voz, voz sin atribuir.
Salida: CLS_Guia/audios/index.html
Uso:  py -3 audios_hilos.py
"""
import csv
import glob
import os
import re
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
GUIA = os.path.join(RAIZ, "CLS_Guia")
DEST = os.path.join(GUIA, "audios")


def ogg_index():
    idx = {}
    for p in glob.glob(os.path.join(RAIZ, "telegram", "**", "*.ogg"), recursive=True):
        idx.setdefault(os.path.splitext(os.path.basename(p))[0], p)
    return idx


def rel_desde_dest(target):
    rel = os.path.relpath(target, DEST).replace("\\", "/")
    return "/".join(quote(p) for p in rel.split("/"))


def hora(base):
    m = re.search(r"@\d{2}-\d{2}-\d{4}_(\d{2})-(\d{2})-(\d{2})", base)
    return f"{m.group(1)}:{m.group(2)}" if m else ""


def main():
    os.makedirs(DEST, exist_ok=True)
    rows = list(csv.DictReader(open(os.path.join(GUIA, "telegram_indice.csv"), encoding="utf-8-sig"), delimiter=";"))
    au = [r for r in rows if r["tipo"] == "audio" and r["clase"].startswith("reversing")]
    oggs = ogg_index()

    # agrupar por fecha (YYYY-MM-DD al inicio del nombre)
    por_fecha = {}
    for r in au:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", r["archivo"])
        fecha = m.group(1) if m else "sin-fecha"
        por_fecha.setdefault(fecha, []).append(r)

    total_pal = sum(int(r["palabras"]) for r in au)
    H = ["<h1>Audios técnicos por sesión</h1>",
         ('<p class="meta-tute"><strong>🎙 {n} notas de voz</strong> agrupadas en {d} sesiones · '
          "~{p:,} palabras transcriptas</p>").format(n=len(au), d=len(por_fecha), p=total_pal).replace(",", "."),
         '<aside class="callout peligro"><p class="callout-titulo">Qué es y qué no</p>'
         "<p>Son <strong>notas de voz</strong> de los grupos con <strong>transcripción automática</strong> (puede errar) "
         "y la <strong>voz no está atribuida</strong> con certeza. No es un tutorial ni material verificado. "
         "Se agrupan por fecha de envío para poder seguir el hilo; podés <strong>escuchar el original</strong> en cada uno. "
         "Son solo los audios marcados como reversing/técnico en el "
         '<a href="../telegram.html">tamizado de Telegram</a>.</p></aside>',
         '<p class="migas"><a href="../telegram.html">← Transcripciones de Telegram</a></p>',
         "<hr>"]

    con_audio = 0
    for fecha in sorted(por_fecha):
        items = sorted(por_fecha[fecha], key=lambda r: r["archivo"])
        H.append(f'<h2>{fecha} · {len(items)} audio(s)</h2>')
        for r in items:
            base = r["archivo"]
            clave = base.split("_", 2)[-1]  # p. ej. audio_10@... o TodoSeVale
            etiqueta = hora(base) or (clave if not clave.startswith("audio_") else "")
            ogg = oggs.get(clave)
            try:
                txt = open(os.path.join(RAIZ, r["ruta"]), encoding="utf-8", errors="replace").read().strip()
            except OSError:
                txt = ""
            txt = re.sub(r"\s+", " ", txt)
            H.append('<section class="tramo">')
            cab = f"🎙 {etiqueta}" if etiqueta else "🎙 nota de voz"
            H.append(f'<p class="meta-tute">{build.esc(cab)} · {int(r["palabras"])} palabras</p>')
            if ogg:
                con_audio += 1
                H.append(f'<audio controls preload="none" src="{rel_desde_dest(ogg)}"></audio>')
            if txt:
                H.append(f"<p>{build.esc(txt)}</p>")
            H.append("</section>")

    build.construir(os.path.join(DEST, "index.html"), "Audios técnicos por sesión (CLS)",
                    "Notas de voz técnicas de Telegram agrupadas por sesión, con reproductor y transcripción automática.",
                    "\n".join(H))
    print(f"{len(au)} audios en {len(por_fecha)} sesiones, {con_audio} con .ogg enlazado -> {DEST}\\index.html")


if __name__ == "__main__":
    main()
