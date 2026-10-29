# -*- coding: utf-8 -*-
"""Genera tres páginas-índice de material adicional de CLS, en src/ (build.py las pasa a HTML):

  - ida-tutes.md : los 69 tutoriales del «Curso IDA desde cero» (texto extraído + tema).
  - teorias.md   : clasificación por título de los 2.017 Teorias_Numeradas (educativo vs cracking).
  - telegram.md  : transcripciones de Telegram clasificadas por tema (heurística por palabras clave).

Todo con etiqueta honesta: lo de IDA es texto extraído y leído por índice; lo de Teorías y Telegram
es clasificación por TÍTULO/palabras clave, no lectura completa de cada archivo.
"""
import csv
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # carpeta que contiene CLS_Guia
GUIA = os.path.join(RAIZ, "CLS_Guia")
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
TELV = os.path.join(RAIZ, "CLS_resultados_intermedios", "transcripciones", "telegram_videos")
TELA = os.path.join(RAIZ, "CLS_resultados_intermedios", "transcripciones", "telegram_audios")


def escribir(rel, texto):
    with open(os.path.join(SRC, rel), "w", encoding="utf-8") as f:
        f.write(texto.rstrip() + "\n")


# ---------------------------------------------------------------- IDA
# Curaduría por tute: tema corto, qué enseña (síntesis leída de la apertura del texto),
# y video afín del MISMO AUTOR (Ricardo Narvaja) en «Reversing desde cero» (en x64dbg/OllyDbg).
# El curso IDA es SOLO texto: el video no es "de este tute" sino el que cubre el mismo tema.
IDA_TUTES = {
    1:  ("Qué es IDA y el curso", "Presenta la serie (la versión en IDA del curso de OllyDbg): loader vs. debugger y cómo encarar Windows.", "01 x64dbg primeros pasos"),
    2:  ("Sistemas de numeración", "Repaso base para arrancar de cero: binario, decimal, hexadecimal, bits y bytes.", "03 Registros, Flags y Números"),
    3:  ("El LOADER de IDA", "El analizador estático: recorrer sus partes y las primeras instrucciones de transferencia.", "14 Conociendo IDA"),
    4:  ("Instrucciones de transferencia", "MOV/XCHG y cómo editar una instrucción en el loader (sobre el crackme de Cruehead).", "04 Instrucciones 2"),
    5:  ("Más instrucciones", "Sigue con las instrucciones principales; su efecto se verá después en el debugger.", "06 Instrucciones 3"),
    6:  ("Aritméticas y lógicas", "ADD/SUB/AND/OR/XOR: operandos, registros y memoria.", "08 Instrucciones 4"),
    7:  ("Control de flujo", "Saltos condicionales e incondicionales y las comparaciones que los disparan.", "09 Instrucciones 5"),
    8:  ("Trabajar en el loader", "Método de reversing estático: comentar y renombrar para entender sin ejecutar.", "15 Ejercicio 2 - Análisis estático"),
    9:  ("Práctica: crackme HOLA_REVERSER", "Primer análisis estático guiado de un crackme propio.", "15 Ejercicio 2 - Análisis estático"),
    10: ("Loader + debugger", "Complementar estático y dinámico; IDA soporta varios debuggers.", "07 Breakpoints"),
    11: ("Bug de IDA 6.8", "Cómo detectar y mitigar el bug de esa versión (fixeado en 6.9).", ""),
    12: ("Práctica: TEST_REVERSER", "Ejercicio propio sencillo para afianzar las instrucciones vistas.", "16 Ejercicio 3 - Análisis Dinámico y Estático"),
    13: ("Plugins de IDA", "Plugins útiles y cómo se usan (nota de compatibilidad 6.8/7.x).", ""),
    14: ("Unpacking 1: UPX", "Desempacar un CRACKME comprimido con UPX y llegar al OEP.", "10 Unpacking 1 - UPX"),
    15: ("Dump y reconstrucción de la IAT", "Dumpear y reconstruir la IAT con Scylla.", "17 Unpacking 3 - IAT Redirection"),
    16: ("Unpacking ASPack 2.2", "Desempacar UnPackMe_ASPack 2.2 (packer didáctico, categoría sencilla).", "13 Unpacking 2 - OEP"),
    17: ("Resolver el ejercicio de unpacking", "Solución del UnPackMe pendiente.", "13 Unpacking 2 - OEP"),
    18: ("Reversear lo desempacado", "Analizar el ejecutable ya desempacado (crackme didáctico).", ""),
    19: ("Crackme de Cruehead", "Reversear el crackme clásico de Cruehead en el loader.", "16 Ejercicio 3 - Análisis Dinámico y Estático"),
    20: ("Qué es una vulnerabilidad", "Introducción al análisis de vulnerabilidades simples; qué es y cómo mirarla.", ""),
    21: ("¿Vulnerable o no?", "Análisis del ejercicio: decidir si hay una vulnerabilidad real.", ""),
    22: ("Differ (comparar versiones)", "Qué es un differ y cómo empareja funciones entre dos versiones de un programa.", ""),
    23: ("Ejercicio IDA1.exe", "Función basada en EBP compilada con DevC++; resolverla.", "18 Funciones basadas en EBP vs basadas en ESP"),
    24: ("Ejercicio IDA2 (cookies)", "Dos valores/cookies a comparar; soluciones de IDA2/3/4.", "20 Ejercicio 4 - Análisis Estático"),
    25: ("Estructuras en IDA (1)", "Cómo ayuda IDA cuando el programa usa estructuras.", "23 Ejercicio con Estructuras (con símbolos)"),
    26: ("Estructuras en IDA (2)", "Por qué agrupar datos en estructuras y cómo aplicarlo en IDA.", "23 Ejercicio con Estructuras (con símbolos)"),
    27: ("Solución IDA_STRUCT", "Resolver el ejercicio de estructuras con símbolos.", "23 Ejercicio con Estructuras (con símbolos)"),
    28: ("Teoría de repaso", "Temas teóricos variados intercalados entre ejercicios.", ""),
    29: ("Programas reales y CVE", "Pasar de crackmes a software real; propone un CVE para practicar.", ""),
    30: ("VLC · CVE-2008-4654", "Diff de dos versiones de VLC guiado por el CVE.", ""),
    31: ("Explicación de la solución del CVE", "Aclara los puntos del buffer overflow del caso VLC.", ""),
    32: ("WinDbg + IDA", "Instalar y manejar WinDbg desde la interfaz de IDA.", ""),
    33: ("Plugins de WinDbg + Mona", "Instalar Mona y plugins de WinDbg standalone.", ""),
    34: ("Explotación y mitigaciones", "Arranca ejecución de código e introduce DEP y otras protecciones.", ""),
    35: ("DEP vs. sin DEP", "Compila con y sin DEP (SetProcessDEPPolicy) para comparar.", ""),
    36: ("Solucionando DEP.exe", "Adaptar el script a la versión con DEP.", ""),
    37: ("Mona en WinDbg", "Mismo ejemplo resuelto con Mona fuera de IDA.", ""),
    38: ("Canary y SEH", "Qué es el canary (stack cookie) y su relación con el SEH.", "21 Excepciones 2"),
    39: ("Canary + DEP pisando SEH", "Caso final: stack overflow con canary y DEP por SEH.", "21 Excepciones 2"),
    40: ("Shellcode", "Tipos de shellcode y su rol en el exploit (con nota de compatibilidad).", ""),
    41: ("Strings en stack y heap", "Ejemplo que ubica cadenas en stack vs. heap.", ""),
    42: ("Ejercicios pendientes", "Resolución de los ejercicios dejados en la parte 41.", ""),
    43: ("Solución práctica 41b", "Demangled names, new vs. malloc; primeros pasos de heap.", ""),
    44: ("WinDbg dentro de IDA (heap)", "Información de heap que se obtiene con WinDbg embebido.", ""),
    45: ("Mona en PRACTICA41b", "Repasar el ejercicio con Mona en WinDbg.", ""),
    46: ("Ejercicio parte 44 (heap)", "Consideraciones de los exploits de heap.", ""),
    47: ("Más teoría de heap", "Aclara conceptos de heap sobre la práctica 44.", ""),
    48: ("LFH vs. heap estándar", "Seguir una alocación y ver dónde cae (LFH o heap estándar).", ""),
    49: ("Cierre user-mode / rumbo a kernel", "Repaso de lo visto y anuncio de la rama de kernel.", ""),
    50: ("Kernel de Windows: escenario", "Armar el entorno para reversear y debuggear kernel.", ""),
    51: ("Drivers en kernel", "Compilar y reversear drivers propios para familiarizarse.", ""),
    52: ("Estructuras de kernel", "Estructuras y mecanismos previos a la explotación.", ""),
    53: ("IRP e IOCTL", "Reversear hasta el IOCTL code; la estructura IRP.", ""),
    54: ("Práctica driver + cliente Python", "Modificar el driver y hacer el cliente en user con Python.", ""),
    55: ("Otro ejercicio de kernel", "Modificar un valor desde kernel evitando la pantalla azul.", ""),
    56: ("HackSys vulnerable driver", "Driver con vulnerabilidades didácticas (HEVD) para estudiarlas.", ""),
    57: ("HackSys: stack overflow", "Explotar el stack overflow del driver desde Python.", ""),
    58: ("Shellcode de token (kernel)", "Shellcode que copia el token de un proceso system (se analiza).", ""),
    59: ("Arbitrary overwrite", "Escritura arbitraria en el driver (método antiguo, XP/7).", ""),
    60: ("HAL en kernel", "Script en Python basado en el código C del driver vulnerable.", ""),
    61: ("Integer overflow (kernel)", "Caso de integer overflow en el mismo driver.", ""),
    62: ("Variante en Windows 10 x86", "La misma explotación del driver, ahora en Win10 de 32 bits.", ""),
    63: ("Segmentación y paginación x86", "Manejo de memoria en x86 (y rumbo a 64 bits).", ""),
    64: ("Desafío SCADA · CVE-2013-0657", "Reversear un CVE real propuesto en los grupos.", ""),
    65: ("Desafío Ekoparty 2018 (1)", "Reversear paso a paso el server de 64 bits del reto.", ""),
    66: ("Desafío Ekoparty 2018 (2)", "Script en Python del exploit del reto.", ""),
    67: ("HackSys pisando SEH (32-bit)", "Método para bypassear la cookie vía SEH.", ""),
    68: ("SSDT y syscalls", "Resolver syscalls: a qué función de kernel saltan.", ""),
    69: ("VA → física a mano (64-bit)", "Traducir una dirección virtual a física manualmente.", ""),
}

