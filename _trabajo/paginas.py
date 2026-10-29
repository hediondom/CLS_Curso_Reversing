# -*- coding: utf-8 -*-
"""Genera las paginas de etapa, el indice del curso y las fichas de recursos.

Escribe Markdown en _trabajo/src; build.py lo convierte a HTML.
"""
import os
import textwrap

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
GUIA = os.path.dirname(os.path.dirname(SRC))  # .../CLS_Guia


def escribir(rel, texto):
    destino = os.path.join(SRC, rel)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(texto).strip() + "\n")


ETAPAS = [
    {
        "n": 0,
        "slug": "etapa-0",
        "titulo": "Laboratorio y método seguro",
        "objetivo": "Armar un entorno aislado, tomar snapshots, verificar hashes y registrar cada práctica con su alcance.",
        "horas": "4 a 6 horas",
        "prereq": "Ninguno.",
        "lecciones": [
            ("00-laboratorio.html", "Un laboratorio que podés romper sin miedo", "VM, snapshots, red aislada, transferencia por ISO y hashes."),
        ],
        "recursos": [
            ("../fichas/inventario-limpio.html", "Inventario limpio de CLS"),
            ("../fichas/transcripciones-telegram.html", "Transcripciones de Telegram"),
        ],
        "puerta": [
            "Mostrar una VM con snapshot limpia y red aislada.",
            "Transferir un archivo sin carpeta compartida y verificar su SHA-256 en host y guest.",
            "Escribir una bitácora con snapshot, programa, hash y observaciones.",
            "Explicar qué harías si el programa deja el sistema en un estado raro.",
        ],
        "errores": [
            "Usar carpeta compartida \"solo para pasar el archivo\".",
            "Tomar la snapshot después de copiar la muestra.",
            "Confundir una snapshot con un backup de los archivos del host.",
        ],
    },
    {
        "n": 1,
        "slug": "etapa-1",
        "titulo": "Fundamentos",
        "objetivo": "Leer un binario sencillo: números, memoria, procesos, formato PE y programas propios en C y Python.",
        "horas": "21 a 25 horas",
        "prereq": "Etapa 0.",
        "lecciones": [
            ("01-numeros.html", "Bits, bytes, hexadecimal y números con signo", "Binario, hex, complemento a dos, little-endian y VA→offset."),
            ("01-memoria.html", "Memoria: stack, heap y marcos de función", "Stack, prólogo/epílogo, argumentos y shadow space en x64."),
            ("01-procesos.html", "Procesos, hilos y mapa de memoria", "Procesos, hilos, handles, mapa de memoria y permisos."),
            ("01-pe.html", "El formato PE: cabeceras, secciones e imports", "Cabecera PE, secciones, IAT y ASLR."),
            ("01-c-python.html", "C y Python mínimos para analizar", "Programas propios en C y herramientas en Python."),
        ],
        "recursos": [
            ("../fichas/reversing-desde-cero.html", "Reversing desde cero (caps. 01–05)"),
            ("../fichas/python-iso.html", "Python ISO video tutes (lógica, no Python)"),
            ("../fichas/masm32-cayetano.html", "Curso de MASM32 (Videos 1–22)"),
        ],
        "puerta": [
            "Convertir valores entre binario, hex y decimal sin calculadora.",
            "Dibujar el stack de una función de 32 bits y explicar el de 64 bits.",
            "Calcular un file offset a partir de una VA y verificarlo en el archivo.",
            "Compilar un programa propio en C y leer su hash y cabecera PE.",
        ],
        "errores": [
            "Memorizar la tabla hexadecimal sin entender el valor posicional.",
            "Confundir dirección virtual con offset del archivo.",
            "Creer que el curso de Python de CLS enseña Python (enseña lógica).",
        ],
    },
    {
        "n": 2,
        "slug": "etapa-2",
        "titulo": "Introducción al reversing",
        "objetivo": "Leer assembly x86/x64, seguir el flujo y usar debugger y desensamblador con criterio. Se divide en 2A (base, 2.1–2.9), 2B (Windows intermedio, 2.10–2.16: ofuscación, TLS, MFC, huella, PE fino, anti-análisis, Ghidra) y 2C (Windows avanzado, 2.17+: packers didácticos, C++ profundo, WinDbg/heap, patch diffing, scripting). Las rutas de malware dinámico, shellcode/C2 y fuzzing quedan como optativas, fuera de la puerta obligatoria.",
        "horas": "32 a 40 h (2A) + ~25 h (2B) + ~30–40 h (2C avanzado)",
        "prereq": "Etapa 1.",
        "lecciones": [
            ("02-registros.html", "Registros, subregistros y flags", "Registros, solapamiento y flags ZF/SF/CF/OF."),
            ("02-instrucciones.html", "Instrucciones: mover, calcular y manipular bits", "MOV, LEA, aritmética, lógica, shifts y cadenas."),
            ("02-flotante.html", "Punto flotante y SSE: los registros xmm", "x87, SSE escalar (movsd/addsd/ucomisd) e IEEE 754."),
            ("02-flujo.html", "Flujo: comparar, saltar y repetir", "CMP/TEST, Jcc, CMOVcc, bucles y tablas de salto."),
            ("02-llamadas.html", "Llamadas, convenciones y marcos de función", "CALL/RET, cdecl/stdcall/fastcall y x64."),
            ("02-debugger.html", "El debugger: x64dbg de punta a punta", "Interfaz, F7/F8/F9, breakpoints y parcheo ético."),
            ("02-ida.html", "IDA y el análisis estático", "Strings, xrefs, grafo, rebase y decompilador."),
            ("02-optimizaciones.html", "Cómo cambia el código con optimizaciones", "Inlining, strength reduction, división por constante y tail calls."),
            ("02-herramientas.html", "Herramientas: del OllyDbg histórico al taller actual", "Qué usar para cada tarea y qué está discontinuado."),
            # --- Bloque 2B · Windows intermedio (edición 4) ---
            ("02-ofuscacion.html", "Ofuscación nativa: leer lo que no quiere ser leído", "Secciones invertidas, basura, saltos al medio y strings ocultas; hallar el bloque real."),
            ("02-tls.html", "TLS: código que corre antes de main", "Directorio TLS, AddressOfCallBacks y callbacks previos al entry point."),
            ("02-mfc.html", "MFC: llegar al handler cuando todo pasa por clases", "Reconocer MFC y alcanzar el handler de un control por el message map."),
            ("02-huella-compilador.html", "Huella de compilador: saber con qué se hizo", "MSVC, MinGW, Delphi, VB6 y MFC por imports, strings y runtime."),
            ("02-pe-fino.html", "PE fino: los directorios que cuentan la historia", "Rich header, recursos, delay-load, .pdata, debug/PDB y Load Config."),
            ("02-anti-analisis.html", "Taxonomía anti-análisis: reconocer, no evadir", "Anti-debug, anti-VM, anti-disassembly y anti-dump: detectarlos."),
            ("02-ghidra.html", "Ghidra (y Cutter): la alternativa libre, con práctica", "El recorrido de IDA replicado en Ghidra: autoanálisis, strings, tipos y decompilador."),
            # --- Bloque 2C · Windows avanzado (edición 5) ---
            ("02-packers.html", "Packers didácticos: UPX, stub, OEP, dump e IAT", "Desempaquetado didáctico de UPX sobre binarios propios; llegar al OEP y reconstruir la IAT."),
            ("02-cpp-profundo.html", "C++ profundo: RTTI, vtables, STL y excepciones", "RTTI, std::string con SSO, contenedores STL y manejo de excepciones."),
            ("02-windbg-heap.html", "WinDbg, TTD y heap", "WinDbg, time-travel debugging y diagnóstico de heap (Page Heap, LFH)."),
            ("02-patch-diffing.html", "Patch diffing y CVE: leer qué cambió", "BinDiff/Diaphora: comparar dos versiones y leer qué arregló un parche (defensivo)."),
            ("02-scripting-debugger.html", "Scripting de debugger: automatizar y dejar evidencia", "Automatizar x64dbg (breakpoints, logs) y guardar evidencia; OllyScript como legado."),
            # --- 2C · rutas optativas (fuera de la puerta obligatoria) ---
            ("02-opt-malware-dinamico.html", "(optativa) Malware dinámico defensivo", "Laboratorio aislado, red simulada, observación de comportamiento e IOCs."),
            ("02-opt-shellcode-c2.html", "(optativa) Shellcode, red y C2: reconocer y describir", "Identificar shellcode y describir tráfico de C2; análisis y clasificación, no construcción."),
            ("02-opt-fuzzing.html", "(optativa) Fuzzing y análisis simbólico", "Fuzzear un parser/crackme propio y usar ejecución simbólica para hallar condiciones."),
        ],
        "recursos": [
            ("../2d.html", "Etapa 2 · Rama optativa 2D — Windows internals (después de 2C)"),
            ("../fichas/reversing-desde-cero.html", "Reversing desde cero (tronco principal)"),
            ("../fichas/ida-desde-cero.html", "Curso IDA desde cero (69 documentos)"),
            ("../fichas/ollydbg-cayetano.html", "Curso de OllyDbg (Videos 23–40)"),
            ("../fichas/ida-pro-docx.html", "Introducción al reversing con IDA Pro (docx)"),
        ],
        "puerta": [
            "**2A** · Explicar qué hace un bloque de 10 instrucciones y qué flags cambia.",
            "**2A** · Reconstruir un if/else y un bucle a partir del listado.",
            "**2A** · Poner los tres tipos de breakpoint y justificar cuál usar.",
            "**2A** · Sincronizar IDA y x64dbg por base o por file offset.",
            "**2B** · Reconocer tres señales de ofuscación y hallar el bloque real sin NOPear a ciegas.",
            "**2B** · Encontrar un TLS callback en el PE y demostrar que corre antes de `main`.",
            "**2B** · Llegar al handler de un control en un binario MFC por una API de texto y el call stack.",
            "**2B** · Identificar el compilador de un binario y navegar los directorios finos del PE (Rich header, Load Config, debug/PDB).",
            "**2B** · Clasificar una técnica anti-análisis y detectarla, y leer el mismo binario en IDA y en Ghidra.",
            "**2C** · Desempaquetar un UPX propio: llegar al OEP, dumpear, reconstruir la IAT y validar con `upx -d`.",
            "**2C** · Reconocer RTTI, `std::string` (SSO), un `std::vector` y un `try/catch` en un binario C++ propio.",
            "**2C** · Diagnosticar un bug de heap propio con WinDbg/Page Heap y leer, con un differ, qué cambió un parche.",
            "**2C** · Automatizar una tarea de análisis con un script de x64dbg y guardar la evidencia.",
        ],
        "errores": [
            "Confundir F7 con F8 y creer que F8 no ejecuta la función.",
            "Leer un salto al revés (pensar que el salto es la condición verdadera).",
            "Usar una copia ilegal de IDA Pro.",
            "Parchear software ajeno para saltar una licencia.",
        ],
    },
    {
        "n": 3,
        "slug": "etapa-3",
        "titulo": ".NET como primera victoria",
        "objetivo": "Entender el runtime .NET, leer IL y comparar fuente, IL y decompilación en un programa propio.",
        "horas": "7 a 10 horas",
        "prereq": "Etapa 2.",
        "lecciones": [
            ("03-dotnet-runtime.html", ".NET: runtime, ensamblados y metadatos", "CLR, IL, JIT, ensamblado y decompiladores."),
            ("03-dotnet-il.html", "Leer IL y comparar fuente, IL y decompilación", "Pila de evaluación, opcodes y reconstrucción."),
        ],
        "recursos": [
            ("../fichas/reversing-desde-cero.html", "Reversing desde cero (contexto de análisis)"),
            ("../fichas/teorias-numeradas.html", "Teorias_Numeradas (títulos .NET, pendiente)"),
        ],
        "puerta": [
            "Explicar C# → IL → JIT → CPU.",
            "Leer un método IL de 20 instrucciones y decir qué devuelve.",
            "Compilar Debug y Release y marcar tres diferencias.",
            "Reconocer señales de ofuscación.",
        ],
        "errores": [
            "Creer que el decompilador devuelve el código fuente exacto.",
            "Asumir que .NET es inseguro por naturaleza.",
            "Analizar software comercial para saltar licencias.",
        ],
    },
    {
        "n": 4,
        "slug": "etapa-4",
        "titulo": "Práctica guiada",
        "objetivo": "Analizar programas propios con método, reconstruir un formato o protocolo desde muestras, contener la ejecución y escribir un informe reproducible.",
        "horas": "19 a 25 horas",
        "prereq": "Etapas 0 a 3.",
        "lecciones": [
            ("04-metodo.html", "Método de análisis: de la pregunta al hallazgo", "Ciclo de cinco pasos, hipótesis y confirmación."),
            ("04-formatos-protocolos.html", "Reconstruir formatos y protocolos propios", "Campos, longitudes, framing, estados y transformaciones desde muestras controladas."),
            ("04-cripto.html", "Reconocer criptografía y encoding en un binario", "XOR, base64, constantes de AES/MD5/RC4 y CryptoAPI/CNG."),
            ("04-informe.html", "El informe reproducible", "Estructura, evidencia, límites y divulgación."),
            ("04-dinamico-seguro.html", "Análisis dinámico seguro: cuándo ejecutar y cuándo no", "Matriz de decisión, contención y respuesta."),
        ],
        "recursos": [
            ("../fichas/reversing-desde-cero.html", "Reversing desde cero (ejercicios 1 y 2)"),
            ("../fichas/inventario-limpio.html", "Inventario y estados de cuarentena"),
        ],
        "puerta": [
            "Analizar un programa propio de punta a punta sin mirar el fuente.",
            "Reconstruir desde muestras propias un formato binario o un framing simple, justificando campos, longitudes y estados.",
            "Confirmar una condición con breakpoints y valores concretos.",
            "Escribir un informe con hash, entorno, evidencia y límites.",
            "Explicar por qué el caso Shelter no es una práctica de principiante.",
        ],
        "errores": [
            "Parchear antes de entender.",
            "Ejecutar una muestra dudosa en el host.",
            "Escribir conclusiones sin evidencia.",
        ],
    },
    {
        "n": 5,
        "slug": "etapa-5",
        "titulo": "Ramas opcionales",
        "objetivo": "Elegir una especialización dentro de Windows, con prerrequisitos y práctica propia, sin convertir el corpus en una lista de tareas peligrosas.",
        "horas": "Variable: 5 a 10 horas por rama",
        "prereq": "Etapas 0 a 4 completas.",
        "lecciones": [
            ("05-malware.html", "Rama malware: análisis defensivo sin ejecutar", "Triage, IOCs, YARA y respuesta."),
            ("05-vulnerabilidades.html", "Rama vulnerabilidades: entender el defecto", "Desbordes, mitigaciones de Windows y divulgación."),
            ("05-automatizacion.html", "Rama automatización: scripts", "IDAPython, Ghidra, pefile y capstone."),
            ("05-fuera-de-alcance.html", "Kernel y otros territorios: qué queda fuera", "Límites explícitos, otras plataformas y prerequisites."),
        ],
        "recursos": [
            ("../2d.html", "2D · Windows internals (rama optativa)"),
            ("etapa-6.html", "Etapa 6 · Kernel y drivers (rama optativa, requiere base técnica específica)"),
            ("../fichas/exploiting-contenedores.html", "Exploiting (contenedores pendientes)"),
            ("../fichas/malware-virus.html", "Virus (excluido)"),
            ("../fichas/themida.html", "Themida (excluido)"),
        ],
        "puerta": [
            "Elegir una rama y completar su práctica con documentación.",
            "Explicar los prerrequisitos y los límites de esa rama.",
            "No ejecutar muestras ni usar técnicas de evasión fuera del marco.",
        ],
        "errores": [
            "Saltar a exploiting sin dominar stack y mitigaciones.",
            "Ejecutar malware para \"ver qué hace\".",
            "Confundir un contenedor sin revisar con una fuente leída.",
        ],
    },
    {
        "n": 6,
        "slug": "etapa-6",
        "titulo": "Rama optativa · Kernel y drivers",
        "optativa": True,
        "objetivo": "Comprender, construir y revisar un driver KMDF didáctico con una interfaz inocua, depurarlo solo en VM descartable y explicar mitigaciones actuales.",
        "horas": "45–65 horas como estimación inicial; puede requerir más tiempo si C, WinDbg o WDK son nuevos.",
        "prereq": "Etapa 0 (laboratorio aislado), C, assembly, memoria y sincronización, WinDbg y 2D.1 (objetos/tokens), 2D.2 (memoria/loader) y 2D.11 (excepciones/debugging). Etapa 2C es recomendada, no requisito; no hace falta completar toda 2D.",
        "lecciones": [
            ("6-01-arquitectura-kernel.html", "Arquitectura del kernel y modelo de E/S", "user/kernel mode, IRQL, pool, IRP, I/O Manager, sincronización y bugchecks."),
            ("6-02-kmdf-ioctl.html", "KMDF: driver propio con IOCTL inocuo", "KMDF/UMDF y una respuesta fija con permisos restrictivos; sin acceso arbitrario a memoria."),
            ("6-03-debug-kernel.html", "Debugging de kernel y bugchecks", "WinDbg en target VM, stacks/dumps y Driver Verifier con rollback."),
            ("6-04-revision-driver.html", "Revisión defensiva de un driver", "device interfaces, IOCTLs, SDDL y validación de entradas."),
            ("6-05-minifilters.html", "Minifilters y callbacks", "Pila de filesystem, callbacks pre/post y límites de observación."),
            ("6-06-mitigaciones.html", "Mitigaciones de Windows para drivers", "firma, Secure Boot, HVCI/VBS, WDAC y vulnerable driver blocklist."),
        ],
        "recursos": [
            ("../2d.html", "2D · Windows internals (solo lecciones requeridas para esta rama)"),
            ("../2d-hyperv.html", "Extensión Hyper-V (optativa, no requisito)"),
        ],
        "puerta": [
            "Explicar la ruta de una solicitud y los límites de IRQL, memoria y sincronización.",
            "Revisar un IOCTL propio de salida fija, con acceso limitado y validación completa; si no se puede cargar en VM conforme a la política vigente, entregar revisión estática.",
            "Leer un stack/dump de driver propio o muestra didáctica, indicando límites de símbolos y causalidad.",
            "Verificar mitigaciones en solo lectura y explicar qué protegen, sin desactivarlas.",
            "Demostrar rollback/limpieza de la VM; Driver Verifier no es requisito de aprobación.",
        ],
        "errores": [
            "Probar un driver en el equipo principal o desactivar protecciones para forzar su carga.",
            "Crear IOCTLs de lectura/escritura arbitraria o asumir que una ACL reemplaza la validación.",
            "Interpretar el módulo del bugcheck como causa raíz sin revisar stack y contexto.",
        ],
    },
]


