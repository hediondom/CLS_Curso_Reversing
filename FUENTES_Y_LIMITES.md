# Fuentes y límites de esta edición

**Edición 5. Fecha de cierre de esta tanda: 27 de octubre de 2026.**

Este documento explica de dónde sale el material del curso, qué se revisó de verdad, qué quedó pendiente, qué se corrigió respecto de las ediciones anteriores y qué decisiones editoriales se tomaron. Está pensado para que otra persona —u otra sesión de trabajo— pueda continuar sin empezar de cero.

## 0. Alcance: solo Windows + refuerzo externo

Esta edición cubre **únicamente reversing de Windows** (binarios PE, x86/x64). Linux/ELF, macOS/Mach-O, Android (APK/DEX) y arquitecturas como ARM/AArch64 quedan **fuera de alcance** por decisión editorial (ver `guia/05-fuera-de-alcance.html`).

Además del material del grupo CLS, el curso incorpora un **refuerzo/actualización de conocimiento externo** para tapar temas que CLS no cubría pero que son necesarios en Windows hoy: **punto flotante y SSE** (`guia/02-flotante.html`), **optimizaciones del compilador** (`guia/02-optimizaciones.html`), **reconocer criptografía y encoding** (`guia/04-cripto.html`), el **taller de herramientas actual** (dentro de `guia/02-herramientas.html`) y **dónde seguir practicando** (en el mapa del curso). Esas lecciones están marcadas como *conocimiento externo (agregado por esta edición)* y no se presentan como material observado de CLS.

## 1. Qué es esta edición

Un curso completo en `CLS_Guia`, solo Windows, con:

- Lecciones HTML en siete etapas numeradas: **0–4 son el recorrido obligatorio**; **5 y 6 son ramas optativas**. La rama optativa 2D y la extensión Hyper-V son materiales complementarios, fuera de la aprobación obligatoria.
- Fichas de recursos con estado de revisión.
- Glosario, preguntas y respuestas, mapa y registro de cobertura, seguimiento.
- Este documento de fuentes y límites.

Los borradores anteriores se conservaron en `CLS_Guia/_backup_2026-10-26/`. No se movió, renombró ni sobrescribió ningún archivo fuente, exportación, inventario o transcripción fuera de `CLS_Guia`.

## 2. Mapa real del corpus

Los conteos se obtuvieron del disco el 26/10/2026:

| Carpeta | Archivos | Tamaño | Qué es |
|---|---:|---:|---|
| `telegram/` | 4.949 | 72,0 GB | Exportaciones del chat + un RAR de Themida |
| `CLS_fuentes_externas/` | 3.460 | 17,2 GB | Clones de GitHub, MEGA y links del chat |
| `CLS_videos_extraidos/` | 254 | 14,6 GB | Videos ya extraídos |
| `CLS_resultados_intermedios/` | 1.368 | 100,3 MB | Chat unido, inventarios, transcripciones, mapas |
| `exportacion_sesion/` | 6 | 25,2 MB | Conversación de una sesión anterior |
| `zips_anteriores/` | 11 | 7,2 MB | Resultados históricos |
| `descargas_sueltas/` | 1 | 1,5 MB | Documento de IDA Pro |
| `CLS_Guia/` | paquete | — | Este curso |

Dentro de `CLS_fuentes_externas`:

| Colección | Archivos | Tamaño | Estado |
|---|---:|---:|---|
| `github/apuromafo_Crackslatinos/` | 2.457 | 7,9 GB | Parcial: títulos y algunos documentos |
| `github/SceneRE_CrackSLatinoS/` | 66 | 0,4 MB | Revisado: son iframes |
| `mega_OTROS/` | 901 | 2,4 GB | Solo mapa de carpetas |
| `links_chat/` | 32 | 6,8 GB | Solo listado |

## 3. Inventarios: cuál es vigente y por qué

Hay tres artefactos que parecen inventarios y **no miden lo mismo**:

| Artefacto | Fecha | Cifra | Qué mide | Estado |
|---|---|---|---|---|
| `inventario_limpio/CLS_inventario_limpio.csv` | 26/10/2026 | 8.154 filas | Una fila por archivo en disco, con SHA-256 | **Vigente** |
| `CLS_resultados/inventario_completo.csv` | 24/10/2026 | 6.499 filas | Solo referencias del `result.json`, sin binarios | Histórico |
| `CLS_plan_estudio.docx` | sesión previa | 100.713 mensajes, 2.638 referencias, 3.861 enlaces | Exportación incompleta, rutas `D:\CLS`, sin medios | Histórico y superado |

