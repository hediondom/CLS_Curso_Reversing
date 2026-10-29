# -*- coding: utf-8 -*-
"""Genera una edicion imprimible en un solo HTML y la convierte a PDF con Chrome."""
import io
import os
import re
import subprocess
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

GUIA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ = os.path.dirname(GUIA)
SALIDA_HTML = os.path.join(GUIA, "_trabajo", "print", "CLS_Curso_Reversing_imprimible.html")
SALIDA_PDF = os.path.join(GUIA, "CLS_Curso_Reversing.pdf")
DRAFT_PDF = os.path.join(GUIA, "_trabajo", "print", "CLS_Curso_Reversing_borrador.pdf")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TOC_ANCHORS = []

LECCIONES = [
    ("guia/00-laboratorio.html", "0.1 Laboratorio"),
    ("guia/01-numeros.html", "1.1 Números y hexadecimal"),
    ("guia/01-memoria.html", "1.2 Memoria y stack"),
    ("guia/01-procesos.html", "1.3 Procesos e hilos"),
    ("guia/01-pe.html", "1.4 Formato PE"),
    ("guia/01-c-python.html", "1.5 C y Python"),
    ("guia/02-registros.html", "2.1 Registros y flags"),
    ("guia/02-instrucciones.html", "2.2 Instrucciones"),
    ("guia/02-flotante.html", "2.3 Punto flotante y SSE"),
    ("guia/02-flujo.html", "2.4 Flujo"),
    ("guia/02-llamadas.html", "2.5 Llamadas"),
    ("guia/02-debugger.html", "2.6 Debugger"),
    ("guia/02-ida.html", "2.7 IDA"),
    ("guia/02-optimizaciones.html", "2.8 Optimizaciones"),
    ("guia/02-herramientas.html", "2.9 Herramientas"),
    ("guia/02-ofuscacion.html", "2.10 Ofuscación nativa"),
    ("guia/02-tls.html", "2.11 TLS callbacks"),
    ("guia/02-mfc.html", "2.12 MFC"),
    ("guia/02-huella-compilador.html", "2.13 Huella de compilador"),
    ("guia/02-pe-fino.html", "2.14 PE fino"),
    ("guia/02-anti-analisis.html", "2.15 Taxonomía anti-análisis"),
    ("guia/02-ghidra.html", "2.16 Ghidra/Cutter"),
    ("guia/02-packers.html", "2.17 Packers didácticos"),
    ("guia/02-cpp-profundo.html", "2.18 C++ profundo"),
    ("guia/02-windbg-heap.html", "2.19 WinDbg, TTD y heap"),
    ("guia/02-patch-diffing.html", "2.20 Patch diffing y CVE"),
    ("guia/02-scripting-debugger.html", "2.21 Scripting de debugger"),
    ("guia/02-opt-malware-dinamico.html", "2.22 (opt) Malware dinámico"),
    ("guia/02-opt-shellcode-c2.html", "2.23 (opt) Shellcode, red y C2"),
    ("guia/02-opt-fuzzing.html", "2.24 (opt) Fuzzing y simbólico"),
    ("guia/03-dotnet-runtime.html", "3.1 .NET runtime"),
    ("guia/03-dotnet-il.html", "3.2 Leer IL"),
    ("guia/04-metodo.html", "4.1 Método de análisis"),
    ("guia/04-formatos-protocolos.html", "4.5 Reconstruir formatos y protocolos"),
    ("guia/04-cripto.html", "4.2 Reconocer criptografía"),
    ("guia/04-informe.html", "4.3 Informe"),
    ("guia/04-dinamico-seguro.html", "4.4 Dinámico seguro"),
    ("guia/05-malware.html", "5.1 Malware"),
    ("guia/05-vulnerabilidades.html", "5.2 Vulnerabilidades"),
    ("guia/05-automatizacion.html", "5.3 Automatización"),
    ("guia/05-fuera-de-alcance.html", "5.4 Fuera de alcance"),
    ("guia/6-01-arquitectura-kernel.html", "6.1 Arquitectura del kernel"),
    ("guia/6-02-kmdf-ioctl.html", "6.2 KMDF e IOCTL inocuo"),
    ("guia/6-03-debug-kernel.html", "6.3 Debugging de kernel"),
    ("guia/6-04-revision-driver.html", "6.4 Revisión defensiva de drivers"),
    ("guia/6-05-minifilters.html", "6.5 Minifilters"),
    ("guia/6-06-mitigaciones.html", "6.6 Mitigaciones para drivers"),
]

