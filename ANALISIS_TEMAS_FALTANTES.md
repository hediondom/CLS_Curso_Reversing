# Análisis de temas faltantes — Curso CLS

**Fecha:** 27 de octubre de 2026. **Alcance:** corpus local `C:\Users\agust\CLS_proyecto` + guía actual `CLS_Guia` + comparación con guías/libros de referencia del mismo tema.

> **Reconciliación editorial (28/10/2026):** las tablas y cifras siguientes son una fotografía histórica de la guía antes de las ediciones 4–5 y de las ramas 2D/Etapa 6; no describen la cobertura actual. El PE fino ahora incluye Authenticode y resolución efectiva de DLL; 2D incorpora WOW64; .NET añade límites de Native AOT y C++/CLI; la rama de vulnerabilidades amplía familias de defectos y fuzzing tiene una práctica reproducible. Para el estado vigente consultá el curso y `mapa_de_cobertura.csv`. La reconciliación no implica que las ramas externas aquí mencionadas (Android, ELF, firmware, etc.) se hayan agregado.

> **Actualización editorial (27/10/2026):** este análisis conserva el diagnóstico de la versión previa a la ampliación optativa 2D/Etapa 6. Las afirmaciones de que kernel/drivers siguen fuera de la guía y de que 2D no existe son históricas; el estado actual está en `FUENTES_Y_LIMITES.md` §10.3 y en `mapa_de_cobertura.csv`. La comparación externa y el resto de los huecos no se volvieron a auditar en esta ampliación.

## Veredicto en una página

La guía actual **no es un índice**: tiene 25 lecciones, ejemplos, prácticas y preguntas. Cubre bien el **núcleo de reversing de Windows x86/x64**: laboratorio, números, memoria, PE, assembly, debugger, IDA, .NET básico, método, criptografía, informe y análisis dinámico seguro.

Pero **no está completa**, ni respecto de todo el corpus CLS ni respecto de una currícula general de reversing. Faltan tres grupos de temas:

1. **Huecos dentro del alcance Windows** que ya tienen material local y no se enseñan: packers/desempaquetado didáctico, anti-debug/anti-VM/anti-disassembly, WinDbg/TTD y heap, C++/VB6/Delphi/Java, patch diffing/CVE, scripting de x64dbg y malware dinámico defensivo.
2. **Ramas avanzadas que existen en CLS pero quedaron fuera**: kernel/drivers, exploiting, Android, Linux/ELF, macOS/Mach-O y ARM.
3. **Temas que ni CLS ni la guía cubren y sí otras guías**: ARM/AArch64 como arquitectura, C++ profundo, anti-VM, análisis de shellcode, firmas de red/C2, FLIRT, ejecución simbólica, fuzzing, binarios Go/Rust, firmware/UEFI y forense de memoria.

Lo que está excluido por ética —cracking comercial, keygens, dongles, protectores, ejecución de malware y exploits contra terceros— **está bien excluido**. Eso no es un “falta”: es un límite deliberado.

---

## 1. Qué cubre hoy la guía

| Etapa | Lecciones | Fortaleza | Debilidad |
|---|---:|---|---|
| 0 · Laboratorio | 1 | VM, snapshots, hash, bitácora | Nada importante para su alcance |
| 1 · Fundamentos | 5 | Números, memoria, procesos, PE, C/Python | Python es mínimo; no hay C++ |
| 2 · Reversing | 9 | Assembly, FP/SSE, flujo, llamadas, debugger, IDA, optimizaciones, herramientas | No hay packers, anti-debug ni WinDbg; C++/VB6/Delphi/Java casi ausentes |
| 3 · .NET | 2 | CLR, IL, decompilación | Solo .NET/C#; no Java, VB6, Delphi ni ofuscadores .NET |
| 4 · Práctica | 4 | Método, cripto, informe, dinámico seguro | No hay patch diffing ni análisis de malware dinámico |
| 5 · Ramas | 4 | Malware estático, vulnerabilidades conceptuales, automatización, límites | Solo Windows; sin kernel, Android, Linux, macOS ni ARM |

**Conclusión parcial:** como curso base de Windows, está bien armado. Como “todo el contenido útil de CLS”, no.

---

## 2. Evidencia local: qué hay y qué se está usando

