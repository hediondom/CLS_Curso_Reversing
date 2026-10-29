---
title: "Mapa del curso"
description: "Siete etapas numeradas: recorrido obligatorio 0–4 y ramas optativas 5–6, más la rama 2D."
---

# Mapa del curso

El recorrido obligatorio son las Etapas 0–4. Las Etapas 5–6 y la rama 2D son optativas y no agregan requisitos para completar el curso base. Cada rama tiene prerrequisitos y una puerta de salida propios.

| Etapa | Foco | Horas estimadas | Lecciones |
|---|---|---|---|
| **0** | [Laboratorio y método seguro](etapa-0.html) | 4 a 6 horas | 1 |
| **1** | [Fundamentos](etapa-1.html) | 21 a 25 horas | 5 |
| **2** | [Introducción al reversing](etapa-2.html) | 32 a 40 h (2A) + ~25 h (2B) + ~30–40 h (2C avanzado) | 24 |
| **3** | [.NET como primera victoria](etapa-3.html) | 7 a 10 horas | 2 |
| **4** | [Práctica guiada](etapa-4.html) | 14 a 18 horas | 4 |
| **5** | [Ramas opcionales](etapa-5.html) | Variable: 5 a 10 horas por rama | 4 |
| **6** | [Rama optativa · Kernel y drivers](etapa-6.html) | 45–65 horas como estimación inicial; puede requerir más tiempo si C, WinDbg o WDK son nuevos. | 6 |

## Cómo estudiar

1. Leé la lección completa, sin saltear los ejemplos.
2. Hacé la práctica en el laboratorio; no solo leas.
3. Respondé las preguntas **antes** de abrir las respuestas.
4. Verificá la puerta de salida. Si no la pasás, repetí la práctica.
5. Anotá en `seguimiento.csv` qué hiciste, cuánto tardaste y qué duda quedó.

## Qué es cada etapa

### Etapa 0 · Laboratorio y método seguro

Armar un entorno aislado, tomar snapshots, verificar hashes y registrar cada práctica con su alcance.

Prerrequisitos: Ninguno.

### Etapa 1 · Fundamentos

Leer un binario sencillo: números, memoria, procesos, formato PE y programas propios en C y Python.

Prerrequisitos: Etapa 0.

### Etapa 2 · Introducción al reversing

Leer assembly x86/x64, seguir el flujo y usar debugger y desensamblador con criterio. Se divide en 2A (base, 2.1–2.9), 2B (Windows intermedio, 2.10–2.16: ofuscación, TLS, MFC, huella, PE fino, anti-análisis, Ghidra) y 2C (Windows avanzado, 2.17+: packers didácticos, C++ profundo, WinDbg/heap, patch diffing, scripting). Las rutas de malware dinámico, shellcode/C2 y fuzzing quedan como optativas, fuera de la puerta obligatoria.

Prerrequisitos: Etapa 1.

### Etapa 3 · .NET como primera victoria

Entender el runtime .NET, leer IL y comparar fuente, IL y decompilación en un programa propio.

Prerrequisitos: Etapa 2.

### Etapa 4 · Práctica guiada

Analizar un programa propio con método, contener la ejecución y escribir un informe reproducible.

Prerrequisitos: Etapas 0 a 3.

### Etapa 5 · Ramas opcionales

Elegir una especialización dentro de Windows, con prerrequisitos y práctica propia, sin convertir el corpus en una lista de tareas peligrosas.

Prerrequisitos: Etapas 0 a 4 completas.

### Etapa 6 · Rama optativa · Kernel y drivers

Comprender, construir y revisar un driver KMDF didáctico con una interfaz inocua, depurarlo solo en VM descartable y explicar mitigaciones actuales.

Prerrequisitos: Etapa 0 (laboratorio aislado), C, assembly, memoria y sincronización, WinDbg y 2D.1 (objetos/tokens), 2D.2 (memoria/loader) y 2D.11 (excepciones/debugging). Etapa 2C es recomendada, no requisito; no hace falta completar toda 2D.

## Material de apoyo

- [Índice de videotutoriales](../videos.html): dónde está en Windows cada video que menciona el curso, con enlace y ruta absoluta.
- [Curso IDA desde cero (69 tutoriales)](../ida-tutes.html): índice por tema, con el texto extraído de cada uno.
- [Teorias_Numeradas clasificadas](../teorias.html): los 2.017 títulos separados en educativos vs cracking de software comercial.
- [Transcripciones de Telegram por tema](../telegram.html): las 523 transcripciones tamizadas; dónde están las sesiones de práctica.
- [Fichas de recursos](../fichas/index.html): qué se revisó, qué falta y qué límites tiene cada fuente.
- [Glosario](../glosario.html): términos en lenguaje de principiante.
- [Preguntas y respuestas](../preguntas_y_respuestas.html): repaso por etapa.
- [Fuentes y límites](../fuentes_y_limites.html): criterios, cobertura y exclusiones.

## Dónde seguir practicando (legal y seguro)

Esta guía practica con **programas propios**, pero conviene seguir con retos pensados para aprender. Estos recursos son **recomendación externa** (no salen del corpus CLS) y permiten practicar reversing de Windows sin problemas legales:

- [crackmes.one](https://crackmes.one/): miles de crackmes subidos para aprender; filtrá por plataforma **Windows** y por dificultad. Analizalos en tu VM.
- [Flare-On Challenge](https://flare-on.com/): competencia anual y gratuita de reversing, centrada en Windows; los retos de años anteriores quedan publicados con soluciones.
- **CTFs (categoría rev)**: [CTFtime](https://ctftime.org/) lista competencias; muchos retos de reversing son binarios de Windows. Buenísimos para practicar con límite de tiempo.
- **Talleres abiertos**: materiales públicos de análisis de malware y reversing (por ejemplo, [OALabs](https://www.openanalysis.net/) o Malware Unicorn) con binarios de práctica.
- **Tus propios programas**: seguí compilando ejemplos con condiciones cada vez más complejas; es la práctica más segura y la que más enseña.

Regla que no cambia: todo en la VM aislada de la Etapa 0, y nada de software ajeno sin permiso.