def etapa_md(e):
    lineas = [
        "---",
        f'title: "Etapa {e["n"]} · {e["titulo"]}"',
        f'description: "{e["objetivo"]}"',
        f'etapa: "Etapa {e["n"]} · {e["titulo"]}"',
        "---",
        "",
        f'# Etapa {e["n"]} · {e["titulo"]}',
        "",
        f':::{{nota}} Objetivo medible',
        e["objetivo"],
        ":::",
        "",
        f'**Prerrequisitos:** {e["prereq"]}  ',
        f'**Duración estimada:** {e["horas"]}. Es una estimación de esta guía, derivada de la suma de las lecciones; no es una duración declarada por CLS.',
        "",
        "## Lecciones",
        "",
        "| # | Lección | Qué aprendés |",
        "|---|---|---|",
    ]
    if e.get("optativa"):
        idx = lineas.index("## Lecciones")
        lineas[idx:idx] = [
            "",
            ":::{aviso} Rama optativa; fuera de la aprobación obligatoria",
            "La Etapa 6 profundiza en kernel/drivers y no cambia los requisitos de las Etapas 0–4. Sus prácticas de carga requieren una VM descartable; nunca modifiques las protecciones del equipo principal.",
            ":::",
            "",
        ]
    for i, (arch, tit, resumen) in enumerate(e["lecciones"], 1):
        lineas.append(f'| {e["n"]}.{i} | [{tit}]({arch}) | {resumen} |')
    lineas += [
        "",
        "## Recursos de CLS para esta etapa",
        "",
    ]
    for href, label in e["recursos"]:
        lineas.append(f"- [{label}]({href})")
    lineas += [
        "",
        "## Evaluación de salida",
        "",
    ]
    for p in e["puerta"]:
        lineas.append(f"- {p}")
    lineas += [
        "",
        ":::{practica} Entregable de la etapa",
        "Un archivo en tu bitácora con: lecciones completadas, ejercicios resueltos, dudas abiertas y evidencia (capturas, valores, hashes). Sin evidencia no se considera aprobada.",
        ":::",
        "",
        "## Errores frecuentes",
        "",
    ]
    for x in e["errores"]:
        lineas.append(f"- {x}")
    lineas += [
        "",
        "## Qué no entra en esta etapa",
        "",
        "Los temas que no tienen material revisado o que exceden el marco se listan en [Kernel y otros territorios](05-fuera-de-alcance.html). No los uses como atajo: cada rama tiene prerrequisitos.",
        "",
        ":::nota Volver",
        "[Mapa del curso](index.html) · [Inicio](../00_EMPEZAR_AQUI.html)",
        ":::",
    ]
    return "\n".join(lineas)