No se suman esas cifras. El inventario vigente tiene 8.154 archivos; el chat unido tiene 100.791 mensajes (2016-01-18 a 2026-10-26). El plan histórico decía 100.713 mensajes porque trabajaba sobre otra exportación y sin los medios.

Estados del inventario vigente: `util` 6.705, `util (trae binarios: solo VM)` 453, `practica (solo VM)` 66, `cuarentena` 202, `excluido (comercial/warez)` 46, `duplicado` 321, `descartado (miniatura)` 361.

**`util` no significa seguro, bueno ni vigente.** Es una clasificación de catálogo. Las recomendaciones del curso se basan en el contenido leído, no en ese estado.

## 4. Método de trabajo por tandas

1. Se leyeron los `LEEME`, resúmenes, mapas, índices y CSV de inventario.
2. Se compararon versiones (inventario limpio vs histórico, plan de estudio vs estado actual).
3. Se procesaron transcripciones por lotes: lectura completa de los capítulos centrales y digest con citas para los secundarios.
4. Se verificaron timestamps contra los `.srt` hermanos.
5. Se extrajo texto de documentos `.docx` seleccionados (IDA Pro y plan de estudio) sin modificar los originales.
6. No se ejecutó ningún binario, no se extrajo ningún comprimido y no se abrió ningún adjunto del chat.
7. Se escribió el curso y se validaron los enlaces relativos contra el disco.

El detalle por lote está en `registro_de_cobertura.csv`; el cruce tema ↔ recurso ↔ archivo está en `mapa_de_cobertura.csv`, que se edita a mano y se valida con `_trabajo/mapa.py` (ese script ya no lo regenera).

## 5. Qué se revisó de verdad

### 5.1 Reversing desde cero (Ricardo Narvaja y Solid)

47 capítulos, 96 archivos `.txt`/`.srt`, 28,6 h según `_progreso.csv`.

Leídos completos o digeridos con citas: **29 capítulos**.

- Leídos por el editor: 01, 02, 03, 04, 05, 07, 11, 14, 15, 18.
- Digeridos por subagentes con citas verificadas: 06, 08, 09, 12, 15b, 16b, 21, 22, 24, 26, 26b, 28, 29b, 30, 35, 36, 37, 38, 39.

Estado al 27/10/2026 (la fuente fechada y autoritativa es [`registro_de_cobertura.csv`](registro_de_cobertura.csv)): **42 de 47 capítulos citados** (38 en 2A + ofuscación 26/30, TLS 38 y MFC 39 integrados en el bloque 2B) y **5 excluidos por criterio** (13, 17, 27, 29, 31: desempaquetado de protectores comerciales). No quedan capítulos pendientes. Las listas de arriba pueden no estar al día capítulo por capítulo; el registro manda.

### 5.2 Videos y material adicional (Cayetano de Juan Úbeda)

40 videos, 22,5 h. Se identificaron dos cursos:

- **Videos 1–22:** «Lenguaje ensamblador con MASM32 para Windows». 13,6 h.
- **Videos 23–40:** «Introducción a reversing con OllyDbg». 9,7 h.

Se leyeron encabezados y pasajes de los 40; completos los cortos (12, 22, 23, 33, 34, 39, 40) y pasajes extensos de 8, 20, 24, 35, 36, 37, 38.

### 5.3 Python ISO video tutes

55 transcripciones (165 segmentos), 12,7 h. Se leyeron 20 completas y 2 parciales; 33 solo por encabezado.

**Hallazgo:** no es un curso de Python. Es un curso de lógica y fundamentos de programación con pseudocódigo y ejemplos en Basic, Pascal y C. No contiene código Python ejecutable. El autor anuncia una segunda parte con Python que no está en la carpeta.

### 5.4 Documentos

