# -*- coding: utf-8 -*-
"""Arma una carpeta autocontenida: el libro-guía + SOLO los materiales que las citas referencian.

Recorre todos los .html de CLS_Guia, junta cada archivo local que la guía enlaza
(videos, transcripciones, documentos, CSV...) y copia el curso + esos archivos a una
carpeta nueva, manteniendo la estructura relativa para que todas las citas abran.

No incluye el material NO citado del proyecto (clones de GitHub, MEGA, etc.).

Uso:
    py -3 armar_curso_portable.py --dry    # solo informa qué entra y cuánto pesa
    py -3 armar_curso_portable.py          # arma la carpeta CLS_curso_portable/
"""
import os
import re
import shutil
import sys
import urllib.parse

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
GUIA = os.path.join(RAIZ, "CLS_Guia")
DESTINO = os.path.join(RAIZ, "CLS_curso_portable")

EXCLUIR_EN_GUIA = {"_review_tmp", "lecciones"}
EXCLUIR_HTML_DIRS = EXCLUIR_EN_GUIA | {"_trabajo"}
EXCLUIR_ARCHIVOS_EN_GUIA = {
    "EDICION_4_PLAN.md", "EDICION_4_QA.md", "PROMPT_MAESTRO.md",
    "edicion-4-plan.html", "analisis-temas.html", "temario.md",
}
EXCLUIR_PREFIJO = ("_backup_",)
HREF = re.compile(r'(?:href|src)="([^"#][^"]*)"')


def htmls():
    for root, dirs, files in os.walk(GUIA):
        dirs[:] = [d for d in dirs if d not in EXCLUIR_HTML_DIRS and not d.startswith(EXCLUIR_PREFIJO)]
        for f in files:
            if f.endswith(".html"):
                yield os.path.join(root, f)


def citas_externas():
    """Archivos citados fuera de CLS_Guia; expande también enlaces a carpetas."""
    archivos, contenedores = set(), set()
    for h in htmls():
        with open(h, encoding="utf-8") as fh:
            txt = fh.read()
        for raw in HREF.findall(txt):
            if raw.startswith(("http://", "https://", "mailto:", "data:", "javascript:")):
                continue
            ruta = urllib.parse.unquote(raw.split("#")[0].split("?")[0])
            if not ruta:
                continue
            full = os.path.normpath(os.path.join(os.path.dirname(h), ruta))
            try:
                rel = os.path.relpath(full, RAIZ)
            except ValueError:
                continue
            if rel.startswith("..") or os.path.isabs(rel):
                continue  # fuera del proyecto
            top = rel.split(os.sep)[0]
            if top == "CLS_Guia":
                continue  # interno a la guía (ya se copia con el curso)
            if os.path.isfile(full):
                archivos.add(rel)
            elif os.path.isdir(full):
                contenedores.add(rel)
                # La guía enlaza carpetas completas desde algunas fichas. Incluir su
                # contenido conserva el destino navegable en la copia compartible.
                for base, dirs, files in os.walk(full):
                    for name in files:
                        path = os.path.join(base, name)
                        archivos.add(os.path.relpath(path, RAIZ))
            # si no existe, se ignora (cita a algo ausente)
    # videos.html menciona esta colección por ruta local, no como un enlace HTML.
    # Incluirla para que también viaje con la copia para compartir.
    swf_root = os.path.join(RAIZ, "CLS_videos_extraidos", "Python ISO video tutes", "Videotutoriales")
    if os.path.isdir(swf_root):
        contenedores.add(os.path.relpath(swf_root, RAIZ))
        for base, dirs, files in os.walk(swf_root):
            for name in files:
                archivos.add(os.path.relpath(os.path.join(base, name), RAIZ))
    return archivos, contenedores


def humano(b):
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"


def tam(rel):
    try:
        return os.path.getsize(os.path.join(RAIZ, rel))
    except OSError:
        return 0


def _ignore_guia(dir_, names):
    # Dentro de _trabajo solo se conservan las carpetas 'extraido*' (textos extraídos que la guía cita).
    if os.path.basename(dir_) == "_trabajo":
        return [n for n in names if not n.startswith("extraido")]
    # En la raíz de CLS_Guia, descartar históricos y artefactos editoriales obsoletos.
    if os.path.abspath(dir_) == os.path.abspath(GUIA):
        return [n for n in names if n in EXCLUIR_EN_GUIA or n in EXCLUIR_ARCHIVOS_EN_GUIA or n.startswith(EXCLUIR_PREFIJO)]
    return [n for n in names if n.startswith(EXCLUIR_PREFIJO)]