def indice_md():
    lineas = [
        "---",
        'title: "Mapa del curso"',
        'description: "Siete etapas numeradas: recorrido obligatorio 0–4 y ramas optativas 5–6, más la rama 2D."',
        "---",
        "",
        "# Mapa del curso",
        "",
        "El recorrido obligatorio son las Etapas 0–4. Las Etapas 5–6 y la rama 2D son optativas y no agregan requisitos para completar el curso base. Cada rama tiene prerrequisitos y una puerta de salida propios.",
        "",
        "| Etapa | Foco | Horas estimadas | Lecciones |",
        "|---|---|---|---|",
    ]
    for e in ETAPAS:
        lineas.append(f'| **{e["n"]}** | [{e["titulo"]}]({e["slug"]}.html) | {e["horas"]} | {len(e["lecciones"])} |')
    lineas += [
        "",
        "## Cómo estudiar",
        "",
        "1. Leé la lección completa, sin saltear los ejemplos.",
        "2. Hacé la práctica en el laboratorio; no solo leas.",
        "3. Respondé las preguntas **antes** de abrir las respuestas.",
        "4. Verificá la puerta de salida. Si no la pasás, repetí la práctica.",
        "5. Anotá en `seguimiento.csv` qué hiciste, cuánto tardaste y qué duda quedó.",
        "",
        "## Qué es cada etapa",
        "",
    ]
    for e in ETAPAS:
        lineas += [
            f'### Etapa {e["n"]} · {e["titulo"]}',
            "",
            e["objetivo"],
            "",
            f'Prerrequisitos: {e["prereq"]}',
            "",
        ]
    lineas += [
        "## Material de apoyo",
        "",
        "- [Índice de videotutoriales](../videos.html): dónde está en Windows cada video que menciona el curso, con enlace y ruta absoluta.",
        "- [Curso IDA desde cero (69 tutoriales)](../ida-tutes.html): índice por tema, con el texto extraído de cada uno.",
        "- [Teorias_Numeradas clasificadas](../teorias.html): los 2.017 títulos separados en educativos vs cracking de software comercial.",
        "- [Transcripciones de Telegram por tema](../telegram.html): las 523 transcripciones tamizadas; dónde están las sesiones de práctica.",
        "- [Fichas de recursos](../fichas/index.html): qué se revisó, qué falta y qué límites tiene cada fuente.",
        "- [Glosario](../glosario.html): términos en lenguaje de principiante.",
        "- [Preguntas y respuestas](../preguntas_y_respuestas.html): repaso por etapa.",
        "- [Fuentes y límites](../fuentes_y_limites.html): criterios, cobertura y exclusiones.",
        "",
        "## Dónde seguir practicando (legal y seguro)",
        "",
        "Esta guía practica con **programas propios**, pero conviene seguir con retos pensados para aprender. Estos recursos son **recomendación externa** (no salen del corpus CLS) y permiten practicar reversing de Windows sin problemas legales:",
        "",
        "- [crackmes.one](https://crackmes.one/): miles de crackmes subidos para aprender; filtrá por plataforma **Windows** y por dificultad. Analizalos en tu VM.",
        "- [Flare-On Challenge](https://flare-on.com/): competencia anual y gratuita de reversing, centrada en Windows; los retos de años anteriores quedan publicados con soluciones.",
        "- **CTFs (categoría rev)**: [CTFtime](https://ctftime.org/) lista competencias; muchos retos de reversing son binarios de Windows. Buenísimos para practicar con límite de tiempo.",
        "- **Talleres abiertos**: materiales públicos de análisis de malware y reversing (por ejemplo, [OALabs](https://www.openanalysis.net/) o Malware Unicorn) con binarios de práctica.",
        "- **Tus propios programas**: seguí compilando ejemplos con condiciones cada vez más complejas; es la práctica más segura y la que más enseña.",
        "",
        "Regla que no cambia: todo en la VM aislada de la Etapa 0, y nada de software ajeno sin permiso.",
        "",
    ]
    return "\n".join(lineas)