- `descargas_sueltas/INTRODUCCIÓN AL REVERSING CON IDA PRO DESDE CERO.docx`: texto extraído (7.620 caracteres) y leído. Es la parte 1 de una serie de 2016.
- `CLS_resultados_intermedios/CLS_plan_estudio.docx`: texto extraído (6.714 caracteres) y leído. Es un plan histórico basado en una exportación incompleta.
- `IDA DESDE CERO`: 69 `.docx` + 47 PDF. Se extrajo el **texto + 3.278 capturas** de los 69 `.docx` y se armaron **69 páginas-tutorial ilustradas** (`ida_tutes/`, índice en `ida-tutes.html`); los **tutes 1–28 se integraron en las lecciones** y los 29–48 se resumieron en clave defensiva en Vulnerabilidades. Los 47 PDF y el `.rar` **no** se extrajeron; los tutes 49–69 (kernel) quedan indexados, fuera del recorrido.

### 5.5 Chat, Telegram y comprimidos

- `CLS_chat_unido.json` (100.791 mensajes): metadatos, totales y muestras; **no** lectura mensaje por mensaje.
- Transcripciones de Telegram: 179 videos (76,5 h) y 357 audios (2,7 h). Se **tamizaron 523 por tema** (heurística por palabras clave); con lo técnico se armaron **5 juntadas ilustradas** (fotogramas + transcripción, `juntadas/`) y **99 audios en hilos** con reproductor (`audios/`). No es lectura completa de cada archivo.
- `_comprimidos.csv`: 79.808 entradas listadas; **no se extrajo** ningún comprimido.
- `_hashes.csv`: 8.154 hashes SHA-256.
- Imágenes: 3.235 en el inventario (más 385 miniaturas descartadas). **No se hizo OCR ni inspección visual**; no se usan como fuente de contenido.
- Documentos: 567 en el inventario (PDF, DOC, DOCX, TXT). Se extrajeron y leyeron los **69 `.docx` del Curso IDA** más dos `.docx` sueltos (IDA Pro y plan de estudio); el resto queda pendiente.
- Audios: 357 mensajes de voz. **No se escucharon**; las transcripciones existen y los candidatos técnicos se tamizaron y agruparon en hilos, pero no se leyeron todas.

### 5.6 Ficciones y correcciones

- Las páginas de SceneRE son **iframes de YouTube**, no texto didáctico. El borrador anterior las citaba como si enseñaran.
- El video «Reverse engineering con Ricardo Narvaja» no es un tutorial: aproximadamente la primera hora es música/intro de stream y desde ~01:01 hay una conversación sobre la profesión.
- El video 37 ejecuta malware (Shelter) y monta un reverse shell en VMs. Es un caso observado, no una práctica recomendada.
- El video 36 inyecta una puerta trasera de Metasploit en una calculadora dentro de una VM. Tampoco es una práctica de esta guía.
- El documento de IDA Pro recomienda descargar IDA Pro 6.8 "desde Google" con una contraseña. **No se reproduce**: se usa IDA Free o Ghidra.
- `Teorias_Numeradas` tiene 2.023 títulos; muchos apuntan a prácticas sobre software comercial o protectores. No se usa como curso ni se abre.

## 6. Discrepancias y afirmaciones dudosas

| Fuente | Lo que dice | Lo que corresponde |
|---|---|---|
| Cap. 01, ~00:22:33 | "el byte más significativo es el de la derecha" | En little-endian, el byte **menos** significativo va primero |
| Cap. 03, ~00:17:00 | Rangos de WORD confundidos | BYTE −128..127; WORD −32.768..32.767; DWORD −2.147.483.648..2.147.483.647 |
| Cap. 07, ~00:06:00 | "cuatro breakpoints por proceso" | Son cuatro por **hilo** (`DR0`–`DR3` en el contexto del hilo) |
| Cap. 09, ~00:08:53 | "JC es igual a JE" | `JE` = `JZ`; `JC` = `JB` (carry) |
| Cap. 14, ~00:01:00 | Buscar IDA Pro "por internet" | Usar IDA Free, Ghidra o licencia educativa |
| Docx IDA 2016 | Descargar IDA Pro 6.8 con contraseña | No se sigue; usar software con licencia |
| Plan de estudio | Rutas `D:\CLS`, 100.713 mensajes, sin medios | Las rutas se actualizaron al árbol local del proyecto y a su inventario vigente |
| Video 37 | Ejecuta malware "para ver qué hace" | Caso observado; la práctica de esta guía es estática y defensiva |