# Grupos: rango, título, nota de alcance, lecciones de la guía que conecta.
IDA_GRUPOS = [
    (1, 13, "Base de IDA, assembly y primeras prácticas", "En scope — Etapa 2.",
     [("Herramientas", "02-herramientas"), ("IDA", "02-ida"), ("Instrucciones", "02-instrucciones"),
      ("Flujo", "02-flujo"), ("Debugger", "02-debugger"), ("Números", "01-numeros")]),
    (14, 18, "Unpacking didáctico (UPX, ASPack), dump e IAT", "Avanzado; packers didácticos, no protectores comerciales. El desempaquetado queda **fuera del recorrido base** de esta guía.",
     []),
    (19, 24, "Crackmes, differ y ejercicios", "En scope como práctica de análisis.",
     [("IDA", "02-ida"), ("Llamadas y pila", "02-llamadas"), ("Flujo", "02-flujo"), ("Vulnerabilidades (defensivo)", "05-vulnerabilidades")]),
    (25, 28, "Estructuras en IDA", "En scope.",
     [("IDA", "02-ida"), ("Memoria", "01-memoria")]),
    (29, 48, "Vulnerabilidades y exploiting en user-mode (VLC/CVE, DEP, Mona, canary/SEH, shellcode, heap)", "Etapa 5, **defensivo-avanzado**: la guía cubre el defecto y las mitigaciones de forma conceptual y defensiva, no la construcción de exploits.",
     [("Vulnerabilidades (defensivo)", "05-vulnerabilidades")]),
    (49, 69, "Kernel de Windows y temas avanzados (drivers, HackSys/HEVD, SSDT/syscalls, VA→física)", "Avanzado, **fuera del recorrido base**. Material de explotación de kernel: se lista por completitud, no se desarrolla.",
     [("Fuera de alcance", "05-fuera-de-alcance")]),
]


