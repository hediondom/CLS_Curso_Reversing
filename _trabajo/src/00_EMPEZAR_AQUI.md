---
title: "CLS · Curso de reversing"
description: "Portada del curso: cómo estudiar, qué se revisó, qué falta y por dónde empezar."
---

# De miles de mensajes a un curso que se puede estudiar

Este paquete convierte el material útil del proyecto **CLS** en un curso de reversing en español, progresivo y verificable. No es un índice ni una lista de enlaces: cada lección explica un concepto, lo conecta con lo anterior, muestra un ejemplo paso a paso, propone una práctica y te permite comprobar si aprendiste.

Está pensado para alguien que empieza, con un marco **educativo, defensivo y autorizado**. Las prácticas usan programas propios, software abierto o crackmes diseñados para aprender.

:::{nota} Empezá por acá
1. Leé esta portada completa (10 minutos).
2. Abrí el [Mapa del curso](guia/index.html) y elegí la Etapa 0.
3. Armá el laboratorio de la [lección 0.1](guia/00-laboratorio.html).
4. Estudiá una lección por vez y hacé la práctica antes de avanzar.
5. Anotá tu avance en [seguimiento.csv](seguimiento.csv).
:::

## Qué vas a poder hacer

Al terminar el recorrido base vas a poder:

- Explicar cómo se representa un programa en memoria y en disco.
- Leer assembly x86/x64 y reconstruir condiciones, bucles y llamadas.
- Usar x64dbg e IDA (o Ghidra) con un método, no a los botones.
- Analizar un programa .NET propio y comparar fuente, IL y decompilación.
- Escribir un informe reproducible con evidencia, límites y hashes.
- Decidir cuándo un programa se ejecuta y cuándo no.
- Reconocer código ofuscado, TLS callbacks, binarios MFC, la huella del compilador y técnicas anti-análisis, y leer el mismo binario en Ghidra (bloque **2B · Windows intermedio**).

## El curso: siete etapas numeradas y una rama 2D

Las **Etapas 0–4** forman el recorrido obligatorio. La **Etapa 5**, la **Etapa 6** y la rama optativa **2D · Windows internals** (asociada a la Etapa 2, después de 2C) no agregan requisitos para completar el curso base.

| Etapa | Foco | Horas estimadas | Puerta de salida |
|---|---|---|---|
| **0** | [Laboratorio y método seguro](guia/etapa-0.html) | 4–6 h | VM aislada, snapshot, hash y bitácora |
| **1** | [Fundamentos](guia/etapa-1.html) | 21–25 h | Números, memoria, PE y un programa propio en C |
| **2** | [Introducción al reversing](guia/etapa-2.html) | 32–40 h (2A) + ~25 h (2B) + ~30–40 h (2C) | Assembly, debugger e IDA; bloques **2B intermedio** y **2C avanzado** (+ 3 rutas optativas) |
| **3** | [.NET como primera victoria](guia/etapa-3.html) | 7–10 h | Leer IL y comparar tres vistas |
| **4** | [Práctica guiada](guia/etapa-4.html) | 14–18 h | Análisis completo + informe reproducible |
| **5** | [Ramas opcionales](guia/etapa-5.html) | variable | Una rama con práctica propia y límites claros |
| **6** | [Kernel y drivers (rama optativa)](guia/etapa-6.html) | 45–65 h estimadas | Revisar un driver propio y sus controles en VM aislada |

La profundización **Etapa 2 · Rama optativa 2D — Windows internals** tiene 13 lecciones (estimación editorial 55–70 h). Se muestra junto a la Etapa 2, pero queda fuera de sus requisitos obligatorios. La extensión Hyper-V también es optativa y separada.

Las horas son **estimaciones editoriales**, no mediciones de alumnos ni duraciones declaradas por CLS. Las de 2B/2C se estiman por bloque; 2D/Etapa 6 pueden requerir más tiempo según las prácticas y experiencia previa.

