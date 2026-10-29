---
title: "Etapa 2 · Introducción al reversing"
description: "Leer assembly x86/x64, seguir el flujo y usar debugger y desensamblador con criterio. Se divide en 2A (base, 2.1–2.9), 2B (Windows intermedio, 2.10–2.16: ofuscación, TLS, MFC, huella, PE fino, anti-análisis, Ghidra) y 2C (Windows avanzado, 2.17+: packers didácticos, C++ profundo, WinDbg/heap, patch diffing, scripting). Las rutas de malware dinámico, shellcode/C2 y fuzzing quedan como optativas, fuera de la puerta obligatoria."
etapa: "Etapa 2 · Introducción al reversing"
---

# Etapa 2 · Introducción al reversing

:::{nota} Objetivo medible
Leer assembly x86/x64, seguir el flujo y usar debugger y desensamblador con criterio. Se divide en 2A (base, 2.1–2.9), 2B (Windows intermedio, 2.10–2.16: ofuscación, TLS, MFC, huella, PE fino, anti-análisis, Ghidra) y 2C (Windows avanzado, 2.17+: packers didácticos, C++ profundo, WinDbg/heap, patch diffing, scripting). Las rutas de malware dinámico, shellcode/C2 y fuzzing quedan como optativas, fuera de la puerta obligatoria.
:::

**Prerrequisitos:** Etapa 1.  
**Duración estimada:** 32 a 40 h (2A) + ~25 h (2B) + ~30–40 h (2C avanzado). Es una estimación de esta guía, derivada de la suma de las lecciones; no es una duración declarada por CLS.

## Lecciones

| # | Lección | Qué aprendés |
|---|---|---|
| 2.1 | [Registros, subregistros y flags](02-registros.html) | Registros, solapamiento y flags ZF/SF/CF/OF. |
| 2.2 | [Instrucciones: mover, calcular y manipular bits](02-instrucciones.html) | MOV, LEA, aritmética, lógica, shifts y cadenas. |
| 2.3 | [Punto flotante y SSE: los registros xmm](02-flotante.html) | x87, SSE escalar (movsd/addsd/ucomisd) e IEEE 754. |
| 2.4 | [Flujo: comparar, saltar y repetir](02-flujo.html) | CMP/TEST, Jcc, CMOVcc, bucles y tablas de salto. |
| 2.5 | [Llamadas, convenciones y marcos de función](02-llamadas.html) | CALL/RET, cdecl/stdcall/fastcall y x64. |
| 2.6 | [El debugger: x64dbg de punta a punta](02-debugger.html) | Interfaz, F7/F8/F9, breakpoints y parcheo ético. |
| 2.7 | [IDA y el análisis estático](02-ida.html) | Strings, xrefs, grafo, rebase y decompilador. |
| 2.8 | [Cómo cambia el código con optimizaciones](02-optimizaciones.html) | Inlining, strength reduction, división por constante y tail calls. |
| 2.9 | [Herramientas: del OllyDbg histórico al taller actual](02-herramientas.html) | Qué usar para cada tarea y qué está discontinuado. |
| 2.10 | [Ofuscación nativa: leer lo que no quiere ser leído](02-ofuscacion.html) | Secciones invertidas, basura, saltos al medio y strings ocultas; hallar el bloque real. |
| 2.11 | [TLS: código que corre antes de main](02-tls.html) | Directorio TLS, AddressOfCallBacks y callbacks previos al entry point. |
| 2.12 | [MFC: llegar al handler cuando todo pasa por clases](02-mfc.html) | Reconocer MFC y alcanzar el handler de un control por el message map. |
| 2.13 | [Huella de compilador: saber con qué se hizo](02-huella-compilador.html) | MSVC, MinGW, Delphi, VB6 y MFC por imports, strings y runtime. |
| 2.14 | [PE fino: los directorios que cuentan la historia](02-pe-fino.html) | Rich header, recursos, delay-load, .pdata, debug/PDB y Load Config. |
| 2.15 | [Taxonomía anti-análisis: reconocer, no evadir](02-anti-analisis.html) | Anti-debug, anti-VM, anti-disassembly y anti-dump: detectarlos. |
| 2.16 | [Ghidra (y Cutter): la alternativa libre, con práctica](02-ghidra.html) | El recorrido de IDA replicado en Ghidra: autoanálisis, strings, tipos y decompilador. |
| 2.17 | [Packers didácticos: UPX, stub, OEP, dump e IAT](02-packers.html) | Desempaquetado didáctico de UPX sobre binarios propios; llegar al OEP y reconstruir la IAT. |
| 2.18 | [C++ profundo: RTTI, vtables, STL y excepciones](02-cpp-profundo.html) | RTTI, std::string con SSO, contenedores STL y manejo de excepciones. |
| 2.19 | [WinDbg, TTD y heap](02-windbg-heap.html) | WinDbg, time-travel debugging y diagnóstico de heap (Page Heap, LFH). |
| 2.20 | [Patch diffing y CVE: leer qué cambió](02-patch-diffing.html) | BinDiff/Diaphora: comparar dos versiones y leer qué arregló un parche (defensivo). |
| 2.21 | [Scripting de debugger: automatizar y dejar evidencia](02-scripting-debugger.html) | Automatizar x64dbg (breakpoints, logs) y guardar evidencia; OllyScript como legado. |
| 2.22 | [(optativa) Malware dinámico defensivo](02-opt-malware-dinamico.html) | Laboratorio aislado, red simulada, observación de comportamiento e IOCs. |
| 2.23 | [(optativa) Shellcode, red y C2: reconocer y describir](02-opt-shellcode-c2.html) | Identificar shellcode y describir tráfico de C2; análisis y clasificación, no construcción. |
| 2.24 | [(optativa) Fuzzing y análisis simbólico](02-opt-fuzzing.html) | Fuzzear un parser/crackme propio y usar ejecución simbólica para hallar condiciones. |

