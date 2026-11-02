# -*- coding: utf-8 -*-
"""Construye el Tomo II de 'Reversing en Windows':
'Kernel, Drivers y Windows Internals' (Edición 5 · Revisión 5.4 Ampliada)
Genera el paquete HTML y compila el PDF paginado con marcadores jerárquicos y paridad par estricta (<= 200 páginas).
"""
import os
import sys
import re
import html
import shutil
import subprocess
import unicodedata
import pypdf

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = THIS_DIR
MODULES_DIR = os.path.join(THIS_DIR, "_trabajo")
DST_GUIA = REPO_ROOT
ARTIFACT_DIR = r"C:\Users\agust\.gemini\antigravity\brain\5f78e7db-99bc-4011-8024-f93ab7c13c8f"
MIRROR_LOCAL = r"D:\Guia\CLS_Guia_Gemini"
PENDRIVE_USB = r"E:\\"

sys.path.insert(0, REPO_ROOT)
from construir_suite import (
    buscar_chrome,
    parsear_pdf_destinos_y_paginas,
    inyectar_outlines_puro,
    SCRATCH_BRAIN,
    normalizar,
)
from construir_tomo3 import md_to_html

CHROME = buscar_chrome()

# -----------------------------------------------------------------------------
# 1. Definición Completa de Módulos y Lecciones de Tomo II
# -----------------------------------------------------------------------------

LECCIONES_E6 = [
    ("guia/6-01-arquitectura-kernel.html", "6.1 Arquitectura del kernel y modelo de E/S"),
    ("guia/6-02-kmdf-ioctl.html", "6.2 KMDF: driver propio con IOCTL inocuo"),
    ("guia/6-03-debug-kernel.html", "6.3 Debugging de kernel y bugchecks"),
    ("guia/6-04-revision-driver.html", "6.4 Revisión defensiva de un driver"),
    ("guia/6-05-minifilters.html", "6.5 Minifilters y callbacks"),
    ("guia/6-06-mitigaciones.html", "6.6 Mitigaciones de Windows para drivers"),
    ("guia/6-07-vbs-hvci-callbacks.html", "6.7 Seguridad profunda en kernel: VBS/HVCI, Callbacks y BYOVD"),
    ("guia/6-08-wfp.html", "6.8 Windows Filtering Platform (WFP): capas ALE y callouts"),
    ("guia/6-09-kcfg-isa.html", "6.9 kCFG a nivel ISA, Bitmap y contraste con CET/IBT"),
    ("guia/6-10-kernel-fuzzing.html", "6.10 Fuzzing de drivers en modo kernel (IOCTL, WTF, kAFL)"),
]

LECCIONES_2D = [
    ("guia/2d-01-objetos.html", "2D.1 Objetos del ejecutivo y tokens de seguridad"),
    ("guia/2d-02-memoria-loader.html", "2D.2 Memoria virtual y el loader de Windows"),
    ("guia/2d-03-registro.html", "2D.3 Arquitectura del Registro de Windows"),
    ("guia/2d-04-servicios.html", "2D.4 Servicios de Windows (SCM)"),
    ("guia/2d-05-task-scheduler.html", "2D.5 Programador de tareas (Task Scheduler)"),
    ("guia/2d-06-com-interfaces.html", "2D.6 Component Object Model (COM): Interfaces"),
    ("guia/2d-07-com-activacion.html", "2D.7 Activación y servidores COM"),
    ("guia/2d-08-dcom-rpc.html", "2D.8 DCOM y RPC sobre ALPC/TCP"),
    ("guia/2d-09-wmi.html", "2D.9 Windows Management Instrumentation (WMI)"),
    ("guia/2d-10-ipc.html", "2D.10 Comunicación entre procesos (IPC) y puertos ALPC"),
    ("guia/2d-11-excepciones.html", "2D.11 Manejo de excepciones x64 (.pdata, SEH, VEH)"),
    ("guia/2d-12-etw.html", "2D.12 Event Tracing for Windows (ETW) y ETWti"),
    ("guia/2d-13-integrador.html", "2D.13 Laboratorio integrador: análisis guiado"),
    ("guia/2d-14-win32k-shadow.html", "2D.14 Subsistema gráfico Win32k y Shadow SSDT"),
    ("guia/2d-15-uefi-boot-chain.html", "2D.15 Cadena de arranque UEFI, winload y bootkits"),
    ("guia/2d-16-hyper-v.html", "2D.16 Hyper-V, particiones, VMBus y virtualización"),
    ("guia/2d-17-vbs-profundo.html", "2D.17 Arquitectura profunda de VBS, Secure Kernel y HVCI"),
]