def copiar_guia():
    dst = os.path.join(DESTINO, "CLS_Guia")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(GUIA, dst, ignore=_ignore_guia)


def corregir_enlaces_a_recurso_excluido():
    """El RAR de Themida no existe en el corpus; no dejar enlaces rotos al distribuir."""
    for rel in (os.path.join("CLS_Guia", "fichas", "themida.html"),
                os.path.join("CLS_Guia", "guia", "05-fuera-de-alcance.html")):
        path = os.path.join(DESTINO, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        text = re.sub(r'<a class="fuente" href="[^"]*Themida[^"]*">([^<]*)</a>',
                      r'\1 [archivo excluido; no incluido en esta copia]', text)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)


def main():
    global DESTINO
    if "--destino" in sys.argv:
        i = sys.argv.index("--destino")
        if i + 1 >= len(sys.argv):
            print("Falta la ruta después de --destino")
            return
        DESTINO = os.path.abspath(sys.argv[i + 1])
    dry = "--dry" in sys.argv

    if "--solo-guia" in sys.argv:
        if not os.path.isdir(DESTINO):
            print("No existe", DESTINO, "- corré sin --solo-guia para armarla entera.")
            return
        print("Refrescando solo el libro-guía en", DESTINO, "...")
        copiar_guia()
        print("  LISTO (los materiales de 14 GB no se tocaron).")
        return

    archivos, contenedores = citas_externas()

    # Resumen por carpeta de primer nivel.
    por_top = {}
    for rel in archivos:
        top = rel.split(os.sep)[0]
        por_top.setdefault(top, [0, 0])
        por_top[top][0] += 1
        por_top[top][1] += tam(rel)
    total_b = sum(v[1] for v in por_top.values())

    print(f"Archivos citados fuera de CLS_Guia: {len(archivos)} ({humano(total_b)})")
    for top in sorted(por_top):
        n, b = por_top[top]
        print(f"  {top}: {n} archivos, {humano(b)}")
    if contenedores:
        print(f"Carpetas completas enlazadas (contenido incluido): {len(contenedores)}")
        for c in sorted(contenedores)[:12]:
            print(f"  - {c}")

    guia_b = 0
    for root, dirs, files in os.walk(GUIA):
        dirs[:] = [d for d in dirs if d not in EXCLUIR_HTML_DIRS and not d.startswith(EXCLUIR_PREFIJO)]
        guia_b += sum(os.path.getsize(os.path.join(root, f)) for f in files)
    print(f"Libro-guía (CLS_Guia, sin _trabajo/_backup): {humano(guia_b)}")
    print(f"TOTAL de la carpeta portable: {humano(guia_b + total_b)}")

    if dry:
        print("\n(Modo informe. Para armar la carpeta: py -3 armar_curso_portable.py)")
        return

    # Copiar.
    if os.path.exists(DESTINO):
        print(f"\nOjo: {DESTINO} ya existe. Borralo o renombralo antes de rearmar.")
        return
    print(f"\nArmando {DESTINO} ...")
    # 1) el libro-guía (conserva _trabajo/extraido; descarta el resto de _trabajo y los backups)
    copiar_guia()
    corregir_enlaces_a_recurso_excluido()
    print("  CLS_Guia copiado")
    # 2) los materiales citados
    n = 0
    for rel in sorted(archivos):
        src = os.path.join(RAIZ, rel)
        dst = os.path.join(DESTINO, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        n += 1
        if n % 20 == 0:
            print(f"  ... {n}/{len(archivos)} materiales")
    print(f"  {n} materiales citados copiados")
    # 3) nota de portabilidad
    with open(os.path.join(DESTINO, "LEEME_PORTABLE.txt"), "w", encoding="utf-8") as f:
        f.write(
            "Copia local autocontenida del curso, preparada para compartir con personas autorizadas.\n\n"
            "Abrí CLS_Guia/00_EMPEZAR_AQUI.html.\n"
            "La guía y los materiales seleccionados usan rutas relativas. Se incluyeron los archivos\n"
            "enlazados individualmente, las carpetas enlazadas desde las fichas y la colección SWF\n"
            "de Python mencionada en el índice de videos.\n"
            "Conservá juntas las subcarpetas para que las referencias sigan abriendo.\n"
            "Incluye material de Telegram y de terceros: antes de redistribuirlo públicamente,\n"
            "revisá derechos y privacidad. Los enlaces al RAR de Themida se indican como excluidos.\n"
        )
    print("  LISTO. Abrir: CLS_curso_portable/CLS_Guia/00_EMPEZAR_AQUI.html")


if __name__ == "__main__":
    main()