## Recursos de CLS para esta etapa

- [Etapa 2 · Rama optativa 2D — Windows internals (después de 2C)](../2d.html)
- [Reversing desde cero (tronco principal)](../fichas/reversing-desde-cero.html)
- [Curso IDA desde cero (69 documentos)](../fichas/ida-desde-cero.html)
- [Curso de OllyDbg (Videos 23–40)](../fichas/ollydbg-cayetano.html)
- [Introducción al reversing con IDA Pro (docx)](../fichas/ida-pro-docx.html)

## Evaluación de salida

- **2A** · Explicar qué hace un bloque de 10 instrucciones y qué flags cambia.
- **2A** · Reconstruir un if/else y un bucle a partir del listado.
- **2A** · Poner los tres tipos de breakpoint y justificar cuál usar.
- **2A** · Sincronizar IDA y x64dbg por base o por file offset.
- **2B** · Reconocer tres señales de ofuscación y hallar el bloque real sin NOPear a ciegas.
- **2B** · Encontrar un TLS callback en el PE y demostrar que corre antes de `main`.
- **2B** · Llegar al handler de un control en un binario MFC por una API de texto y el call stack.
- **2B** · Identificar el compilador de un binario y navegar los directorios finos del PE (Rich header, Load Config, debug/PDB).
- **2B** · Clasificar una técnica anti-análisis y detectarla, y leer el mismo binario en IDA y en Ghidra.
- **2C** · Desempaquetar un UPX propio: llegar al OEP, dumpear, reconstruir la IAT y validar con `upx -d`.
- **2C** · Reconocer RTTI, `std::string` (SSO), un `std::vector` y un `try/catch` en un binario C++ propio.
- **2C** · Diagnosticar un bug de heap propio con WinDbg/Page Heap y leer, con un differ, qué cambió un parche.
- **2C** · Automatizar una tarea de análisis con un script de x64dbg y guardar la evidencia.

:::{practica} Entregable de la etapa
Un archivo en tu bitácora con: lecciones completadas, ejercicios resueltos, dudas abiertas y evidencia (capturas, valores, hashes). Sin evidencia no se considera aprobada.
:::

## Errores frecuentes

- Confundir F7 con F8 y creer que F8 no ejecuta la función.
- Leer un salto al revés (pensar que el salto es la condición verdadera).
- Usar una copia ilegal de IDA Pro.
- Parchear software ajeno para saltar una licencia.

## Qué no entra en esta etapa

Los temas que no tienen material revisado o que exceden el marco se listan en [Kernel y otros territorios](05-fuera-de-alcance.html). No los uses como atajo: cada rama tiene prerrequisitos.

:::nota Volver
[Mapa del curso](index.html) · [Inicio](../00_EMPEZAR_AQUI.html)
:::