def gen_ida():
    csv_path = os.path.join(GUIA, "ida_tutes_indice.csv")
    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            rows.append(r)
    by_num = {int(r["numero"]): r for r in rows}
    tot_pal = sum(int(r["palabras"]) for r in rows)

    # Targets/herramientas por tute, leídos del texto extraído (dato observado).
    EXE = re.compile(r"\b([A-Za-z0-9_]+\.(?:exe|dll|7z))\b", re.I)
    CVE = re.compile(r"CVE-\d{4}-\d+", re.I)
    datos = {}
    extra_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extraido_ida")
    for n, r in by_num.items():
        try:
            txt = open(os.path.join(extra_dir, r["archivo"][:-5] + ".txt"), encoding="utf-8").read()
        except OSError:
            txt = ""
        exes = sorted(set(m.group(1) for m in EXE.finditer(txt)), key=str.lower)
        # descarta ejecutables de sistema/herramienta para no ensuciar el "target"
        ruido = {"windbg.exe", "idaq.exe", "gflags.exe", "explorer.exe", "cmd.exe", "conhost.exe",
                 "csrss.exe", "dllhost.exe", "dwm.exe", "taskhost.exe", "python.exe", "calc.exe",
                 "vcredist_x86.exe", "msvcrt.dll", "ntdll.dll", "gdi32.dll", "win32_remote.exe"}
        exes = [e for e in exes if e.lower() not in ruido]
        cves = sorted(set(CVE.findall(txt.upper())))
        datos[n] = (exes[:3], cves)

    L = [
        "---",
        'title: "Curso IDA desde cero · índice de los 69 tutoriales"',
        'description: "Qué enseña cada uno de los 69 tutoriales de IDA, con práctica, video afín y lección, y el texto extraído para leer offline."',
        "---",
        "",
        "# Curso «IDA desde cero» — índice de los 69 tutoriales",
        "",
        ":::{nota} Qué es esto y cómo leerlo",
        f"Se **extrajo el texto y las 3.278 capturas** de los 69 tutoriales `.docx` del curso (en total ~{tot_pal:,} palabras) y se armó este índice. ".replace(",", "."),
        "Cada tute trae: **qué enseña** (síntesis leída de su apertura), la **práctica/target** que usa (dato observado en el texto), "
        "un **video afín** y la **lección** de esta guía con la que se conecta. Y el enlace **📖 Leer tutorial ilustrado**, "
        "que abre el tute completo como página (texto + las pantallas de IDA intercaladas + tiempo de lectura). Así no es solo texto: es un mapa de por dónde entrar.",
        ":::",
        "",
        ":::{aviso} Sobre el «video afín»",
        "El curso IDA es **solo texto** (no tiene videos propios). El «▶ video afín» es del **mismo autor** (Ricardo Narvaja), de la serie "
        "«Reversing desde cero», que cubre el **mismo tema** pero con x64dbg/OllyDbg en vez de IDA. No es la grabación de ese tute: es el video que explica lo mismo. "
        "Lo abrís desde el [índice de videotutoriales](videos.html).",
        ":::",
        "",
        ":::{aviso} Alcance",
        "La parte **base (tutes 1–28)** encaja en el recorrido de esta guía. De la **29 en adelante** es vulnerabilidades/exploiting y, de la 49, kernel: "
        "material avanzado de la Etapa 5, **defensivo**. No se enseña a atacar sistemas ajenos ni a vulnerar software comercial.",
        ":::",
        "",
    ]
    for a, b, titulo, nota, lecciones in IDA_GRUPOS:
        L.append(f"## Tutes {a}–{b} · {titulo}")
        L.append("")
        L.append(nota)
        if lecciones:
            enl = " · ".join(f"[{lab}](guia/{slug}.html)" for lab, slug in lecciones)
            L.append("")
            L.append(f"**Se conecta con:** {enl}.")
        L.append("")
        for n in range(a, b + 1):
            r = by_num.get(n)
            if not r:
                continue
            tema, sintesis, video = IDA_TUTES.get(n, ("", r["resumen_primeras_lineas"][:120], ""))
            exes, cves = datos.get(n, ([], []))
            txt_rel = "CLS_Guia/_trabajo/extraido_ida/" + r["archivo"][:-5] + ".txt"
            extras = [f"**📖 [Leer tutorial ilustrado](ida_tutes/{n}.html)**"]
            tgt = ", ".join(f"`{e}`" for e in exes)
            if cves:
                tgt = (tgt + ", " if tgt else "") + ", ".join(f"`{c}`" for c in cves)
            if tgt:
                extras.append(f"*Práctica:* {tgt}")
            if video:
                extras.append(f"*▶ video afín:* [«{video}»](videos.html)")
            extras.append(f"{{{{src:{txt_rel}|solo texto}}}} ({int(r['palabras'])} palabras)")
            L.append(f"- **{n} · {tema}** — {sintesis} · " + " · ".join(extras))
        L.append("")
    escribir("ida-tutes.md", "\n".join(L))
    return len(rows), tot_pal