| Colección | Cantidad / tema | Estado en la guía |
|---|---|---|
| `Reversing desde cero` | 47 capítulos; 38 leídos con cita, 7 excluidos por protectores/ofuscación, 2 pendientes (38 TLS, 39 MFC) | Base de las etapas 1–4 |
| `Videos y material adicional` | 40 videos: 22 de MASM32 y 18 de OllyDbg | Usados como apoyo; OllyDbg histórico |
| `IDA desde cero` | 69 tutoriales ilustrados; 1–28 integrados; 29–48 vulnerabilidades/exploiting; 49–69 kernel | 1–28 en el curso; 29–69 solo indexados |
| `Teorias_Numeradas` | 2.017 títulos: 426 educativos / 1.591 cracking comercial | Clasificados por título; no abiertos |
| `Python ISO` | 55 transcripciones | 22 leídas; es lógica, no Python |
| `Telegram` | 523 transcripciones tamizadas; 5 juntadas + 99 audios | Índices, no lectura completa |
| `mega_OTROS` | 901 archivos; carpetas de Linux, macOS, Java, PAIMEI, virus, exploit | Sin integrar |
| `github/apuromafo` | 2.457 archivos; series de OllyDbg, x64dbg, Radare, IDA Bigundilla, C/C++, MASM | Solo algunas series usadas |
| `links_chat` | 32 carpetas; curso Android, Ghidra, keygens, ejercicios | Sin integrar |
| `CLS_videos_extraidos` | 254 archivos de video | No se reproducen; se usan transcripciones |

### 2.1. Clasificación de `Teorias_Numeradas`

| Categoría | Cantidad | ¿Está en la guía? |
|---|---:|---|
| Práctica sobre software comercial | 800 | No, excluido |
| Unpacking | 456 | No, excluido |
| Seriales/keygen | 195 | No, excluido |
| .NET/Java/VB | 122 | Solo .NET básico |
| Parcheo | 83 | No, excluido |
| Crackmes/retos | 70 | Parcial (banco de prácticas) |
| Criptografía | 60 | Parcial (04-cripto) |
| Herramientas | 56 | Parcial (02-herramientas) |
| Dongles/protecciones | 44 | No, excluido |
| Intro | 37 | Sí, base |
| Kernel/drivers | 27 | No, fuera de alcance |
| Fundamentos | 26 | Sí |
| Android | 15 | No, fuera de alcance |
| Anti-debug | 13 | Parcial (menciones) |
| Exploiting | 13 | Conceptual, no práctico |

**Lectura:** el corpus tiene mucho material de unpacking, kernel, Android, .NET/Java/VB y exploiting. La guía usa la parte educativa de fundamentos y herramientas, pero deja fuera varias ramas que sí existen localmente.

---

## 3. Matriz de brechas locales

Prioridad: **P0** = hueco importante dentro del alcance Windows; **P1** = avanzado con material local; **P2** = otra plataforma o tema externo.