FICHAS = [
    {
        "slug": "reversing-desde-cero",
        "titulo": "Reversing desde cero (Ricardo Narvaja y Solid)",
        "autor": "Ricardo Narvaja y Solid (según títulos y audio)",
        "tipo": "Curso en video con transcripción y subtítulos (47 capítulos)",
        "ruta": "CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)",
        "etapa": "2 (tronco); apoya 1 y 4",
        "nivel": "Principiante a intermedio",
        "prereq": "Etapas 0 y 1",
        "estado": "Revisado parcial: 38 de 47 capítulos leídos o digeridos con cita verificada",
        "leido": "Ofuscación (26, 30), TLS (38) y MFC (39) quedaron integrados en el bloque **2B · Windows intermedio** (lecciones 2.10–2.12). Siguen **excluidos por criterio** (desempaquetado de protectores comerciales, fuera del recorrido base) 5 capítulos: 13 y 17 (unpacking/OEP) y 27, 29, 31 (AcProtect). El resto está citado en las lecciones; el detalle por capítulo está en `registro_de_cobertura.csv`.",
        "contenido": "x64dbg, registros y flags, instrucciones, PE (VA/RVA/offset), IDA, stack y convenciones, ejercicios de análisis dinámico y estático, anti-debug, ofuscación, ASLR, TLS, excepciones y tips de C++/MFC.",
        "utilidad": "Es el mejor material en español para el recorrido base: progresivo, con ejemplos numéricos y ejercicios. Usa x64dbg (vigente) y contrasta con IDA.",
        "limites": "Transcripción ASR con errores en mnemónicos y números; algunos capítulos avanzados son desempaquetado de protectores comerciales y quedan fuera del recorrido base. No todos los capítulos tienen la misma calidad.",
        "duracion": "28,6 h (53 segmentos según _progreso.csv; los 47 capítulos incluyen cortes y apéndices)",
        "referencias": [
            ("CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_03 Registros, Flags y Números_03 Registros, Flags y Números.txt", "Cap. 03, registros y números"),
            ("CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_05 Virtual Adress, RVA, Offsets y Desplazamientos_05 Virtual Adress, RVA, Offsets y Desplazamientos.txt", "Cap. 05, VA/RVA/offset"),
            ("CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_18 Funciones basadas en EBP vs basadas en ESP_18 Funciones basadas en EBP vs basadas en ESP.txt", "Cap. 18, stack y convenciones"),
            ("CLS_resultados_intermedios/transcripciones/_progreso.csv", "Duraciones por capítulo"),
        ],
    },
    {
        "slug": "ida-desde-cero",
        "titulo": "Curso IDA desde cero (69 tutoriales)",
        "autor": "Ricardo Narvaja (según el índice y el documento de la parte 1)",
        "tipo": "69 documentos .docx + 47 PDF en inglés + índice",
        "ruta": "CLS_fuentes_externas/github/apuromafo_Crackslatinos/IDA DESDE CERO/CURSO DE IDA TUTES",
        "etapa": "2",
        "nivel": "Principiante a avanzado",
        "prereq": "Etapa 2 (assembly, PE)",
        "estado": "Revisado: texto extraído de los 69 tutes e indexado por tema (ver índice)",
        "leido": "Se extrajo el texto de los 69 .docx (~122.000 palabras) y se armó un índice por tema: ver [Curso IDA desde cero · índice](../ida-tutes.html). Los 47 PDF en inglés y los exámenes no se procesaron.",
        "contenido": "Curso de 69 partes: base de IDA e instrucciones (1–13), desempaquetado de packers (14–18), crackmes y ejercicios (19–24), estructuras (25–28), CVEs reales y exploiting user-mode (29–48, p. ej. VLC CVE-2008-4654, DEP, Mona, canary/SEH, shellcode, heap, integer overflow) y kernel de Windows (49–69).",
        "utilidad": "El material de IDA más completo del corpus. Los tutes 1–28 complementan el recorrido base; de 29 en adelante es vulnerabilidades/exploiting/kernel (avanzado, defensivo).",
        "limites": "Los originales `.docx` traen capturas que no se extraen (solo el texto). La parte avanzada (exploiting/kernel) excede el recorrido base. Clasificación de alcance orientativa.",
        "duracion": "Desconocida: no hay marcas de tiempo; no se infiere de los títulos.",
        "referencias": [
            ("CLS_fuentes_externas/github/apuromafo_Crackslatinos/IDA DESDE CERO/INDICE.docx", "Índice del curso"),
            ("CLS_fuentes_externas/github/apuromafo_Crackslatinos/IDA DESDE CERO/CURSO DE IDA TUTES/1-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.docx", "Parte 1 (mismo texto que el docx de descargas_sueltas)"),
        ],
    },
    {
        "slug": "masm32-cayetano",
        "titulo": "Lenguaje ensamblador con MASM32 (Cayetano de Juan Úbeda)",
        "autor": "Cayetano de Juan Úbeda",
        "tipo": "22 videos con transcripción (Videos 1–22 de «Videos y material adicional»)",
        "ruta": "CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa",
        "etapa": "1–2",
        "nivel": "Principiante",
        "prereq": "Nociones de programación",
        "estado": "Revisado parcial: encabezados de los 22 y pasajes de varios; 13,6 h",
        "leido": "Se leyeron los encabezados y pasajes de los 22; completos los cortos (12, 22). El resto se muestreó.",
        "contenido": "MASM32, IDE EasyCode, ensamblador de 16 bits, registros de 32, tipos de datos, MOV, direccionamiento, transferencia de control, instrucciones de cadena, formularios, macros, APIs de Windows y depuración del propio ejecutable.",
        "utilidad": "Buena práctica de assembly en español, con programas propios. Complementa la teoría de registros e instrucciones del curso principal.",
        "limites": "MASM32 y EasyCode son herramientas de 32 bits con interfaz antigua; algunas APIs y ejemplos están desactualizados. No es un curso de reversing, es de programación en assembly.",
        "duracion": "13,6 h (suma de las duraciones de los últimos subtítulos)",
        "referencias": [
            ("CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video1_Video1.txt", "Video 1, presentación"),
            ("CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video5_Video5.txt", "Video 5, registros de 32 bits"),
            ("CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video21_Video21.txt", "Video 21, depuración del propio .exe"),
        ],
    },
    {
        "slug": "ollydbg-cayetano",
        "titulo": "Introducción al reversing con OllyDbg (Cayetano de Juan Úbeda)",
        "autor": "Cayetano de Juan Úbeda",
        "tipo": "18 videos con transcripción (Videos 23–40)",
        "ruta": "CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa",
        "etapa": "2",
        "nivel": "Principiante a intermedio",
        "prereq": "Assembly básico",
        "estado": "Revisado parcial: encabezados y pasajes; ejecuta malware en el video 37",
        "leido": "Se leyeron encabezados y pasajes de los 18; completos los cortos (23, 33, 34, 39, 40). El video 37 se leyó en su introducción y en pasajes clave.",
        "contenido": "OllyDbg, programas propios en assembly, variables y estructuras, procedimientos, condicionales, bucles, formularios, PE, APIs de malware, crackme, XOR, malware Shelter, .NET/MSIL, ExeInfoPE y .NET Reflector.",
        "utilidad": "Muestra el método de análisis con un debugger histórico y cubre PE, XOR y .NET desde la práctica. Útil para entender conceptos, no la interfaz actual.",
        "limites": "OllyDbg es de 32 bits y no se actualiza. El video 37 ejecuta malware y monta un reverse shell en VMs: es un caso observado, no una práctica recomendada. El video 36 inyecta una backdoor de Metasploit.",
        "duracion": "9,7 h (suma de duraciones de los últimos subtítulos)",
        "referencias": [
            ("CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video24_Video24.txt", "Video 24, OllyDbg"),
            ("CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video33_Video33.txt", "Video 33, PE"),
            ("CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video37_Video37.txt", "Video 37, Shelter"),
            ("CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video38_Video38.txt", "Video 38, .NET/MSIL"),
        ],
    },
    {
        "slug": "python-iso",
        "titulo": "Python ISO video tutes (Daniel Bermúdez)",
        "autor": "Daniel Bermúdez (Bogotá); fuente declarada: libro de Omar Iván Trejos Buriticá",
        "tipo": "55 transcripciones de video (165 segmentos) sobre lógica de programación",
        "ruta": "CLS_resultados_intermedios/transcripciones/extraidos/Python ISO video tutes",
        "etapa": "1",
        "nivel": "Principiante",
        "prereq": "Ninguno",
        "estado": "Revisado parcial: 20 archivos completos y 2 parciales; el resto por encabezado",
        "leido": "20 archivos completos (Qué es Python, Historia, Fundamentos, Algoritmos, Metodología, Estructuras, Variables, Decisiones, Ciclos, Arreglos, Matrices/Funciones) y 2 parciales; 33 solo por encabezado.",
        "contenido": "Lógica de programación, algoritmos, secuencia/decisión/ciclo, arreglos, matrices, funciones y prueba de escritorio, con pseudocódigo y ejemplos en Basic, Pascal y C.",
        "utilidad": "Sirve como base de lógica y algoritmos, especialmente para quien nunca programó. No enseña Python.",
        "limites": "No contiene código Python ejecutable; usa Python 2.5.1 (2007) como referencia y `print` como sentencia. Faltan los temas avanzados que el autor anuncia. No reemplaza un curso de Python 3.",
        "duracion": "12,7 h (165 segmentos según _progreso.csv)",
        "referencias": [
            ("CLS_resultados_intermedios/transcripciones/extraidos/Python ISO video tutes/Videotutoriales_QueesPython_QueesPython.txt", "Qué es Python"),
            ("CLS_resultados_intermedios/transcripciones/extraidos/Python ISO video tutes/Videotutoriales_HistoriaPython_HistoriaPython.txt", "Historia y versiones"),
            ("CLS_resultados_intermedios/transcripciones/extraidos/Python ISO video tutes/Videotutoriales_Arreglos1_Arreglos1.txt", "Arreglos"),
        ],
    },
    {
        "slug": "reverse-engineering-ricardo",
        "titulo": "Reverse engineering con Ricardo Narvaja (video suelto)",
        "autor": "Ricardo Narvaja (entrevista/stream)",
        "tipo": "1 video con transcripción (1,9 h)",
        "ruta": "CLS_resultados_intermedios/transcripciones/extraidos/Reverse engineering con Ricardo Narvaja",
        "etapa": "Transversal (orientación)",
        "nivel": "Principiante",
        "prereq": "Ninguno",
        "estado": "Revisado parcial: inicio, búsqueda temática y final",
        "leido": "Se leyó el inicio (letra de una canción), se buscaron temas y se leyó el final. No es un tutorial técnico.",
        "contenido": "Aproximadamente la primera hora es música/intro de stream; desde ~01:01 hay una conversación sobre la profesión del reversing: salidas laborales, formación, experiencia y mercado.",
        "utilidad": "Contexto vocacional y motivacional. No aporta técnica paso a paso.",
        "limites": "No es un curso. No se debe citar como fuente de conceptos técnicos ni usar como práctica.",
        "duracion": "1,9 h",
        "referencias": [
            ("CLS_resultados_intermedios/transcripciones/extraidos/Reverse engineering con Ricardo Narvaja/Reverse engineering con Ricardo Narvaja.txt", "Transcripción completa"),
            ("CLS_resultados_intermedios/transcripciones/extraidos/Reverse engineering con Ricardo Narvaja/Reverse engineering con Ricardo Narvaja.srt", "Subtítulos con timestamps"),
        ],
    },
    {
        "slug": "teorias-numeradas",
        "titulo": "Teorias_Numeradas (colección de tutoriales)",
        "autor": "Múltiples autores de la comunidad CLS",
        "tipo": "2.023 contenedores (.rar, .zip, .7z) organizados por número, ~3,5 GB",
        "ruta": "CLS_fuentes_externas/github/apuromafo_Crackslatinos/Teorias_Numeradas",
        "etapa": "4 (referencia); gran parte fuera del recorrido",
        "nivel": "Variable",
        "prereq": "Variable",
        "estado": "Clasificado por título: 2.017 tutoriales separados en educativos vs cracking (ver índice)",
        "leido": "Se clasificaron los 2.017 títulos por categoría: ver [Teorias_Numeradas clasificadas](../teorias.html). ~1.591 (79%) apuntan a cracking de software comercial; ~426 son candidatos educativos. No se abrió ningún contenedor (varios con contraseña).",
        "contenido": "Tutoriales de todos los niveles: teoría básica, assembler, .NET/Java/VB, herramientas, crackmes, criptografía, y gran parte sobre cracking/unpacking/seriales de software comercial.",
        "utilidad": "Índice para localizar un tema; el filtrado por título ayuda a descartar el ~79% de cracking comercial. No es un curso secuencial.",
        "limites": "Clasificación **por título, no por contenido**: un título no demuestra lo que enseña. No se abrió ningún .zip. No presentar como leído.",
        "duracion": "Desconocida por archivo; el CSV tiene tamaños, no duraciones.",
        "referencias": [
            ("CLS_resultados_intermedios/teorias_numeradas_por_etapa.csv", "Listado de 2.023 títulos con etapa y ruta"),
        ],
    },
    {
        "slug": "ida-pro-docx",
        "titulo": "Introducción al reversing con IDA Pro desde cero (parte 1)",
        "autor": "Ricardo Narvaja",
        "tipo": "Documento .docx de 51 párrafos (2016), con capturas",
        "ruta": "descargas_sueltas/INTRODUCCIÓN AL REVERSING CON IDA PRO DESDE CERO.docx",
        "etapa": "2",
        "nivel": "Principiante",
        "prereq": "Assembly y PE básicos",
        "estado": "Revisado: texto extraído y leído",
        "leido": "Se extrajo el texto completo (7.620 caracteres) y se leyó. Es la parte 1 de una serie.",
        "contenido": "Por qué IDA frente a OllyDbg, cómo distinguir PE32/PE32+ por la cabecera, Quick Start, proximity view, grafo, prefijos de línea y opcodes, loader vs debugger, guardar desktop, strings, imports, hex dump, graph overview y colores de la barra de navegación.",
        "utilidad": "Introducción escrita y compacta a la interfaz de IDA, útil como complemento del capítulo 14.",
        "limites": "Es de 2016 (IDA 6.8, Windows 10 Anniversary), recomienda descargar IDA Pro 6.8 de Google con contraseña y menciona Python 2.7.6. Esas instrucciones **no se siguen**: usar IDA Free/Ghidra y Python 3. La interfaz cambió.",
        "duracion": "No declarada; lectura estimada 40–60 minutos",
        "referencias": [
            ("descargas_sueltas/INTRODUCCIÓN AL REVERSING CON IDA PRO DESDE CERO.docx", "Documento original"),
            ("CLS_Guia/_trabajo/extraido/INTRODUCCIÓN AL REVERSING CON IDA PRO DESDE CERO.txt", "Texto extraído para lectura"),
        ],
    },
    {
        "slug": "inventario-limpio",
        "titulo": "Inventario limpio de CLS",
        "autor": "Proyecto CLS (sesión previa)",
        "tipo": "CSV de 8.154 filas, hashes SHA-256, resumen JSON y listado de comprimidos",
        "ruta": "CLS_resultados_intermedios/inventario_limpio",
        "etapa": "0 y transversal",
        "nivel": "No aplica",
        "prereq": "Ninguno",
        "estado": "Revisado: LEEME, resumen y muestreo del CSV",
        "leido": "LEEME.md, _resumen.json, estructura del CSV y consultas por tipo/fuente/estado. No se recorrieron las 8.154 filas una por una.",
        "contenido": "Una fila por archivo en disco, con estado (`util`, `cuarentena`, `excluido`, `duplicado`, `descartado`), tipo, fuente, tamaño, fecha, autor, ID de mensaje, hash y ruta.",
        "utilidad": "Mapa maestro para localizar material y entender la clasificación. Es la fuente de conteos de esta guía.",
        "limites": "`util` no implica seguridad, calidad ni vigencia. Es el inventario vigente (26/10/2026), distinto del histórico de `CLS_resultados` (6.499 filas, 24/10/2026).",
        "duracion": "No aplica",
        "referencias": [
            ("CLS_resultados_intermedios/inventario_limpio/LEEME.md", "LEEME del inventario"),
            ("CLS_resultados_intermedios/inventario_limpio/CLS_inventario_limpio.csv", "Inventario"),
            ("CLS_resultados_intermedios/inventario_limpio/_comprimidos.csv", "Listado de comprimidos"),
        ],
    },
    {
        "slug": "chat-unido",
        "titulo": "Chat unido de CLS",
        "autor": "Comunidad CLS",
        "tipo": "JSON de 100.791 mensajes (2016-01-18 a 2026-10-26)",
        "ruta": "CLS_resultados_intermedios/inventario_limpio/CLS_chat_unido.json",
        "etapa": "Transversal (referencia)",
        "nivel": "No aplica",
        "prereq": "Ninguno",
        "estado": "Revisado como índice: metadatos y muestras, no mensaje por mensaje",
        "leido": "Se verificaron totales, estructura y campos; se consultaron mensajes por archivo y por tema. No se leyó completo.",
        "contenido": "Conversaciones del grupo, con referencias a archivos, enlaces y decisiones. Cada mensaje con archivo apunta a la ruta real en disco.",
        "utilidad": "Rastrear el origen de un recurso y el contexto de una decisión. No es material didáctico por sí mismo.",
        "limites": "Volumen enorme; las menciones no demuestran el contenido de un recurso. No se usa como fuente de conceptos.",
        "duracion": "No aplica",
        "referencias": [
            ("CLS_resultados_intermedios/inventario_limpio/CLS_chat_unido.json", "Chat unido"),
        ],
    },
    {
        "slug": "transcripciones-telegram",
        "titulo": "Transcripciones de videos y audios de Telegram",
        "autor": "Varios autores del grupo",
        "tipo": "179 videos transcritos (76,5 h) y 357 audios (2,7 h)",
        "ruta": "CLS_resultados_intermedios/transcripciones/telegram_videos y telegram_audios",
        "etapa": "5 / referencia",
        "nivel": "Variable",
        "prereq": "Variable",
        "estado": "Clasificadas por tema (heurística): 523 transcripciones tamizadas (ver índice)",
        "leido": "Se clasificaron las 523 transcripciones por palabras clave: ver [Transcripciones de Telegram por tema](../telegram.html). ~344 son charla/demo/no técnico, ~54 cracking de software comercial y ~125 reversing/técnico (entre ellas, las sesiones de práctica y 'juntadas' grabadas).",
        "contenido": "Mezcla de demos de software comercial, cracking, charla y, lo valioso, sesiones de práctica de reversing ('juntadas', ejercicios compartidos). Los audios tienen rutas `File not included` en el JSON original.",
        "utilidad": "El tamizado encuentra las sesiones técnicas largas (juntadas/ejercicios) entre cientos de archivos no relevantes.",
        "limites": "Clasificación **automática por palabras clave**, no lectura completa. La voz no está atribuida con certeza. Hay que abrir las candidatas para confirmar.",
        "duracion": "79,2 h en total",
        "referencias": [
            ("CLS_resultados_intermedios/transcripciones/_progreso.csv", "Duraciones y estado"),
            ("CLS_resultados_intermedios/transcripciones/_lista.csv", "Índice con autor y ruta"),
            ("CLS_resultados_intermedios/CLS_resultados/transcripciones_PENDIENTES.md", "Nota sobre audios no incluidos"),
        ],
    },
    {
        "slug": "scenere-docs",
        "titulo": "SceneRE · docs/CursoReversing-desde-cero",
        "autor": "SceneRE / CrackSLatinoS",
        "tipo": "47 páginas Markdown (~450 bytes cada una)",
        "ruta": "CLS_fuentes_externas/github/SceneRE_CrackSLatinoS/docs/CursoReversing-desde-cero",
        "etapa": "2 (índice)",
        "nivel": "No aplica",
        "prereq": "Ninguno",
        "estado": "Revisado: son solo incrustaciones de YouTube",
        "leido": "Se abrieron y compararon las páginas: contienen título e iframe, no texto didáctico.",
        "contenido": "Índice de videos del mismo curso. No aporta explicaciones propias.",
        "utilidad": "Sirve para mapear capítulos a videos. El contenido real está en las transcripciones.",
        "limites": "No es fuente de texto. El borrador anterior lo citaba como si enseñara; esta edición lo corrige.",
        "duracion": "No aplica",
        "referencias": [
            ("CLS_fuentes_externas/github/SceneRE_CrackSLatinoS/docs/CursoReversing-desde-cero/001-x64dbg-primeros-pasos.md", "Página 001"),
            ("CLS_fuentes_externas/github/SceneRE_CrackSLatinoS/docs/CursoReversing-desde-cero/003-registros-flags-y-numeros.md", "Página 003"),
        ],
    },
    {
        "slug": "exploiting-contenedores",
        "titulo": "Exploiting (contenedores)",
        "autor": "Comunidad CLS / varios",
        "tipo": "Carpetas con .rar y material de cursos",
        "ruta": "CLS_fuentes_externas/github/apuromafo_Crackslatinos/EXPLOITING",
        "etapa": "5",
        "nivel": "Avanzado",
        "prereq": "Etapas 0–4, memoria, mitigaciones",
        "estado": "Pendiente de revisar: no se extrajo",
        "leido": "Solo se verificó la existencia y el tamaño. No se abrió.",
        "contenido": "Según el mapa, cursos de exploiting básico, medio y avanzado. Material de otras plataformas (ARM) queda fuera del alcance Windows de esta guía. **No verificado.**",
        "utilidad": "Referencia para una rama avanzada con laboratorio autorizado.",
        "limites": "No se usa como práctica: el exploiting contra terceros está fuera del alcance. No se ejecutan binarios.",
        "duracion": "Desconocida",
        "referencias": [
            ("CLS_fuentes_externas/github/apuromafo_Crackslatinos/EXPLOITING", "Carpeta"),
            ("CLS_fuentes_externas/mega_OTROS/OTROS", "Material adicional"),
        ],
    },
    {
        "slug": "malware-virus",
        "titulo": "Virus y programación de virus (excluido)",
        "autor": "Varios (material antiguo)",
        "tipo": "Carpetas con documentos y binarios",
        "ruta": "CLS_fuentes_externas/mega_OTROS/OTROS",
        "etapa": "Fuera de alcance",
        "nivel": "Avanzado / riesgoso",
        "prereq": "No corresponde",
        "estado": "Excluido: no se lee ni se ejecuta",
        "leido": "Solo se verificó la existencia por el mapa. No se abrió.",
        "contenido": "Material antiguo de virus y programación de virus. **No revisado y no recomendado.**",
        "utilidad": "Ninguna para el recorrido base. La rama de malware de esta guía usa triage estático defensivo, no este material.",
        "limites": "Riesgo legal y de seguridad. Se respeta la clasificación del inventario y no se ejecuta.",
        "duracion": "No aplica",
        "referencias": [
            ("CLS_resultados_intermedios/mapa_carpetas_etapas.csv", "Clasificación como material viejo, solo VM"),
            ("CLS_resultados_intermedios/inventario_limpio/LEEME.md", "Estados de cuarentena y exclusión"),
        ],
    },
    {
        "slug": "themida",
        "titulo": "Themida + WinLicense 2.x (Unpacking)",
        "autor": "Desconocido",
        "tipo": "Archivo .rar de ~51 MB",
        "ruta": "telegram/Themida + WinLicense 2.x (Unpacking).rar",
        "etapa": "Fuera de alcance",
        "nivel": "Avanzado",
        "prereq": "No corresponde",
        "estado": "Excluido: no se extrae ni se usa",
        "leido": "Solo se verificó la existencia y el tamaño. No se abrió.",
        "contenido": "Desempaquetado de un protector comercial. **No revisado.**",
        "utilidad": "Ninguna para el recorrido base.",
        "limites": "Fuera del marco legal y ético de esta guía. No se enseña a eludir protecciones comerciales.",
        "duracion": "No aplica",
        "referencias": [
            ("telegram/Themida + WinLicense 2.x (Unpacking).rar", "Archivo"),
        ],
    },
    {
        "slug": "zips-anteriores",
        "titulo": "zips_anteriores (resultados históricos)",
        "autor": "Proyecto CLS (sesiones previas)",
        "tipo": "4 .zip y una carpeta con resultados de análisis anteriores",
        "ruta": "zips_anteriores",
        "etapa": "Histórico",
        "nivel": "No aplica",
        "prereq": "Ninguno",
        "estado": "Histórico: reemplazado por el inventario limpio",
        "leido": "Se compararon tamaños y contenido con los resultados actuales. No se usan sus cifras.",
        "contenido": "Versiones anteriores de inventarios y análisis (418 KB a 2,2 MB).",
        "utilidad": "Trazabilidad de decisiones. No es fuente vigente.",
        "limites": "Puede estar desactualizado y contener cifras incompatibles. No se suman sus conteos a los actuales.",
        "duracion": "No aplica",
        "referencias": [
            ("zips_anteriores/cls_analisis_intermedios.zip", "Análisis previo"),
            ("zips_anteriores/CLS_resultados_intermedios.zip", "Resultados previos"),
            ("CLS_resultados_intermedios/inventario_limpio/LEEME.md", "Inventario vigente"),
        ],
    },
    {
        "slug": "exportacion-sesion",
        "titulo": "Exportación de la sesión anterior",
        "autor": "Sesión de trabajo previa",
        "tipo": "JSONL de ~10 MB y metadatos",
        "ruta": "exportacion_sesion/session-export-1793043392845",
        "etapa": "Transversal (decisiones)",
        "nivel": "No aplica",
        "prereq": "Ninguno",
        "estado": "Pendiente de revisar: no se leyó en esta edición",
        "leido": "Se verificaron tamaño y estructura. No se leyó la conversación.",
        "contenido": "Conversación previa que explica decisiones y requisitos del proyecto. **No verificada en detalle.**",
        "utilidad": "Puede aclarar por qué se tomó una decisión editorial.",
        "limites": "No es una fuente técnica. Las afirmaciones de una sesión anterior no se validan solas.",
        "duracion": "No aplica",
        "referencias": [
            ("exportacion_sesion/session-export-1793043392845/transcript.jsonl", "Transcripción"),
            ("exportacion_sesion/session-export-1793043392845/metadata.json", "Metadatos"),
        ],
    },
    {
        "slug": "plan-estudio-historico",
        "titulo": "CLS_plan_estudio.docx (plan histórico)",
        "autor": "Sesión previa del proyecto",
        "tipo": "Documento .docx de 6.714 caracteres de texto",
        "ruta": "CLS_resultados_intermedios/CLS_plan_estudio.docx",
        "etapa": "Histórico",
        "nivel": "No aplica",
        "prereq": "Ninguno",
        "estado": "Revisado: texto extraído y comparado con el estado actual",
        "leido": "Se extrajo y leyó el texto completo.",
        "contenido": "Plan de aprendizaje de 5 etapas basado en un `result.json` de 100.713 mensajes, con rutas `D:\\CLS` y sin medios. Estima 20–30 h para fundamentos, 35–50 h para reversing, etc.",
        "utilidad": "Muestra el estado del proyecto antes de tener los archivos en disco. Útil para entender la evolución.",
        "limites": "Supuestos superados: no había medios, usaba rutas `D:\\CLS`, y sus conteos (100.713 mensajes, 2.638 referencias) no coinciden con el inventario actual (100.791 mensajes, 8.154 archivos). No se usa como fuente vigente.",
        "duracion": "No aplica",
        "referencias": [
            ("CLS_resultados_intermedios/CLS_plan_estudio.docx", "Documento original"),
            ("CLS_Guia/_trabajo/extraido/CLS_plan_estudio.txt", "Texto extraído"),
        ],
    },
    {
        "slug": "curso-reversing-2020",
        "titulo": "Curso Reversing 2020",
        "autor": "Comunidad CLS (Solid)",
        "tipo": "Un .rar de ~5 MB y un .txt",
        "ruta": "CLS_fuentes_externas/github/apuromafo_Crackslatinos/CURSO REVERSING 2020",
        "etapa": "4",
        "nivel": "Intermedio",
        "prereq": "Etapa 2",
        "estado": "Pendiente de revisar: no se extrajo",
        "leido": "Solo se verificó la existencia. No se abrió.",
        "contenido": "Según el mapa, un curso con crackme de Solid. **No verificado.**",
        "utilidad": "Potencial para práctica guiada si se revisa.",
        "limites": "No se puede citar como leído. No se ejecuta sin revisar.",
        "duracion": "Desconocida",
        "referencias": [
            ("CLS_fuentes_externas/github/apuromafo_Crackslatinos/CURSO REVERSING 2020", "Carpeta"),
        ],
    },
]