:::{nota} Cómo se cuentan las lecciones
La **Etapa 2** reúne 2A, 2B y 2C, además de 3 rutas optativas (2.22–2.24) que no son obligatorias. La rama optativa 2D se asocia a la Etapa 2 después de 2C y aporta 13 lecciones fuera de sus horas obligatorias. La Etapa 6 tiene 6 lecciones optativas. La extensión Hyper-V está fuera de ambos núcleos. El apartado 5.4 «Fuera de alcance» es una página de límites, no una lección a cursar.
:::

## Cómo estudiar

Cada lección tiene la misma estructura:

1. **Objetivo** y prerrequisitos.
2. **Explicación** con lenguaje sencillo y conexión con lo anterior.
3. **Ejemplo paso a paso**, con valores y direcciones cuando el material los aporta.
4. **Práctica** en el laboratorio.
5. **Preguntas de repaso** con respuestas razonadas.
6. **Puerta de salida**: qué tenés que poder hacer antes de avanzar.
7. **Fuentes**: rutas locales, capítulos y timestamps.

La regla es simple: **no avances si no podés hacer la práctica**. Leer sin ejecutar deja la sensación de entender y no la comprensión.

## Qué se revisó de verdad (y qué no)

Esta edición no leyó "todo CLS". Sería falso decirlo: el corpus tiene más de 8.000 archivos y 144,9 horas de transcripciones. Lo que se hizo:

| Lote | Qué contiene | Qué se hizo |
|---|---|---|
| **Reversing desde cero** | 47 capítulos, 28,6 h | 42 con citas (38 en 2A + ofuscación 26/30, TLS 38 y MFC 39 en 2B); 5 excluidos por criterio (13, 17, 27, 29, 31) |
| **Videos y material adicional** | 40 videos, 22,5 h (MASM32 + OllyDbg) | Encabezados y pasajes de los 40; varios completos |
| **Curso IDA desde cero** | 69 .docx + 47 PDF | 69 páginas-tutorial ilustradas (texto + 3.278 capturas); tutes 1–28 integrados en las lecciones |
| **Python ISO video tutes** | 55 transcripciones, 12,7 h | 20 completas + 2 parciales; **no enseña Python** |
| **Introducción al reversing con IDA Pro** | 1 .docx de 2016 | Texto extraído y leído |
| **Teorias_Numeradas** | 2.023 contenedores (2.017 con título legible) | Clasificados por título: 426 educativos / 1.591 cracking comercial |
| **Transcripciones de Telegram** | 179 videos (76,5 h) + 357 audios (2,7 h) | Tamizadas por tema (heurística); 5 juntadas ilustradas + 99 audios en hilos con reproductor |
| **Chat unido** | 100.791 mensajes | Metadatos y muestras; **no mensaje por mensaje** |
| **Comprimidos** | 2.299 | Listado generado; no se extrajeron |
| **Imágenes y documentos** | 3.235 imágenes, 567 documentos | Sin OCR; documentos leídos: los 69 `.docx` del Curso IDA (texto + capturas) y 2 `.docx` sueltos |
| **Inventario limpio** | 8.154 archivos | LEEME, resumen y consultas agregadas |

El detalle fila por fila está en [registro_de_cobertura.csv](registro_de_cobertura.csv) y [mapa_de_cobertura.csv](mapa_de_cobertura.csv). Los criterios y las exclusiones están en [Fuentes y límites](fuentes_y_limites.html).

:::{aviso} Lo que no se puede afirmar
- No se ejecutó ningún binario del corpus.
- No se extrajo ningún comprimido.
- No se abrió ningún adjunto del chat.
- No se leyeron **de punta a punta** los 47 capítulos del curso principal (sí 38, con cita) ni las 795 transcripciones completas (se tamizaron por tema y se procesaron las técnicas).
- El tamizado de Telegram y la clasificación de Teorias_Numeradas son **por título/palabras clave**, no lectura completa de cada archivo.
- Un título, un nombre de archivo o una mención **no** demuestran lo que enseña un recurso.
:::

## Cómo se leen las fuentes

En todo el curso vas a encontrar cuatro tipos de afirmación:

| Etiqueta | Significado |
|---|---|
| **Contenido observado en CLS** | Figura en un archivo leído; se cita ruta, capítulo y timestamp cuando existe |
| **Síntesis del material CLS** | Resumen con palabras propias de varios fragmentos observados |
| **Conocimiento externo** | Teoría general que no depende de un archivo de CLS |
| **Recomendación editorial** | Sugerencia de método o seguridad agregada por esta guía |