| Tema | Dónde está en CLS | ¿En la guía? | Prioridad |
|---|---|---|---|
| **Packers, UPX, OEP, dump e IAT** | Caps. 10, 13, 17; IDA 14–18; 456 títulos de unpacking | Solo se menciona; no hay lección | **P0** |
| **Anti-debug, anti-VM y anti-disassembly** | Caps. 22, 24, 26, 30; 13 títulos de anti-debug; PMA caps. 15–17 | Menciones en debugger/malware; sin lección | **P0** |
| **WinDbg, TTD y scripting de WinDbg** | IDA 32–33, 37, 44–45; 20+ títulos de WinDbg/kernel | Solo aparece en la tabla de herramientas | **P0** |
| **Heap internals y heap exploitation** | IDA 44–48, 56–62; PAIMEI heap trace | Solo stack/canary; no heap | **P0/P1** |
| **C++: vtables, RTTI, STL, excepciones** | Cap. 37; IDA 41–43; PMA cap. 20 | Tips sueltos; sin lección | **P0** |
| **VB6/p-code, Delphi, Java** | 43 títulos VB/p-code, 28 Delphi, 15 Java | Solo .NET/C# | **P0/P1** |
| **Ofuscación .NET y decompiladores** | 48 títulos .NET; dnSpy/Reflector/Reactors | Solo IL básico | **P1** |
| **Patch diffing, CVE y análisis de parches** | IDA 29–31 (VLC CVE), 64–66 (SCADA/Ekoparty); BinDiff/Diaphora | Solo mención en herramientas | **P0** |
| **Scripting de x64dbg/OllyDbg** | 202, 212, 295, 1235, 1405, 1876 | Solo IDAPython/Ghidra | **P1** |
| **Malware dinámico: inyección, persistencia, C2** | Video 37 (Shelter); PMA caps. 11–14 | Solo triage estático | **P1** |
| **Kernel y drivers** | 27 títulos; IDA 49–69; PRE cap. 3 | Fuera de alcance explícito | **P2** (avanzado) |
| **Exploiting: heap, ROP, fuzzing, shellcode** | 13 títulos; IDA 29–48; PMA caps. 18–19 | Conceptual, sin práctica | **P2** (avanzado) |
| **Android** | 15 títulos + curso Android en `links_chat` | Fuera de alcance | **P2** |
| **Linux/ELF** | 13 títulos + `CRACKING EN LINUX` | Fuera de alcance | **P2** |
| **macOS/Mach-O** | `CRACKING EN OSX` + 1 título | Fuera de alcance | **P2** |
| **ARM/AArch64** | `CURSO DE ARM EXPLOIT`; ARM Protector (packer) | Fuera de alcance | **P2** |
| **Fuzzing** | 2 títulos; PMA/Android Handbook | No | **P2** |
| **Ejecución simbólica** | PRE cap. 5; sin títulos locales claros | No | **P2** |
| **YARA/CAPA y detección** | Herramientas mencionadas; 0 títulos locales | Solo mención | **P2** |
| **Forense de memoria** | PAIMEI; 1 título dudoso | No | **P2** |
| **Go/Rust** | 0 títulos | No | **P2** |
| **Firmware/UEFI/IoT** | 1 título dudoso | No | **P2** |

---

## 4. Comparación con otras guías y libros

Los índices externos se usan solo como **lista de temas**, no como prueba de calidad ni como contenido leído. Fecha de consulta: 27/10/2026.

| Tema | Guía CLS | Practical Malware Analysis | Practical Reverse Engineering | The IDA Pro Book | Learning Linux Binary Analysis | Android Hacker's Handbook |
|---|---|---|---|---|---|---|
| x86/x64, PE, assembly, IDA, debugger | ✅ | ✅ | ✅ | ✅ | ◐ | ◐ |
| Anti-disassembly / anti-debug / anti-VM | ◐ | ✅ | ◐ | ◐ | ✅ | ◐ |
| Packers y unpacking | ❌ | ✅ | ◐ | ◐ | ✅ | ◐ |
| Shellcode | ◐ | ✅ | ◐ | ◐ | ◐ | ◐ |
| C++ (vtables, RTTI, objetos) | ◐ | ✅ | ◐ | ◐ | ❌ | ❌ |
| Kernel y drivers | ❌ | ✅ | ✅ | ❌ | ✅ | ◐ |
| WinDbg, kernel debugging y scripting | ◐ | ✅ | ✅ | ✅ | ◐ | ◐ |
| Malware: comportamiento, inyección, persistencia, C2 | ◐ | ✅ | ◐ | ❌ | ◐ | ◐ |
| Firmas de red y análisis de C2 | ❌ | ✅ | ◐ | ❌ | ◐ | ◐ |
| Vulnerabilidades y exploiting | ◐ | ◐ | ◐ | ✅ | ✅ | ✅ |
| Patch diffing / FLIRT / firmas de biblioteca | ◐ | ◐ | ◐ | ✅ | ◐ | ❌ |
| .NET / Java / VB6 / Delphi | ◐ | ◐ | ◐ | ◐ | ❌ | ◐ |
| Android | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Linux/ELF y forense | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| ARM/AArch64 | ❌ | ❌ | ✅ | ❌ | ❌ | ◐ |
| Ofuscación y deobfuscación | ◐ | ✅ | ✅ | ✅ | ◐ | ◐ |
| Ejecución simbólica | ❌ | ❌ | ✅ | ◐ | ❌ | ❌ |
| Fuzzing | ❌ | ◐ | ❌ | ❌ | ◐ | ✅ |
| YARA/CAPA/detección | ◐ | ✅ | ❌ | ❌ | ◐ | ◐ |
| Go/Rust, firmware/UEFI, forense de memoria | ❌ | ❌ | ❌ | ◐ | ✅ (forense) | ◐ |