def ficha_md(f):
    L = [
        "---",
        f'title: "{f["titulo"]}"',
        f'description: "Ficha del recurso: {f["tipo"]}"',
        "---",
        "",
        f'# {f["titulo"]}',
        "",
        "| Campo | Dato |",
        "|---|---|",
        f'| **Autor / organización** | {f["autor"]} |',
        f'| **Tipo** | {f["tipo"]} |',
        f'| **Ruta local** | `{f["ruta"]}` |',
        f'| **Etapa** | {f["etapa"]} |',
        f'| **Nivel** | {f["nivel"]} |',
        f'| **Prerrequisitos** | {f["prereq"]} |',
        f'| **Duración** | {f["duracion"]} |',
        f'| **Estado** | {f["estado"]} |',
        "",
        "## Qué se revisó",
        "",
        f["leido"],
        "",
        "## Contenido explicado",
        "",
        f["contenido"],
        "",
        "## Utilidad para el curso",
        "",
        f["utilidad"],
        "",
        "## Limitaciones y antigüedad",
        "",
        f["limites"],
        "",
        "## Referencias verificables",
        "",
    ]
    for ruta, label in f["referencias"]:
        L.append(f'- {{{{src:{ruta}|{label}}}}}')
    L += [
        "",
        ":::nota Volver",
        "[Índice de fichas](index.html) · [Mapa del curso](../guia/index.html) · [Inicio](../00_EMPEZAR_AQUI.html)",
        ":::",
    ]
    return "\n".join(L)