ETAPAS = [
    ("guia/etapa-0.html", "Etapa 0 · Laboratorio"),
    ("guia/etapa-1.html", "Etapa 1 · Fundamentos"),
    ("guia/etapa-2.html", "Etapa 2 · Reversing"),
    ("guia/etapa-3.html", "Etapa 3 · .NET"),
    ("guia/etapa-4.html", "Etapa 4 · Práctica"),
    ("guia/etapa-5.html", "Etapa 5 · Ramas"),
    ("guia/etapa-6.html", "Etapa 6 · Rama optativa: Kernel y drivers"),
]

RAMA_2D = [
    ("2d.html", "2D · Windows internals (optativa)"),
    ("guia/2d-01-objetos.html", "2D.1 Objetos y tokens"),
    ("guia/2d-02-memoria-loader.html", "2D.2 Memoria y loader"),
    ("guia/2d-03-registro.html", "2D.3 Registro"),
    ("guia/2d-04-servicios.html", "2D.4 Servicios"),
    ("guia/2d-05-task-scheduler.html", "2D.5 Task Scheduler"),
    ("guia/2d-06-com-interfaces.html", "2D.6 COM interfaces"),
    ("guia/2d-07-com-activacion.html", "2D.7 COM activación"),
    ("guia/2d-08-dcom-rpc.html", "2D.8 DCOM y RPC"),
    ("guia/2d-09-wmi.html", "2D.9 WMI"),
    ("guia/2d-10-ipc.html", "2D.10 IPC"),
    ("guia/2d-11-excepciones.html", "2D.11 Excepciones"),
    ("guia/2d-12-etw.html", "2D.12 ETW"),
    ("guia/2d-13-integrador.html", "2D.13 Integrador"),
    ("2d-hyperv.html", "Extensión optativa Hyper-V"),
]

FICHAS = [
    "reversing-desde-cero", "ida-desde-cero", "masm32-cayetano", "ollydbg-cayetano",
    "python-iso", "reverse-engineering-ricardo", "teorias-numeradas", "ida-pro-docx",
    "inventario-limpio", "chat-unido", "transcripciones-telegram", "scenere-docs",
    "exploiting-contenedores", "malware-virus", "themida",
    "zips-anteriores", "exportacion-sesion", "plan-estudio-historico", "curso-reversing-2020",
]


def contenido(rel):
    with open(os.path.join(GUIA, rel.replace("/", os.sep)), encoding="utf-8") as f:
        h = f.read()
    m = re.search(r'<main id="contenido">(.*?)</main>', h, re.S)
    if not m:
        raise ValueError(rel)
    cuerpo = m.group(1)
    cuerpo = re.sub(r'<nav class="migas".*?</nav>', "", cuerpo, flags=re.S)
    cuerpo = re.sub(r'<div class="pager">.*?</div>', "", cuerpo, flags=re.S)
    # El callout "Volver" (navegación entre páginas) sobra en un PDF de un solo documento.
    cuerpo = re.sub(r'<aside class="callout[^"]*"><p class="callout-titulo">Volver</p>.*?</aside>', "", cuerpo, flags=re.S)
    # En papel no se puede desplegar: abrir todos los <details> para que las respuestas se vean.
    cuerpo = cuerpo.replace("<details", "<details open")
    return cuerpo