**Leyenda:** ✅ dedicado; ◐ parcial o mencionado; ❌ ausente. La comparación es por **temas del índice**, no por profundidad.

### Qué muestran las diferencias

- **Practical Malware Analysis** dedica capítulos enteros a anti-disassembly, anti-debug, anti-VM, packers, shellcode, C++ y malware en 64 bits. La guía CLS cubre el análisis estático básico, pero no esa progresión.
- **Practical Reverse Engineering** incluye ARM, kernel de Windows (syscalls, IRQL, pool, MDL, APCs, IRPs, drivers, rootkits), automatización con WinDbg y ofuscación/deobfuscación con ejecución simbólica. CLS tiene material local de kernel y WinDbg, pero la guía no lo enseña.
- **The IDA Pro Book** agrega FLIRT, personalidades de compilador, plugins, módulos de loader/procesador y análisis de código ofuscado. La guía usa IDA, pero no enseña esas capas.
- **Learning Linux Binary Analysis** cubre ELF, ptrace, protección binaria, forense y `/proc/kcore`. CLS tiene material de Linux, pero la guía lo declara fuera de alcance.
- **Android Hacker's Handbook** cubre arquitectura Android, rooting, fuzzing, auditoría y explotación. CLS tiene 15 títulos y un curso Android; la guía no los usa.

---

## 5. Qué agregar y en qué orden

### P0 — Huecos dentro de Windows que conviene cerrar ya

1. **`02-packers.html` — Packers y desempaquetado didáctico.** UPX, OEP, dump, IAT, secciones. Solo con binarios propios o crackmes didácticos; nada de protectores comerciales. Material: caps. 10/13/17, IDA 14–18, 456 títulos.
2. **`02-antidebug.html` — Anti-debug, anti-VM y anti-disassembly.** Detección y reconocimiento; no evasión de protecciones comerciales. Material: caps. 22/24/26/30, 13 títulos, PMA 15–17.
3. **`02-windbg-heap.html` — WinDbg/TTD y heap.** WinDbg, TTD, page heap, LFH, heap spraying conceptual. Material: IDA 32–33/37/44–48, PRE cap. 3–4.
4. **`02-runtimes.html` — VB6/p-code, Delphi y Java.** VMT de Delphi, p-code de VB6, bytecode Java. Material: 43+28+15 títulos.
5. **`04-patchdiff.html` — Patch diffing y CVE.** BinDiff/Diaphora, diff de dos versiones, CVE-2008-4654 y retos SCADA/Ekoparty como casos. Material: IDA 29–31/64–66.
6. **`02-cpp.html` — C++ de verdad.** Vtables, RTTI, STL, excepciones, `std::string`, herencia. Material: cap. 37, IDA 41–43, PMA cap. 20.
7. **`05-scripting.html` — Scripting de x64dbg y OllyDbg.** Además de IDAPython/Ghidra. Material: 202/212/295/1235/1405/1876.
8. **`05-malware-dinamico.html` — Malware dinámico defensivo.** Sandbox, Procmon, inyección, persistencia, C2, IOCs. Material: video 37, PMA 11–14. Solo laboratorio aislado.

### P1 — Avanzado, con prerrequisitos y ética

9. **`06-kernel.html` — Introducción defensiva a kernel/drivers.** IRP, IOCTL, SSDT, rootkits, HEVD. Material: 27 títulos, IDA 49–69, PRE cap. 3.
10. **`06-exploiting.html` — Laboratorio de exploiting.** Heap, UAF, ROP, fuzzing, shellcode; solo binarios propios o labs deliberadamente vulnerables. Material: IDA 29–48, PMA 18–19.
11. **`06-shellcode.html` — Análisis de shellcode.** Position-independent code, encodings, NOP sleds; análisis, no creación.

### P2 — Otras plataformas (track separado)

12. **Android:** APK/DEX, smali, jadx, Frida, manifiesto, nativo. 15 títulos + curso.
13. **Linux/ELF:** ELF, GOT/PLT, ptrace, gdb, forense, `/proc/kcore`.
14. **macOS/Mach-O:** Mach-O, dyld, codesign, otool/lldb.
15. **ARM/AArch64:** registros, ABI, instrucciones, Android/iOS nativo.

