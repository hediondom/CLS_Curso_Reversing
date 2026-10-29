---
title: "2.24 (optativa) · Fuzzing y análisis simbólico"
description: "Encontrar fallos en un parser o crackme propio: fuzzear, guardar entradas, reproducir crashes; y usar ejecución simbólica para hallar qué condición llega a un bloque. Ruta optativa."
etapa: "Etapa 2 · Windows avanzado (2C) · ruta optativa"
---

# Fuzzing y análisis simbólico

:::{aviso} Ruta optativa · sobre binarios propios
Especialización, no requisito de 2C. Se practica con un **parser o crackme propio** y busca **encontrar y entender fallos** (bugs de robustez) y condiciones de entrada, en clave defensiva. **Prerrequisitos:** C/compilación (1.5), WinDbg/heap ([2.19](02-windbg-heap.html)), método de análisis (4.1).
:::

Dos técnicas que **automatizan** la búsqueda de problemas, cada una por un camino distinto:

## Fuzzing: romper a fuerza de entradas

El fuzzing encuentra fallos en el parser, pero no sustituye la reconstrucción de su estructura: para deducir campos y framing desde muestras, consulta [4.5](../guia/04-formatos-protocolos.html).

Fuzzear es alimentar al programa con **muchísimas entradas** (mutadas o generadas) y ver cuáles lo hacen **crashear o colgarse**. Un crash es una pista de un bug (overflow, desreferencia nula, consumo de memoria). El flujo (**conocimiento externo**):

1. **Elegí un objetivo chico:** un **parser propio** (lee un formato de archivo o un input de texto) o un crackme. Cuanto más acotado, mejor.
2. **Semillas:** juntá entradas válidas de ejemplo (*corpus* inicial).
3. **Fuzzer:** herramientas como **AFL++**, **libFuzzer** (si compilás con instrumentación) o **WinAFL** en Windows. Mutan el corpus y maximizan la **cobertura** de código.
4. **Guardá todo:** cada entrada que provoca un crash se **guarda** tal cual, para reproducir.
5. **Triage:** reproducís el crash (con Page Heap de [2.19](02-windbg-heap.html) si es de memoria), lo minimizás y explicás la causa.

La **reproducibilidad** es el punto: un fuzzing sirve si podés volver a disparar el crash con la entrada guardada y señalar la línea.

## Reducir el corpus y minimizar un crash son tareas distintas

El corpus puede crecer con casos que recorren los mismos caminos. En libFuzzer, -merge=1 permite construir un corpus reducido conservando las entradas que aportan cobertura nueva; no promete conservar todas las propiedades semánticas ni elegir el archivo más corto para cada camino. Conserva el corpus original y versiona el corpus curado por separado.

Minimizar un **crash concreto** busca una entrada más pequeña que siga reproduciendo ese mismo fallo; libFuzzer ofrece -minimize_crash=1 con un límite de ejecuciones/tiempo. Guarda siempre el crash original, la versión minimizada, hashes y el comando exacto. Los flags cambian entre fuzzers: consulta la documentación de la herramienta y no uses una opción de corpus como sustituto de reproducir el fallo.

## Análisis simbólico: resolver en vez de adivinar

En vez de probar entradas al azar, la **ejecución simbólica** trata la entrada como una **incógnita** y, con un *solver* (SMT), calcula **qué valor** hace que la ejecución tome un camino. Sirve para "¿qué entrada llega a este bloque?" sin fuerza bruta (**conocimiento externo**). Herramientas: **angr**, **Triton**, **Miasm** (el "taller actual" de [2.9](02-herramientas.html) las nombra). Dónde brilla:

- Un crackme con una comparación compleja: angr puede **hallar la clave** resolviendo las restricciones hasta el "chico bueno".
- Encontrar la entrada que alcanza un bloque de error que el fuzzer no pega por azar.

Límite práctico: la **explosión de caminos**. En binarios grandes el árbol de estados crece muchísimo; por eso conviene **acotar** (empezar desde una función, fijar longitudes) y combinarlo con fuzzing.

## Ejemplo: fuzzing + simbólico sobre un parser propio

*(Ejemplo **ilustrativo**: flujo y salida construidos.)*