def fichas_indice():
    L = [
        "---",
        'title: "Fichas de recursos"',
        'description: "Qué se revisó de cada recurso de CLS, con estado, límites y referencias."',
        "---",
        "",
        "# Fichas de recursos",
        "",
        "Cada ficha describe un recurso del proyecto: qué es, para qué etapa sirve y, sobre todo, **si su contenido se revisó o sigue pendiente**. Una mención o un título no demuestran lo que enseña un recurso.",
        "",
        "| Recurso | Tipo | Estado |",
        "|---|---|---|",
    ]
    for f in FICHAS:
        L.append(f'| [{f["titulo"]}]({f["slug"]}.html) | {f["tipo"]} | {f["estado"]} |')
    L += [
        "",
        "## Cómo leer el estado",
        "",
        "- **Revisado:** se leyó el contenido y se puede citar.",
        "- **Revisado parcial:** se leyó una parte; la ficha dice qué falta.",
        "- **Pendiente de revisar:** solo se verificó la existencia o el título. No se usa como fuente de contenido.",
        "- **Excluido / fuera de alcance:** no se usa como práctica por riesgo o por marco legal.",
        "",
        "## Criterios",
        "",
        "Las rutas son relativas a la raíz del proyecto. Los enlaces abren el archivo local cuando existe; si no, la ficha lo aclara. No se copiaron binarios ni se extrajeron comprimidos para armar este paquete.",
        "",
        ":::nota Volver",
        "[Mapa del curso](../guia/index.html) · [Inicio](../00_EMPEZAR_AQUI.html) · [Fuentes y límites](../fuentes_y_limites.html)",
        ":::",
    ]
    return "\n".join(L)


def gen_seguimiento():
    """Escribe seguimiento.csv desde ETAPAS, para que nunca quede desfasado de las lecciones."""
    filas = ["etapa;leccion;fecha;horas;resultado;dudas;proximo_paso"]
    for e in ETAPAS:
        etiqueta = f"{e['n']} {e['titulo']}"
        for arch, _tit, _res in e["lecciones"]:
            filas.append(f"{etiqueta};guia/{arch};;;;;")
    with open(os.path.join(GUIA, "seguimiento.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(filas) + "\n")
    return sum(len(e["lecciones"]) for e in ETAPAS)


def main():
    for e in ETAPAS:
        escribir(f"guia/{e['slug']}.md", etapa_md(e))
    escribir("guia/index.md", indice_md())
    for f in FICHAS:
        escribir(f"fichas/{f['slug']}.md", ficha_md(f))
    escribir("fichas/index.md", fichas_indice())
    n_seg = gen_seguimiento()
    print(f"{len(ETAPAS)} etapas, 1 indice, {len(FICHAS)} fichas, seguimiento {n_seg} lecciones")


if __name__ == "__main__":
    main()