def ancla(rel):
    return "sec-" + re.sub(r"[^a-zA-Z0-9]+", "-", rel.replace(".html", "")).strip("-")

# Mapa de navegación interna para resolver links cruzados
mapa = {}
mapa["guia/etapa-6.html"] = ancla("guia/etapa-6.html")
mapa["etapa-6.html"] = ancla("guia/etapa-6.html")
mapa["2d.html"] = ancla("2d.html")
mapa["../2d.html"] = ancla("2d.html")

for rel, _ in LECCIONES_E6:
    mapa[rel] = ancla(rel)
    mapa[os.path.basename(rel)] = ancla(rel)

for rel, _ in LECCIONES_2D:
    mapa[rel] = ancla(rel)
    mapa[os.path.basename(rel)] = ancla(rel)

mapa["2d-hyperv.html"] = ancla("guia/2d-16-hyper-v.html")
mapa["guia/2d-hyperv.html"] = ancla("guia/2d-16-hyper-v.html")

mapa["ERRATAS_TOMO_II.md"] = "tomo2-anexo-erratas"
mapa["PLAN_DE_AMPLIACION.md"] = "tomo2-anexo-plan"

def contenido(rel):
    ruta = os.path.join(DST_GUIA, rel.replace("/", os.sep))
    with open(ruta, encoding="utf-8") as f:
        h = f.read()
    m = re.search(r'<main[^>]*id="contenido"[^>]*>(.*?)</main>', h, re.S)
    if not m:
        m = re.search(r'<main[^>]*>(.*?)</main>', h, re.S)
    if not m:
        raise ValueError(f"No se encontró <main> en {rel}")
    cuerpo = m.group(1)
    cuerpo = re.sub(r'<nav class="migas".*?</nav>', "", cuerpo, flags=re.S)
    cuerpo = re.sub(r'<div class="pager">.*?</div>', "", cuerpo, flags=re.S)
    cuerpo = re.sub(r'<aside class="callout[^"]*"><p class="callout-titulo">Volver</p>.*?</aside>', "", cuerpo, flags=re.S)
    cuerpo = cuerpo.replace('<h2 id="fuentes">', '<h2>')
    cuerpo = cuerpo.replace("<details", "<details open")
    return cuerpo

def limpiar_enlaces(html_str, mapa_local):
    def rep(m):
        clase = m.group(1) or ""
        href = m.group(2)
        texto = m.group(3)
        if href.startswith(("http://", "https://", "mailto:")):
            return f'<a href="{href}">{texto}</a>'
        if "fuente" in clase:
            return f'<span class="fuente">{texto}</span>'
        if href in mapa_local:
            return f'<a href="#{mapa_local[href]}">{texto}</a>'
        if href.startswith("#"):
            return f'<a href="{href}">{texto}</a>'
        return f"<span>{texto}</span>"

    return re.sub(
        r'<a(?:\s+class="([^"]*)")?\s+href="([^"]+)"[^>]*>(.*?)</a>',
        rep,
        html_str,
        flags=re.S,
    )

# -----------------------------------------------------------------------------
# 2. Generación del HTML Maestro de Impresión para Tomo II
# -----------------------------------------------------------------------------