### P3 — No hay material local suficiente

16. **Go/Rust:** binarios con runtime propio, tablas de funciones, `gopclntab`, `rustc` symbols.
17. **Fuzzing y ejecución simbólica:** AFL++, libFuzzer, angr, Z3.
18. **YARA/CAPA:** ingeniería de reglas, capacidades, falsos positivos.
19. **Forense de memoria:** Volatility, volcados, procesos ocultos.
20. **Firmware/UEFI/IoT:** UEFI, SPI, binarios MIPS/ARM.

---

## 6. Qué no conviene agregar

- Cracking de software comercial, keygens, seriales, dongles.
- Desempaquetado de protectores comerciales (Themida, ACProtect, VMProtect) como práctica.
- Ejecución de malware fuera de un laboratorio defensivo.
- Exploits contra sistemas de terceros.
- “Anti-anti-debug” para evadir protecciones comerciales.

La guía ya excluye esto y hace bien. El análisis de brechas **no** debería empujar el curso hacia ese lado.

---

## 7. Conclusión

- **Como curso base de reversing de Windows:** está bastante completo. Le faltan, sobre todo, **packers, anti-debug/anti-VM, WinDbg/heap, C++/VB6/Delphi/Java, patch diffing y scripting**.
- **Como cobertura de todo CLS:** no está completo. Faltan kernel, exploiting, Android, Linux, macOS y ARM, todos presentes en el corpus.
- **Como currícula general de reversing:** le faltan temas que otras guías sí cubren: ARM, C++ profundo, anti-VM, shellcode, firmas de red/C2, FLIRT, ejecución simbólica, fuzzing, Go/Rust y forense de memoria.

**Próximo paso recomendado:** agregar primero los 5 temas P0 que más cambian la experiencia —packers, anti-debug, WinDbg/heap, runtimes y patch diffing— y dejar kernel/Android/Linux como tracks separados con prerrequisitos. Eso cierra los huecos más visibles sin convertir el curso en una enciclopedia.

---

## 8. Fuentes y límites

### Locales

- `CLS_resultados_intermedios/teorias_numeradas_por_etapa.csv` — 2.017 títulos y categorías.
- `CLS_Guia/ida_tutes_indice.csv` — 69 tutoriales de IDA con tema y palabras.
- `CLS_resultados_intermedios/mapa_carpetas_etapas.csv` — 45 filas de asignación por etapa.
- `CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/` — 47 capítulos.
- `CLS_Guia/00_EMPEZAR_AQUI.html`, `guia/index.html`, `05-fuera-de-alcance.html` — alcance declarado.
- `CLS_Guia/registro_de_cobertura.csv` — lotes y pendientes.

### Externas (solo índices/TOC, consultadas 27/10/2026)

- *Practical Malware Analysis* (Sikorski y Honig), TOC de la Library of Congress: https://catdir.loc.gov/catdir/enhancements/fy1211/2012000214-t.html
- *Practical Reverse Engineering* (Dang, Gazet, Bachaalany), TOC de la Library of Congress: https://catdir.loc.gov/catdir/enhancements/fy1606/2013954099-t.html
- *The IDA Pro Book, 2nd Edition* (Chris Eagle), TOC en Google Books: https://books.google.com.ar/books?id=kOJ5G_mAbZoC
- *Learning Linux Binary Analysis* (Ryan O'Neill), TOC en Reference Global: https://reference-global.com/book/9781782167112?tab=description
- *Android Hacker's Handbook* (Drake et al.), registro y descripción: https://discover.knoxcountylibrary.org/oreilly/ocn875820167

### Límites

- Los conteos de `Teorias_Numeradas` son **por título**, no por contenido; los contenedores no se abrieron.
- Los tutoriales de IDA 29–69 están indexados, no necesariamente leídos en profundidad.
- La comparación externa usa **índices/TOC**, no la lectura completa de cada libro.
- Las prioridades son **recomendación editorial**, no una obligación: dependen del objetivo del curso (Windows base vs. currícula completa).
- La guía actual está en edición activa; este análisis se basa en el estado del 27/10/2026.