# ---------------------------------------------------------------- Teorias
CRACKING = {
    "E4 Práctica sobre software comercial", "E4 Unpacking", "E4 Seriales/keygen",
    "E4 Parcheo", "E4 Dongles/protecciones", "E4 Anti-debug",
}


def gen_teorias():
    csv_path = os.path.join(RAIZ, "CLS_resultados_intermedios", "teorias_numeradas_por_etapa.csv")
    cat = {}
    educ, crack = [], []
    with open(csv_path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            e = r["etapa"]
            cat[e] = cat.get(e, 0) + 1
            (crack if e in CRACKING else educ).append(r)
    total = sum(cat.values())
    n_crack = sum(v for k, v in cat.items() if k in CRACKING)
    n_educ = total - n_crack

    L = [
        "---",
        'title: "Teorias_Numeradas · clasificación por título"',
        'description: "Los 2.017 tutoriales de la colección Teorias_Numeradas separados en educativos vs cracking de software comercial."',
        "---",
        "",
        "# Teorias_Numeradas — clasificación por título",
        "",
        ":::{aviso} Clasificación por título, no por contenido",
        f"La colección tiene **{total:,} tutoriales** en contenedores (`.rar`/`.zip`/`.7z`, varios con contraseña), ~3,5 GB, **sin abrir**. "
        "Esta separación es **por el título** de cada uno, no por haber leído el contenido. Un título no demuestra lo que enseña: tomalo como orientación para buscar, no como material revisado.".replace(",", "."),
        ":::",
        "",
        f"De los {total} títulos, **~{n_crack} ({100*n_crack//total}%) apuntan a cracking de software comercial** "
        f"(práctica sobre programas comerciales, unpacking de protectores, seriales/keygen, parcheo, dongles, anti-debug) y quedan **fuera del recorrido base**. "
        f"Los **~{n_educ} restantes** son candidatos educativos (fundamentos, herramientas, .NET, crackmes de práctica, criptografía, y ramas avanzadas).",
        "",
        "## Distribución por categoría (etiqueta del título)",
        "",
        "| Categoría | Cantidad | Clase |",
        "|---|---|---|",
    ]
    for k, v in sorted(cat.items(), key=lambda x: -x[1]):
        clase = "cracking comercial (fuera de scope)" if k in CRACKING else "educativo / candidato"
        L.append(f"| {k} | {v} | {clase} |")
    L += [
        "",
        "## Candidatos educativos (no cracking)",
        "",
        "Son los que, por su título, no apuntan a cracking de software comercial. Igual hay que abrir y revisar cada uno antes de recomendarlo.",
        "",
    ]
    educ.sort(key=lambda r: r["etapa"])
    etapa_actual = None
    for r in educ:
        if r["etapa"] != etapa_actual:
            etapa_actual = r["etapa"]
            L.append(f"**{etapa_actual}**")
        L.append(f"- {r['numero']} — {r['titulo']}")
    escribir("teorias.md", "\n".join(L))
    return total, n_crack, n_educ


# ---------------------------------------------------------------- Telegram
KW_REV = ("reversing", "reverse", "ensamblador", "assembly", "ollydbg", "x64dbg", "x32dbg",
          "ida pro", " ida ", "debugger", "debugguear", "breakpoint", "desensambl", "unpack",
          "desempac", "stack", "registro eax", "opcode", "shellcode", "exploit", " pe ",
          "cabecera pe", "api de windows", "dll", "offset", "hexadecimal")
KW_CRACK = ("crack", "serial", "keygen", "parche", "parchear", "licencia", "activar",
            "registrar el programa", "full version", "pirat", "trial", "demo del programa")


def clasif(nombre, texto):
    t = (nombre + " " + texto[:1500]).lower()
    rev = any(k in t for k in KW_REV)
    crk = any(k in t for k in KW_CRACK)
    if crk and rev:
        return "cracking (usa reversing sobre software comercial)"
    if crk:
        return "cracking / activación de software comercial"
    if rev:
        return "reversing / técnico (candidato educativo)"
    return "charla / demo / otro (no técnico)"


def gen_telegram():
    filas = []
    for base, tipo in [(TELV, "video"), (TELA, "audio")]:
        if not os.path.isdir(base):
            continue
        for f in sorted(os.listdir(base)):
            if not f.endswith(".txt"):
                continue
            full = os.path.join(base, f)
            try:
                txt = open(full, encoding="utf-8", errors="ignore").read()
            except OSError:
                txt = ""
            nombre = f[:-4]
            # título "humano": lo que va después del id
            m = re.search(r"\d{4}-\d{2}-\d{2}_\d+_(.*)", nombre)
            etiqueta = (m.group(1) if m else nombre)
            filas.append((tipo, nombre, etiqueta, len(txt.split()), clasif(etiqueta, txt),
                          "CLS_resultados_intermedios/transcripciones/telegram_" + tipo + "s/" + f))
    # resumen por clase
    import collections
    por_clase = collections.Counter(x[4] for x in filas)
    # CSV completo
    with open(os.path.join(GUIA, "telegram_indice.csv"), "w", encoding="utf-8-sig", newline="") as g:
        w = csv.writer(g, delimiter=";")
        w.writerow(["tipo", "archivo", "etiqueta", "palabras", "clase", "ruta"])
        for row in filas:
            w.writerow(row)

    revs = [x for x in filas if x[4].startswith("reversing")]
    L = [
        "---",
        'title: "Transcripciones de Telegram · índice por tema"',
        'description: "Las 523 transcripciones de videos y audios de Telegram, clasificadas por tema con una heurística."',
        "---",
        "",
        "# Transcripciones de Telegram — índice por tema",
        "",
        ":::{aviso} Clasificación automática, no lectura completa",
        f"Son **{len(filas)} transcripciones** ({sum(1 for x in filas if x[0]=='video')} de video y {sum(1 for x in filas if x[0]=='audio')} de audio). "
        "La clase de cada una se asignó con una **heurística por palabras clave** sobre el nombre y el inicio del texto, **no** leyendo cada archivo entero. Es un primer tamizado para encontrar lo técnico, no una revisión cerrada.",
        ":::",
        "",
        ":::{nota} Lo técnico, presentado para leer/ver",
        "Con el material candidato se armaron dos vistas más cómodas que el texto suelto:",
        "",
        "- **[Juntadas ilustradas](juntadas/index.html)** — las 5 sesiones de práctica más largas, con **fotogramas del video cada ~3 min + la transcripción de ese tramo** y enlace para reproducir el original.",
        "- **[Audios técnicos por sesión](audios/index.html)** — las 99 notas de voz técnicas **agrupadas por fecha**, cada una con **reproductor inline** y su transcripción.",
        "",
        "Las dos son **transcripción automática de sesiones en vivo** (voz sin atribuir), no tutoriales verificados.",
        ":::",
        "",
        "## Distribución por clase",
        "",
        "| Clase | Cantidad |",
        "|---|---|",
    ]
    for k, v in por_clase.most_common():
        L.append(f"| {k} | {v} |")
    L += [
        "",
        f"La mayoría son **demos de software o cracking/activación de programas comerciales** (p. ej. plugins de audio, suites), fuera del marco de esta guía, o **charla** no técnica. "
        f"Solo **{len(revs)}** se marcan como reversing/técnico; conviene abrirlas y confirmar antes de usarlas.",
        "",
        "## Candidatos reversing / técnico",
        "",
    ]
    if revs:
        for tipo, nombre, etiqueta, pal, clase, ruta in sorted(revs, key=lambda x: -x[3])[:80]:
            L.append(f"- **({tipo})** {etiqueta[:70]} — {{{{src:{ruta}|texto}}}} ({pal} palabras)")
    else:
        L.append("*(ninguna superó el umbral de palabras clave técnicas.)*")
    L += [
        "",
        f"El índice completo de las {len(filas)} transcripciones, con su clase y ruta, está en [telegram_indice.csv](telegram_indice.csv).",
    ]
    escribir("telegram.md", "\n".join(L))
    return len(filas), dict(por_clase), len(revs)


def main():
    n_ida, pal = gen_ida()
    print(f"IDA: {n_ida} tutes, {pal} palabras -> src/ida-tutes.md")
    tot, nc, ne = gen_teorias()
    print(f"Teorias: {tot} títulos ({nc} cracking / {ne} educativos) -> src/teorias.md")
    n_tel, clases, nr = gen_telegram()
    print(f"Telegram: {n_tel} transcripciones, {nr} reversing -> src/telegram.md")
    for k, v in sorted(clases.items(), key=lambda x: -x[1]):
        print(f"    {v:4d}  {k}")


if __name__ == "__main__":
    main()