def ancla(rel):
    return "sec-" + re.sub(r"[^a-zA-Z0-9]+", "-", rel.replace(".html", "")).strip("-")


def limpiar_enlaces(html, mapa):
    def rep(m):
        clase = m.group(1) or ""
        href = m.group(2)
        texto = m.group(3)
        if href.startswith(("http://", "https://", "mailto:")):
            return f'<a href="{href}">{texto}</a>'   # enlace externo: clicable en el PDF
        if "fuente" in clase:
            return f'<span class="fuente">{texto}</span>'
        if href in mapa:
            return f'<a href="#{mapa[href]}">{texto}</a>'
        if href.startswith("#"):
            return f'<a href="{href}">{texto}</a>'
        return f"<span>{texto}</span>"

    return re.sub(
        r'<a(?:\s+class="([^"]*)")?\s+href="([^"]+)"[^>]*>(.*?)</a>',
        rep, html, flags=re.S,
    )


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto).strip().casefold()


def paginas_por_ancla(ruta_pdf, anclas):
    """Obtiene páginas 1-based desde los destinos HTML del PDF ya paginado."""
    from pypdf import PdfReader

    reader = PdfReader(ruta_pdf)
    destinos = reader.named_destinations
    resultado = {}
    for ancla_id in anclas:
        destino = destinos.get("/" + ancla_id) or destinos.get(ancla_id)
        if destino is None:
            raise ValueError(f"No se encontró el destino PDF #{ancla_id}")
        resultado[ancla_id] = reader.get_destination_page_number(destino) + 1

    # Chrome puede asignar el nombre `fuentes` a un destino interno distinto.
    # El encabezado real es una coincidencia exacta y se encuentra al final.
    if "fuentes" in resultado:
        for numero, pagina in enumerate(reader.pages, 1):
            lineas = [normalizar(x) for x in (pagina.extract_text() or "").splitlines()]
            if "fuentes y limites" in lineas:
                resultado["fuentes"] = numero
                break
    return resultado, len(reader.pages)


def etiquetas_paginas(anclas, paginas, total):
    etiquetas = {}
    for i, ancla_id in enumerate(anclas):
        inicio = paginas[ancla_id]
        fin = total
        for siguiente in anclas[i + 1:]:
            if paginas[siguiente] > inicio:
                fin = paginas[siguiente] - 1
                break
        cantidad = fin - inicio + 1
        rango = str(inicio) if inicio == fin else f"{inicio}-{fin}"
        unidad = "pág." if cantidad == 1 else "págs."
        etiquetas[ancla_id] = f"p. {rango} · {cantidad} {unidad}"
    return etiquetas


def reemplazar_etiquetas(html, etiquetas):
    def rep(m):
        ancla_id = m.group(1)
        texto = etiquetas.get(ancla_id, "páginas pendientes")
        return f'<span class="toc-pag" data-anchor="{ancla_id}">{texto}</span>'
    return re.sub(
        r'<span class="toc-pag" data-anchor="([^"]+)">.*?</span>',
        rep, html, flags=re.S,
    )


def renderizar_pdf(ruta_html, ruta_pdf):
    cmd = [
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
        "--user-data-dir=" + os.path.join(GUIA, "_trabajo", "chrome-perfil"),
        "--allow-file-access-from-files", "--virtual-time-budget=15000",
        "--no-pdf-header-footer", "--print-to-pdf-no-header",
        f"--print-to-pdf={ruta_pdf}",
        "file:///" + ruta_html.replace("\\", "/"),
    ]
    subprocess.run(cmd, check=True)