Cuando el audio y la teoría discrepan, se citan ambos y se explica la diferencia. Ejemplos: la explicación de little-endian del capítulo 01 invierte la palabra "significativo"; el capítulo 07 dice "cuatro breakpoints por proceso" cuando son por hilo; el capítulo 03 se enreda con los rangos de WORD. Las lecciones lo marcan.

## Qué hay en el paquete

| Archivo o carpeta | Para qué |
|---|---|
| [guia/](guia/index.html) | Las lecciones HTML, etapa por etapa |
| [Materiales](materiales.html) | Hub: un solo lugar con enlaces a todo |
| [Buscar](buscar.html) | Buscador offline por palabra en todo el curso |
| [Banco de prácticas](practicas.html) | Crackmes del corpus para practicar en VM, con hash y mapeo al curso |
| [Índice de videotutoriales](videos.html) | Dónde está en Windows cada video mencionado, con enlace y ruta |
| [Curso IDA · índice por tema](ida-tutes.html) | Los 69 tutes de IDA, con tema y cantidad de palabras |
| [Teorias_Numeradas · educativo vs. cracking](teorias.html) | Los 2.023 contenedores (2.017 con título legible) clasificados por título |
| [Telegram por tema](telegram.html) | 523 transcripciones tamizadas; dónde están las sesiones de práctica |
| [fichas/](fichas/index.html) | Qué es cada recurso, qué se revisó y qué falta |
| [glosario.html](glosario.html) | Términos en lenguaje de principiante |
| [preguntas_y_respuestas.html](preguntas_y_respuestas.html) | Repaso por etapa, con respuestas |
| [mapa_de_cobertura.csv](mapa_de_cobertura.csv) | Tema ↔ recurso ↔ archivo/capítulo ↔ estado |
| [registro_de_cobertura.csv](registro_de_cobertura.csv) | Lotes, archivos, revisados, pendientes y motivo |
| [seguimiento.csv](seguimiento.csv) | Tu planilla de avance |
| [Fuentes y límites](fuentes_y_limites.html) | Criterios, alcance y limitaciones |
| [CLS_Curso_Reversing.pdf](CLS_Curso_Reversing.pdf) | Edición de estudio (solo teoría) para leer sin pantalla; las prácticas y los materiales están acá en el HTML |
| [plantilla_informe.md](plantilla_informe.md) | Base para tus informes |

Todo funciona **offline**. Las fuentes locales se enlazan con rutas relativas; los enlaces a transcripciones, videos y documentos abren el archivo original. El paquete trae HTML, CSV, el PDF y las **imágenes de los tutes ilustrados y los fotogramas de las juntadas** (~130 MB). Los **videos y audios** (decenas de GB) **se vinculan, no se copian**: para que abran, mantené las carpetas del proyecto una al lado de la otra (o usá los ZIP de compartir).

:::{nota} Compartir el curso
Los enlaces locales son **relativos** y funcionan si se conserva la estructura del paquete. Para compartir, prepará una copia curada con los archivos que tengas derecho a redistribuir; no compartas la carpeta de proyecto completa ni exportaciones de chats, corpus sin revisar o medios de terceros. La edición pública de presentación contiene el PDF de teoría; el paquete local conserva el HTML y los tutoriales de apoyo. Más detalle en el [Índice de videotutoriales](videos.html).
:::

## Requisitos

- Una computadora con **Windows**. Esta edición cubre **solo reversing de Windows** (binarios PE, x86/x64); Linux, macOS, Android y ARM quedan fuera, aunque los fundamentos se trasladen.
- VirtualBox, VMware o Hyper-V para el laboratorio.
- x64dbg, un editor hexadecimal y un visor de PE (gratuitos).
- IDA Free o Ghidra. **No** hace falta IDA Pro.
- Ganas de escribir programas propios: son el mejor material de práctica.

## Seguridad y legalidad