Cuando el audio se equivoca en un mnemónico o un número, la lección lo marca y enseña el valor correcto. No se copian errores del ASR.

## 7. Criterios de inclusión y exclusión

### Se incluye

- Material en español, progresivo, con ejemplos y ejercicios.
- Programas propios, software abierto o crackmes diseñados para aprender.
- Análisis estático y dinámico en laboratorio aislado.
- Contexto histórico cuando ayuda a entender (OllyDbg, MASM32, Python 2).
- Contenido defensivo sobre malware, vulnerabilidades y mitigaciones.

### Se excluye

- Eludir licencias, DRM, autenticación o controles de acceso.
- Producir cracks, keygens o parches para software comercial.
- Desempaquetar protectores comerciales (Themida, WinLicense, ACProtect) como práctica.
- Ejecutar adjuntos del chat, muestras en cuarentena o instaladores desconocidos.
- Presentar títulos o contenedores como si fueran contenido leído.
- Sumar cifras de inventarios incompatibles.

Los estados `cuarentena`, `excluido`, `descartado` y `duplicado` se respetan. No se convierten en tareas.

## 8. Seguridad y legalidad

El curso es educativo, defensivo y para uso autorizado:

- Las prácticas de reversing se hacen con programas propios o crackmes.
- El malware se estudia en estático; la ejecución dinámica queda fuera de alcance.
- Las vulnerabilidades se practican en programas propios o laboratorios diseñados para eso.
- La divulgación de una vulnerabilidad es privada y coordinada.
- No se distribuyen claves, contraseñas ni instrucciones para abrir material protegido.
- No se copiaron binarios al paquete de estudio.

## 9. Convenciones de rutas y enlaces

- En las páginas HTML, los enlaces a fuentes son relativos a la página y apuntan a la raíz del proyecto con `../` o `../../`.
- En los CSV, las rutas son relativas a la **raíz local del proyecto**.
- Los nombres con espacios o acentos se codifican en la URL (`%20`, `%C3%A1`).
- Los enlaces se verificaron contra el disco con un script; los que no existen se marcan como pendientes.
- **Los recursos se vinculan, no se incluyen.** El paquete contiene HTML, CSV, el PDF, las páginas-tutorial ilustradas de IDA con sus capturas y los textos extraídos en `_trabajo/extraido_ida/`; los videos, binarios y comprimidos **se vinculan**, no se copian.
- Los recursos externos (URLs) no se incluyen como enlaces vivos si no se verificaron; en ese caso se indica el título y se deja constancia.

## 10. Qué se construyó (ediciones 4–5) y qué falta

Lo de las ediciones anteriores ya está hecho: los 38 capítulos citados, los 69 documentos de IDA extraídos/ilustrados/integrados, `Teorias_Numeradas` clasificado por título (426 educativos / 1.591 cracking) y las transcripciones de Telegram tamizadas (juntadas + audios).

### 10.1 Edición 4 — Etapa 2B · Windows intermedio (HECHO)

La "capa intermedia" que faltaba se construyó como **bloque 2B** dentro de la Etapa 2 (sin renumerar las etapas), con 7 lecciones nuevas, cada una con ejemplo, práctica, repaso, puerta de salida, fuentes y etiquetas:

- **2.10 Ofuscación nativa** (caps. 26 y 30) · **2.11 TLS callbacks** (cap. 38) · **2.12 MFC** (cap. 39).
- **2.13 Huella de compilador** (MSVC/MinGW/Delphi/VB6/MFC) · **2.14 PE fino** (Rich header, recursos, delay-load, `.pdata`, debug/PDB, Load Config).
- **2.15 Taxonomía anti-análisis** (caps. 22 y 24; reconocer, no evadir) · **2.16 Ghidra/Cutter** (recorrido equivalente al de IDA; conocimiento externo).

**Dos límites declarados del bloque 2B:** (a) las fuentes citan la **ruta local** del capítulo (vía el enlace a la transcripción) pero **no el timestamp exacto** dentro del video, como sí hacen las lecciones de 2A; (b) los **ejemplos paso a paso de 2B son ilustrativos** —bytes, direcciones y listados construidos para mostrar la técnica—, no volcados de un binario puntual del corpus. Está marcado así en cada lección.

### 10.2 Edición 5 — Etapa 2C · Windows avanzado (HECHO)