```text
Objetivo: parser propio  parse_registro(archivo)   (lee un header + N bytes)

Fuzzing (WinAFL, 2 h, corpus de 5 archivos válidos):
  crashes/ id:000  → len declarado 0xFFFF con archivo de 20 bytes
  Triage con Page Heap: AV en parse_registro+0x3e (lee fuera del buffer)
  Causa: confía en el 'len' del header sin validarlo contra el tamaño real.

Simbólico (angr) para alcanzar el bloque "formato_v2":
  entrada hallada: primeros 4 bytes = "RG02"  → toma ese camino
```

El fuzzer encontró un bug de robustez (no valida `len`); angr encontró **qué bytes** activan una rama concreta. Los dos resultados son **reproducibles** y señalan una línea.

## Práctica

En tu VM, con un **parser propio** y datos de prueba inventados:

1. Definí un harness determinista que procese una entrada y termine sin depender de red, reloj, rutas personales ni servicios externos.
2. Prepará un corpus pequeño de archivos válidos y anotá qué estructura cubre cada uno. Guardá una copia inmutable del corpus inicial.
3. Activá cobertura si la herramienta lo permite; ejecutá con límites razonables de tiempo y memoria. Conservá cada entrada que produzca un fallo.
4. Reproducí un crash sin el fuzzer, minimizá esa entrada para conservar el mismo fallo y registra versión de herramienta, comando, hash del original y del caso reducido, y pila/síntoma.
5. Reducí por separado el corpus preservando cobertura (en libFuzzer, -merge=1); compara cobertura y cantidad de casos. No borres el corpus original ni los crashes.
6. Corregí el parser y añadí el caso reducido como regresión; comprobá que los ejemplos válidos siguen pasando.
7. Como ejercicio separado, usá angr sobre un binario propio pequeño para hallar una entrada que alcance una rama concreta; explicá qué restricciones resolvió y qué quedó fuera del modelo.

## Preguntas de repaso

?? ¿Qué es fuzzing y qué buscás con un crash?
!! Alimentar el programa con **muchas entradas** (mutadas/generadas) para ver cuáles lo rompen. Un **crash** es la pista de un bug (overflow, null deref, etc.); lo guardás para reproducir y explicar la causa.

?? ¿Por qué guardás cada entrada que crashea?
!! Por **reproducibilidad**: un hallazgo sirve si podés volver a disparar el crash con esa entrada exacta, minimizarla y señalar la línea culpable.

?? ¿En qué se diferencia el análisis simbólico del fuzzing?
!! El fuzzing **prueba** entradas (al azar/mutadas); el simbólico trata la entrada como **incógnita** y un *solver* **calcula** qué valor toma un camino. Uno adivina con cobertura; el otro resuelve restricciones.

?? ¿Cuál es el límite típico del análisis simbólico?
!! La **explosión de caminos**: el árbol de estados crece muchísimo en binarios grandes. Se acota (desde una función, fijando longitudes) y se combina con fuzzing.

?? ¿Qué herramientas nombrás para cada técnica?
!! Fuzzing: **AFL++**, **libFuzzer**, **WinAFL**. Simbólico: **angr**, **Triton**, **Miasm**.

:::{nota} Puerta de salida (optativa)
Podés: (1) fuzzear un parser/crackme propio y guardar los crashes; (2) reproducir y explicar un crash con Page Heap; (3) usar ejecución simbólica para hallar la entrada que alcanza un bloque; (4) minimizar un crash reproducible y un corpus conservando cobertura; explicar la explosión de caminos y cuándo combinar ambas.
:::

## Fuentes de esta lección

- LLVM: [libFuzzer: coverage-guided fuzz testing](https://www.llvm.org/docs/LibFuzzer.html).

- [Herramientas: el taller actual](02-herramientas.html) (2.9) — menciona angr, Unicorn, Triton y Miasm en el taller moderno.
- [WinDbg, TTD y heap](02-windbg-heap.html) (2.19) — Page Heap para reproducir y diagnosticar los crashes de memoria del fuzzing.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la mención de angr/Triton/Miasm en el taller actual (2.9). **Conocimiento externo:** fuzzing (AFL++/libFuzzer/WinAFL), ejecución simbólica (angr) y la explosión de caminos. **Recomendación editorial:** el enfoque sobre binarios propios, el ejemplo ilustrativo y la práctica de triage reproducible.
:::