def generar_html_tomo2():
    css = open(os.path.join(DST_GUIA, "guia", "estilo.css"), encoding="utf-8").read()
    css_print = """
@page {
  size: A4;
  margin: 18mm 16mm 20mm 16mm;
  @bottom-center {
    content: counter(page);
    font-family: Helvetica, Arial, sans-serif;
    font-size: 8pt;
    color: #666666;
  }
}
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { background: #fff; font-size: 10.5pt; line-height: 1.5; }
main { max-width: none; padding: 0; }
.print-sec { break-before: page; }
.print-sec:first-of-type { break-before: auto; }
.print-sec h1 { font-size: 20pt; margin-top: 0; }
.print-sec h2 { font-size: 13pt; margin-top: 1.4em; }
.print-sec h3 { font-size: 11.5pt; }
.print-sec pre, .print-sec code, .print-sec pre code {
  color: #111111 !important;
  -webkit-text-fill-color: #111111 !important;
}
.print-sec pre {
  font-size: 8.3pt;
  white-space: pre-wrap;
  break-inside: avoid;
  page-break-inside: avoid;
  background-color: #f6f8fa !important;
  border: 1px solid #d0d7de !important;
  border-radius: 4px;
  padding: 6px 10px;
}
.print-sec code {
  font-family: "Cascadia Code", "Consolas", monospace !important;
}
.print-sec :not(pre) > code {
  background-color: #f0f2f5 !important;
  padding: 1px 4px;
  border-radius: 3px;
  border: 1px solid #e1e4e8;
}
.print-sec pre.arbol-triage { font-size: 6.5pt; line-height: 1.17; padding: 6px 10px; margin: 4px 0; }
.print-sec table { font-size: 8.6pt; width: 100%; table-layout: auto; word-wrap: break-word; overflow-wrap: break-word; word-break: normal; }
.print-sec th, .print-sec td { overflow-wrap: break-word; word-break: normal; hyphens: none; }
.print-sec td:not(:first-child) code, .print-sec th:not(:first-child) code { word-break: break-word; }
.print-sec .tabla { overflow-x: visible !important; break-inside: avoid; page-break-inside: avoid; }
.print-sec tr { break-inside: avoid; page-break-inside: avoid; }
.print-sec .callout, .print-sec .gate, .print-sec details, .print-sec .ampliacion-ext, .print-sec .nota-ed { break-inside: avoid; page-break-inside: avoid; }
.print-sec h2, .print-sec h3, .print-sec h4 { break-after: avoid; page-break-after: avoid; }
.print-sec a { color: #000; text-decoration: none; }
.portada-pdf { text-align: left; padding-top: 26mm; }
.portada-pdf .kicker { color: #0b5f6b; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: 9pt; }
.portada-pdf h1 { font-size: 34pt; line-height: 1.05; margin: .2em 0 .3em; }
.portada-pdf .sub { font-size: 11.5pt; color: #333; max-width: 165mm; line-height: 1.5; margin-bottom: 5mm; }
.portada-pdf .aviso { border-left: 4px solid #8a1c1c; background: #fbe7e7; padding: 8pt 10pt; margin: 16pt 0; font-size: 9.5pt; }
.toc { margin-top: 14pt; }
.toc .etapa { font-weight: 700; font-size: 11pt; color: #0b5f6b; margin-top: 5mm; margin-bottom: 2mm; border-bottom: 1px solid #ccc; padding-bottom: 1mm; }
.toc ol { list-style: none; padding-left: 0; margin: 0; }
.toc li { display: flex; justify-content: space-between; align-items: baseline; font-size: 9.5pt; padding: 1.2mm 0; border-bottom: 1px dotted #e0e0e0; }
.toc li a { color: #222; text-decoration: none; flex-grow: 1; padding-right: 4mm; }
.toc-pag { font-weight: 700; color: #0b5f6b; font-size: 9pt; text-align: right; min-width: 14mm; }
"""

    partes = [f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Reversing en Windows — Tomo II</title><style>{css}\n{css_print}</style></head><body><main>']

    # 1. Portada
    partes.append("""
<section class="print-sec portada-pdf" id="portada">
<p class="kicker">Ingeniería Inversa en Windows · Edición Libre y Abierta · Revisión 5.4 (Ampliada) · TOMO II DE III</p>
<h1>Reversing en Windows<br><span style="font-size: 19pt; font-weight: 600; color: #0b5f6b;">Tomo II — Ramas Especializadas: Kernel, Drivers e Internals</span></h1>
<p class="sub">Profundización avanzada en el sistema operativo Windows a nivel Ring 0 y subsistemas de plataforma: arquitectura del kernel NT, drivers WDM/KMDF, IOCTLs, depuración de kernel con WinDbg (KDNET), minifiltros de sistema de archivos, mitigaciones HVCI/VBS, Windows Filtering Platform (WFP), kCFG a nivel ISA y CET/IBT, Fuzzing de drivers en kernel (WTF, kAFL/Nyx), objetos del ejecutivo, procesos/hilos, Registro, servicios, Task Scheduler, COM/DCOM, RPC, WMI, ALPC, excepciones x64 (.pdata/UNWIND_INFO), ETW/ETWti, virtualización con Hyper-V/VMBus, mitigación Win32k System Call Lockdown y cadena de arranque segura UEFI/bootkits.</p>
<p class="sub"><strong>Contenido y Balance Editorial de este Volumen:</strong> Comprende la <strong>Etapa 6 completa (Lecciones 6.1 a 6.10)</strong>, la <strong>Rama 2D completa (Lecciones 2D.1 a 2D.17)</strong> y el <strong>Anexo A (Fe de Erratas Técnica y Trazabilidad con Tomo I)</strong>, en su versión íntegra, exhaustiva y sin condensación de formato.</p>
<p class="sub"><strong>Requisitos previos:</strong> Este tomo asume el dominio del tronco principal (Etapas 0 a 4 del <strong>Tomo I</strong>). Para las sesiones prácticas de laboratorio en Ring 0 se recomienda tener abierta la <strong>Separata de Escritorio</strong> (Hojas 1 a 6).</p>
<div class="aviso"><strong>Seguridad de Laboratorio Obligatoria:</strong> Toda práctica con controladores de kernel (<code>.sys</code>), depuración con <code>bcdedit /debug on</code>, Driver Verifier, Special Pool o interceptores de red debe realizarse exclusivamente dentro de una <strong>máquina virtual aislada y descartable</strong>, nunca en la estación de trabajo física.</div>
</section>
""")

    # 2. Índice General (TOC)
    t2_anchors = []

    def t2_ref(aid):
        return f'<span class="toc-pag" data-anchor="{aid}">calculando</span>'

    def t2_row(aid, title):
        t2_anchors.append(aid)
        return f'<li><a href="#{aid}">{title}</a>{t2_ref(aid)}</li>'

    def t2_heading(aid, title):
        t2_anchors.append(aid)
        return f'<div class="etapa"><a href="#{aid}">{title}</a>{t2_ref(aid)}</div>'

    toc_t2 = ['<section class="print-sec" id="toc"><h1>Contenido — Tomo II</h1><div class="toc" style="max-width: 175mm;">']

    # Etapa 6 en TOC
    toc_t2.append(t2_heading(mapa["guia/etapa-6.html"], "Etapa 6 · Kernel y drivers en Windows (Lecciones 6.1 a 6.10)") + '<ol>')
    for rel, tit in LECCIONES_E6:
        toc_t2.append(t2_row(mapa[rel], tit))
    toc_t2.append('</ol>')

    # Rama 2D en TOC
    toc_t2.append(t2_heading(mapa["2d.html"], "Rama 2D · Windows Internals y Virtualización (Lecciones 2D.1 a 2D.17)") + '<ol>')
    for rel, tit in LECCIONES_2D:
        toc_t2.append(t2_row(mapa[rel], tit))
    toc_t2.append('</ol>')

    # Anexo Erratas en TOC
    toc_t2.append('<div class="etapa" style="margin-top:5mm;">Anexos Editoriales</div><ol>')
    toc_t2.append(t2_row("tomo2-anexo-erratas", "Anexo A · Fe de Erratas Técnica y Matriz de Trazabilidad con Tomo I"))
    toc_t2.append('</ol>')

    toc_t2.append('</div></section>')
    partes.append("".join(toc_t2))

    # 3. Contenido de Lecciones
    anclas_presentes = set(t2_anchors) | {"portada", "toc"}
    mapa_t2 = {k: v for k, v in mapa.items() if v in anclas_presentes}

    # Apertura Etapa 6
    h_e6 = limpiar_enlaces(contenido("guia/etapa-6.html"), mapa_t2)
    partes.append(f'<section class="print-sec" id="{mapa["guia/etapa-6.html"]}">{h_e6}</section>')

    # Lecciones 6.1 a 6.10
    for lrel, _ in LECCIONES_E6:
        lh = limpiar_enlaces(contenido(lrel), mapa_t2)
        partes.append(f'<section class="print-sec" id="{mapa[lrel]}">{lh}</section>')

    # Apertura Rama 2D
    h_2d = limpiar_enlaces(contenido("2d.html"), mapa_t2)
    partes.append(f'<section class="print-sec" id="{mapa["2d.html"]}">{h_2d}</section>')

    # Lecciones 2D.1 a 2D.17
    for lrel, _ in LECCIONES_2D:
        lh = limpiar_enlaces(contenido(lrel), mapa_t2)
        partes.append(f'<section class="print-sec" id="{mapa[lrel]}">{lh}</section>')

    # 4. Anexo A: Fe de Erratas
    with open(os.path.join(DST_GUIA, "ERRATAS_TOMO_II.md"), "r", encoding="utf-8") as f_err:
        erratas_raw = f_err.read()

    erratas_html = md_to_html(erratas_raw, section_prefix="erratas")
    partes.append(f'<section class="print-sec" id="tomo2-anexo-erratas"><h1 style="color:#0b5f6b;">Anexo A · Fe de Erratas Técnica y Matriz de Trazabilidad</h1>{erratas_html}</section>')

    partes.append("</main></body></html>")

    # Estructura de marcadores PDF (outlines / bookmarks)
    hijos_e6 = [(tit, ancla(rel)) for rel, tit in LECCIONES_E6]
    hijos_2d = [(tit, ancla(rel)) for rel, tit in LECCIONES_2D]
    arbol_marcadores = [
        ("Portada y Prólogo", "portada", []),
        ("Índice General", "toc", []),
        ("Etapa 6 · Kernel y Drivers en Windows", ancla("guia/etapa-6.html"), hijos_e6),
        ("Rama 2D · Windows Internals y Virtualización", ancla("2d.html"), hijos_2d),
        ("Anexo A · Fe de Erratas Técnica", "tomo2-anexo-erratas", []),
    ]

    return "\n".join(partes), t2_anchors, arbol_marcadores

# -----------------------------------------------------------------------------
# 3. Motor de Compilación y Estabilización con Chrome Headless
# -----------------------------------------------------------------------------

def compilar_tomo2_pdf():
    html_doc, toc_anchors, arbol_marcadores = generar_html_tomo2()

    salida_html = os.path.join(DST_GUIA, "_trabajo", "print", "Tomo_2_Kernel_e_Internals.html")
    draft_pdf = os.path.join(DST_GUIA, "_trabajo", "print", "Tomo_2_borrador.pdf")
    salida_pdf = os.path.join(DST_GUIA, "Tomo_2_Kernel_e_Internals.pdf")
    artifact_pdf = os.path.join(ARTIFACT_DIR, "Tomo_2_Kernel_e_Internals.pdf")

    os.makedirs(os.path.dirname(salida_html), exist_ok=True)

    def renderizar(src_html, dst_pdf):
        cmd = [
            CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--user-data-dir=" + os.path.join(SCRATCH_BRAIN, "chrome-prof"),
            "--allow-file-access-from-files", "--virtual-time-budget=15000",
            "--no-pdf-header-footer", "--print-to-pdf-no-header",
            f"--print-to-pdf={dst_pdf}",
            "file:///" + src_html.replace("\\", "/"),
        ]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.returncode != 0 or not os.path.exists(dst_pdf):
            raise RuntimeError(f"Fallo al renderizar PDF con Chrome: {r.stderr.decode('utf-8', errors='ignore')}")

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
            if cantidad == 1:
                etiquetas[ancla_id] = f"p. {inicio}"
            else:
                etiquetas[ancla_id] = f"pp. {inicio}–{fin} ({cantidad} págs.)"
        return etiquetas

    def reemplazar_etiquetas(html_s, etiquetas):
        def rep(m):
            ancla_id = m.group(1)
            texto = etiquetas.get(ancla_id, "calculando")
            return f'<span class="toc-pag" data-anchor="{ancla_id}">{texto}</span>'
        return re.sub(
            r'<span class="toc-pag" data-anchor="([^"]+)">.*?</span>',
            rep, html_s, flags=re.S,
        )

    print("\n[Tomo 2] Renderizando e iterando el índice paginado con Chrome...")
    etiquetas = {}
    total = 0
    paginas = {}
    dests_oid_map = {}

    for intento in range(4):
        with open(salida_html, "w", encoding="utf-8") as f:
            f.write(html_doc)
        renderizar(salida_html, draft_pdf)
        paginas, dests_oid_map, _page_objs, total = parsear_pdf_destinos_y_paginas(draft_pdf, toc_anchors)
        nuevas = etiquetas_paginas(toc_anchors, paginas, total)
        print(f"  Paso {intento + 1}: {total} páginas generadas | {len(nuevas)} anclas indexadas")
        if intento > 0 and nuevas == etiquetas:
            print("  TOC estabilizado exitosamente.")
            break
        etiquetas = nuevas
        html_doc = reemplazar_etiquetas(html_doc, etiquetas)

    total_contenido = total
    # Asegurar paridad par para encuadernación doble faz
    if total % 2 != 0:
        print(f"  Total impar ({total} págs.). Añadiendo página blanca final para cuadernillos pares...")
        html_doc = html_doc.replace("</main></body></html>", '<section class="print-sec" style="break-before:page;page-break-before:always;"><p style="color:#aaa;text-align:center;margin-top:120mm;font-size:9pt;">— Página reservada para anotaciones de laboratorio —</p></section></main></body></html>')
        with open(salida_html, "w", encoding="utf-8") as f:
            f.write(html_doc)
        renderizar(salida_html, draft_pdf)
        paginas, dests_oid_map, _page_objs, total = parsear_pdf_destinos_y_paginas(draft_pdf, toc_anchors)
        print(f"  Total con paridad par garantizada: {total} páginas.")

    # Inyección de marcadores PDF (outlines)
    print("  Inyectando marcadores jerárquicos (PDF outlines)...")
    dests_oid_map["portada"] = _page_objs[0]
    dests_oid_map["toc"] = _page_objs[1]
    shutil.copy2(draft_pdf, salida_pdf)
    inyectar_outlines_puro(salida_pdf, arbol_marcadores, dests_oid_map)

    # Copias de distribución
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    shutil.copy2(salida_pdf, artifact_pdf)
    print(f"  Copia en artefactos: {artifact_pdf}")

    if os.path.exists(MIRROR_LOCAL):
        dst_m = os.path.join(MIRROR_LOCAL, "Tomo_2_Kernel_e_Internals.pdf")
        shutil.copy2(salida_pdf, dst_m)
        print(f"  Copia en mirror D:\\: {dst_m}")

    if os.path.exists(PENDRIVE_USB):
        dst_e = os.path.join(PENDRIVE_USB, "Tomo_2_Kernel_e_Internals.pdf")
        shutil.copy2(salida_pdf, dst_e)
        print(f"  Copia en pendrive E:\\: {dst_e}")

    tam = os.path.getsize(salida_pdf)
    print(f"\n=======================================================")
    print(f"TOMO II COMPILADO EXITOSAMENTE:")
    print(f"  Archivo: {salida_pdf}")
    print(f"  Tamaño: {tam:,} bytes ({tam/(1024*1024):.2f} MB)")
    print(f"  Páginas totales: {total} págs. (Paridad par: {total % 2 == 0})")
    print(f"=======================================================\n")

if __name__ == "__main__":
    compilar_tomo2_pdf()