:::{peligro} Leé esto antes de ejecutar cualquier cosa
- No ejecutes adjuntos del chat, cracks, keygens, instaladores desconocidos ni archivos en cuarentena.
- No analices malware en tu máquina personal. La rama de malware de esta guía es **estática y defensiva**.
- No uses las técnicas para eludir licencias, DRM, autenticación o controles de acceso.
- No analices software ajeno sin permiso. Los ejercicios de vulnerabilidades se hacen en programas propios o laboratorios diseñados para eso.
- Si encontrás una vulnerabilidad, reportala en privado y no publiques el exploit.
:::

## Qué falta en esta edición (y por qué)

Esta edición es, a propósito, una **cobertura parcial y honesta**: lee y cita un núcleo representativo del material y documenta el resto como pendiente, en lugar de aparentar que revisó todo. Lo que queda afuera cae en dos grupos.

**Excluido por criterio (ética y alcance), no por falta de tiempo:**

- Cinco capítulos de «Reversing desde cero» (13, 17, 27, 29, 31): desempaquetado de protectores comerciales (AcProtect). Enseñarlos cruzaría a vulnerar software comercial, fuera del marco educativo y defensivo de esta guía. (La **ofuscación** de los caps. 26 y 30 ya **no** está excluida: es la lección [2.10](guia/02-ofuscacion.html); TLS y MFC son 2.11 y 2.12.)
- La mayor parte de `Teorias_Numeradas`: muchos títulos apuntan a cracking de software comercial, y además son contenedores sin abrir (varios con contraseña).
- Android, Linux/ELF y macOS: esta edición cubre **solo Windows**.

**Ya procesado en esta tanda (índices nuevos, antes pendientes):**

- Los 69 documentos del «Curso IDA desde cero»: se extrajo **texto + 3.278 capturas** y se armaron **69 páginas-tutorial ilustradas** (índice en [Curso IDA · índice por tema](ida-tutes.html)). Además, los **tutes 1–28 quedaron integrados en las lecciones** (Números, Instrucciones, IDA, Herramientas, Debugger, Llamadas, Flujo y Vulnerabilidades), citados uno por uno.
- Los 2.023 contenedores de `Teorias_Numeradas`: se clasificaron por título en educativos vs. práctica sobre software comercial (426 / 1.591 de 2.017 legibles). Ver [Teorias_Numeradas · qué es educativo y qué no](teorias.html). Siguen sin abrir (varios con contraseña); la clasificación es por título, no por contenido.
- Las transcripciones de Telegram: se tamizaron 523 por palabras clave y, con lo técnico, se armaron **5 [juntadas ilustradas](juntadas/index.html)** (fotogramas + transcripción + reproducir) y los **99 [audios técnicos en hilos por sesión](audios/index.html)** con reproductor. Índice general en [Transcripciones de Telegram por tema](telegram.html).

**Pendiente por volumen o formato (se podría sumar en una próxima tanda):**

- Leer de verdad (no por título/heurística) las transcripciones y tutes de IDA ya indexados: el índice dice dónde mirar, pero citar con precisión exige abrir cada uno.
- Los contenedores de **exploiting de Windows**: material avanzado de la Etapa 5, sin extraer; la guía cubre el defecto y las mitigaciones de forma conceptual y defensiva, no la construcción de exploits.

El detalle fila por fila está en [registro_de_cobertura.csv](registro_de_cobertura.csv). Regla de fondo: una mención o un título **no** demuestran lo que enseña un recurso, así que nada de esto se presenta como leído: los tres índices nuevos clasifican **títulos y texto extraído**, no una lectura completa.

## Atribución

Este curso es una obra derivada del proyecto CLS. El material didáctico principal es de **Ricardo Narvaja y Solid** («Reversing desde cero»), **Cayetano de Juan Úbeda** (MASM32 y OllyDbg) y **Daniel Bermúdez** (lógica de programación). Las fichas indican autoría, ruta y límites de cada recurso. Esta guía no está afiliada a CLS ni a los autores; los errores de interpretación son de esta edición.

:::{nota} Empezá ahora
[Etapa 0 · Laboratorio](guia/etapa-0.html) · [Mapa del curso](guia/index.html) · [Fichas](fichas/index.html) · [Glosario](glosario.html)
:::