def agregar_numeros_visibles(ruta_pdf):
    """Superpone el número de página centrado en el margen inferior."""
    from pypdf import PdfReader, PdfWriter
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen import canvas

    reader = PdfReader(ruta_pdf)
    writer = PdfWriter()
    writer.append(reader)
    ruta_temporal = ruta_pdf + ".numerado"
    for numero, pagina in enumerate(writer.pages, 1):
        ancho = float(pagina.mediabox.width)
        alto = float(pagina.mediabox.height)
        buffer = io.BytesIO()
        lienzo = canvas.Canvas(buffer, pagesize=(ancho, alto))
        lienzo.setFillColor(HexColor("#666666"))
        lienzo.setFont("Helvetica", 8)
        lienzo.drawCentredString(ancho / 2, 15, str(numero))
        lienzo.save()
        buffer.seek(0)
        superposicion = PdfReader(buffer).pages[0]
        pagina.merge_page(superposicion)
        pagina.compress_content_streams()
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    with open(ruta_temporal, "wb") as archivo:
        writer.write(archivo)
    os.replace(ruta_temporal, ruta_pdf)


def main():
    TOC_ANCHORS.clear()
    page_labels = {}

    def ref(anchor_id):
        return f'<span class="toc-pag" data-anchor="{anchor_id}">{page_labels.get(anchor_id, "calculando")}</span>'

    def row(anchor_id, title):
        TOC_ANCHORS.append(anchor_id)
        return f'<li><a href="#{anchor_id}">{title}</a>{ref(anchor_id)}</li>'

    def heading(anchor_id, title):
        TOC_ANCHORS.append(anchor_id)
        return f'<div class="etapa"><a href="#{anchor_id}">{title}</a>{ref(anchor_id)}</div>'

    mapa = {}
    for rel, _ in LECCIONES + ETAPAS:
        mapa[rel] = ancla(rel)
    for rel, _ in RAMA_2D:
        mapa[rel] = ancla(rel)
    mapa["../2d.html"] = ancla("2d.html")
    mapa["../2d-hyperv.html"] = ancla("2d-hyperv.html")
    mapa["../guia/etapa-6.html"] = ancla("guia/etapa-6.html")
    for slug in FICHAS:
        mapa[f"fichas/{slug}.html"] = "ficha-" + slug
    mapa["fichas/index.html"] = "fichas"
    mapa["glosario.html"] = "glosario"
    mapa["preguntas_y_respuestas.html"] = "preguntas"
    mapa["00_EMPEZAR_AQUI.html"] = "portada"
    mapa["guia/index.html"] = "mapa-curso"
    mapa["videos.html"] = "videos"

    css = open(os.path.join(GUIA, "guia", "estilo.css"), encoding="utf-8").read()
    css_print = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { background: #fff; font-size: 10.5pt; line-height: 1.5; }
main { max-width: none; padding: 0; }
.print-sec { break-before: page; }
.print-sec:first-of-type { break-before: auto; }
.print-sec h1 { font-size: 20pt; margin-top: 0; }
.print-sec h2 { font-size: 13pt; margin-top: 1.4em; }
.print-sec h3 { font-size: 11.5pt; }
.print-sec pre { font-size: 8.5pt; white-space: pre-wrap; break-inside: avoid; page-break-inside: avoid; }
.print-sec table { font-size: 8.8pt; }
.print-sec .tabla { break-inside: avoid; page-break-inside: avoid; }
.print-sec tr { break-inside: avoid; page-break-inside: avoid; }
.print-sec .callout, .print-sec .gate, .print-sec details { break-inside: avoid; page-break-inside: avoid; }
.print-sec h2, .print-sec h3, .print-sec h4 { break-after: avoid; page-break-after: avoid; }
.print-sec a { color: #000; text-decoration: none; }
.portada-pdf { text-align: left; padding-top: 30mm; }
.portada-pdf .kicker { color: #0b5f6b; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: 9pt; }
.portada-pdf h1 { font-size: 34pt; line-height: 1.05; margin: .2em 0 .3em; }
.portada-pdf .sub { font-size: 13pt; color: #333; max-width: 150mm; }
.portada-pdf .aviso { border-left: 4px solid #8a1c1c; background: #fbe7e7; padding: 8pt 10pt; margin: 18pt 0; font-size: 9.5pt; }
.toc { margin-top: 16pt; columns: 2; column-gap: 12mm; font-size: 10pt; }
.toc h2 { column-span: all; border-bottom: 1px solid #999; }
.toc ol { margin: 0; padding-left: 16pt; }
.toc li { display: flex; align-items: baseline; gap: 5pt; margin: 2pt 0; break-inside: avoid; }
.toc li a { flex: 1; min-width: 0; }
.toc-pag { white-space: nowrap; font-size: 8pt; color: #444; }
.toc .etapa { display: flex; justify-content: space-between; gap: 5pt; font-weight: 700; margin-top: 6pt; color: #0b5f6b; break-inside: avoid; }
.toc .etapa a { color: inherit; text-decoration: none; }
details.qa { padding: 4pt 6pt; margin: 4pt 0; }
details.qa summary { font-size: 10pt; }
"""

    partes = [f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>CLS · Curso de reversing</title><style>{css}\n{css_print}</style></head><body><main>']

    # Portada
    partes.append("""
<section class="print-sec portada-pdf" id="portada">
<p class="kicker">Proyecto CLS · Edición 5</p>
<h1>Curso de reversing</h1>
<p class="sub">De los fundamentos al análisis guiado. Un curso en español, progresivo y verificable, construido a partir del material del proyecto CLS.</p>
<p class="sub"><strong>Actualizado 28 de octubre de 2026</strong> · Ruta base: Etapas 0–4 · Optativas: Etapas 5–6 y rama 2D de la Etapa 2</p>
<p class="sub">Incluye el recorrido base, bloques optativos 2C/2D y la rama de kernel/drivers; el conteo editorial incluye contenidos optativos y fichas fuera del recorrido obligatorio.</p>
<p class="sub"><em>Edición de estudio — teoría. Para practicar (abrir los videos y los tutes de IDA, el banco de prácticas, las transcripciones, los audios y el buscador) usá la versión <strong>HTML</strong> del curso, entrando por <code>00_EMPEZAR_AQUI.html</code>; este PDF explica la teoría para leer sin pantalla.</em></p>
<div class="aviso"><strong>Material educativo y defensivo.</strong> Las prácticas usan programas propios, software abierto o crackmes diseñados para aprender. No se enseña a eludir licencias, DRM ni controles de acceso. No se ejecutaron binarios del corpus ni se extrajeron comprimidos.</div>
<p class="sub">Esta edición es una cobertura parcial y declarada del corpus. Lo que falta está en <em>Fuentes y límites</em>, al final del documento.</p>
</section>
""")

    # TOC
    toc = ['<section class="print-sec" id="toc"><h1>Contenido</h1><div class="toc">']
    toc.append('<div class="etapa">Apertura</div><ol>')
    toc.append(row("portada-texto", "Cómo estudiar y qué se revisó"))
    toc.append(row("mapa-curso", "Mapa del curso"))
    toc.append('</ol>')
    # Etapas y lecciones en orden
    orden = [
        ("Etapa 0", ["guia/00-laboratorio.html"]),
        ("Etapa 1", ["guia/01-numeros.html", "guia/01-memoria.html", "guia/01-procesos.html", "guia/01-pe.html", "guia/01-c-python.html"]),
        ("Etapa 2", ["guia/02-registros.html", "guia/02-instrucciones.html", "guia/02-flotante.html", "guia/02-flujo.html", "guia/02-llamadas.html", "guia/02-debugger.html", "guia/02-ida.html", "guia/02-optimizaciones.html", "guia/02-herramientas.html", "guia/02-ofuscacion.html", "guia/02-tls.html", "guia/02-mfc.html", "guia/02-huella-compilador.html", "guia/02-pe-fino.html", "guia/02-anti-analisis.html", "guia/02-ghidra.html", "guia/02-packers.html", "guia/02-cpp-profundo.html", "guia/02-windbg-heap.html", "guia/02-patch-diffing.html", "guia/02-scripting-debugger.html", "guia/02-opt-malware-dinamico.html", "guia/02-opt-shellcode-c2.html", "guia/02-opt-fuzzing.html"]),
        ("Etapa 3", ["guia/03-dotnet-runtime.html", "guia/03-dotnet-il.html"]),
        ("Etapa 4", ["guia/04-metodo.html", "guia/04-formatos-protocolos.html", "guia/04-cripto.html", "guia/04-informe.html", "guia/04-dinamico-seguro.html"]),
        ("Etapa 5", ["guia/05-malware.html", "guia/05-vulnerabilidades.html", "guia/05-automatizacion.html", "guia/05-fuera-de-alcance.html"]),
        ("Etapa 6 · Rama optativa", ["guia/6-01-arquitectura-kernel.html", "guia/6-02-kmdf-ioctl.html", "guia/6-03-debug-kernel.html", "guia/6-04-revision-driver.html", "guia/6-05-minifilters.html", "guia/6-06-mitigaciones.html"]),
    ]
    nombres = dict(LECCIONES)
    for etapa, lecs in orden:
        numero = re.search(r"\d+", etapa).group(0)
        toc.append(heading(mapa[f"guia/etapa-{numero}.html"], etapa) + '<ol>')
        for rel in lecs:
            toc.append(row(mapa[rel], nombres[rel]))
        toc.append('</ol>')
    toc.append(heading(mapa["2d.html"], "2D · Windows internals (optativa)") + '<ol>')
    for rel, titulo in RAMA_2D:
        if rel == "2d.html":
            continue
        toc.append(row(mapa[rel], titulo))
    toc.append('</ol>')
    toc.append('<div class="etapa">Material de apoyo</div><ol>')
    toc.append(row("glosario", "Glosario"))
    toc.append(row("preguntas", "Preguntas y respuestas"))
    toc.append(row("fuentes", "Fuentes y límites"))
    toc.append('</ol></div></section>')
    partes.append("".join(toc))

    # Apertura: portada de texto + mapa
    for rel, anchor in [("00_EMPEZAR_AQUI.html", "portada-texto"), ("guia/index.html", "mapa-curso")]:
        h = limpiar_enlaces(contenido(rel), mapa)
        partes.append(f'<section class="print-sec" id="{anchor}">{h}</section>')

    # Etapas y lecciones
    for rel, _ in ETAPAS:
        h = limpiar_enlaces(contenido(rel), mapa)
        partes.append(f'<section class="print-sec" id="{mapa[rel]}">{h}</section>')
        etapa_num = rel.split("-")[-1].replace(".html", "")
        pref = f"guia/{etapa_num}-" if etapa_num == "6" else f"guia/0{etapa_num}-"
        lecs = [x for x in LECCIONES if x[0].startswith(pref)]
        for lrel, _ in lecs:
            lh = limpiar_enlaces(contenido(lrel), mapa)
            partes.append(f'<section class="print-sec" id="{mapa[lrel]}">{lh}</section>')

    # Profundización optativa 2D y extensión Hyper-V: van al final para mantener intacto el recorrido base.
    for rel, _titulo in RAMA_2D:
        h = limpiar_enlaces(contenido(rel), mapa)
        partes.append(f'<section class="print-sec" id="{mapa[rel]}">{h}</section>')

    # Glosario y preguntas
    for rel, anchor in [("glosario.html", "glosario"), ("preguntas_y_respuestas.html", "preguntas")]:
        h = limpiar_enlaces(contenido(rel), mapa)
        if anchor == "preguntas":
            h = h.replace('<details class="qa">', '<details class="qa" open>')
        partes.append(f'<section class="print-sec" id="{anchor}">{h}</section>')

    # (El índice de videotutoriales y las fichas de recursos NO van en el PDF de teoría:
    #  son material de apoyo para usar con la computadora; viven en la versión HTML.)

    # Fuentes
    with open(os.path.join(GUIA, "FUENTES_Y_LIMITES.md"), encoding="utf-8") as f:
        fuentes_md = f.read()
    # Pasar por limpiar_enlaces: en el PDF, los enlaces relativos a archivos (CSV, .md)
    # no deben quedar como file:// rotos, sino como texto plano.
    fuentes_html = limpiar_enlaces(build.md(fuentes_md), mapa)
    partes.append(f'<section class="print-sec" id="fuentes"><h1>Fuentes y límites</h1>{fuentes_html}</section>')

    partes.append("</main></body></html>")
    os.makedirs(os.path.dirname(SALIDA_HTML), exist_ok=True)
    html_documento = "\n".join(partes)
    etiquetas = {}
    paginas = {}
    total = 0
    print("Generando PDF e iterando el índice paginado...")
    for intento in range(5):
        with open(SALIDA_HTML, "w", encoding="utf-8") as f:
            f.write(html_documento)
        renderizar_pdf(SALIDA_HTML, DRAFT_PDF)
        paginas, total = paginas_por_ancla(DRAFT_PDF, TOC_ANCHORS)
        nuevas = etiquetas_paginas(TOC_ANCHORS, paginas, total)
        if intento > 0 and nuevas == etiquetas:
            break
        etiquetas = nuevas
        html_documento = reemplazar_etiquetas(html_documento, etiquetas)
    else:
        raise RuntimeError("El índice paginado no se estabilizó tras cinco generaciones")

    agregar_marcadores(DRAFT_PDF, paginas)
    agregar_numeros_visibles(DRAFT_PDF)
    os.replace(DRAFT_PDF, SALIDA_PDF)
    print("PDF:", SALIDA_PDF, os.path.getsize(SALIDA_PDF), "bytes")


def agregar_marcadores(ruta_pdf, paginas_conocidas=None):
    """Post-proceso: agrega marcadores (outline) usando los destinos con nombre que crea Chrome."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("  (sin pypdf: PDF sin marcadores; instalá con 'py -3 -m pip install pypdf')")
        return
    r = PdfReader(ruta_pdf)
    nd = r.named_destinations
    w = PdfWriter()
    w.append(r)

    def pagina(clave):
        if paginas_conocidas and clave in paginas_conocidas:
            return paginas_conocidas[clave] - 1
        d = nd.get("/" + clave) or nd.get(clave)
        if d is None:
            return None
        try:
            return r.get_destination_page_number(d)
        except Exception:
            return None

    def add(titulo, clave, parent=None):
        p = pagina(clave)
        if p is None:
            return parent
        return w.add_outline_item(titulo, p, parent=parent)

    add("Portada", "portada-texto")
    add("Mapa del curso", "mapa-curso")
    for erel, etit in ETAPAS:
        padre = add(etit, ancla(erel))
        mnum = re.search(r"etapa-(\d)", erel)
        if not mnum:
            continue
        pref = f"{mnum.group(1)}-" if mnum.group(1) == "6" else f"0{mnum.group(1)}-"
        for lrel, ltit in LECCIONES:
            if os.path.basename(lrel).startswith(pref):
                add(ltit, ancla(lrel), parent=padre)
    rama = add("2D · Windows internals (optativa)", ancla("2d.html"))
    for rel, titulo in RAMA_2D:
        if rel != "2d.html":
            add(titulo, ancla(rel), parent=rama)
    add("Glosario", "glosario")
    add("Preguntas y respuestas", "preguntas")
    add("Fuentes y límites", "fuentes")

    with open(ruta_pdf, "wb") as f:
        w.write(f)
    print("  marcadores agregados")


if __name__ == "__main__":
    main()