El núcleo avanzado se construyó como bloque **2C** dentro de la Etapa 2 (sin renumerar las etapas):

- **2.17 Packers didácticos** (UPX/OEP/dump/IAT sobre binarios propios) · **2.18 C++ profundo** (RTTI, SSO, STL, excepciones) · **2.19 WinDbg, TTD y heap** · **2.20 Patch diffing y CVE** · **2.21 Scripting de debugger**.
- **Rutas optativas** (fuera de la puerta obligatoria, con sus propios prerrequisitos): **2.22** Malware dinámico defensivo, **2.23** Shellcode/red/C2 (solo reconocer y clasificar), **2.24** Fuzzing y análisis simbólico.

### 10.3 Edición 5 — 2D · Windows internals y Etapa 6 · Kernel/drivers (COMPLETADO)

Se añadieron **13 lecciones optativas 2D**, recomendadas después de 2C, y una extensión conceptual separada sobre Hyper-V. La estimación editorial se ajustó a **45–60 h** y, en las revisiones del 28/10/2026, primero a **50–65 h** (2D.6, 2D.8 y 2D.9 sumaron unas diez páginas y pasos de práctica) y después a **55–70 h** (2D.10–2D.13 sumaron unas once páginas y pasos de práctica); no está medida con alumnos y no se presenta como duración probada. La Etapa 6 pasó de 40–60 h a **45–65 h**: entre las dos revisiones sus seis lecciones sumaron unas veinte páginas y pasos de lectura guiada (bugchecks, inventario de minifilters, estado de VBS/HVCI). 2.18 también se amplió, pero lo agregado entraba en el rango que 2C tenía entonces (~25–35 h).

- 2D.1–2D.5: objetos/tokens, memoria/loader, Registro, servicios y Task Scheduler.
- 2D.6–2D.13: COM, activación COM, DCOM/RPC, WMI, IPC, excepciones, ETW e integrador.
- La **Etapa 6** añade seis lecciones optativas de kernel y drivers. Requiere C, assembly, memoria/sincronización, WinDbg y solo las lecciones 2D pertinentes (2D.1, 2D.2 y 2D.11); 2C es recomendada, no requisito. Estimación inicial: **45–65 h**, posiblemente más según experiencia previa.
- Hyper-V queda como extensión optativa separada, sin requisito para 2D ni Etapa 6.

La ampliación es principalmente **conocimiento externo** basado en documentación primaria de Microsoft Learn/WDK; los ejemplos están marcados como ilustrativos. No se cargó un driver ni se verificaron los laboratorios en una VM. El laboratorio KMDF propuesto limita el IOCTL a devolver una estructura fija; no incluye lectura/escritura arbitraria de memoria. Las prácticas de kernel exigen VM descartable con snapshot y nunca recomiendan modificar protecciones del host.

### 10.4 Revisión del 28/10/2026 — temas del núcleo de reversing (2B, 2C y 4.1)

Para que quien termine el recorrido encuentre explicados los temas que más aparecen al analizar binarios reales, se ampliaron lecciones existentes, sin etapas ni ramas nuevas y sin renumerar:

- **Temas que faltaban:** resolución dinámica de APIs, API hashing, API sets y capa nativa `ntdll`/`syscall` (2.14); cadenas UTF-16, con longitud, en el stack y cifradas, y patrones de colecciones de datos (lección de IDA); rutinas de descifrado y aplanamiento del flujo (2.10); Go, Rust y Delphi (2.13); reconstrucción de un formato de archivo propio (4.1); trazas condicionales e instrumentación con Frida (2.21).
- **Lecciones finas ampliadas:** 2.15 (`CheckRemoteDebuggerPresent`, `ProcessDebugPort`, tiempos, `CPUID`, tabla de documentación), 2.16 (tipos y estructuras, scripting, headless, Version Tracking), 2.17 (OEP en x64, señales genéricas, por qué falla un dump) y 2.20 (cómo empareja un differ, ruido, símbolos públicos).
- **Estimaciones:** el PDF pasó de 371 a 395 páginas. 2B sumó unas once páginas y nueve pasos de práctica que piden compilar programas propios (APIs dinámicas, cadenas cifradas, flujo aplanado, Go/Rust, chequeos anti-debug, estructuras y scripts en Ghidra): pasa de **~20 h** a **~25 h**. 2C sumó unas ocho páginas y seis pasos (UPX de 64 bits, entropía, diff con ruido de compilación, Version Tracking, trazas y Frida): pasa de **~25–35 h** a **~30–40 h**. La lección 4.1 sumó dos páginas y un ejercicio de formato propio con lector en Python: pasa de 4 h a 6 h y la Etapa 4 de **12–16 h** a **14–18 h**. La lección de IDA (2A) creció dos páginas y dos pasos que entran en su rango de 32–40 h. Ninguna estimación está medida con alumnos.
- **Fuentes:** documentación de Microsoft Learn, Go, Rust, Ghidra, x64dbg, Frida, BinDiff, UPX y Python, comprobada en esta revisión. Lo de Delphi (convención `register`, firma `TPF0`, cabecera de los `string`) queda como conocimiento externo sin enlace, porque la documentación de Embarcadero no respondió durante la verificación.
- **Siguen fuera, y así lo dice cada lección:** ofuscación por máquina virtual y desofuscación simbólica, tipos de Go y *traits* de Rust, p-code de VB6, neutralizar anti-análisis, packers multicapa y protectores comerciales, extensiones de Ghidra y SLEIGH, diff de parches completos de Windows, Stalker de Frida, DynamoRIO/Pin y protocolos de terceros.

Ningún ejemplo nuevo se compiló ni se ejecutó: están marcados como **ilustrativos** y las prácticas nuevas no están verificadas.

### 10.5 Pendiente / futuro

- **Laboratorios reproducibles:** compilar los binarios de práctica propios y publicar versiones de herramientas, archivos y hashes/salidas esperadas. Los ejemplos de 2B, 2C, 2D y Etapa 6 están marcados como **ilustrativos** cuando no hay ejecución verificada.
- Continúan fuera del recorrido Windows: exploiting comercial, Android, Linux/ELF, macOS y ARM.

Opcional (no bloquea el cierre): sumar **capturas propias** a los ejemplos trabajados de 2B, que hoy son ejemplos **ilustrativos escritos** (bytes y direcciones), sin capturas.

Análisis detallado con evidencia (de otra sesión de trabajo, revisado por esta edición): [`ANALISIS_TEMAS_FALTANTES.md`](ANALISIS_TEMAS_FALTANTES.md).

## 11. Limitaciones de esta edición

- La cobertura es **parcial y declarada**: no se leyó todo el corpus.
- Las duraciones de video provienen de `_progreso.csv` o de la suma de subtítulos; las de las lecciones son estimaciones editoriales.
- Las citas de audio pueden tener errores de ASR; se marcan cuando se detectan.
- No se verificó el contenido de los comprimidos ni de los binarios.
- No se probaron los ejercicios en todas las versiones de Windows, IDA, x64dbg o .NET.
- Las herramientas cambian: los atajos y menús pueden diferir de los descritos.
- El curso no reemplaza una formación formal ni una autorización para analizar sistemas ajenos.

## 12. Atribución

- **Reversing desde cero:** Ricardo Narvaja y Solid.
- **MASM32 y OllyDbg:** Cayetano de Juan Úbeda.
- **Lógica de programación:** Daniel Bermúdez, basado en el libro de Omar Iván Trejos Buriticá.
- **Introducción al reversing con IDA Pro:** Ricardo Narvaja (2016).
- **Comunidad CLS:** inventarios, chat, transcripciones y catalogación.

Esta guía es una obra derivada con fines educativos. No está afiliada a CLS ni a los autores. Los errores de interpretación y las decisiones editoriales son responsabilidad de esta edición.

## 13. Verificación rápida

Para comprobar que el paquete está completo:

```powershell
# Contar lecciones y fichas
(Get-ChildItem .\guia -Filter *.html).Count
(Get-ChildItem .\fichas -Filter *.html).Count

# Verificar que la portada y los índices existen
Test-Path .\00_EMPEZAR_AQUI.html
Test-Path .\guia\index.html
Test-Path .\fichas\index.html
```

Los enlaces relativos se verifican con la herramienta de build de esta edición (`verificar_enlaces.py`, dentro de `_trabajo/`, que **no** viaja en el paquete compartido); la última corrida dio 0 enlaces rotos. El resultado y las incidencias se registran en la sección de estado de la portada y en `registro_de_cobertura.csv`.




